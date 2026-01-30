#!/usr/bin/env python3
"""
Simple script to test email functionality
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from services.email_service import EmailService

# Load environment variables
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✓ Loaded .env from: {env_path}")
else:
    load_dotenv()
    print("⚠ .env file not found, using system environment variables")

# Print configuration (without password)
print("\nEmail Configuration:")
print(f"  EMAIL_HOST: {os.getenv('EMAIL_HOST')}")
print(f"  EMAIL_PORT: {os.getenv('EMAIL_PORT')}")
print(f"  EMAIL_USE_TLS: {os.getenv('EMAIL_USE_TLS')}")
print(f"  EMAIL_HOST_USER: {os.getenv('EMAIL_HOST_USER')}")
print(f"  DEFAULT_FROM_EMAIL: {os.getenv('DEFAULT_FROM_EMAIL')}")
print(f"  ADMIN_EMAIL: {os.getenv('ADMIN_EMAIL')}")
print(f"  EMAIL_HOST_PASSWORD: {'*' * 10 if os.getenv('EMAIL_HOST_PASSWORD') else 'NOT SET'}")

async def test_email():
    """Test sending an email"""
    print("\n" + "="*50)
    print("Testing Email Service...")
    print("="*50)
    
    # Get test email from user or use default
    test_email = input("\nEnter test email address (or press Enter for admin email): ").strip()
    if not test_email:
        test_email = os.getenv('ADMIN_EMAIL', 'test@example.com')
    
    try:
        email_service = EmailService()
        print(f"\nAttempting to send test email to: {test_email}")
        
        result = await email_service.send_email(
            to_email=test_email,
            subject="Test Email from SPARS Backend",
            body="This is a test email to verify email functionality.",
            html_body="<html><body><h1>Test Email</h1><p>This is a test email to verify email functionality.</p></body></html>"
        )
        
        if result:
            print(f"\n✓ SUCCESS: Test email sent successfully to {test_email}")
            print("  Please check your inbox (and spam folder).")
        else:
            print(f"\n✗ FAILED: Email service returned False")
            print("  Check the error messages above for details.")
            
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_email())




