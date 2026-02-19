from flask import Blueprint, request, jsonify
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database modules - ADD THE NEW FUNCTIONS
from database.config import (
    get_db_connection,
    add_unknown_question,
    add_chat_history,
    execute_query,  # NEW: For SELECT queries that return multiple rows
    execute_query_one,  # NEW: For SELECT queries that return one row
    IN_PRODUCTION  # NEW: To check environment
)
from database.models import FAQ

# Import NLP modules
from nlp.matcher import matcher, handle_greetings, handle_common_questions

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint with advanced NLP matching and greeting handling
    """
    try:
        # Get request data
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        question = data.get('question', '').strip()
        session_id = data.get('session_id', 'anonymous')

        if not question:
            return jsonify({'error': 'No question provided'}), 400

        print(f"\n📝 Received: '{question}' from session: {session_id}")

        # ===== STEP 1: Check for greetings first =====
        greeting_response = handle_greetings(question)
        if greeting_response:
            print(f"👋 Greeting detected: {greeting_response['match_type']}")
            response = {
                'question': question,
                'answer': greeting_response['answer'],
                'confidence': greeting_response['confidence'],
                'matched': True,
                'match_type': greeting_response['match_type'],
                'matched_by': greeting_response['matched_by'],
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id
            }

            # Save to chat history
            try:
                add_chat_history(
                    session_id=session_id,
                    user_message=question,
                    bot_response=response['answer']
                )
            except Exception as e:
                print(f"⚠️ Could not save chat history: {e}")

            return jsonify(response)

        # ===== STEP 2: Check for common questions about the bot =====
        common_response = handle_common_questions(question)
        if common_response:
            print(f"💬 Common question detected: {common_response['match_type']}")
            response = {
                'question': question,
                'answer': common_response['answer'],
                'confidence': common_response['confidence'],
                'matched': True,
                'match_type': common_response['match_type'],
                'matched_by': common_response['matched_by'],
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id
            }

            # Save to chat history
            try:
                add_chat_history(
                    session_id=session_id,
                    user_message=question,
                    bot_response=response['answer']
                )
            except Exception as e:
                print(f"⚠️ Could not save chat history: {e}")

            return jsonify(response)

        # ===== STEP 3: Find best match using advanced NLP =====
        best_match = matcher.find_best_match(question)

        # Prepare base response
        response = {
            'question': question,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        }

        # ===== STEP 4: Handle based on match type and confidence =====
        if best_match:
            confidence = best_match['confidence']
            match_type = best_match.get('match_type', 'unknown')

            if match_type == 'exact' or confidence >= 0.8:
                # High confidence - return answer directly
                response.update({
                    'answer': best_match['answer'],
                    'confidence': confidence,
                    'matched': True,
                    'faq_id': best_match['id'],
                    'match_type': 'exact',
                    'matched_by': best_match.get('matched_by', 'tfidf')
                })
                print(f"✅ Exact match: {confidence}")

            elif match_type == 'similar' or confidence >= 0.6:
                # Medium confidence - return with suggestions
                suggestions = matcher.get_suggestions(question, n=2)
                response.update({
                    'answer': f"I found a possible answer:\n\n{best_match['answer']}\n\n" +
                              (f"Did you mean: {suggestions[0]['question']}?" if suggestions else ""),
                    'confidence': confidence,
                    'matched': True,
                    'faq_id': best_match['id'],
                    'match_type': 'similar',
                    'matched_by': best_match.get('matched_by', 'tfidf'),
                    'suggestions': suggestions
                })
                print(f"⚠️ Similar match: {confidence}")

            elif match_type == 'low' or confidence >= 0.4:
                # Low confidence - ask for clarification
                suggestions = matcher.get_suggestions(question, n=3)
                suggestions_text = "\n".join(
                    [f"• {s['question']}" for s in suggestions]) if suggestions else "No related questions found."

                response.update({
                    'answer': "I'm not entirely sure what you're asking. Here are some related questions:\n\n" +
                              suggestions_text +
                              "\n\nCould you rephrase your question?",
                    'confidence': confidence,
                    'matched': False,
                    'match_type': 'low',
                    'matched_by': best_match.get('matched_by', 'tfidf'),
                    'suggestions': suggestions
                })
                print(f"❓ Low confidence: {confidence}")

            else:
                # Too low - log as unknown
                unknown_id = add_unknown_question(question, session_id)
                response.update({
                    'answer': "I'm not sure about this yet, but I've saved your question for review. I'll update you soon!",
                    'confidence': confidence,
                    'matched': False,
                    'match_type': 'unknown',
                    'matched_by': best_match.get('matched_by', 'tfidf'),
                    'unknown_id': unknown_id
                })
                print(f"❌ No match: logged as #{unknown_id}")

        else:
            # No match at all
            unknown_id = add_unknown_question(question, session_id)
            response.update({
                'answer': "I'm not sure about this yet, but I've saved your question for review. I'll update you soon!",
                'confidence': 0,
                'matched': False,
                'match_type': 'none',
                'matched_by': 'none',
                'unknown_id': unknown_id
            })
            print(f"❌ No match found: logged as #{unknown_id}")

        # ===== STEP 5: Save to chat history =====
        try:
            add_chat_history(
                session_id=session_id,
                user_message=question,
                bot_response=response['answer']
            )
        except Exception as e:
            print(f"⚠️ Could not save chat history: {e}")

        return jsonify(response)

    except Exception as e:
        print(f"🔥 Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'answer': "I'm having trouble processing your request right now. Please try again later.",
            'matched': False,
            'match_type': 'error'
        }), 500


@chat_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """Get chat history for a session"""
    try:
        conn = get_db_connection()

        if IN_PRODUCTION:
            # PostgreSQL version
            from psycopg2.extras import RealDictCursor
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                "SELECT * FROM chat_history WHERE session_id = %s ORDER BY timestamp DESC LIMIT 50",
                (session_id,)
            )
            history = cur.fetchall()
        else:
            # SQLite version
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM chat_history WHERE session_id = ? ORDER BY timestamp DESC LIMIT 50",
                (session_id,)
            )
            history = cur.fetchall()

        conn.close()

        return jsonify({
            'session_id': session_id,
            'history': [dict(row) for row in history]
        })

    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify({'error': 'Could not fetch history'}), 500


@chat_bp.route('/chat/suggestions', methods=['GET'])
def get_suggestions():
    """Get popular questions for suggestions"""
    try:
        conn = get_db_connection()

        if IN_PRODUCTION:
            # PostgreSQL version
            from psycopg2.extras import RealDictCursor
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # Get most frequently asked questions
            cur.execute("""
                SELECT user_message, COUNT(*) as count 
                FROM chat_history 
                GROUP BY user_message 
                ORDER BY count DESC 
                LIMIT 6
            """)
            suggestions = cur.fetchall()

            # If not enough history, get random FAQs
            if len(suggestions) < 6:
                cur.execute(
                    "SELECT question FROM faqs ORDER BY RANDOM() LIMIT %s",
                    (6 - len(suggestions),)
                )
                faqs = cur.fetchall()

                all_suggestions = [s['user_message'] for s in suggestions] + [f['question'] for f in faqs]
            else:
                all_suggestions = [s['user_message'] for s in suggestions]

        else:
            # SQLite version
            cur = conn.cursor()

            # Get most frequently asked questions
            cur.execute("""
                SELECT user_message, COUNT(*) as count 
                FROM chat_history 
                GROUP BY user_message 
                ORDER BY count DESC 
                LIMIT 6
            """)
            suggestions = cur.fetchall()

            # If not enough history, get random FAQs
            if len(suggestions) < 6:
                cur.execute(
                    "SELECT question FROM faqs ORDER BY RANDOM() LIMIT ?",
                    (6 - len(suggestions),)
                )
                faqs = cur.fetchall()

                all_suggestions = [s[0] for s in suggestions] + [f[0] for f in faqs]
            else:
                all_suggestions = [s[0] for s in suggestions]

        conn.close()

        return jsonify({
            'suggestions': all_suggestions[:6]
        })

    except Exception as e:
        print(f"Error getting suggestions: {e}")
        return jsonify({'suggestions': [
            "What is the cut-off mark for Medicine?",
            "How much are school fees?",
            "Where is the best area to live?",
            "Does LAUTECH accept second choice?",
            "How do I check admission status?",
            "Which area has the best electricity?"
        ]})