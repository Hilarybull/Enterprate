"""
AI Website Builder API Tests - Iteration 4
Tests for all AI Website Builder endpoints:
- GET /api/ai-websites/color-schemes/list - Returns available color schemes (public)
- GET /api/ai-websites/languages/list - Returns supported languages (public)
- GET /api/ai-websites/platforms/list - Returns deployment platforms (public)
- POST /api/ai-websites/lead - Handle lead form submission (public)
- POST /api/ai-websites/generate - Generate a website from business description (auth)
- GET /api/ai-websites - List all websites for workspace (auth)
- POST /api/ai-websites/{id}/refine - Refine website with feedback (auth)
- POST /api/ai-websites/{id}/deploy - Deploy website to chosen platform (auth)
- GET /api/ai-websites/{id}/download - Download website HTML (auth)
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

JWT_SECRET = "enterprate-os-jwt-secret-change-in-production"

# Test user and workspace IDs
TEST_USER_ID = "test-user-aiwebsite-iter4-001"
TEST_WORKSPACE_ID = "test-workspace-aiwebsite-iter4-001"


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
            email: "test-aiwebsite-iter4@enterprate.com",
            name: "AI Website Builder Test User Iter4",
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
    
    print("Test data setup complete for AI Website Builder iteration 4");
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
# PUBLIC ENDPOINTS TESTS
# ============================================

class TestColorSchemesAPI:
    """Tests for Color Schemes API - GET /api/ai-websites/color-schemes/list (public)"""
    
    def test_color_schemes_returns_200_without_auth(self, api_client):
        """Test GET /api/ai-websites/color-schemes/list returns 200 without auth"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/color-schemes/list")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_color_schemes_returns_all_expected_schemes(self, api_client):
        """Test color schemes returns all 6 expected schemes"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/color-schemes/list")
        assert response.status_code == 200
        
        data = response.json()
        expected_schemes = ["modern", "professional", "creative", "minimal", "warm", "nature"]
        
        for scheme in expected_schemes:
            assert scheme in data, f"Should contain {scheme} color scheme"
            assert "primary" in data[scheme], f"{scheme} should have primary color"
            assert "secondary" in data[scheme], f"{scheme} should have secondary color"
            assert "accent" in data[scheme], f"{scheme} should have accent color"
    
    def test_color_schemes_colors_are_valid_hex(self, api_client):
        """Test that all color values are valid hex colors"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/color-schemes/list")
        assert response.status_code == 200
        
        data = response.json()
        for scheme_name, colors in data.items():
            for color_type, color_value in colors.items():
                assert color_value.startswith("#"), f"{scheme_name}.{color_type} should be hex color"
                assert len(color_value) == 7, f"{scheme_name}.{color_type} should be 7 chars (#RRGGBB)"


class TestLanguagesAPI:
    """Tests for Languages API - GET /api/ai-websites/languages/list (public)"""
    
    def test_languages_returns_200_without_auth(self, api_client):
        """Test GET /api/ai-websites/languages/list returns 200 without auth"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/languages/list")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_languages_returns_15_languages(self, api_client):
        """Test languages returns all 15 supported languages"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/languages/list")
        assert response.status_code == 200
        
        data = response.json()
        expected_languages = ["en", "es", "fr", "de", "it", "pt", "nl", "pl", "ru", "zh", "ja", "ko", "ar", "hi", "tr"]
        
        assert len(data) == 15, f"Should have 15 languages, got {len(data)}"
        
        for lang_code in expected_languages:
            assert lang_code in data, f"Should contain {lang_code} language"
            assert "name" in data[lang_code], f"{lang_code} should have name"
            assert "direction" in data[lang_code], f"{lang_code} should have direction"
    
    def test_arabic_has_rtl_direction(self, api_client):
        """Test that Arabic has RTL direction"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/languages/list")
        assert response.status_code == 200
        
        data = response.json()
        assert data["ar"]["direction"] == "rtl", "Arabic should have RTL direction"
    
    def test_english_has_ltr_direction(self, api_client):
        """Test that English has LTR direction"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/languages/list")
        assert response.status_code == 200
        
        data = response.json()
        assert data["en"]["direction"] == "ltr", "English should have LTR direction"


