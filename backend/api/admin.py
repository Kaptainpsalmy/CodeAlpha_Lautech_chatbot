from flask import Blueprint, request, jsonify, session
import sys
import os
import sqlite3
from datetime import datetime, timedelta
import hashlib
import secrets

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db_connection, add_faq
from database.models import FAQ, UnknownQuestion
from nlp.matcher import matcher

admin_bp = Blueprint('admin', __name__)

# Simple admin authentication (in production, use proper auth)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Change in production!
ADMIN_TOKEN = secrets.token_hex(16)  # Generate random token


def verify_token(auth_header):
    """Simple token verification"""
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ')[1]
    return token == ADMIN_TOKEN


@admin_bp.route('/login', methods=['POST'])
def login():
    """Admin login - returns token"""
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': ADMIN_TOKEN,
                'user': {
                    'username': username,
                    'role': 'admin'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/verify', methods=['GET'])
def verify():
    """Verify token is valid"""
    auth_header = request.headers.get('Authorization')

    if verify_token(auth_header):
        return jsonify({
            'success': True,
            'message': 'Token valid',
            'user': {'username': ADMIN_USERNAME, 'role': 'admin'}
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid token'
        }), 401


@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get comprehensive dashboard statistics"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db_connection()

        # Total FAQs
        total_faqs = conn.execute("SELECT COUNT(*) as count FROM faqs").fetchone()

        # Unknown questions stats
        unknown_total = conn.execute("SELECT COUNT(*) as count FROM unknown_questions").fetchone()
        unknown_unanswered = conn.execute(
            "SELECT COUNT(*) as count FROM unknown_questions WHERE answered = 0").fetchone()

        # Total chats
        total_chats = conn.execute("SELECT COUNT(*) as count FROM chat_history").fetchone()

        # Chats today
        today = datetime.now().date()
        chats_today = conn.execute(
            "SELECT COUNT(*) as count FROM chat_history WHERE date(timestamp) = ?",
            (today.isoformat(),)
        ).fetchone()

        # Popular questions (top 10)
        popular = conn.execute("""
            SELECT user_message, COUNT(*) as frequency 
            FROM chat_history 
            GROUP BY user_message 
            ORDER BY frequency DESC 
            LIMIT 10
        """).fetchall()

        # Unknown questions trend (last 7 days)
        trend = []
        for i in range(6, -1, -1):
            date = (today - timedelta(days=i)).isoformat()
            count = conn.execute(
                "SELECT COUNT(*) as count FROM unknown_questions WHERE date(asked_at) = ?",
                (date,)
            ).fetchone()
            trend.append({
                'date': date,
                'count': count['count'] if count else 0
            })

        # Category distribution
        categories = conn.execute("""
            SELECT category, COUNT(*) as count 
            FROM faqs 
            GROUP BY category 
            ORDER BY count DESC
        """).fetchall()

        conn.close()

        return jsonify({
            'success': True,
            'stats': {
                'total_faqs': total_faqs['count'] if total_faqs else 0,
                'unknown_total': unknown_total['count'] if unknown_total else 0,
                'unknown_unanswered': unknown_unanswered['count'] if unknown_unanswered else 0,
                'total_chats': total_chats['count'] if total_chats else 0,
                'chats_today': chats_today['count'] if chats_today else 0,
                'popular_questions': [dict(p) for p in popular],
                'unknown_trend': trend,
                'categories': [dict(c) for c in categories]
            }
        })

    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/unknown', methods=['GET'])
def get_unknown():
    """Get all unknown questions with filtering and pagination"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Get query parameters
        filter_by = request.args.get('filter', 'all')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit

        conn = get_db_connection()

        # Build query based on filter
        if filter_by == 'unanswered':
            query = "SELECT * FROM unknown_questions WHERE answered = 0 ORDER BY asked_at DESC LIMIT ? OFFSET ?"
            count_query = "SELECT COUNT(*) as count FROM unknown_questions WHERE answered = 0"
            params = [limit, offset]
        elif filter_by == 'answered':
            query = "SELECT * FROM unknown_questions WHERE answered = 1 ORDER BY asked_at DESC LIMIT ? OFFSET ?"
            count_query = "SELECT COUNT(*) as count FROM unknown_questions WHERE answered = 1"
            params = [limit, offset]
        else:
            query = "SELECT * FROM unknown_questions ORDER BY asked_at DESC LIMIT ? OFFSET ?"
            count_query = "SELECT COUNT(*) as count FROM unknown_questions"
            params = [limit, offset]

        # Get total count
        total = conn.execute(count_query).fetchone()
        total_count = total['count'] if total else 0

        # Get paginated results
        questions = conn.execute(query, params).fetchall()
        conn.close()

        return jsonify({
            'success': True,
            'questions': [dict(q) for q in questions],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        })

    except Exception as e:
        print(f"Error getting unknown questions: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/unknown/<int:question_id>', methods=['GET'])
def get_unknown_detail(question_id):
    """Get details of a specific unknown question"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db_connection()
        question = conn.execute(
            "SELECT * FROM unknown_questions WHERE id = ?",
            (question_id,)
        ).fetchone()
        conn.close()

        if not question:
            return jsonify({'error': 'Question not found'}), 404

        return jsonify({
            'success': True,
            'question': dict(question)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/unknown/answer', methods=['POST'])
def answer_unknown():
    """Add answer to unknown question and move to FAQs"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()

        question_id = data.get('question_id')
        answer = data.get('answer', '').strip()
        category = data.get('category', 'General').strip()

        if not question_id or not answer:
            return jsonify({'error': 'Missing required fields'}), 400

        # Get the unknown question
        conn = get_db_connection()
        unknown = conn.execute(
            "SELECT question FROM unknown_questions WHERE id = ?",
            (question_id,)
        ).fetchone()

        if not unknown:
            conn.close()
            return jsonify({'error': 'Question not found'}), 404

        # Add to FAQs
        new_faq_id = add_faq(unknown['question'], answer, category)

        # Mark unknown as answered
        conn.execute(
            "UPDATE unknown_questions SET answered = 1 WHERE id = ?",
            (question_id,)
        )
        conn.commit()
        conn.close()

        # Refresh matcher index
        matcher.load_faqs()

        return jsonify({
            'success': True,
            'message': 'Answer added to FAQs',
            'faq_id': new_faq_id
        })

    except Exception as e:
        print(f"Error answering unknown: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/unknown/bulk-answer', methods=['POST'])
def bulk_answer_unknown():
    """Answer multiple unknown questions at once"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        answers = data.get('answers', [])

        results = []
        for item in answers:
            question_id = item.get('question_id')
            answer = item.get('answer')
            category = item.get('category', 'General')

            if question_id and answer:
                try:
                    conn = get_db_connection()
                    unknown = conn.execute(
                        "SELECT question FROM unknown_questions WHERE id = ?",
                        (question_id,)
                    ).fetchone()

                    if unknown:
                        new_faq_id = add_faq(unknown['question'], answer, category)

                        conn.execute(
                            "UPDATE unknown_questions SET answered = 1 WHERE id = ?",
                            (question_id,)
                        )
                        conn.commit()

                        results.append({
                            'question_id': question_id,
                            'success': True,
                            'faq_id': new_faq_id
                        })
                    conn.close()
                except Exception as e:
                    results.append({
                        'question_id': question_id,
                        'success': False,
                        'error': str(e)
                    })

        # Refresh matcher index
        matcher.load_faqs()

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/faqs', methods=['GET'])
def get_faqs():
    """Get all FAQs with filtering and pagination"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Get query parameters
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit

        conn = get_db_connection()

        # Build query with filters
        query = "SELECT * FROM faqs WHERE 1=1"
        count_query = "SELECT COUNT(*) as count FROM faqs WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            count_query += " AND category = ?"
            params.append(category)

        if search:
            query += " AND (question LIKE ? OR answer LIKE ?)"
            count_query += " AND (question LIKE ? OR answer LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term])

        # Get total count
        total = conn.execute(count_query, params[:len(params)]).fetchone()
        total_count = total['count'] if total else 0

        # Add pagination
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        # Get paginated results
        faqs = conn.execute(query, params).fetchall()
        conn.close()

        # Get all categories for filter dropdown
        conn = get_db_connection()
        categories = conn.execute("SELECT DISTINCT category FROM faqs ORDER BY category").fetchall()
        conn.close()

        return jsonify({
            'success': True,
            'faqs': [dict(f) for f in faqs],
            'categories': [c['category'] for c in categories],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        })

    except Exception as e:
        print(f"Error getting FAQs: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/faqs/<int:faq_id>', methods=['GET'])
def get_faq(faq_id):
    """Get a single FAQ by ID"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db_connection()
        faq = conn.execute(
            "SELECT * FROM faqs WHERE id = ?",
            (faq_id,)
        ).fetchone()
        conn.close()

        if not faq:
            return jsonify({'error': 'FAQ not found'}), 404

        return jsonify({
            'success': True,
            'faq': dict(faq)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/faqs', methods=['POST'])
def create_faq():
    """Create new FAQ"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()

        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()
        category = data.get('category', 'General').strip()

        if not question or not answer:
            return jsonify({'error': 'Question and answer are required'}), 400

        # Check if question already exists
        conn = get_db_connection()
        existing = conn.execute(
            "SELECT id FROM faqs WHERE question = ?",
            (question,)
        ).fetchone()

        if existing:
            conn.close()
            return jsonify({'error': 'A FAQ with this question already exists'}), 400

        conn.close()

        # Add to database
        faq_id = add_faq(question, answer, category)

        # Refresh matcher index
        matcher.load_faqs()

        return jsonify({
            'success': True,
            'message': 'FAQ created successfully',
            'faq_id': faq_id
        }), 201

    except Exception as e:
        print(f"Error creating FAQ: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/faqs/<int:faq_id>', methods=['PUT'])
def update_faq(faq_id):
    """Update existing FAQ"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()

        question = data.get('question')
        answer = data.get('answer')
        category = data.get('category')

        conn = get_db_connection()

        # Check if FAQ exists
        existing = conn.execute(
            "SELECT id FROM faqs WHERE id = ?",
            (faq_id,)
        ).fetchone()

        if not existing:
            conn.close()
            return jsonify({'error': 'FAQ not found'}), 404

        # Build update query dynamically
        updates = []
        params = []

        if question is not None:
            updates.append("question = ?")
            params.append(question)

        if answer is not None:
            updates.append("answer = ?")
            params.append(answer)

        if category is not None:
            updates.append("category = ?")
            params.append(category)

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE faqs SET {', '.join(updates)} WHERE id = ?"
            params.append(faq_id)

            conn.execute(query, params)
            conn.commit()

        conn.close()

        # Refresh matcher index
        matcher.load_faqs()

        return jsonify({
            'success': True,
            'message': 'FAQ updated successfully'
        })

    except Exception as e:
        print(f"Error updating FAQ: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/faqs/<int:faq_id>', methods=['DELETE'])
def delete_faq(faq_id):
    """Delete FAQ"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db_connection()

        # Check if FAQ exists
        existing = conn.execute(
            "SELECT id FROM faqs WHERE id = ?",
            (faq_id,)
        ).fetchone()

        if not existing:
            conn.close()
            return jsonify({'error': 'FAQ not found'}), 404

        # Delete the FAQ
        conn.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
        conn.commit()
        conn.close()

        # Refresh matcher index
        matcher.load_faqs()

        return jsonify({
            'success': True,
            'message': 'FAQ deleted successfully'
        })

    except Exception as e:
        print(f"Error deleting FAQ: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/faqs/bulk', methods=['POST'])
def bulk_import_faqs():
    """Bulk import FAQs from JSON"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        faqs = data.get('faqs', [])

        results = []
        for faq in faqs:
            question = faq.get('question', '').strip()
            answer = faq.get('answer', '').strip()
            category = faq.get('category', 'General').strip()

            if question and answer:
                try:
                    faq_id = add_faq(question, answer, category)
                    results.append({
                        'question': question[:50],
                        'success': True,
                        'faq_id': faq_id
                    })
                except Exception as e:
                    results.append({
                        'question': question[:50],
                        'success': False,
                        'error': str(e)
                    })

        # Refresh matcher index
        matcher.load_faqs()

        return jsonify({
            'success': True,
            'imported': len([r for r in results if r['success']]),
            'failed': len([r for r in results if not r['success']]),
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get detailed analytics"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db_connection()

        # Time range (default: last 30 days)
        days = int(request.args.get('days', 30))
        start_date = (datetime.now() - timedelta(days=days)).date()

        # Daily chat counts
        daily_chats = conn.execute("""
            SELECT date(timestamp) as date, COUNT(*) as count
            FROM chat_history
            WHERE date(timestamp) >= ?
            GROUP BY date(timestamp)
            ORDER BY date
        """, (start_date.isoformat(),)).fetchall()

        # Unknown questions by day
        daily_unknown = conn.execute("""
            SELECT date(asked_at) as date, COUNT(*) as count
            FROM unknown_questions
            WHERE date(asked_at) >= ?
            GROUP BY date(asked_at)
            ORDER BY date
        """, (start_date.isoformat(),)).fetchall()

        # Response rate (matched vs unknown)
        total_queries = conn.execute(
            "SELECT COUNT(*) as count FROM chat_history"
        ).fetchone()['count']

        unknown_count = conn.execute(
            "SELECT COUNT(*) as count FROM unknown_questions WHERE answered = 0"
        ).fetchone()['count']

        response_rate = ((total_queries - unknown_count) / total_queries * 100) if total_queries > 0 else 0

        conn.close()

        return jsonify({
            'success': True,
            'analytics': {
                'daily_chats': [dict(d) for d in daily_chats],
                'daily_unknown': [dict(d) for d in daily_unknown],
                'response_rate': round(response_rate, 2),
                'total_queries': total_queries,
                'pending_unknown': unknown_count
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # You can store settings in a database table
        # For now, return default settings
        return jsonify({
            'success': True,
            'settings': {
                'similarity_threshold': matcher.thresholds['similar'],
                'exact_threshold': matcher.thresholds['exact'],
                'enable_suggestions': True,
                'enable_tts': True,
                'auto_refresh': True
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    auth_header = request.headers.get('Authorization')

    if not verify_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()

        # Update matcher thresholds if provided
        if 'similarity_threshold' in data:
            matcher.thresholds['similar'] = float(data['similarity_threshold'])

        if 'exact_threshold' in data:
            matcher.thresholds['exact'] = float(data['exact_threshold'])

        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500