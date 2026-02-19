"""
Text preprocessing module for cleaning and preparing text for matching
"""

import re
import nltk
import string
import os
import ssl
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Fix for SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Set NLTK data path for production
if os.environ.get('VERCEL_ENV'):
    # In Vercel, use /tmp directory
    nltk_data_dir = '/tmp/nltk_data'
    nltk.data.path.append(nltk_data_dir)
else:
    # Local development
    nltk_data_dir = os.path.expanduser('~/nltk_data')

# Download required NLTK data
required_packages = [
    'punkt',
    'punkt_tab',
    'stopwords',
    'wordnet'
]

for package in required_packages:
    try:
        if package == 'punkt':
            nltk.data.find('tokenizers/punkt')
        elif package == 'punkt_tab':
            nltk.data.find('tokenizers/punkt_tab')
        elif package == 'stopwords':
            nltk.data.find('corpora/stopwords')
        elif package == 'wordnet':
            nltk.data.find('corpora/wordnet')
        print(f"✅ NLTK {package} found")
    except LookupError:
        print(f"⚠️ NLTK {package} not found, downloading...")
        nltk.download(package, download_dir=nltk_data_dir, quiet=False)

        
class TextPreprocessor:
    def __init__(self, use_lemmatization=True, remove_stopwords=True):
        """
        Initialize the text preprocessor

        Args:
            use_lemmatization: If True, use lemmatization (better but slower)
                               If False, use stemming (faster but less accurate)
            remove_stopwords: If True, remove common stopwords
        """
        self.use_lemmatization = use_lemmatization
        self.remove_stopwords = remove_stopwords

        # Initialize stemmer and lemmatizer
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

        # Get English stopwords
        self.stop_words = set(stopwords.words('english'))

        # Add custom LAUTECH-specific stopwords (words too common to be useful)
        self.custom_stopwords = {
            'lautech', 'university', 'school', 'student', 'students',
            'question', 'answer', 'please', 'like', 'get', 'want',
            'know', 'tell', 'would', 'could', 'thanks', 'thank'
        }
        self.stop_words.update(self.custom_stopwords)

    def clean_text(self, text):
        """
        Basic text cleaning

        Args:
            text: Raw input text

        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)

        # Remove numbers (optional - you might want to keep numbers for fees, cut-off marks)
        # text = re.sub(r'\d+', '', text)

        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def tokenize(self, text):
        """
        Tokenize text into words

        Args:
            text: Cleaned text

        Returns:
            List of tokens
        """
        return nltk.word_tokenize(text)

    def remove_stopwords_from_tokens(self, tokens):
        """
        Remove stopwords from token list

        Args:
            tokens: List of tokens

        Returns:
            Filtered tokens
        """
        return [token for token in tokens if token not in self.stop_words and len(token) > 2]

    def stem_tokens(self, tokens):
        """
        Apply stemming to tokens

        Args:
            tokens: List of tokens

        Returns:
            Stemmed tokens
        """
        return [self.stemmer.stem(token) for token in tokens]

    def lemmatize_tokens(self, tokens):
        """
        Apply lemmatization to tokens

        Args:
            tokens: List of tokens

        Returns:
            Lemmatized tokens
        """
        return [self.lemmatizer.lemmatize(token) for token in tokens]

    def process(self, text):
        """
        Complete preprocessing pipeline with optimizations for FAQ matching
        """
        if not text or not isinstance(text, str):
            return ""

        # Step 1: Clean text
        cleaned = self.clean_text(text)

        # Step 2: Handle common LAUTECH-specific terms
        cleaned = cleaned.replace('lautech', '')  # Remove as it's in every question
        cleaned = cleaned.replace('university', '')
        cleaned = cleaned.replace('school', '')

        # Step 3: Tokenize
        tokens = self.tokenize(cleaned)

        # Step 4: Remove stopwords and short words
        if self.remove_stopwords:
            tokens = self.remove_stopwords_from_tokens(tokens)

        # Step 5: Keep important educational terms
        important_terms = {
            'cutoff': 'cutoff',
            'cut-off': 'cutoff',
            'cut off': 'cutoff',
            'mark': 'mark',
            'score': 'score',
            'fee': 'fee',
            'fees': 'fee',
            'pay': 'pay',
            'payment': 'pay',
            'hostel': 'hostel',
            'accommodation': 'hostel',
            'lodge': 'hostel',
            'admission': 'admission',
            'admit': 'admission',
            'jamb': 'jamb',
            'utme': 'utme',
            'post-utme': 'utme',
            'medicine': 'medicine',
            'med': 'medicine',
            'engineering': 'engineering',
            'engr': 'engineering',
            'library': 'library',
            'read': 'read',
            'reading': 'read',
            'cult': 'cult',
            'cultist': 'cult',
            'security': 'security',
            'safe': 'security',
            'area': 'area',
            'place': 'area',
            'location': 'area'
        }

        # Normalize important terms
        normalized_tokens = []
        for token in tokens:
            found = False
            for key, value in important_terms.items():
                if key in token or token in key:
                    normalized_tokens.append(value)
                    found = True
                    break
            if not found:
                normalized_tokens.append(token)

        # Step 6: Apply lemmatization
        if self.use_lemmatization:
            normalized_tokens = self.lemmatize_tokens(normalized_tokens)
        else:
            normalized_tokens = self.stem_tokens(normalized_tokens)

        # Step 7: Join back into string
        processed = ' '.join(normalized_tokens)

        return processed
    def process_batch(self, texts):
        """
        Process multiple texts at once

        Args:
            texts: List of raw text strings

        Returns:
            List of processed text strings
        """
        return [self.process(text) for text in texts]

    def extract_keywords(self, text, top_n=5):
        """
        Extract most important keywords from text

        Args:
            text: Raw input text
            top_n: Number of keywords to extract

        Returns:
            List of top keywords
        """
        processed = self.process(text)
        words = processed.split()

        # Count word frequencies
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]


# Create a singleton instance for easy import
preprocessor = TextPreprocessor()

# For testing
if __name__ == "__main__":
    # Test the preprocessor
    test_texts = [
        "What is the cut-off mark for Medicine at LAUTECH?",
        "How much are the school fees for freshers?",
        "Where can I find the best accommodation near campus?",
        "Does LAUTECH accept second choice candidates in JAMB?"
    ]

    print("🧪 Testing Text Preprocessor")
    print("=" * 60)

    for text in test_texts:
        processed = preprocessor.process(text)
        keywords = preprocessor.extract_keywords(text)
        print(f"\nOriginal: {text}")
        print(f"Processed: {processed}")
        print(f"Keywords: {keywords}")