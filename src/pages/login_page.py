import logging
import time
from selenium.webdriver.common.by import By
from .base_page import BasePage

logger = logging.getLogger(__name__)

class LoginPage(BasePage):
    """Login page locators and actions"""

    # Locators
    USERNAME_FIELD = (By.NAME, "username")
    PASSWORD_FIELD = (By.NAME, "password")
    LOGIN_BUTTON = (By.XPATH, "//button[contains(text(), 'Proceed') or @type='submit']")
    ERROR_MESSAGE = (By.XPATH, "//div[contains(@class, 'error') or contains(text(), 'User does not exist')]")
    CAPTCHA_IFRAME = (By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
    CAPTCHA_CHECKBOX = (By.ID, "recaptcha-anchor")

    def __init__(self, driver):
        super().__init__(driver)
        self.url = None  # Will be set from config

    def navigate_to_login(self, url):
        """Navigate to login page"""
        self.driver.get(url)
        self.wait_for_page_load()
        logger.info("Navigated to login page")

    def enter_username(self, username):
        """Enter username in login field"""
        return self.enter_text(self.USERNAME_FIELD, username)

    def enter_password(self, password):
        """Enter password in password field"""
        return self.enter_text(self.PASSWORD_FIELD, password)

    def handle_captcha(self):
        """Handle reCAPTCHA if present"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src")
                if src and "recaptcha" in src.lower():
                    self.driver.switch_to.frame(iframe)

                    # Click the checkbox
                    if self.click_element(self.CAPTCHA_CHECKBOX, timeout=5):
                        logger.info("CAPTCHA checkbox clicked")
                        self.driver.switch_to.default_content()
                        time.sleep(3)  # Wait for CAPTCHA processing
                        return True

                    self.driver.switch_to.default_content()
            return False
        except Exception as e:
            logger.warning(f"Error handling CAPTCHA: {str(e)}")
            return False

    def click_login_button(self):
        """Click the login button"""
        return self.click_element(self.LOGIN_BUTTON)

    def get_error_message(self):
        """Get error message if login fails"""
        return self.get_element_text(self.ERROR_MESSAGE)

    def is_error_displayed(self):
        """Check if error message is displayed"""
        return self.is_element_visible(self.ERROR_MESSAGE)

    def perform_login(self, username, password, url):
        """Complete login flow"""
        self.navigate_to_login(url)

        if not self.enter_username(username):
            return False

        time.sleep(2)  # Wait for UI

        self.handle_captcha()
        time.sleep(2)  # Wait for CAPTCHA

        if not self.click_login_button():
            return False

        time.sleep(2)  # Wait for login processing

        if not self.enter_password(password):
            return False

        time.sleep(1)

        if not self.click_login_button():
            return False

        time.sleep(3)  # Wait for login completion

        # Check for error message
        if self.is_error_displayed():
            error_msg = self.get_error_message()
            logger.error(f"Login failed: {error_msg}")
            return False

        logger.info("Login completed successfully")
        return True
