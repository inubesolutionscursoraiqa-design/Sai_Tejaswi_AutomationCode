import logging
import json
import time
from src.core.browser import Browser
from src.core.runner import run_actions
from src.core.db import Database

logger = logging.getLogger(__name__)

def execute(context):
    """
    Execute the change user workflow

    Args:
        context: Dictionary containing execution context
    """
    logger.info("=== Starting Change User Workflow ===")

    browser = Browser(context)

    try:
        # Load config to get database settings and usernames
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Load the base recording
        with open('recordings/ChangeUser/change_user.json', 'r') as f:
            recording = json.load(f)

        # Initialize database connection and get fresh OTP if needed
        db = Database(config)

        # Run the complete workflow
        logger.info("Running complete change user workflow...")
        success = run_actions(browser, json_path=None, actions_list=recording)

        if success:
            logger.info("=== Change User Workflow Completed Successfully ===")
        else:
            logger.error("=== Change User Workflow Failed ===")

        return success

    except Exception as e:
        logger.error(f"=== Change User Workflow Error: {str(e)} ===")
        try:
            browser.get_driver().save_screenshot("screenshots/change_user_error.png")
        except:
            pass
        raise

    finally:
        browser.close()

