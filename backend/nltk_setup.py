"""
Download NLTK data during build time
"""

import nltk
import os

# Create a writable directory for NLTK data
nltk_data_dir = '/tmp/nltk_data'
os.makedirs(nltk_data_dir, exist_ok=True)

# Set NLTK data path
nltk.data.path.append(nltk_data_dir)

# Download required NLTK data
print("📥 Downloading NLTK punkt tokenizer...")
nltk.download('punkt', download_dir=nltk_data_dir, quiet=False)
print("✅ NLTK punkt downloaded successfully")

# Download stopwords
print("📥 Downloading NLTK stopwords...")
nltk.download('stopwords', download_dir=nltk_data_dir, quiet=False)
print("✅ NLTK stopwords downloaded successfully")

# Download wordnet
print("📥 Downloading NLTK wordnet...")
nltk.download('wordnet', download_dir=nltk_data_dir, quiet=False)
print("✅ NLTK wordnet downloaded successfully")

print(f"📁 NLTK data installed at: {nltk_data_dir}")