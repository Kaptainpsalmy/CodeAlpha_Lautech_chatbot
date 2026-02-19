"""
Quick optimization script to test improved matching
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp.matcher import matcher
from nlp.preprocess import preprocessor

# Test questions with expected matches
test_cases = [
    ("cut off mark for medicine", "What is the cut-off mark for my course?"),
    ("how much is school fees", "How much are the school fees?"),
    ("best place to live", "Which area is the quietest for academic-focused students?"),
    ("second choice jamb", "Does LAUTECH accept second-choice candidates?"),
    ("hostel accommodation", "Does the school provide hostel accommodation?"),
    ("library reading hours", "What is the best place to read in LAUTECH?"),
    ("cultists on campus", "Are there cultists in LAUTECH?"),
    ("post utme form", "Is there a Post-UTME exam?"),
    ("age limit for admission", "What is the minimum age for admission?"),
    ("verification documents", "What documents are needed for the verification exercise after admission?")
]

print("🚀 Testing Optimized Matching")
print("=" * 80)
print(f"{'Question':<30} {'Expected Match':<40} {'Confidence':<10}")
print("=" * 80)

for question, expected in test_cases:
    match = matcher.find_best_match(question)

    if match:
        is_correct = "✅" if expected in match['question'] else "❌"
        print(f"{question:<30} {match['question'][:40]:<40} {match['confidence']:.3f} {is_correct}")
    else:
        print(f"{question:<30} {'NO MATCH':<40} {'0.000':<10} ❌")

print("=" * 80)