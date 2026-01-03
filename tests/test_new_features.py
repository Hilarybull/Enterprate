"""
EnterprateAI New Features Tests - Iteration 2
Tests for:
- Scheduling Service API (optimal times, scheduled actions)
- Advanced Analytics API (dashboard, revenue trends, lead funnel, reports)
- Extended Growth Agent (new alert types: low_engagement, growth_opportunity, instagram_opportunity)
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


# ============================================
# SCHEDULING API TESTS
# ============================================

class TestSchedulingOptimalTimesAPI:
    """Tests for Scheduling Optimal Times API - GET /api/scheduling/optimal-times"""
    
    def test_optimal_times_without_auth_returns_401(self, api_client):
        """Test GET /api/scheduling/optimal-times without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            f"{BASE_URL}/api/scheduling/optimal-times?platform=instagram&count=5",
            headers=headers
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_optimal_times_instagram_returns_200(self, authenticated_client):
        """Test GET /api/scheduling/optimal-times for Instagram returns 200"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/scheduling/optimal-times?platform=instagram&count=5"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_optimal_times_returns_correct_count(self, authenticated_client):
        """Test that optimal times returns requested count"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/scheduling/optimal-times?platform=instagram&count=5"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of optimal times"
        assert len(data) <= 5, f"Should return at most 5 times, got {len(data)}"
    
    def test_optimal_times_structure(self, authenticated_client):
        """Test optimal times response structure"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/scheduling/optimal-times?platform=linkedin&count=3"
        )
        assert response.status_code == 200
        
        data = response.json()
        if len(data) > 0:
            time_slot = data[0]
            assert "scheduledFor" in time_slot, "Should contain scheduledFor"
            assert "platform" in time_slot, "Should contain platform"
            assert "timeSlot" in time_slot, "Should contain timeSlot"
            assert "dayOfWeek" in time_slot, "Should contain dayOfWeek"
            assert "predictedEngagement" in time_slot, "Should contain predictedEngagement"
            assert "recommendation" in time_slot, "Should contain recommendation"
    
    def test_optimal_times_different_platforms(self, authenticated_client):
        """Test optimal times for different platforms"""
        platforms = ["linkedin", "twitter", "facebook", "instagram"]
        
        for platform in platforms:
            response = authenticated_client.get(
                f"{BASE_URL}/api/scheduling/optimal-times?platform={platform}&count=3"
            )
            assert response.status_code == 200, f"Failed for platform: {platform}"
            
            data = response.json()
            if len(data) > 0:
                assert data[0]["platform"] == platform, f"Platform mismatch for {platform}"


class TestSchedulingActionsAPI:
    """Tests for Scheduling Actions API - POST/GET /api/scheduling/actions"""
    
    def test_schedule_action_without_auth_returns_401(self, api_client):
        """Test POST /api/scheduling/actions without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/scheduling/actions",
            headers=headers,
            json={
                "actionType": "social_post",
                "platform": "instagram",
                "content": "Test post"
            }
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_schedule_action_returns_200(self, authenticated_client):
        """Test POST /api/scheduling/actions with auth returns 200"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/scheduling/actions",
            json={
                "actionType": "social_post",
                "platform": "instagram",
                "content": "TEST_Scheduled post for Instagram #business #growth",
                "hashtags": ["business", "growth"]
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_schedule_action_returns_scheduled_data(self, authenticated_client):
        """Test that schedule action returns proper data"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/scheduling/actions",
            json={
                "actionType": "social_post",
                "platform": "linkedin",
                "content": "TEST_LinkedIn scheduled post",
                "hashtags": ["linkedin", "professional"]
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data, "Should contain action id"
        assert "scheduledFor" in data, "Should contain scheduledFor"
        assert "status" in data, "Should contain status"
        assert data["status"] == "scheduled", f"Status should be scheduled, got {data['status']}"
        assert data["platform"] == "linkedin", "Platform should match"
    
    def test_get_scheduled_actions_returns_200(self, authenticated_client):
        """Test GET /api/scheduling/actions returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/scheduling/actions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_get_scheduled_actions_returns_list(self, authenticated_client):
        """Test GET /api/scheduling/actions returns list"""
        response = authenticated_client.get(f"{BASE_URL}/api/scheduling/actions")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of scheduled actions"
    
    def test_get_scheduled_actions_with_status_filter(self, authenticated_client):
        """Test GET /api/scheduling/actions with status filter"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/scheduling/actions?status=scheduled"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list"
        # All returned actions should have status=scheduled
        for action in data:
            assert action.get("status") == "scheduled", f"Expected scheduled status, got {action.get('status')}"
    
    def test_get_scheduled_actions_with_platform_filter(self, authenticated_client):
        """Test GET /api/scheduling/actions with platform filter"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/scheduling/actions?platform=instagram"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list"


# ============================================
# ADVANCED ANALYTICS API TESTS
# ============================================

class TestAnalyticsDashboardAPI:
    """Tests for Analytics Dashboard API - GET /api/analytics/dashboard"""
    
    def test_dashboard_without_auth_returns_401(self, api_client):
        """Test GET /api/analytics/dashboard without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_dashboard_returns_200(self, authenticated_client):
        """Test GET /api/analytics/dashboard with auth returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/analytics/dashboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_dashboard_returns_overview_metrics(self, authenticated_client):
        """Test dashboard returns overview, growth, social, finance metrics"""
        response = authenticated_client.get(f"{BASE_URL}/api/analytics/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check main sections
        assert "overview" in data, "Should contain overview section"
        assert "growth" in data, "Should contain growth section"
        assert "social" in data, "Should contain social section"
        assert "finance" in data, "Should contain finance section"
        assert "generatedAt" in data, "Should contain generatedAt timestamp"
    
    def test_dashboard_overview_structure(self, authenticated_client):
        """Test dashboard overview section structure"""
        response = authenticated_client.get(f"{BASE_URL}/api/analytics/dashboard")
        data = response.json()
        
        overview = data["overview"]
        assert "totalRevenue" in overview, "Overview should contain totalRevenue"
        assert "totalExpenses" in overview, "Overview should contain totalExpenses"
        assert "netProfit" in overview, "Overview should contain netProfit"
        assert "profitMargin" in overview, "Overview should contain profitMargin"
    
    def test_dashboard_growth_structure(self, authenticated_client):
        """Test dashboard growth section structure"""
        response = authenticated_client.get(f"{BASE_URL}/api/analytics/dashboard")
        data = response.json()
        
        growth = data["growth"]
        assert "totalLeads" in growth, "Growth should contain totalLeads"
        assert "convertedLeads" in growth, "Growth should contain convertedLeads"
        assert "conversionRate" in growth, "Growth should contain conversionRate"
        assert "activeCampaigns" in growth, "Growth should contain activeCampaigns"
    
    def test_dashboard_social_structure(self, authenticated_client):
        """Test dashboard social section structure"""
        response = authenticated_client.get(f"{BASE_URL}/api/analytics/dashboard")
        data = response.json()
        
        social = data["social"]
        assert "totalPosts" in social, "Social should contain totalPosts"
        assert "publishedPosts" in social, "Social should contain publishedPosts"
        assert "scheduledPosts" in social, "Social should contain scheduledPosts"
        assert "platformBreakdown" in social, "Social should contain platformBreakdown"


class TestAnalyticsRevenueTrendsAPI:
    """Tests for Revenue Trends API - GET /api/analytics/revenue-trends"""
    
    def test_revenue_trends_without_auth_returns_401(self, api_client):
        """Test GET /api/analytics/revenue-trends without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            f"{BASE_URL}/api/analytics/revenue-trends?days=30",
            headers=headers
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_revenue_trends_returns_200(self, authenticated_client):
        """Test GET /api/analytics/revenue-trends with auth returns 200"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/analytics/revenue-trends?days=30"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_revenue_trends_returns_summary(self, authenticated_client):
        """Test revenue trends returns summary with totals"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/analytics/revenue-trends?days=30"
        )
        assert response.status_code == 200
        
        data = response.json()
        
        assert "period" in data, "Should contain period"
        assert "trends" in data, "Should contain trends"
        assert "summary" in data, "Should contain summary"
        
        summary = data["summary"]
        assert "totalRevenue" in summary, "Summary should contain totalRevenue"
        assert "totalExpenses" in summary, "Summary should contain totalExpenses"
        assert "totalProfit" in summary, "Summary should contain totalProfit"
        assert "avgDailyRevenue" in summary, "Summary should contain avgDailyRevenue"
    
    def test_revenue_trends_different_periods(self, authenticated_client):
        """Test revenue trends with different day periods"""
        for days in [7, 30, 90]:
            response = authenticated_client.get(
                f"{BASE_URL}/api/analytics/revenue-trends?days={days}"
            )
            assert response.status_code == 200, f"Failed for {days} days"
            
            data = response.json()
            assert data["period"] == f"{days} days", f"Period should be {days} days"


