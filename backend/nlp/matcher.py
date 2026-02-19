"""
Advanced FAQ matcher using TF-IDF and cosine similarity
"""

import sys
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from datetime import datetime
import string

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db_connection
from nlp.preprocess import preprocessor
from nlp.custom_mappings import get_custom_match


# ===== STANDALONE FUNCTIONS FOR GREETINGS =====
# These are outside the class so they can be imported directly

def handle_greetings(user_question):
    """
    Handle basic greetings and common phrases
    Returns response if matched, None otherwise
    """
    question_lower = user_question.lower().strip()

    # Remove punctuation for better matching
    question_lower = question_lower.translate(str.maketrans('', '', string.punctuation))

    # Comprehensive greetings dictionary
    greetings = {
        # Basic greetings
        'hi': "Hello! 👋 How can I help you with LAUTECH today?",
        'hello': "Hi there! 👋 What would you like to know about LAUTECH?",
        'hey': "Hey! 👋 Ask me anything about LAUTECH admissions, fees, or campus life.",
        'howdy': "Howdy! 👋 Ready to answer your LAUTECH questions!",
        'good morning': "Good morning! ☀️ Hope you're having a great day. What LAUTECH info do you need?",
        'good afternoon': "Good afternoon! 🌤️ How can I assist you with LAUTECH?",
        'good evening': "Good evening! 🌙 I'm here to answer your LAUTECH questions.",
        'good day': "Good day! 👋 What would you like to know about LAUTECH?",

        # Variations
        'hello there': "Hello! 👋 How can I help with LAUTECH today?",
        'hi there': "Hi! 👋 Ask me anything about LAUTECH!",
        'hey there': "Hey! 👋 Ready to help with your LAUTECH questions!",

        # How are you
        'how are you': "I'm doing great, thanks for asking! 🤖 Ready to help you with LAUTECH questions. How can I assist?",
        'how are you doing': "I'm functioning perfectly! 😊 What LAUTECH information do you need?",
        'how are things': "All systems operational! 👍 What can I help you with regarding LAUTECH?",
        'you good': "I'm good! 👍 Ask me anything about LAUTECH!",

        # What's up
        'whats up': "Not much, just waiting to answer your LAUTECH questions! 😊 What's up with you?",
        'sup': "Sup! 👋 Got any LAUTECH questions for me?",
        'wassup': "Hey there! 👋 Ready to help with LAUTECH info!",
        'whats good': "All good! 👍 What LAUTECH questions do you have?",

        # Welcome
        'welcome': "Thank you! 👋 Feel free to ask me anything about LAUTECH.",
        'nice to meet you': "Nice to meet you too! 🎉 I'm here to help with all your LAUTECH questions.",

        # Politeness
        'pleased to meet you': "Likewise! 👋 Ask me anything about LAUTECH!",
        'good to see you': "Good to see you too! 😊 What LAUTECH info do you need?",
        'good to meet you': "Great to meet you! 🎓 Ready to answer your LAUTECH questions!",
    }

    # Check exact matches and partial matches
    for greeting, response in greetings.items():
        if greeting in question_lower or question_lower in greeting:
            return {
                'answer': response,
                'confidence': 1.0,
                'match_type': 'greeting',
                'matched_by': 'greeting_handler'
            }

    # Check if question contains greeting words
    greeting_words = ['hi', 'hello', 'hey', 'howdy', 'greetings', 'good morning',
                      'good afternoon', 'good evening', 'good day', 'morning', 'afternoon', 'evening']

    if any(word in question_lower for word in greeting_words):
        return {
            'answer': "Hello! 👋 I'm the LAUTECH assistant. You can ask me about:\n\n" +
                      "• **Admissions** - cut-off marks, requirements, JAMB\n" +
                      "• **Fees** - school fees, payments, installments\n" +
                      "• **Accommodation** - hostels, areas, security\n" +
                      "• **Academics** - courses, CGPA, library\n" +
                      "• **Campus Life** - food, electricity, transport\n\n" +
                      "What would you like to know?",
            'confidence': 0.9,
            'match_type': 'greeting',
            'matched_by': 'greeting_handler'
        }

    return None


