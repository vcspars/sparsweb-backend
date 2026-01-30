#!/usr/bin/env python3
"""
Backend Setup Verification Script
Run this on your VM to verify everything is configured correctly
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("="*70)
print("SPARS Backend Setup Verification")
print("="*70)

# Load environment variables
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"[OK] .env file found: {env_path}")
else:
    print(f"[ERROR] .env file NOT found at: {env_path}")
    print("  Please create .env file with required variables")
    sys.exit(1)

print("\n=== Environment Variables Check ===")
required_vars = {
    "EMAIL_HOST": os.getenv("EMAIL_HOST"),
    "EMAIL_PORT": os.getenv("EMAIL_PORT", "587"),
    "EMAIL_USE_TLS": os.getenv("EMAIL_USE_TLS", "True"),
    "EMAIL_HOST_USER": os.getenv("EMAIL_HOST_USER"),
    "EMAIL_HOST_PASSWORD": os.getenv("EMAIL_HOST_PASSWORD"),
    "DEFAULT_FROM_EMAIL": os.getenv("DEFAULT_FROM_EMAIL"),
    "ADMIN_EMAIL": os.getenv("ADMIN_EMAIL"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
}

all_ok = True
for var_name, var_value in required_vars.items():
    if var_value:
        if "PASSWORD" in var_name or "KEY" in var_name:
            masked = var_value[:8] + "..." + var_value[-4:] if len(var_value) > 12 else "***"
            print(f"[OK] {var_name}: {masked}")
        else:
            print(f"[OK] {var_name}: {var_value}")
    else:
        print(f"[ERROR] {var_name}: NOT SET")
        all_ok = False

print("\n=== File Structure Check ===")
files_to_check = {
    "main.py": "Main FastAPI application",
    "run.py": "Server startup script",
    "database.py": "Database models",
    "routers/forms.py": "Form endpoints",
    "routers/chatbot.py": "Chatbot endpoint",
    "services/email_service.py": "Email service",
    "services/db_service.py": "Database service",
    "services/excel_service.py": "Excel export service",
    "services/chatbot_service.py": "Chatbot service",
}

backend_dir = Path(__file__).parent
for file_path, description in files_to_check.items():
    full_path = backend_dir / file_path
    if full_path.exists():
        print(f"[OK] {file_path} - {description}")
    else:
        print(f"[ERROR] {file_path} - MISSING")
        all_ok = False

print("\n=== PDF Files Check ===")
pdfs_dir = backend_dir / "pdfs"
if pdfs_dir.exists():
    brochure_pdf = None
    profile_pdf = None
    
    for pdf_file in pdfs_dir.glob("*.pdf*"):
        if "brochure" in pdf_file.name.lower():
            brochure_pdf = pdf_file
        if "product_profile" in pdf_file.name.lower() or "productprofile" in pdf_file.name.lower():
            profile_pdf = pdf_file
    
    if brochure_pdf:
        print(f"[OK] Brochure PDF found: {brochure_pdf.name}")
    else:
        print(f"[WARNING] Brochure PDF not found in {pdfs_dir}")
    
    if profile_pdf:
        print(f"[OK] Product Profile PDF found: {profile_pdf.name}")
    else:
        print(f"[WARNING] Product Profile PDF not found in {pdfs_dir}")
else:
    print(f"[WARNING] PDFs directory not found: {pdfs_dir}")

print("\n=== Python Dependencies Check ===")
try:
    import fastapi
    print(f"[OK] FastAPI: {fastapi.__version__}")
except ImportError:
    print("[ERROR] FastAPI not installed")
    all_ok = False

try:
    import uvicorn
    print(f"[OK] Uvicorn: {uvicorn.__version__}")
except ImportError:
    print("[ERROR] Uvicorn not installed")
    all_ok = False

try:
    import sqlalchemy
    print(f"[OK] SQLAlchemy: {sqlalchemy.__version__}")
except ImportError:
    print("[ERROR] SQLAlchemy not installed")
    all_ok = False

try:
    import openai
    print(f"[OK] OpenAI: {openai.__version__}")
except ImportError:
    print("[ERROR] OpenAI not installed")
    all_ok = False

try:
    import openpyxl
    print(f"[OK] OpenPyXL: {openpyxl.__version__}")
except ImportError:
    print("[ERROR] OpenPyXL not installed")
    all_ok = False

print("\n=== Service Initialization Check ===")
try:
    from services.email_service import EmailService
    from services.chatbot_service import ChatbotService
    from services.db_service import DatabaseService
    from services.excel_service import ExcelService
    
    email_service = EmailService()
    if email_service.smtp_host:
        print("[OK] EmailService initialized successfully")
    else:
        print("[ERROR] EmailService missing EMAIL_HOST")
        all_ok = False
    
    chatbot_service = ChatbotService()
    if chatbot_service.api_key:
        print("[OK] ChatbotService initialized with API key")
    else:
        print("[WARNING] ChatbotService initialized without API key (will use fallback)")
    
    print("[OK] DatabaseService available")
    print("[OK] ExcelService available")
    
except Exception as e:
    print(f"[ERROR] Service initialization failed: {e}")
    all_ok = False

print("\n=== Database Check ===")
try:
    from database import init_db, get_db
    init_db()
    print("[OK] Database initialized successfully")
    
    db = next(get_db())
    print("[OK] Database connection successful")
    db.close()
except Exception as e:
    print(f"[ERROR] Database error: {e}")
    all_ok = False

print("\n=== API Endpoints Check ===")
try:
    from main import app
    routes = [route.path for route in app.routes]
    required_routes = [
        "/api/newsletter",
        "/api/contact",
        "/api/brochure",
        "/api/product-profile",
        "/api/talk-to-sales",
        "/api/request-demo",
        "/api/chatbot",
    ]
    
    for route in required_routes:
        if any(route in r for r in routes):
            print(f"[OK] Route registered: {route}")
        else:
            print(f"[WARNING] Route not found: {route}")
    
    print("[OK] FastAPI app loaded successfully")
except Exception as e:
    print(f"[ERROR] Failed to load app: {e}")
    all_ok = False

print("\n" + "="*70)
if all_ok:
    print("[SUCCESS] Backend is ready to use!")
    print("\nTo start the server:")
    print("  python run.py")
    print("  or")
    print("  uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    print("\nServer will be available at: http://0.0.0.0:8000")
    print("API docs at: http://0.0.0.0:8000/docs")
else:
    print("[ERROR] Some issues found. Please fix them before starting the server.")
    sys.exit(1)
print("="*70)












