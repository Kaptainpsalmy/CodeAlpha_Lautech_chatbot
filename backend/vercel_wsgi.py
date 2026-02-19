"""
Vercel WSGI entry point
"""

import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api import app

# Vercel expects a variable named 'app'
handler = app