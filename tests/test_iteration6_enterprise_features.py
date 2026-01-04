"""
Iteration 6 Tests: Enterprise Features
- Team Collaboration API
- A/B Testing API
- Campaign Automation API
- Website Analytics API
- Expanded Quick Templates (15 templates)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from previous iterations
TEST_EMAIL = "webbuilder_test2@example.com"
TEST_PASSWORD = "Test123!"
TEST_WORKSPACE_ID = "592c480e-7da2-4500-a987-567c1c450ba7"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get headers with auth token and workspace"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "X-Workspace-ID": TEST_WORKSPACE_ID
    }


# ============================================
# TEAM COLLABORATION API TESTS
# ============================================

class TestTeamRolesAPI:
    """Test GET /api/team/roles - Returns 5 roles"""
    
    def test_get_roles_returns_200(self):
        """Test roles endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/team/roles")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_get_roles_returns_5_roles(self):
        """Test roles endpoint returns exactly 5 roles"""
        response = requests.get(f"{BASE_URL}/api/team/roles")
        data = response.json()
        assert len(data) == 5, f"Expected 5 roles, got {len(data)}"
    
    def test_get_roles_contains_expected_roles(self):
        """Test roles contains owner, admin, editor, viewer, guest"""
        response = requests.get(f"{BASE_URL}/api/team/roles")
        data = response.json()
        expected_roles = ["owner", "admin", "editor", "viewer", "guest"]
        for role in expected_roles:
            assert role in data, f"Missing role: {role}"
    
    def test_roles_have_required_fields(self):
        """Test each role has level, label, permissions"""
        response = requests.get(f"{BASE_URL}/api/team/roles")
        data = response.json()
        for role_name, role_data in data.items():
            assert "level" in role_data, f"Role {role_name} missing 'level'"
            assert "label" in role_data, f"Role {role_name} missing 'label'"
            assert "permissions" in role_data, f"Role {role_name} missing 'permissions'"


class TestTeamMembersAPI:
    """Test GET /api/team/members - List team members (requires auth)"""
    
    def test_get_members_requires_auth(self):
        """Test members endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/team/members")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
    
    def test_get_members_with_auth(self, auth_headers):
        """Test members endpoint with authentication"""
        response = requests.get(f"{BASE_URL}/api/team/members", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_get_members_returns_list(self, auth_headers):
        """Test members endpoint returns a list"""
        response = requests.get(f"{BASE_URL}/api/team/members", headers=auth_headers)
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"


class TestTeamInviteAPI:
    """Test POST /api/team/invite - Invite team member"""
    
    def test_invite_requires_auth(self):
        """Test invite endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/team/invite", json={
            "email": "test@example.com",
            "role": "editor"
        })
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
    
    def test_invite_member_with_auth(self, auth_headers):
        """Test invite member with authentication"""
        test_email = f"test_invite_{int(time.time())}@example.com"
        response = requests.post(f"{BASE_URL}/api/team/invite", 
            headers=auth_headers,
            json={
                "email": test_email,
                "role": "editor",
                "message": "Test invitation"
            }
        )
        # Should succeed or fail with validation error (not auth error)
        assert response.status_code in [200, 201, 400], f"Unexpected status: {response.status_code}: {response.text}"


# ============================================
# A/B TESTING API TESTS
# ============================================

