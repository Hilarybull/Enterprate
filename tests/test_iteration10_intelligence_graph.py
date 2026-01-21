"""
Test Suite for Iteration 10 - Intelligence Graph Feature
Tests all Intelligence Graph APIs and integration logging
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://business-wizard.preview.emergentagent.com').rstrip('/')

# Test credentials
TEST_EMAIL = "test_invoice@example.com"
TEST_PASSWORD = "Test123!"
WORKSPACE_ID = "17387b8d-5b7d-4685-b069-641f72b2b9e5"


class TestAuthentication:
    """Authentication tests"""
    
    def test_login_success(self):
        """Test login returns valid JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert len(data["token"]) > 0


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed")


@pytest.fixture(scope="module")
def headers(auth_token):
    """Get headers with auth token and workspace ID"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-ID": WORKSPACE_ID,
        "Content-Type": "application/json"
    }


class TestIntelligenceGraphAPIs:
    """Test Intelligence Graph API endpoints"""
    
    def test_get_insights(self, headers):
        """GET /api/intelligence/insights - Get aggregated insights"""
        response = requests.get(f"{BASE_URL}/api/intelligence/insights", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "today" in data
        assert "month" in data
        assert "entityCounts" in data
        assert "recentActivity" in data
        
        # Verify today/month structure
        assert "total" in data["today"]
        assert "breakdown" in data["today"]
        assert "total" in data["month"]
        assert "breakdown" in data["month"]
        
        # Verify entity counts
        assert isinstance(data["entityCounts"], dict)
    
    def test_get_events(self, headers):
        """GET /api/intelligence/events - Get events list"""
        response = requests.get(f"{BASE_URL}/api/intelligence/events?limit=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            event = data[0]
            assert "id" in event
            assert "workspace_id" in event
            assert "occurredAt" in event
    
    def test_get_events_with_entity_filter(self, headers):
        """GET /api/intelligence/events with entity_type filter"""
        response = requests.get(f"{BASE_URL}/api/intelligence/events?entity_type=invoice&limit=5", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # All returned events should be invoice type
        for event in data:
            assert event.get("entityType") == "invoice"
    
    def test_get_activity_summary_daily(self, headers):
        """GET /api/intelligence/summary - Get daily activity summary"""
        response = requests.get(f"{BASE_URL}/api/intelligence/summary?period_type=daily&periods=7", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # Each summary should have period and counts
        for summary in data:
            assert "period" in summary
            assert "period_type" in summary
            assert summary["period_type"] == "daily"
    
    def test_get_activity_summary_monthly(self, headers):
        """GET /api/intelligence/summary - Get monthly activity summary"""
        response = requests.get(f"{BASE_URL}/api/intelligence/summary?period_type=monthly&periods=3", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        for summary in data:
            if "period_type" in summary:
                assert summary["period_type"] == "monthly"
    
    def test_post_manual_event(self, headers):
        """POST /api/intelligence/events - Log manual event"""
        event_data = {
            "eventType": "test_manual_event",
            "entityType": "catalogue",
            "entityId": "test-manual-entity-123",
            "data": {"test_key": "test_value"},
            "metadata": {"source": "pytest"}
        }
        
        response = requests.post(f"{BASE_URL}/api/intelligence/events", headers=headers, json=event_data)
        assert response.status_code == 200
        data = response.json()
        
        # Verify event was created
        assert "id" in data
        assert data["eventType"] == "test_manual_event"
        assert data["entityType"] == "catalogue"
        assert data["entityId"] == "test-manual-entity-123"
        assert data["data"]["test_key"] == "test_value"
    
    def test_get_entity_timeline(self, headers):
        """GET /api/intelligence/entity/{type}/{id}/timeline - Get entity timeline"""
        # First create an event for a specific entity
        event_data = {
            "eventType": "timeline_test_event",
            "entityType": "invoice",
            "entityId": "timeline-test-invoice-123",
            "data": {"action": "test"}
        }
        requests.post(f"{BASE_URL}/api/intelligence/events", headers=headers, json=event_data)
        
        # Now get the timeline
        response = requests.get(
            f"{BASE_URL}/api/intelligence/entity/invoice/timeline-test-invoice-123/timeline",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # Should have at least the event we just created
        assert len(data) >= 1
        assert data[0]["entityId"] == "timeline-test-invoice-123"
    
    def test_get_entity_stats(self, headers):
        """GET /api/intelligence/stats/{entity_type} - Get entity stats"""
        response = requests.get(f"{BASE_URL}/api/intelligence/stats/invoice", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "entityType" in data
        assert data["entityType"] == "invoice"
        assert "eventBreakdown" in data
        assert isinstance(data["eventBreakdown"], list)


class TestIntelligenceLoggingIntegration:
    """Test that other services log events to Intelligence Graph"""
    
    def test_invoice_create_logs_event(self, headers):
        """Invoice creation should log an intelligence event"""
        # Create an invoice
        invoice_data = {
            "clientName": "TEST_Intel_Invoice_Client",
            "clientEmail": "test_intel@example.com",
            "lineItems": [{"name": "Test Service", "quantity": 1, "unitPrice": 100}],
            "currency": "GBP",
            "status": "draft"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/invoices", headers=headers, json=invoice_data)
        assert create_response.status_code == 200
        invoice_id = create_response.json()["id"]
        
        # Check that an event was logged
        time.sleep(0.5)  # Small delay for event to be logged
        events_response = requests.get(
            f"{BASE_URL}/api/intelligence/events?entity_type=invoice&limit=5",
            headers=headers
        )
        assert events_response.status_code == 200
        events = events_response.json()
        
        # Find the event for our invoice
        found_event = False
        for event in events:
            if event.get("entityId") == invoice_id and event.get("eventType") == "created":
                found_event = True
                assert event["data"]["clientName"] == "TEST_Intel_Invoice_Client"
                break
        
        assert found_event, "Invoice creation event not found in intelligence events"
    
    def test_document_generate_logs_event(self, headers):
        """Document generation should log an intelligence event"""
        # Generate a document
        doc_data = {
            "documentType": "terms_conditions",
            "inputs": {
                "companyName": "TEST_Intel_Doc_Company",
                "businessType": "Tech",
                "jurisdiction": "UK",
                "refundPolicy": "30 days",
                "liabilityLimit": "£5000"
            }
        }
        
        gen_response = requests.post(f"{BASE_URL}/api/documents/generate", headers=headers, json=doc_data)
        assert gen_response.status_code == 200
        
        # Check that an event was logged
        time.sleep(0.5)
        events_response = requests.get(
            f"{BASE_URL}/api/intelligence/events?entity_type=document&limit=5",
            headers=headers
        )
        assert events_response.status_code == 200
        events = events_response.json()
        
        # Find the generated event
        found_event = False
        for event in events:
            if event.get("eventType") == "generated" and event.get("data", {}).get("documentType") == "terms_conditions":
                found_event = True
                break
        
        assert found_event, "Document generation event not found in intelligence events"
    
    def test_document_save_logs_event(self, headers):
        """Document save should log an intelligence event"""
        # Save a document
        save_data = {
            "documentType": "privacy_policy",
            "title": "TEST_Intel_Privacy_Policy",
            "content": "Test privacy policy content",
            "inputs": {"companyName": "TEST_Intel_Company"}
        }
        
        save_response = requests.post(f"{BASE_URL}/api/documents/save", headers=headers, json=save_data)
        assert save_response.status_code == 200
        doc_id = save_response.json()["id"]
        
        # Check that an event was logged
        time.sleep(0.5)
        events_response = requests.get(
            f"{BASE_URL}/api/intelligence/events?entity_type=document&limit=5",
            headers=headers
        )
        assert events_response.status_code == 200
        events = events_response.json()
        
        # Find the saved event
        found_event = False
        for event in events:
            if event.get("entityId") == doc_id and event.get("eventType") == "saved":
                found_event = True
                assert event["data"]["title"] == "TEST_Intel_Privacy_Policy"
                break
        
        assert found_event, "Document save event not found in intelligence events"
    
    def test_catalogue_bulk_add_logs_event(self, headers):
        """Catalogue bulk add should log an intelligence event"""
        # Bulk add items
        bulk_data = {
            "items": [
                {"name": "TEST_Intel_Bulk_Item_1", "unitPrice": 25, "currency": "GBP"},
                {"name": "TEST_Intel_Bulk_Item_2", "unitPrice": 35, "currency": "GBP"}
            ]
        }
        
        bulk_response = requests.post(f"{BASE_URL}/api/catalogue/bulk", headers=headers, json=bulk_data)
        assert bulk_response.status_code == 200
        assert bulk_response.json()["addedCount"] == 2
        
        # Check that an event was logged
        time.sleep(0.5)
        events_response = requests.get(
            f"{BASE_URL}/api/intelligence/events?entity_type=catalogue&limit=5",
            headers=headers
        )
        assert events_response.status_code == 200
        events = events_response.json()
        
        # Find the bulk_added event
        found_event = False
        for event in events:
            if event.get("eventType") == "bulk_added":
                found_event = True
                assert event["data"]["count"] >= 2
                break
        
        assert found_event, "Catalogue bulk add event not found in intelligence events"
    
    def test_brand_asset_upload_logs_event(self, headers):
        """Brand asset upload should log an intelligence event"""
        # Upload brand logo
        brand_data = {
            "assetType": "logo",
            "imageBase64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "filename": "TEST_intel_brand_logo.png"
        }
        
        upload_response = requests.post(f"{BASE_URL}/api/invoices/brand/assets", headers=headers, json=brand_data)
        assert upload_response.status_code == 200
        asset_id = upload_response.json()["id"]
        
        # Check that an event was logged
        time.sleep(0.5)
        events_response = requests.get(
            f"{BASE_URL}/api/intelligence/events?entity_type=brand&limit=5",
            headers=headers
        )
        assert events_response.status_code == 200
        events = events_response.json()
        
        # Find the logo_uploaded event
        found_event = False
        for event in events:
            if event.get("eventType") == "logo_uploaded" and event.get("entityId") == asset_id:
                found_event = True
                assert event["data"]["filename"] == "TEST_intel_brand_logo.png"
                break
        
        assert found_event, "Brand asset upload event not found in intelligence events"


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_data(self, headers):
        """Clean up TEST_ prefixed data"""
        # Get all catalogue items and delete TEST_ prefixed ones
        cat_response = requests.get(f"{BASE_URL}/api/catalogue", headers=headers)
        if cat_response.status_code == 200:
            items = cat_response.json()
            for item in items:
                if item.get("name", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/catalogue/{item['id']}", headers=headers)
        
        # Get all invoices and delete TEST_ prefixed ones
        inv_response = requests.get(f"{BASE_URL}/api/invoices", headers=headers)
        if inv_response.status_code == 200:
            invoices = inv_response.json()
            for inv in invoices:
                if inv.get("clientName", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/invoices/{inv['id']}", headers=headers)
        
        assert True  # Cleanup completed
