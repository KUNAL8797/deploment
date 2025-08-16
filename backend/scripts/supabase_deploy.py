#!/usr/bin/env python3
"""
Supabase-specific deployment script
Handles schema deployment and verification for Supabase PostgreSQL
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_database_url(database_url):
    """Parse database URL into components"""
    try:
        # Remove postgresql:// prefix
        url = database_url.replace('postgresql://', '').replace('postgres://', '')
        
        # Split user:password@host:port/database
        auth_part, host_part = url.split('@')
        user, password = auth_part.split(':')
        host_port, database = host_part.split('/')
        host, port = host_port.split(':')
        
        return {
            'user': user,
            'password': password,
            'host': host,
            'port': int(port),
            'database': database
        }
    except Exception as e:
        logger.error(f"Error parsing database URL: {e}")
        return None


def test_connection(db_config):
    """Test database connection"""
    try:
        logger.info("Testing database connection...")
        
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            sslmode='require'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        logger.info(f"Connected to: {version}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


def deploy_schema(db_config):
    """Deploy database schema to Supabase"""
    try:
        logger.info("Deploying database schema...")
        
        # Read SQL file
        sql_file = os.path.join(os.path.dirname(__file__), '..', 'sql', 'init_database.sql')
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        # Connect to database
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            sslmode='require'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Execute SQL commands
        # Split by semicolon and execute each command separately
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        for i, command in enumerate(commands):
            if command.strip():
                try:
                    logger.info(f"Executing command {i+1}/{len(commands)}")
                    cursor.execute(command)
                except Exception as e:
                    # Some commands might fail if they already exist (like CREATE TYPE)
                    if "already exists" in str(e).lower():
                        logger.warning(f"Command {i+1} skipped (already exists): {str(e)[:100]}")
                    else:
                        logger.error(f"Command {i+1} failed: {e}")
                        raise
        
        cursor.close()
        conn.close()
        
        logger.info("Schema deployment completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Schema deployment failed: {e}")
        return False


def verify_schema(db_config):
    """Verify that all tables and indexes were created"""
    try:
        logger.info("Verifying database schema...")
        
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['users', 'ideas', 'idea_insights']
        
        logger.info(f"Found tables: {tables}")
        
        for table in expected_tables:
            if table in tables:
                logger.info(f"✅ Table '{table}' exists")
            else:
                logger.error(f"❌ Table '{table}' missing")
                return False
        
        # Check indexes
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY indexname;
        """)
        
        indexes = [row[0] for row in cursor.fetchall()]
        logger.info(f"Found {len(indexes)} indexes")
        
        # Check for admin user
        cursor.execute("SELECT username FROM users WHERE role = 'admin' LIMIT 1;")
        admin_user = cursor.fetchone()
        
        if admin_user:
            logger.info(f"✅ Admin user exists: {admin_user[0]}")
        else:
            logger.warning("⚠️ No admin user found")
        
        cursor.close()
        conn.close()
        
        logger.info("Schema verification completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Schema verification failed: {e}")
        return False


def main():
    """Main deployment function"""
    logger.info("Starting Supabase database deployment...")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        logger.info("Set it like: export DATABASE_URL='postgresql://postgres:password@db.xxx.supabase.co:5432/postgres'")
        sys.exit(1)
    
    # Parse database URL
    db_config = parse_database_url(database_url)
    if not db_config:
        logger.error("Failed to parse DATABASE_URL")
        sys.exit(1)
    
    logger.info(f"Connecting to Supabase database at {db_config['host']}")
    
    # Step 1: Test connection
    if not test_connection(db_config):
        logger.error("❌ Database connection failed")
        sys.exit(1)
    
    # Step 2: Deploy schema
    if not deploy_schema(db_config):
        logger.error("❌ Schema deployment failed")
        sys.exit(1)
    
    # Step 3: Verify schema
    if not verify_schema(db_config):
        logger.error("❌ Schema verification failed")
        sys.exit(1)
    
    logger.info("✅ Supabase database deployment completed successfully!")
    
    # Print connection info for backend configuration
    print("\n" + "="*60)
    print("SUPABASE DATABASE READY")
    print("="*60)
    print("Use this connection string for your backend:")
    print(f"DATABASE_URL={database_url}")
    print("\nNext steps:")
    print("1. Configure this DATABASE_URL in your Render backend service")
    print("2. Deploy your backend to Render")
    print("3. Test the API endpoints")
    print("="*60)


if __name__ == "__main__":
    main()