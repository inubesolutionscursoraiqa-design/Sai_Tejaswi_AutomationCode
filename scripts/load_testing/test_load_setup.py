#!/usr/bin/env python3
"""
Simple test to verify load testing setup works
"""
import sys
import logging
from src.load_testing.load_tester import LoadTester

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_single_user():
    """Test with a single user to verify setup"""
    logger.info("Testing load testing setup with single user...")

    try:
        tester = LoadTester("LoginLogout", "recordings/LoginLogout/login_logout.json")

        # Run test with 1 user
        results = tester.run_load_test(num_users=1, ramp_up_time=0)

        logger.info("Test completed successfully!")
        logger.info(f"Results: {results}")

        return True

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_single_user()
    sys.exit(0 if success else 1)

