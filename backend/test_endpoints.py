#!/usr/bin/env python3
"""
Test all backend endpoints
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {description or endpoint}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=10)
        else:
            print(f"[ERROR] Unknown method: {method}")
            return False
        
        print(f"Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        except:
            print(f"Response: {response.text[:200]}")
        
        if response.status_code in [200, 201]:
            print("[OK] Test passed!")
            return True
        else:
            print(f"[WARNING] Status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Is it running?")
        print("Start server with: python run.py")
        return False
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

def main():
    print("="*60)
    print("SPARS Backend API Test Suite")
    print("="*60)
    
    # Test health check
    test_endpoint("GET", "/health", description="Health Check")
    
    # Test root endpoint
    test_endpoint("GET", "/", description="Root Endpoint")
    
    # Test newsletter subscription
    test_endpoint("POST", "/api/newsletter", 
                 {"email": "test@example.com"},
                 "Newsletter Subscription")
    
    # Test contact form
    test_endpoint("POST", "/api/contact",
                 {
                     "name": "Test User",
                     "email": "test@example.com",
                     "phone": "1234567890",
                     "company": "Test Company",
                     "inquiry_type": "General Inquiry",
                     "message": "This is a test message"
                 },
                 "Contact Form")
    
    # Test talk to sales
    test_endpoint("POST", "/api/talk-to-sales",
                 {
                     "name": "Test User",
                     "email": "test@example.com",
                     "phone": "1234567890",
                     "company": "Test Company",
                     "message": "I want to learn more about SPARS"
                 },
                 "Talk to Sales")
    
    # Test chatbot (this will verify OPENAI_API_KEY is loaded)
    print("\n" + "="*60)
    print("Testing Chatbot (this verifies OPENAI_API_KEY is loaded)")
    print("="*60)
    test_endpoint("POST", "/api/chatbot",
                 {
                     "message": "Hello, what is SPARS?"
                 },
                 "Chatbot")
    
    print("\n" + "="*60)
    print("Test Suite Complete!")
    print("="*60)
    print("\nIf you see the chatbot warning, it means OPENAI_API_KEY")
    print("was not loaded. Check that:")
    print("1. .env file exists in the backend directory")
    print("2. OPENAI_API_KEY is set in .env file")
    print("3. Server was restarted after adding the key")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)

