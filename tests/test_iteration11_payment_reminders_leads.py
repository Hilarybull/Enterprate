"""
Iteration 11 Tests: Payment Reminders and Lead CRM Integration
Tests for:
1. Payment Reminders: GET /api/invoices/reminders/summary
2. Payment Reminders: GET /api/invoices/reminders/pending
3. Payment Reminders: POST /api/invoices/reminders/{invoice_id}/mark-paid
4. Payment Reminders: POST /api/invoices/reminders/{invoice_id}/send
5. Payment Reminders: POST /api/invoices/reminders/update-overdue
6. Lead CRM: GET /api/leads
7. Lead CRM: POST /api/leads
8. Lead CRM: POST /api/leads/{contact_id}/convert
9. Lead CRM: GET /api/leads/analytics
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_EMAIL = "test_invoice@example.com"
TEST_PASSWORD = "Test123!"
WORKSPACE_ID = "17387b8d-5b7d-4685-b069-641f72b2b9e5"


class TestAuth:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        return data["token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth token and workspace"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "x-workspace-id": WORKSPACE_ID
        }
    
    def test_login_success(self):
        """Test login returns valid token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 0
        print(f"✓ Login successful, token received")


class TestPaymentRemindersSummary:
    """Test payment reminders summary endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "x-workspace-id": WORKSPACE_ID
        }
    
    def test_get_payment_summary(self, headers):
        """GET /api/invoices/reminders/summary - Get payment status summary"""
        response = requests.get(
            f"{BASE_URL}/api/invoices/reminders/summary",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "byStatus" in data, "Missing byStatus in response"
        assert "totalOutstanding" in data, "Missing totalOutstanding"
        assert "totalCollected" in data, "Missing totalCollected"
        assert "overdueCount" in data, "Missing overdueCount"
        assert "overdueAmount" in data, "Missing overdueAmount"
        
        # Verify byStatus structure
        by_status = data["byStatus"]
        expected_statuses = ["draft", "pending_review", "sent", "paid", "overdue"]
        for status in expected_statuses:
            assert status in by_status, f"Missing status: {status}"
            assert "count" in by_status[status], f"Missing count for {status}"
            assert "total" in by_status[status], f"Missing total for {status}"
        
        print(f"✓ Payment summary retrieved: Outstanding={data['totalOutstanding']}, Collected={data['totalCollected']}, Overdue={data['overdueCount']}")


class TestPaymentRemindersPending:
    """Test pending reminders endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "x-workspace-id": WORKSPACE_ID
        }
    
    def test_get_pending_reminders(self, headers):
        """GET /api/invoices/reminders/pending - Get pending reminders"""
        response = requests.get(
            f"{BASE_URL}/api/invoices/reminders/pending",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list), "Response should be a list"
        
        # If there are pending reminders, verify structure
        if len(data) > 0:
            reminder = data[0]
            assert "invoice" in reminder, "Missing invoice in reminder"
            assert "reminder_type" in reminder, "Missing reminder_type"
            assert "days_until_due" in reminder, "Missing days_until_due"
            print(f"✓ Found {len(data)} pending reminders")
        else:
            print("✓ No pending reminders (expected if no invoices near due date)")


