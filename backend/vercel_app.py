"""
Vercel entry point - simplified
"""

import sys
import os
import traceback

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
try:
    from api import app
    print("✅ Flask app imported successfully")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    traceback.print_exc()
    raise

# Vercel requires a variable named 'app'
handler = app