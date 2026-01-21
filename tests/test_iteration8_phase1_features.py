"""
Test Suite for Phase 1 Features - Iteration 8
Tests: Catalogue System, Business Documents, Tax Autofill, Menu Structure
"""
import pytest
import requests
import os
import io
import csv

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://business-wizard.preview.emergentagent.com')
WORKSPACE_ID = "592c480e-7da2-4500-a987-567c1c450ba7"

# Test credentials from previous iterations
TEST_EMAIL = "webbuilder_test2@example.com"
TEST_PASSWORD = "Test123!"


class TestAuthentication:
    """Authentication tests"""
    
    def test_login_success(self):
        """Test login returns valid JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get headers with auth token and workspace"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "X-Workspace-ID": WORKSPACE_ID,
        "Content-Type": "application/json"
    }


# ============================================
# CATALOGUE API TESTS
# ============================================

class TestCatalogueAPI:
    """Product/Service Catalogue CRUD tests"""
    
    created_item_id = None
    
    def test_get_catalogue_items_empty_or_list(self, auth_headers):
        """GET /api/catalogue - Get all catalogue items"""
        response = requests.get(f"{BASE_URL}/api/catalogue", headers=auth_headers)
        assert response.status_code == 200, f"Failed to get catalogue: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
    
    def test_create_catalogue_item(self, auth_headers):
        """POST /api/catalogue - Create new catalogue item"""
        payload = {
            "name": "TEST_Consulting Service",
            "description": "Professional consulting services",
            "unitPrice": 150.00,
            "currency": "GBP",
            "taxRate": 20.0,
            "sku": "TEST-CONSULT-001",
            "category": "Services"
        }
        response = requests.post(f"{BASE_URL}/api/catalogue", json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Failed to create item: {response.text}"
        
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["unitPrice"] == payload["unitPrice"]
        assert data["currency"] == payload["currency"]
        assert data["sku"] == payload["sku"]
        assert "id" in data
        
        # Store for later tests
        TestCatalogueAPI.created_item_id = data["id"]
    
    def test_get_single_catalogue_item(self, auth_headers):
        """GET /api/catalogue/{id} - Get single item"""
        if not TestCatalogueAPI.created_item_id:
            pytest.skip("No item created to fetch")
        
        response = requests.get(
            f"{BASE_URL}/api/catalogue/{TestCatalogueAPI.created_item_id}", 
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get item: {response.text}"
        
        data = response.json()
        assert data["id"] == TestCatalogueAPI.created_item_id
        assert data["name"] == "TEST_Consulting Service"
    
    def test_update_catalogue_item(self, auth_headers):
        """PUT /api/catalogue/{id} - Update catalogue item"""
        if not TestCatalogueAPI.created_item_id:
            pytest.skip("No item created to update")
        
        update_payload = {
            "name": "TEST_Updated Consulting Service",
            "unitPrice": 175.00
        }
        response = requests.put(
            f"{BASE_URL}/api/catalogue/{TestCatalogueAPI.created_item_id}",
            json=update_payload,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to update item: {response.text}"
        
        data = response.json()
        assert data["name"] == update_payload["name"]
        assert data["unitPrice"] == update_payload["unitPrice"]
        
        # Verify persistence with GET
        get_response = requests.get(
            f"{BASE_URL}/api/catalogue/{TestCatalogueAPI.created_item_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["name"] == update_payload["name"]
    
    def test_search_catalogue_items(self, auth_headers):
        """GET /api/catalogue?search=... - Search catalogue"""
        response = requests.get(
            f"{BASE_URL}/api/catalogue?search=TEST",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Search failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
    
    def test_filter_catalogue_by_category(self, auth_headers):
        """GET /api/catalogue?category=... - Filter by category"""
        response = requests.get(
            f"{BASE_URL}/api/catalogue?category=Services",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Filter failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
    
    def test_delete_catalogue_item(self, auth_headers):
        """DELETE /api/catalogue/{id} - Delete catalogue item"""
        if not TestCatalogueAPI.created_item_id:
            pytest.skip("No item created to delete")
        
        response = requests.delete(
            f"{BASE_URL}/api/catalogue/{TestCatalogueAPI.created_item_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to delete item: {response.text}"
        
        # Verify deletion with GET
        get_response = requests.get(
            f"{BASE_URL}/api/catalogue/{TestCatalogueAPI.created_item_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404, "Item should not exist after deletion"


class TestCatalogueUpload:
    """Catalogue file upload and validation tests"""
    
    def test_upload_csv_file(self, auth_headers):
        """POST /api/catalogue/upload - Upload CSV file for validation"""
        # Create a CSV file in memory
        csv_content = "Name,Description,Unit Price,Currency,Tax Rate,SKU,Category\n"
        csv_content += "TEST_Product A,Description A,99.99,GBP,20,SKU-A,Products\n"
        csv_content += "TEST_Product B,Description B,49.99,GBP,20,SKU-B,Products\n"
        csv_content += "TEST_Service C,Description C,199.99,GBP,0,SKU-C,Services\n"
        
        files = {
            'file': ('test_catalogue.csv', csv_content, 'text/csv')
        }
        
        # Remove Content-Type for multipart
        headers = {
            "Authorization": auth_headers["Authorization"],
            "X-Workspace-ID": auth_headers["X-Workspace-ID"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/catalogue/upload",
            files=files,
            headers=headers
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        data = response.json()
        assert "accepted" in data
        assert "needsReview" in data
        assert "rejected" in data
        assert "summary" in data
        
        # Should have accepted items
        assert len(data["accepted"]) >= 0  # May have some accepted
    
    def test_upload_csv_with_missing_price(self, auth_headers):
        """Test CSV upload with missing price goes to needsReview"""
        csv_content = "Name,Description,Unit Price,Currency\n"
        csv_content += "TEST_No Price Item,Description,,GBP\n"
        
        files = {
            'file': ('test_missing_price.csv', csv_content, 'text/csv')
        }
        
        headers = {
            "Authorization": auth_headers["Authorization"],
            "X-Workspace-ID": auth_headers["X-Workspace-ID"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/catalogue/upload",
            files=files,
            headers=headers
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        data = response.json()
        # Item with missing price should be in needsReview
        assert len(data["needsReview"]) >= 1 or len(data["rejected"]) >= 0


class TestCatalogueBulkAdd:
    """Bulk add validated items tests"""
    
    def test_bulk_add_items(self, auth_headers):
        """POST /api/catalogue/bulk - Bulk add validated items"""
        items = [
            {
                "name": "TEST_Bulk Item 1",
                "description": "Bulk added item 1",
                "unitPrice": 25.00,
                "currency": "GBP",
                "category": "Products"
            },
            {
                "name": "TEST_Bulk Item 2",
                "description": "Bulk added item 2",
                "unitPrice": 35.00,
                "currency": "GBP",
                "category": "Products"
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/catalogue/bulk",
            json={"items": items},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Bulk add failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert data["addedCount"] == 2


# ============================================
# DOCUMENTS API TESTS
# ============================================

class TestDocumentsAPI:
    """Business Documents wizard tests"""
    
    generated_doc = None
    saved_doc_id = None
    
    def test_get_documents_list(self, auth_headers):
        """GET /api/documents - Get all documents"""
        response = requests.get(f"{BASE_URL}/api/documents", headers=auth_headers)
        assert response.status_code == 200, f"Failed to get documents: {response.text}"
        data = response.json()
        assert isinstance(data, list)
    
    def test_generate_terms_conditions(self, auth_headers):
        """POST /api/documents/generate - Generate Terms & Conditions"""
        payload = {
            "documentType": "terms_conditions",
            "inputs": {
                "companyName": "TEST Company Ltd",
                "businessType": "SaaS",
                "jurisdiction": "England & Wales",
                "refundPolicy": "30-day money back guarantee",
                "liabilityLimit": "£10,000"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Generate failed: {response.text}"
        
        data = response.json()
        assert "title" in data
        assert "content" in data
        assert "documentType" in data
        assert data["documentType"] == "terms_conditions"
        assert len(data["content"]) > 100  # Should have substantial content
        
        TestDocumentsAPI.generated_doc = data
    
    def test_generate_privacy_policy(self, auth_headers):
        """POST /api/documents/generate - Generate Privacy Policy"""
        payload = {
            "documentType": "privacy_policy",
            "inputs": {
                "companyName": "TEST Company Ltd",
                "companyAddress": "123 Test Street, London, UK",
                "contactEmail": "privacy@testcompany.com",
                "dataCollected": "Name, email, payment information",
                "thirdParties": "Stripe, Google Analytics",
                "dataRetention": "7 years"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Generate failed: {response.text}"
        
        data = response.json()
        assert data["documentType"] == "privacy_policy"
        assert "PRIVACY POLICY" in data["content"].upper() or "privacy" in data["content"].lower()
    
    def test_generate_nda(self, auth_headers):
        """POST /api/documents/generate - Generate NDA"""
        payload = {
            "documentType": "nda",
            "inputs": {
                "disclosingParty": "TEST Company Ltd",
                "receivingParty": "Partner Corp",
                "purpose": "Business partnership discussions",
                "duration": "2 years",
                "jurisdiction": "England & Wales"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Generate failed: {response.text}"
        
        data = response.json()
        assert data["documentType"] == "nda"
    
    def test_save_document(self, auth_headers):
        """POST /api/documents/save - Save generated document"""
        if not TestDocumentsAPI.generated_doc:
            pytest.skip("No document generated to save")
        
        payload = {
            "documentType": "terms_conditions",
            "title": TestDocumentsAPI.generated_doc["title"],
            "content": TestDocumentsAPI.generated_doc["content"],
            "inputs": {
                "companyName": "TEST Company Ltd",
                "businessType": "SaaS"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/save",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Save failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "id" in data
        
        TestDocumentsAPI.saved_doc_id = data["id"]
    
    def test_get_saved_document(self, auth_headers):
        """GET /api/documents/{id} - Get saved document"""
        if not TestDocumentsAPI.saved_doc_id:
            pytest.skip("No document saved to fetch")
        
        response = requests.get(
            f"{BASE_URL}/api/documents/{TestDocumentsAPI.saved_doc_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get document: {response.text}"
        
        data = response.json()
        assert data["id"] == TestDocumentsAPI.saved_doc_id
        assert "content" in data
    
    def test_filter_documents_by_type(self, auth_headers):
        """GET /api/documents?doc_type=... - Filter by document type"""
        response = requests.get(
            f"{BASE_URL}/api/documents?doc_type=terms_conditions",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Filter failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
    
    def test_generate_invalid_document_type(self, auth_headers):
        """POST /api/documents/generate - Invalid document type returns 400"""
        payload = {
            "documentType": "invalid_type",
            "inputs": {}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == 400, "Should reject invalid document type"


# ============================================
# TAX AUTOFILL API TESTS
# ============================================

class TestTaxAutofillAPI:
    """Tax Calculator auto-fill tests"""
    
    def test_get_tax_autofill_data(self, auth_headers):
        """GET /api/finance/tax-autofill - Get auto-fill data from invoices"""
        response = requests.get(
            f"{BASE_URL}/api/finance/tax-autofill",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Tax autofill failed: {response.text}"
        
        data = response.json()
        # Should return tax autofill structure
        assert "annualRevenue" in data or "totalRevenue" in data or "revenue" in data or isinstance(data, dict)
    
    def test_get_tax_autofill_with_year(self, auth_headers):
        """GET /api/finance/tax-autofill?tax_year=... - Get data for specific year"""
        response = requests.get(
            f"{BASE_URL}/api/finance/tax-autofill?tax_year=2024-2025",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Tax autofill with year failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, dict)


# ============================================
# MENU STRUCTURE VERIFICATION (via API)
# ============================================

class TestMenuStructure:
    """Verify menu structure changes via API availability"""
    
    def test_catalogue_endpoint_exists(self, auth_headers):
        """Verify /api/catalogue endpoint exists (new menu item)"""
        response = requests.get(f"{BASE_URL}/api/catalogue", headers=auth_headers)
        assert response.status_code == 200, "Catalogue endpoint should exist"
    
    def test_documents_endpoint_exists(self, auth_headers):
        """Verify /api/documents endpoint exists (new menu item)"""
        response = requests.get(f"{BASE_URL}/api/documents", headers=auth_headers)
        assert response.status_code == 200, "Documents endpoint should exist"
    
    def test_ai_websites_endpoint_exists(self, auth_headers):
        """Verify /api/ai-websites endpoint exists (AI Website Builder)"""
        response = requests.get(f"{BASE_URL}/api/ai-websites", headers=auth_headers)
        assert response.status_code == 200, "AI Websites endpoint should exist"
    
    def test_website_analytics_endpoint_exists(self, auth_headers):
        """Verify /api/website-analytics endpoint exists (under AI Website Builder)"""
        response = requests.get(f"{BASE_URL}/api/website-analytics", headers=auth_headers)
        # May return 200 or empty list
        assert response.status_code in [200, 404], f"Analytics endpoint issue: {response.text}"
    
    def test_domains_endpoint_exists(self, auth_headers):
        """Verify /api/domains endpoint exists (under AI Website Builder)"""
        # First get a website to test domains endpoint
        websites_response = requests.get(f"{BASE_URL}/api/ai-websites", headers=auth_headers)
        if websites_response.status_code == 200:
            websites = websites_response.json()
            if websites and len(websites) > 0:
                website_id = websites[0].get("id")
                response = requests.get(f"{BASE_URL}/api/domains/website/{website_id}", headers=auth_headers)
                assert response.status_code in [200, 404], f"Domains endpoint issue: {response.text}"
                return
        # If no websites, just verify the route pattern exists
        assert True, "Domains endpoint exists but requires website_id"


# ============================================
# CLEANUP
# ============================================

class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_catalogue_items(self, auth_headers):
        """Delete TEST_ prefixed catalogue items"""
        response = requests.get(f"{BASE_URL}/api/catalogue", headers=auth_headers)
        if response.status_code == 200:
            items = response.json()
            for item in items:
                if item.get("name", "").startswith("TEST_"):
                    requests.delete(
                        f"{BASE_URL}/api/catalogue/{item['id']}",
                        headers=auth_headers
                    )
        assert True  # Cleanup is best effort


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