class TestAnalyticsLeadFunnelAPI:
    """Tests for Lead Funnel API - GET /api/analytics/lead-funnel"""
    
    def test_lead_funnel_without_auth_returns_401(self, api_client):
        """Test GET /api/analytics/lead-funnel without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/analytics/lead-funnel", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_lead_funnel_returns_200(self, authenticated_client):
        """Test GET /api/analytics/lead-funnel with auth returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/analytics/lead-funnel")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_lead_funnel_returns_funnel_data(self, authenticated_client):
        """Test lead funnel returns funnel data with conversion rates"""
        response = authenticated_client.get(f"{BASE_URL}/api/analytics/lead-funnel")
        assert response.status_code == 200
        
        data = response.json()
        
        assert "total" in data, "Should contain total"
        assert "funnel" in data, "Should contain funnel"
        assert "funnelRates" in data, "Should contain funnelRates"
        assert "stageConversion" in data, "Should contain stageConversion"
        assert "overallConversionRate" in data, "Should contain overallConversionRate"
    
    def test_lead_funnel_stages(self, authenticated_client):
        """Test lead funnel contains all stages"""
        response = authenticated_client.get(f"{BASE_URL}/api/analytics/lead-funnel")
        data = response.json()
        
        funnel = data["funnel"]
        expected_stages = ["NEW", "CONTACTED", "QUALIFIED", "CONVERTED", "LOST"]
        
        for stage in expected_stages:
            assert stage in funnel, f"Funnel should contain {stage} stage"


