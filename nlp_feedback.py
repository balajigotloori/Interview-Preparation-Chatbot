import os
import json
import re
from textblob import TextBlob
import math

try:
    import openai
except Exception:
    openai = None
import importlib


def _get_gemini_client():
    """Lazily import the google.generativeai client to avoid hard import-time
    failures during static analysis or when the package isn't installed.
    Returns the client module/object or None if unavailable.
    """
    try:
        mod = importlib.import_module('google.generativeai')
        # Some package versions expose a `client` attribute, others may expose
        # top-level callables — prefer `client` if present.
        return getattr(mod, 'client', mod)
    except Exception:
        return None


# Heuristic analyzer (existing behavior). Keeps the same return schema.
def _heuristic_analyze(question, answer):
    blob = TextBlob(answer)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    words = len(answer.split())

    q_words = set([w.lower() for w in question.split() if len(w) > 3])
    a_words = set([w.lower().strip('.,') for w in answer.split()])
    overlap = len(q_words.intersection(a_words))
    relevance = overlap / (len(q_words) + 1)

    noun_phrases = len(blob.noun_phrases)

    score = (min(words / 20, 1.0) * 0.4 + max(min(relevance, 1.0), 0) * 0.3
             + min(noun_phrases/3, 1.0)*0.2 + (polarity+1)/2*0.1) * 10
    score = round(score, 1)

    feedback = []
    if words < 20:
        feedback.append(
            'Try to give a slightly longer answer with more specifics.')
    if relevance < 0.1:
        feedback.append(
            'Your answer could be more focused on the question. Mention relevant keywords.')
    if subjectivity > 0.6:
        feedback.append(
            'You used a lot of subjective language; add facts or examples where possible.')
    if noun_phrases < 1:
        feedback.append(
            'Consider structuring your answer with clearer points or examples.')

    if not feedback:
        feedback_text = 'Good answer — clear and relevant.'
    else:
        feedback_text = ' '.join(feedback)

    return {
        'score': score,
        'polarity': polarity,
        'subjectivity': subjectivity,
        'relevance': relevance,
        'noun_phrases': noun_phrases,
        'feedback': feedback_text
    }


def _parse_json_from_text(text):
    # Find the last {...} JSON-like block in the text
    matches = re.findall(r"\{.*\}", text, flags=re.S)
    if not matches:
        return None
    last = matches[-1]
    try:
        return json.loads(last)
    except Exception:
        return None


def _gpt_analyze(question, answer, model='gpt-3.5-turbo'):
    """
    Call OpenAI Chat API to evaluate the answer. Expects OPENAI_API_KEY in env.
    The model should return JSON with keys: score (0-10), feedback, and optional fields.
    """
    if openai is None:
        raise RuntimeError('openai package not available')

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not set in environment')

    openai.api_key = api_key

    system = (
        "You are an expert interview coach. Evaluate the user's answer to the question using a short rubric. "
        "Return a JSON object containing at least: score (0-10), feedback (brief text). "
        "You may include optional fields like polarity, relevance. Be concise and return only valid JSON or text that includes JSON."
    )

    user_prompt = (
        f"Question: {question}\n\nAnswer: {answer}\n\n"
        "Provide a short evaluation and a numeric score from 0 (poor) to 10 (excellent). "
        "Return the result as JSON."
    )

    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'system', 'content': system},
                      {'role': 'user', 'content': user_prompt}],
            max_tokens=300,
            temperature=0.2,
        )
        text = resp['choices'][0]['message']['content']
        parsed = _parse_json_from_text(text)
        if parsed and 'score' in parsed:
            return parsed
        else:
            # Try to extract score heuristically from text then fallback to heuristics
            m = re.search(r"score\D*(\d{1,2}(?:\.\d)?)", text, flags=re.I)
            if m:
                try:
                    score = float(m.group(1))
                    parsed = parsed or {}
                    parsed['score'] = score
                    parsed.setdefault('feedback', text.strip())
                    return parsed
                except Exception:
                    pass
    except Exception as e:
        # Bubble up later; the caller will fall back
        raise

    return None


