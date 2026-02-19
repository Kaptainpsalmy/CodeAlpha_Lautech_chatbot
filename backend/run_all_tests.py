"""
Run all tests in sequence
"""

import subprocess
import sys
import time

def run_test(name, command):
    """Run a test and return result"""
    print(f"\n{'='*60}")
    print(f" Running: {name}")
    print(f"{'='*60}")

    try:
        # Use Python with UTF-8 encoding
        result = subprocess.run(
            f'python {command}',
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running test: {e}")
        return False

def main():
    print("LAUTECH Chatbot - Complete Test Suite")
    print("Make sure your server is running on port 5000!")
    print("Press Ctrl+C to stop\n")

    time.sleep(2)

    tests = [
        ("Database Integrity", "test_database_integrity.py"),
        ("Comprehensive API Tests", "test_comprehensive.py"),
    ]

    results = []

    for name, command in tests:
        success = run_test(name, command)
        results.append((name, success))

    print("\n" + "="*60)
    print("Final Test Summary")
    print("="*60)

    all_passed = True
    for name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{status} - {name}")
        if not success:
            all_passed = False

    if all_passed:
        print("\nAll tests passed! Your chatbot is ready for production!")
    else:
        print("\nSome tests failed. Review the output above.")

if __name__ == "__main__":
    main()