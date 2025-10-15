import logging
import time
from selenium.webdriver.common.by import By
from .base_page import BasePage

logger = logging.getLogger(__name__)

class ChangeUserPage(BasePage):
    """Change user profile page locators and actions"""

    # Locators
    FIRST_NAME_FIELD = (By.NAME, "firstName")
    LAST_NAME_FIELD = (By.NAME, "lastName")
    EMAIL_FIELD = (By.NAME, "email")
    PHONE_FIELD = (By.NAME, "phone")
    SAVE_BUTTON = (By.XPATH, "//button[contains(text(), 'Save') or @type='submit']")
    CANCEL_BUTTON = (By.XPATH, "//button[contains(text(), 'Cancel')]")
    ERROR_MESSAGE = (By.XPATH, "//div[contains(@class, 'error') or contains(text(), 'validation')]")
    SUCCESS_MESSAGE = (By.XPATH, "//div[contains(@class, 'success') or contains(text(), 'updated successfully')]")

    def __init__(self, driver):
        super().__init__(driver)

    def enter_first_name(self, first_name):
        """Enter first name"""
        return self.enter_text(self.FIRST_NAME_FIELD, first_name)

    def enter_last_name(self, last_name):
        """Enter last name"""
        return self.enter_text(self.LAST_NAME_FIELD, last_name)

    def enter_email(self, email):
        """Enter email"""
        return self.enter_text(self.EMAIL_FIELD, email)

    def enter_phone(self, phone):
        """Enter phone number"""
        return self.enter_text(self.PHONE_FIELD, phone)

    def click_save_button(self):
        """Click save button"""
        return self.click_element(self.SAVE_BUTTON)

    def click_cancel_button(self):
        """Click cancel button"""
        return self.click_element(self.CANCEL_BUTTON)

    def get_error_message(self):
        """Get error message if save fails"""
        return self.get_element_text(self.ERROR_MESSAGE)

    def get_success_message(self):
        """Get success message if save succeeds"""
        return self.get_element_text(self.SUCCESS_MESSAGE)

    def is_error_displayed(self):
        """Check if error message is displayed"""
        return self.is_element_visible(self.ERROR_MESSAGE)

    def is_success_displayed(self):
        """Check if success message is displayed"""
        return self.is_element_visible(self.SUCCESS_MESSAGE)

    def perform_change_user(self, first_name, last_name, email, phone):
        """Complete change user flow"""
        if not self.enter_first_name(first_name):
            return False

        time.sleep(1)

        if not self.enter_last_name(last_name):
            return False

        time.sleep(1)

        if not self.enter_email(email):
            return False

        time.sleep(1)

        if not self.enter_phone(phone):
            return False

        time.sleep(1)

        if not self.click_save_button():
            return False

        time.sleep(3)  # Wait for save completion

        # Check for error or success
        if self.is_error_displayed():
            error_msg = self.get_error_message()
            logger.error(f"User change failed: {error_msg}")
            return False

        if self.is_success_displayed():
            logger.info("User profile updated successfully")
            return True

        logger.warning("User change status unclear")
        return False

    def perform_negative_change_user(self, first_name, last_name, email, phone):
        """Perform change user with invalid data (for negative testing)"""
        if not self.enter_first_name(first_name):
            return False

        time.sleep(1)

        if not self.enter_last_name(last_name):
            return False

        time.sleep(1)

        if not self.enter_email(email):
            return False

        time.sleep(1)

        if not self.enter_phone(phone):
            return False

        time.sleep(1)

        if not self.click_save_button():
            return False

        time.sleep(3)  # Wait for validation

        # Should show error for invalid data
        if self.is_error_displayed():
            error_msg = self.get_error_message()
            logger.info(f"Validation error correctly shown: {error_msg}")
            return True

        logger.warning("Expected validation error not shown")
        return False
