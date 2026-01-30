#!/usr/bin/env python3
"""Test email configuration"""
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

print("Email Configuration Check:")
print(f"EMAIL_HOST: {os.getenv('EMAIL_HOST')}")
print(f"EMAIL_PORT: {os.getenv('EMAIL_PORT')}")
print(f"EMAIL_USE_TLS: {os.getenv('EMAIL_USE_TLS')}")
print(f"EMAIL_HOST_USER: {os.getenv('EMAIL_HOST_USER')}")
print(f"EMAIL_HOST_PASSWORD: {'SET' if os.getenv('EMAIL_HOST_PASSWORD') else 'NOT SET'}")
print(f"DEFAULT_FROM_EMAIL: {os.getenv('DEFAULT_FROM_EMAIL')}")
print(f"ADMIN_EMAIL: {os.getenv('ADMIN_EMAIL')}")


