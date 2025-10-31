# AI-Powered Interview Preparation Chatbot — Documentation

This DOCUMENTATION.md expands on the README and explains how to enable GPT-based feedback, environment setup, and a short provider comparison (OpenAI ChatGPT vs Google Gemini).

## Project overview

The project is an MVP that simulates interviews and provides AI-driven feedback. Core components:

- `app.py` — Streamlit interface
- `interview_manager.py` — interview session controller
- `nlp_feedback.py` — answer analysis (heuristics + optional GPT integration)
- `db.py` — SQLite storage
- `questions.json` — question bank

## Enabling GPT-based feedback (OpenAI)

1. Install `openai` Python package in your environment (venv recommended):

   pip install openai

2. Export your OpenAI API key as environment variable (Windows PowerShell):

```powershell
$env:OPENAI_API_KEY = "sk-..."
# Or permanently in system/user env variables
```

3. Optionally set the `OPENAI_MODEL` env var to the model you want (e.g., `gpt-4`, `gpt-4o`, `gpt-3.5-turbo`). The default is `gpt-3.5-turbo`.

4. Enable GPT for feedback by either:
   - Setting `USE_GPT=1` in the environment, or
   - Calling `analyze_answer(question, answer, use_gpt=True)` from code.

The `nlp_feedback.py` module will attempt a GPT call, parse JSON from the response (or extract a numeric score heuristically), and return a dictionary with at least `score` and `feedback`. On any failure it falls back to the heuristic analyzer.

### UI behavior when API key is missing

The Streamlit UI includes a checkbox to enable GPT-based feedback. If the checkbox is enabled but `OPENAI_API_KEY` is not configured in the environment (or Streamlit secrets), the app will:

- Show a clear error/warning message in the sidebar explaining the missing key.
- Continue to run and fall back to the local heuristic analyzer so no functionality is lost.

This avoids runtime failures and gives a clear path for users to set their API key.

## Using Google service account for demo (Streamlit Cloud)

For the demo, store your Google service-account JSON in Streamlit secrets under the key `gcloud_service_account` or set the environment variable `GC_SERVICE_ACCOUNT_JSON` with the JSON content. The app will write the JSON to a temporary file at startup and set `GOOGLE_APPLICATION_CREDENTIALS` so the backend Gemini adapter can authenticate.

Example `secrets.toml` for Streamlit Cloud (paste the JSON as a single string):

```toml
[gcloud_service_account]
key = "{ \"type\": \"service_account\", \"project_id\": ... }"
```

Or add `GC_SERVICE_ACCOUNT_JSON` as a host environment variable with the JSON string.

## Using Google Gemini instead of OpenAI

The project currently integrates OpenAI's chat completions API. You can use Google Gemini (API) in place of OpenAI, but you'll need to:

- Install and configure the Google Cloud client for the model.
- Implement a small adapter function in `nlp_feedback.py` that calls Gemini with the same prompt and returns a JSON-like response.

Recommended packages for a lightweight demo

```
pip install -r requirements.txt
# If you plan to use OpenAI:
pip install openai
# If you plan to use Google Gemini/Generative AI locally, install one of:
# pip install google-cloud-aiplatform
# pip install google-genai  # if using the newer google-genai package (check availability)
```

Pros/cons quick comparison:

- OpenAI ChatGPT (gpt-3.5/gpt-4):
  - Pros: mature SDKs, clear ChatCompletion format, wide community support, many tutorials.
  - Cons: cost can be high for larger models, rate limits.
- Google Gemini:
  - Pros: state-of-the-art models (Gemini Ultra, etc.) and strong multimodal capabilities.
  - Cons: newer integration patterns, slightly different prompt/response handling; you'd need to adapt response parsing.

Recommendation for the MVP: start with OpenAI (ChatGPT) because the SDK is simple to integrate and the ChatCompletion pattern maps neatly to our `system/user` prompt approach. If you have an existing Gemini key or preference, you can implement a small adapter with similar behavior.

## Security and API keys

- Never commit API keys to source control.
- Use environment variables or a secret manager for production.

## Running the app (quick)

```powershell
python -m venv .venv
& .venv\Scripts\Activate.ps1
pip install -r "d:\projects\interview chatbot\requirements.txt"
pip install openai
python -m textblob.download_corpora
& .venv\Scripts\python.exe -m streamlit run "d:\projects\interview chatbot\app.py"
```

## Where to extend next

- Add a Gemini adapter in `nlp_feedback.py` if you want to use Google APIs.
- Add better prompt engineering and rubric templates for consistent scoring.
- Add unit tests for the GPT adapter and heuristics.

---