def _gemini_analyze(question, answer, model='gemini-lite'):
    """
    Call Google Gemini (Generative AI) to evaluate the answer. Expects GOOGLE_API_KEY or
    application default credentials configured.

    Return a dict similar to _gpt_analyze or None on failure.
    """
    client = _get_gemini_client()
    if client is None:
        raise RuntimeError('google.generativeai client not available')

    # Build a prompt similar to the OpenAI prompt
    system = (
        "You are an expert interview coach. Evaluate the user's answer to the question using a short rubric. "
        "Return a JSON object containing at least: score (0-10), feedback (brief text)."
    )
    prompt = f"{system}\nQuestion: {question}\n\nAnswer: {answer}\n\nReturn the result as JSON."

    try:
        # NOTE: exact client API may differ depending on installed google library version.
        # We'll call a generic `generate_text` style method if available.
        resp = client.generate_text(model=model, prompt=prompt)
        text = resp.text if hasattr(resp, 'text') else str(resp)
        parsed = _parse_json_from_text(text)
        if parsed and 'score' in parsed:
            return parsed
        else:
            m = re.search(r"score\D*(\d{1,2}(?:\.\d)?)", text, flags=re.I)
            if m:
                try:
                    score = float(m.group(1))
                    parsed = parsed or {}
                    parsed['score'] = score
                    parsed.setdefault('feedback', text.strip())
                    return parsed
                except Exception:
                    pass
    except Exception:
        raise

    return None


def validate_gemini_credentials(model=None, timeout=10):
    """
    Try a tiny Gemini call to validate credentials. Returns (True, message) on success
    or (False, error_message) on failure. This will perform a network call and should
    only be used interactively by the developer/admin.
    """
    client = _get_gemini_client()
    if client is None:
        return False, 'google.generativeai client library not installed'

    model = model or os.getenv('GEMINI_MODEL', 'gemini-lite')
    prompt = 'Please reply with a short confirmation: OK.'
    try:
        # Attempt a small call; exact method signature depends on installed client
        resp = client.generate_text(model=model, prompt=prompt)
        text = getattr(resp, 'text', None) or str(resp)
        return True, text.strip()[:200]
    except Exception as e:
        return False, str(e)


def validate_openai_credentials(model=None):
    """
    Attempt a tiny OpenAI call (ChatCompletion) to validate OPENAI_API_KEY. Returns
    (True, message) on success or (False, error_message) on failure.
    """
    if openai is None:
        return False, 'openai package not installed'
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return False, 'OPENAI_API_KEY not set'
    try:
        model = model or os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'system', 'content': 'You are a test assistant.'},
                      {'role': 'user', 'content': 'Reply with OK.'}],
            max_tokens=5,
            temperature=0.0,
        )
        text = resp['choices'][0]['message']['content']
        return True, text.strip()
    except Exception as e:
        return False, str(e)


def analyze_answer(question, answer, use_gpt=None):
    """
    Analyze an answer. By default this uses heuristics. To enable GPT-based feedback:
    - set environment variable OPENAI_API_KEY and either set USE_GPT=1 in env or pass use_gpt=True.

    Returns a dictionary: {'score', 'feedback', ...}
    """
    env_flag = os.getenv('USE_GPT', '').lower() in ('1', 'true', 'yes')
    enabled = use_gpt is True or (use_gpt is None and env_flag)

    if enabled:
        # Provider selection via OPENAI_PROVIDER env var: 'openai' (default) or 'gemini'
        provider = os.getenv('OPENAI_PROVIDER', os.getenv(
            'PROVIDER', 'openai')).lower()
        # Allow forcing provider via use_gpt (string) - if use_gpt is 'gemini'
        if isinstance(use_gpt, str):
            provider = use_gpt.lower()
        try:
            if provider == 'gemini':
                model = os.getenv('GEMINI_MODEL', 'gemini-lite')
                result = _gemini_analyze(question, answer, model=model)
            else:
                model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
                result = _gpt_analyze(question, answer, model=model)

            if result:
                # Ensure score exists and normalized (0-10)
                if 'score' in result:
                    try:
                        result['score'] = round(float(result['score']), 1)
                    except Exception:
                        result['score'] = 0.0
                else:
                    result['score'] = 0.0
                return result
        except Exception:
            # If provider call fails for any reason, fall back to heuristic analyzer
            pass

    return _heuristic_analyze(question, answer)
