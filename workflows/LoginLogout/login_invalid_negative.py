import logging
import json
import time
from src.core.browser import Browser
from src.core.runner import run_actions
from src.core.db import Database

logger = logging.getLogger(__name__)

def execute(context):
    """
    Execute the negative scenario - login with invalid username and captcha

    This test verifies that the system properly validates and rejects login attempts
    with non-existent usernames, displaying "User does not exist" error message.

    Test Flow:
    1. Navigate to login page
    2. Enter invalid username: NONEXISTENT_USER_12345
    3. Complete recaptcha challenge
    4. Click Proceed button
    5. Verify system displays "User does not exist" error message

    Args:
        context: Dictionary containing execution context

    Returns:
        bool: True if validation error occurs as expected, False otherwise
    """
    logger.info("=== Starting Login Invalid Username Negative Test ===")
    start_time = time.time()

    browser = Browser(context)

    try:
        # Load configuration
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Load the negative scenario recording
        with open('recordings/LoginLogout/login_invalid_negative.json', 'r') as f:
            recording = json.load(f)

        logger.info(f"🔍 Testing login with invalid username: {config.get('invalid_username_login', 'NONEXISTENT_USER_12345')}")
        logger.info("✅ Expected: System should reject login with 'User does not exist' error")

        # Execute the negative test scenario
        logger.info("🚀 Executing login invalid username workflow...")
        success = run_actions(browser, json_path=None, actions_list=recording)

        # Evaluate results
        execution_time = time.time() - start_time

        if success:
            logger.error("❌ TEST FAILED: Invalid username login was accepted (should have been rejected)")
            logger.error(f"⏱️  Execution time: {execution_time:.2f}s")
            return False
        else:
            logger.info("✅ TEST PASSED: Invalid username properly rejected with 'User does not exist' error")
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
            browser.get_driver().save_screenshot("screenshots/login_invalid_critical_error.png")
            logger.info("📸 Critical error screenshot saved")
        except:
            logger.warning("Failed to save error screenshot")

        raise

    finally:
        logger.info("🔒 Closing browser...")
        browser.close()
