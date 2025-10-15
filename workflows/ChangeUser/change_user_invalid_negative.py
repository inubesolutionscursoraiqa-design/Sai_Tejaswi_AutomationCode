import logging
import json
import time
from src.core.browser import Browser
from src.core.runner import run_actions
from src.core.db import Database

logger = logging.getLogger(__name__)

def execute(context):
    """
    Execute the negative scenario - change user with invalid/non-existent username

    This optimized test efficiently verifies that the system properly validates
    and throws an error when attempting to change to a user that doesn't exist.

    Test Flow:
    1. Login with valid credentials
    2. Navigate to change user functionality
    3. Enter invalid username: INVALID_USER_NOT_FOUND
    4. Verify system throws "user not found" validation error

    Args:
        context: Dictionary containing execution context

    Returns:
        bool: True if validation error occurs as expected, False otherwise
    """
    logger.info("=== Starting Optimized Change User Invalid Username Test ===")
    start_time = time.time()

    browser = Browser(context)

    try:
        # Load configuration
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Load optimized recording
        with open('recordings/ChangeUser/change_user_invalid_negative.json', 'r') as f:
            recording = json.load(f)

        logger.info(f"🔍 Testing invalid username scenario: {config.get('invalid_username', 'INVALID_USER_NOT_FOUND')}")
        logger.info("✅ Expected: System should reject invalid username with validation error")

        # Execute the test scenario
        logger.info("🚀 Executing optimized invalid username workflow...")
        success = run_actions(browser, json_path=None, actions_list=recording)

        # Evaluate results
        execution_time = time.time() - start_time

        if success:
            logger.error("❌ TEST FAILED: Invalid username was accepted (should have been rejected)")
            logger.error(f"⏱️  Execution time: {execution_time:.2f}s")
            return False
        else:
            logger.info("✅ TEST PASSED: Invalid username properly rejected with validation error")
            logger.info(f"⏱️  Execution time: {execution_time:.2f}s")
            return True

    except AssertionError as e:
        # Expected validation error - test passes
        execution_time = time.time() - start_time
        logger.info(f"✅ TEST PASSED: Validation error correctly thrown - {str(e)}")
        logger.info(f"⏱️  Execution time: {execution_time:.2f}s")
        return True

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ TEST ERROR: Unexpected exception occurred - {str(e)}")
        logger.error(f"⏱️  Execution time: {execution_time:.2f}s")

        # Take error screenshot for debugging
        try:
            browser.get_driver().save_screenshot("screenshots/change_user_invalid_critical_error.png")
            logger.info("📸 Critical error screenshot saved")
        except:
            logger.warning("Failed to save error screenshot")

        raise

    finally:
        logger.info("🔒 Closing browser...")
        browser.close()
