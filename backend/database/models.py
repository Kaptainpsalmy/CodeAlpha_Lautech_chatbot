from datetime import datetime
from .config import get_db_connection


class FAQ:
    """FAQ Model Class"""

    def __init__(self, id=None, question=None, answer=None, category=None, created_at=None, updated_at=None):
        self.id = id
        self.question = question
        self.answer = answer
        self.category = category
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @staticmethod
    def get_by_id(faq_id):
        """Get FAQ by ID"""
        conn = get_db_connection()
        faq = conn.execute("SELECT * FROM faqs WHERE id = ?", (faq_id,)).fetchone()
        conn.close()
        return dict(faq) if faq else None

    @staticmethod
    def search_by_question(query):
        """Search FAQs by question (for matching)"""
        conn = get_db_connection()
        faqs = conn.execute(
            "SELECT * FROM faqs WHERE question LIKE ? ORDER BY id",
            (f'%{query}%',)
        ).fetchall()
        conn.close()
        return [dict(faq) for faq in faqs]

    @staticmethod
    def update_answer(faq_id, new_answer):
        """Update FAQ answer"""
        conn = get_db_connection()
        conn.execute(
            "UPDATE faqs SET answer = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_answer, faq_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(faq_id):
        """Delete FAQ by ID"""
        conn = get_db_connection()
        conn.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
        conn.commit()
        conn.close()


class UnknownQuestion:
    """Unknown Question Model Class"""

    def __init__(self, id=None, question=None, asked_at=None, answered=False, session_id=None):
        self.id = id
        self.question = question
        self.asked_at = asked_at or datetime.now()
        self.answered = answered
        self.session_id = session_id

    @staticmethod
    def mark_as_answered(question_id):
        """Mark unknown question as answered"""
        conn = get_db_connection()
        conn.execute(
            "UPDATE unknown_questions SET answered = 1 WHERE id = ?",
            (question_id,)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_unanswered_count():
        """Get count of unanswered questions"""
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) as count FROM unknown_questions WHERE answered = 0").fetchone()
        conn.close()
        return count['count']


class ChatHistory:
    """Chat History Model Class"""

    @staticmethod
    def get_session_history(session_id, limit=50):
        """Get chat history for a session"""
        conn = get_db_connection()
        history = conn.execute(
            "SELECT * FROM chat_history WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit)
        ).fetchall()
        conn.close()
        return [dict(h) for h in history]

    @staticmethod
    def clear_session(session_id):
        """Clear chat history for a session"""
        conn = get_db_connection()
        conn.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()