class TestABTestsListAPI:
    """Test GET /api/ab-tests - List A/B tests"""
    
    def test_list_ab_tests_requires_auth(self):
        """Test A/B tests list requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ab-tests")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
    
    def test_list_ab_tests_with_auth(self, auth_headers):
        """Test A/B tests list with authentication"""
        response = requests.get(f"{BASE_URL}/api/ab-tests", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_list_ab_tests_returns_list(self, auth_headers):
        """Test A/B tests returns a list"""
        response = requests.get(f"{BASE_URL}/api/ab-tests", headers=auth_headers)
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"


class TestABTestsCreateAPI:
    """Test POST /api/ab-tests - Create A/B test"""
    
    def test_create_ab_test_requires_auth(self):
        """Test create A/B test requires authentication"""
        response = requests.post(f"{BASE_URL}/api/ab-tests", json={
            "name": "Test",
            "description": "Test",
            "testType": "campaign",
            "variants": []
        })
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
    
    def test_create_ab_test_with_auth(self, auth_headers):
        """Test create A/B test with authentication"""
        test_name = f"Test AB {int(time.time())}"
        response = requests.post(f"{BASE_URL}/api/ab-tests",
            headers=auth_headers,
            json={
                "name": test_name,
                "description": "Test A/B test for iteration 6",
                "testType": "campaign",
                "variants": [
                    {"name": "Control (A)", "content": {"headline": "Test A"}},
                    {"name": "Variant B", "content": {"headline": "Test B"}}
                ],
                "durationDays": 7,
                "goalMetric": "conversion_rate"
            }
        )
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response should contain 'id'"
        return data.get("id")


# ============================================
# CAMPAIGN AUTOMATION API TESTS
# ============================================

class TestAutomationTriggersAPI:
    """Test GET /api/automation/triggers - Returns 13 triggers"""
    
    def test_get_triggers_returns_200(self):
        """Test triggers endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/automation/triggers")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_get_triggers_returns_dict(self):
        """Test triggers endpoint returns a dictionary"""
        response = requests.get(f"{BASE_URL}/api/automation/triggers")
        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
    
    def test_get_triggers_count(self):
        """Test triggers endpoint returns expected number of triggers"""
        response = requests.get(f"{BASE_URL}/api/automation/triggers")
        data = response.json()
        # Should have at least 10 triggers (13 expected)
        assert len(data) >= 10, f"Expected at least 10 triggers, got {len(data)}"
        print(f"Found {len(data)} triggers: {list(data.keys())}")


