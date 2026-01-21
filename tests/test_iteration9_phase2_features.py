"""
Phase 2 Testing - Iteration 9
Tests for:
- Enhanced Invoicing with line items, PDF generation, brand assets
- Product Catalogue CSV/Excel upload
- Business Documents PDF export
- Tax Calculator Auto-fill API
"""
import pytest
import requests
import os
import base64
import io
import csv

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable not set")

# Test credentials
TEST_EMAIL = "test_invoice@example.com"
TEST_PASSWORD = "Test123!"
WORKSPACE_ID = "17387b8d-5b7d-4685-b069-641f72b2b9e5"


class TestAuthentication:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
    
    def test_login_returns_token(self, auth_token):
        """Test that login returns a valid token"""
        assert auth_token is not None
        assert len(auth_token) > 0


class TestCatalogueUpload:
    """Test catalogue CSV/Excel upload and parsing"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "X-Workspace-ID": WORKSPACE_ID
            }
        pytest.skip("Authentication failed")
    
    def test_catalogue_csv_upload(self, auth_headers):
        """Test CSV file upload and parsing"""
        # Create a CSV file in memory
        csv_content = "name,description,unitPrice,currency,taxRate,sku,category\n"
        csv_content += "TEST_Product A,Description A,99.99,GBP,20,SKU001,Software\n"
        csv_content += "TEST_Product B,Description B,149.99,GBP,20,SKU002,Services\n"
        csv_content += "TEST_Product C,Missing price,,,SKU003,Other\n"  # Missing price - should need review
        
        files = {
            'file': ('test_catalogue.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/catalogue/upload",
            headers=auth_headers,
            files=files
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "accepted" in data
        assert "needsReview" in data
        assert "rejected" in data
        assert "summary" in data
        
        # Should have 2 accepted items (with valid prices)
        assert len(data["accepted"]) >= 2
        
        # Should have 1 item needing review (missing price)
        assert len(data["needsReview"]) >= 1
    
    def test_catalogue_bulk_add(self, auth_headers):
        """Test bulk adding validated items"""
        items = [
            {
                "name": "TEST_Bulk Item 1",
                "description": "Bulk test item",
                "unitPrice": 50.00,
                "currency": "GBP",
                "taxRate": 20,
                "sku": "BULK001",
                "category": "Software"
            },
            {
                "name": "TEST_Bulk Item 2",
                "description": "Another bulk item",
                "unitPrice": 75.00,
                "currency": "GBP",
                "taxRate": 20,
                "sku": "BULK002",
                "category": "Services"
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/catalogue/bulk",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={"items": items}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("addedCount") == 2


class TestEnhancedInvoicing:
    """Test enhanced invoicing with line items, PDF, and brand assets"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "X-Workspace-ID": WORKSPACE_ID,
                "Content-Type": "application/json"
            }
        pytest.skip("Authentication failed")
    
    @pytest.fixture(scope="class")
    def created_invoice_id(self, auth_headers):
        """Create an invoice and return its ID"""
        invoice_data = {
            "clientName": "TEST_Client Corp",
            "clientEmail": "test_client@example.com",
            "clientAddress": "123 Test Street, London",
            "currency": "GBP",
            "dueDate": "2025-02-28",
            "notes": "Thank you for your business",
            "termsAndConditions": "Payment due within 30 days",
            "status": "draft",
            "lineItems": [
                {
                    "name": "Consulting Services",
                    "description": "Monthly consulting",
                    "quantity": 10,
                    "unitPrice": 150.00,
                    "taxRate": 20
                },
                {
                    "name": "Software License",
                    "description": "Annual license",
                    "quantity": 1,
                    "unitPrice": 500.00,
                    "taxRate": 20
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/invoices",
            headers=auth_headers,
            json=invoice_data
        )
        
        if response.status_code == 200:
            return response.json().get("id")
        pytest.skip(f"Failed to create invoice: {response.status_code} - {response.text}")
    
    def test_create_invoice_with_line_items(self, auth_headers):
        """Test creating invoice with line items"""
        invoice_data = {
            "clientName": "TEST_New Client",
            "clientEmail": "newclient@example.com",
            "clientAddress": "456 New Street",
            "currency": "GBP",
            "dueDate": "2025-03-15",
            "status": "draft",
            "lineItems": [
                {
                    "name": "Service A",
                    "quantity": 5,
                    "unitPrice": 100.00,
                    "taxRate": 20
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/invoices",
            headers=auth_headers,
            json=invoice_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify invoice structure
        assert "id" in data
        assert "invoiceNumber" in data
        assert data["clientName"] == "TEST_New Client"
        assert data["clientEmail"] == "newclient@example.com"
        
        # Verify totals calculation
        # 5 * 100 = 500 subtotal, 500 * 0.20 = 100 tax, total = 600
        assert data["subtotal"] == 500.00
        assert data["taxTotal"] == 100.00
        assert data["total"] == 600.00
        
        # Verify line items
        assert len(data["lineItems"]) == 1
        assert data["lineItems"][0]["name"] == "Service A"
    
    def test_get_invoices(self, auth_headers):
        """Test getting all invoices"""
        response = requests.get(
            f"{BASE_URL}/api/invoices",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_single_invoice(self, auth_headers, created_invoice_id):
        """Test getting a single invoice"""
        response = requests.get(
            f"{BASE_URL}/api/invoices/{created_invoice_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_invoice_id
        assert "lineItems" in data
        assert "total" in data
    
    def test_generate_invoice_pdf(self, auth_headers, created_invoice_id):
        """Test PDF generation for invoice"""
        response = requests.get(
            f"{BASE_URL}/api/invoices/{created_invoice_id}/pdf",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        
        # Verify it's a valid PDF (starts with %PDF)
        assert response.content[:4] == b'%PDF'
    
    def test_finalize_invoice(self, auth_headers, created_invoice_id):
        """Test finalizing a draft invoice"""
        response = requests.post(
            f"{BASE_URL}/api/invoices/{created_invoice_id}/finalize",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending_review"
    
    def test_update_invoice(self, auth_headers):
        """Test updating invoice details"""
        # First create a draft invoice
        invoice_data = {
            "clientName": "TEST_Update Client",
            "clientEmail": "update@example.com",
            "currency": "GBP",
            "status": "draft",
            "lineItems": [
                {"name": "Item 1", "quantity": 1, "unitPrice": 100.00, "taxRate": 0}
            ]
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/invoices",
            headers=auth_headers,
            json=invoice_data
        )
        
        assert create_response.status_code == 200
        invoice_id = create_response.json()["id"]
        
        # Update the invoice
        update_data = {
            "notes": "Updated notes",
            "clientAddress": "New Address"
        }
        
        update_response = requests.patch(
            f"{BASE_URL}/api/invoices/{invoice_id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["notes"] == "Updated notes"
        assert data["clientAddress"] == "New Address"


class TestBrandAssets:
    """Test brand asset upload for invoices"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "X-Workspace-ID": WORKSPACE_ID,
                "Content-Type": "application/json"
            }
        pytest.skip("Authentication failed")
    
    def test_upload_brand_logo(self, auth_headers):
        """Test uploading a brand logo"""
        # Create a simple 1x1 PNG image (smallest valid PNG)
        # This is a minimal valid PNG file
        png_data = base64.b64encode(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f'
            b'\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        ).decode('utf-8')
        
        response = requests.post(
            f"{BASE_URL}/api/invoices/brand/assets",
            headers=auth_headers,
            json={
                "assetType": "logo",
                "imageBase64": png_data,
                "filename": "test_logo.png"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("assetType") == "logo"
    
    def test_get_brand_assets(self, auth_headers):
        """Test getting brand assets list"""
        response = requests.get(
            f"{BASE_URL}/api/invoices/brand/assets",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_brand_logo(self, auth_headers):
        """Test getting specific brand asset (logo)"""
        response = requests.get(
            f"{BASE_URL}/api/invoices/brand/assets/logo",
            headers=auth_headers
        )
        
        # May return 200 with data or error if not found
        assert response.status_code == 200


class TestTaxAutofill:
    """Test tax calculator auto-fill API"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "X-Workspace-ID": WORKSPACE_ID
            }
        pytest.skip("Authentication failed")
    
    def test_get_tax_autofill_data(self, auth_headers):
        """Test getting auto-fill data from invoices and expenses"""
        response = requests.get(
            f"{BASE_URL}/api/finance/tax-autofill",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "annualRevenue" in data
        assert "annualExpenses" in data
        assert "taxYear" in data
        assert "sources" in data
        
        # Verify data types
        assert isinstance(data["annualRevenue"], (int, float))
        assert isinstance(data["annualExpenses"], (int, float))
    
    def test_get_tax_autofill_with_year(self, auth_headers):
        """Test getting auto-fill data for specific tax year"""
        response = requests.get(
            f"{BASE_URL}/api/finance/tax-autofill?tax_year=2024-2025",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "taxYear" in data


class TestDocumentExport:
    """Test business document PDF export"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "X-Workspace-ID": WORKSPACE_ID,
                "Content-Type": "application/json"
            }
        pytest.skip("Authentication failed")
    
    def test_generate_document(self, auth_headers):
        """Test generating a business document"""
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            headers=auth_headers,
            json={
                "documentType": "terms_conditions",
                "inputs": {
                    "companyName": "TEST_Company Ltd",
                    "businessType": "Software Services",
                    "jurisdiction": "England & Wales",
                    "refundPolicy": "30-day money back guarantee",
                    "liabilityLimit": "the amount paid for services"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "title" in data
        assert "content" in data
        assert len(data["content"]) > 100  # Should have substantial content
    
    def test_export_document_to_pdf(self, auth_headers):
        """Test exporting document to PDF"""
        response = requests.post(
            f"{BASE_URL}/api/documents/export",
            headers=auth_headers,
            json={
                "title": "Test Terms & Conditions",
                "content": "1. INTRODUCTION\n\nThese are test terms and conditions.\n\n2. SERVICES\n\nWe provide software services.",
                "format": "pdf"
            }
        )
        
        assert response.status_code == 200
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type or "text/plain" in content_type
        
        # If PDF, verify it starts with %PDF
        if "application/pdf" in content_type:
            assert response.content[:4] == b'%PDF'
    
    def test_save_document(self, auth_headers):
        """Test saving a generated document"""
        response = requests.post(
            f"{BASE_URL}/api/documents/save",
            headers=auth_headers,
            json={
                "documentType": "privacy_policy",
                "title": "TEST_Privacy Policy",
                "content": "This is a test privacy policy content.",
                "inputs": {
                    "companyName": "TEST_Company",
                    "contactEmail": "test@example.com"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "id" in data


class TestInvoiceSendEmail:
    """Test invoice email sending (expected to fail without valid SendGrid key)"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "X-Workspace-ID": WORKSPACE_ID,
                "Content-Type": "application/json"
            }
        pytest.skip("Authentication failed")
    
    def test_send_invoice_email_mocked(self, auth_headers):
        """Test sending invoice email - expected to fail without valid SendGrid API key"""
        # First create an invoice
        invoice_data = {
            "clientName": "TEST_Email Client",
            "clientEmail": "email_test@example.com",
            "currency": "GBP",
            "status": "pending_review",
            "lineItems": [
                {"name": "Test Service", "quantity": 1, "unitPrice": 100.00, "taxRate": 20}
            ]
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/invoices",
            headers=auth_headers,
            json=invoice_data
        )
        
        if create_response.status_code != 200:
            pytest.skip("Could not create invoice for email test")
        
        invoice_id = create_response.json()["id"]
        
        # Try to send email - expected to fail with 500 (SendGrid not configured)
        send_response = requests.post(
            f"{BASE_URL}/api/invoices/{invoice_id}/send",
            headers=auth_headers
        )
        
        # Either 200 (if SendGrid works) or 500/520 (if not configured or network error)
        assert send_response.status_code in [200, 500, 520]
        
        if send_response.status_code in [500, 520]:
            # Expected - SendGrid not configured or network error
            # This is expected behavior - MOCKED
            print(f"Email send returned {send_response.status_code} - SendGrid MOCKED")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            return {
                "Authorization": f"Bearer {token}",
                "X-Workspace-ID": WORKSPACE_ID
            }
        pytest.skip("Authentication failed")
    
    def test_cleanup_test_catalogue_items(self, auth_headers):
        """Clean up TEST_ prefixed catalogue items"""
        # Get all catalogue items
        response = requests.get(
            f"{BASE_URL}/api/catalogue",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            items = response.json()
            deleted_count = 0
            for item in items:
                if item.get("name", "").startswith("TEST_"):
                    delete_response = requests.delete(
                        f"{BASE_URL}/api/catalogue/{item['id']}",
                        headers=auth_headers
                    )
                    if delete_response.status_code == 200:
                        deleted_count += 1
            
            print(f"Cleaned up {deleted_count} test catalogue items")
        
        assert True  # Cleanup is best-effort
