#!/usr/bin/env python3
"""
Deployment verification script
Tests database connectivity and basic functionality
"""

import os
import sys
import logging
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database_connection():
    """Test database connection using the app's database module"""
    try:
        # Add the app directory to the path
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        from app.database import check_database_connection
        
        logger.info("Testing database connection...")
        
        if check_database_connection():
            logger.info("✅ Database connection successful")
            return True
        else:
            logger.error("❌ Database connection failed")
            return False
            
    except Exception as e:
        logger.error(f"Database connection test error: {e}")
        return False


def test_api_endpoints(base_url):
    """Test basic API endpoints"""
    try:
        logger.info(f"Testing API endpoints at {base_url}")
        
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Root endpoint working")
            data = response.json()
            logger.info(f"API Version: {data.get('version', 'Unknown')}")
        else:
            logger.error(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Health endpoint working")
            health_data = response.json()
            logger.info(f"Health Status: {health_data.get('status', 'Unknown')}")
        else:
            logger.error(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test docs endpoint (if available)
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            logger.info("✅ API documentation available")
        else:
            logger.info("ℹ️ API documentation not available (normal for production)")
        
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API endpoint test failed: {e}")
        return False


def test_user_registration(base_url):
    """Test user registration endpoint"""
    try:
        logger.info("Testing user registration...")
        
        test_user = {
            "username": f"test_user_{int(datetime.now().timestamp())}",
            "email": f"test_{int(datetime.now().timestamp())}@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(
            f"{base_url}/auth/register",
            json=test_user,
            timeout=10
        )
        
        if response.status_code == 201:
            logger.info("✅ User registration working")
            return True
        else:
            logger.error(f"❌ User registration failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"User registration test failed: {e}")
        return False


def main():
    """Main verification function"""
    logger.info("Starting deployment verification...")
    
    # Test database connection
    if not test_database_connection():
        logger.error("❌ Database verification failed")
        sys.exit(1)
    
    # Test API endpoints if URL provided
    api_url = os.getenv('API_URL')
    if api_url:
        logger.info(f"Testing API at: {api_url}")
        
        if not test_api_endpoints(api_url):
            logger.error("❌ API endpoint verification failed")
            sys.exit(1)
        
        if not test_user_registration(api_url):
            logger.error("❌ User registration verification failed")
            sys.exit(1)
    else:
        logger.info("API_URL not set, skipping API tests")
    
    logger.info("✅ All deployment verification tests passed!")
    
    print("\n" + "="*50)
    print("DEPLOYMENT VERIFICATION COMPLETE")
    print("="*50)
    print("✅ Database connection: Working")
    if api_url:
        print("✅ API endpoints: Working")
        print("✅ User registration: Working")
    print("\nYour deployment is ready for use!")
    print("="*50)


if __name__ == "__main__":
    main()