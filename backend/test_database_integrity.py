"""
Test database integrity and data quality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db_connection
from database.models import FAQ, UnknownQuestion

def test_database_integrity():
    """Test database structure and data quality"""

    print("DATABASE INTEGRITY TEST")
    print("=" * 60)

    conn = get_db_connection()

    # Test 1: Check if tables exist
    print("\n[1] Checking tables...")
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    table_names = [t['name'] for t in tables]
    expected_tables = ['faqs', 'unknown_questions', 'chat_history']

    for table in expected_tables:
        if table in table_names:
            print(f"   [OK] Table '{table}' exists")
        else:
            print(f"   [FAIL] Table '{table}' missing!")

    # Test 2: Check FAQs table structure
    print("\n[2] Checking FAQs table structure...")
    faq_columns = conn.execute("PRAGMA table_info(faqs)").fetchall()
    expected_faq_columns = ['id', 'question', 'answer', 'category', 'created_at', 'updated_at']

    column_names = [col['name'] for col in faq_columns]
    for col in expected_faq_columns:
        if col in column_names:
            print(f"   [OK] Column '{col}' exists")
        else:
            print(f"   [FAIL] Column '{col}' missing!")

    # Test 3: Check FAQ data quality
    print("\n[3] Checking FAQ data quality...")
    faqs = conn.execute("SELECT * FROM faqs").fetchall()

    print(f"   Total FAQs: {len(faqs)}")

    # Check for empty questions/answers
    empty_questions = [f for f in faqs if not f['question'] or not f['question'].strip()]
    empty_answers = [f for f in faqs if not f['answer'] or not f['answer'].strip()]

    if empty_questions:
        print(f"   [FAIL] Found {len(empty_questions)} FAQs with empty questions")
    else:
        print(f"   [OK] No empty questions")

    if empty_answers:
        print(f"   [FAIL] Found {len(empty_answers)} FAQs with empty answers")
    else:
        print(f"   [OK] No empty answers")

    # Test 4: Check categories
    print("\n[4] Checking categories...")
    categories = conn.execute(
        "SELECT category, COUNT(*) as count FROM faqs GROUP BY category"
    ).fetchall()

    for cat in categories:
        print(f"   {cat['category']}: {cat['count']} FAQs")

    # Test 5: Check for duplicate questions
    print("\n[5] Checking for duplicates...")
    questions = [f['question'] for f in faqs]
    duplicates = set([q for q in questions if questions.count(q) > 1])

    if duplicates:
        print(f"   [FAIL] Found duplicate questions: {duplicates}")
    else:
        print(f"   [OK] No duplicate questions")

    # Test 6: Check unknown questions table
    print("\n[6] Checking unknown questions...")
    unknown = conn.execute("SELECT * FROM unknown_questions").fetchall()
    unanswered = conn.execute(
        "SELECT * FROM unknown_questions WHERE answered = 0"
    ).fetchall()

    print(f"   Total unknown: {len(unknown)}")
    print(f"   Unanswered: {len(unanswered)}")

    conn.close()

    print("\n" + "=" * 60)
    print("Database integrity check complete!")

if __name__ == "__main__":
    test_database_integrity()