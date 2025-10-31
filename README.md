# AI-Powered Interview Preparation Chatbot (MVP)

This MVP provides a Streamlit-based interface to simulate HR and technical interviews with AI-driven feedback, scoring, and an analytics dashboard.

Quick start

1. Create a Python 3.8+ virtual environment and activate it.
2. Install dependencies:

   pip install -r requirements.txt

3. Set environment variables (optional):

   - OPENAI_API_KEY (for GPT-based feedback if configured)

4. Run the app:

   streamlit run app.py

Files

- `app.py` - Streamlit web UI
- `interview_manager.py` - Interview flow controller
- `nlp_feedback.py` - Analysis and scoring utilities
- `db.py` - SQLite storage helpers
- `questions.json` - Sample HR and Technical questions
- `smoke_test.py` - Quick test for the NLP feedback

Notes

- This is an MVP and uses simple heuristics for scoring. Replace or augment with GPT-style scoring for production.
- On Windows, `pyttsx3` may require `pypiwin32` and audio drivers.
