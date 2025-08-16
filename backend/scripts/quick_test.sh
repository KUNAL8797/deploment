#!/bin/bash

# Quick API Test Script
# Tests basic endpoints without authentication

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get API URL
API_URL=${1:-$API_URL}

if [ -z "$API_URL" ]; then
    echo -e "${RED}Error: API URL not provided${NC}"
    echo "Usage: ./quick_test.sh <api_url>"
    echo "   or: export API_URL=<api_url> && ./quick_test.sh"
    exit 1
fi

# Remove trailing slash
API_URL=${API_URL%/}

echo -e "${YELLOW}Testing API at: $API_URL${NC}"
echo "=================================="

# Test 1: Root endpoint
echo -n "Testing root endpoint... "
if curl -s -f "$API_URL/" > /dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
    # Get version info
    VERSION=$(curl -s "$API_URL/" | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'Unknown'))" 2>/dev/null || echo "Unknown")
    echo "   Version: $VERSION"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# Test 2: Health endpoint
echo -n "Testing health endpoint... "
if curl -s -f "$API_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
    # Get health status
    STATUS=$(curl -s "$API_URL/health" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'Unknown'))" 2>/dev/null || echo "Unknown")
    echo "   Status: $STATUS"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# Test 3: API Documentation (if available)
echo -n "Testing API docs... "
if curl -s -f "$API_URL/docs" > /dev/null; then
    echo -e "${GREEN}✅ AVAILABLE${NC}"
else
    echo -e "${YELLOW}⚠️ NOT AVAILABLE (normal for production)${NC}"
fi

# Test 4: CORS preflight
echo -n "Testing CORS... "
if curl -s -f -X OPTIONS "$API_URL/" \
    -H "Origin: https://example.com" \
    -H "Access-Control-Request-Method: GET" > /dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${YELLOW}⚠️ CORS may not be configured${NC}"
fi

# Test 5: Response time
echo -n "Testing response time... "
RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "$API_URL/health")
if (( $(echo "$RESPONSE_TIME < 5.0" | bc -l) )); then
    echo -e "${GREEN}✅ FAST (${RESPONSE_TIME}s)${NC}"
elif (( $(echo "$RESPONSE_TIME < 10.0" | bc -l) )); then
    echo -e "${YELLOW}⚠️ SLOW (${RESPONSE_TIME}s)${NC}"
else
    echo -e "${RED}❌ VERY SLOW (${RESPONSE_TIME}s)${NC}"
fi

echo "=================================="
echo -e "${GREEN}Quick test completed!${NC}"
echo ""
echo "For comprehensive testing, run:"
echo "python scripts/test_api.py $API_URL"