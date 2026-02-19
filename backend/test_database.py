from database.config import (
    init_database,
    get_all_faqs,
    add_unknown_question,
    get_unknown_questions,
    add_chat_history
)
from database.models import FAQ, UnknownQuestion, ChatHistory


def run_tests():
    """Test all database functions"""

    print("🧪 Running Database Tests...")
    print("=" * 50)

    # Test 1: Initialize database
    print("\n1️⃣ Testing database initialization...")
    init_database()
    print("   ✅ Database initialized")

    # Test 2: Get all FAQs
    print("\n2️⃣ Testing FAQ retrieval...")
    faqs = get_all_faqs()
    print(f"   ✅ Retrieved {len(faqs)} FAQs")
    if faqs:
        print(f"   📝 Sample: {faqs[0]['question'][:50]}...")

    # Test 3: Add unknown question
    print("\n3️⃣ Testing unknown question logging...")
    q_id = add_unknown_question("What is the best hostel?", session_id="test123")
    print(f"   ✅ Added unknown question with ID: {q_id}")

    # Test 4: Get unknown questions
    print("\n4️⃣ Testing unknown question retrieval...")
    unknown = get_unknown_questions(answered=False)
    print(f"   ✅ Found {len(unknown)} unanswered questions")

    # Test 5: Mark question as answered
    print("\n5️⃣ Testing marking question as answered...")
    if unknown:
        UnknownQuestion.mark_as_answered(unknown[0]['id'])
        print(f"   ✅ Marked question ID {unknown[0]['id']} as answered")

    # Test 6: Add chat history
    print("\n6️⃣ Testing chat history...")
    add_chat_history(
        session_id="test123",
        user_message="What is the cut-off mark?",
        bot_response="The cut-off mark is 170."
    )
    print("   ✅ Added chat history")

    # Test 7: Get session history
    print("\n7️⃣ Testing session history retrieval...")
    history = ChatHistory.get_session_history("test123")
    print(f"   ✅ Retrieved {len(history)} messages")

    # Test 8: Search FAQ
    print("\n8️⃣ Testing FAQ search...")
    if faqs:
        search_results = FAQ.search_by_question("admission")
        print(f"   ✅ Found {len(search_results)} FAQs matching 'admission'")

    # Test 9: Get unanswered count
    print("\n9️⃣ Testing unanswered count...")
    count = UnknownQuestion.get_unanswered_count()
    print(f"   ✅ {count} unanswered questions in queue")

    print("\n" + "=" * 50)
    print("🎉 All tests completed successfully!")

    return True


if __name__ == "__main__":
    run_tests()