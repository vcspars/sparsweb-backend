#!/usr/bin/env python3
"""Test sending an email directly"""
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from services.email_service import EmailService

async def test_email():
    email_service = EmailService()
    
    print("\nTesting email send...")
    result = await email_service.send_email(
        to_email="ahmedyaqoobbusiness@gmail.com",
        subject="Test Email from SPARS Backend",
        body="This is a test email to verify email functionality.",
        html_body="<html><body><h1>Test Email</h1><p>This is a test email to verify email functionality.</p></body></html>"
    )
    
    if result:
        print("[SUCCESS] Email sent successfully!")
    else:
        print("[FAILED] Email failed to send. Check error messages above.")

if __name__ == "__main__":
    asyncio.run(test_email())

