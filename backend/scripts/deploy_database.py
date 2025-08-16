#!/usr/bin/env python3
"""
Database deployment script for AI Innovation Incubator
This script sets up the database schema for production deployment
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings
from app.database import Base, engine
from app.models import user, idea, insight  # Import all models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database_schema():
    """Create all database tables and indexes"""
    try:
        logger.info("Creating database schema...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database schema created successfully!")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Error creating database schema: {e}")
        return False


def verify_database_connection():
    """Verify that we can connect to the database"""
    try:
        logger.info("Verifying database connection...")
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            
        logger.info("Database connection verified!")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False


def create_admin_user():
    """Create default admin user if it doesn't exist"""
    try:
        from app.models.user import User, UserRole
        from app.database import SessionLocal
        from passlib.context import CryptContext
        
        logger.info("Creating admin user...")
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        db = SessionLocal()
        
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            logger.info("Admin user already exists, skipping creation")
            db.close()
            return True
        
        # Create admin user
        hashed_password = pwd_context.hash("admin123")  # Change this password!
        admin_user = User(
            username="admin",
            email="admin@ideaforge.ai",
            hashed_password=hashed_password,
            role=UserRole.ADMIN
        )
        
        db.add(admin_user)
        db.commit()
        db.close()
        
        logger.info("Admin user created successfully!")
        logger.warning("⚠️  Default admin password is 'admin123' - CHANGE THIS IN PRODUCTION!")
        return True
        
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        return False


def main():
    """Main deployment function"""
    logger.info("Starting database deployment...")
    logger.info(f"Database URL: {settings.database_url.split('@')[0] if '@' in settings.database_url else 'SQLite'}")
    
    # Step 1: Verify database connection
    if not verify_database_connection():
        logger.error("❌ Database deployment failed - connection error")
        sys.exit(1)
    
    # Step 2: Create database schema
    if not create_database_schema():
        logger.error("❌ Database deployment failed - schema creation error")
        sys.exit(1)
    
    # Step 3: Create admin user
    if not create_admin_user():
        logger.error("❌ Database deployment failed - admin user creation error")
        sys.exit(1)
    
    logger.info("✅ Database deployment completed successfully!")
    
    # Print next steps
    print("\n" + "="*50)
    print("DATABASE DEPLOYMENT COMPLETE")
    print("="*50)
    print("Next steps:")
    print("1. Change the default admin password")
    print("2. Configure your application environment variables")
    print("3. Start your application server")
    print("4. Test the API endpoints")
    print("\nAPI Documentation will be available at: /docs")
    print("="*50)


if __name__ == "__main__":
    main()