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

TEST_VALIDATION_REPORT = {
    "ideaType": "business",
    "ideaName": "SmartMeal - AI Meal Planning",
    "ideaDescription": "An AI-powered meal planning app that creates personalized weekly meal plans based on dietary preferences, allergies, and available ingredients.",
    "industry": "Technology",
    "subIndustry": "FoodTech",
    "problemSolved": "People struggle to plan healthy meals consistently, leading to unhealthy eating habits and food waste.",
    "targetAudience": "Busy professionals aged 25-45 who want to eat healthier but lack time for meal planning",
    "urgencyLevel": "high",
    "howItWorks": "Users input dietary preferences, allergies, and pantry items. The AI generates a personalized weekly meal plan with recipes and shopping lists.",
    "deliveryModel": "saas",
    "targetMarket": "B2C",
    "targetLocation": "United States",
    "customerBudget": "medium",
    "goToMarketChannel": ["SEO", "Social", "Ads"]
}

# NEW MODULE TEST DATA

# Blueprint test data
TEST_BLUEPRINT = {
    "businessName": "TechFlow Solutions",
    "industry": "Technology",
    "businessType": "SaaS",
    "description": "AI-powered project management platform for tech teams",
    "targetMarket": "Small to medium tech companies",
    "fundingGoal": 500000
}

# Finance test data
TEST_EXPENSE = {
    "description": "Office supplies and equipment",
    "amount": 450.75,
    "category": "office",  # Fixed: use valid enum value
    "date": "2024-01-15",
    "vendor": "Office Depot",
    "receiptUrl": "https://example.com/receipt.jpg"
}

TEST_TAX_ESTIMATE = {
    "annualRevenue": 120000,  # Fixed: correct field name
    "annualExpenses": 45000,  # Fixed: correct field name
    "businessType": "ltd",
    "country": "UK"  # Added required field
}

TEST_COMPLIANCE_ITEM = {
    "title": "VAT Registration",
    "description": "Register for VAT if turnover exceeds £85,000",
    "category": "tax",
    "dueDate": "2024-03-31",
    "priority": "high"
}

# Operations test data
TEST_TASK = {
    "title": "Implement user authentication system",
    "description": "Build secure login and registration functionality",
    "priority": "high",
    "dueDate": "2024-02-15",
    "assignee": "dev-team"  # Fixed: correct field name
}

TEST_EMAIL_TEMPLATE = {
    "name": "Welcome Email",
    "subject": "Welcome to TechFlow Solutions!",
    "bodyHtml": "<h1>Welcome!</h1><p>Thank you for joining us. We're excited to have you on board!</p>",  # Fixed: required field
    "bodyText": "Welcome! Thank you for joining us. We're excited to have you on board!",
    "category": "general"
}

TEST_EMAIL_SEND = {
    "to": ["customer@example.com"],  # Fixed: must be a list
    "templateId": None,  # Will be set after template creation
    "subject": "Welcome to our platform",
    "bodyHtml": "<p>Thank you for signing up!</p>"
}

TEST_DOCUMENT = {
    "name": "Company Privacy Policy",  # Fixed: correct field name
    "type": "pdf",  # Fixed: required field
    "content": "This document outlines our privacy practices...",
    "category": "legal"
}

TEST_WORKFLOW = {
    "name": "Customer Onboarding",
    "description": "Standard process for new customer onboarding",
    "category": "customer_success",
    "steps": [  # Fixed: use correct WorkflowStep schema
        {
            "id": "step-1",
            "title": "Send welcome email",
            "description": "Send automated welcome email to new customer",
            "order": 1,
            "action": "email"
        },
        {
            "id": "step-2", 
            "title": "Schedule onboarding call",
            "description": "Book initial onboarding call with customer success team",
            "order": 2,
            "action": "task"
        },
        {
            "id": "step-3",
            "title": "Provide access credentials", 
            "description": "Send login credentials and setup instructions",
            "order": 3,
            "action": "email"
        }
    ]
}

# Marketing test data
TEST_CAMPAIGN = {
    "name": "Q1 Product Launch",
    "description": "Launch campaign for our new AI features",
    "type": "content",  # Fixed: use valid enum value
    "budget": 15000,
    "startDate": "2024-02-01",
    "endDate": "2024-03-31"
}