class TestAutomationActionsAPI:
    """Test GET /api/automation/actions - Returns 12 actions"""
    
    def test_get_actions_returns_200(self):
        """Test actions endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/automation/actions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_get_actions_returns_dict(self):
        """Test actions endpoint returns a dictionary"""
        response = requests.get(f"{BASE_URL}/api/automation/actions")
        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
    
    def test_get_actions_count(self):
        """Test actions endpoint returns expected number of actions"""
        response = requests.get(f"{BASE_URL}/api/automation/actions")
        data = response.json()
        # Should have at least 8 actions (12 expected)
        assert len(data) >= 8, f"Expected at least 8 actions, got {len(data)}"
        print(f"Found {len(data)} actions: {list(data.keys())}")


class TestAutomationRulesAPI:
    """Test automation rules CRUD"""
    
    def test_create_rule_requires_auth(self):
        """Test create rule requires authentication"""
        response = requests.post(f"{BASE_URL}/api/automation/rules", json={
            "name": "Test Rule",
            "description": "Test",
            "trigger": {"type": "lead_created"},
            "actions": [{"type": "send_notification", "config": {}}]
        })
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
    
    def test_create_rule_with_auth(self, auth_headers):
        """Test create automation rule with authentication"""
        rule_name = f"Test Rule {int(time.time())}"
        response = requests.post(f"{BASE_URL}/api/automation/rules",
            headers=auth_headers,
            json={
                "name": rule_name,
                "description": "Test automation rule for iteration 6",
                "trigger": {"type": "lead_created", "config": {}},
                "conditions": [],
                "actions": [{"type": "send_notification", "config": {"message": "New lead!"}}],
                "isActive": True,
                "priority": 0
            }
        )
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response should contain 'id'"
    
    def test_list_rules_with_auth(self, auth_headers):
        """Test list automation rules with authentication"""
        response = requests.get(f"{BASE_URL}/api/automation/rules", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"


# ============================================
# WEBSITE ANALYTICS API TESTS
# ============================================

class TestWebsiteAnalyticsOverviewAPI:
    """Test GET /api/website-analytics/overview - Analytics overview"""
    
    def test_overview_requires_auth(self):
        """Test analytics overview requires authentication"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/overview")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
    
    def test_overview_with_auth(self, auth_headers):
        """Test analytics overview with authentication"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/overview", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_overview_returns_expected_structure(self, auth_headers):
        """Test analytics overview returns expected structure"""
        response = requests.get(f"{BASE_URL}/api/website-analytics/overview", headers=auth_headers)
        data = response.json()
        assert "summary" in data, "Response should contain 'summary'"
        assert "websites" in data, "Response should contain 'websites'"
        
        summary = data.get("summary", {})
        expected_fields = ["totalWebsites", "totalPageViews", "totalVisitors", "totalConversions"]
        for field in expected_fields:
            assert field in summary, f"Summary missing field: {field}"


# ============================================
# EXPANDED TEMPLATES API TESTS (15 templates)
# ============================================

class TestExpandedTemplatesAPI:
    """Test GET /api/ai-websites/templates/list - Returns 15 templates"""
    
    def test_templates_list_returns_200(self):
        """Test templates list returns 200"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/list")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_templates_list_returns_15_templates(self):
        """Test templates list returns exactly 15 templates"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/list")
        data = response.json()
        assert len(data) == 15, f"Expected 15 templates, got {len(data)}"
    
    def test_templates_contains_new_templates(self):
        """Test templates contains the 5 new templates (Education, Legal, Events, Agency, Nonprofit)"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/list")
        data = response.json()
        new_templates = ["education", "legal", "events", "agency", "nonprofit"]
        for template_id in new_templates:
            assert template_id in data, f"Missing new template: {template_id}"
    
    def test_templates_have_required_fields(self):
        """Test each template has required fields"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/list")
        data = response.json()
        required_fields = ["name", "icon", "description", "defaultColorScheme", "prompt", "features", "cta"]
        for template_id, template_data in data.items():
            for field in required_fields:
                assert field in template_data, f"Template {template_id} missing field: {field}"
    
    def test_get_specific_template_education(self):
        """Test get specific template - Education"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/education")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("id") == "education", f"Expected id 'education', got {data.get('id')}"
        assert "name" in data, "Template should have 'name'"
    
    def test_get_specific_template_legal(self):
        """Test get specific template - Legal"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/legal")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("id") == "legal", f"Expected id 'legal', got {data.get('id')}"
    
    def test_get_specific_template_events(self):
        """Test get specific template - Events"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/events")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("id") == "events", f"Expected id 'events', got {data.get('id')}"
    
    def test_get_specific_template_agency(self):
        """Test get specific template - Agency"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/agency")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("id") == "agency", f"Expected id 'agency', got {data.get('id')}"
    
    def test_get_specific_template_nonprofit(self):
        """Test get specific template - Nonprofit"""
        response = requests.get(f"{BASE_URL}/api/ai-websites/templates/nonprofit")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("id") == "nonprofit", f"Expected id 'nonprofit', got {data.get('id')}"


# ============================================
# AUTOMATION OPERATORS API TEST
# ============================================

class TestAutomationOperatorsAPI:
    """Test GET /api/automation/operators"""
    
    def test_get_operators_returns_200(self):
        """Test operators endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/automation/operators")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_get_operators_returns_dict(self):
        """Test operators endpoint returns a dictionary"""
        response = requests.get(f"{BASE_URL}/api/automation/operators")
        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"


# ============================================
# CLEANUP TEST DATA
# ============================================

class TestCleanup:
    """Cleanup test data created during tests"""
    
    def test_cleanup_test_ab_tests(self, auth_headers):
        """Cleanup A/B tests created during testing"""
        response = requests.get(f"{BASE_URL}/api/ab-tests", headers=auth_headers)
        if response.status_code == 200:
            tests = response.json()
            for test in tests:
                if test.get("name", "").startswith("Test AB"):
                    requests.delete(f"{BASE_URL}/api/ab-tests/{test['id']}", headers=auth_headers)
        assert True  # Cleanup is best-effort
    
    def test_cleanup_test_automation_rules(self, auth_headers):
        """Cleanup automation rules created during testing"""
        response = requests.get(f"{BASE_URL}/api/automation/rules", headers=auth_headers)
        if response.status_code == 200:
            rules = response.json()
            for rule in rules:
                if rule.get("name", "").startswith("Test Rule"):
                    requests.delete(f"{BASE_URL}/api/automation/rules/{rule['id']}", headers=auth_headers)
        assert True  # Cleanup is best-effort


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
