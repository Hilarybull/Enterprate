"""
AI Website Builder API Tests - Iteration 5
Tests for Quick Templates feature and Netlify deployment fix:
- GET /api/ai-websites/templates/list - Returns 10 industry templates (NEW)
- GET /api/ai-websites/templates/{id} - Returns specific template details (NEW)
- POST /api/ai-websites/generate - Generate website with template content
- POST /api/ai-websites/{id}/deploy with platform=netlify - Verify HTML content-type (FIXED)
- POST /api/company-profile/check-name - Companies House API verification
- Full workflow: Select template -> Generate -> Deploy to Netlify -> Verify site serves HTML
"""
import pytest
import requests
import os
import jwt
import uuid
from datetime import datetime, timezone, timedelta

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable not set")

JWT_SECRET = os.environ.get('JWT_SECRET', 'f9d7515d1f8e155bf5772a64dd65603788fc40e2091e594e18f6261154078c66')

# Test user and workspace IDs
TEST_USER_ID = "test-user-iter5-001"
TEST_WORKSPACE_ID = "test-workspace-iter5-001"

# Expected templates
EXPECTED_TEMPLATES = [
    "saas", "restaurant", "portfolio", "salon", "beauty",
    "online_store", "consulting", "fitness", "real_estate", "healthcare"
]


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
    
    mongo_script = f'''
    use('enterprate_os');
    
    // Create test user if not exists
    db.users.updateOne(
        {{ id: "{TEST_USER_ID}" }},
        {{ $set: {{
            id: "{TEST_USER_ID}",
            email: "test-iter5@enterprate.com",
            name: "AI Website Builder Test User Iter5",
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
    
    print("Test data setup complete for iteration 5");
    '''
    
    result = subprocess.run(
        ["mongosh", "--quiet", "--eval", mongo_script],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"MongoDB setup warning: {result.stderr}")
    
    yield


# ============================================
# QUICK TEMPLATES TESTS (NEW FEATURE)
# ============================================

class TestTemplatesListAPI:
    """Tests for Templates List API - GET /api/ai-websites/templates/list (public)"""
    
    def test_templates_list_returns_200_without_auth(self, api_client):
        """Test GET /api/ai-websites/templates/list returns 200 without auth"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/list")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_templates_list_returns_10_templates(self, api_client):
        """Test templates list returns all 10 industry templates"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/list")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 10, f"Should have 10 templates, got {len(data)}"
        
        for template_id in EXPECTED_TEMPLATES:
            assert template_id in data, f"Should contain {template_id} template"
    
    def test_templates_have_required_fields(self, api_client):
        """Test each template has all required fields"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/list")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["name", "icon", "description", "defaultColorScheme", "heroImage", "prompt", "features", "cta"]
        
        for template_id, template in data.items():
            for field in required_fields:
                assert field in template, f"Template {template_id} should have {field}"
    
    def test_saas_template_content(self, api_client):
        """Test SaaS template has correct content"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/list")
        assert response.status_code == 200
        
        data = response.json()
        saas = data.get("saas", {})
        
        assert saas["name"] == "SaaS / Tech Startup"
        assert saas["icon"] == "code"
        assert saas["defaultColorScheme"] == "modern"
        assert "SaaS platform" in saas["prompt"]
        assert len(saas["features"]) >= 4
        assert saas["cta"] == "Start Free Trial"
    
    def test_restaurant_template_content(self, api_client):
        """Test Restaurant template has correct content"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/list")
        assert response.status_code == 200
        
        data = response.json()
        restaurant = data.get("restaurant", {})
        
        assert restaurant["name"] == "Restaurant / Cafe"
        assert restaurant["icon"] == "utensils"
        assert restaurant["defaultColorScheme"] == "warm"
        assert "restaurant" in restaurant["prompt"].lower()
        assert restaurant["cta"] == "Reserve a Table"


class TestTemplateByIdAPI:
    """Tests for Template by ID API - GET /api/ai-websites/templates/{id} (public)"""
    
    def test_get_saas_template_returns_200(self, api_client):
        """Test GET /api/ai-websites/templates/saas returns 200"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/saas")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_get_template_includes_id(self, api_client):
        """Test template response includes id field"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/saas")
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data, "Response should include id field"
        assert data["id"] == "saas"
    
    def test_get_all_templates_by_id(self, api_client):
        """Test getting each template by ID"""
        for template_id in EXPECTED_TEMPLATES:
            response = requests.get(f"{BASE_URL}/api/ai-websites/templates/{template_id}")
            assert response.status_code == 200, f"Failed for template {template_id}: {response.text}"
            
            data = response.json()
            assert data["id"] == template_id
            assert "name" in data
            assert "prompt" in data
    
    def test_get_invalid_template_returns_error(self, api_client):
        """Test GET /api/ai-websites/templates/invalid returns error"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/invalid_template")
        assert response.status_code == 200  # Returns 200 with error message
        
        data = response.json()
        assert "error" in data, "Should return error for invalid template"
        assert data["error"] == "Template not found"


