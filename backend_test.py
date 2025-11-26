#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Enterprate OS
Tests all backend APIs according to the test sequence specified.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

# Test configuration
BACKEND_URL = get_backend_url()
if not BACKEND_URL:
    print("❌ Could not read REACT_APP_BACKEND_URL from /app/frontend/.env")
    sys.exit(1)

API_BASE = f"{BACKEND_URL}/api"
print(f"🔗 Testing API at: {API_BASE}")

# Test data
TEST_USER = {
    "email": "enterprate.test@example.com",
    "password": "SecureTest123!",
    "name": "Enterprate Test User"
}

TEST_WORKSPACE = {
    "name": "Enterprate Test Company",
    "country": "United States",
    "industry": "Technology",
    "stage": "Growth"
}

TEST_INVOICE = {
    "clientName": "Acme Corporation",
    "clientEmail": "billing@acme.com",
    "amount": 2500.00,
    "description": "Software Development Services",
    "dueDate": "2024-02-15"
}

TEST_LEAD = {
    "name": "Sarah Johnson",
    "email": "sarah.johnson@techstartup.com",
    "phone": "+1-555-0123",
    "source": "WEBSITE",
    "status": "NEW"
}

TEST_IDEA = {
    "idea": "An AI-powered project management platform that automatically prioritizes tasks based on business impact and team capacity",
    "targetCustomer": "Small to medium-sized tech companies and startups"
}

TEST_CHAT = {
    "message": "Hello! I'm looking for help with business strategy and growth planning. What can you help me with?"
}

# Global variables for test state
auth_token = None
workspace_id = None
test_results = []

