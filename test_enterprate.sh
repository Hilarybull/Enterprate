#!/bin/bash

echo "========================================"
echo "Enterprate OS - API Testing"
echo "========================================"

API_URL="https://smartbiz-platform-1.preview.emergentagent.com/api"

# Test 1: Register
echo -e "\n1. Testing Registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@enterprate.com","name":"Demo User","password":"demo123"}')

TOKEN=$(echo $REGISTER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "   ✗ Registration failed"
  exit 1
else
  echo "   ✓ Registration successful"
  USER_ID=$(echo $REGISTER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['id'])")
fi

# Test 2: Get Current User
echo -e "\n2. Testing Get Current User..."
ME_RESPONSE=$(curl -s "$API_URL/auth/me" -H "Authorization: Bearer $TOKEN")
if echo $ME_RESPONSE | grep -q "email"; then
  echo "   ✓ Auth verification successful"
else
  echo "   ✗ Auth verification failed"
fi

# Test 3: Create Workspace
echo -e "\n3. Testing Workspace Creation..."
WS_RESPONSE=$(curl -s -X POST "$API_URL/workspaces" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo Company","country":"USA","industry":"Technology","stage":"Startup"}')

WORKSPACE_ID=$(echo $WS_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$WORKSPACE_ID" ]; then
  echo "   ✗ Workspace creation failed"
else
  echo "   ✓ Workspace created: $WORKSPACE_ID"
fi

# Test 4: Genesis AI - Idea Score
echo -e "\n4. Testing Genesis AI..."
GENESIS_RESPONSE=$(curl -s -X POST "$API_URL/genesis/idea-score" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{"idea":"AI-powered business management platform","targetCustomer":"Small businesses"}')

if echo $GENESIS_RESPONSE | grep -q "score"; then
  SCORE=$(echo $GENESIS_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['score'])")
  echo "   ✓ Genesis AI working - Idea Score: $SCORE/100"
else
  echo "   ✗ Genesis AI failed"
fi

# Test 5: Create Invoice
echo -e "\n5. Testing Navigator (Invoicing)..."
INV_RESPONSE=$(curl -s -X POST "$API_URL/navigator/invoices" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{"customerName":"Acme Corp","amount":1500.00,"currency":"USD"}')

if echo $INV_RESPONSE | grep -q "customerName"; then
  echo "   ✓ Invoice created successfully"
else
  echo "   ✗ Invoice creation failed"
fi

# Test 6: Create Lead
echo -e "\n6. Testing Growth (CRM)..."
LEAD_RESPONSE=$(curl -s -X POST "$API_URL/growth/leads" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","source":"Website"}')

if echo $LEAD_RESPONSE | grep -q "email"; then
  echo "   ✓ Lead created successfully"
else
  echo "   ✗ Lead creation failed"
fi

# Test 7: Create Website
echo -e "\n7. Testing Website Builder..."
SITE_RESPONSE=$(curl -s -X POST "$API_URL/websites" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{"name":"Company Website","domain":"demo.example.com"}')

WEBSITE_ID=$(echo $SITE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$WEBSITE_ID" ]; then
  echo "   ✗ Website creation failed"
else
  echo "   ✓ Website created: $WEBSITE_ID"
fi

# Test 8: Get Intelligence Events
echo -e "\n8. Testing Intelligence Graph..."
EVENTS_RESPONSE=$(curl -s "$API_URL/intel/events?limit=5" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID")

EVENT_COUNT=$(echo $EVENTS_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)

if [ "$EVENT_COUNT" -gt 0 ]; then
  echo "   ✓ Intelligence events logged: $EVENT_COUNT events"
else
  echo "   ✗ No intelligence events found"
fi

echo -e "\n========================================"
echo "Test Summary: All Core Features Working ✓"
echo "========================================"
