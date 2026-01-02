#!/usr/bin/env python3
"""
COMPREHENSIVE A-Z Backend API Testing for EnterprateAI Platform
Tests ALL backend APIs according to the review request checklist.
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

# Test credentials from review request
TEST_CREDENTIALS = {
    "email": "test-bugfix@example.com",
    "password": "TestPass123!"
}

# Global variables for test state
auth_token = None
workspace_id = None
test_results = []
passed_count = 0
failed_count = 0

def log_test(test_name, success, status_code=None, details="", response_sample=""):
    """Log test results with detailed information"""
    global passed_count, failed_count
    
    status = "✅ PASS" if success else "❌ FAIL"
    if success:
        passed_count += 1
    else:
        failed_count += 1
    
    print(f"{status} {test_name}")
    if status_code:
        print(f"   Status: {status_code}")
    if details:
        print(f"   Details: {details}")
    if response_sample:
        print(f"   Sample: {response_sample[:100]}...")
    
    test_results.append({
        "test": test_name,
        "success": success,
        "status_code": status_code,
        "details": details,
        "response_sample": response_sample,
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
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=default_headers, timeout=30)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=data, headers=default_headers, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=default_headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        try:
            response_data = response.json()
        except:
            response_data = response.text
            
        return response.status_code, response_data
            
    except requests.exceptions.Timeout:
        return None, "Request timeout"
    except requests.exceptions.ConnectionError:
        return None, "Connection error - backend may not be running"
    except Exception as e:
        return None, f"Request error: {str(e)}"

# ===== AUTHENTICATION MODULE TESTS =====

def test_auth_register():
    """Test POST /api/auth/register - Test user registration"""
    print("\n🔐 Testing User Registration...")
    
    status_code, response = make_request("POST", "/auth/register", TEST_CREDENTIALS)
    
    if status_code == 201 or (status_code == 400 and "already registered" in str(response).lower()):
        log_test("POST /api/auth/register", True, status_code, 
                "User registration working (new user created or already exists)")
        return True
    else:
        log_test("POST /api/auth/register", False, status_code, 
                "Registration failed", str(response)[:100])
        return False

def test_auth_login():
    """Test POST /api/auth/login - Test login"""
    print("\n🔑 Testing User Login...")
    
    status_code, response = make_request("POST", "/auth/login", TEST_CREDENTIALS)
    
    if status_code == 200 and isinstance(response, dict) and "token" in response:
        global auth_token
        auth_token = response["token"]
        log_test("POST /api/auth/login", True, status_code, 
                "Login successful, token received", f"Token: {auth_token[:20]}...")
        return True
    else:
        log_test("POST /api/auth/login", False, status_code, 
                "Login failed", str(response)[:100])
        return False

def test_auth_me():
    """Test GET /api/auth/me - Get current user"""
    print("\n👤 Testing Get Current User...")
    
    if not auth_token:
        log_test("GET /api/auth/me", False, None, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    status_code, response = make_request("GET", "/auth/me", headers=headers)
    
    if status_code == 200 and isinstance(response, dict) and "email" in response:
        log_test("GET /api/auth/me", True, status_code, 
                f"Current user: {response.get('email')}")
        return True
    else:
        log_test("GET /api/auth/me", False, status_code, 
                "Failed to get current user", str(response)[:100])
        return False

def test_google_oauth_init():
    """Test POST /api/auth/google/init - Google OAuth init"""
    print("\n🔐 Testing Google OAuth Init...")
    
    status_code, response = make_request("POST", "/auth/google/init", {})
    
    if status_code == 200:
        log_test("POST /api/auth/google/init", True, status_code, 
                "OAuth init endpoint working")
        return True
    else:
        log_test("POST /api/auth/google/init", False, status_code, 
                "OAuth init failed", str(response)[:100])
        return False

def test_google_oauth_callback():
    """Test GET /api/auth/google/callback - Google OAuth callback"""
    print("\n🔐 Testing Google OAuth Callback...")
    
    # Test with invalid session (should fail gracefully)
    invalid_data = {"session_id": "invalid-test-session"}
    status_code, response = make_request("POST", "/auth/google/callback", invalid_data)
    
    if status_code == 401 or (status_code >= 400 and "invalid" in str(response).lower()):
        log_test("GET /api/auth/google/callback", True, status_code, 
                "OAuth callback correctly rejects invalid session")
        return True
    else:
        log_test("GET /api/auth/google/callback", False, status_code, 
                "OAuth callback should reject invalid session", str(response)[:100])
        return False

# ===== WORKSPACE MODULE TESTS =====

def test_workspaces_list():
    """Test GET /api/workspaces - List workspaces"""
    print("\n🏢 Testing List Workspaces...")
    
    if not auth_token:
        log_test("GET /api/workspaces", False, None, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    status_code, response = make_request("GET", "/workspaces", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        if len(response) > 0:
            global workspace_id
            workspace_id = response[0].get("id")
        log_test("GET /api/workspaces", True, status_code, 
                f"Retrieved {len(response)} workspace(s)")
        return True
    else:
        log_test("GET /api/workspaces", False, status_code, 
                "Failed to get workspaces", str(response)[:100])
        return False

def test_workspaces_create():
    """Test POST /api/workspaces - Create workspace"""
    print("\n🏢 Testing Create Workspace...")
    
    if not auth_token:
        log_test("POST /api/workspaces", False, None, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    workspace_data = {
        "name": "Test Workspace",
        "country": "United Kingdom",
        "industry": "Technology",
        "stage": "Growth"
    }
    
    status_code, response = make_request("POST", "/workspaces", workspace_data, headers)
    
    if status_code == 201 and isinstance(response, dict) and "id" in response:
        global workspace_id
        workspace_id = response["id"]
        log_test("POST /api/workspaces", True, status_code, 
                f"Workspace created: {response.get('name')}")
        return True
    else:
        log_test("POST /api/workspaces", False, status_code, 
                "Failed to create workspace", str(response)[:100])
        return False

def test_workspaces_get():
    """Test GET /api/workspaces/{id} - Get workspace details"""
    print("\n🏢 Testing Get Workspace Details...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/workspaces/{id}", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    status_code, response = make_request("GET", f"/workspaces/{workspace_id}", headers=headers)
    
    if status_code == 200 and isinstance(response, dict) and "name" in response:
        log_test("GET /api/workspaces/{id}", True, status_code, 
                f"Workspace details: {response.get('name')}")
        return True
    else:
        log_test("GET /api/workspaces/{id}", False, status_code, 
                "Failed to get workspace details", str(response)[:100])
        return False

# ===== COMPANY PROFILE MODULE TESTS =====

def test_company_profile_get():
    """Test GET /api/company-profile - Get company profile"""
    print("\n🏢 Testing Get Company Profile...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/company-profile", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    status_code, response = make_request("GET", "/company-profile", headers=headers)
    
    if status_code == 200 or status_code == 404:  # 404 is OK if no profile exists yet
        log_test("GET /api/company-profile", True, status_code, "Company profile endpoint working")
        return True
    else:
        log_test("GET /api/company-profile", False, status_code, 
                "Failed to get company profile", str(response)[:100])
        return False

def test_company_profile_create():
    """Test POST /api/company-profile - Create/update profile"""
    print("\n🏢 Testing Create Company Profile...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/company-profile", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    profile_data = {
        "companyName": "Test Company Ltd",
        "industry": "Technology",
        "description": "A test technology company"
    }
    
    status_code, response = make_request("POST", "/company-profile", profile_data, headers)
    
    if status_code in [200, 201]:
        log_test("POST /api/company-profile", True, status_code, "Company profile created/updated")
        return True
    else:
        log_test("POST /api/company-profile", False, status_code, 
                "Failed to create company profile", str(response)[:100])
        return False

def test_company_profile_check_name():
    """Test POST /api/company-profile/check-name - Check company name availability"""
    print("\n🔍 Testing Check Company Name Availability...")
    
    if not auth_token:
        log_test("POST /api/company-profile/check-name", False, None, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    name_data = {"companyName": "Test Unique Company Name 2024"}
    
    status_code, response = make_request("POST", "/company-profile/check-name", name_data, headers)
    
    if status_code == 200:
        log_test("POST /api/company-profile/check-name", True, status_code, "Name availability checked")
        return True
    else:
        log_test("POST /api/company-profile/check-name", False, status_code, 
                "Failed to check company name", str(response)[:100])
        return False

def test_company_profile_confirm_registration():
    """Test POST /api/company-profile/confirm-registration - Confirm registration"""
    print("\n✅ Testing Confirm Company Registration...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/company-profile/confirm-registration", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    confirm_data = {"companyNumber": "12345678"}
    
    status_code, response = make_request("POST", "/company-profile/confirm-registration", confirm_data, headers)
    
    if status_code in [200, 201]:
        log_test("POST /api/company-profile/confirm-registration", True, status_code, "Registration confirmation processed")
        return True
    else:
        log_test("POST /api/company-profile/confirm-registration", False, status_code, 
                "Failed to confirm registration", str(response)[:100])
        return False

def test_company_profile_generate_branding():
    """Test POST /api/company-profile/generate-branding - Generate branding"""
    print("\n🎨 Testing Generate Company Branding...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/company-profile/generate-branding", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    branding_data = {
        "companyName": "Test Company",
        "industry": "Technology",
        "style": "modern"
    }
    
    status_code, response = make_request("POST", "/company-profile/generate-branding", branding_data, headers)
    
    if status_code == 200:
        log_test("POST /api/company-profile/generate-branding", True, status_code, "Company branding generated")
        return True
    else:
        log_test("POST /api/company-profile/generate-branding", False, status_code, 
                "Failed to generate branding", str(response)[:100])
        return False

def test_company_profile_generate_website_content():
    """Test POST /api/company-profile/generate-website-content - Generate website content"""
    print("\n🌐 Testing Generate Website Content...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/company-profile/generate-website-content", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    content_data = {
        "companyName": "Test Company",
        "industry": "Technology",
        "section": "hero"
    }
    
    status_code, response = make_request("POST", "/company-profile/generate-website-content", content_data, headers)
    
    if status_code == 200:
        log_test("POST /api/company-profile/generate-website-content", True, status_code, "Website content generated")
        return True
    else:
        log_test("POST /api/company-profile/generate-website-content", False, status_code, 
                "Failed to generate website content", str(response)[:100])
        return False

# ===== FINANCE MODULE TESTS =====

def test_finance_invoices_list():
    """Test GET /api/finance/invoices - List invoices"""
    print("\n💰 Testing List Invoices...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/finance/invoices", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/finance/invoices", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/finance/invoices", True, status_code, f"Retrieved {len(response)} invoice(s)")
        return True
    else:
        log_test("GET /api/finance/invoices", False, status_code, 
                "Failed to get invoices", str(response)[:100])
        return False

def test_finance_invoices_create():
    """Test POST /api/finance/invoices - Create invoice"""
    print("\n💰 Testing Create Invoice...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/finance/invoices", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    invoice_data = {
        "clientName": "Test Client Ltd",
        "clientEmail": "client@test.com",
        "amount": 1500.00,
        "description": "Consulting services",
        "dueDate": "2024-02-15"
    }
    
    status_code, response = make_request("POST", "/finance/invoices", invoice_data, headers)
    
    if status_code in [200, 201]:
        log_test("POST /api/finance/invoices", True, status_code, "Invoice created successfully")
        return True
    else:
        log_test("POST /api/finance/invoices", False, status_code, 
                "Failed to create invoice", str(response)[:100])
        return False

def test_finance_expenses_list():
    """Test GET /api/finance/expenses - List expenses"""
    print("\n💸 Testing List Expenses...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/finance/expenses", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/finance/expenses", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/finance/expenses", True, status_code, f"Retrieved {len(response)} expense(s)")
        return True
    else:
        log_test("GET /api/finance/expenses", False, status_code, 
                "Failed to get expenses", str(response)[:100])
        return False

def test_finance_expenses_create():
    """Test POST /api/finance/expenses - Create expense"""
    print("\n💸 Testing Create Expense...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/finance/expenses", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    expense_data = {
        "description": "Office supplies",
        "amount": 250.50,
        "category": "office",
        "date": "2024-01-15",
        "vendor": "Office Depot"
    }
    
    status_code, response = make_request("POST", "/finance/expenses", expense_data, headers)
    
    if status_code in [200, 201]:
        log_test("POST /api/finance/expenses", True, status_code, "Expense created successfully")
        return True
    else:
        log_test("POST /api/finance/expenses", False, status_code, 
                "Failed to create expense", str(response)[:100])
        return False

def test_finance_scan_receipt():
    """Test POST /api/finance/scan-receipt - Scan receipt"""
    print("\n📄 Testing Scan Receipt...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/finance/scan-receipt", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    # Test with minimal valid base64 image
    receipt_data = {
        "imageBase64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    }
    
    status_code, response = make_request("POST", "/finance/scan-receipt", receipt_data, headers)
    
    if status_code == 200:
        log_test("POST /api/finance/scan-receipt", True, status_code, "Receipt scanning working")
        return True
    else:
        log_test("POST /api/finance/scan-receipt", False, status_code, 
                "Failed to scan receipt", str(response)[:100])
        return False

def test_finance_estimate_tax():
    """Test POST /api/finance/estimate-tax - Estimate tax"""
    print("\n🧮 Testing Estimate Tax...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/finance/estimate-tax", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    tax_data = {
        "annualRevenue": 100000,
        "annualExpenses": 30000,
        "businessType": "ltd",
        "country": "UK"
    }
    
    status_code, response = make_request("POST", "/finance/estimate-tax", tax_data, headers)
    
    if status_code == 200:
        log_test("POST /api/finance/estimate-tax", True, status_code, "Tax estimation working")
        return True
    else:
        log_test("POST /api/finance/estimate-tax", False, status_code, 
                "Failed to estimate tax", str(response)[:100])
        return False

def test_finance_compliance_list():
    """Test GET /api/finance/compliance - List compliance items"""
    print("\n✅ Testing List Compliance Items...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/finance/compliance", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/finance/compliance", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/finance/compliance", True, status_code, f"Retrieved {len(response)} compliance item(s)")
        return True
    else:
        log_test("GET /api/finance/compliance", False, status_code, 
                "Failed to get compliance items", str(response)[:100])
        return False

def test_finance_compliance_create():
    """Test POST /api/finance/compliance - Create compliance item"""
    print("\n✅ Testing Create Compliance Item...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/finance/compliance", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    compliance_data = {
        "title": "VAT Registration",
        "description": "Register for VAT if turnover exceeds £85,000",
        "category": "tax",
        "priority": "high",
        "dueDate": "2024-03-31"
    }
    
    status_code, response = make_request("POST", "/finance/compliance", compliance_data, headers)
    
    if status_code in [200, 201]:
        log_test("POST /api/finance/compliance", True, status_code, "Compliance item created successfully")
        return True
    else:
        log_test("POST /api/finance/compliance", False, status_code, 
                "Failed to create compliance item", str(response)[:100])
        return False

def test_finance_compliance_defaults():
    """Test GET /api/finance/compliance/defaults - Get default UK checklist"""
    print("\n📝 Testing Get Default UK Compliance...")
    
    if not auth_token:
        log_test("GET /api/finance/compliance/defaults", False, None, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    status_code, response = make_request("GET", "/finance/compliance/defaults?business_type=ltd", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/finance/compliance/defaults", True, status_code, f"Retrieved {len(response)} default compliance item(s)")
        return True
    else:
        log_test("GET /api/finance/compliance/defaults", False, status_code, 
                "Failed to get default compliance", str(response)[:100])
        return False

# ===== OPERATIONS MODULE TESTS =====

def test_operations_tasks_list():
    """Test GET /api/operations/tasks - List tasks"""
    print("\n📝 Testing List Tasks...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/operations/tasks", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/operations/tasks", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/operations/tasks", True, status_code, f"Retrieved {len(response)} task(s)")
        return True
    else:
        log_test("GET /api/operations/tasks", False, status_code, 
                "Failed to get tasks", str(response)[:100])
        return False

def test_operations_tasks_create():
    """Test POST /api/operations/tasks - Create task"""
    print("\n📝 Testing Create Task...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/operations/tasks", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    task_data = {
        "title": "Test Task",
        "description": "A test task for API testing",
        "priority": "medium",
        "dueDate": "2024-02-15",
        "assignee": "test-user"
    }
    
    status_code, response = make_request("POST", "/operations/tasks", task_data, headers)
    
    if status_code in [200, 201]:
        log_test("POST /api/operations/tasks", True, status_code, "Task created successfully")
        return True
    else:
        log_test("POST /api/operations/tasks", False, status_code, 
                "Failed to create task", str(response)[:100])
        return False

def test_operations_email_templates_list():
    """Test GET /api/operations/email-templates - List email templates"""
    print("\n📧 Testing List Email Templates...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/operations/email-templates", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/operations/email-templates", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/operations/email-templates", True, status_code, f"Retrieved {len(response)} email template(s)")
        return True
    else:
        log_test("GET /api/operations/email-templates", False, status_code, 
                "Failed to get email templates", str(response)[:100])
        return False

def test_operations_email_templates_create():
    """Test POST /api/operations/email-templates - Create template"""
    print("\n📧 Testing Create Email Template...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/operations/email-templates", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    template_data = {
        "name": "Welcome Email",
        "subject": "Welcome to our platform!",
        "bodyHtml": "<h1>Welcome!</h1><p>Thank you for joining us.</p>",
        "bodyText": "Welcome! Thank you for joining us.",
        "category": "general"
    }
    
    status_code, response = make_request("POST", "/operations/email-templates", template_data, headers)
    
    if status_code in [200, 201]:
        log_test("POST /api/operations/email-templates", True, status_code, "Email template created successfully")
        return True
    else:
        log_test("POST /api/operations/email-templates", False, status_code, 
                "Failed to create email template", str(response)[:100])
        return False

def test_operations_email_logs():
    """Test GET /api/operations/email-logs - List email logs"""
    print("\n📜 Testing Get Email Logs...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/operations/email-logs", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/operations/email-logs", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/operations/email-logs", True, status_code, f"Retrieved {len(response)} email log(s)")
        return True
    else:
        log_test("GET /api/operations/email-logs", False, status_code, 
                "Failed to get email logs", str(response)[:100])
        return False

def test_operations_generate_email():
    """Test POST /api/operations/generate-email - AI email generation"""
    print("\n🤖 Testing AI Email Generation...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/operations/generate-email", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    email_request = {
        "type": "welcome",
        "recipient": "customer",
        "tone": "professional"
    }
    
    status_code, response = make_request("POST", "/operations/generate-email", email_request, headers)
    
    if status_code == 200:
        log_test("POST /api/operations/generate-email", True, status_code, "AI email generated successfully")
        return True
    else:
        log_test("POST /api/operations/generate-email", False, status_code, 
                "Failed to generate AI email", str(response)[:100])
        return False

def test_operations_send_approved_email():
    """Test POST /api/operations/send-approved-email - Send email"""
    print("\n📤 Testing Send Approved Email...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/operations/send-approved-email", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    email_data = {
        "to": ["test@example.com"],
        "subject": "Test Email",
        "content": "This is a test email"
    }
    
    status_code, response = make_request("POST", "/operations/send-approved-email", email_data, headers)
    
    if status_code == 200:
        log_test("POST /api/operations/send-approved-email", True, status_code, "Email sent successfully (MOCKED)")
        return True
    else:
        log_test("POST /api/operations/send-approved-email", False, status_code, 
                "Failed to send email", str(response)[:100])
        return False

def test_operations_pending_emails():
    """Test GET /api/operations/pending-emails - List pending emails"""
    print("\n📧 Testing Get Pending Emails...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/operations/pending-emails", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/operations/pending-emails", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/operations/pending-emails", True, status_code, f"Retrieved {len(response)} pending email(s)")
        return True
    else:
        log_test("GET /api/operations/pending-emails", False, status_code, 
                "Failed to get pending emails", str(response)[:100])
        return False

# ===== MARKETING/GROWTH MODULE TESTS =====

def test_marketing_leads_list():
    """Test GET /api/marketing/leads - List leads"""
    print("\n🎯 Testing List Leads...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/marketing/leads", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/marketing/leads", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/marketing/leads", True, status_code, f"Retrieved {len(response)} lead(s)")
        return True
    else:
        log_test("GET /api/marketing/leads", False, status_code, 
                "Failed to get leads", str(response)[:100])
        return False

def test_marketing_leads_create():
    """Test POST /api/marketing/leads - Create lead"""
    print("\n🎯 Testing Create Lead...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/marketing/leads", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    lead_data = {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "+44 20 1234 5678",
        "source": "WEBSITE",
        "status": "NEW"
    }
    
    status_code, response = make_request("POST", "/marketing/leads", lead_data, headers)
    
    if status_code in [200, 201]:
        log_test("POST /api/marketing/leads", True, status_code, "Lead created successfully")
        return True
    else:
        log_test("POST /api/marketing/leads", False, status_code, 
                "Failed to create lead", str(response)[:100])
        return False

def test_marketing_campaigns_list():
    """Test GET /api/marketing/campaigns - List campaigns"""
    print("\n🚀 Testing List Campaigns...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/marketing/campaigns", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/marketing/campaigns", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/marketing/campaigns", True, status_code, f"Retrieved {len(response)} campaign(s)")
        return True
    else:
        log_test("GET /api/marketing/campaigns", False, status_code, 
                "Failed to get campaigns", str(response)[:100])
        return False

def test_marketing_campaigns_create():
    """Test POST /api/marketing/campaigns - Create campaign"""
    print("\n🚀 Testing Create Campaign...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/marketing/campaigns", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    campaign_data = {
        "name": "Q1 2024 Launch Campaign",
        "description": "Product launch campaign for Q1",
        "type": "content",
        "budget": 10000,
        "startDate": "2024-01-01",
        "endDate": "2024-03-31"
    }
    
    status_code, response = make_request("POST", "/marketing/campaigns", campaign_data, headers)
    
    if status_code in [200, 201]:
        log_test("POST /api/marketing/campaigns", True, status_code, "Campaign created successfully")
        return True
    else:
        log_test("POST /api/marketing/campaigns", False, status_code, 
                "Failed to create campaign", str(response)[:100])
        return False

def test_marketing_social_posts_list():
    """Test GET /api/marketing/social-posts - List social posts"""
    print("\n📱 Testing List Social Posts...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/marketing/social-posts", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/marketing/social-posts", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/marketing/social-posts", True, status_code, f"Retrieved {len(response)} social post(s)")
        return True
    else:
        log_test("GET /api/marketing/social-posts", False, status_code, 
                "Failed to get social posts", str(response)[:100])
        return False

def test_marketing_social_posts_generate():
    """Test POST /api/marketing/social-posts/generate - AI generate social post"""
    print("\n🤖 Testing AI Generate Social Post...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/marketing/social-posts/generate", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    generate_data = {
        "platform": "linkedin",
        "topic": "AI business automation",
        "tone": "professional",
        "includeHashtags": True
    }
    
    status_code, response = make_request("POST", "/marketing/social-posts/generate", generate_data, headers)
    
    if status_code == 200:
        log_test("POST /api/marketing/social-posts/generate", True, status_code, "AI social post generated successfully")
        return True
    else:
        log_test("POST /api/marketing/social-posts/generate", False, status_code, 
                "Failed to generate AI social post", str(response)[:100])
        return False

# ===== BLUEPRINT MODULE TESTS =====

def test_blueprint_list():
    """Test GET /api/blueprint - List blueprints"""
    print("\n📋 Testing List Blueprints...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/blueprint", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/blueprint", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/blueprint", True, status_code, f"Retrieved {len(response)} blueprint(s)")
        return True
    else:
        log_test("GET /api/blueprint", False, status_code, 
                "Failed to get blueprints", str(response)[:100])
        return False

def test_blueprint_create():
    """Test POST /api/blueprint - Create blueprint"""
    print("\n📋 Testing Create Blueprint...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/blueprint", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    blueprint_data = {
        "businessName": "Test Tech Solutions",
        "industry": "Technology",
        "businessType": "SaaS",
        "description": "AI-powered business solutions",
        "targetMarket": "SME businesses",
        "fundingGoal": 250000
    }
    
    status_code, response = make_request("POST", "/blueprint", blueprint_data, headers)
    
    if status_code in [200, 201]:
        log_test("POST /api/blueprint", True, status_code, "Blueprint created successfully")
        return True
    else:
        log_test("POST /api/blueprint", False, status_code, 
                "Failed to create blueprint", str(response)[:100])
        return False

def test_blueprint_generate():
    """Test POST /api/blueprint/generate - Generate blueprint content"""
    print("\n🤖 Testing Generate Blueprint Content...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/blueprint/generate", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    generate_data = {
        "businessName": "Test Company",
        "industry": "Technology",
        "section": "executive_summary"
    }
    
    status_code, response = make_request("POST", "/blueprint/generate", generate_data, headers)
    
    if status_code == 200:
        log_test("POST /api/blueprint/generate", True, status_code, "Blueprint content generated successfully")
        return True
    else:
        log_test("POST /api/blueprint/generate", False, status_code, 
                "Failed to generate blueprint content", str(response)[:100])
        return False

def test_blueprint_generate_document():
    """Test POST /api/blueprint/generate-document - Generate business document"""
    print("\n📄 Testing Generate Business Document...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/blueprint/generate-document", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    doc_data = {
        "documentType": "business_plan",
        "companyName": "Test Company",
        "industry": "Technology"
    }
    
    status_code, response = make_request("POST", "/blueprint/generate-document", doc_data, headers)
    
    if status_code == 200:
        log_test("POST /api/blueprint/generate-document", True, status_code, "Business document generated successfully")
        return True
    else:
        log_test("POST /api/blueprint/generate-document", False, status_code, 
                "Failed to generate business document", str(response)[:100])
        return False

# ===== AI CHAT MODULE TESTS =====

def test_chat():
    """Test POST /api/chat - Send chat message (Advisory mode)"""
    print("\n🤖 Testing AI Chat (Advisory Mode)...")
    
    if not auth_token:
        log_test("POST /api/chat (Advisory)", False, None, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    chat_data = {
        "message": "What are the key steps to start a tech company?",
        "mode": "advisory"
    }
    
    status_code, response = make_request("POST", "/chat", chat_data, headers)
    
    if status_code == 200 and isinstance(response, dict) and "response" in response:
        log_test("POST /api/chat (Advisory)", True, status_code, "AI chat response received")
        return True
    else:
        log_test("POST /api/chat (Advisory)", False, status_code, 
                "Failed to get AI chat response", str(response)[:100])
        return False

def test_chat_data_backed():
    """Test POST /api/chat - Send chat message (Data-backed mode with company number)"""
    print("\n🤖 Testing AI Chat (Data-backed Mode)...")
    
    if not auth_token:
        log_test("POST /api/chat (Data-backed)", False, None, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    chat_data = {
        "message": "Analyze the financial health of this company",
        "mode": "data_backed",
        "company_number": "12345678"
    }
    
    status_code, response = make_request("POST", "/chat", chat_data, headers)
    
    if status_code == 200 and isinstance(response, dict) and "response" in response:
        log_test("POST /api/chat (Data-backed)", True, status_code, "Data-backed chat response received")
        return True
    else:
        log_test("POST /api/chat (Data-backed)", False, status_code, 
                "Failed to get data-backed chat response", str(response)[:100])
        return False

def test_chat_presentation():
    """Test POST /api/chat - Send chat message (Presentation mode)"""
    print("\n🤖 Testing AI Chat (Presentation Mode)...")
    
    if not auth_token:
        log_test("POST /api/chat (Presentation)", False, None, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    chat_data = {
        "message": "Create a pitch deck outline for a SaaS startup",
        "mode": "presentation"
    }
    
    status_code, response = make_request("POST", "/chat", chat_data, headers)
    
    if status_code == 200 and isinstance(response, dict) and "response" in response:
        log_test("POST /api/chat (Presentation)", True, status_code, "Presentation chat response received")
        return True
    else:
        log_test("POST /api/chat (Presentation)", False, status_code, 
                "Failed to get presentation chat response", str(response)[:100])
        return False

def test_chat_history():
    """Test GET /api/chat/history/{session_id} - Get chat history"""
    print("\n📜 Testing Get Chat History...")
    
    if not auth_token:
        log_test("GET /api/chat/history/{session_id}", False, None, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    session_id = "test-session-123"
    
    status_code, response = make_request("GET", f"/chat/history/{session_id}", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/chat/history/{session_id}", True, status_code, f"Retrieved {len(response)} chat message(s)")
        return True
    else:
        log_test("GET /api/chat/history/{session_id}", False, status_code, 
                "Failed to get chat history", str(response)[:100])
        return False

def test_chat_clear_history():
    """Test DELETE /api/chat/history/{session_id} - Clear chat history"""
    print("\n🗑️ Testing Clear Chat History...")
    
    if not auth_token:
        log_test("DELETE /api/chat/history/{session_id}", False, None, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    session_id = "test-session-123"
    
    status_code, response = make_request("DELETE", f"/chat/history/{session_id}", headers=headers)
    
    if status_code == 200:
        log_test("DELETE /api/chat/history/{session_id}", True, status_code, "Chat history cleared successfully")
        return True
    else:
        log_test("DELETE /api/chat/history/{session_id}", False, status_code, 
                "Failed to clear chat history", str(response)[:100])
        return False

def test_chat_modes():
    """Test GET /api/chat/modes - Get assistant modes info"""
    print("\n🤖 Testing Get Chat Modes Info...")
    
    if not auth_token:
        log_test("GET /api/chat/modes", False, None, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    status_code, response = make_request("GET", "/chat/modes", headers=headers)
    
    if status_code == 200:
        log_test("GET /api/chat/modes", True, status_code, "Chat modes info retrieved")
        return True
    else:
        log_test("GET /api/chat/modes", False, status_code, 
                "Failed to get chat modes info", str(response)[:100])
        return False

# ===== VALIDATION REPORTS MODULE TESTS =====

def test_validation_reports_list():
    """Test GET /api/validation-reports - List reports"""
    print("\n📊 Testing List Validation Reports...")
    
    if not auth_token or not workspace_id:
        log_test("GET /api/validation-reports", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_code, response = make_request("GET", "/validation-reports", headers=headers)
    
    if status_code == 200 and isinstance(response, list):
        log_test("GET /api/validation-reports", True, status_code, f"Retrieved {len(response)} validation report(s)")
        return True
    else:
        log_test("GET /api/validation-reports", False, status_code, 
                "Failed to get validation reports", str(response)[:100])
        return False

def test_validation_reports_create():
    """Test POST /api/validation-reports - Create report"""
    print("\n📊 Testing Create Validation Report...")
    
    if not auth_token or not workspace_id:
        log_test("POST /api/validation-reports", False, None, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    report_data = {
        "ideaType": "business",
        "ideaName": "AI Meal Planner",
        "ideaDescription": "An AI-powered meal planning app",
        "industry": "Technology",
        "targetAudience": "Busy professionals",
        "problemSolved": "Meal planning complexity"
    }
    
    status_code, response = make_request("POST", "/validation-reports", report_data, headers)
    
    if status_code in [200, 201]:
        log_test("POST /api/validation-reports", True, status_code, "Validation report created successfully")
        return True
    else:
        log_test("POST /api/validation-reports", False, status_code, 
                "Failed to create validation report", str(response)[:100])
        return False

def main():
    """Run comprehensive A-Z backend API testing"""
    print("🚀 COMPREHENSIVE A-Z BACKEND API TESTING - EnterprateAI Platform")
    print("=" * 80)
    print(f"🔗 Base URL: {API_BASE}")
    print(f"👤 Test User: {TEST_CREDENTIALS['email']}")
    print("=" * 80)
    
    # Track all test functions
    all_tests = [
        # Authentication Module
        test_auth_register,
        test_auth_login,
        test_auth_me,
        test_google_oauth_init,
        test_google_oauth_callback,
        
        # Workspace Module
        test_workspaces_list,
        test_workspaces_create,
        test_workspaces_get,
        
        # Company Profile Module
        test_company_profile_get,
        test_company_profile_create,
        test_company_profile_check_name,
        test_company_profile_confirm_registration,
        test_company_profile_generate_branding,
        test_company_profile_generate_website_content,
        
        # Finance Module
        test_finance_invoices_list,
        test_finance_invoices_create,
        test_finance_expenses_list,
        test_finance_expenses_create,
        test_finance_scan_receipt,
        test_finance_estimate_tax,
        test_finance_compliance_list,
        test_finance_compliance_create,
        test_finance_compliance_defaults,
        
        # Operations Module
        test_operations_tasks_list,
        test_operations_tasks_create,
        test_operations_email_templates_list,
        test_operations_email_templates_create,
        test_operations_email_logs,
        test_operations_generate_email,
        test_operations_send_approved_email,
        test_operations_pending_emails,
        
        # Marketing/Growth Module
        test_marketing_leads_list,
        test_marketing_leads_create,
        test_marketing_campaigns_list,
        test_marketing_campaigns_create,
        test_marketing_social_posts_list,
        test_marketing_social_posts_generate,
        
        # Blueprint Module
        test_blueprint_list,
        test_blueprint_create,
        test_blueprint_generate,
        test_blueprint_generate_document,
        
        # AI Chat Module
        test_chat,
        test_chat_data_backed,
        test_chat_presentation,
        test_chat_history,
        test_chat_clear_history,
        test_chat_modes,
        
        # Validation Reports Module
        test_validation_reports_list,
        test_validation_reports_create,
    ]
    
    # Run all tests
    for test_func in all_tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ ERROR in {test_func.__name__}: {str(e)}")
            log_test(test_func.__name__, False, None, f"Test error: {str(e)}")
    
    # Print comprehensive summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Total Passed: {passed_count}")
    print(f"❌ Total Failed: {failed_count}")
    print(f"📈 Success Rate: {(passed_count / (passed_count + failed_count) * 100):.1f}%")
    print(f"🔍 Total Endpoints Tested: {passed_count + failed_count}")
    
    # List all failures
    failures = [result for result in test_results if not result["success"]]
    if failures:
        print(f"\n❌ FAILED ENDPOINTS ({len(failures)}):")
        for failure in failures:
            print(f"   • {failure['test']} - {failure['details']}")
    
    # List all successes by category
    successes = [result for result in test_results if result["success"]]
    if successes:
        print(f"\n✅ SUCCESSFUL ENDPOINTS ({len(successes)}):")
        categories = {
            "Authentication": [s for s in successes if "auth" in s["test"].lower()],
            "Workspace": [s for s in successes if "workspace" in s["test"].lower()],
            "Company Profile": [s for s in successes if "company" in s["test"].lower()],
            "Finance": [s for s in successes if "finance" in s["test"].lower()],
            "Operations": [s for s in successes if "operations" in s["test"].lower()],
            "Marketing": [s for s in successes if "marketing" in s["test"].lower()],
            "Blueprint": [s for s in successes if "blueprint" in s["test"].lower()],
            "AI Chat": [s for s in successes if "chat" in s["test"].lower()],
            "Validation": [s for s in successes if "validation" in s["test"].lower()],
        }
        
        for category, tests in categories.items():
            if tests:
                print(f"   📁 {category}: {len(tests)} endpoints")
    
    print("=" * 80)
    
    return passed_count, failed_count

if __name__ == "__main__":
    main()