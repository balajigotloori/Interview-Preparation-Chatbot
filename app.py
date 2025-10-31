import streamlit as st
from interview_manager import InterviewManager
import pandas as pd
from db import Database

st.set_page_config(page_title='Interview Prep Chatbot', layout='centered')

st.title('AI-Powered Interview Preparation Chatbot (MVP)')

if 'manager' not in st.session_state:
    st.session_state.manager = InterviewManager()

if 'session_id' not in st.session_state:
    st.session_state.session_id = None

with st.sidebar:
    st.header('User Registration')
    name = st.text_input('Name')
    email = st.text_input('Email')
    domain = st.selectbox('Domain', ['hr', 'technical', 'mixed'])
    # If a Google service account is provided in Streamlit secrets or env var,
    # write it to a temp file and set GOOGLE_APPLICATION_CREDENTIALS so the
    # Gemini adapter can authenticate server-side.
    try:
        import os
        import tempfile
        import json
        sa_json = None
        if 'gcloud_service_account' in st.secrets:
            sa_json = st.secrets['gcloud_service_account']
        elif os.getenv('GC_SERVICE_ACCOUNT_JSON'):
            sa_json = os.getenv('GC_SERVICE_ACCOUNT_JSON')

        if sa_json:
            # write to a temporary file
            tmp_path = os.path.join(
                tempfile.gettempdir(), 'gcloud_service_account.json')
            # if stored as dict in secrets, serialize
            if isinstance(sa_json, dict):
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    json.dump(sa_json, f)
            else:
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    f.write(sa_json)
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = tmp_path
            st.info(
                'Using Google service account from secrets for backend API calls.')
        # If OPENAI_API_KEY is provided in Streamlit secrets, set it into the
        # environment so other modules relying on os.getenv can find it.
        try:
            if 'OPENAI_API_KEY' in st.secrets and not os.getenv('OPENAI_API_KEY'):
                os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
                st.info('Loaded OPENAI_API_KEY from Streamlit secrets.')
        except Exception:
            # If secrets are not accessible for any reason, continue silently.
            pass
    except Exception:
        # silently ignore; adapter will fall back to heuristics if no credentials
        pass
    st.markdown('---')
    st.subheader('AI Feedback (optional)')
    use_gpt = st.checkbox(
        'Enable GPT-based feedback (requires OPENAI_API_KEY)')
    openai_model = st.selectbox('Model', ['gpt-3.5-turbo', 'gpt-4'], index=0)
    # Provider availability checks
    from importlib import util as _util
    _openai_available = _util.find_spec('openai') is not None
    _gemini_available = _util.find_spec('google.generativeai') is not None
    st.markdown('**Provider availability**')
    st.write(f"OpenAI installed: {'✅' if _openai_available else '❌'}")
    st.write(f"Gemini client installed: {'✅' if _gemini_available else '❌'}")
    # Show a warning if the user enables GPT but no API key is configured
    if use_gpt:
        import os
        if not os.getenv('OPENAI_API_KEY'):
            st.error('OPENAI_API_KEY not found. GPT feedback will fall back to local heuristics.\n\nSet OPENAI_API_KEY in your environment or use Streamlit secrets to enable GPT.')
    if st.button('Start Interview'):
        if not name:
            st.warning('Enter a name to start')
        else:
            user = {'name': name, 'email': email, 'domain': domain}
            st.session_state.session_id = st.session_state.manager.start_session(
                user)
            st.success(f"Started session for {name}")
    st.markdown('---')
    st.subheader('Credential checks')
    if st.button('Validate Gemini credentials'):
        from nlp_feedback import validate_gemini_credentials
        ok, msg = validate_gemini_credentials()
        if ok:
            st.success('Gemini validation succeeded: ' + msg)
        else:
            st.error('Gemini validation failed: ' + msg)

    if st.button('Validate OpenAI credentials'):
        from nlp_feedback import validate_openai_credentials
        ok, msg = validate_openai_credentials()
        if ok:
            st.success('OpenAI validation succeeded: ' + msg)
        else:
            st.error('OpenAI validation failed: ' + msg)

st.subheader('Interview')
if st.session_state.session_id:
    if 'current_q' not in st.session_state or st.button('Next Question'):
        interview_type = domain if domain != 'mixed' else (
            st.selectbox('Choose type for this question', ['hr', 'technical']))
        q = st.session_state.manager.get_question(
            interview_type if interview_type else 'hr')
        st.session_state.current_q = q
    st.write('Question:')
    st.write(st.session_state.current_q)
    answer = st.text_area('Your Answer')
    if st.button('Submit Answer'):
        # Pass the use_gpt flag and selected model into the submission
        # set OPENAI_MODEL env var if checkbox is used
        if use_gpt:
            import os
            os.environ['OPENAI_MODEL'] = openai_model
        feedback = st.session_state.manager.submit_answer(
            st.session_state.session_id, st.session_state.current_q, answer, use_gpt=use_gpt)
        st.write('Feedback:')
        st.write(feedback.get('feedback'))
        st.write('Score:')
        st.write(feedback.get('score'))

    if st.button('Show Summary'):
        db = Database()
        rows = db.get_session_responses(st.session_state.session_id)
        df = pd.DataFrame(
            rows, columns=['question', 'answer', 'feedback', 'score', 'created_at'])
        st.write(df)
        st.line_chart(df['score'])
else:
    st.info('Start a session from the sidebar')