TEST_SOCIAL_POST = {
    "platform": "linkedin",
    "content": "Excited to announce our new AI-powered project management features! 🚀",
    "scheduledFor": "2024-02-01T10:00:00Z",
    "campaignId": None  # Will be set after campaign creation
}

TEST_SOCIAL_GENERATE = {
    "platform": "twitter",
    "topic": "AI project management",
    "tone": "professional",
    "includeHashtags": True
}

# Global variables for test state
auth_token = None
workspace_id = None
validation_report_id = None
blueprint_id = None
expense_id = None
compliance_item_id = None
task_id = None
email_template_id = None
document_id = None
workflow_id = None
campaign_id = None
social_post_id = None
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
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=default_headers, timeout=30)
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

def test_create_validation_report():
    """Test validation report creation API"""
    print("\n📊 Testing Validation Report Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Validation Report Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/validation-reports", TEST_VALIDATION_REPORT, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "report" in response:
            global validation_report_id
            validation_report_id = response["id"]
            report = response.get("report", {})
            scores = report.get("scores", {})
            opp_score = scores.get("opportunity", {}).get("value", 0)
            log_test("Validation Report Creation", True, 
                    f"Report created: {response.get('ideaInput', {}).get('ideaName', 'Unknown')} (Score: {opp_score}/10)")
            return True
        else:
            log_test("Validation Report Creation", False, "Missing id or report in response", response)
            return False
    else:
        log_test("Validation Report Creation", False, "Report creation failed", response)
        return False

def test_list_validation_reports():
    """Test list validation reports API"""
    print("\n📋 Testing List Validation Reports...")
    
    if not auth_token or not workspace_id:
        log_test("List Validation Reports", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/validation-reports", headers=headers)
    
    if success and isinstance(response, list):
        if len(response) > 0:
            first_report = response[0]
            if "id" in first_report and "ideaName" in first_report:
                log_test("List Validation Reports", True, 
                        f"Retrieved {len(response)} report(s), first: {first_report.get('ideaName')}")
                return True
            else:
                log_test("List Validation Reports", False, "Missing required fields in report items", response)
                return False
        else:
            log_test("List Validation Reports", True, "No reports found (empty list)")
            return True
    else:
        log_test("List Validation Reports", False, "Failed to get reports list", response)
        return False

def test_get_validation_report():
    """Test get specific validation report API"""
    print("\n📄 Testing Get Validation Report...")
    
    if not auth_token or not workspace_id or not validation_report_id:
        log_test("Get Validation Report", False, "Missing auth token, workspace ID, or report ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", f"/validation-reports/{validation_report_id}", headers=headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "report" in response and "ideaInput" in response:
            idea_name = response.get("ideaInput", {}).get("ideaName", "Unknown")
            status = response.get("status", "unknown")
            log_test("Get Validation Report", True, 
                    f"Retrieved report: {idea_name} (Status: {status})")
            return True
        else:
            log_test("Get Validation Report", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Get Validation Report", False, "Failed to get specific report", response)
        return False

def test_update_report_status():
    """Test update validation report status API"""
    print("\n✅ Testing Update Report Status...")
    
    if not auth_token or not workspace_id or not validation_report_id:
        log_test("Update Report Status", False, "Missing auth token, workspace ID, or report ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    status_data = {"status": "accepted"}
    success, response = make_request("PUT", f"/validation-reports/{validation_report_id}/status", status_data, headers)
    
    if success and isinstance(response, dict):
        if "message" in response and "report" in response:
            updated_status = response.get("report", {}).get("status", "unknown")
            log_test("Update Report Status", True, 
                    f"Status updated to: {updated_status}")
            return True
        else:
            log_test("Update Report Status", False, "Missing message or report in response", response)
            return False
    else:
        log_test("Update Report Status", False, "Failed to update report status", response)
        return False

def test_get_engagement_stats():
    """Test get engagement statistics API"""
    print("\n📈 Testing Get Engagement Stats...")
    
    if not auth_token or not workspace_id:
        log_test("Get Engagement Stats", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/validation-reports/engagement", headers=headers)
    
    if success and isinstance(response, dict):
        if "totalValidations" in response:
            total = response.get("totalValidations", 0)
            accepted = response.get("acceptedCount", 0)
            rejected = response.get("rejectedCount", 0)
            pending = response.get("pendingCount", 0)
            log_test("Get Engagement Stats", True, 
                    f"Stats: {total} total, {accepted} accepted, {rejected} rejected, {pending} pending")
            return True
        else:
            log_test("Get Engagement Stats", False, "Missing totalValidations in response", response)
            return False
    else:
        log_test("Get Engagement Stats", False, "Failed to get engagement stats", response)
        return False

def test_modify_validation_report():
    """Test modify and regenerate validation report API"""
    print("\n🔄 Testing Modify Validation Report...")
    
    if not auth_token or not workspace_id or not validation_report_id:
        log_test("Modify Validation Report", False, "Missing auth token, workspace ID, or report ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    # Modified test data
    modified_data = TEST_VALIDATION_REPORT.copy()
    modified_data["ideaName"] = "SmartMeal Pro - Enhanced AI Meal Planning"
    modified_data["urgencyLevel"] = "medium"
    modified_data["customerBudget"] = "high"
    
    success, response = make_request("POST", f"/validation-reports/{validation_report_id}/modify", modified_data, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "report" in response:
            idea_name = response.get("ideaInput", {}).get("ideaName", "Unknown")
            status = response.get("status", "unknown")
            log_test("Modify Validation Report", True, 
                    f"Report modified: {idea_name} (Status reset to: {status})")
            return True
        else:
            log_test("Modify Validation Report", False, "Missing id or report in response", response)
            return False
    else:
        log_test("Modify Validation Report", False, "Failed to modify report", response)
        return False


# ===== BLUEPRINT MODULE TESTS =====

def test_create_blueprint():
    """Test blueprint creation API"""
    print("\n📋 Testing Blueprint Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Blueprint Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/blueprint", TEST_BLUEPRINT, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "businessName" in response:
            global blueprint_id
            blueprint_id = response["id"]
            log_test("Blueprint Creation", True, 
                    f"Blueprint created: {response.get('businessName')} (ID: {blueprint_id})")
            return True
        else:
            log_test("Blueprint Creation", False, "Missing id or businessName in response", response)
            return False
    else:
        log_test("Blueprint Creation", False, "Blueprint creation failed", response)
        return False


def test_get_blueprints():
    """Test get blueprints API"""
    print("\n📋 Testing Get Blueprints...")
    
    if not auth_token or not workspace_id:
        log_test("Get Blueprints", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/blueprint", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Blueprints", True, f"Retrieved {len(response)} blueprint(s)")
        return True
    else:
        log_test("Get Blueprints", False, "Failed to get blueprints", response)
        return False


def test_get_blueprint():
    """Test get specific blueprint API"""
    print("\n📄 Testing Get Specific Blueprint...")
    
    if not auth_token or not workspace_id or not blueprint_id:
        log_test("Get Specific Blueprint", False, "Missing auth token, workspace ID, or blueprint ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", f"/blueprint/{blueprint_id}", headers=headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "businessName" in response:
            log_test("Get Specific Blueprint", True, 
                    f"Retrieved blueprint: {response.get('businessName')}")
            return True
        else:
            log_test("Get Specific Blueprint", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Get Specific Blueprint", False, "Failed to get specific blueprint", response)
        return False


def test_generate_blueprint_section():
    """Test generate blueprint section API"""
    print("\n🤖 Testing Generate Blueprint Section...")
    
    if not auth_token or not workspace_id or not blueprint_id:
        log_test("Generate Blueprint Section", False, "Missing auth token, workspace ID, or blueprint ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", f"/blueprint/{blueprint_id}/generate-section/executive_summary", None, headers)
    
    if success and isinstance(response, dict):
        if "section" in response or "content" in response:
            log_test("Generate Blueprint Section", True, "Executive summary section generated successfully")
            return True
        else:
            log_test("Generate Blueprint Section", False, "Missing section content in response", response)
            return False
    else:
        log_test("Generate Blueprint Section", False, "Failed to generate blueprint section", response)
        return False


def test_generate_swot():
    """Test generate SWOT analysis API"""
    print("\n📊 Testing Generate SWOT Analysis...")
    
    if not auth_token or not workspace_id or not blueprint_id:
        log_test("Generate SWOT Analysis", False, "Missing auth token, workspace ID, or blueprint ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", f"/blueprint/{blueprint_id}/generate-swot", None, headers)
    
    if success and isinstance(response, dict):
        # Check for SWOT components
        if "strengths" in response and "weaknesses" in response and "opportunities" in response and "threats" in response:
            log_test("Generate SWOT Analysis", True, "SWOT analysis generated successfully")
            return True
        else:
            log_test("Generate SWOT Analysis", False, "Missing SWOT components in response", response)
            return False
    else:
        log_test("Generate SWOT Analysis", False, "Failed to generate SWOT analysis", response)
        return False


def test_generate_financials():
    """Test generate financial projections API"""
    print("\n💰 Testing Generate Financial Projections...")
    
    if not auth_token or not workspace_id or not blueprint_id:
        log_test("Generate Financial Projections", False, "Missing auth token, workspace ID, or blueprint ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", f"/blueprint/{blueprint_id}/generate-financials", None, headers)
    
    if success and isinstance(response, list):
        # Check if it's a list of financial projections
        if len(response) > 0 and "year" in response[0] and "revenue" in response[0]:
            log_test("Generate Financial Projections", True, f"Financial projections generated for {len(response)} years")
            return True
        else:
            log_test("Generate Financial Projections", False, "Invalid financial projections format", response)
            return False
    else:
        log_test("Generate Financial Projections", False, "Failed to generate financial projections", response)
        return False


# ===== FINANCE MODULE TESTS =====

def test_create_expense():
    """Test expense creation API"""
    print("\n💸 Testing Expense Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Expense Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/finance/expenses", TEST_EXPENSE, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "description" in response:
            global expense_id
            expense_id = response["id"]
            log_test("Expense Creation", True, 
                    f"Expense created: {response.get('description')} - ${response.get('amount')}")
            return True
        else:
            log_test("Expense Creation", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Expense Creation", False, "Expense creation failed", response)
        return False


def test_get_expenses():
    """Test get expenses API"""
    print("\n📊 Testing Get Expenses...")
    
    if not auth_token or not workspace_id:
        log_test("Get Expenses", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/finance/expenses", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Expenses", True, f"Retrieved {len(response)} expense(s)")
        return True
    else:
        log_test("Get Expenses", False, "Failed to get expenses", response)
        return False


def test_get_expense_summary():
    """Test get expense summary API"""
    print("\n📈 Testing Get Expense Summary...")
    
    if not auth_token or not workspace_id:
        log_test("Get Expense Summary", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/finance/expenses/summary", headers=headers)
    
    if success and isinstance(response, dict):
        if "totalAmount" in response or "count" in response:
            total = response.get("totalAmount", 0)
            count = response.get("count", 0)
            log_test("Get Expense Summary", True, f"Summary: {count} expenses, total: ${total}")
            return True
        else:
            log_test("Get Expense Summary", False, "Missing summary fields in response", response)
            return False
    else:
        log_test("Get Expense Summary", False, "Failed to get expense summary", response)
        return False


def test_estimate_tax():
    """Test tax estimation API"""
    print("\n🧮 Testing Tax Estimation...")
    
    if not auth_token or not workspace_id:
        log_test("Tax Estimation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/finance/estimate-tax", TEST_TAX_ESTIMATE, headers)
    
    if success and isinstance(response, dict):
        if "estimatedTax" in response or "taxBreakdown" in response:
            estimated_tax = response.get("estimatedTax", 0)
            log_test("Tax Estimation", True, f"Estimated tax: £{estimated_tax}")
            return True
        else:
            log_test("Tax Estimation", False, "Missing tax estimation in response", response)
            return False
    else:
        log_test("Tax Estimation", False, "Tax estimation failed", response)
        return False


def test_create_compliance_item():
    """Test compliance item creation API"""
    print("\n✅ Testing Compliance Item Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Compliance Item Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/finance/compliance", TEST_COMPLIANCE_ITEM, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "title" in response:
            global compliance_item_id
            compliance_item_id = response["id"]
            log_test("Compliance Item Creation", True, 
                    f"Compliance item created: {response.get('title')}")
            return True
        else:
            log_test("Compliance Item Creation", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Compliance Item Creation", False, "Compliance item creation failed", response)
        return False


def test_get_compliance_items():
    """Test get compliance items API"""
    print("\n📋 Testing Get Compliance Items...")
    
    if not auth_token or not workspace_id:
        log_test("Get Compliance Items", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/finance/compliance", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Compliance Items", True, f"Retrieved {len(response)} compliance item(s)")
        return True
    else:
        log_test("Get Compliance Items", False, "Failed to get compliance items", response)
        return False


def test_get_default_compliance():
    """Test get default compliance checklist API"""
    print("\n📝 Testing Get Default Compliance...")
    
    if not auth_token:
        log_test("Get Default Compliance", False, "Missing auth token")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    success, response = make_request("GET", "/finance/compliance/defaults?business_type=ltd", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Default Compliance", True, f"Retrieved {len(response)} default compliance item(s)")
        return True
    else:
        log_test("Get Default Compliance", False, "Failed to get default compliance", response)
        return False


# ===== OPERATIONS MODULE TESTS =====

def test_create_task():
    """Test task creation API"""
    print("\n📝 Testing Task Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Task Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/operations/tasks", TEST_TASK, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "title" in response:
            global task_id
            task_id = response["id"]
            log_test("Task Creation", True, 
                    f"Task created: {response.get('title')} (Priority: {response.get('priority')})")
            return True
        else:
            log_test("Task Creation", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Task Creation", False, "Task creation failed", response)
        return False


def test_get_tasks():
    """Test get tasks API"""
    print("\n📋 Testing Get Tasks...")
    
    if not auth_token or not workspace_id:
        log_test("Get Tasks", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/operations/tasks", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Tasks", True, f"Retrieved {len(response)} task(s)")
        return True
    else:
        log_test("Get Tasks", False, "Failed to get tasks", response)
        return False


def test_get_task_stats():
    """Test get task statistics API"""
    print("\n📊 Testing Get Task Stats...")
    
    if not auth_token or not workspace_id:
        log_test("Get Task Stats", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/operations/tasks/stats", headers=headers)
    
    if success and isinstance(response, dict):
        if "total" in response and "byStatus" in response:
            total = response.get("total", 0)
            by_status = response.get("byStatus", {})
            log_test("Get Task Stats", True, f"Stats: {total} total tasks, status breakdown available")
            return True
        else:
            log_test("Get Task Stats", False, "Missing stats fields in response", response)
            return False
    else:
        log_test("Get Task Stats", False, "Failed to get task stats", response)
        return False


def test_create_email_template():
    """Test email template creation API"""
    print("\n📧 Testing Email Template Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Email Template Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/operations/email-templates", TEST_EMAIL_TEMPLATE, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "name" in response:
            global email_template_id
            email_template_id = response["id"]
            log_test("Email Template Creation", True, 
                    f"Email template created: {response.get('name')}")
            return True
        else:
            log_test("Email Template Creation", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Email Template Creation", False, "Email template creation failed", response)
        return False


def test_get_email_templates():
    """Test get email templates API"""
    print("\n📧 Testing Get Email Templates...")
    
    if not auth_token or not workspace_id:
        log_test("Get Email Templates", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/operations/email-templates", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Email Templates", True, f"Retrieved {len(response)} email template(s)")
        return True
    else:
        log_test("Get Email Templates", False, "Failed to get email templates", response)
        return False


def test_send_email():
    """Test send email API (MOCKED)"""
    print("\n📤 Testing Send Email (MOCKED)...")
    
    if not auth_token or not workspace_id:
        log_test("Send Email", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/operations/send-email", TEST_EMAIL_SEND, headers)
    
    if success and isinstance(response, dict):
        if "messageId" in response or "status" in response:
            log_test("Send Email", True, "Email sent successfully (MOCKED)")
            return True
        else:
            log_test("Send Email", False, "Missing email response fields", response)
            return False
    else:
        log_test("Send Email", False, "Email sending failed", response)
        return False


def test_get_email_logs():
    """Test get email logs API"""
    print("\n📜 Testing Get Email Logs...")
    
    if not auth_token or not workspace_id:
        log_test("Get Email Logs", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/operations/email-logs", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Email Logs", True, f"Retrieved {len(response)} email log(s)")
        return True
    else:
        log_test("Get Email Logs", False, "Failed to get email logs", response)
        return False


def test_create_document():
    """Test document creation API"""
    print("\n📄 Testing Document Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Document Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/operations/documents", TEST_DOCUMENT, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "title" in response:
            global document_id
            document_id = response["id"]
            log_test("Document Creation", True, 
                    f"Document created: {response.get('title')}")
            return True
        else:
            log_test("Document Creation", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Document Creation", False, "Document creation failed", response)
        return False


def test_get_documents():
    """Test get documents API"""
    print("\n📚 Testing Get Documents...")
    
    if not auth_token or not workspace_id:
        log_test("Get Documents", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/operations/documents", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Documents", True, f"Retrieved {len(response)} document(s)")
        return True
    else:
        log_test("Get Documents", False, "Failed to get documents", response)
        return False


def test_create_workflow():
    """Test workflow creation API"""
    print("\n🔄 Testing Workflow Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Workflow Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/operations/workflows", TEST_WORKFLOW, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "name" in response:
            global workflow_id
            workflow_id = response["id"]
            log_test("Workflow Creation", True, 
                    f"Workflow created: {response.get('name')}")
            return True
        else:
            log_test("Workflow Creation", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Workflow Creation", False, "Workflow creation failed", response)
        return False


def test_get_workflows():
    """Test get workflows API"""
    print("\n🔄 Testing Get Workflows...")
    
    if not auth_token or not workspace_id:
        log_test("Get Workflows", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/operations/workflows", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Workflows", True, f"Retrieved {len(response)} workflow(s)")
        return True
    else:
        log_test("Get Workflows", False, "Failed to get workflows", response)
        return False


def test_get_default_workflows():
    """Test get default workflows API"""
    print("\n📋 Testing Get Default Workflows...")
    
    if not auth_token:
        log_test("Get Default Workflows", False, "Missing auth token")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    success, response = make_request("GET", "/operations/workflows/defaults", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Default Workflows", True, f"Retrieved {len(response)} default workflow(s)")
        return True
    else:
        log_test("Get Default Workflows", False, "Failed to get default workflows", response)
        return False


# ===== MARKETING MODULE TESTS =====

def test_create_campaign():
    """Test campaign creation API"""
    print("\n🚀 Testing Campaign Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Campaign Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/marketing/campaigns", TEST_CAMPAIGN, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "name" in response:
            global campaign_id
            campaign_id = response["id"]
            log_test("Campaign Creation", True, 
                    f"Campaign created: {response.get('name')} (Budget: ${response.get('budget')})")
            return True
        else:
            log_test("Campaign Creation", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Campaign Creation", False, "Campaign creation failed", response)
        return False


def test_get_campaigns():
    """Test get campaigns API"""
    print("\n📊 Testing Get Campaigns...")
    
    if not auth_token or not workspace_id:
        log_test("Get Campaigns", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/marketing/campaigns", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Campaigns", True, f"Retrieved {len(response)} campaign(s)")
        return True
    else:
        log_test("Get Campaigns", False, "Failed to get campaigns", response)
        return False


def test_create_social_post():
    """Test social post creation API"""
    print("\n📱 Testing Social Post Creation...")
    
    if not auth_token or not workspace_id:
        log_test("Social Post Creation", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    # Set campaign ID if available
    test_post = TEST_SOCIAL_POST.copy()
    if campaign_id:
        test_post["campaignId"] = campaign_id
    
    success, response = make_request("POST", "/marketing/social-posts", test_post, headers)
    
    if success and isinstance(response, dict):
        if "id" in response and "platform" in response:
            global social_post_id
            social_post_id = response["id"]
            log_test("Social Post Creation", True, 
                    f"Social post created for {response.get('platform')}")
            return True
        else:
            log_test("Social Post Creation", False, "Missing required fields in response", response)
            return False
    else:
        log_test("Social Post Creation", False, "Social post creation failed", response)
        return False


def test_get_social_posts():
    """Test get social posts API"""
    print("\n📱 Testing Get Social Posts...")
    
    if not auth_token or not workspace_id:
        log_test("Get Social Posts", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/marketing/social-posts", headers=headers)
    
    if success and isinstance(response, list):
        log_test("Get Social Posts", True, f"Retrieved {len(response)} social post(s)")
        return True
    else:
        log_test("Get Social Posts", False, "Failed to get social posts", response)
        return False


def test_generate_social_post():
    """Test AI generate social post API"""
    print("\n🤖 Testing AI Generate Social Post...")
    
    if not auth_token or not workspace_id:
        log_test("AI Generate Social Post", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("POST", "/marketing/social-posts/generate", TEST_SOCIAL_GENERATE, headers)
    
    if success and isinstance(response, dict):
        if "content" in response or "generatedContent" in response:
            content = response.get("content") or response.get("generatedContent", "")
            log_test("AI Generate Social Post", True, 
                    f"AI generated social post ({len(content)} chars)")
            return True
        else:
            log_test("AI Generate Social Post", False, "Missing generated content in response", response)
            return False
    else:
        log_test("AI Generate Social Post", False, "AI social post generation failed", response)
        return False


def test_get_growth_analytics():
    """Test get growth analytics API"""
    print("\n📈 Testing Get Growth Analytics...")
    
    if not auth_token or not workspace_id:
        log_test("Get Growth Analytics", False, "Missing auth token or workspace ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-Id": workspace_id
    }
    
    success, response = make_request("GET", "/marketing/analytics", headers=headers)
    
    if success and isinstance(response, dict):
        if "totalLeads" in response or "campaignMetrics" in response:
            leads = response.get("totalLeads", 0)
            campaigns = response.get("totalCampaigns", 0)
            log_test("Get Growth Analytics", True, 
                    f"Analytics: {leads} leads, {campaigns} campaigns")
            return True
        else:
            log_test("Get Growth Analytics", False, "Missing analytics fields in response", response)
            return False
    else:
        log_test("Get Growth Analytics", False, "Failed to get growth analytics", response)
        return False

def run_all_tests():
    """Run all backend API tests in sequence"""
    print("🚀 Starting Enterprate OS Backend API Tests - FOUR NEW MODULES")
    print("=" * 80)
    
    # Test sequence as specified in review request
    tests = [
        # Core authentication and workspace setup
        test_user_registration,
        test_user_login,
        test_workspace_creation,
        test_get_workspaces,
        
        # Module 1: Business Blueprint Generator
        test_create_blueprint,
        test_get_blueprints,
        test_get_blueprint,
        test_generate_blueprint_section,
        test_generate_swot,
        test_generate_financials,
        
        # Module 2: Finance & Compliance
        test_create_expense,
        test_get_expenses,
        test_get_expense_summary,
        test_estimate_tax,
        test_create_compliance_item,
        test_get_compliance_items,
        test_get_default_compliance,
        
        # Module 3: Operations
        test_create_task,
        test_get_tasks,
        test_get_task_stats,
        test_create_email_template,
        test_get_email_templates,
        test_send_email,
        test_get_email_logs,
        test_create_document,
        test_get_documents,
        test_create_workflow,
        test_get_workflows,
        test_get_default_workflows,
        
        # Module 4: Growth/Marketing
        test_create_campaign,
        test_get_campaigns,
        test_create_social_post,
        test_get_social_posts,
        test_generate_social_post,
        test_get_growth_analytics,
        
        # Legacy tests (existing functionality)
        test_invoice_creation,
        test_get_invoices,
        test_lead_creation,
        test_get_leads,
        test_idea_scoring,
        test_get_events,
        test_ai_chat,
        test_create_validation_report,
        test_list_validation_reports,
        test_get_validation_report,
        test_update_report_status,
        test_get_engagement_stats,
        test_modify_validation_report
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
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY - FOUR NEW MODULES")
    print("=" * 80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    # Module breakdown
    print("\n🔍 MODULE BREAKDOWN:")
    print("   📋 Blueprint Generator: 6 endpoints")
    print("   💰 Finance & Compliance: 7 endpoints") 
    print("   ⚙️  Operations: 12 endpoints")
    print("   📈 Marketing/Growth: 6 endpoints")
    print("   🔧 Legacy APIs: 17 endpoints")
    print(f"   📊 Total: {len(tests)} endpoints tested")
    
    if failed > 0:
        print("\n🔍 FAILED TESTS:")
        for result in test_results:
            if not result["success"]:
                print(f"   • {result['test']}: {result['details']}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)