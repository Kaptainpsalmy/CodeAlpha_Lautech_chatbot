"""
Standalone test script - no circular imports
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import custom mappings directly
from nlp.custom_mappings import get_custom_match

print("🚀 Testing Custom Mappings (Standalone)")
print("=" * 60)

test_questions = [
    "how much is school fees",
    "second choice jamb",
    "verification documents",
    "best place to live",
    "library hours",
    "cultists on campus",
    "cut off mark medicine",
    "post utme form",
]

for question in test_questions:
    match = get_custom_match(question)
    if match:
        print(f"✅ '{question[:30]}...' -> FAQ ID: {match['faq_id']} (conf: {match['confidence']})")
    else:
        print(f"❌ '{question[:30]}...' -> No custom match")

print("=" * 60)
print("\nNow testing with full matcher (this will use both systems):")

# Now test with full matcher
from nlp.matcher import matcher

for question in test_questions:
    match = matcher.find_best_match(question)
    if match:
        matched_by = match.get('matched_by', 'tfidf')
        print(f"✅ '{question[:30]}...' -> {match['question'][:40]}... ({match['confidence']:.3f}) [{matched_by}]")
    else:
        print(f"❌ '{question[:30]}...' -> No match")