import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'lautech.db')

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

print("📊 DATABASE SUMMARY")
print("=" * 50)

# Check FAQs
faqs = conn.execute("SELECT COUNT(*) as count FROM faqs").fetchone()
print(f"FAQs table: {faqs['count']} records")

# Check categories
categories = conn.execute("SELECT category, COUNT(*) as count FROM faqs GROUP BY category").fetchall()
print("\nCategories:")
for cat in categories:
    print(f"  - {cat['category']}: {cat['count']} FAQs")

# Show sample
print("\nSample FAQs:")
sample = conn.execute("SELECT question, category FROM faqs LIMIT 3").fetchall()
for i, faq in enumerate(sample, 1):
    print(f"  {i}. [{faq['category']}] {faq['question'][:60]}...")

conn.close()