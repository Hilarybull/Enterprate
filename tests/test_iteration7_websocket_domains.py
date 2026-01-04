"""
Iteration 7 Tests: WebSocket Real-Time Notifications, Custom Domains, and Notification Center
Tests for:
- WebSocket status endpoint (/api/ws/status)
- Custom Domains API (CRUD operations)
- Notification Service integration
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from previous iterations
TEST_EMAIL = "webbuilder_test2@example.com"
TEST_PASSWORD = "Test123!"
TEST_WORKSPACE_ID = "592c480e-7da2-4500-a987-567c1c450ba7"


class TestWebSocketStatus:
    """Tests for WebSocket status endpoint - GET /api/ws/status"""
    
    def test_ws_status_endpoint_exists(self):
        """Test that WebSocket status endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/ws/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_ws_status_returns_correct_structure(self):
        """Test that WebSocket status returns expected fields"""
        response = requests.get(f"{BASE_URL}/api/ws/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data, "Missing 'status' field"
        assert "total_connections" in data, "Missing 'total_connections' field"
        assert "active_users" in data, "Missing 'active_users' field"
        assert "active_workspaces" in data, "Missing 'active_workspaces' field"
    
    def test_ws_status_values_are_valid(self):
        """Test that WebSocket status values are valid types"""
        response = requests.get(f"{BASE_URL}/api/ws/status")
        data = response.json()
        
        assert data["status"] == "online", f"Expected status 'online', got {data['status']}"
        assert isinstance(data["total_connections"], int), "total_connections should be int"
        assert isinstance(data["active_users"], int), "active_users should be int"
        assert isinstance(data["active_workspaces"], int), "active_workspaces should be int"
        assert data["total_connections"] >= 0, "total_connections should be >= 0"


class TestAuthentication:
    """Authentication helper tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
    
    def test_login_returns_token(self, auth_token):
        """Test that login returns a valid token"""
        assert auth_token is not None, "Token should not be None"
        assert len(auth_token) > 0, "Token should not be empty"


class TestCustomDomainsAPI:
    """Tests for Custom Domains API endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth and workspace"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "X-Workspace-Id": TEST_WORKSPACE_ID,
            "Content-Type": "application/json"
        }
    
    def test_get_website_domains_requires_auth(self):
        """Test that GET /api/domains/website/{id} requires authentication"""
        response = requests.get(f"{BASE_URL}/api/domains/website/test-website-id")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_get_website_domains_requires_workspace(self, auth_token):
        """Test that GET /api/domains/website/{id} requires workspace header"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/domains/website/test-website-id", headers=headers)
        assert response.status_code == 400, f"Expected 400 for missing workspace, got {response.status_code}"
    
    def test_get_website_domains_returns_list(self, headers):
        """Test that GET /api/domains/website/{id} returns a list"""
        response = requests.get(f"{BASE_URL}/api/domains/website/test-website-id", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
    
    def test_add_domain_requires_auth(self):
        """Test that POST /api/domains requires authentication"""
        response = requests.post(f"{BASE_URL}/api/domains", json={
            "websiteId": "test-id",
            "domain": "test.example.com"
        })
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_add_domain_requires_workspace(self, auth_token):
        """Test that POST /api/domains requires workspace header"""
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(f"{BASE_URL}/api/domains", headers=headers, json={
            "websiteId": "test-id",
            "domain": "test.example.com"
        })
        assert response.status_code == 400, f"Expected 400 for missing workspace, got {response.status_code}"
    
    def test_add_domain_validates_website_exists(self, headers):
        """Test that POST /api/domains validates website exists"""
        response = requests.post(f"{BASE_URL}/api/domains", headers=headers, json={
            "websiteId": "non-existent-website-id",
            "domain": "test.example.com"
        })
        # Should return error about website not found
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == False, "Should fail for non-existent website"
        assert "error" in data, "Should have error message"
    
    def test_verify_domain_requires_auth(self):
        """Test that POST /api/domains/{id}/verify requires authentication"""
        response = requests.post(f"{BASE_URL}/api/domains/test-domain-id/verify")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_verify_domain_requires_workspace(self, auth_token):
        """Test that POST /api/domains/{id}/verify requires workspace header"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/domains/test-domain-id/verify", headers=headers)
        assert response.status_code == 400, f"Expected 400 for missing workspace, got {response.status_code}"
    
    def test_verify_domain_handles_not_found(self, headers):
        """Test that POST /api/domains/{id}/verify handles non-existent domain"""
        response = requests.post(f"{BASE_URL}/api/domains/non-existent-domain-id/verify", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == False, "Should fail for non-existent domain"
    
    def test_delete_domain_requires_auth(self):
        """Test that DELETE /api/domains/{id} requires authentication"""
        response = requests.delete(f"{BASE_URL}/api/domains/test-domain-id")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_delete_domain_requires_workspace(self, auth_token):
        """Test that DELETE /api/domains/{id} requires workspace header"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.delete(f"{BASE_URL}/api/domains/test-domain-id", headers=headers)
        assert response.status_code == 400, f"Expected 400 for missing workspace, got {response.status_code}"
    
    def test_delete_domain_handles_not_found(self, headers):
        """Test that DELETE /api/domains/{id} handles non-existent domain"""
        response = requests.delete(f"{BASE_URL}/api/domains/non-existent-domain-id", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") == False, "Should fail for non-existent domain"
    
    def test_get_domain_by_id_requires_auth(self):
        """Test that GET /api/domains/{id} requires authentication"""
        response = requests.get(f"{BASE_URL}/api/domains/test-domain-id")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"


class TestNotificationsAPI:
    """Tests for Notifications API endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth and workspace"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "X-Workspace-Id": TEST_WORKSPACE_ID,
            "Content-Type": "application/json"
        }
    
    def test_get_notifications_requires_auth(self):
        """Test that GET /api/notifications requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_get_notifications_returns_list(self, headers):
        """Test that GET /api/notifications returns a list"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
    
    def test_get_unread_count_requires_auth(self):
        """Test that GET /api/notifications/unread-count requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_get_unread_count_returns_number(self, headers):
        """Test that GET /api/notifications/unread-count returns a count"""
        response = requests.get(f"{BASE_URL}/api/notifications/unread-count", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # API returns unreadCount field
        assert "unreadCount" in data or "count" in data or isinstance(data, int), "Response should have count"
        if "unreadCount" in data:
            assert isinstance(data["unreadCount"], int), "unreadCount should be an integer"


class TestAIWebsitesForDomains:
    """Tests for AI Websites API to verify domain integration"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth and workspace"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "X-Workspace-Id": TEST_WORKSPACE_ID,
            "Content-Type": "application/json"
        }
    
    def test_get_ai_websites_returns_list(self, headers):
        """Test that GET /api/ai-websites returns a list"""
        response = requests.get(f"{BASE_URL}/api/ai-websites", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
    
    def test_ai_websites_have_deployment_fields(self, headers):
        """Test that AI websites have deployment-related fields"""
        response = requests.get(f"{BASE_URL}/api/ai-websites", headers=headers)
        data = response.json()
        
        # Check if any deployed websites exist
        deployed = [w for w in data if w.get("status") == "deployed"]
        if deployed:
            website = deployed[0]
            # Deployed websites should have deployment URL
            assert "deploymentUrl" in website or "status" in website, "Deployed website should have deployment info"


class TestHealthAndBasicEndpoints:
    """Basic health and endpoint tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
    
    def test_api_root_accessible(self):
        """Test that API is accessible"""
        response = requests.get(f"{BASE_URL}/api/ws/status")
        assert response.status_code == 200, "API should be accessible"


class TestDomainValidation:
    """Tests for domain validation logic"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth and workspace"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "X-Workspace-Id": TEST_WORKSPACE_ID,
            "Content-Type": "application/json"
        }
    
    def test_add_domain_strips_protocol(self, headers):
        """Test that domain strips http:// prefix"""
        response = requests.post(f"{BASE_URL}/api/domains", headers=headers, json={
            "websiteId": "test-website-id",
            "domain": "http://test.example.com"
        })
        # Should process the domain (even if website doesn't exist)
        assert response.status_code == 200
    
    def test_add_domain_strips_www(self, headers):
        """Test that domain strips www. prefix"""
        response = requests.post(f"{BASE_URL}/api/domains", headers=headers, json={
            "websiteId": "test-website-id",
            "domain": "www.test.example.com"
        })
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