def handle_common_questions(user_question):
    """
    Handle common questions about the bot itself
    """
    question_lower = user_question.lower().strip()

    common_patterns = {
        'what can you do': "I can answer questions about LAUTECH including:\n\n" +
                           "📚 **Admissions** - Cut-off marks, requirements, JAMB, Post-UTME\n" +
                           "💰 **Fees** - School fees, payment methods, installments\n" +
                           "🏠 **Accommodation** - Hostels, areas to live, security, electricity\n" +
                           "📖 **Academics** - Courses, CGPA calculation, library, reading spots\n" +
                           "🍽️ **Campus Life** - Food places, restaurants, hangout spots\n" +
                           "🚍 **Transport** - Fares, bike policy, areas\n" +
                           "❓ **General Info** - Location, VC, protests, current events\n\n" +
                           "Just ask me anything about LAUTECH!",

        'what can you help with': "I specialize in LAUTECH information:\n\n" +
                                  "• Admissions & requirements\n" +
                                  "• School fees & payments\n" +
                                  "• Accommodation & hostels\n" +
                                  "• Courses & academics\n" +
                                  "• Campus life & security\n" +
                                  "• Transport & amenities\n\n" +
                                  "What would you like to know?",

        'what is your purpose': "My purpose is to help LAUTECH students and aspirants get quick, accurate answers to their questions about the university. Think of me as your 24/7 LAUTECH guide! 🎓",

        'who are you': "I'm the LAUTECH Smart Assistant, an AI chatbot designed to help students and aspirants with information about Ladoke Akintola University of Technology. Ask me anything about admissions, fees, courses, or campus life!",

        'what is your name': "I'm called LAUTECH Smart Assistant! 🤖 You can just call me LAUTECH Bot. I'm here to answer all your questions about the university.",

        'who created you': "I was created by Samuel as part of the CodeAlpha internship project. I'm designed to help LAUTECH students and aspirants get quick answers to their questions!",

        'are you a robot': "Yes, I'm an AI chatbot! 🤖 But I'm here to help with real information about LAUTECH. Ask me anything!",

        'are you real': "I'm a real AI assistant, though not a human. I'm programmed to help with LAUTECH information. How can I assist you today?",

        'thank you': "You're welcome! 😊 Is there anything else you'd like to know about LAUTECH?",
        'thanks': "You're welcome! 👍 Happy to help with any other LAUTECH questions.",
        'thank': "You're welcome! 😊 Feel free to ask more questions about LAUTECH.",

        'goodbye': "Goodbye! 👋 Feel free to come back if you have more questions about LAUTECH. Have a great day!",
        'bye': "Bye! 👋 Hope I was helpful. Ask me anytime about LAUTECH!",
        'see you': "See you later! 👋 Remember I'm always here to help with LAUTECH questions.",
        'see you later': "See you later! 👋 Take care and good luck with your LAUTECH journey!",

        'help': "I can help with:\n\n" +
                "📌 **Admissions** - cut-off marks, requirements\n" +
                "💰 **Fees** - school fees, payments\n" +
                "🏠 **Accommodation** - hostels, areas\n" +
                "📚 **Academics** - courses, CGPA\n" +
                "🍔 **Campus Life** - food, security\n\n" +
                "Just type your question!",

        'how do you work': "I work by matching your questions to my database of LAUTECH FAQs. When I don't know something, I save it so the admin can add the answer later. Smart, right? 😊",

        'are you helpful': "I try my best! 🤖 I have information on admissions, fees, accommodation, and more. Ask me something about LAUTECH and see for yourself!",
    }

    for pattern, response in common_patterns.items():
        if pattern in question_lower:
            return {
                'answer': response,
                'confidence': 1.0,
                'match_type': 'common',
                'matched_by': 'common_handler'
            }

    # Check for thank you variations
    thank_you_words = ['thank', 'thanks', 'thx', 'ty', 'appreciate', 'grateful']
    if any(word in question_lower for word in thank_you_words):
        return {
            'answer': "You're very welcome! 😊 Is there anything else you'd like to know about LAUTECH?",
            'confidence': 1.0,
            'match_type': 'common',
            'matched_by': 'common_handler'
        }

    # Check for goodbye variations
    goodbye_words = ['bye', 'goodbye', 'see you', 'cya', 'farewell', 'take care']
    if any(word in question_lower for word in goodbye_words):
        return {
            'answer': "Goodbye! 👋 Thanks for chatting. Remember I'm always here if you have more LAUTECH questions. Have a great day!",
            'confidence': 1.0,
            'match_type': 'common',
            'matched_by': 'common_handler'
        }

    return None


