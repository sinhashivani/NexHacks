"""
Vercel serverless function entry point for FastAPI app.
Vercel automatically detects FastAPI apps - just expose the 'app' object.
"""

import sys
from pathlib import Path

# Add parent directory to Python path so we can import from root-level modules
# This allows imports like 'from polymarket.news import fetch_news'
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Load environment variables (Vercel will provide these via env vars)
from dotenv import load_dotenv
env_path = root_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

# Import the FastAPI app from main.py
# Vercel executes from repo root, so 'api.main' is correct
from api.main import app

# Vercel's Python runtime automatically detects FastAPI apps
# No handler function needed - just expose 'app'
__all__ = ['app']
