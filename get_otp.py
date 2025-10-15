#!/usr/bin/env python3
"""
Script to fetch the latest OTP for user 'Amith' from the database
"""

import json
import logging
import sys
import os

# Add core module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.db import Database

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Get latest OTP for user Amith"""
    try:
        # Load configuration
        with open('config.json', 'r') as f:
            config = json.load(f)

        logger = logging.getLogger(__name__)
        logger.info("=== Getting Latest OTP for Amith ===")

        # Initialize database connection
        db = Database(config)

        # Get the latest OTP for Amith (forget_username)
        username = config.get('forget_username', 'Amith')
        logger.info(f"Fetching OTP for username: {username}")

        otp = db.get_latest_otp(username)

        if otp:
            logger.info(f"✅ Latest OTP for '{username}': {otp}")
            print(f"\n🔑 Latest OTP for '{username}': {otp}")
            return otp
        else:
            logger.warning(f"❌ No OTP found for '{username}'")
            print(f"\n❌ No OTP found for '{username}'")
            return None

    except Exception as e:
        logger.error(f"❌ Error getting OTP: {str(e)}")
        print(f"\n❌ Error getting OTP: {str(e)}")
        return None

    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main()
