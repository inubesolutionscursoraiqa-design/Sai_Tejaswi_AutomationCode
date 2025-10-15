import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class BasePage:
    """Base page class containing common Selenium methods for all pages"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def click_element(self, locator, timeout=10):
        """Click an element with explicit wait"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
            logger.info(f"Clicked element: {locator}")
            return True
        except TimeoutException:
            logger.error(f"Timeout clicking element: {locator}")
            return False
        except Exception as e:
            logger.error(f"Error clicking element {locator}: {str(e)}")
            return False

    def enter_text(self, locator, text, timeout=10):
        """Enter text into an input field with explicit wait"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            # Clear field first
            element.clear()
            element.send_keys(text)
            logger.info(f"Entered text '{text}' into element: {locator}")
            return True
        except TimeoutException:
            logger.error(f"Timeout entering text into element: {locator}")
            return False
        except Exception as e:
            logger.error(f"Error entering text into element {locator}: {str(e)}")
            return False

    def wait_for_element(self, locator, timeout=10):
        """Wait for element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            logger.info(f"Element found: {locator}")
            return element
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {locator}")
            return None

    def get_element_text(self, locator, timeout=10):
        """Get text from an element"""
        try:
            element = self.wait_for_element(locator, timeout)
            if element:
                text = element.text.strip()
                logger.info(f"Got text '{text}' from element: {locator}")
                return text
            return ""
        except Exception as e:
            logger.error(f"Error getting text from element {locator}: {str(e)}")
            return ""

    def is_element_visible(self, locator, timeout=5):
        """Check if element is visible"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            logger.info(f"Element is visible: {locator}")
            return True
        except TimeoutException:
            logger.debug(f"Element not visible: {locator}")
            return False
        except Exception as e:
            logger.error(f"Error checking element visibility {locator}: {str(e)}")
            return False

    def take_screenshot(self, filename):
        """Take screenshot and save to reports/screenshots"""
        try:
            screenshot_path = f"reports/screenshots/{filename}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return None

    def wait_for_page_load(self, timeout=30):
        """Wait for page to load completely"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            logger.info("Page loaded completely")
            return True
        except TimeoutException:
            logger.warning("Page load timeout")
            return False

    def switch_to_frame(self, frame_locator):
        """Switch to iframe"""
        try:
            self.driver.switch_to.frame(frame_locator)
            logger.info(f"Switched to frame: {frame_locator}")
            return True
        except Exception as e:
            logger.error(f"Error switching to frame {frame_locator}: {str(e)}")
            return False

    def switch_to_default_content(self):
        """Switch back to main content"""
        try:
            self.driver.switch_to.default_content()
            logger.info("Switched to default content")
            return True
        except Exception as e:
            logger.error(f"Error switching to default content: {str(e)}")
            return False

    def scroll_to_element(self, locator):
        """Scroll to element"""
        try:
            element = self.wait_for_element(locator)
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                logger.info(f"Scrolled to element: {locator}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error scrolling to element {locator}: {str(e)}")
            return False