# ============================================
# NETLIFY DEPLOYMENT FIX TESTS
# ============================================

class TestNetlifyDeploymentFix:
    """Tests for Netlify deployment fix - HTML content-type"""
    
    generated_website_id = None
    deployed_site_url = None
    
    def test_generate_website_for_deployment(self, authenticated_client):
        """Generate a website for deployment testing"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": "TEST_ITER5_NETLIFY_A modern tech startup for deployment testing",
                "brandPreferences": {"colorScheme": "modern"},
                "contactMethod": "form",
                "language": "en",
                "includeLeadForm": True
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        TestNetlifyDeploymentFix.generated_website_id = data["id"]
        assert "htmlContent" in data
        assert "<!DOCTYPE html>" in data["htmlContent"] or "<!doctype html>" in data["htmlContent"].lower()
    
    def test_deploy_to_netlify_returns_success(self, authenticated_client):
        """Test deploying to Netlify returns success"""
        if not TestNetlifyDeploymentFix.generated_website_id:
            pytest.skip("No website generated")
        
        unique_name = f"test-iter5-{uuid.uuid4().hex[:8]}"
        
        response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/{TestNetlifyDeploymentFix.generated_website_id}/deploy",
            json={
                "platform": "netlify",
                "siteName": unique_name
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True, "Deployment should succeed"
        assert "siteUrl" in data, "Should return site URL"
        assert "netlify.app" in data["siteUrl"], "URL should be Netlify domain"
        assert "siteId" in data, "Should return site ID"
        assert "deployId" in data, "Should return deploy ID"
        
        TestNetlifyDeploymentFix.deployed_site_url = data["siteUrl"]
    
    def test_deployed_site_serves_html_content_type(self, api_client):
        """Test deployed site serves text/html content-type (FIX VERIFICATION)"""
        if not TestNetlifyDeploymentFix.deployed_site_url:
            pytest.skip("No site deployed")
        
        import time
        time.sleep(3)  # Wait for deployment to propagate
        
        response = requests.head(TestNetlifyDeploymentFix.deployed_site_url, timeout=30)
        
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type, f"Content-Type should be text/html, got {content_type}"
    
    def test_deployed_site_returns_valid_html(self, api_client):
        """Test deployed site returns valid HTML content"""
        if not TestNetlifyDeploymentFix.deployed_site_url:
            pytest.skip("No site deployed")
        
        response = requests.get(TestNetlifyDeploymentFix.deployed_site_url, timeout=30)
        assert response.status_code == 200, f"Site should return 200, got {response.status_code}"
        
        html_content = response.text
        assert "<!DOCTYPE html>" in html_content or "<!doctype html>" in html_content.lower(), "Should return HTML document"
        assert "<html" in html_content.lower(), "Should contain html tag"
        assert "</html>" in html_content.lower(), "Should contain closing html tag"


# ============================================
# COMPANIES HOUSE API TESTS
# ============================================

class TestCompaniesHouseAPI:
    """Tests for Companies House API - POST /api/company-profile/check-name"""
    
    def test_check_name_without_auth_returns_401(self, api_client):
        """Test POST /api/company-profile/check-name without auth returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/company-profile/check-name",
            headers={"Content-Type": "application/json"},
            json={"companyName": "Test Company"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_check_name_with_auth_returns_200(self, authenticated_client):
        """Test POST /api/company-profile/check-name with auth returns 200"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/company-profile/check-name",
            json={"companyName": "Apple Inc"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_check_name_returns_proper_structure(self, authenticated_client):
        """Test check-name returns proper response structure"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/company-profile/check-name",
            json={"companyName": "Microsoft Corporation"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "searchedName" in data, "Should contain searchedName"
        assert "isAvailable" in data, "Should contain isAvailable"
        assert "confidence" in data, "Should contain confidence"
        assert "checkedAt" in data, "Should contain checkedAt"
    
    def test_check_name_returns_matches(self, authenticated_client):
        """Test check-name returns exact and similar matches"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/company-profile/check-name",
            json={"companyName": "Google"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Should have either exactMatches or similarMatches
        has_matches = "exactMatches" in data or "similarMatches" in data
        assert has_matches, "Should return matches"
    
    def test_check_name_returns_suggestions(self, authenticated_client):
        """Test check-name returns name suggestions"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/company-profile/check-name",
            json={"companyName": "Tech Solutions"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "suggestions" in data, "Should contain suggestions"
        if data["suggestions"]:
            suggestion = data["suggestions"][0]
            assert "name" in suggestion, "Suggestion should have name"
            assert "reason" in suggestion, "Suggestion should have reason"


# ============================================
# TEMPLATE-BASED WEBSITE GENERATION TESTS
# ============================================

class TestTemplateBasedGeneration:
    """Tests for generating websites using template content"""
    
    def test_generate_with_saas_template_prompt(self, authenticated_client):
        """Test generating website using SaaS template prompt"""
        # Get template prompt
        template_response = requests.get(f"{BASE_URL}/api/ai-websites/templates/saas")
        template = template_response.json()
        
        # Generate website with template prompt
        response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": f"TEST_ITER5_TEMPLATE_{template['prompt']}",
                "brandPreferences": {"colorScheme": template["defaultColorScheme"]},
                "contactMethod": "form",
                "language": "en",
                "includeLeadForm": True
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert "htmlContent" in data
        assert data["status"] == "draft"
    
    def test_generate_with_restaurant_template_prompt(self, authenticated_client):
        """Test generating website using Restaurant template prompt"""
        template_response = requests.get(f"{BASE_URL}/api/ai-websites/templates/restaurant")
        template = template_response.json()
        
        response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": f"TEST_ITER5_TEMPLATE_{template['prompt']}",
                "brandPreferences": {"colorScheme": template["defaultColorScheme"]},
                "contactMethod": "form",
                "language": "en"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "htmlContent" in data
    
    def test_generate_with_healthcare_template_prompt(self, authenticated_client):
        """Test generating website using Healthcare template prompt"""
        template_response = requests.get(f"{BASE_URL}/api/ai-websites/templates/healthcare")
        template = template_response.json()
        
        response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": f"TEST_ITER5_TEMPLATE_{template['prompt']}",
                "brandPreferences": {"colorScheme": template["defaultColorScheme"]},
                "contactMethod": "form"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "htmlContent" in data


# ============================================
# FULL WORKFLOW TEST
# ============================================

class TestFullWorkflow:
    """Integration test for complete workflow: Template -> Generate -> Deploy -> Verify"""
    
    def test_complete_template_to_deployment_workflow(self, authenticated_client):
        """Test complete workflow: Select template -> Generate -> Deploy to Netlify -> Verify HTML"""
        import time
        
        # Step 1: Get template
        template_response = requests.get(f"{BASE_URL}/api/ai-websites/templates/consulting")
        assert template_response.status_code == 200
        template = template_response.json()
        
        # Step 2: Generate website using template
        generate_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": f"TEST_ITER5_WORKFLOW_{template['prompt']}",
                "brandPreferences": {"colorScheme": template["defaultColorScheme"]},
                "contactMethod": "form",
                "language": "en",
                "includeLeadForm": True
            }
        )
        assert generate_response.status_code == 200
        website_id = generate_response.json()["id"]
        
        # Step 3: Deploy to Netlify
        unique_name = f"workflow-test-{uuid.uuid4().hex[:8]}"
        deploy_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/{website_id}/deploy",
            json={
                "platform": "netlify",
                "siteName": unique_name
            }
        )
        assert deploy_response.status_code == 200
        deploy_data = deploy_response.json()
        assert deploy_data["success"] == True
        site_url = deploy_data["siteUrl"]
        
        # Step 4: Wait for deployment and verify HTML content-type
        time.sleep(3)
        
        head_response = requests.head(site_url, timeout=30)
        content_type = head_response.headers.get("content-type", "")
        assert "text/html" in content_type, f"Site should serve text/html, got {content_type}"
        
        # Step 5: Verify HTML content
        get_response = requests.get(site_url, timeout=30)
        assert get_response.status_code == 200
        assert "<!DOCTYPE html>" in get_response.text or "<!doctype html>" in get_response.text.lower()
        
        # Step 6: Verify website in list
        list_response = authenticated_client.get(f"{BASE_URL}/api/ai-websites")
        assert list_response.status_code == 200
        websites = list_response.json()
        website = next((w for w in websites if w["id"] == website_id), None)
        assert website is not None, "Website should be in list"
        assert website["status"] == "deployed", "Status should be deployed"


# ============================================
# CLEANUP TEST DATA
# ============================================

class TestCleanup:
    """Cleanup test data after all tests"""
    
    def test_cleanup_test_data(self, authenticated_client):
        """Cleanup TEST_ITER5_ prefixed data"""
        import subprocess
        
        mongo_script = f'''
        use('enterprate_os');
        
        // Delete test websites from iteration 5
        var result = db.ai_websites.deleteMany({{ "businessContext.description": /^TEST_ITER5_/ }});
        print("Deleted " + result.deletedCount + " test websites");
        
        print("Test data cleanup complete for iteration 5");
        '''
        
        result = subprocess.run(
            ["mongosh", "--quiet", "--eval", mongo_script],
            capture_output=True,
            text=True
        )
        
        # This test always passes - cleanup is best effort
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
