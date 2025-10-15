import os
import json
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

logger = logging.getLogger(__name__)

class Config:
    """Configuration management for the automation framework"""

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self._config = self._load_config()

    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded successfully")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_file} not found")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing configuration file: {str(e)}")
            return {}

    def get_driver(self):
        """Create and return WebDriver instance"""
        browser_type = self._config.get("browser", "chrome").lower()
        headless = self._config.get("headless", False)

        if browser_type == "firefox":
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
        else:
            # Default to Chrome
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-infobars")

            driver = webdriver.Chrome(options=options)

        # Set timeouts
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)

        logger.info(f"WebDriver initialized: {browser_type}, headless: {headless}")
        return driver

    @property
    def BASE_URL(self):
        """Get base URL"""
        return self._config.get("url", "")

    @property
    def USERNAME(self):
        """Get username"""
        return self._config.get("username", "")

    @property
    def PASSWORD(self):
        """Get password"""
        return self._config.get("password", "")

    @property
    def FORGET_USERNAME(self):
        """Get username for password reset"""
        return self._config.get("forget_username", "")

    @property
    def NEW_USERNAME(self):
        """Get new username for change user"""
        return self._config.get("new_username", "")

    @property
    def NEW_PASSWORD(self):
        """Get new password"""
        return self._config.get("new_password", "")

    @property
    def INVALID_USERNAME(self):
        """Get invalid username for negative testing"""
        return self._config.get("invalid_username", "INVALID_USER_12345")

    @property
    def DB_HOST(self):
        """Get database host"""
        return self._config.get("db_host", "")

    @property
    def DB_PORT(self):
        """Get database port"""
        return self._config.get("db_port", 5432)

    @property
    def DB_NAME(self):
        """Get database name"""
        return self._config.get("db_name", "")

    @property
    def DB_USER(self):
        """Get database user"""
        return self._config.get("db_user", "")

    @property
    def DB_PASSWORD(self):
        """Get database password"""
        return self._config.get("db_password", "")
