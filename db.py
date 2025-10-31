import sqlite3
import json
from datetime import datetime


class Database:
    def __init__(self, path='interview.db'):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            user_email TEXT,
            domain TEXT,
            started_at TEXT
        )
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            question TEXT,
            answer TEXT,
            feedback TEXT,
            score REAL,
            created_at TEXT
        )
        ''')
        self.conn.commit()

    def create_session(self, user):
        cur = self.conn.cursor()
        cur.execute('''INSERT INTO sessions (user_name, user_email, domain, started_at) VALUES (?,?,?,?)''',
                    (user.get('name'), user.get('email'), user.get('domain'), datetime.utcnow().isoformat()))
        self.conn.commit()
        return cur.lastrowid

    def save_response(self, session_id, question, answer, feedback):
        cur = self.conn.cursor()
        feedback_json = json.dumps(feedback)
        score = feedback.get('score', 0)
        cur.execute('''INSERT INTO responses (session_id, question, answer, feedback, score, created_at) VALUES (?,?,?,?,?,?)''',
                    (session_id, question, answer, feedback_json, score, datetime.utcnow().isoformat()))
        self.conn.commit()

    def get_session_responses(self, session_id):
        cur = self.conn.cursor()
        cur.execute(
            'SELECT question, answer, feedback, score, created_at FROM responses WHERE session_id=?', (session_id,))
        rows = cur.fetchall()
        return rows

    def close_session(self, session_id):
        # Could add ended_at; placeholder
        pass

    def __del__(self):
        try:
            self.conn.close()
        except:
            pass