class TestPaymentRemindersUpdateOverdue:
    """Test update overdue status endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "x-workspace-id": WORKSPACE_ID
        }
    
    def test_update_overdue_status(self, headers):
        """POST /api/invoices/reminders/update-overdue - Update overdue status"""
        response = requests.post(
            f"{BASE_URL}/api/invoices/reminders/update-overdue",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "checked" in data, "Missing checked count"
        assert "marked_overdue" in data, "Missing marked_overdue count"
        
        print(f"✓ Overdue update: Checked {data['checked']} invoices, marked {data['marked_overdue']} as overdue")


class TestPaymentRemindersMarkPaid:
    """Test mark invoice as paid endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "x-workspace-id": WORKSPACE_ID
        }
    
    def test_mark_paid_creates_and_marks(self, headers):
        """POST /api/invoices/reminders/{invoice_id}/mark-paid - Create invoice and mark as paid"""
        # First create a test invoice
        invoice_data = {
            "clientName": "TEST_MarkPaid Client",
            "clientEmail": "test_markpaid@example.com",
            "currency": "GBP",
            "dueDate": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "status": "sent",
            "lineItems": [
                {
                    "name": "Test Service",
                    "description": "Test service for mark paid",
                    "quantity": 1,
                    "unitPrice": 100.00,
                    "taxRate": 20
                }
            ]
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/invoices",
            json=invoice_data,
            headers=headers
        )
        assert create_response.status_code in [200, 201], f"Failed to create invoice: {create_response.text}"
        invoice = create_response.json()
        invoice_id = invoice.get("id")
        assert invoice_id, "No invoice ID returned"
        
        # Now mark it as paid
        mark_paid_response = requests.post(
            f"{BASE_URL}/api/invoices/reminders/{invoice_id}/mark-paid",
            json={
                "paymentDate": datetime.now().strftime("%Y-%m-%d"),
                "paymentMethod": "bank_transfer"
            },
            headers=headers
        )
        assert mark_paid_response.status_code == 200, f"Failed to mark paid: {mark_paid_response.text}"
        data = mark_paid_response.json()
        
        assert data.get("success") == True, "Mark paid should return success=True"
        assert "invoice" in data, "Response should contain invoice"
        assert data["invoice"]["status"] == "paid", "Invoice status should be 'paid'"
        
        print(f"✓ Invoice {invoice_id} marked as paid successfully")
        
        # Cleanup - delete the test invoice
        requests.delete(f"{BASE_URL}/api/invoices/{invoice_id}", headers=headers)


class TestPaymentRemindersSend:
    """Test send payment reminder endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "x-workspace-id": WORKSPACE_ID
        }
    
    def test_send_reminder_returns_expected_response(self, headers):
        """POST /api/invoices/reminders/{invoice_id}/send - Send payment reminder"""
        # First create a test invoice
        invoice_data = {
            "clientName": "TEST_Reminder Client",
            "clientEmail": "test_reminder@example.com",
            "currency": "GBP",
            "dueDate": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),  # Overdue
            "status": "sent",
            "lineItems": [
                {
                    "name": "Test Service",
                    "description": "Test service for reminder",
                    "quantity": 1,
                    "unitPrice": 200.00,
                    "taxRate": 20
                }
            ]
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/invoices",
            json=invoice_data,
            headers=headers
        )
        assert create_response.status_code in [200, 201], f"Failed to create invoice: {create_response.text}"
        invoice = create_response.json()
        invoice_id = invoice.get("id")
        
        # Try to send reminder
        send_response = requests.post(
            f"{BASE_URL}/api/invoices/reminders/{invoice_id}/send?reminder_type=first_overdue",
            headers=headers
        )
        assert send_response.status_code == 200, f"Failed: {send_response.text}"
        data = send_response.json()
        
        # Note: SendGrid email will fail because SENDGRID_FROM_EMAIL is not verified
        # But the endpoint should still return a response
        assert "success" in data, "Response should contain success field"
        
        if data.get("success"):
            print(f"✓ Reminder sent successfully for invoice {invoice_id}")
        else:
            # Expected: SendGrid not configured with verified sender
            assert "error" in data, "Should have error message if not successful"
            print(f"✓ Reminder endpoint works but email not sent (expected - SendGrid not configured): {data.get('error')}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/invoices/{invoice_id}", headers=headers)


class TestLeadCRMGet:
    """Test Lead CRM GET endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "x-workspace-id": WORKSPACE_ID
        }
    
    def test_get_website_leads(self, headers):
        """GET /api/leads - Get website leads"""
        response = requests.get(
            f"{BASE_URL}/api/leads",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list), "Response should be a list"
        
        # If there are leads, verify structure
        if len(data) > 0:
            lead = data[0]
            assert "id" in lead, "Lead should have id"
            assert "email" in lead, "Lead should have email"
            assert "source" in lead, "Lead should have source"
            print(f"✓ Found {len(data)} website leads")
        else:
            print("✓ No website leads yet (expected for new workspace)")


