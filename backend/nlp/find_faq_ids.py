"""
Find correct FAQ IDs in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db_connection

conn = get_db_connection()

print("=" * 60)
print("🔍 Finding Correct FAQ IDs")
print("=" * 60)

# Get all FAQs with their IDs
all_faqs = conn.execute("SELECT id, question FROM faqs ORDER BY id").fetchall()
print("\n📋 All FAQs in database:")
for faq in all_faqs:
    print(f"ID {faq['id']:2d}: {faq['question']}")

print("\n" + "=" * 60)
print("💰 Fee-related FAQs:")
fees = conn.execute(
    "SELECT id, question FROM faqs WHERE question LIKE '%fee%' OR question LIKE '%fees%'"
).fetchall()
for f in fees:
    print(f"ID {f['id']}: {f['question']}")

print("\n" + "=" * 60)
print("📝 Second Choice FAQs:")
second = conn.execute(
    "SELECT id, question FROM faqs WHERE question LIKE '%second%'"
).fetchall()
for s in second:
    print(f"ID {s['id']}: {s['question']}")

print("\n" + "=" * 60)
print("🏠 Accommodation FAQs:")
accommodation = conn.execute(
    "SELECT id, question FROM faqs WHERE question LIKE '%hostel%' OR question LIKE '%live%' OR question LIKE '%area%'"
).fetchall()
for a in accommodation:
    print(f"ID {a['id']}: {a['question']}")

print("\n" + "=" * 60)
print("📚 Library FAQs:")
library = conn.execute(
    "SELECT id, question FROM faqs WHERE question LIKE '%library%' OR question LIKE '%read%'"
).fetchall()
for l in library:
    print(f"ID {l['id']}: {l['question']}")

print("\n" + "=" * 60)
print("🔪 Cult/Security FAQs:")
cult = conn.execute(
    "SELECT id, question FROM faqs WHERE question LIKE '%cult%' OR question LIKE '%security%'"
).fetchall()
for c in cult:
    print(f"ID {c['id']}: {c['question']}")

print("\n" + "=" * 60)
print("🎓 Medicine FAQs:")
medicine = conn.execute(
    "SELECT id, question FROM faqs WHERE question LIKE '%med%'"
).fetchall()
for m in medicine:
    print(f"ID {m['id']}: {m['question']}")

conn.close()