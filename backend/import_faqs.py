import json
import os
import sys
from database.config import init_database, add_faq, get_all_faqs


def import_faqs_from_json():
    """Import FAQs from JSON file to database"""

    # Initialize database first
    init_database()

    # Path to FAQs JSON file
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'faqs.json')

    # Check if file exists
    if not os.path.exists(json_path):
        print(f"❌ Error: {json_path} not found!")
        return False

    # Load FAQs from JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            faqs = json.load(file)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return False

    print(f"📚 Found {len(faqs)} FAQs in JSON file")

    # Add each FAQ to database
    success_count = 0
    for faq in faqs:
        try:
            add_faq(
                question=faq['question'],
                answer=faq['answer'],
                category=faq.get('category', 'Uncategorized')
            )
            success_count += 1
            print(f"✅ Added: {faq['question'][:50]}...")
        except Exception as e:
            print(f"❌ Failed to add: {faq['question'][:50]}... Error: {e}")

    print(f"\n🎉 Successfully imported {success_count} out of {len(faqs)} FAQs!")
    return True


def verify_import():
    """Verify that FAQs were imported correctly"""
    faqs = get_all_faqs()
    print(f"\n📊 Database now contains {len(faqs)} FAQs")

    # Show sample by category
    categories = {}
    for faq in faqs:
        cat = faq['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

    print("\n📁 FAQs by category:")
    for cat, count in categories.items():
        print(f"   {cat}: {count} FAQs")

    return faqs


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 LAUTECH FAQ Database Setup")
    print("=" * 50)

    if import_faqs_from_json():
        verify_import()

    print("\n✨ Database setup complete!")

