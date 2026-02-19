"""
Check actual FAQ IDs in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db_connection

conn = get_db_connection()
faqs = conn.execute("SELECT id, question, category FROM faqs ORDER BY id").fetchall()
conn.close()

print("📋 FAQ IDs in Database")
print("=" * 80)
print(f"{'ID':<5} {'Category':<15} {'Question'}")
print("=" * 80)

for faq in faqs:
    print(f"{faq['id']:<5} {faq['category']:<15} {faq['question'][:60]}...")

print("=" * 80)
print(f"Total FAQs: {len(faqs)}")