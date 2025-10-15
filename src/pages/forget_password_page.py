import logging
import time
from selenium.webdriver.common.by import By
from .base_page import BasePage

logger = logging.getLogger(__name__)

class ForgetPasswordPage(BasePage):
    """Forget password page locators and actions"""

    # Locators
    FORGET_USERNAME_FIELD = (By.NAME, "username")
    SEND_OTP_BUTTON = (By.XPATH, "//button[contains(text(), 'Send OTP') or @type='submit']")
    OTP_INPUT_FIELDS = (By.XPATH, "//input[contains(@id, 'otp-input') or contains(@placeholder, 'OTP')]")
    NEW_PASSWORD_FIELD = (By.NAME, "new_password")
    CONFIRM_PASSWORD_FIELD = (By.NAME, "confirm_password")
    RESET_BUTTON = (By.XPATH, "//button[contains(text(), 'Reset') or @type='submit']")
    ERROR_MESSAGE = (By.XPATH, "//div[contains(@class, 'error') or contains(text(), 'User does not exist')]")
    SUCCESS_MESSAGE = (By.XPATH, "//div[contains(@class, 'success') or contains(text(), 'Password reset successfully')]")

    def __init__(self, driver):
        super().__init__(driver)
        self.url = None  # Will be set from config

    def navigate_to_forget_password(self, url):
        """Navigate to forget password page"""
        self.driver.get(url)
        self.wait_for_page_load()
        logger.info("Navigated to forget password page")

    def enter_forget_username(self, username):
        """Enter username for password reset"""
        return self.enter_text(self.FORGET_USERNAME_FIELD, username)

    def click_send_otp(self):
        """Click send OTP button"""
        return self.click_element(self.SEND_OTP_BUTTON)

    def enter_otp_digits(self, otp_digits):
        """Enter OTP digits into individual input fields"""
        try:
            otp_fields = self.driver.find_elements(*self.OTP_INPUT_FIELDS)

            if len(otp_fields) != len(otp_digits):
                logger.error(f"OTP field count mismatch: expected {len(otp_digits)}, found {len(otp_fields)}")
                return False

            for i, field in enumerate(otp_fields):
                if i < len(otp_digits):
                    field.clear()
                    field.send_keys(otp_digits[i])
                    logger.info(f"Entered OTP digit {i+1}: {otp_digits[i]}")

            return True
        except Exception as e:
            logger.error(f"Error entering OTP digits: {str(e)}")
            return False

    def enter_new_password(self, password):
        """Enter new password"""
        return self.enter_text(self.NEW_PASSWORD_FIELD, password)

    def enter_confirm_password(self, password):
        """Enter confirm password"""
        return self.enter_text(self.CONFIRM_PASSWORD_FIELD, password)

    def click_reset_button(self):
        """Click reset password button"""
        return self.click_element(self.RESET_BUTTON)

    def get_error_message(self):
        """Get error message if password reset fails"""
        return self.get_element_text(self.ERROR_MESSAGE)

    def get_success_message(self):
        """Get success message if password reset succeeds"""
        return self.get_element_text(self.SUCCESS_MESSAGE)

    def is_error_displayed(self):
        """Check if error message is displayed"""
        return self.is_element_visible(self.ERROR_MESSAGE)

    def is_success_displayed(self):
        """Check if success message is displayed"""
        return self.is_element_visible(self.SUCCESS_MESSAGE)

    def perform_forget_password_flow(self, username, otp_digits, new_password, url):
        """Complete forget password flow"""
        self.navigate_to_forget_password(url)

        if not self.enter_forget_username(username):
            return False

        time.sleep(2)

        if not self.click_send_otp():
            return False

        time.sleep(3)  # Wait for OTP to be sent

        if not self.enter_otp_digits(otp_digits):
            return False

        time.sleep(2)

        if not self.enter_new_password(new_password):
            return False

        time.sleep(1)

        if not self.enter_confirm_password(new_password):
            return False

        time.sleep(1)

        if not self.click_reset_button():
            return False

        time.sleep(3)  # Wait for reset completion

        # Check for error or success
        if self.is_error_displayed():
            error_msg = self.get_error_message()
            logger.error(f"Password reset failed: {error_msg}")
            return False

        if self.is_success_displayed():
            logger.info("Password reset completed successfully")
            return True

        logger.warning("Password reset status unclear")
        return False
