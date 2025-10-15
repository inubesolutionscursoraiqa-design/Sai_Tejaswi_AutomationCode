import logging
import json
import time
from src.core.browser import Browser
from src.core.runner import run_actions

logger = logging.getLogger(__name__)

def execute(context):
    """
    Execute the login and logout workflow
    
    This test verifies that a user can successfully:
    1. Login to the system with valid credentials
    2. Logout from the system
    
    Args:
        context: Dictionary containing execution context
        
    Returns:
        bool: True if workflow completes successfully, False otherwise
    """
    logger.info("=== Starting Login Logout Workflow ===")
    start_time = time.time()
    
    browser = Browser(context)
    
    try:
        # Load the login-logout recording
        logger.info("Loading login_logout workflow recording...")
        
        # Run the complete workflow
        logger.info("Running login and logout workflow...")
        success = run_actions(browser, json_path="recordings/LoginLogout/login_logout.json")
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        if success:
            logger.info("TEST PASSED: Login and logout completed successfully")
            logger.info(f"Execution time: {execution_time:.2f}s")
            # Log the success message that the report generator looks for
            print("Workflow LoginLogout/login_logout completed successfully")
            return True
        else:
            logger.error("TEST FAILED: Login and logout workflow failed")
            logger.error(f"Execution time: {execution_time:.2f}s")
            # Log the failure message that the report generator looks for
            print("Workflow LoginLogout/login_logout failed")
            return False
            
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"TEST ERROR: Unexpected exception occurred - {str(e)}")
        logger.error(f"Execution time: {execution_time:.2f}s")

        # Take error screenshot for debugging
        try:
            browser.get_driver().save_screenshot("screenshots/login_logout_critical_error.png")
            logger.info("Critical error screenshot saved")
        except:
            logger.warning("Failed to save error screenshot")

        raise

    finally:
        logger.info("Closing browser...")
        browser.close()
