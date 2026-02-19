"""
Test script for the NLP matcher
Run this to see how well the matcher performs
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp.matcher import matcher
from nlp.preprocess import preprocessor


def test_preprocessing():
    """Test text preprocessing"""
    print("\n🧪 Testing Text Preprocessing")
    print("=" * 60)

    test_texts = [
        "What is the cut-off mark for Medicine at LAUTECH?",
        "How much are the school fees for freshers?",
        "Where can I find accommodation near campus?",
        "Does LAUTECH accept second choice?",
        "Tell me about hostel facilities"
    ]

    for text in test_texts:
        processed = preprocessor.process(text)
        keywords = preprocessor.extract_keywords(text)
        print(f"\nOriginal: {text}")
        print(f"Processed: {processed}")
        print(f"Keywords: {keywords}")


def test_matching():
    """Test FAQ matching"""
    print("\n🧪 Testing FAQ Matching")
    print("=" * 60)

    test_questions = [
        "cut off mark for medicine",
        "how much is school fees",
        "best place to live",
        "second choice jamb",
        "hostel accommodation",
        "library reading hours",
        "cultists on campus",
        "post utme form",
        "age limit for admission",
        "verification documents"
    ]

    results = {
        'exact': 0,
        'similar': 0,
        'low': 0,
        'unknown': 0
    }

    for q in test_questions:
        print(f"\n📝 Question: {q}")
        match = matcher.find_best_match(q)

        if match:
            print(f"   Match: {match['question'][:80]}")
            print(f"   Confidence: {match['confidence']:.3f}")
            print(f"   Type: {match.get('match_type', 'unknown')}")

            # Count results
            match_type = match.get('match_type', 'unknown')
            if match_type in results:
                results[match_type] += 1
            else:
                results['unknown'] += 1

            # Show suggestions if available
            if match.get('all_matches'):
                print("   Other matches:")
                for alt in match['all_matches'][:2]:
                    print(f"     • {alt['question'][:60]} ({alt['confidence']:.3f})")
        else:
            print("   ❌ No match found")
            results['unknown'] += 1

    print("\n" + "=" * 60)
    print("📊 Matching Summary")
    print("=" * 60)
    for match_type, count in results.items():
        percentage = (count / len(test_questions)) * 100
        print(f"{match_type.title():10}: {count:2} questions ({percentage:.0f}%)")


def test_suggestions():
    """Test suggestion generation"""
    print("\n🧪 Testing Suggestions")
    print("=" * 60)

    test_questions = [
        "fees",
        "accommodation",
        "admission",
        "medicine"
    ]

    for q in test_questions:
        print(f"\n📝 Question: '{q}'")
        suggestions = matcher.get_suggestions(q, n=3)

        if suggestions:
            print("   Suggestions:")
            for s in suggestions:
                print(f"     • {s['question']} ({s['confidence']:.3f})")
        else:
            print("   No suggestions")


if __name__ == "__main__":
    print("🚀 LAUTECH NLP Matcher Test Suite")
    print("=" * 60)

    # Run tests
    test_preprocessing()
    test_matching()
    test_suggestions()

    print("\n✅ Tests complete!")