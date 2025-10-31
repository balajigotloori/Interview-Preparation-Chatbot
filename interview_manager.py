import json
import random
from db import Database
from nlp_feedback import analyze_answer


class InterviewManager:
    def __init__(self, questions_path='questions.json', db_path='interview.db'):
        with open(questions_path, 'r', encoding='utf-8') as f:
            self.questions = json.load(f)
        self.db = Database(db_path)

    def start_session(self, user):
        session_id = self.db.create_session(user)
        return session_id

    def get_question(self, interview_type='hr'):
        pool = self.questions.get(interview_type, [])
        return random.choice(pool) if pool else None

    def submit_answer(self, session_id, question, answer, use_gpt=False):
        # pass use_gpt through to the analyzer (it may fall back to heuristics)
        feedback = analyze_answer(question, answer, use_gpt=use_gpt)
        score = feedback.get('score', 0)
        self.db.save_response(session_id, question, answer, feedback)
        return feedback

    def end_session(self, session_id):
        self.db.close_session(session_id)
