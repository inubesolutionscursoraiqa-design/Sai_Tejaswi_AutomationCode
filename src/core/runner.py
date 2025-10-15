import json
import logging
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.core.playwright_utils import PlaywrightUtils

logger = logging.getLogger(__name__)

def load_actions(json_path):
    """Load actions from JSON file"""
    try:
        with open(json_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Failed to load JSON file {json_path}: {str(e)}")
        raise

def run_actions(browser, json_path=None, actions_list=None):
    """Run actions from JSON file or actions list - simple and direct approach"""
    if actions_list is not None:
        actions = actions_list
    elif json_path is not None:
        actions = load_actions(json_path)
    else:
        raise ValueError("Either json_path or actions_list must be provided")

    driver = browser.get_driver()
    
    # Initialize Playwright-inspired utilities
    pw = PlaywrightUtils(driver)

    # Load credentials from config.json
    config_data = {}
    try:
        with open('config.json', 'r') as f:
            config_data = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load config file: {str(e)}")

    for i, action in enumerate(actions):
        action_type = action.get("type")
        logger.info(f"Step {i+1}: Executing action: {action_type}")
        
        try:
            if action_type == "goto":
                url = action.get("url")
                logger.info(f"Navigating to: {url}")

                # Replace with config values if needed
                if url == "CONFIG_URL" and 'url' in config_data:
                    url = config_data['url']
                    logger.info(f"Using URL from config: {url}")

                driver.get(url)
                time.sleep(3)  # Wait for page to load
                logger.info("Page loaded")
                
            elif action_type == "wait":
                seconds = action.get("seconds", 1)
                logger.info(f"Waiting for {seconds} seconds")
                time.sleep(seconds)
                
            elif action_type == "input":
                xpath = action.get("xpath")
                value = action.get("value")
                logger.info(f"Entering text '{value}' into element: {xpath}")

                # Replace with config values if needed
                if value == "CONFIG_USERNAME" and 'username' in config_data:
                    value = config_data['username']
                    logger.info(f"Using username from config: {value}")
                elif value == "CONFIG_PASSWORD" and 'password' in config_data:
                    value = config_data['password']
                    logger.info(f"Using password from config: {value}")
                elif value == "CONFIG_FORGET_USERNAME" and 'forget_username' in config_data:
                    value = config_data['forget_username']
                    logger.info(f"Using forget username from config: {value}")
                elif value == "CONFIG_NEW_PASSWORD" and 'new_password' in config_data:
                    value = config_data['new_password']
                    logger.info(f"Using new password from config: {value}")
                elif value == "CONFIG_NEW_USERNAME" and 'new_username' in config_data:
                    value = config_data['new_username']
                    logger.info(f"Using new username from config: {value}")
                elif value == "CONFIG_NEW_USER_NAME" and 'new_user_name' in config_data:
                    value = config_data['new_user_name']
                    logger.info(f"Using new user name from config: {value}")
                elif value == "CONFIG_NEW_USER_EMAIL" and 'new_user_email' in config_data:
                    value = config_data['new_user_email']
                    logger.info(f"Using new user email from config: {value}")
                elif value == "CONFIG_NEW_USER_PHONE" and 'new_user_phone' in config_data:
                    value = config_data['new_user_phone']
                    logger.info(f"Using new user phone from config: {value}")
                elif value == "CONFIG_NEW_USER_DOB" and 'new_user_dob' in config_data:
                    value = config_data['new_user_dob']
                    logger.info(f"Using new user DOB from config: {value}")
                elif value == "CONFIG_NEW_USER_ADDRESS" and 'new_user_address' in config_data:
                    value = config_data['new_user_address']
                    logger.info(f"Using new user address from config: {value}")
                elif value == "INVALID_USER_NOT_FOUND" and 'invalid_username' in config_data:
                    value = config_data['invalid_username']
                    logger.info(f"Using invalid username from config: {value}")
                elif value == "INVALID_USERNAME_LOGIN" and 'invalid_username_login' in config_data:
                    value = config_data['invalid_username_login']
                    logger.info(f"Using invalid username for login from config: {value}")
                elif value == "INVALID_USERNAME_FORGET" and 'invalid_username_forget' in config_data:
                    value = config_data['invalid_username_forget']
                    logger.info(f"Using invalid username for forget password from config: {value}")
                elif value == "DIFFERENT_PASSWORD_123" and 'different_password' in config_data:
                    value = config_data['different_password']
                    logger.info(f"Using different password from config: {value}")

                # Simple and direct - wait and enter text
                element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )

                # Handle clearing vs entering text
                if value == "":  # Empty string means clear the field
                    # Aggressive clearing for autocomplete/dropdown fields
                    try:
                        # Try JavaScript clearing first
                        driver.execute_script("arguments[0].value = '';", element)
                        logger.info("Cleared field using JavaScript")
                    except:
                        # Fallback to regular clear
                        element.clear()
                        logger.info("Cleared field using element.clear()")

                    # Additional clearing with backspace (for autocomplete fields)
                    current_value = element.get_attribute("value") or ""
                    if current_value:
                        for _ in range(len(current_value)):
                            element.send_keys("\b")  # Backspace
                        logger.info("Cleared field using backspace")

                    time.sleep(0.1)
                else:
                    # Aggressive clearing for all input fields
                    try:
                        # Try JavaScript clearing first
                        driver.execute_script("arguments[0].value = '';", element)
                        logger.info("Cleared field using JavaScript")
                    except:
                        # Fallback to regular clear
                        element.clear()
                        logger.info("Cleared field using element.clear()")

                    # Additional clearing with backspace (for autocomplete fields)
                    current_value = element.get_attribute("value") or ""
                    if current_value:
                        for _ in range(len(current_value)):
                            element.send_keys("\b")  # Backspace
                        logger.info("Cleared field using backspace")

                    time.sleep(0.1)

                    # Special handling for date fields and hidden fields
                    element_type = element.get_attribute("type")
                    element_id = element.get_attribute("id") or ""
                    element_name = element.get_attribute("name") or ""

                    # Check if this is a date field
                    is_date_field = (element_type == "date" or
                                   "date" in element_id.lower() or
                                   "dob" in element_id.lower() or
                                   "birth" in element_name.lower())
                                   
                    # Check if this is a hidden field (for dropdowns)
                    is_hidden_field = element_type == "hidden"

                    if is_date_field:
                        logger.info(f"Detected date field, entering date: {value}")
                        # Use JavaScript to set date value directly (more reliable)
                        try:
                            driver.execute_script(f"arguments[0].value = '{value}';", element)
                            # Trigger change and input events
                            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", element)
                            logger.info(f"Set date using JavaScript: {value}")
                        except Exception as e:
                            logger.warning(f"JavaScript date setting failed, trying send_keys: {e}")
                            # Fallback to send_keys
                            element.clear()
                            element.send_keys(value)
                        time.sleep(1)
                    elif is_hidden_field:
                        logger.info(f"Detected hidden field (likely dropdown), setting value: {value}")
                        
                        # Check if this is a MUI Select hidden input
                        element_name = element.get_attribute("name") or ""
                        is_mui_select = False
                        
                        try:
                            # Check if this is a MUI select by looking for related elements
                            if element_name in ["user_type_id", "role_id"] or "mui" in driver.page_source.lower():
                                is_mui_select = True
                                logger.info(f"Detected MUI Select hidden field: {element_name}")
                        except:
                            pass
                            
                        if is_mui_select:
                            # Special handling for MUI Select components
                            logger.info(f"Using special MUI Select handling for {element_name}")
                            try:
                                # 1. Set the value directly
                                driver.execute_script(f"arguments[0].value = '{value}';", element)
                                
                                # 2. Find and update the visible text
                                select_id = f"mui-component-select-{element_name}"
                                driver.execute_script(f"""
                                    // Find the visible select element
                                    var selectElement = document.getElementById('{select_id}');
                                    if (selectElement) {{
                                        // Get the option text
                                        var options = document.querySelectorAll('li[data-value="{value}"]');
                                        var optionText = options.length > 0 ? options[0].textContent : '';
                                        
                                        // Update the visible text
                                        selectElement.textContent = optionText || '{value}';
                                        
                                        // Dispatch events
                                        var changeEvent = new Event('change', {{ bubbles: true }});
                                        arguments[0].dispatchEvent(changeEvent);
                                    }}
                                """)
                                
                                logger.info(f"Successfully set MUI Select value: {value}")
                            except Exception as e:
                                logger.warning(f"MUI Select special handling failed: {str(e)}")
                                # Fallback to regular hidden field handling
                                driver.execute_script(f"arguments[0].value = '{value}';", element)
                                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", element)
                        else:
                            # Regular hidden field
                            driver.execute_script(f"arguments[0].value = '{value}';", element)
                            # Trigger change event to ensure UI updates
                            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", element)
                            
                        time.sleep(0.5)
                    else:
                        # Regular text input
                        element.send_keys(value)
                        time.sleep(0.1)

                    # Verify the value was entered (for debugging)
                    entered_value = element.get_attribute("value")
                    if entered_value != value:
                        # For date fields, don't fail on format differences - just log
                        if is_date_field:
                            logger.warning(f"Date field value mismatch (may be formatting): Expected: {value}, Got: {entered_value}")
                            logger.info("Date field set - continuing execution (date fields may have different internal formats)")
                        else:
                            logger.warning(f"Value mismatch! Expected: {value}, Got: {entered_value}")
                    else:
                        logger.info(f"Successfully entered text: {value} (verified: {entered_value})")
                
            elif action_type == "click" or action_type == "jsclick":
                xpath = action.get("xpath")
                use_js = action_type == "jsclick"
                logger.info(f"Clicking element: {xpath} {'(using JavaScript)' if use_js else ''}")

                # Wait and click with more detailed error handling
                try:
                    # First wait for presence with longer timeout for dropdown options
                    timeout = 15 if ("//li[" in xpath or "option" in xpath or "-option-" in xpath) else 10
                    element = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    logger.info(f"Element is present (waited up to {timeout}s)")

                    if use_js:
                        # Use JavaScript click directly for jsclick type
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.5)
                        
                        # Check if this is a MUI dropdown (Material-UI)
                        is_mui_dropdown = False
                        try:
                            element_id = element.get_attribute("id") or ""
                            element_class = element.get_attribute("class") or ""
                            element_role = element.get_attribute("role") or ""
                            
                            if ("mui-component-select" in element_id.lower() or 
                                "muiselect" in element_class.lower() or
                                "combobox" in element_role.lower()):
                                is_mui_dropdown = True
                                logger.info("Detected Material-UI dropdown component")
                        except:
                            pass
                            
                        # Special handling for MUI dropdown trigger
                        if is_mui_dropdown:
                            logger.info("Using special handling for MUI dropdown")
                            # Force open the dropdown with special MUI events
                            driver.execute_script("""
                                // Scroll into view and ensure visibility
                                arguments[0].scrollIntoView({block: 'center'});
                                
                                // Force click with multiple events
                                arguments[0].click();
                                arguments[0].dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
                                arguments[0].dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
                                arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));
                                
                                // Set aria-expanded to true (MUI uses this)
                                arguments[0].setAttribute('aria-expanded', 'true');
                            """, element)
                            logger.info("MUI dropdown clicked with special handling")
                            time.sleep(1)
                            
                        # Special handling for dropdown options
                        elif "option" in xpath or "//li" in xpath or "-option-" in xpath:
                            logger.info("Using special handling for dropdown option")
                            # Force element to be visible and clickable
                            driver.execute_script("""
                                arguments[0].style.display = 'block';
                                arguments[0].style.visibility = 'visible';
                                arguments[0].style.opacity = '1';
                                arguments[0].style.pointerEvents = 'auto';
                            """, element)
                            time.sleep(0.5)
                            # Triple click for dropdown options to ensure selection
                            driver.execute_script("arguments[0].click();", element)
                            time.sleep(0.2)
                            driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));", element)
                            time.sleep(0.2)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", element)
                            logger.info("Dropdown option clicked with multiple events")
                        else:
                            # Regular jsclick
                            driver.execute_script("arguments[0].click();", element)
                            
                        logger.info("JavaScript click successful")
                        time.sleep(0.5)
                    else:
                        # Special handling for dropdown options - wait longer and scroll
                        if "-option-" in xpath or "//li[" in xpath or "option" in xpath:
                            logger.info("Handling dropdown option click")
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            time.sleep(0.5)
                            # Try visible click first
                            try:
                                element = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, xpath))
                                )
                                element.click()
                                logger.info("Dropdown option click successful")
                            except:
                                # Fallback to JS click
                                logger.info("Regular click failed, using JS for dropdown option")
                                driver.execute_script("arguments[0].click();", element)
                        else:
                            # Then wait for it to be clickable for regular clicks
                            element = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, xpath))
                            )
                            logger.info("Element is clickable")
                            element.click()
                        
                        time.sleep(0.3)
                        logger.info("Click successful")

                except Exception as e:
                    logger.error(f"Failed to click element {xpath}: {str(e)}")
                    # Take screenshot for debugging
                    try:
                        screenshot_path = os.path.join("screenshots", f"click_error_{i+1}.png")
                        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                        driver.save_screenshot(screenshot_path)
                        logger.info(f"Saved click error screenshot to {screenshot_path}")
                    except:
                        pass

                    # Try JavaScript click as fallback
                    try:
                        logger.info("Trying JavaScript click as fallback...")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].click();", element)
                        logger.info("JavaScript click successful")
                        time.sleep(0.3)
                    except Exception as js_error:
                        logger.error(f"JavaScript click also failed: {str(js_error)}")
                        # Take another screenshot
                        try:
                            screenshot_path = os.path.join("screenshots", f"click_error_js_{i+1}.png")
                            driver.save_screenshot(screenshot_path)
                            logger.info(f"Saved JavaScript click error screenshot to {screenshot_path}")
                        except:
                            pass
                        raise
                
            elif action_type == "recaptcha":
                logger.info("Handling recaptcha")
                time.sleep(3)
                
                # Find recaptcha iframe
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    try:
                        src = iframe.get_attribute("src")
                        if src and "recaptcha" in src.lower():
                            driver.switch_to.frame(iframe)
                            
                            # Click the checkbox
                            checkbox = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
                            )
                            checkbox.click()
                            
                            driver.switch_to.default_content()
                            logger.info("Recaptcha handled successfully")
                            time.sleep(3)
                            break
                    except Exception as e:
                        driver.switch_to.default_content()
                        logger.warning(f"Recaptcha attempt failed: {str(e)}")
                        
            elif action_type == "screenshot":
                filename = action.get("filename")
                logger.info(f"Taking screenshot: {filename}")
                screenshot_path = os.path.join("screenshots", filename)
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                driver.save_screenshot(screenshot_path)
                
            elif action_type == "custom_js":
                code = action.get("code")
                logger.info("Executing custom JavaScript code")
                try:
                    result = driver.execute_script(code)
                    logger.info(f"Custom JavaScript execution result: {result}")
                    time.sleep(2)  # Wait for JS to complete
                except Exception as e:
                    logger.error(f"Custom JavaScript execution failed: {str(e)}")
                    if action.get("critical", True):
                        raise
                        
            elif action_type == "playwright":
                logger.info("Executing Playwright-style action")
                pw_action = action.get("action")
                selector = action.get("xpath")
                
                try:
                    if pw_action == "click":
                        # Playwright-style click with auto-waiting
                        force = action.get("force", False)
                        timeout = action.get("timeout", 30)
                        logger.info(f"Playwright click: {selector} (force={force}, timeout={timeout})")
                        pw.wait_for_selector_and_click(selector, timeout=timeout, force=force)
                        
                    elif pw_action == "fill":
                        # Playwright-style fill with auto-waiting
                        value = action.get("value")
                        
                        # Replace config values
                        if value == "CONFIG_USERNAME" and 'username' in config_data:
                            value = config_data['username']
                            logger.info(f"Using username from config: {value}")
                        elif value == "CONFIG_PASSWORD" and 'password' in config_data:
                            value = config_data['password']
                            logger.info(f"Using password from config: {value}")
                        elif value == "CONFIG_FORGET_USERNAME" and 'forget_username' in config_data:
                            value = config_data['forget_username']
                            logger.info(f"Using forget username from config: {value}")
                        elif value == "CONFIG_NEW_PASSWORD" and 'new_password' in config_data:
                            value = config_data['new_password']
                            logger.info(f"Using new password from config: {value}")
                        elif value == "CONFIG_NEW_USERNAME" and 'new_username' in config_data:
                            value = config_data['new_username']
                            logger.info(f"Using new username from config: {value}")
                        elif value == "CONFIG_NEW_USER_NAME" and 'new_user_name' in config_data:
                            value = config_data['new_user_name']
                            logger.info(f"Using new user name from config: {value}")
                        elif value == "CONFIG_NEW_USER_EMAIL" and 'new_user_email' in config_data:
                            value = config_data['new_user_email']
                            logger.info(f"Using new user email from config: {value}")
                        elif value == "CONFIG_NEW_USER_PHONE" and 'new_user_phone' in config_data:
                            value = config_data['new_user_phone']
                            logger.info(f"Using new user phone from config: {value}")
                        elif value == "CONFIG_NEW_USER_DOB" and 'new_user_dob' in config_data:
                            value = config_data['new_user_dob']
                            logger.info(f"Using new user DOB from config: {value}")
                        elif value == "CONFIG_NEW_USER_ADDRESS" and 'new_user_address' in config_data:
                            value = config_data['new_user_address']
                            logger.info(f"Using new user address from config: {value}")
                        elif value == "CONFIG_URL" and 'url' in config_data:
                            value = config_data['url']
                            logger.info(f"Using URL from config: {value}")
                            
                        timeout = action.get("timeout", 30)
                        logger.info(f"Playwright fill: {selector} with value: {value}")
                        pw.fill(selector, value, timeout=timeout)
                        
                    elif pw_action == "select_option":
                        # Playwright-style select option
                        value = action.get("value")
                        label = action.get("label")
                        index = action.get("index")
                        
                        # Handle config values for dropdowns if needed
                        if isinstance(value, str) and value.startswith("CONFIG_") and value[7:] in config_data:
                            config_key = value[7:]
                            value = config_data[config_key]
                            logger.info(f"Using {config_key} from config: {value}")
                            
                        timeout = action.get("timeout", 30)
                        logger.info(f"Playwright select_option: {selector} (value={value}, label={label}, index={index})")
                        pw.select_option(selector, value=value, label=label, index=index, timeout=timeout)
                        
                    elif pw_action == "evaluate":
                        # Playwright-style JS evaluation
                        script = action.get("script")
                        arg = action.get("arg")
                        
                        # Replace config values in arg
                        if arg == "CONFIG_URL" and 'url' in config_data:
                            arg = config_data['url']
                            logger.info(f"Using URL from config: {arg}")
                        elif arg == "CONFIG_USERNAME" and 'username' in config_data:
                            arg = config_data['username']
                            logger.info(f"Using username from config: {arg}")
                        elif arg == "CONFIG_PASSWORD" and 'password' in config_data:
                            arg = config_data['password']
                            logger.info(f"Using password from config: {arg}")
                        
                        timeout = action.get("timeout", 30)
                        logger.info(f"Playwright evaluate script with arg: {arg}")
                        pw.evaluate(script, arg=arg, timeout=timeout)
                        
                    else:
                        logger.warning(f"Unknown Playwright action: {pw_action}")
                        
                    # Wait after Playwright action
                    time.sleep(action.get("wait_after", 0.5))
                    
                except Exception as e:
                    logger.error(f"Playwright action failed: {str(e)}")
                    if action.get("critical", True):
                        raise

            elif action_type == "validate":
                xpath = action.get("xpath")
                expected_text = action.get("expected_text", "")
                validation_type = action.get("validation_type", "contains")  # contains, exact, exists, or not_exists

                logger.info(f"Validating element: {xpath} with expected text: '{expected_text}' (type: {validation_type})")
                
                # For exists validation, we need to handle differently
                if validation_type == "exists":
                    try:
                        # Wait for element to be present
                        element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        logger.info(f"Validation (exists): Element found successfully")
                        continue  # Skip the rest of the validation logic
                    except Exception as e:
                        logger.error(f"Validation (exists) failed: Element not found - {str(e)}")
                        if action.get("critical", True):
                            raise
                        continue
                
                try:
                    # Wait for element to be present for other validation types
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )

                    # Get the actual text
                    actual_text = element.text.strip().lower()
                    expected_text_lower = expected_text.strip().lower()

                    # Perform validation based on type
                    validation_passed = False
                    if validation_type == "contains":
                        validation_passed = expected_text_lower in actual_text
                        logger.info(f"Validation (contains): '{expected_text_lower}' in '{actual_text}' = {validation_passed}")
                    elif validation_type == "exact":
                        validation_passed = actual_text == expected_text_lower
                        logger.info(f"Validation (exact): '{actual_text}' == '{expected_text_lower}' = {validation_passed}")
                    elif validation_type == "exists":
                        validation_passed = True  # Element exists, that's enough
                        logger.info(f"Validation (exists): Element found = {validation_passed}")
                    elif validation_type == "not_exists":
                        # For negative scenarios, we expect the element NOT to exist
                        logger.info("Validation (not_exists): Element should not be found")
                        validation_passed = False  # Will be set to True below if element is not found
                    else:
                        logger.warning(f"Unknown validation type: {validation_type}")
                        validation_passed = False

                    if validation_type == "not_exists":
                        # For "not_exists" validation, we expect the element to NOT be found
                        # If element is not found (exception), validation passes
                        if "presence_of_element_located" in str(e) or "NoSuchElementException" in str(e):
                            validation_passed = True
                            logger.info("Validation (not_exists): Element correctly not found = True")
                        else:
                            validation_passed = False
                            logger.error("Validation (not_exists): Element was found when it shouldn't exist")
                    elif not validation_passed:
                        error_msg = f"Validation failed! Expected: '{expected_text}' (type: {validation_type}), Got: '{actual_text}'"
                        logger.error(error_msg)
                        raise AssertionError(error_msg)

                    logger.info("Validation passed successfully")

                except Exception as e:
                    if validation_type == "not_exists":
                        # For "not_exists" validation, if element is not found, that's what we want
                        if "NoSuchElementException" in str(e) or "presence_of_element_located" in str(e):
                            logger.info("Validation (not_exists): Element correctly not found - validation passed")
                            validation_passed = True
                        else:
                            logger.error(f"Validation (not_exists) failed with unexpected error: {str(e)}")
                            raise
                    else:
                        logger.error(f"Validation failed: {str(e)}")
                        # Take error screenshot
                        try:
                            error_path = os.path.join("screenshots", f"validation_error_{i+1}.png")
                            os.makedirs(os.path.dirname(error_path), exist_ok=True)
                            driver.save_screenshot(error_path)
                            logger.info(f"Saved validation error screenshot to {error_path}")
                        except:
                            pass
                        raise

            else:
                logger.warning(f"Unknown action type: {action_type}")
                
        except Exception as e:
            logger.error(f"Failed to execute action {action_type}: {str(e)}")
            
            # Take error screenshot
            try:
                error_path = os.path.join("screenshots", f"error_step_{i+1}.png")
                os.makedirs(os.path.dirname(error_path), exist_ok=True)
                driver.save_screenshot(error_path)
                logger.info(f"Saved error screenshot to {error_path}")
            except:
                pass
                
            if action.get("critical", True):
                raise
    
    logger.info("All actions completed successfully")
    return True