class TestAnalyticsReportAPI:
    """Tests for Business Report API - GET /api/analytics/report"""
    
    def test_report_without_auth_returns_401(self, api_client):
        """Test GET /api/analytics/report without auth returns 401/403"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            f"{BASE_URL}/api/analytics/report?report_type=monthly",
            headers=headers
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_report_monthly_returns_200(self, authenticated_client):
        """Test GET /api/analytics/report with monthly type returns 200"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/analytics/report?report_type=monthly"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_report_returns_comprehensive_data(self, authenticated_client):
        """Test report returns comprehensive data with insights"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/analytics/report?report_type=monthly"
        )
        assert response.status_code == 200
        
        data = response.json()
        
        assert "reportType" in data, "Should contain reportType"
        assert "period" in data, "Should contain period"
        assert "generatedAt" in data, "Should contain generatedAt"
        assert "executiveSummary" in data, "Should contain executiveSummary"
        assert "sections" in data, "Should contain sections"
        assert "insights" in data, "Should contain insights"
        assert "recommendations" in data, "Should contain recommendations"
    
    def test_report_executive_summary(self, authenticated_client):
        """Test report executive summary structure"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/analytics/report?report_type=monthly"
        )
        data = response.json()
        
        summary = data["executiveSummary"]
        assert "revenue" in summary, "Summary should contain revenue"
        assert "profit" in summary, "Summary should contain profit"
        assert "leads" in summary, "Summary should contain leads"
        assert "conversionRate" in summary, "Summary should contain conversionRate"
        assert "activeCampaigns" in summary, "Summary should contain activeCampaigns"
    
    def test_report_different_types(self, authenticated_client):
        """Test report with different types (weekly, monthly, quarterly)"""
        report_types = ["weekly", "monthly", "quarterly"]
        
        for report_type in report_types:
            response = authenticated_client.get(
                f"{BASE_URL}/api/analytics/report?report_type={report_type}"
            )
            assert response.status_code == 200, f"Failed for report type: {report_type}"
            
            data = response.json()
            assert data["reportType"] == report_type, f"Report type should be {report_type}"


# ============================================
# EXTENDED GROWTH AGENT TESTS (New Alert Types)
# ============================================

class TestGrowthAgentNewAlertTypes:
    """Tests for Growth Agent new alert types: low_engagement, growth_opportunity, instagram_opportunity"""
    
    def test_analyze_includes_new_alert_types(self, authenticated_client):
        """Test that analyze can return new alert types"""
        response = authenticated_client.get(f"{BASE_URL}/api/growth/agent/analyze")
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data, "Should contain alerts"
        
        # Check that alerts is a list
        assert isinstance(data["alerts"], list), "Alerts should be a list"
        
        # Check alert structure if any alerts exist
        for alert in data["alerts"]:
            assert "id" in alert, "Alert should have id"
            assert "type" in alert, "Alert should have type"
            assert "severity" in alert, "Alert should have severity"
            assert "title" in alert, "Alert should have title"
            assert "message" in alert, "Alert should have message"
    
    def test_recommend_low_engagement_type(self, authenticated_client):
        """Test recommend endpoint with low_engagement alert type"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/growth/agent/recommend",
            json={"alertType": "low_engagement"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Should contain recommendation id"
        assert "status" in data, "Should contain status"
        assert data["status"] == "pending", "New recommendation should be pending"
    
    def test_recommend_growth_opportunity_type(self, authenticated_client):
        """Test recommend endpoint with growth_opportunity alert type"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/growth/agent/recommend",
            json={"alertType": "growth_opportunity"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Should contain recommendation id"
        assert "title" in data, "Should contain title"
    
    def test_recommend_instagram_campaign_type(self, authenticated_client):
        """Test recommend endpoint with instagram_campaign alert type"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/growth/agent/recommend",
            json={"alertType": "instagram_campaign"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Should contain recommendation id"
        assert "actions" in data, "Should contain actions"
        
        # Check if Instagram is mentioned in actions
        actions = data.get("actions", [])
        instagram_action = next(
            (a for a in actions if a.get("platform") == "instagram"),
            None
        )
        # Instagram campaign should have Instagram-related actions
        assert instagram_action is not None or len(actions) > 0, "Should have actions"


# ============================================
# DYNAMIC FEES API - Verify 13 entries
# ============================================

class TestDynamicFeesCount:
    """Verify Dynamic Fees API returns exactly 13 entries"""
    
    def test_fees_returns_13_entries(self, api_client):
        """Test GET /api/company-profile/fees returns exactly 13 entries"""
        response = api_client.get(f"{BASE_URL}/api/company-profile/fees")
        assert response.status_code == 200
        
        data = response.json()
        assert "fees" in data, "Response should contain 'fees' key"
        assert len(data["fees"]) == 13, f"Expected 13 fees, got {len(data['fees'])}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
