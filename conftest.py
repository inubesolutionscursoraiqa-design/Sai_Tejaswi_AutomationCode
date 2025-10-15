import pytest
import logging
from src.utils.config import Config

# Setup logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_execution.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def config():
    """Provide configuration object for all tests"""
    return Config()

@pytest.fixture(scope="function")
def driver(config):
    """Provide WebDriver instance for each test"""
    driver = config.get_driver()
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def login_page(driver):
    """Provide LoginPage instance for tests"""
    from src.pages.login_page import LoginPage
    return LoginPage(driver)

@pytest.fixture(scope="function")
def dashboard_page(driver):
    """Provide DashboardPage instance for tests"""
    from src.pages.dashboard_page import DashboardPage
    return DashboardPage(driver)

@pytest.fixture(scope="function")
def forget_password_page(driver):
    """Provide ForgetPasswordPage instance for tests"""
    from src.pages.forget_password_page import ForgetPasswordPage
    return ForgetPasswordPage(driver)

@pytest.fixture(scope="function")
def change_user_page(driver):
    """Provide ChangeUserPage instance for tests"""
    from src.pages.change_user_page import ChangeUserPage
    return ChangeUserPage(driver)
