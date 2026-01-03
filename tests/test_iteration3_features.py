"""
EnterprateAI New Features Tests - Iteration 3
Tests for:
- Notifications API (real-time notifications for scheduled actions)
- A/B Testing API (create, start, analyze tests)
- Team Collaboration API (members, invites, activity, comments)
- AI Website Builder API (generate, refine, deploy)
- TikTok & YouTube scheduling (optimal times)
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
TEST_USER_ID = "test-user-iter3-001"
TEST_WORKSPACE_ID = "test-workspace-iter3-001"


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
            email: "test-iter3@enterprate.com",
            name: "Iteration 3 Test User",
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
    
    print("Test data setup complete for iteration 3");
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
# NOTIFICATIONS API TESTS
# ============================================

class TestNotificationsAPI:
    """Tests for Notifications API - GET /api/notifications"""
    
    def test_notifications_without_auth_returns_401(self, api_client):
        """Test GET /api/notifications without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_notifications_with_auth_returns_200(self, authenticated_client):
        """Test GET /api/notifications with auth returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_notifications_returns_list(self, authenticated_client):
        """Test GET /api/notifications returns list"""
        response = authenticated_client.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of notifications"
    
    def test_notifications_unread_only_filter(self, authenticated_client):
        """Test GET /api/notifications?unread_only=true"""
        response = authenticated_client.get(f"{BASE_URL}/api/notifications?unread_only=true")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list"
        # All returned notifications should be unread
        for notification in data:
            assert notification.get("read") == False, "All notifications should be unread"


class TestNotificationsUnreadCountAPI:
    """Tests for Notifications Unread Count API - GET /api/notifications/unread-count"""
    
    def test_unread_count_without_auth_returns_401(self, api_client):
        """Test GET /api/notifications/unread-count without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/notifications/unread-count", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_unread_count_with_auth_returns_200(self, authenticated_client):
        """Test GET /api/notifications/unread-count with auth returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_unread_count_returns_count(self, authenticated_client):
        """Test unread count returns proper structure"""
        response = authenticated_client.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 200
        
        data = response.json()
        assert "unreadCount" in data, "Should contain unreadCount"
        assert isinstance(data["unreadCount"], int), "unreadCount should be integer"


# ============================================
# A/B TESTING API TESTS
# ============================================

class TestABTestingCreateAPI:
    """Tests for A/B Testing Create API - POST /api/ab-tests"""
    
    def test_create_ab_test_without_auth_returns_401(self, api_client):
        """Test POST /api/ab-tests without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/ab-tests",
            headers=headers,
            json={
                "name": "Test AB",
                "description": "Test description",
                "testType": "campaign",
                "variants": [{"name": "A"}, {"name": "B"}]
            }
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_create_ab_test_with_auth_returns_200(self, authenticated_client):
        """Test POST /api/ab-tests with auth returns 200"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/ab-tests",
            json={
                "name": "TEST_Campaign AB Test",
                "description": "Testing campaign variants",
                "testType": "campaign",
                "variants": [
                    {"name": "Control", "content": {"headline": "Original"}},
                    {"name": "Variant B", "content": {"headline": "New Version"}}
                ],
                "goalMetric": "conversion_rate",
                "durationDays": 14
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_create_ab_test_returns_proper_structure(self, authenticated_client):
        """Test create A/B test returns proper structure"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/ab-tests",
            json={
                "name": "TEST_Landing Page Test",
                "description": "Testing landing page variants",
                "testType": "landing_page",
                "variants": [
                    {"name": "Control", "content": {"cta": "Sign Up"}},
                    {"name": "Variant B", "content": {"cta": "Get Started"}}
                ],
                "goalMetric": "click_rate"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data, "Should contain id"
        assert "name" in data, "Should contain name"
        assert "status" in data, "Should contain status"
        assert data["status"] == "draft", "New test should be in draft status"
        assert "variants" in data, "Should contain variants"
        assert len(data["variants"]) == 2, "Should have 2 variants"


class TestABTestingListAPI:
    """Tests for A/B Testing List API - GET /api/ab-tests"""
    
    def test_list_ab_tests_without_auth_returns_401(self, api_client):
        """Test GET /api/ab-tests without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/ab-tests", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_list_ab_tests_with_auth_returns_200(self, authenticated_client):
        """Test GET /api/ab-tests with auth returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/ab-tests")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_list_ab_tests_returns_list(self, authenticated_client):
        """Test GET /api/ab-tests returns list"""
        response = authenticated_client.get(f"{BASE_URL}/api/ab-tests")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of A/B tests"


class TestABTestingStartAPI:
    """Tests for A/B Testing Start API - POST /api/ab-tests/{id}/start"""
    
    created_test_id = None
    
    def test_start_ab_test_flow(self, authenticated_client):
        """Test starting an A/B test"""
        # First create a test
        create_response = authenticated_client.post(
            f"{BASE_URL}/api/ab-tests",
            json={
                "name": "TEST_Start Test",
                "description": "Test to start",
                "testType": "email",
                "variants": [
                    {"name": "Control", "content": {"subject": "Original"}},
                    {"name": "Variant B", "content": {"subject": "New Subject"}}
                ]
            }
        )
        assert create_response.status_code == 200
        test_id = create_response.json()["id"]
        TestABTestingStartAPI.created_test_id = test_id
        
        # Now start the test
        start_response = authenticated_client.post(f"{BASE_URL}/api/ab-tests/{test_id}/start")
        assert start_response.status_code == 200, f"Expected 200, got {start_response.status_code}: {start_response.text}"
        
        data = start_response.json()
        assert data.get("status") == "running", "Test should be running after start"
        assert "startDate" in data, "Should have startDate after starting"


class TestABTestingAnalyzeAPI:
    """Tests for A/B Testing Analyze API - GET /api/ab-tests/{id}/analyze"""
    
    def test_analyze_ab_test(self, authenticated_client):
        """Test analyzing an A/B test"""
        # First create and start a test
        create_response = authenticated_client.post(
            f"{BASE_URL}/api/ab-tests",
            json={
                "name": "TEST_Analyze Test",
                "description": "Test to analyze",
                "testType": "social_post",
                "variants": [
                    {"name": "Control", "content": {"text": "Original post"}},
                    {"name": "Variant B", "content": {"text": "New post"}}
                ],
                "goalMetric": "engagement"
            }
        )
        assert create_response.status_code == 200
        test_id = create_response.json()["id"]
        
        # Start the test
        authenticated_client.post(f"{BASE_URL}/api/ab-tests/{test_id}/start")
        
        # Analyze the test
        analyze_response = authenticated_client.get(f"{BASE_URL}/api/ab-tests/{test_id}/analyze")
        assert analyze_response.status_code == 200, f"Expected 200, got {analyze_response.status_code}: {analyze_response.text}"
        
        data = analyze_response.json()
        assert "testId" in data, "Should contain testId"
        assert "results" in data, "Should contain results"
        assert "goalMetric" in data, "Should contain goalMetric"
        assert "hasStatisticalSignificance" in data, "Should contain hasStatisticalSignificance"


# ============================================
# TEAM COLLABORATION API TESTS
# ============================================

class TestTeamMembersAPI:
    """Tests for Team Members API - GET /api/team/members"""
    
    def test_team_members_without_auth_returns_401(self, api_client):
        """Test GET /api/team/members without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/team/members", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_team_members_with_auth_returns_200(self, authenticated_client):
        """Test GET /api/team/members with auth returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/team/members")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_team_members_returns_list(self, authenticated_client):
        """Test GET /api/team/members returns list"""
        response = authenticated_client.get(f"{BASE_URL}/api/team/members")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of team members"


class TestTeamInviteAPI:
    """Tests for Team Invite API - POST /api/team/invite"""
    
    def test_team_invite_without_auth_returns_401(self, api_client):
        """Test POST /api/team/invite without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/team/invite",
            headers=headers,
            json={"email": "test@example.com", "role": "editor"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_team_invite_with_auth_returns_200(self, authenticated_client):
        """Test POST /api/team/invite with auth returns 200"""
        import uuid
        unique_email = f"test-invite-{uuid.uuid4().hex[:8]}@example.com"
        
        response = authenticated_client.post(
            f"{BASE_URL}/api/team/invite",
            json={
                "email": unique_email,
                "role": "editor",
                "message": "Join our team!"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_team_invite_returns_proper_structure(self, authenticated_client):
        """Test team invite returns proper structure"""
        import uuid
        unique_email = f"test-invite-{uuid.uuid4().hex[:8]}@example.com"
        
        response = authenticated_client.post(
            f"{BASE_URL}/api/team/invite",
            json={
                "email": unique_email,
                "role": "viewer"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data, "Should contain invite id"
        assert "email" in data, "Should contain email"
        assert "role" in data, "Should contain role"
        assert "status" in data, "Should contain status"
        assert data["status"] == "pending", "New invite should be pending"


class TestTeamActivityAPI:
    """Tests for Team Activity API - GET /api/team/activity"""
    
    def test_team_activity_without_auth_returns_401(self, api_client):
        """Test GET /api/team/activity without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/team/activity", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_team_activity_with_auth_returns_200(self, authenticated_client):
        """Test GET /api/team/activity with auth returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/team/activity")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_team_activity_returns_list(self, authenticated_client):
        """Test GET /api/team/activity returns list"""
        response = authenticated_client.get(f"{BASE_URL}/api/team/activity")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of activities"


class TestTeamCommentsAPI:
    """Tests for Team Comments API - POST /api/team/comments"""
    
    def test_add_comment_without_auth_returns_401(self, api_client):
        """Test POST /api/team/comments without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/team/comments",
            headers=headers,
            json={
                "entityType": "campaign",
                "entityId": "test-123",
                "content": "Test comment"
            }
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_add_comment_with_auth_returns_200(self, authenticated_client):
        """Test POST /api/team/comments with auth returns 200"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/team/comments",
            json={
                "entityType": "campaign",
                "entityId": "test-campaign-123",
                "content": "TEST_This is a test comment"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_add_comment_returns_proper_structure(self, authenticated_client):
        """Test add comment returns proper structure"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/team/comments",
            json={
                "entityType": "lead",
                "entityId": "test-lead-456",
                "content": "TEST_Comment on lead"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data, "Should contain comment id"
        assert "content" in data, "Should contain content"
        assert "entityType" in data, "Should contain entityType"
        assert "entityId" in data, "Should contain entityId"
        assert "userId" in data, "Should contain userId"
        assert "createdAt" in data, "Should contain createdAt"


class TestTeamRolesAPI:
    """Tests for Team Roles API - GET /api/team/roles (no auth required)"""
    
    def test_team_roles_returns_200(self, api_client):
        """Test GET /api/team/roles returns 200 without auth"""
        response = api_client.get(f"{BASE_URL}/api/team/roles")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_team_roles_returns_all_roles(self, api_client):
        """Test GET /api/team/roles returns all expected roles"""
        response = api_client.get(f"{BASE_URL}/api/team/roles")
        assert response.status_code == 200
        
        data = response.json()
        expected_roles = ["owner", "admin", "editor", "viewer", "guest"]
        
        for role in expected_roles:
            assert role in data, f"Should contain {role} role"


# ============================================
# AI WEBSITE BUILDER API TESTS
# ============================================

class TestWebsiteGenerateAPI:
    """Tests for Website Generate API - POST /api/websites/generate"""
    
    def test_generate_website_without_auth_returns_401(self, api_client):
        """Test POST /api/websites/generate without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/websites/generate",
            headers=headers,
            json={"userDescription": "A tech startup"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_generate_website_with_auth_returns_200(self, authenticated_client):
        """Test POST /api/websites/generate with auth returns 200"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/websites/generate",
            json={
                "userDescription": "TEST_A modern tech startup offering AI-powered solutions for small businesses",
                "brandPreferences": {"colorScheme": "modern"},
                "contactMethod": "form"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_generate_website_returns_proper_structure(self, authenticated_client):
        """Test generate website returns proper structure"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/websites/generate",
            json={
                "userDescription": "TEST_Professional consulting firm specializing in business strategy",
                "brandPreferences": {"colorScheme": "professional"},
                "contactMethod": "email",
                "contactValue": "contact@test.com"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data, "Should contain website id"
        assert "htmlContent" in data, "Should contain htmlContent"
        assert "status" in data, "Should contain status"
        assert data["status"] == "draft", "New website should be in draft status"


class TestWebsiteListAPI:
    """Tests for Website List API - GET /api/websites"""
    
    def test_list_websites_without_auth_returns_401(self, api_client):
        """Test GET /api/websites without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/websites", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_list_websites_with_auth_returns_200(self, authenticated_client):
        """Test GET /api/websites with auth returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/websites")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_list_websites_returns_list(self, authenticated_client):
        """Test GET /api/websites returns list"""
        response = authenticated_client.get(f"{BASE_URL}/api/websites")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of websites"


class TestWebsiteRefineAPI:
    """Tests for Website Refine API - POST /api/websites/{id}/refine"""
    
    def test_refine_website_flow(self, authenticated_client):
        """Test refining a website with feedback"""
        # First generate a website
        generate_response = authenticated_client.post(
            f"{BASE_URL}/api/websites/generate",
            json={
                "userDescription": "TEST_E-commerce store selling handmade crafts",
                "brandPreferences": {"colorScheme": "warm"}
            }
        )
        assert generate_response.status_code == 200
        website_id = generate_response.json()["id"]
        
        # Now refine it
        refine_response = authenticated_client.post(
            f"{BASE_URL}/api/websites/{website_id}/refine",
            json={
                "feedback": "Make the hero section more prominent and add more testimonials"
            }
        )
        assert refine_response.status_code == 200, f"Expected 200, got {refine_response.status_code}: {refine_response.text}"
        
        data = refine_response.json()
        assert "id" in data, "Should contain website id"
        assert "htmlContent" in data, "Should contain refined htmlContent"
        assert "version" in data, "Should contain version"
        assert data["version"] >= 2, "Version should be incremented after refinement"


class TestWebsiteColorSchemesAPI:
    """Tests for Website Color Schemes API - GET /api/websites/color-schemes/list (no auth)"""
    
    def test_color_schemes_returns_200(self, api_client):
        """Test GET /api/websites/color-schemes/list returns 200 without auth"""
        response = api_client.get(f"{BASE_URL}/api/websites/color-schemes/list")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_color_schemes_returns_all_schemes(self, api_client):
        """Test GET /api/websites/color-schemes/list returns all expected schemes"""
        response = api_client.get(f"{BASE_URL}/api/websites/color-schemes/list")
        assert response.status_code == 200
        
        data = response.json()
        expected_schemes = ["modern", "professional", "creative", "minimal", "warm", "nature"]
        
        for scheme in expected_schemes:
            assert scheme in data, f"Should contain {scheme} color scheme"
            assert "primary" in data[scheme], f"{scheme} should have primary color"
            assert "secondary" in data[scheme], f"{scheme} should have secondary color"
            assert "accent" in data[scheme], f"{scheme} should have accent color"


# ============================================
# TIKTOK & YOUTUBE SCHEDULING API TESTS
# ============================================

class TestTikTokSchedulingAPI:
    """Tests for TikTok Scheduling API - GET /api/scheduling/optimal-times?platform=tiktok"""
    
    def test_tiktok_optimal_times_without_auth_returns_401(self, api_client):
        """Test GET /api/scheduling/optimal-times?platform=tiktok without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            f"{BASE_URL}/api/scheduling/optimal-times?platform=tiktok&count=3",
            headers=headers
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_tiktok_optimal_times_with_auth_returns_200(self, authenticated_client):
        """Test GET /api/scheduling/optimal-times?platform=tiktok with auth returns 200"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/scheduling/optimal-times?platform=tiktok&count=3"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_tiktok_optimal_times_returns_proper_structure(self, authenticated_client):
        """Test TikTok optimal times returns proper structure"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/scheduling/optimal-times?platform=tiktok&count=5"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of optimal times"
        
        if len(data) > 0:
            time_slot = data[0]
            assert time_slot["platform"] == "tiktok", "Platform should be tiktok"
            assert "scheduledFor" in time_slot, "Should contain scheduledFor"
            assert "predictedEngagement" in time_slot, "Should contain predictedEngagement"
            assert "recommendation" in time_slot, "Should contain recommendation"


class TestYouTubeSchedulingAPI:
    """Tests for YouTube Scheduling API - GET /api/scheduling/optimal-times?platform=youtube"""
    
    def test_youtube_optimal_times_without_auth_returns_401(self, api_client):
        """Test GET /api/scheduling/optimal-times?platform=youtube without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            f"{BASE_URL}/api/scheduling/optimal-times?platform=youtube&count=3",
            headers=headers
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_youtube_optimal_times_with_auth_returns_200(self, authenticated_client):
        """Test GET /api/scheduling/optimal-times?platform=youtube with auth returns 200"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/scheduling/optimal-times?platform=youtube&count=3"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_youtube_optimal_times_returns_proper_structure(self, authenticated_client):
        """Test YouTube optimal times returns proper structure"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/scheduling/optimal-times?platform=youtube&count=5"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of optimal times"
        
        if len(data) > 0:
            time_slot = data[0]
            assert time_slot["platform"] == "youtube", "Platform should be youtube"
            assert "scheduledFor" in time_slot, "Should contain scheduledFor"
            assert "predictedEngagement" in time_slot, "Should contain predictedEngagement"
            assert "recommendation" in time_slot, "Should contain recommendation"


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
        
        // Delete test A/B tests
        db.ab_tests.deleteMany({{ name: /^TEST_/ }});
        
        // Delete test websites
        db.ai_websites.deleteMany({{ "businessContext.description": /^TEST_/ }});
        
        // Delete test comments
        db.comments.deleteMany({{ content: /^TEST_/ }});
        
        // Delete test scheduled actions
        db.scheduled_actions.deleteMany({{ content: /^TEST_/ }});
        
        // Delete test invites
        db.team_invites.deleteMany({{ email: /test-invite-/ }});
        
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
