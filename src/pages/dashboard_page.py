import logging
import time
from selenium.webdriver.common.by import By
from .base_page import BasePage

logger = logging.getLogger(__name__)

class DashboardPage(BasePage):
    """Dashboard page locators and actions"""

    # Locators
    USER_MENU_BUTTON = (By.XPATH, "//*[@id='root']/div/div[1]/div[1]/div/div[2]/div/div[2]/button")
    LOGOUT_BUTTON = (By.XPATH, "/html/body/div[3]/div[3]/ul/div[3]/button[2]")
    DASHBOARD_CONTENT = (By.XPATH, "//div[contains(@class, 'dashboard') or contains(text(), 'Welcome')]")
    USER_PROFILE_LINK = (By.XPATH, "//a[contains(text(), 'Profile') or contains(@href, 'profile')]")

    def __init__(self, driver):
        super().__init__(driver)

    def click_user_menu(self):
        """Click on user menu button"""
        return self.click_element(self.USER_MENU_BUTTON)

    def click_logout_button(self):
        """Click on logout button"""
        return self.click_element(self.LOGOUT_BUTTON)

    def perform_logout(self):
        """Complete logout flow"""
        if not self.click_user_menu():
            return False

        time.sleep(2)  # Wait for menu to appear

        if not self.click_logout_button():
            return False

        time.sleep(2)  # Wait for logout to complete

        logger.info("Logout completed successfully")
        return True

    def is_dashboard_visible(self):
        """Check if dashboard content is visible"""
        return self.is_element_visible(self.DASHBOARD_CONTENT)

    def click_profile_link(self):
        """Click on profile link"""
        return self.click_element(self.USER_PROFILE_LINK)

    def navigate_to_profile(self):
        """Navigate to user profile page"""
        if not self.click_user_menu():
            return False

        time.sleep(2)

        if not self.click_profile_link():
            return False

        time.sleep(3)  # Wait for profile page to load

        logger.info("Navigated to profile page")
        return True
