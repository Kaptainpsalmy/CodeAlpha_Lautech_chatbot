import requests
import json
import time
import random
import string
from datetime import datetime
import os  # Add missing import
import sys

BASE_URL = "http://localhost:5000"
ADMIN_TOKEN = None

def print_header(text):
    """Print header without emojis"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def print_result(test_name, success, details=""):
    status = "PASSED" if success else "FAILED"
    print(f"{status} - {test_name}")
    if details and not success:
        print(f"      Details: {details}")

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        return response.status_code == 200
    except:
        return False

def test_home():
    """Test home endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        return response.status_code == 200
    except:
        return False

# ===== CHAT ENDPOINT TESTS =====

def test_chat_normal_questions():
    """Test normal FAQ questions"""
    questions = [
        ("What is the cut off mark for medicine?", True),
        ("How much are school fees?", True),
        ("Where is LAUTECH located?", True),
        ("Does LAUTECH accept second choice?", True),
        ("random question that should not match xyz123", False)
    ]

    results = []
    for question, should_match in questions:
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"question": question, "session_id": "test_session"}
            )

            if response.status_code == 200:
                data = response.json()
                matched = data.get('matched', False)

                if should_match and matched:
                    results.append(True)
                elif not should_match and not matched:
                    results.append(True)
                else:
                    results.append(False)
                    print(f"   [FAIL] '{question[:30]}...' matched={matched}, expected={should_match}")
            else:
                results.append(False)
        except:
            results.append(False)

    return all(results)

def test_chat_greetings():
    """Test greeting messages"""
    greetings = [
        "hi", "hello", "hey", "good morning",
        "how are you", "what's up", "good evening"
    ]

    success_count = 0
    for greeting in greetings:
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"question": greeting, "session_id": "test_session"}
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('match_type') in ['greeting', 'common']:
                    success_count += 1
                    print(f"   [OK] '{greeting}' → {data.get('match_type')}")
                else:
                    print(f"   [FAIL] '{greeting}' → {data.get('match_type', 'unknown')}")
            else:
                print(f"   [FAIL] '{greeting}' → HTTP {response.status_code}")
        except:
            print(f"   [FAIL] '{greeting}' → Exception")

    return success_count >= len(greetings) * 0.7

def test_chat_common_questions():
    """Test questions about the bot"""
    questions = [
        "what can you do",
        "who are you",
        "what is your name",
        "who created you",
        "thank you",
        "bye"
    ]

    success_count = 0
    for question in questions:
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"question": question, "session_id": "test_session"}
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('match_type') == 'common':
                    success_count += 1
                    print(f"   [OK] '{question}' → common match")
                else:
                    print(f"   [FAIL] '{question}' → {data.get('match_type', 'unknown')}")
            else:
                print(f"   [FAIL] '{question}' → HTTP {response.status_code}")
        except:
            print(f"   [FAIL] '{question}' → Exception")

    return success_count >= len(questions) * 0.8

# ===== EDGE CASE TESTS =====

def test_edge_cases():
    """Test edge cases"""
    edge_cases = [
        ("", False),                    # Empty string
        ("a", False),                    # Single character
        ("a" * 1000, False),             # Very long string
        ("!@#$%^&*()", False),           # Special characters only
        ("SELECT * FROM users", False),   # SQL injection attempt
        ("<script>alert('xss')</script>", False),  # XSS attempt
        ("What is the cut-off mark? 😊", True),  # With emoji
        ("cutt off markk for medcine", True),     # With typos
    ]

    results = []
    for question, should_handle in edge_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"question": question, "session_id": "test_session"}
            )

            if response.status_code == 200:
                # Should always return 200 even for bad input
                results.append(True)
                print(f"   [OK] '{question[:30]}...' → {response.status_code}")
            else:
                results.append(False)
                print(f"   [FAIL] '{question[:30]}...' → {response.status_code}")
        except:
            results.append(False)
            print(f"   [FAIL] '{question[:30]}...' → Exception")

    return all(results)

def test_unknown_logging():
    """Test that unknown questions are logged"""
    try:
        # Ask a random question
        random_question = f"test_question_{random.randint(1000, 9999)}"

        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"question": random_question, "session_id": "test_session"}
        )

        if response.status_code != 200:
            return False

        data = response.json()
        if not data.get('matched') and data.get('unknown_id'):
            print(f"   [OK] Unknown question logged with ID: {data['unknown_id']}")
            return True
        return False
    except:
        return False

