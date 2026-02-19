"""
API Test Script
Run this to test all endpoints are working
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"


def print_separator():
    print("\n" + "=" * 60)


def test_home():
    """Test root endpoint"""
    print("🏠 Testing Home Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_chat():
    """Test chat endpoint with various questions"""
    print("\n💬 Testing Chat Endpoint...")

    test_questions = [
        "What is the cut off mark for medicine?",
        "How much is school fees?",
        "Where is LAUTECH located?",
        "This is a completely random question that shouldn't match anything"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n  Test {i}: '{question}'")

        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={
                    "question": question,
                    "session_id": "test_session_123"
                },
                headers={"Content-Type": "application/json"}
            )

            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"  Matched: {data.get('matched', False)}")
                print(f"  Confidence: {data.get('confidence', 0)}")
                print(f"  Answer: {data['answer'][:100]}...")
            else:
                print(f"  Error: {response.text}")

        except Exception as e:
            print(f"  ❌ Failed: {e}")

        time.sleep(0.5)  # Small delay between requests


def test_suggestions():
    """Test suggestions endpoint"""
    print("\n💡 Testing Suggestions Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/suggestions")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Suggestions:")
            for i, suggestion in enumerate(data.get('suggestions', []), 1):
                print(f"  {i}. {suggestion}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_unknown_stats():
    """Test unknown questions stats"""
    print("\n📊 Testing Unknown Questions Stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/unknown/stats")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total unknown: {data.get('total', 0)}")
            print(f"Unanswered: {data.get('unanswered', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("🧪 LAUTECH Chatbot API Tests")
    print_separator()

    tests = [
        ("Home", test_home),
        ("Health", test_health),
        ("Chat", test_chat),
        ("Suggestions", test_suggestions),
        ("Unknown Stats", test_unknown_stats)
    ]

    results = []

    for name, test_func in tests:
        print_separator()
        print(f"Running: {name}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((name, False))

    print_separator()
    print("📋 Test Summary")
    print_separator()

    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")
        if not result:
            all_passed = False

    print_separator()
    if all_passed:
        print("🎉 All tests passed! API is ready.")
    else:
        print("⚠️ Some tests failed. Check the output above.")


if __name__ == "__main__":
    run_all_tests()