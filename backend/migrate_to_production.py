"""
Migrate data from SQLite to PostgreSQL
Run this locally with DATABASE_URL set to your production database
"""

import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_data():
    """Migrate all data from SQLite to PostgreSQL"""

    # Connect to SQLite (local)
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'lautech.db')
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found at {sqlite_path}")
        return False

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    print("✅ Connected to SQLite database")

    # Connect to PostgreSQL (production)
    pg_url = os.environ.get('DATABASE_URL')
    if not pg_url:
        print("❌ DATABASE_URL environment variable not set")
        return False

    pg_conn = psycopg2.connect(pg_url)
    pg_cur = pg_conn.cursor()
    print("✅ Connected to PostgreSQL database")

    # Clear existing data in PostgreSQL (optional)
    print("\n🔄 Clearing existing PostgreSQL data...")
    pg_cur.execute("DELETE FROM chat_history")
    pg_cur.execute("DELETE FROM unknown_questions")
    pg_cur.execute("DELETE FROM faqs")
    pg_conn.commit()

    # Migrate FAQs
    print("\n📚 Migrating FAQs...")
    faqs = sqlite_conn.execute("SELECT * FROM faqs").fetchall()
    for faq in faqs:
        try:
            pg_cur.execute(
                "INSERT INTO faqs (id, question, answer, category, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (faq['id'], faq['question'], faq['answer'], faq['category'], faq['created_at'], faq['updated_at'])
            )
        except Exception as e:
            print(f"   ❌ Error migrating FAQ {faq['id']}: {e}")

    pg_conn.commit()
    print(f"✅ Migrated {len(faqs)} FAQs")

    # Migrate unknown questions
    print("\n❓ Migrating unknown questions...")
    unknown = sqlite_conn.execute("SELECT * FROM unknown_questions").fetchall()
    for u in unknown:
        try:
            pg_cur.execute(
                "INSERT INTO unknown_questions (id, question, asked_at, answered, session_id) VALUES (%s, %s, %s, %s, %s)",
                (u['id'], u['question'], u['asked_at'], u['answered'], u['session_id'])
            )
        except Exception as e:
            print(f"   ❌ Error migrating unknown {u['id']}: {e}")

    pg_conn.commit()
    print(f"✅ Migrated {len(unknown)} unknown questions")

    # Migrate chat history
    print("\n💬 Migrating chat history...")
    history = sqlite_conn.execute("SELECT * FROM chat_history").fetchall()
    for h in history:
        try:
            pg_cur.execute(
                "INSERT INTO chat_history (id, session_id, user_message, bot_response, timestamp) VALUES (%s, %s, %s, %s, %s)",
                (h['id'], h['session_id'], h['user_message'], h['bot_response'], h['timestamp'])
            )
        except Exception as e:
            print(f"   ❌ Error migrating history {h['id']}: {e}")

    pg_conn.commit()
    print(f"✅ Migrated {len(history)} chat history entries")

    # Verify migration
    print("\n🔍 Verifying migration...")

    pg_cur.execute("SELECT COUNT(*) FROM faqs")
    faq_count = pg_cur.fetchone()[0]

    pg_cur.execute("SELECT COUNT(*) FROM unknown_questions")
    unknown_count = pg_cur.fetchone()[0]

    pg_cur.execute("SELECT COUNT(*) FROM chat_history")
    history_count = pg_cur.fetchone()[0]

    print(f"📊 PostgreSQL now has:")
    print(f"   - {faq_count} FAQs")
    print(f"   - {unknown_count} unknown questions")
    print(f"   - {history_count} chat history entries")

    # Close connections
    sqlite_conn.close()
    pg_conn.close()

    print("\n🎉 Migration complete!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 LAUTECH Chatbot - Production Migration Tool")
    print("=" * 60)

    success = migrate_data()

    if success:
        print("\n✅ Your data is now in production!")
        print("🚀 Deploy to Vercel and your chatbot will work!")
    else:
        print("\n❌ Migration failed. Check the errors above.")