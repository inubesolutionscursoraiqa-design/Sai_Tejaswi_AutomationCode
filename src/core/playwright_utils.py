"""
Playwright-inspired utilities for Selenium to handle DOM changes more effectively
"""
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

logger = logging.getLogger(__name__)

class PlaywrightUtils:
    """
    Utilities that mimic Playwright's auto-waiting and robust element handling
    for use with Selenium WebDriver
    """
    
    def __init__(self, driver):
        """Initialize with a Selenium WebDriver instance"""
        self.driver = driver
        self.default_timeout = 30  # seconds
        
    def wait_for_selector(self, selector, timeout=None):
        """
        Wait for an element matching the selector to be present in DOM
        
        Args:
            selector: XPath selector string
            timeout: Timeout in seconds (uses default_timeout if None)
            
        Returns:
            The found element
        """
        if timeout is None:
            timeout = self.default_timeout
            
        logger.info(f"Waiting for selector: {selector} (timeout: {timeout}s)")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
            logger.info(f"Found element for selector: {selector}")
            return element
        except TimeoutException:
            logger.error(f"Timeout waiting for selector: {selector}")
            raise
            
    def wait_for_selector_and_click(self, selector, timeout=None, force=False):
        """
        Wait for element and click it when it's ready
        
        Args:
            selector: XPath selector string
            timeout: Timeout in seconds
            force: If True, use JavaScript to click
        """
        element = self.wait_for_selector(selector, timeout)
        
        # Ensure element is visible and scrolled into view
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        
        try:
            if force:
                logger.info(f"Force-clicking element using JavaScript: {selector}")
                self.driver.execute_script("arguments[0].click();", element)
            else:
                logger.info(f"Clicking element: {selector}")
                # Wait for element to be clickable
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                element.click()
            
            logger.info(f"Successfully clicked element: {selector}")
            return True
        except Exception as e:
            logger.warning(f"Click failed, trying JavaScript click: {str(e)}")
            try:
                self.driver.execute_script("arguments[0].click();", element)
                logger.info(f"JavaScript click successful: {selector}")
                return True
            except Exception as js_e:
                logger.error(f"JavaScript click also failed: {str(js_e)}")
                raise
                
    def fill(self, selector, value, timeout=None):
        """
        Fill an input field with the given value
        
        Args:
            selector: XPath selector string
            value: Value to fill
            timeout: Timeout in seconds
        """
        element = self.wait_for_selector(selector, timeout)
        
        # Clear the field
        try:
            element.clear()
            time.sleep(0.1)
        except:
            logger.warning(f"Could not clear element, trying JavaScript clear")
            self.driver.execute_script("arguments[0].value = '';", element)
            
        # Type the value
        try:
            element.send_keys(value)
            logger.info(f"Filled element {selector} with value: {value}")
            return True
        except Exception as e:
            logger.warning(f"Send keys failed, trying JavaScript: {str(e)}")
            try:
                self.driver.execute_script(f"arguments[0].value = '{value}';", element)
                logger.info(f"JavaScript fill successful: {value}")
                return True
            except Exception as js_e:
                logger.error(f"JavaScript fill also failed: {str(js_e)}")
                raise
                
    def select_option(self, selector, value=None, label=None, index=None, timeout=None):
        """
        Select an option from a dropdown (handles both native and custom dropdowns)
        
        Args:
            selector: XPath selector for the dropdown
            value: Option value to select
            label: Option text to select
            index: Option index to select
            timeout: Timeout in seconds
        """
        # First check if this is a MUI select
        is_mui = False
        try:
            html = self.driver.page_source.lower()
            if "mui" in html or "material-ui" in html:
                is_mui = True
                logger.info("Detected Material-UI components")
        except:
            pass
            
        if is_mui:
            return self._handle_mui_select(selector, value, label, index, timeout)
        else:
            return self._handle_standard_select(selector, value, label, index, timeout)
            
    def _handle_mui_select(self, selector, value=None, label=None, index=None, timeout=None):
        """Handle Material-UI select components"""
        logger.info(f"Handling MUI select: {selector} with value: {value}, label: {label}")
        
        # Try to determine the field name from the selector
        field_name = None
        if "user_type" in selector.lower():
            field_name = "user_type_id"
        elif "role" in selector.lower():
            field_name = "role_id"
            
        # Execute specialized JavaScript to handle MUI select
        script = f"""
        (function() {{
            try {{
                // 1. Find the select element
                let selectElement = document.evaluate("{selector}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (!selectElement) {{
                    console.error('Select element not found');
                    return false;
                }}
                
                // 2. Determine if this is a MUI select
                const isMuiSelect = selectElement.id && selectElement.id.includes('mui-component-select');
                const fieldName = {repr(field_name) if field_name else 'null'};
                
                // 3. Handle MUI select
                if (isMuiSelect || fieldName) {{
                    // Find the hidden input
                    let hiddenInput = fieldName ? 
                        document.querySelector(`input[name="${{fieldName}}"]`) : 
                        document.querySelector('input[type="hidden"][class*="MuiSelect-nativeInput"]');
                    
                    if (hiddenInput) {{
                        // Set the value directly
                        hiddenInput.value = {repr(value) if value else '"1"'};
                        
                        // Update the visible text
                        selectElement.textContent = {repr(label) if label else '"EXTERNAL"'};
                        
                        // Dispatch events
                        const event = new Event('change', {{ bubbles: true }});
                        hiddenInput.dispatchEvent(event);
                        
                        console.log('Successfully set MUI select value');
                        return true;
                    }}
                }}
                
                // 4. Fallback: Click to open dropdown
                selectElement.click();
                
                // 5. Wait for dropdown to open and select option
                setTimeout(() => {{
                    const options = document.querySelectorAll('li[role="option"]');
                    let targetOption = null;
                    
                    // Find by value
                    if ({repr(value) if value else 'null'}) {{
                        for (const opt of options) {{
                            if (opt.getAttribute('data-value') === {repr(value) if value else 'null'}) {{
                                targetOption = opt;
                                break;
                            }}
                        }}
                    }}
                    
                    // Find by text
                    if (!targetOption && {repr(label) if label else 'null'}) {{
                        for (const opt of options) {{
                            if (opt.textContent.includes({repr(label) if label else 'null'})) {{
                                targetOption = opt;
                                break;
                            }}
                        }}
                    }}
                    
                    // Find by index
                    if (!targetOption && {repr(index) if index is not None else 'null'} !== null) {{
                        targetOption = options[{index if index is not None else 0}];
                    }}
                    
                    // Click the option
                    if (targetOption) {{
                        targetOption.click();
                        console.log('Successfully clicked option');
                        return true;
                    }}
                    
                    return false;
                }}, 500);
                
                return true;
            }} catch (error) {{
                console.error('Error in MUI select handling:', error);
                return false;
            }}
        }})();
        """
        
        try:
            result = self.driver.execute_script(script)
            time.sleep(1)  # Wait for the dropdown to close
            logger.info(f"MUI select script result: {result}")
            return True
        except Exception as e:
            logger.error(f"MUI select script failed: {str(e)}")
            return False
            
    def _handle_standard_select(self, selector, value=None, label=None, index=None, timeout=None):
        """Handle standard HTML select elements"""
        element = self.wait_for_selector(selector, timeout)
        
        # TODO: Implement standard select handling if needed
        return False
        
    def evaluate(self, script, arg=None, timeout=None):
        """
        Evaluate JavaScript in the page context
        
        Args:
            script: JavaScript to execute
            arg: Argument to pass to the script
            timeout: Timeout in seconds
            
        Returns:
            The result of the script execution
        """
        try:
            if arg:
                result = self.driver.execute_script(script, arg)
            else:
                result = self.driver.execute_script(script)
                
            logger.info(f"Script evaluation successful")
            return result
        except Exception as e:
            logger.error(f"Script evaluation failed: {str(e)}")
            raise
