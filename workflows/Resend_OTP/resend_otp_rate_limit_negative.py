import logging
import json
import time
from src.core.browser import Browser
from src.core.runner import run_actions
from src.core.db import Database

logger = logging.getLogger(__name__)

def execute(context):
    """
    Execute the negative scenario - Resend_OTP rate limiting test

    This test validates that the system properly handles rapid OTP resend attempts
    by implementing rate limiting or cooldown periods. The workflow includes:
    1. Login with valid credentials (user "Siri")
    2. Navigate to forget password flow
    3. Send initial OTP
    4. Immediately try to resend OTP (testing rate limiting)
    5. Try to resend OTP again quickly (testing cooldown/rate limit)
    6. Verify system shows rate limiting error message

    Args:
        context: Dictionary containing execution context

    Returns:
        bool: True if rate limiting validation works correctly, False otherwise
    """
    logger.info("=== Starting Resend_OTP Rate Limit Negative Test ===")
    start_time = time.time()

    browser = Browser(context)

    try:
        # Load configuration
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Load the rate limit negative scenario recording
        with open('recordings/Resend_OTP/resend_otp_rate_limit_negative.json', 'r') as f:
            recording = json.load(f)

        logger.info("🔄 Testing Resend_OTP rate limiting functionality...")
        logger.info("✅ Expected: System should show rate limiting error when resending OTP too quickly")

        # Execute the rate limiting test scenario
        logger.info("🚀 Executing Resend_OTP rate limit test...")
        success = run_actions(browser, json_path=None, actions_list=recording)

        # Evaluate results
        execution_time = time.time() - start_time

        if success:
            logger.error("❌ TEST FAILED: Rate limiting validation failed - system allowed rapid resends")
            logger.error(f"⏱️  Execution time: {execution_time:.2f}s")
            return False
        else:
            logger.info("✅ TEST PASSED: Rate limiting validation working correctly")
            logger.info(f"⏱️  Execution time: {execution_time:.2f}s")
            return True

    except AssertionError as e:
        # Expected validation error - test passes
        execution_time = time.time() - start_time
        logger.info(f"✅ TEST PASSED: Rate limiting error correctly thrown - {str(e)}")
        logger.info(f"⏱️  Execution time: {execution_time:.2f}s")
        return True

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ TEST ERROR: Unexpected exception occurred - {str(e)}")
        logger.error(f"⏱️  Execution time: {execution_time:.2f}s")

        # Take error screenshot for debugging
        try:
            browser.get_driver().save_screenshot("screenshots/resend_otp_rate_limit_critical_error.png")
            logger.info("📸 Critical error screenshot saved")
        except:
            logger.warning("Failed to save error screenshot")

        raise

    finally:
        logger.info("🔒 Closing browser...")
        browser.close()

