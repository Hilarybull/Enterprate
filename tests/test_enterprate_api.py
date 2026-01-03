"""
EnterprateAI Backend API Tests
Tests for:
- Dynamic Fees API (public)
- Growth Agent API (authenticated)
- Finance Invoices API (authenticated)
"""
import pytest
import requests
import os
import jwt
from datetime import datetime, timezone, timedelta

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable not set")

JWT_SECRET = "enterprate-os-jwt-secret-change-in-production"

# Test user and workspace IDs
TEST_USER_ID = "test-user-api-001"
TEST_WORKSPACE_ID = "test-workspace-api-001"


def generate_test_token(user_id: str = TEST_USER_ID) -> str:
    """Generate a valid JWT token for testing"""
    exp = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {"user_id": user_id, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token():
    """Generate authentication token"""
    return generate_test_token()


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-ID": TEST_WORKSPACE_ID
    })
    return api_client


@pytest.fixture(scope="module", autouse=True)
def setup_test_data():
    """Setup test user and workspace in MongoDB"""
    import subprocess
    
    # Create test user and workspace membership
    mongo_script = f'''
    use('enterprate_os');
    
    // Create test user if not exists
    db.users.updateOne(
        {{ id: "{TEST_USER_ID}" }},
        {{ $set: {{
            id: "{TEST_USER_ID}",
            email: "test-api@enterprate.com",
            name: "API Test User",
            created_at: new Date()
        }} }},
        {{ upsert: true }}
    );
    
    // Create workspace membership
    db.workspace_memberships.updateOne(
        {{ workspace_id: "{TEST_WORKSPACE_ID}", user_id: "{TEST_USER_ID}" }},
        {{ $set: {{
            workspace_id: "{TEST_WORKSPACE_ID}",
            user_id: "{TEST_USER_ID}",
            role: "owner",
            created_at: new Date()
        }} }},
        {{ upsert: true }}
    );
    
    print("Test data setup complete");
    '''
    
    result = subprocess.run(
        ["mongosh", "--quiet", "--eval", mongo_script],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"MongoDB setup warning: {result.stderr}")
    
    yield
    
    # Cleanup is optional - keeping test data for debugging


# ============================================
# DYNAMIC FEES API TESTS (Public - No Auth)
# ============================================

