#!/usr/bin/env python3
"""
Alembic migration runner for production deployment
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_alembic_upgrade():
    """Run Alembic upgrade to head"""
    try:
        logger.info("Running Alembic migrations...")
        
        # Change to the backend directory
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        os.chdir(backend_dir)
        
        # Run alembic upgrade
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("Alembic migrations completed successfully!")
        logger.info(f"Output: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Alembic migration failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("Alembic not found. Make sure it's installed: pip install alembic")
        return False


def main():
    """Main function"""
    logger.info("Starting database migration...")
    
    if run_alembic_upgrade():
        logger.info("✅ Database migration completed successfully!")
    else:
        logger.error("❌ Database migration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()