#!/bin/bash

# Simple Frontend Test Script
# Tests basic frontend functionality without browser automation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get URLs
FRONTEND_URL=${1:-$FRONTEND_URL}
BACKEND_URL=${2:-$BACKEND_URL}

if [ -z "$FRONTEND_URL" ]; then
    echo -e "${RED}Error: Frontend URL not provided${NC}"
    echo "Usage: ./simple_test.sh <frontend_url> [backend_url]"
    echo "   or: export FRONTEND_URL=<url> && ./simple_test.sh"
    exit 1
fi

# Remove trailing slashes
FRONTEND_URL=${FRONTEND_URL%/}
BACKEND_URL=${BACKEND_URL%/}

echo -e "${BLUE}🧪 Testing Frontend Deployment${NC}"
echo -e "${BLUE}Frontend: $FRONTEND_URL${NC}"
if [ -n "$BACKEND_URL" ]; then
    echo -e "${BLUE}Backend: $BACKEND_URL${NC}"
fi
echo "=================================="

# Test 1: Frontend accessibility
echo -n "Testing frontend accessibility... "
if curl -s -f -I "$FRONTEND_URL" > /dev/null; then
    echo -e "${GREEN}✅ ACCESSIBLE${NC}"
    
    # Get response headers
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "$FRONTEND_URL")
    echo "   Status Code: $STATUS_CODE"
    echo "   Response Time: ${RESPONSE_TIME}s"
else
    echo -e "${RED}❌ NOT ACCESSIBLE${NC}"
fi

# Test 2: Content type
echo -n "Testing content type... "
CONTENT_TYPE=$(curl -s -I "$FRONTEND_URL" | grep -i "content-type" | cut -d' ' -f2- | tr -d '\r\n')
if [[ "$CONTENT_TYPE" == *"text/html"* ]]; then
    echo -e "${GREEN}✅ HTML CONTENT${NC}"
    echo "   Content-Type: $CONTENT_TYPE"
else
    echo -e "${YELLOW}⚠️ UNEXPECTED CONTENT TYPE${NC}"
    echo "   Content-Type: $CONTENT_TYPE"
fi

# Test 3: HTTPS
echo -n "Testing HTTPS... "
if [[ "$FRONTEND_URL" == https://* ]]; then
    echo -e "${GREEN}✅ HTTPS ENABLED${NC}"
else
    echo -e "${YELLOW}⚠️ HTTP ONLY${NC}"
fi

# Test 4: Basic HTML structure
echo -n "Testing HTML structure... "
HTML_CONTENT=$(curl -s "$FRONTEND_URL")
if [[ "$HTML_CONTENT" == *"<html"* ]] && [[ "$HTML_CONTENT" == *"</html>"* ]]; then
    echo -e "${GREEN}✅ VALID HTML${NC}"
    
    # Check for React app
    if [[ "$HTML_CONTENT" == *"id=\"root\""* ]]; then
        echo "   React root element found"
    fi
    
    # Check for title
    if [[ "$HTML_CONTENT" =~ \<title\>([^<]*)\</title\> ]]; then
        TITLE="${BASH_REMATCH[1]}"
        echo "   Title: $TITLE"
    fi
else
    echo -e "${RED}❌ INVALID HTML${NC}"
fi

# Test 5: Static assets
echo -n "Testing static assets... "
STATIC_ASSETS=0
if [[ "$HTML_CONTENT" == *"/static/"* ]]; then
    STATIC_ASSETS=1
    echo -e "${GREEN}✅ STATIC ASSETS FOUND${NC}"
else
    echo -e "${YELLOW}⚠️ NO STATIC ASSETS DETECTED${NC}"
fi

# Test 6: Backend connectivity (if backend URL provided)
if [ -n "$BACKEND_URL" ]; then
    echo -n "Testing backend connectivity... "
    if curl -s -f "$BACKEND_URL/health" > /dev/null; then
        echo -e "${GREEN}✅ BACKEND REACHABLE${NC}"
        
        # Get backend status
        BACKEND_STATUS=$(curl -s "$BACKEND_URL/health" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'Unknown'))" 2>/dev/null || echo "Unknown")
        echo "   Backend Status: $BACKEND_STATUS"
    else
        echo -e "${RED}❌ BACKEND NOT REACHABLE${NC}"
    fi
fi

# Test 7: Mobile viewport
echo -n "Testing mobile viewport... "
if [[ "$HTML_CONTENT" == *"viewport"* ]]; then
    echo -e "${GREEN}✅ MOBILE VIEWPORT CONFIGURED${NC}"
else
    echo -e "${YELLOW}⚠️ NO MOBILE VIEWPORT${NC}"
fi

# Test 8: Performance check
echo -n "Testing performance... "
LOAD_TIME=$(curl -s -w "%{time_total}" -o /dev/null "$FRONTEND_URL")
if (( $(echo "$LOAD_TIME < 2.0" | bc -l) )); then
    echo -e "${GREEN}✅ FAST (${LOAD_TIME}s)${NC}"
elif (( $(echo "$LOAD_TIME < 5.0" | bc -l) )); then
    echo -e "${YELLOW}⚠️ MODERATE (${LOAD_TIME}s)${NC}"
else
    echo -e "${RED}❌ SLOW (${LOAD_TIME}s)${NC}"
fi

# Test 9: Security headers
echo -n "Testing security headers... "
SECURITY_HEADERS=$(curl -s -I "$FRONTEND_URL")
SECURITY_SCORE=0

if [[ "$SECURITY_HEADERS" == *"X-Content-Type-Options"* ]]; then
    ((SECURITY_SCORE++))
fi
if [[ "$SECURITY_HEADERS" == *"X-Frame-Options"* ]]; then
    ((SECURITY_SCORE++))
fi
if [[ "$SECURITY_HEADERS" == *"Strict-Transport-Security"* ]]; then
    ((SECURITY_SCORE++))
fi

if [ $SECURITY_SCORE -ge 2 ]; then
    echo -e "${GREEN}✅ GOOD SECURITY ($SECURITY_SCORE/3)${NC}"
elif [ $SECURITY_SCORE -ge 1 ]; then
    echo -e "${YELLOW}⚠️ BASIC SECURITY ($SECURITY_SCORE/3)${NC}"
else
    echo -e "${RED}❌ POOR SECURITY ($SECURITY_SCORE/3)${NC}"
fi

echo "=================================="
echo -e "${GREEN}✅ Frontend testing completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Test user registration and login"
echo "2. Test idea creation and management"
echo "3. Test AI enhancement features"
echo "4. Monitor application performance"
echo ""
echo "For comprehensive testing with browser automation:"
echo "npm install puppeteer axios"
echo "node scripts/test_frontend.js $FRONTEND_URL $BACKEND_URL"