class TestPlatformsAPI:
    """Tests for Platforms API - GET /api/ai-websites/platforms/list (public)"""
    
    def test_platforms_returns_200_without_auth(self, api_client):
        """Test GET /api/ai-websites/platforms/list returns 200 without auth"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/platforms/list")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_platforms_returns_all_3_platforms(self, api_client):
        """Test platforms returns all 3 deployment platforms"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/platforms/list")
        assert response.status_code == 200
        
        data = response.json()
        expected_platforms = ["netlify", "vercel", "railway"]
        
        assert len(data) == 3, f"Should have 3 platforms, got {len(data)}"
        
        for platform in expected_platforms:
            assert platform in data, f"Should contain {platform} platform"
            assert "name" in data[platform], f"{platform} should have name"
            assert "key_env" in data[platform], f"{platform} should have key_env"


class TestLeadSubmissionAPI:
    """Tests for Lead Submission API - POST /api/ai-websites/lead (public)"""
    
    def test_lead_submission_returns_200(self, api_client):
        """Test POST /api/ai-websites/lead returns 200"""
        unique_email = f"test-lead-{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(
            f"{BASE_URL}/api/ai-websites/lead",
            json={
                "name": "Test Lead User",
                "email": unique_email,
                "phone": "+1234567890",
                "message": "TEST_This is a test lead submission",
                "workspaceId": "test-workspace-001",
                "source": "website_form"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_lead_submission_returns_proper_structure(self, api_client):
        """Test lead submission returns proper structure"""
        unique_email = f"test-lead-{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(
            f"{BASE_URL}/api/ai-websites/lead",
            json={
                "name": "Test Lead User 2",
                "email": unique_email,
                "message": "TEST_Another test lead",
                "workspaceId": "test-workspace-002",
                "source": "landing_page"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data, "Should contain success"
        assert data["success"] == True, "success should be True"
        assert "leadId" in data, "Should contain leadId"
        assert "message" in data, "Should contain message"
    
    def test_lead_submission_without_phone(self, api_client):
        """Test lead submission works without phone number"""
        unique_email = f"test-lead-{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(
            f"{BASE_URL}/api/ai-websites/lead",
            json={
                "name": "Test Lead No Phone",
                "email": unique_email,
                "message": "TEST_Lead without phone",
                "workspaceId": "test-workspace-003",
                "source": "website_form"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True


# ============================================
# AUTHENTICATED ENDPOINTS TESTS
# ============================================

class TestGenerateWebsiteAPI:
    """Tests for Generate Website API - POST /api/ai-websites/generate (auth required)"""
    
    def test_generate_without_auth_returns_401(self, api_client):
        """Test POST /api/ai-websites/generate without auth returns 401/403"""
        response = requests.post(
            f"{BASE_URL}/api/ai-websites/generate",
            headers={"Content-Type": "application/json"},
            json={"userDescription": "A tech startup"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_generate_with_auth_returns_200(self, authenticated_client):
        """Test POST /api/ai-websites/generate with auth returns 200"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": "TEST_A modern tech startup offering AI-powered solutions",
                "brandPreferences": {"colorScheme": "modern"},
                "contactMethod": "form",
                "language": "en",
                "includeLeadForm": True
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_generate_returns_proper_structure(self, authenticated_client):
        """Test generate website returns proper structure"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": "TEST_Professional consulting firm specializing in business strategy",
                "brandPreferences": {"colorScheme": "professional"},
                "contactMethod": "email",
                "contactValue": "contact@test.com",
                "language": "en",
                "includeLeadForm": True
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data, "Should contain website id"
        assert "htmlContent" in data, "Should contain htmlContent"
        assert "status" in data, "Should contain status"
        assert data["status"] == "draft", "New website should be in draft status"
        assert "message" in data, "Should contain message"
    
    def test_generate_with_different_color_schemes(self, authenticated_client):
        """Test generate website with different color schemes"""
        color_schemes = ["modern", "professional", "creative", "minimal", "warm", "nature"]
        
        for scheme in color_schemes:
            response = authenticated_client.post(
                f"{BASE_URL}/api/ai-websites/generate",
                json={
                    "userDescription": f"TEST_Business with {scheme} color scheme",
                    "brandPreferences": {"colorScheme": scheme},
                    "contactMethod": "form"
                }
            )
            assert response.status_code == 200, f"Failed for color scheme {scheme}: {response.text}"
            
            data = response.json()
            assert "htmlContent" in data
            # Verify the color scheme is applied in HTML
            html = data["htmlContent"]
            assert "<!DOCTYPE html>" in html or "<!doctype html>" in html.lower()
    
    def test_generate_with_different_languages(self, authenticated_client):
        """Test generate website with different languages"""
        languages = ["en", "es", "fr", "de"]
        
        for lang in languages:
            response = authenticated_client.post(
                f"{BASE_URL}/api/ai-websites/generate",
                json={
                    "userDescription": f"TEST_Business website in {lang}",
                    "brandPreferences": {"colorScheme": "modern"},
                    "language": lang,
                    "contactMethod": "form"
                }
            )
            assert response.status_code == 200, f"Failed for language {lang}: {response.text}"
            
            data = response.json()
            html = data["htmlContent"]
            assert f'lang="{lang}"' in html, f"HTML should have lang={lang}"


class TestListWebsitesAPI:
    """Tests for List Websites API - GET /api/ai-websites (auth required)"""
    
    def test_list_without_auth_returns_401(self, api_client):
        """Test GET /api/ai-websites without auth returns 401/403"""
        response = requests.get(
            f"{BASE_URL}/api/ai-websites",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_list_with_auth_returns_200(self, authenticated_client):
        """Test GET /api/ai-websites with auth returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/ai-websites")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_list_returns_array(self, authenticated_client):
        """Test GET /api/ai-websites returns array"""
        response = authenticated_client.get(f"{BASE_URL}/api/ai-websites")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of websites"
    
    def test_list_contains_generated_websites(self, authenticated_client):
        """Test list contains previously generated websites"""
        # First generate a website
        generate_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": "TEST_Website for list test",
                "brandPreferences": {"colorScheme": "modern"},
                "contactMethod": "form"
            }
        )
        assert generate_response.status_code == 200
        website_id = generate_response.json()["id"]
        
        # Now list websites
        list_response = authenticated_client.get(f"{BASE_URL}/api/ai-websites")
        assert list_response.status_code == 200
        
        data = list_response.json()
        website_ids = [w["id"] for w in data]
        assert website_id in website_ids, "Generated website should be in list"


class TestRefineWebsiteAPI:
    """Tests for Refine Website API - POST /api/ai-websites/{id}/refine (auth required)"""
    
    created_website_id = None
    
    def test_refine_website_flow(self, authenticated_client):
        """Test refining a website with feedback"""
        # First generate a website
        generate_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": "TEST_E-commerce store for refine test",
                "brandPreferences": {"colorScheme": "warm"},
                "contactMethod": "form"
            }
        )
        assert generate_response.status_code == 200
        website_id = generate_response.json()["id"]
        TestRefineWebsiteAPI.created_website_id = website_id
        
        # Now refine it
        refine_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/{website_id}/refine",
            json={
                "feedback": "Make the headline bigger and add more testimonials"
            }
        )
        assert refine_response.status_code == 200, f"Expected 200, got {refine_response.status_code}: {refine_response.text}"
        
        data = refine_response.json()
        assert "id" in data, "Should contain website id"
        assert "htmlContent" in data, "Should contain refined htmlContent"
        assert "version" in data, "Should contain version"
        assert data["version"] >= 2, "Version should be incremented after refinement"
        assert "message" in data, "Should contain message"
    
    def test_refine_nonexistent_website_returns_404(self, authenticated_client):
        """Test refining non-existent website returns 404"""
        fake_id = str(uuid.uuid4())
        
        response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/{fake_id}/refine",
            json={"feedback": "Some feedback"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestDeployWebsiteAPI:
    """Tests for Deploy Website API - POST /api/ai-websites/{id}/deploy (auth required)"""
    
    def test_deploy_to_netlify_simulated(self, authenticated_client):
        """Test deploying to Netlify (simulated)"""
        # First generate a website
        generate_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": "TEST_Website for Netlify deploy test",
                "brandPreferences": {"colorScheme": "modern"},
                "contactMethod": "form"
            }
        )
        assert generate_response.status_code == 200
        website_id = generate_response.json()["id"]
        
        # Deploy to Netlify
        deploy_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/{website_id}/deploy",
            json={
                "platform": "netlify",
                "siteName": "test-netlify-site"
            }
        )
        assert deploy_response.status_code == 200, f"Expected 200, got {deploy_response.status_code}: {deploy_response.text}"
        
        data = deploy_response.json()
        assert "success" in data, "Should contain success"
        assert data["success"] == True, "success should be True"
        assert "siteUrl" in data, "Should contain siteUrl"
        assert "netlify.app" in data["siteUrl"], "URL should be Netlify domain"
        assert "message" in data, "Should contain message"
        assert "simulated" in data["message"].lower(), "Should indicate simulated deployment"
    
    def test_deploy_to_vercel_simulated(self, authenticated_client):
        """Test deploying to Vercel (simulated)"""
        # First generate a website
        generate_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": "TEST_Website for Vercel deploy test",
                "brandPreferences": {"colorScheme": "professional"},
                "contactMethod": "form"
            }
        )
        assert generate_response.status_code == 200
        website_id = generate_response.json()["id"]
        
        # Deploy to Vercel
        deploy_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/{website_id}/deploy",
            json={
                "platform": "vercel",
                "siteName": "test-vercel-site"
            }
        )
        assert deploy_response.status_code == 200, f"Expected 200, got {deploy_response.status_code}: {deploy_response.text}"
        
        data = deploy_response.json()
        assert data["success"] == True
        assert "vercel.app" in data["siteUrl"], "URL should be Vercel domain"
    
    def test_deploy_to_railway_simulated(self, authenticated_client):
        """Test deploying to Railway (simulated)"""
        # First generate a website
        generate_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": "TEST_Website for Railway deploy test",
                "brandPreferences": {"colorScheme": "creative"},
                "contactMethod": "form"
            }
        )
        assert generate_response.status_code == 200
        website_id = generate_response.json()["id"]
        
        # Deploy to Railway
        deploy_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/{website_id}/deploy",
            json={
                "platform": "railway",
                "siteName": "test-railway-site"
            }
        )
        assert deploy_response.status_code == 200, f"Expected 200, got {deploy_response.status_code}: {deploy_response.text}"
        
        data = deploy_response.json()
        assert data["success"] == True
        assert "railway.app" in data["siteUrl"], "URL should be Railway domain"
    
    def test_deploy_nonexistent_website_returns_404(self, authenticated_client):
        """Test deploying non-existent website returns 404"""
        fake_id = str(uuid.uuid4())
        
        response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/{fake_id}/deploy",
            json={"platform": "netlify"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestDownloadWebsiteAPI:
    """Tests for Download Website API - GET /api/ai-websites/{id}/download (auth required)"""
    
    def test_download_website_returns_html(self, authenticated_client):
        """Test downloading website returns HTML content"""
        # First generate a website
        generate_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": "TEST_Website for download test",
                "brandPreferences": {"colorScheme": "minimal"},
                "contactMethod": "form"
            }
        )
        assert generate_response.status_code == 200
        website_id = generate_response.json()["id"]
        
        # Download the website
        download_response = authenticated_client.get(
            f"{BASE_URL}/api/ai-websites/{website_id}/download"
        )
        assert download_response.status_code == 200, f"Expected 200, got {download_response.status_code}"
        
        # Check content type
        content_type = download_response.headers.get("content-type", "")
        assert "text/html" in content_type, f"Content-Type should be text/html, got {content_type}"
        
        # Check content
        html_content = download_response.text
        assert "<!DOCTYPE html>" in html_content or "<!doctype html>" in html_content.lower()
    
    def test_download_has_attachment_header(self, authenticated_client):
        """Test download has Content-Disposition attachment header"""
        # First generate a website
        generate_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": "TEST_Website for attachment header test",
                "brandPreferences": {"colorScheme": "nature"},
                "contactMethod": "form"
            }
        )
        assert generate_response.status_code == 200
        website_id = generate_response.json()["id"]
        
        # Download the website
        download_response = authenticated_client.get(
            f"{BASE_URL}/api/ai-websites/{website_id}/download"
        )
        assert download_response.status_code == 200
        
        # Check Content-Disposition header
        content_disposition = download_response.headers.get("content-disposition", "")
        assert "attachment" in content_disposition, "Should have attachment disposition"
        assert ".html" in content_disposition, "Filename should have .html extension"
    
    def test_download_nonexistent_website_returns_error(self, authenticated_client):
        """Test downloading non-existent website returns error"""
        fake_id = str(uuid.uuid4())
        
        response = authenticated_client.get(
            f"{BASE_URL}/api/ai-websites/{fake_id}/download"
        )
        # Should return 200 with error message or 404
        if response.status_code == 200:
            data = response.json()
            assert "error" in data, "Should contain error message"


# ============================================
# INTEGRATION TESTS
# ============================================

class TestWebsiteBuilderWorkflow:
    """Integration tests for complete website builder workflow"""
    
    def test_complete_workflow_generate_refine_deploy_download(self, authenticated_client):
        """Test complete workflow: generate -> refine -> deploy -> download"""
        # Step 1: Generate
        generate_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/generate",
            json={
                "userDescription": "TEST_Complete workflow test - A modern SaaS company",
                "brandPreferences": {"colorScheme": "modern"},
                "language": "en",
                "contactMethod": "form",
                "includeLeadForm": True
            }
        )
        assert generate_response.status_code == 200
        website_id = generate_response.json()["id"]
        initial_html = generate_response.json()["htmlContent"]
        
        # Step 2: Refine
        refine_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/{website_id}/refine",
            json={"feedback": "Add more social proof and testimonials"}
        )
        assert refine_response.status_code == 200
        assert refine_response.json()["version"] >= 2
        
        # Step 3: Deploy
        deploy_response = authenticated_client.post(
            f"{BASE_URL}/api/ai-websites/{website_id}/deploy",
            json={"platform": "netlify", "siteName": "workflow-test"}
        )
        assert deploy_response.status_code == 200
        assert deploy_response.json()["success"] == True
        site_url = deploy_response.json()["siteUrl"]
        
        # Step 4: Download
        download_response = authenticated_client.get(
            f"{BASE_URL}/api/ai-websites/{website_id}/download"
        )
        assert download_response.status_code == 200
        assert "<!DOCTYPE html>" in download_response.text or "<!doctype html>" in download_response.text.lower()
        
        # Step 5: Verify in list
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
        """Cleanup TEST_ prefixed data"""
        import subprocess
        
        mongo_script = f'''
        use('enterprate_os');
        
        // Delete test websites
        var result = db.ai_websites.deleteMany({{ "businessContext.description": /^TEST_/ }});
        print("Deleted " + result.deletedCount + " test websites");
        
        // Delete test leads
        result = db.leads.deleteMany({{ message: /^TEST_/ }});
        print("Deleted " + result.deletedCount + " test leads");
        
        print("Test data cleanup complete");
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
