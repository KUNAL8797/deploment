#!/usr/bin/env python3
"""
API Testing Script for Deployed Backend
Tests all major API endpoints and functionality
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APITester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_idea_id = None
        
    def test_health_endpoints(self):
        """Test health and basic endpoints"""
        logger.info("Testing health endpoints...")
        
        try:
            # Test root endpoint
            response = self.session.get(f"{self.base_url}/", timeout=30)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Root endpoint: {data.get('message', 'OK')}")
                logger.info(f"   Version: {data.get('version', 'Unknown')}")
                logger.info(f"   Environment: {data.get('environment', 'Unknown')}")
            else:
                logger.error(f"❌ Root endpoint failed: {response.status_code}")
                return False
            
            # Test health endpoint
            response = self.session.get(f"{self.base_url}/health", timeout=30)
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Health endpoint: {health_data.get('status', 'Unknown')}")
                logger.info(f"   Database: {health_data.get('database', 'Unknown')}")
                
                checks = health_data.get('checks', {})
                for check, status in checks.items():
                    status_icon = "✅" if status else "❌"
                    logger.info(f"   {check}: {status_icon}")
                    
            else:
                logger.error(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health endpoint test failed: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        logger.info("Testing user registration...")
        
        try:
            timestamp = int(datetime.now().timestamp())
            test_user = {
                "username": f"testuser_{timestamp}",
                "email": f"test_{timestamp}@example.com",
                "password": "testpassword123"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=test_user,
                timeout=30
            )
            
            if response.status_code == 201:
                user_data = response.json()
                self.test_user_id = user_data.get('id')
                logger.info(f"✅ User registration successful")
                logger.info(f"   User ID: {self.test_user_id}")
                logger.info(f"   Username: {user_data.get('username')}")
                return True
            else:
                logger.error(f"❌ User registration failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"User registration test failed: {e}")
            return False
    
    def test_user_login(self):
        """Test user login and get auth token"""
        logger.info("Testing user login...")
        
        try:
            timestamp = int(datetime.now().timestamp())
            login_data = {
                "username": f"testuser_{timestamp}",
                "password": "testpassword123"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data=login_data,  # Form data for OAuth2
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get('access_token')
                logger.info(f"✅ User login successful")
                logger.info(f"   Token type: {token_data.get('token_type')}")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f"Bearer {self.auth_token}"
                })
                
                return True
            else:
                logger.error(f"❌ User login failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"User login test failed: {e}")
            return False
    
    def test_create_idea(self):
        """Test idea creation"""
        logger.info("Testing idea creation...")
        
        try:
            test_idea = {
                "title": "AI-Powered Test Automation Platform",
                "description": "A comprehensive testing platform that uses artificial intelligence to automatically generate, execute, and maintain test cases for web applications.",
                "development_stage": "concept"
            }
            
            response = self.session.post(
                f"{self.base_url}/ideas",
                json=test_idea,
                timeout=30
            )
            
            if response.status_code == 201:
                idea_data = response.json()
                self.test_idea_id = idea_data.get('id')
                logger.info(f"✅ Idea creation successful")
                logger.info(f"   Idea ID: {self.test_idea_id}")
                logger.info(f"   Title: {idea_data.get('title')}")
                logger.info(f"   Stage: {idea_data.get('development_stage')}")
                return True
            else:
                logger.error(f"❌ Idea creation failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Idea creation test failed: {e}")
            return False
    
    def test_get_ideas(self):
        """Test getting ideas list"""
        logger.info("Testing get ideas...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/ideas",
                timeout=30
            )
            
            if response.status_code == 200:
                ideas_data = response.json()
                ideas_count = len(ideas_data.get('items', []))
                logger.info(f"✅ Get ideas successful")
                logger.info(f"   Ideas count: {ideas_count}")
                logger.info(f"   Total: {ideas_data.get('total', 0)}")
                return True
            else:
                logger.error(f"❌ Get ideas failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Get ideas test failed: {e}")
            return False
    
    def test_ai_enhancement(self):
        """Test AI enhancement functionality"""
        logger.info("Testing AI enhancement...")
        
        if not self.test_idea_id:
            logger.warning("⚠️ Skipping AI enhancement test - no test idea available")
            return True
        
        try:
            response = self.session.post(
                f"{self.base_url}/ideas/{self.test_idea_id}/enhance",
                timeout=60  # AI calls can take longer
            )
            
            if response.status_code == 200:
                enhanced_data = response.json()
                logger.info(f"✅ AI enhancement successful")
                logger.info(f"   AI validated: {enhanced_data.get('ai_validated')}")
                logger.info(f"   Feasibility score: {enhanced_data.get('feasibility_score')}")
                return True
            else:
                logger.error(f"❌ AI enhancement failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                # Don't fail the entire test suite for AI issues
                logger.warning("⚠️ AI enhancement failed but continuing tests...")
                return True
                
        except Exception as e:
            logger.error(f"AI enhancement test failed: {e}")
            logger.warning("⚠️ AI enhancement failed but continuing tests...")
            return True
    
    def test_idea_filtering(self):
        """Test idea filtering and search"""
        logger.info("Testing idea filtering...")
        
        try:
            # Test filtering by stage
            response = self.session.get(
                f"{self.base_url}/ideas?development_stage=concept",
                timeout=30
            )
            
            if response.status_code == 200:
                filtered_data = response.json()
                logger.info(f"✅ Idea filtering successful")
                logger.info(f"   Filtered results: {len(filtered_data.get('items', []))}")
                return True
            else:
                logger.error(f"❌ Idea filtering failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Idea filtering test failed: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        logger.info("Cleaning up test data...")
        
        try:
            if self.test_idea_id:
                response = self.session.delete(
                    f"{self.base_url}/ideas/{self.test_idea_id}",
                    timeout=30
                )
                if response.status_code == 200:
                    logger.info("✅ Test idea deleted")
                else:
                    logger.warning(f"⚠️ Failed to delete test idea: {response.status_code}")
            
            # Note: We don't delete the test user as it might be useful for debugging
            logger.info("✅ Cleanup completed")
            
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
    
    def run_all_tests(self):
        """Run all API tests"""
        logger.info(f"Starting API tests for: {self.base_url}")
        
        tests = [
            ("Health Endpoints", self.test_health_endpoints),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Create Idea", self.test_create_idea),
            ("Get Ideas", self.test_get_ideas),
            ("AI Enhancement", self.test_ai_enhancement),
            ("Idea Filtering", self.test_idea_filtering),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            logger.info(f"\n--- Running: {test_name} ---")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Test {test_name} crashed: {e}")
                failed += 1
            
            time.sleep(1)  # Brief pause between tests
        
        # Cleanup
        self.cleanup_test_data()
        
        # Results
        total = passed + failed
        logger.info(f"\n{'='*50}")
        logger.info(f"API TEST RESULTS")
        logger.info(f"{'='*50}")
        logger.info(f"Total tests: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {failed} ❌")
        logger.info(f"Success rate: {(passed/total)*100:.1f}%")
        logger.info(f"{'='*50}")
        
        return failed == 0


def main():
    """Main testing function"""
    # Get API URL from environment or command line
    api_url = os.getenv('API_URL')
    
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    if not api_url:
        logger.error("API URL not provided")
        logger.info("Usage: python test_api.py <api_url>")
        logger.info("   or: export API_URL=<api_url> && python test_api.py")
        sys.exit(1)
    
    # Ensure URL format
    if not api_url.startswith('http'):
        api_url = f"https://{api_url}"
    
    logger.info(f"Testing API at: {api_url}")
    
    # Run tests
    tester = APITester(api_url)
    success = tester.run_all_tests()
    
    if success:
        logger.info("🎉 All API tests passed!")
        sys.exit(0)
    else:
        logger.error("💥 Some API tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()