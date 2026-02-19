from flask import Blueprint, request, jsonify
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db_connection, add_unknown_question
from database.models import UnknownQuestion

unknown_bp = Blueprint('unknown', __name__)


@unknown_bp.route('/unknown/<int:question_id>', methods=['PUT'])
def mark_as_answered(question_id):
    """Mark an unknown question as answered"""
    try:
        UnknownQuestion.mark_as_answered(question_id)
        return jsonify({'success': True, 'message': 'Question marked as answered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@unknown_bp.route('/unknown/stats', methods=['GET'])
def get_unknown_stats():
    """Get statistics about unknown questions"""
    try:
        conn = get_db_connection()

        # Total unknown questions
        total = conn.execute("SELECT COUNT(*) as count FROM unknown_questions").fetchone()

        # Unanswered count
        unanswered = conn.execute("SELECT COUNT(*) as count FROM unknown_questions WHERE answered = 0").fetchone()

        # Most common unknown questions
        common = conn.execute("""
            SELECT question, COUNT(*) as frequency 
            FROM unknown_questions 
            GROUP BY question 
            ORDER BY frequency DESC 
            LIMIT 10
        """).fetchall()

        conn.close()

        return jsonify({
            'total': total['count'] if total else 0,
            'unanswered': unanswered['count'] if unanswered else 0,
            'common': [dict(q) for q in common]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500