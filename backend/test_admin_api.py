"""
Test script for Admin API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"
TOKEN = None


def print_separator():
    print("\n" + "=" * 60)


def test_login():
    """Test admin login"""
    print("\n🔐 Testing Admin Login...")

    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        global TOKEN
        TOKEN = data['token']
        print(f"✅ Login successful! Token: {TOKEN[:20]}...")
        return True
    else:
        print(f"❌ Login failed: {response.text}")
        return False


def test_get_stats():
    """Test getting dashboard stats"""
    print("\n📊 Testing Get Stats...")

    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        stats = data['stats']
        print(f"✅ Total FAQs: {stats['total_faqs']}")
        print(f"✅ Unknown questions: {stats['unknown_unanswered']}")
        print(f"✅ Total chats: {stats['total_chats']}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_get_unknown():
    """Test getting unknown questions"""
    print("\n❓ Testing Get Unknown Questions...")

    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/api/admin/unknown", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data['questions'])} unknown questions")
        if data['questions']:
            print(f"   First: {data['questions'][0]['question'][:50]}...")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_get_faqs():
    """Test getting FAQs"""
    print("\n📚 Testing Get FAQs...")

    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/api/admin/faqs", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data['faqs'])} FAQs")
        print(f"✅ Categories: {', '.join(data['categories'][:5])}...")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Admin API")
    print_separator()

    tests = [
        ("Login", test_login),
        ("Get Stats", test_get_stats),
        ("Get Unknown", test_get_unknown),
        ("Get FAQs", test_get_faqs)
    ]

    results = []
    for name, test_func in tests:
        print_separator()
        print(f"Running: {name}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error: {e}")
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
        print("🎉 All admin API tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above.")