import pytest
import logging
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utils.config import Config

logger = logging.getLogger(__name__)

class TestLogin:
    """Test cases for login functionality"""

    @pytest.fixture(scope="class")
    def setup(self):
        """Setup test environment"""
        config = Config()
        driver = config.get_driver()
        yield driver
        driver.quit()

    def test_valid_login_logout(self, setup):
        """Test complete login and logout flow"""
        driver = setup
        login_page = LoginPage(driver)
        dashboard_page = DashboardPage(driver)

        # Perform login
        success = login_page.perform_login(
            Config.USERNAME,
            Config.PASSWORD,
            Config.BASE_URL
        )

        assert success, "Login should be successful"

        # Take screenshot
        login_page.take_screenshot("login_success")

        # Verify dashboard is visible
        assert dashboard_page.is_dashboard_visible(), "Dashboard should be visible after login"

        # Perform logout
        logout_success = dashboard_page.perform_logout()
        assert logout_success, "Logout should be successful"

        # Take screenshot
        dashboard_page.take_screenshot("logout_success")

    def test_invalid_username_login(self, setup):
        """Test login with invalid username"""
        driver = setup
        login_page = LoginPage(driver)

        # Perform login with invalid username
        success = login_page.perform_login(
            "INVALID_USER_12345",
            Config.PASSWORD,
            Config.BASE_URL
        )

        assert not success, "Login with invalid username should fail"

        # Verify error message is displayed
        assert login_page.is_error_displayed(), "Error message should be displayed"

        error_msg = login_page.get_error_message()
        assert "User does not exist" in error_msg.lower(), f"Expected 'User does not exist' error, got: {error_msg}"

        # Take screenshot
        login_page.take_screenshot("login_invalid_error")