class TestLeadCRMSubmit:
    """Test Lead CRM submit endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "x-workspace-id": WORKSPACE_ID
        }
    
    def test_submit_website_lead(self, headers):
        """POST /api/leads - Submit website lead and sync to CRM"""
        unique_id = str(uuid.uuid4())[:8]
        lead_data = {
            "name": f"TEST_Lead User {unique_id}",
            "email": f"test_lead_{unique_id}@example.com",
            "phone": "+1234567890",
            "company": "Test Company",
            "message": "I'm interested in your services",
            "websiteId": "test-website-123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/leads",
            json=lead_data,
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response
        assert data.get("success") == True, "Should return success=True"
        assert "contact_id" in data, "Should return contact_id"
        assert data.get("action") in ["created", "updated"], "Action should be created or updated"
        
        contact_id = data["contact_id"]
        print(f"✓ Lead submitted successfully, contact_id: {contact_id}, action: {data['action']}")
        
        # Verify lead appears in GET /api/leads
        get_response = requests.get(
            f"{BASE_URL}/api/leads",
            headers=headers
        )
        assert get_response.status_code == 200
        leads = get_response.json()
        
        # Find our lead
        our_lead = next((l for l in leads if l.get("id") == contact_id), None)
        assert our_lead is not None, "Created lead should appear in leads list"
        assert our_lead["email"] == lead_data["email"], "Email should match"
        assert our_lead["source"] == "website", "Source should be 'website'"
        
        print(f"✓ Lead verified in CRM contacts")
        
        return contact_id


class TestLeadCRMConvert:
    """Test Lead CRM convert endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "x-workspace-id": WORKSPACE_ID
        }
    
    def test_convert_lead_to_customer(self, headers):
        """POST /api/leads/{contact_id}/convert - Convert lead to customer"""
        # First create a lead
        unique_id = str(uuid.uuid4())[:8]
        lead_data = {
            "name": f"TEST_Convert Lead {unique_id}",
            "email": f"test_convert_{unique_id}@example.com",
            "phone": "+1234567890",
            "company": "Convert Test Company",
            "message": "Convert me to customer"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/leads",
            json=lead_data,
            headers=headers
        )
        assert create_response.status_code == 200
        contact_id = create_response.json().get("contact_id")
        
        # Convert to customer
        convert_response = requests.post(
            f"{BASE_URL}/api/leads/{contact_id}/convert",
            headers=headers
        )
        assert convert_response.status_code == 200, f"Failed: {convert_response.text}"
        data = convert_response.json()
        
        assert data.get("success") == True, "Should return success=True"
        assert "message" in data, "Should have message"
        
        print(f"✓ Lead {contact_id} converted to customer successfully")


class TestLeadCRMAnalytics:
    """Test Lead CRM analytics endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "x-workspace-id": WORKSPACE_ID
        }
    
    def test_get_lead_analytics(self, headers):
        """GET /api/leads/analytics - Get lead analytics"""
        response = requests.get(
            f"{BASE_URL}/api/leads/analytics",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "bySource" in data, "Missing bySource"
        assert "byStatus" in data, "Missing byStatus"
        assert "byStage" in data, "Missing byStage"
        assert "totalLeads" in data, "Missing totalLeads"
        assert "websiteLeads" in data, "Missing websiteLeads"
        assert "recentLeads" in data, "Missing recentLeads"
        
        print(f"✓ Lead analytics retrieved: Total={data['totalLeads']}, Website={data['websiteLeads']}")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "x-workspace-id": WORKSPACE_ID
        }
    
    def test_cleanup_test_data(self, headers):
        """Clean up TEST_ prefixed data"""
        # Get all invoices and delete TEST_ ones
        invoices_response = requests.get(f"{BASE_URL}/api/invoices", headers=headers)
        if invoices_response.status_code == 200:
            invoices = invoices_response.json()
            deleted_count = 0
            for invoice in invoices:
                if invoice.get("clientName", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/invoices/{invoice['id']}", headers=headers)
                    deleted_count += 1
            print(f"✓ Cleaned up {deleted_count} test invoices")
        
        # Note: Contacts cleanup would require a delete endpoint
        print("✓ Cleanup completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