def log_test(test_name, success, details="", response_data=None):
    """Log test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")
    if response_data and not success:
        print(f"   Response: {response_data}")
    
    test_results.append({
        "test": test_name,
        "success": success,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })

def make_request(method, endpoint, data=None, headers=None, expect_success=True):
    """Make HTTP request with error handling"""
    url = f"{API_BASE}{endpoint}"
    
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=default_headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=default_headers, timeout=30)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=data, headers=default_headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        # Check if we expect success
        if expect_success and response.status_code >= 400:
            return False, f"HTTP {response.status_code}: {response.text}"
        
        try:
            return True, response.json()
        except:
            return True, response.text
            
    except requests.exceptions.Timeout:
        return False, "Request timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection error - backend may not be running"
    except Exception as e:
        return False, f"Request error: {str(e)}"

def test_user_registration():
    """Test user registration API"""
    print("\n🔐 Testing User Registration...")
    
    success, response = make_request("POST", "/auth/register", TEST_USER)
    
    if success and isinstance(response, dict):
        if "token" in response and "user" in response:
            global auth_token
            auth_token = response["token"]
            user_data = response["user"]
            log_test("User Registration", True, 
                    f"User created: {user_data.get('name')} ({user_data.get('email')})")
            return True
        else:
            log_test("User Registration", False, "Missing token or user in response", response)
            return False
    else:
        log_test("User Registration", False, "Registration failed", response)
        return False

def test_user_login():
    """Test user login API"""
    print("\n🔑 Testing User Login...")
    
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    success, response = make_request("POST", "/auth/login", login_data)
    
    if success and isinstance(response, dict):
        if "token" in response and "user" in response:
            global auth_token
            auth_token = response["token"]
            log_test("User Login", True, "Login successful, token received")
            return True
        else:
            log_test("User Login", False, "Missing token in response", response)
            return False
    else:
        log_test("User Login", False, "Login failed", response)
        return False

def test_workspace_creation():
    """Test workspace creation API"""
    print("\n🏢 Testing Workspace Creation...")
    
    if not auth_token:
        log_test("Workspace Creation", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    success, response = make_request("POST", "/workspaces", TEST_WORKSPACE, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "name" in response:
            global workspace_id
            workspace_id = response["id"]
            log_test("Workspace Creation", True, 
                    f"Workspace created: {response.get('name')} (ID: {workspace_id})")
            return True
        else:
            log_test("Workspace Creation", False, "Missing id or name in response", response)
            return False
    else:
        log_test("Workspace Creation", False, "Workspace creation failed", response)
        return False

def test_get_workspaces():
    """Test get workspaces API"""
    print("\n📋 Testing Get Workspaces...")
    
    if not auth_token:
        log_test("Get Workspaces", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    success, response = make_request("GET", "/workspaces", headers=headers)
    
    if success and isinstance(response, list):
        if len(response) > 0:
            log_test("Get Workspaces", True, f"Retrieved {len(response)} workspace(s)")
            return True
        else:
            log_test("Get Workspaces", False, "No workspaces returned")
            return False
    else:
        log_test("Get Workspaces", False, "Failed to get workspaces", response)
        return False

def test_invoice_creation():
    """Test invoice creation API"""
    print("\n💰 Testing Invoice Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Invoice Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/navigator/invoices", TEST_INVOICE, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "clientName" in response:
            log_test("Invoice Creation", True, 
                    f"Invoice created for {response.get('clientName')}: ${response.get('amount')}")
            return True
        else:
            log_test("Invoice Creation", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Invoice Creation", False, "Invoice creation failed", response)
        return False

def test_get_invoices():
    """Test get invoices API"""
    print("\n📄 Testing Get Invoices...")
    
    if not auth_token or not workspace_id:
        log_test("Get Invoices", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/navigator/invoices", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Invoices", True, f"Retrieved {len(response)} invoice(s)")
        return True
    else:
        log_test("Get Invoices", False, "Failed to get invoices", response)
        return False

def test_lead_creation():
    """Test lead creation API"""
    print("\n🎯 Testing Lead Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Lead Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/growth/leads", TEST_LEAD, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "name" in response:
            log_test("Lead Creation", True, 
                    f"Lead created: {response.get('name')} ({response.get('email')})")
            return True
        else:
            log_test("Lead Creation", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Lead Creation", False, "Lead creation failed", response)
        return False

def test_get_leads():
    """Test get leads API"""
    print("\n👥 Testing Get Leads...")
    
    if not auth_token or not workspace_id:
        log_test("Get Leads", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/growth/leads", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Leads", True, f"Retrieved {len(response)} lead(s)")
        return True
    else:
        log_test("Get Leads", False, "Failed to get leads", response)
        return False

def test_idea_scoring():
    """Test idea scoring API"""
    print("\n💡 Testing Idea Scoring...")
    
    if not auth_token or not workspace_id:
        log_test("Idea Scoring", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/genesis/idea-score", TEST_IDEA, headers)
    
    if success and isinstance(response, dict):
        if "score" in response and "analysis" in response:
            log_test("Idea Scoring", True, 
                    f"Idea scored: {response.get('score')}/100")
            return True
        else:
            log_test("Idea Scoring", False, "Missing score or analysis in response", response)
            return False
    else:
        log_test("Idea Scoring", False, "Idea scoring failed", response)
        return False

def test_get_events():
    """Test get events API"""
    print("\n📊 Testing Get Events...")
    
    if not auth_token or not workspace_id:
        log_test("Get Events", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/intel/events", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Events", True, f"Retrieved {len(response)} event(s)")
        return True
    else:
        log_test("Get Events", False, "Failed to get events", response)
        return False

def test_ai_chat():
    """Test AI chat API"""
    print("\n🤖 Testing AI Chat...")
    
    if not auth_token:
        log_test("AI Chat", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    success, response = make_request("POST", "/chat", TEST_CHAT, headers)
    
    if success and isinstance(response, dict):
        if "response" in response and "session_id" in response:
            chat_response = response.get("response", "")
            log_test("AI Chat", True, 
                    f"Chat response received ({len(chat_response)} chars)")
            return True
        else:
            log_test("AI Chat", False, "Missing response or session_id", response)
            return False
    else:
        log_test("AI Chat", False, "AI chat failed", response)
        return False

def run_all_tests():
    """Run all backend API tests in sequence"""
    print("🚀 Starting Enterprate OS Backend API Tests")
    print("=" * 60)
    
    # Test sequence as specified
    tests = [
        test_user_registration,
        test_user_login,
        test_workspace_creation,
        test_get_workspaces,
        test_invoice_creation,
        test_get_invoices,
        test_lead_creation,
        test_get_leads,
        test_idea_scoring,
        test_get_events,
        test_ai_chat
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ FAIL {test_func.__name__}: Unexpected error: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed > 0:
        print("\n🔍 FAILED TESTS:")
        for result in test_results:
            if not result["success"]:
                print(f"   • {result['test']}: {result['details']}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)