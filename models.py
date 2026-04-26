import sqlite3
import uuid
import json
import hashlib
from datetime import datetime
from config import DATABASE

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            questions TEXT NOT NULL,
            created_at TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id TEXT NOT NULL,
            answers TEXT NOT NULL,
            submitted_at TEXT NOT NULL,
            FOREIGN KEY (form_id) REFERENCES forms(id)
        )
    ''')

    conn.commit()
    conn.close()


class Form:
    def __init__(self, title, description, questions):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.questions = questions
        self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def save(self, user_id=None):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO forms
            (id, title, description, questions, created_at, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            self.id,
            self.title,
            self.description,
            json.dumps(self.questions, ensure_ascii=False),
            self.created_at,
            user_id
        ))
        conn.commit()
        conn.close()
        return self.id

    @staticmethod
    def get_all(user_id=None):
        conn = get_db()
        cursor = conn.cursor()
        if user_id:
            cursor.execute(
                'SELECT * FROM forms WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            )
        else:
            cursor.execute(
                'SELECT * FROM forms ORDER BY created_at DESC'
            )
        rows = cursor.fetchall()
        conn.close()
        forms = []
        for row in rows:
            form = dict(row)
            form['questions'] = json.loads(form['questions'])
            forms.append(form)
        return forms

    @staticmethod
    def get_by_id(form_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM forms WHERE id = ?',
            (form_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            form = dict(row)
            form['questions'] = json.loads(form['questions'])
            return form
        return None


class Response:
    def __init__(self, form_id, answers):
        self.form_id = form_id
        self.answers = answers
        self.submitted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def save(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO responses (form_id, answers, submitted_at)
            VALUES (?, ?, ?)
        ''', (
            self.form_id,
            json.dumps(self.answers, ensure_ascii=False),
            self.submitted_at
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all(form_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM responses WHERE form_id = ?',
            (form_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        responses = []
        for row in rows:
            r = dict(row)
            r['answers'] = json.loads(r['answers'])
            responses.append(r)
        return responses

    @staticmethod
    def count(form_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT COUNT(*) as total FROM responses WHERE form_id = ?',
            (form_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row['total'] if row else 0


class User:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = self.hash_password(password)
        self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def save(self):
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (name, email, password, created_at)
                VALUES (?, ?, ?, ?)
            ''', (
                self.name,
                self.email,
                self.password,
                self.created_at
            ))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    @staticmethod
    def get_by_email(email):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE email = ?',
            (email,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def verify_password(email, password):
        user = User.get_by_email(email)
        if not user:
            return None
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if user['password'] == hashed:
            return user
        return None