# ===== ADMIN API TESTS =====

def test_admin_login():
    """Test admin login"""
    global ADMIN_TOKEN

    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"username": "admin", "password": "admin123"}
        )

        if response.status_code == 200:
            data = response.json()
            ADMIN_TOKEN = data.get('token')
            return bool(ADMIN_TOKEN)
        return False
    except:
        return False

def test_admin_verify():
    """Test token verification"""
    if not ADMIN_TOKEN:
        return False

    try:
        headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
        response = requests.get(f"{BASE_URL}/api/admin/verify", headers=headers)
        return response.status_code == 200
    except:
        return False

def test_admin_stats():
    """Test getting stats"""
    if not ADMIN_TOKEN:
        return False

    try:
        headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)

        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print(f"   Stats: {stats.get('total_faqs')} FAQs, {stats.get('unknown_unanswered')} unknown")
            return True
        return False
    except:
        return False

def test_admin_unknown():
    """Test getting unknown questions"""
    if not ADMIN_TOKEN:
        return False

    try:
        headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
        response = requests.get(f"{BASE_URL}/api/admin/unknown", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data.get('questions', []))} unknown questions")
            return True
        return False
    except:
        return False

def test_admin_faqs():
    """Test getting FAQs"""
    if not ADMIN_TOKEN:
        return False

    try:
        headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
        response = requests.get(f"{BASE_URL}/api/admin/faqs", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data.get('faqs', []))} FAQs")
            return True
        return False
    except:
        return False

# ===== DATABASE TESTS =====

def test_database_connection():
    """Test database connection by importing"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from database.config import get_db_connection

        conn = get_db_connection()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        return True
    except Exception as e:
        print(f"   [FAIL] DB Error: {e}")
        return False

# ===== SUGGESTIONS TESTS =====

def test_suggestions():
    """Test suggestions endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/chat/suggestions")

        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            print(f"   Got {len(suggestions)} suggestions")
            return len(suggestions) > 0
        return False
    except:
        return False

# ===== LOAD TEST =====

def test_load():
    """Simulate multiple simultaneous users"""
    import threading

    results = []

    def send_request(i):
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"question": f"Test question {i}", "session_id": f"load_test_{i}"},
                timeout=5
            )
            results.append(response.status_code == 200)
        except:
            results.append(False)

    threads = []
    for i in range(10):
        t = threading.Thread(target=send_request, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    success_rate = sum(results) / len(results) * 100
    print(f"   Load test: {success_rate:.1f}% success rate")

    return success_rate > 80

# ===== RUN ALL TESTS =====

def run_all_tests():
    """Run all test suites"""

    tests = [
        ("Health Check", test_health),
        ("Home Endpoint", test_home),
        ("Database Connection", test_database_connection),
        ("Normal Questions", test_chat_normal_questions),
        ("Greetings", test_chat_greetings),
        ("Common Questions", test_chat_common_questions),
        ("Edge Cases", test_edge_cases),
        ("Unknown Logging", test_unknown_logging),
        ("Suggestions", test_suggestions),
        ("Admin Login", test_admin_login),
        ("Admin Verify", test_admin_verify),
        ("Admin Stats", test_admin_stats),
        ("Admin Unknown", test_admin_unknown),
        ("Admin FAQs", test_admin_faqs),
        ("Load Test", test_load),
    ]

    print_header("LAUTECH Chatbot - Comprehensive Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    for name, test_func in tests:
        print(f"\n▶ Testing: {name}")
        try:
            result = test_func()
            results.append((name, result, ""))
        except Exception as e:
            results.append((name, False, str(e)))

    print_header("Test Results Summary")

    passed = 0
    failed = 0

    for name, result, error in results:
        if result:
            print(f"[OK] {name}")
            passed += 1
        else:
            print(f"[FAIL] {name} {error}")
            failed += 1

    print_header(f"Final Score: {passed}/{passed + failed} tests passed ({passed/(passed+failed)*100:.1f}%)")

    if failed == 0:
        print("\nALL TESTS PASSED! Your chatbot is ready for production!")
    else:
        print(f"\n{ failed} tests failed. Review the output above.")

    return passed == len(tests)

if __name__ == "__main__":
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=2)
    except:
        print("Cannot connect to server. Make sure it's running on port 5000")
        print("   Run: python run.py")
        exit(1)

    run_all_tests()