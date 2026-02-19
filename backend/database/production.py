"""
Production database configuration with PostgreSQL
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from datetime import datetime
import json

# Get database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', '')


def get_db_connection():
    """Get production database connection"""
    if DATABASE_URL.startswith('postgresql://'):
        # PostgreSQL connection
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        # Fallback to SQLite for development
        import sqlite3
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), '../../data/lautech.db'))
        conn.row_factory = sqlite3.Row
        return conn


def init_production_db():
    """Initialize production database with tables"""
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
    print("✅ Production database initialized!")


def migrate_from_sqlite():
    """Migrate data from SQLite to PostgreSQL"""
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), '../../data/lautech.db'))
    sqlite_conn.row_factory = sqlite3.Row

    # Connect to PostgreSQL
    pg_conn = get_db_connection()
    pg_cur = pg_conn.cursor()

    # Migrate FAQs
    faqs = sqlite_conn.execute("SELECT * FROM faqs").fetchall()
    for faq in faqs:
        pg_cur.execute(
            "INSERT INTO faqs (id, question, answer, category, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (faq['id'], faq['question'], faq['answer'], faq['category'], faq['created_at'], faq['updated_at'])
        )
    print(f"✅ Migrated {len(faqs)} FAQs")

    # Migrate unknown questions
    unknown = sqlite_conn.execute("SELECT * FROM unknown_questions").fetchall()
    for u in unknown:
        pg_cur.execute(
            "INSERT INTO unknown_questions (id, question, asked_at, answered, session_id) VALUES (%s, %s, %s, %s, %s)",
            (u['id'], u['question'], u['asked_at'], u['answered'], u['session_id'])
        )
    print(f"✅ Migrated {len(unknown)} unknown questions")

    # Migrate chat history
    history = sqlite_conn.execute("SELECT * FROM chat_history").fetchall()
    for h in history:
        pg_cur.execute(
            "INSERT INTO chat_history (id, session_id, user_message, bot_response, timestamp) VALUES (%s, %s, %s, %s, %s)",
            (h['id'], h['session_id'], h['user_message'], h['bot_response'], h['timestamp'])
        )
    print(f"✅ Migrated {len(history)} chat history entries")

    pg_conn.commit()
    pg_conn.close()
    sqlite_conn.close()
    print("🎉 Migration complete!")


if __name__ == "__main__":
    print("🚀 Starting production database migration...")
    init_production_db()
    migrate_from_sqlite()