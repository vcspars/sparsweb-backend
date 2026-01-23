#!/usr/bin/env python3
"""
Test script to verify backend server setup and endpoints
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
env_path = backend_dir / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"[OK] Loaded .env file from: {env_path}")
else:
    load_dotenv()
    print(f"[WARNING] .env file not found at: {env_path}")
    print("  Attempting to load from current directory...")

# Check environment variables
print("\n=== Environment Variables Check ===")
openai_key = os.getenv("OPENAI_API_KEY")
email_host = os.getenv("EMAIL_HOST")
email_user = os.getenv("EMAIL_HOST_USER")

if openai_key:
    masked_key = openai_key[:8] + "..." + openai_key[-4:] if len(openai_key) > 12 else "***"
    print(f"[OK] OPENAI_API_KEY: {masked_key}")
else:
    print("[ERROR] OPENAI_API_KEY: NOT SET")

if email_host:
    print(f"[OK] EMAIL_HOST: {email_host}")
else:
    print("[ERROR] EMAIL_HOST: NOT SET")

if email_user:
    print(f"[OK] EMAIL_HOST_USER: {email_user}")
else:
    print("[ERROR] EMAIL_HOST_USER: NOT SET")

# Test imports
print("\n=== Testing Imports ===")
try:
    from main import app
    print("[OK] FastAPI app imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import app: {e}")
    sys.exit(1)

try:
    from services.chatbot_service import ChatbotService
    chatbot = ChatbotService()
    if chatbot.api_key:
        print("[OK] ChatbotService initialized with API key")
    else:
        print("[WARNING] ChatbotService initialized without API key (will use fallback)")
except Exception as e:
    print(f"[ERROR] Failed to import ChatbotService: {e}")

try:
    from routers import forms, chatbot, download
    print("[OK] All routers imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import routers: {e}")

# Test database
print("\n=== Testing Database ===")
try:
    from database import init_db, get_db
    init_db()
    print("[OK] Database initialized successfully")
    
    # Test database connection
    db = next(get_db())
    print("[OK] Database connection successful")
    db.close()
except Exception as e:
    print(f"[ERROR] Database error: {e}")

print("\n=== Server Ready ===")
print("You can now start the server with:")
print("  python run.py")
print("  or")
print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
print("\nAPI will be available at: http://localhost:8000")
print("API docs at: http://localhost:8000/docs")

