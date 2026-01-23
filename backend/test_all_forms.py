#!/usr/bin/env python3
"""
Comprehensive test script for all SPARS forms
Tests all endpoints and sends emails to ahmedyaqoobbusiness@gmail.com
"""
import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "ahmedyaqoobbusiness@gmail.com"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(
                url, 
                json=data, 
                headers={"Content-Type": "application/json"}, 
                timeout=15
            )
        else:
            print(f"[ERROR] Unknown method: {method}")
            return False
        
        print(f"\nEndpoint: {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response:\n{json.dumps(result, indent=2)}")
        except:
            print(f"Response: {response.text[:300]}")
        
        if response.status_code in [200, 201]:
            print("[SUCCESS] Test passed!")
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
    print_header("SPARS Backend - Comprehensive Form Testing")
    print(f"\nTesting all forms with email: {TEST_EMAIL}")
    print(f"Server: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # 1. Newsletter Subscription
    print_header("1. Newsletter Subscription Form")
    results['newsletter'] = test_endpoint(
        "POST", 
        "/api/newsletter",
        {"email": TEST_EMAIL},
        "Newsletter Subscription"
    )
    
    # 2. Contact Form (General Inquiry)
    print_header("2. Contact Form (General Inquiry)")
    results['contact'] = test_endpoint(
        "POST",
        "/api/contact",
        {
            "name": "Ahmed Yaqoob",
            "email": TEST_EMAIL,
            "phone": "+1 (555) 123-4567",
            "company": "Test Business Inc.",
            "inquiry_type": "General Inquiry",
            "message": "This is a test message from the automated form testing script. Please ignore this email."
        },
        "Contact Form"
    )
    
    # 3. Brochure Request
    print_header("3. Brochure Request Form")
    results['brochure'] = test_endpoint(
        "POST",
        "/api/brochure",
        {
            "full_name": "Ahmed Yaqoob",
            "email": TEST_EMAIL,
            "company": "Test Business Inc.",
            "phone": "+1 (555) 123-4567",
            "job_role": "Operations Manager",
            "agreed_to_marketing": True
        },
        "Brochure Request"
    )
    
    # 4. Product Profile Form
    print_header("4. Product Profile Form")
    results['product_profile'] = test_endpoint(
        "POST",
        "/api/product-profile",
        {
            "first_name": "Ahmed",
            "last_name": "Yaqoob",
            "email": TEST_EMAIL,
            "phone": "+1 (555) 123-4567",
            "job_title": "Operations Manager",
            "company_name": "Test Business Inc.",
            "industry": "Home Furnishing",
            "company_size": "51-200 employees",
            "website": "https://www.testbusiness.com",
            "address": "123 Test Street, New York, NY 10001",
            "current_system": "Excel & Manual Processes",
            "warehouses": 2,
            "users": 25,
            "requirements": "Need comprehensive ERP solution for inventory and order management",
            "timeline": "3-6 months"
        },
        "Product Profile"
    )
    
    # 5. Talk to Sales Form
    print_header("5. Talk to Sales Form")
    results['talk_to_sales'] = test_endpoint(
        "POST",
        "/api/talk-to-sales",
        {
            "name": "Ahmed Yaqoob",
            "email": TEST_EMAIL,
            "phone": "+1 (555) 123-4567",
            "company": "Test Business Inc.",
            "message": "I'm interested in learning more about SPARS ERP solution. Please contact me to schedule a demo."
        },
        "Talk to Sales"
    )
    
    # 6. Request Demo Form
    print_header("6. Request Demo Form")
    # Calculate a date 7 days from now
    demo_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    results['request_demo'] = test_endpoint(
        "POST",
        "/api/request-demo",
        {
            "first_name": "Ahmed",
            "last_name": "Yaqoob",
            "email": TEST_EMAIL,
            "phone": "+1 (555) 123-4567",
            "company_name": "Test Business Inc.",
            "company_size": "51-200",
            "preferred_demo_date": demo_date,
            "preferred_demo_time": "10:00 AM",
            "additional_information": "This is a test demo request from the automated testing script. Please ignore."
        },
        "Request Demo"
    )
    
    # Summary
    print_header("Test Summary")
    print("\nForm Test Results:")
    print("-" * 70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for form_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {form_name.replace('_', ' ').title():.<50} {status}")
    
    print("-" * 70)
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} [PASS]")
    print(f"Failed: {failed} [FAIL]")
    
    if passed == total:
        print("\n[SUCCESS] All forms are working correctly!")
        print(f"\nCheck your email ({TEST_EMAIL}) for:")
        print("  - Newsletter subscription confirmation")
        print("  - Contact form confirmation")
        print("  - Brochure email with PDF attachment")
        print("  - Product profile email with PDF attachment")
        print("  - Talk to Sales confirmation")
        print("  - Demo request confirmation")
        print("\nAlso check the admin email for notification emails about each submission.")
    else:
        print(f"\n[WARNING] {failed} form(s) failed. Check the errors above.")
    
    print("\n" + "="*70)
    print("Testing Complete!")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

