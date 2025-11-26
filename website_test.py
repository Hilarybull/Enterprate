#!/usr/bin/env python3
"""
Quick test for Website APIs
"""

import requests
import json

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

BACKEND_URL = get_backend_url()
API_BASE = f"{BACKEND_URL}/api"

# Use existing test user credentials
TEST_USER = {
    "email": "enterprate.test@example.com",
    "password": "SecureTest123!"
}

TEST_WEBSITE = {
    "name": "Enterprate Test Website",
    "domain": "test.enterprate.com"
}

def login_and_get_workspace():
    """Login and get workspace info"""
    # Login
    login_response = requests.post(f"{API_BASE}/auth/login", json=TEST_USER)
    if login_response.status_code != 200:
        print("❌ Login failed")
        return None, None
    
    token = login_response.json()["token"]
    
    # Get workspaces
    headers = {"Authorization": f"Bearer {token}"}
    workspace_response = requests.get(f"{API_BASE}/workspaces", headers=headers)
    if workspace_response.status_code != 200 or not workspace_response.json():
        print("❌ No workspaces found")
        return None, None
    
    workspace_id = workspace_response.json()[0]["id"]
    return token, workspace_id

def test_website_apis():
    """Test website CRUD operations"""
    print("🌐 Testing Website APIs...")
    
    token, workspace_id = login_and_get_workspace()
    if not token or not workspace_id:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": workspace_id,
        "Content-Type": "application/json"
    }
    
    # Test create website
    create_response = requests.post(f"{API_BASE}/websites", json=TEST_WEBSITE, headers=headers)
    if create_response.status_code != 200:
        print(f"❌ Website creation failed: {create_response.status_code} - {create_response.text}")
        return False
    
    website_data = create_response.json()
    website_id = website_data.get("id")
    print(f"✅ Website created: {website_data.get('name')} (ID: {website_id})")
    
    # Test get websites
    get_response = requests.get(f"{API_BASE}/websites", headers=headers)
    if get_response.status_code != 200:
        print(f"❌ Get websites failed: {get_response.status_code} - {get_response.text}")
        return False
    
    websites = get_response.json()
    print(f"✅ Retrieved {len(websites)} website(s)")
    
    # Test get specific website
    if website_id:
        get_one_response = requests.get(f"{API_BASE}/websites/{website_id}", headers=headers)
        if get_one_response.status_code == 200:
            print(f"✅ Retrieved specific website: {get_one_response.json().get('name')}")
        else:
            print(f"❌ Get specific website failed: {get_one_response.status_code}")
    
    return True

if __name__ == "__main__":
    success = test_website_apis()
    print(f"\n🌐 Website API Test: {'✅ PASSED' if success else '❌ FAILED'}")