# ===== FAQ MATCHER CLASS =====
class FAQMatcher:
    def __init__(self):
        """Initialize the FAQ matcher with optimized parameters"""
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.7,
            sublinear_tf=True,
            use_idf=True,
            norm='l2'
        )
        self.faqs = []
        self.faq_vectors = None
        self.is_fitted = False
        self.last_update = None

        # Adjusted thresholds for better matching
        self.thresholds = {
            'exact': 0.6,
            'similar': 0.4,
            'low': 0.25,
            'unknown': 0.0
        }

        # Load FAQs on initialization
        self.load_faqs()

    def load_faqs(self):
        """Load FAQs from database and build vectors"""
        try:
            conn = get_db_connection()
            faqs = conn.execute(
                "SELECT id, question, answer, category FROM faqs"
            ).fetchall()
            conn.close()

            if not faqs:
                print("⚠️ No FAQs found in database")
                self.faqs = []
                return

            self.faqs = [dict(faq) for faq in faqs]

            # Preprocess all questions
            questions = [faq['question'] for faq in self.faqs]
            processed_questions = preprocessor.process_batch(questions)

            # Create TF-IDF vectors
            self.faq_vectors = self.vectorizer.fit_transform(processed_questions)
            self.is_fitted = True
            self.last_update = datetime.now()

            print(f"✅ Loaded {len(self.faqs)} FAQs and built TF-IDF vectors")

        except Exception as e:
            print(f"🔥 Error loading FAQs: {e}")
            self.faqs = []
            self.is_fitted = False

    def refresh_if_needed(self):
        """Refresh FAQ vectors if database has changed"""
        self.load_faqs()

    def find_best_match(self, user_question):
        """
        Find the best matching FAQ for a user question
        Now with custom mappings for common questions
        """

        # Step 1: Check custom mappings first
        try:
            custom_match = get_custom_match(user_question)

            if custom_match:
                # Find the FAQ with this ID
                for faq in self.faqs:
                    if faq['id'] == custom_match['faq_id']:
                        match = faq.copy()
                        match['confidence'] = custom_match['confidence']
                        match['match_type'] = custom_match['match_type']
                        match['matched_by'] = custom_match['matched_by']
                        print(f"🎯 Custom match found for: {user_question[:50]}...")
                        return match
        except Exception as e:
            print(f"⚠️ Custom mapping check failed: {e}")

        # Step 2: If no custom match, proceed with TF-IDF
        if not self.faqs or not self.is_fitted:
            print("⚠️ No FAQs loaded, attempting to reload...")
            self.load_faqs()
            if not self.faqs:
                return None

        try:
            # Preprocess user question
            processed_user = preprocessor.process(user_question)

            # If question is too short, use simpler matching
            if len(processed_user.split()) < 2:
                return self._handle_short_query(user_question)

            # Transform user question to vector
            user_vector = self.vectorizer.transform([processed_user])

            # Calculate cosine similarity with all FAQs
            similarities = cosine_similarity(user_vector, self.faq_vectors).flatten()

            # Get top matches
            top_indices = np.argsort(similarities)[::-1][:5]
            top_scores = similarities[top_indices]

            # Get best match
            best_idx = top_indices[0]
            best_score = top_scores[0]

            # If best score is too low, try keyword matching
            if best_score < 0.2:
                return self._keyword_match(user_question)

            # Prepare result
            best_match = self.faqs[best_idx].copy()
            best_match['confidence'] = round(float(best_score), 3)
            best_match['all_matches'] = [
                {
                    'question': self.faqs[idx]['question'],
                    'confidence': round(float(score), 3)
                }
                for idx, score in zip(top_indices[1:4], top_scores[1:4])
                if score > 0.2
            ]

            # Determine match type based on threshold
            if best_score >= self.thresholds['exact']:
                best_match['match_type'] = 'exact'
            elif best_score >= self.thresholds['similar']:
                best_match['match_type'] = 'similar'
            elif best_score >= self.thresholds['low']:
                best_match['match_type'] = 'low'
            else:
                best_match['match_type'] = 'unknown'

            # Boost with keywords
            best_match = self._boost_with_keywords(user_question, best_match)

            print(f"📊 Best match: '{best_match['question'][:50]}...'")
            print(f"   Confidence: {best_score:.3f} ({best_match['match_type']})")

            return best_match

        except Exception as e:
            print(f"🔥 Error in find_best_match: {e}")
            return self._fallback_match(user_question)

    def _handle_short_query(self, user_question):
        """
        Special handling for very short queries (1-2 words)
        """
        query_lower = user_question.lower().strip()

        # Dictionary of keywords to FAQ IDs
        keyword_map = {
            'hostel': 32,
            'fees': 29,
            'fee': 29,
            'cut': 8,
            'cutoff': 8,
            'mark': 8,
            'lautech': 2,
            'location': 2,
            'where': 2,
            'medicine': 11,
            'med': 11,
            'engineer': 19,
            'engineering': 19,
            'repair': 57,
            'fix': 57,
            'library': 24,
            'read': 41,
            'cult': 40,
            'security': 39,
            'food': 37,
            'eat': 37,
            'transport': 46,
            'bus': 46,
            'bike': 47,
            'school': 2,
            'university': 2,
            'campus': 2,
            'about': 1,
            'info': 1,
        }

        # Check if query matches any keyword
        for keyword, faq_id in keyword_map.items():
            if keyword in query_lower or query_lower == keyword:
                for faq in self.faqs:
                    if faq['id'] == faq_id:
                        match = faq.copy()
                        match['confidence'] = 0.85
                        match['match_type'] = 'keyword'
                        match['matched_by'] = 'short_query'
                        print(f"🔑 Keyword match: '{keyword}' -> ID {faq_id}")
                        return match

        return None

    def _keyword_match(self, user_question):
        """
        Fallback method using simple keyword matching
        """
        try:
            # Extract keywords from user question
            keywords = preprocessor.extract_keywords(user_question, top_n=5)

            if not keywords:
                return None

            best_score = 0
            best_match = None

            for faq in self.faqs:
                # Count how many keywords appear in FAQ question
                faq_text = preprocessor.process(faq['question'])
                matches = sum(1 for keyword in keywords if keyword in faq_text)

                if matches > 0:
                    score = matches / len(keywords)
                    if score > best_score:
                        best_score = score
                        best_match = faq.copy()
                        best_match['confidence'] = round(score * 0.7, 3)
                        best_match['match_type'] = 'keyword'

            return best_match

        except Exception as e:
            print(f"🔥 Error in keyword matching: {e}")
            return None

    def _fallback_match(self, user_question):
        """
        Ultimate fallback - simple string matching
        """
        try:
            user_lower = user_question.lower()
            best_score = 0
            best_match = None

            for faq in self.faqs:
                faq_lower = faq['question'].lower()

                # Check for exact substring matches
                if user_lower in faq_lower or faq_lower in user_lower:
                    score = 0.5
                    if score > best_score:
                        best_score = score
                        best_match = faq.copy()
                        best_match['confidence'] = 0.5
                        best_match['match_type'] = 'substring'
                        best_match['matched_by'] = 'fallback'

            return best_match

        except Exception as e:
            print(f"🔥 Error in fallback matching: {e}")
            return None

    def get_suggestions(self, user_question, n=3):
        """
        Get alternative suggestions for low-confidence matches
        """
        try:
            if not self.faqs or not self.is_fitted:
                return []

            processed_user = preprocessor.process(user_question)
            user_vector = self.vectorizer.transform([processed_user])
            similarities = cosine_similarity(user_vector, self.faq_vectors).flatten()

            # Get top N indices
            top_indices = np.argsort(similarities)[::-1][:n]

            suggestions = []
            for idx in top_indices:
                if similarities[idx] > 0.3:
                    suggestions.append({
                        'question': self.faqs[idx]['question'],
                        'confidence': float(similarities[idx])
                    })

            return suggestions

        except Exception as e:
            print(f"🔥 Error getting suggestions: {e}")
            return []

    def _boost_with_keywords(self, user_question, base_match):
        """
        Boost confidence score if important keywords match
        """
        if not base_match:
            return base_match

        # Extract keywords from user question
        keywords = preprocessor.extract_keywords(user_question, top_n=3)

        if not keywords:
            return base_match

        # Check how many keywords appear in the matched FAQ
        faq_text = base_match['question'].lower()
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in faq_text)

        if keyword_matches > 0:
            # Boost confidence based on keyword matches
            boost = (keyword_matches / len(keywords)) * 0.2
            base_match['confidence'] = min(base_match['confidence'] + boost, 1.0)

            # Reclassify match type if confidence increased enough
            if base_match['confidence'] >= self.thresholds['exact']:
                base_match['match_type'] = 'exact'
            elif base_match['confidence'] >= self.thresholds['similar']:
                base_match['match_type'] = 'similar'
            elif base_match['confidence'] >= self.thresholds['low']:
                base_match['match_type'] = 'low'

        return base_match

    def add_faq_to_index(self, faq_id, question, answer):
        """
        Add a new FAQ to the index without reloading everything
        """
        try:
            # Add to faqs list
            new_faq = {
                'id': faq_id,
                'question': question,
                'answer': answer
            }
            self.faqs.append(new_faq)

            # Reprocess all questions
            questions = [faq['question'] for faq in self.faqs]
            processed_questions = preprocessor.process_batch(questions)
            self.faq_vectors = self.vectorizer.fit_transform(processed_questions)

            print(f"✅ Added FAQ {faq_id} to index")

        except Exception as e:
            print(f"🔥 Error adding FAQ to index: {e}")


# Create singleton instance
matcher = FAQMatcher()

# For testing
if __name__ == "__main__":
    print("🧪 Testing FAQ Matcher")
    print("=" * 60)

    test_questions = [
        "What is the cut off mark for medicine?",
        "How much is school fees?",
        "Where can I live near campus?",
        "Does LAUTECH accept second choice?",
        "What's the best place to read?",
        "Tell me about hostel accommodation",
        "When is post UTME form coming out?",
        "Are there cultists in LAUTECH?"
    ]

    for q in test_questions:
        print(f"\n📝 Question: {q}")
        match = matcher.find_best_match(q)

        if match:
            print(f"✅ Match: {match['question']}")
            print(f"   Confidence: {match['confidence']:.3f}")
            print(f"   Type: {match.get('match_type', 'unknown')}")

            if match.get('all_matches'):
                print("   Other suggestions:")
                for alt in match['all_matches']:
                    print(f"     - {alt['question'][:60]}... ({alt['confidence']:.3f})")
        else:
            print("❌ No match found")

        print("-" * 40)