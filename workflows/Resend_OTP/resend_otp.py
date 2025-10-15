import logging
import json
import time
from src.core.browser import Browser
from src.core.runner import run_actions
from src.core.db import Database

logger = logging.getLogger(__name__)

def execute(context):
    """
    Execute the Resend_OTP workflow - test OTP resend functionality with dynamic OTP

    This test validates that the OTP can be resent and the latest OTP from database
    is used for password reset. The workflow includes:
    1. Login with valid credentials (user "Siri")
    2. Navigate to forget password flow
    3. Click Resend OTP link (the key functionality being tested)
    4. Wait for OTP to be generated in database
    5. Fetch latest OTP from database for user "Siri"
    6. Enter the dynamic OTP values
    7. Complete password reset process

    Args:
        context: Dictionary containing execution context

    Returns:
        bool: True if workflow completes successfully, False otherwise
    """
    logger.info("=== Starting Resend_OTP Workflow with Dynamic OTP ===")
    start_time = time.time()

    browser = Browser(context)

    try:
        # Load configuration
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Load the Resend_OTP recording
        with open('recordings/Resend_OTP/resend_otp.json', 'r') as f:
            recording = json.load(f)

        # Split actions: run initial steps, then handle OTP inputs separately
        initial_actions = []
        otp_input_actions = []
        final_actions = []

        # Find OTP input actions and split the recording
        for action in recording:
            if action['type'] == 'input' and 'otp-input-' in action.get('xpath', ''):
                otp_input_actions.append(action)
            elif otp_input_actions:  # After we've found OTP inputs
                final_actions.append(action)
            else:  # Before OTP inputs
                initial_actions.append(action)

        logger.info(f"Initial actions: {len(initial_actions)}")
        logger.info(f"OTP input actions: {len(otp_input_actions)}")
        logger.info(f"Final actions: {len(final_actions)}")

        # Run initial actions (up to but not including OTP inputs)
        logger.info("Running initial steps (login, recaptcha, send OTP, resend OTP)...")
        success = run_actions(browser, json_path=None, actions_list=initial_actions)
        if not success:
            logger.error("Initial steps failed")
            return False

        # Wait for OTP to be generated in database after resend
        logger.info("Waiting for OTP to be generated in database after resend...")
        time.sleep(5)  # Wait for OTP to be stored in database

        # Initialize database connection and get fresh OTP
        logger.info("Fetching latest OTP from database after resend...")
        db = Database(config)

        try:
            # Get OTP digits from database for user "Siri" (since we logged in with Siri)
            username = config.get('username', 'Siri')
            logger.info(f"Fetching OTP digits for username: {username}")

            otp_digits = db.get_otp_digits(username)

            if not otp_digits:
                logger.error("Failed to retrieve OTP digits from database after resend")
                return False

            logger.info(f"✅ Successfully retrieved OTP digits after resend: {otp_digits}")

            # Update OTP input actions with fresh values from database
            updated_otp_actions = []
            logger.info(f"Processing {len(otp_input_actions)} OTP input actions")

            for i, action in enumerate(otp_input_actions):
                logger.info(f"Processing OTP action {i+1}: {action.get('xpath', '')}")
                xpath = action.get('xpath', '')

                # Extract digit index from xpath like "//*[@id=\"otp-input-0\"]"
                import re
                digits_in_xpath = re.findall(r'\d+', xpath)
                logger.info(f"Found digits in xpath '{xpath}': {digits_in_xpath}")

                if digits_in_xpath:
                    digit_str = digits_in_xpath[-1]
                    logger.info(f"Last digit string: '{digit_str}'")

                    try:
                        digit_index = int(digit_str)
                        logger.info(f"Parsed digit index: {digit_index}")

                        # Get the OTP digit for this position
                        otp_key = f"otp_digit_{digit_index}"
                        if otp_key in otp_digits:
                            # Create a copy of the action with updated value from database
                            updated_action = action.copy()
                            updated_action['value'] = otp_digits[otp_key]
                            updated_otp_actions.append(updated_action)
                            logger.info(f"✅ Updated OTP digit {digit_index}: {otp_digits[otp_key]}")
                        else:
                            logger.warning(f"❌ No OTP digit found for index {digit_index}")
                            updated_otp_actions.append(action)
                    except ValueError as e:
                        logger.error(f"❌ Failed to parse digit '{digit_str}': {e}")
                        updated_otp_actions.append(action)
                else:
                    logger.error(f"❌ No digits found in OTP xpath: {xpath}")
                    updated_otp_actions.append(action)

            logger.info(f"Updated {len(updated_otp_actions)} OTP input actions with database values")

            # Run OTP inputs with fresh values from database, then final actions
            logger.info("Running OTP input actions with fresh database values...")
            success = run_actions(browser, json_path=None, actions_list=updated_otp_actions)
            if not success:
                logger.error("OTP input failed")
                return False

            # Run final actions (submit button, password reset, etc.)
            logger.info("Running final actions (submit, password reset, etc.)...")
            success = run_actions(browser, json_path=None, actions_list=final_actions)

        finally:
            db.close()

        # Evaluate results
        execution_time = time.time() - start_time

        if success:
            logger.info("✅ RESEND_OTP WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info(f"⏱️  Execution time: {execution_time:.2f}s")
            logger.info("🎯 OTP resend functionality with dynamic OTP is working correctly")
            return True
        else:
            logger.error("❌ RESEND_OTP WORKFLOW FAILED")
            logger.error(f"⏱️  Execution time: {execution_time:.2f}s")
            return False

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ RESEND_OTP WORKFLOW ERROR: {str(e)}")
        logger.error(f"⏱️  Execution time: {execution_time:.2f}s")

        # Take error screenshot for debugging
        try:
            browser.get_driver().save_screenshot("screenshots/resend_otp_critical_error.png")
            logger.info("📸 Critical error screenshot saved")
        except:
            logger.warning("Failed to save error screenshot")

        raise

    finally:
        logger.info("🔒 Closing browser...")
        browser.close()
