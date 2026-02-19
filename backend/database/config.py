"""
Database configuration - automatically switches between SQLite and PostgreSQL
"""

import os
import sys

# Check if we're in production (Vercel)
IN_PRODUCTION = os.environ.get('VERCEL_ENV') is not None

if IN_PRODUCTION:
    # Use production database (PostgreSQL)
    import psycopg2
    from psycopg2.extras import RealDictCursor

    DATABASE_URL = os.environ.get('DATABASE_URL')

    def get_db_connection():
        """Create and return a PostgreSQL database connection"""
        if not DATABASE_URL:
            raise Exception("DATABASE_URL environment variable not set")

        conn = psycopg2.connect(DATABASE_URL)
        return conn

    def execute_query(conn, query, params=None):
        """Execute a SELECT query and return all results"""
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchall()

    def execute_query_one(conn, query, params=None):
        """Execute a SELECT query and return one result"""
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchone()

    def execute_write(conn, query, params=None):
        """Execute an INSERT/UPDATE/DELETE query"""
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        conn.commit()
        return cur.rowcount

    def init_database():
        """Initialize PostgreSQL database and create tables"""
        conn = get_db_connection()
        cur = conn.cursor()

        # Create FAQs table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS faqs (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create unknown questions table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS unknown_questions (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                answered BOOLEAN DEFAULT FALSE,
                session_id TEXT
            )
        ''')

        # Create chat history table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ PostgreSQL database initialized")

else:
    # Use development SQLite
    import sqlite3
    import os

    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'lautech.db')

    def get_db_connection():
        """Create and return a SQLite database connection"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(conn, query, params=None):
        """Execute a SELECT query and return all results"""
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchall()

    def execute_query_one(conn, query, params=None):
        """Execute a SELECT query and return one result"""
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchone()

    def execute_write(conn, query, params=None):
        """Execute an INSERT/UPDATE/DELETE query"""
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        conn.commit()
        return cur.rowcount

    def init_database():
        """Initialize SQLite database and create tables"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unknown_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                answered BOOLEAN DEFAULT 0,
                session_id TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ SQLite database initialized")

# Initialize database on module import
init_database()

# Common functions that work with both databases
def add_faq(question, answer, category=None):
    """Add a new FAQ to the database"""
    conn = get_db_connection()

    if IN_PRODUCTION:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO faqs (question, answer, category) VALUES (%s, %s, %s) RETURNING id",
            (question, answer, category)
        )
        faq_id = cur.fetchone()[0]
        conn.commit()
    else:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO faqs (question, answer, category) VALUES (?, ?, ?)",
            (question, answer, category)
        )
        faq_id = cur.lastrowid
        conn.commit()

    conn.close()
    return faq_id

def get_all_faqs():
    """Retrieve all FAQs from database"""
    conn = get_db_connection()

    if IN_PRODUCTION:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM faqs ORDER BY id")
        faqs = cur.fetchall()
    else:
        cur = conn.cursor()
        cur.execute("SELECT * FROM faqs ORDER BY id")
        faqs = cur.fetchall()

    conn.close()
    return [dict(faq) for faq in faqs]

def add_unknown_question(question, session_id=None):
    """Log an unknown question"""
    conn = get_db_connection()

    if IN_PRODUCTION:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO unknown_questions (question, session_id) VALUES (%s, %s) RETURNING id",
            (question, session_id)
        )
        question_id = cur.fetchone()[0]
        conn.commit()
    else:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO unknown_questions (question, session_id) VALUES (?, ?)",
            (question, session_id)
        )
        question_id = cur.lastrowid
        conn.commit()

    conn.close()
    return question_id

def get_unknown_questions(answered=False):
    """Get all unknown questions"""
    conn = get_db_connection()

    if IN_PRODUCTION:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT * FROM unknown_questions WHERE answered = %s ORDER BY asked_at DESC",
            (answered,)
        )
        questions = cur.fetchall()
    else:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM unknown_questions WHERE answered = ? ORDER BY asked_at DESC",
            (1 if answered else 0,)
        )
        questions = cur.fetchall()

    conn.close()
    return [dict(q) for q in questions]

def add_chat_history(session_id, user_message, bot_response):
    """Save chat history"""
    conn = get_db_connection()

    if IN_PRODUCTION:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (%s, %s, %s)",
            (session_id, user_message, bot_response)
        )
    else:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (?, ?, ?)",
            (session_id, user_message, bot_response)
        )

    conn.commit()
    conn.close()