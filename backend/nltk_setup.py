"""
Download NLTK data during build time
"""

import nltk
import os
import ssl

# Fix for SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Create a writable directory for NLTK data
nltk_data_dir = '/tmp/nltk_data'
os.makedirs(nltk_data_dir, exist_ok=True)

# Set NLTK data path
nltk.data.path.append(nltk_data_dir)

# Download all required NLTK data
print("📥 Downloading NLTK punkt...")
nltk.download('punkt', download_dir=nltk_data_dir, quiet=False)

print("📥 Downloading NLTK punkt_tab...")
nltk.download('punkt_tab', download_dir=nltk_data_dir, quiet=False)

print("📥 Downloading NLTK stopwords...")
nltk.download('stopwords', download_dir=nltk_data_dir, quiet=False)

print("📥 Downloading NLTK wordnet...")
nltk.download('wordnet', download_dir=nltk_data_dir, quiet=False)

print(f"📁 NLTK data installed at: {nltk_data_dir}")
print("✅ All NLTK data downloaded successfully")