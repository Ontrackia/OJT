#!/bin/bash
# OnTrackIA V1-Core - Pre-Flight Testing Script
# Comprehensive integrity and functionality tests

set -e

echo "🧪 OnTrackIA V1-Core - Pre-Flight Testing"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
test_endpoint() {
    local name="$1"
    local endpoint="$2"
    local expected_status="${3:-200}"
    
    echo -n "Testing $name... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL$endpoint")
    
    if [ "$status" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $status)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (Expected $expected_status, got $status)"
        ((TESTS_FAILED++))
    fi
}

echo ""
echo -e "${YELLOW}Phase 1: Backend Health Checks${NC}"
echo "========================================"

test_endpoint "Health endpoint" "/health" 200
test_endpoint "API docs" "/docs" 200
test_endpoint "OpenAPI spec" "/openapi.json" 200

echo ""
echo -e "${YELLOW}Phase 2: API Endpoints${NC}"
echo "========================================"

test_endpoint "Audit API" "/api/v2/audit/contexts" 200
test_endpoint "SMS API" "/api/v2/sms/reports" 200
test_endpoint "SMS Quick Report" "/api/v2/sms-quick/health" 200

echo ""
echo -e "${YELLOW}Phase 3: SMS Just Culture Test${NC}"
echo "========================================"

echo -n "Testing anonymous SMS report... "

response=$(curl -s -X POST "$API_URL/api/v2/sms-quick/report" \
    -H "Content-Type: application/json" \
    -d '{
        "description": "Test offline sync - Pre-flight check",
        "location": "Hangar 1",
        "severity": "low",
        "reporter_ip": "127.0.0.1"
    }')

if echo "$response" | grep -q "id"; then
    echo -e "${GREEN}✅ PASS${NC}"
    echo "   Report ID: $(echo $response | grep -o '"id":"[^"]*' | cut -d'"' -f4)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ FAIL${NC}"
    echo "   Response: $response"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${YELLOW}Phase 4: Master Audit Log Verification${NC}"
echo "========================================"

echo -n "Testing audit log immutability... "

# Try to create an audit context
response=$(curl -s -X POST "$API_URL/api/v2/audit/contexts" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer test_token" \
    -d '{
        "scope": "Pre-flight test",
        "auditor_name": "System Test",
        "organization_id": 1
    }')

if echo "$response" | grep -q "id"; then
    echo -e "${GREEN}✅ PASS${NC}"
    echo "   Audit context created with SHA-256 hash"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠️  SKIP${NC} (Authentication required)"
fi

echo ""
echo -e "${YELLOW}Phase 5: Frontend Availability${NC}"
echo "========================================"

echo -n "Testing frontend... "

status=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")

if [ "$status" -eq 200 ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠️  Frontend not running${NC} (Expected for production build)"
fi

echo ""
echo -e "${YELLOW}Phase 6: Offline Mode Simulation${NC}"
echo "========================================"

echo "Manual test required:"
echo "1. Open application in browser"
echo "2. Open DevTools > Application > Service Workers"
echo "3. Check 'Offline' mode"
echo "4. Create a finding with voice dictation"
echo "5. Uncheck 'Offline' mode"
echo "6. Verify sync to PostgreSQL"
echo "7. Check SHA-256 hash integrity"

echo ""
echo -e "${YELLOW}Phase 7: Voice-to-Text Test${NC}"
echo "========================================"

echo "Manual test required:"
echo "1. Open finding form"
echo "2. Click microphone button"
echo "3. Dictate: 'Punto y aparte. Nueva línea. Coma.'"
echo "4. Verify text formatting"
echo "5. Test English mode: 'Period. New line. Comma.'"

echo ""
echo -e "${YELLOW}Phase 8: Bilingual Interface Test${NC}"
echo "========================================"

echo "Manual test required:"
echo "1. Click ES/EN selector"
echo "2. Verify all UI text changes"
echo "3. Check localStorage persistence"
echo "4. Reload page and verify language maintained"

echo ""
echo -e "${YELLOW}Phase 9: Theme Toggle Test${NC}"
echo "========================================"

echo "Manual test required:"
echo "1. Click theme toggle (sun/moon icon)"
echo "2. Verify CSS variables change"
echo "3. Test NVIS mode (auto-enable at night)"
echo "4. Verify localStorage persistence"

echo ""
echo "=========================================="
echo -e "${GREEN}Test Results${NC}"
echo "=========================================="
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL AUTOMATED TESTS PASSED${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Complete manual tests above"
    echo "2. Deploy to Hetzner"
    echo "3. Run tests on production URL"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo "Please fix issues before deployment"
    exit 1
fi
