from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

from services.email_service import EmailService
from services.chatbot_service import ChatbotService
from routers import forms, chatbot, download
from database import init_db

# Load environment variables - specify the path explicitly
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Fallback: try loading from current directory
    load_dotenv()

# Initialize database
init_db()

app = FastAPI(
    title="SPARS Backend API",
    description="Backend API for SPARS website forms and chatbot",
    version="1.0.0"
)

# CORS configuration - Allow Vercel frontend and local development
# For production, you may want to restrict this to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins - adjust for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(forms.router, prefix="/api", tags=["forms"])
app.include_router(chatbot.router, prefix="/api", tags=["chatbot"])
app.include_router(download.router, prefix="/api/download", tags=["download"])

@app.get("/")
async def root():
    return {"message": "SPARS Backend API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