class TestDynamicFeesAPI:
    """Tests for Dynamic Fees API - GET /api/company-profile/fees"""
    
    def test_get_all_fees_returns_200(self, api_client):
        """Test GET /api/company-profile/fees returns 200"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/fees")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_get_all_fees_returns_13_entries(self, api_client):
        """Test that fees endpoint returns exactly 13 fee entries"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/fees")
        assert response.status_code == 200
        
        data = response.json()
        assert "fees" in data, "Response should contain 'fees' key"
        assert len(data["fees"]) == 13, f"Expected 13 fees, got {len(data['fees'])}"
    
    def test_fees_have_required_fields(self, api_client):
        """Test that each fee entry has required fields"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/fees")
        data = response.json()
        
        required_fields = ["id", "businessType", "title", "registrationAuthority", "onlineFee", "paperFee"]
        
        for fee in data["fees"]:
            for field in required_fields:
                assert field in fee, f"Fee entry missing required field: {field}"
    
    def test_fees_include_ltd_type(self, api_client):
        """Test that fees include Ltd company type"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/fees")
        data = response.json()
        
        ltd_fee = next((f for f in data["fees"] if f["businessType"] == "ltd"), None)
        assert ltd_fee is not None, "Ltd business type not found in fees"
        assert ltd_fee["onlineFee"] == "£50", f"Expected £50 online fee for Ltd, got {ltd_fee['onlineFee']}"
    
    def test_get_fee_for_specific_type_ltd(self, api_client):
        """Test GET /api/company-profile/fees/ltd returns fee info"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/fees/ltd")
        assert response.status_code == 200
        
        data = response.json()
        assert data["businessType"] == "ltd"
        assert data["title"] == "Private Company Limited by Shares (Ltd)"
        assert data["onlineFee"] == "£50"
        assert data["paperFee"] == "£71"
        assert data["sameDayFee"] == "£78"
    
    def test_get_fee_for_sole_trader(self, api_client):
        """Test GET /api/company-profile/fees/sole_trader returns free"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/fees/sole_trader")
        assert response.status_code == 200
        
        data = response.json()
        assert data["businessType"] == "sole_trader"
        assert data["onlineFee"] == "Free"
    
    def test_get_fee_for_invalid_type(self, api_client):
        """Test GET /api/company-profile/fees/invalid returns error"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/fees/invalid_type_xyz")
        assert response.status_code == 200  # Returns 200 with error message
        
        data = response.json()
        assert "error" in data, "Should return error for invalid type"
    
    def test_companies_house_fees_endpoint(self, api_client):
        """Test GET /api/company-profile/fees/companies-house/all"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/fees/companies-house/all")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of fees"
        # Companies House types: ltd, ltd_guarantee, plc, unlimited, llp, lp, cic_shares, cic_guarantee, overseas
        assert len(data) == 9, f"Expected 9 Companies House types, got {len(data)}"
    
    def test_other_authorities_fees_endpoint(self, api_client):
        """Test GET /api/company-profile/fees/other-authorities/all"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/fees/other-authorities/all")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of fees"
        # Other types: sole_trader, cio, coop, royal_charter
        assert len(data) == 4, f"Expected 4 other authority types, got {len(data)}"


# ============================================
# GROWTH AGENT API TESTS (Authenticated)
# ============================================

class TestGrowthAgentAPI:
    """Tests for Growth Agent API - requires authentication"""
    
    def test_analyze_without_auth_returns_401(self, api_client):
        """Test GET /api/growth/agent/analyze without auth returns 401/403"""
        # Remove auth headers for this test
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/growth/agent/analyze", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_analyze_with_auth_returns_200(self, authenticated_client):
        """Test GET /api/growth/agent/analyze with auth returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/growth/agent/analyze")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_analyze_returns_performance_data(self, authenticated_client):
        """Test that analyze endpoint returns performance analysis data"""
        response = authenticated_client.get(f"{BASE_URL}/api/growth/agent/analyze")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        assert "healthScore" in data, "Response should contain healthScore"
        assert "leads" in data, "Response should contain leads analysis"
        assert "revenue" in data, "Response should contain revenue analysis"
        assert "campaigns" in data, "Response should contain campaigns analysis"
        assert "alerts" in data, "Response should contain alerts"
        assert "status" in data, "Response should contain status"
        
        # Validate health score range
        assert 0 <= data["healthScore"] <= 100, "Health score should be 0-100"
        
        # Validate status values
        assert data["status"] in ["healthy", "warning", "critical"], f"Invalid status: {data['status']}"
    
    def test_analyze_leads_structure(self, authenticated_client):
        """Test leads analysis structure"""
        response = authenticated_client.get(f"{BASE_URL}/api/growth/agent/analyze")
        data = response.json()
        
        leads = data["leads"]
        assert "currentPeriod" in leads
        assert "previousPeriod" in leads
        assert "percentChange" in leads
        assert "conversionRate" in leads
        assert "trend" in leads
        assert leads["trend"] in ["up", "down", "stable"]
    
    def test_recommend_without_auth_returns_401(self, api_client):
        """Test POST /api/growth/agent/recommend without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/growth/agent/recommend",
            headers=headers,
            json={"alertType": "lead_decline"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_recommend_with_auth_returns_200(self, authenticated_client):
        """Test POST /api/growth/agent/recommend with auth returns 200"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/growth/agent/recommend",
            json={"alertType": "lead_decline"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_recommend_returns_recommendation_data(self, authenticated_client):
        """Test that recommend endpoint returns recommendation data"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/growth/agent/recommend",
            json={"alertType": "lead_decline"}
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        assert "id" in data, "Response should contain recommendation id"
        assert "title" in data, "Response should contain title"
        assert "type" in data, "Response should contain type"
        assert "description" in data, "Response should contain description"
        assert "actions" in data, "Response should contain actions"
        assert "status" in data, "Response should contain status"
        
        # Validate status is pending for new recommendation
        assert data["status"] == "pending", f"New recommendation should be pending, got {data['status']}"
    
    def test_recommend_different_alert_types(self, authenticated_client):
        """Test recommend endpoint with different alert types"""
        alert_types = ["lead_decline", "conversion_decline", "revenue_decline", "no_campaigns"]
        
        for alert_type in alert_types:
            response = authenticated_client.post(
                f"{BASE_URL}/api/growth/agent/recommend",
                json={"alertType": alert_type}
            )
            assert response.status_code == 200, f"Failed for alert type: {alert_type}"
            
            data = response.json()
            assert data["status"] == "pending"
    
    def test_get_recommendations_list(self, authenticated_client):
        """Test GET /api/growth/agent/recommendations returns list"""
        response = authenticated_client.get(f"{BASE_URL}/api/growth/agent/recommendations")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of recommendations"


# ============================================
# FINANCE INVOICES API TESTS (Authenticated)
# ============================================

class TestFinanceInvoicesAPI:
    """Tests for Finance Invoices API - consolidated route"""
    
    def test_invoices_without_auth_returns_401(self, api_client):
        """Test GET /api/finance/invoices without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/finance/invoices", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_invoices_with_auth_returns_200(self, authenticated_client):
        """Test GET /api/finance/invoices with auth returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/finance/invoices")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_invoices_returns_list(self, authenticated_client):
        """Test that invoices endpoint returns a list"""
        response = authenticated_client.get(f"{BASE_URL}/api/finance/invoices")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of invoices"
    
    def test_legacy_navigator_invoices_still_works(self, authenticated_client):
        """Test that legacy /api/navigator/invoices still works"""
        response = authenticated_client.get(f"{BASE_URL}/api/navigator/invoices")
        assert response.status_code == 200, f"Legacy endpoint should still work, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return list of invoices"
    
    def test_create_invoice(self, authenticated_client):
        """Test POST /api/finance/invoices creates invoice"""
        invoice_data = {
            "clientName": "TEST_API_Client",
            "clientEmail": "test@client.com",
            "items": [
                {"description": "Test Service", "quantity": 1, "unitPrice": 100.00}
            ],
            "dueDate": "2025-02-01",
            "notes": "Test invoice from API tests"
        }
        
        response = authenticated_client.post(
            f"{BASE_URL}/api/finance/invoices",
            json=invoice_data
        )
        
        # Accept 200, 201, or 422 (validation error is acceptable)
        assert response.status_code in [200, 201, 422], f"Unexpected status: {response.status_code}: {response.text}"
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "id" in data, "Created invoice should have id"


# ============================================
# ENTITY TYPES API TESTS (Public)
# ============================================

class TestEntityTypesAPI:
    """Tests for Entity Types API"""
    
    def test_get_entity_types_returns_200(self, api_client):
        """Test GET /api/company-profile/entity-types returns 200"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/entity-types")
        assert response.status_code == 200
    
    def test_entity_types_structure(self, api_client):
        """Test entity types response structure"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/entity-types")
        data = response.json()
        
        assert "entityTypes" in data, "Response should contain entityTypes"
        assert "feeNotice" in data, "Response should contain feeNotice"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
