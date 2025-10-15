import logging
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

class Browser:
    def __init__(self, context):
        self.context = context
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.setup_browser()
        
    def setup_browser(self):
        """Initialize the browser with appropriate options"""
        try:
            # Get browser type from context, default to "chrome"
            browser_type = self.context.get("browser_type", "chrome").lower()
            
            if browser_type == "firefox":
                self._setup_firefox()
            else:
                # Default to Chrome
                self._setup_chrome()
                
            # Set timeouts for any browser
            if self.driver:
                self.driver.set_page_load_timeout(30)  # 30 seconds timeout for page loads
                self.driver.set_script_timeout(30)     # 30 seconds timeout for scripts
                self.logger.info(f"Browser ({browser_type}) initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {str(e)}")
            raise
            
    def _setup_chrome(self):
        """Setup Chrome browser"""
        try:
            chrome_options = ChromeOptions()
            if self.context.get("headless", False):
                chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--start-maximized")
            
            # Performance optimizations with eager loading
            chrome_options.page_load_strategy = 'eager'  # Using eager loading as it worked before
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Enable JavaScript
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "download.default_directory": os.path.abspath("downloads"),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            })
            
            # Disable automation flags for better recaptcha handling
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Try multiple methods to initialize Chrome
            driver_initialized = False
            
            # Method 1: Try using chromedriver path from config.json
            try:
                with open('config.json', 'r') as f:
                    config_data = json.load(f)
                    chromedriver_path = config_data.get('chromedriver_path')
                    
                    if chromedriver_path and os.path.exists(chromedriver_path):
                        self.logger.info(f"Using ChromeDriver from config: {chromedriver_path}")
                        service = ChromeService(executable_path=chromedriver_path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        driver_initialized = True
                        self.logger.info("Chrome initialized successfully with config path")
            except Exception as e:
                self.logger.debug(f"Config chromedriver path not available: {str(e)}")
            
            # Method 2: Try using ChromeDriverManager
            if not driver_initialized and WEBDRIVER_MANAGER_AVAILABLE:
                try:
                    self.logger.info("Attempting to use ChromeDriverManager...")
                    service = ChromeService(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver_initialized = True
                    self.logger.info("Chrome initialized successfully with ChromeDriverManager")
                except Exception as e:
                    self.logger.warning(f"ChromeDriverManager failed: {str(e)}")
            
            # Method 3: Try initializing Chrome directly (chromedriver in PATH)
            if not driver_initialized:
                try:
                    self.logger.info("Attempting to use Chrome from PATH...")
                    self.driver = webdriver.Chrome(options=chrome_options)
                    driver_initialized = True
                    self.logger.info("Chrome initialized successfully from PATH")
                except Exception as e:
                    self.logger.error(f"Chrome from PATH failed: {str(e)}")
            
            if not driver_initialized:
                raise Exception("Failed to initialize Chrome with all available methods")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome: {str(e)}")
            self.logger.error("Please ensure Chrome and ChromeDriver are properly installed")
            self.logger.error("You can specify chromedriver_path in config.json or add chromedriver to PATH")
            raise
            
    def _setup_firefox(self):
        """Setup Firefox browser"""
        try:
            firefox_options = FirefoxOptions()
            if self.context.get("headless", False):
                firefox_options.add_argument("--headless")
            firefox_options.page_load_strategy = 'eager'
            
            try:
                # Try using GeckoDriverManager
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
            except Exception as firefox_error:
                self.logger.warning(f"GeckoDriverManager failed: {str(firefox_error)}")
                self.logger.info("Trying to initialize Firefox without GeckoDriverManager")
                # Try initializing Firefox directly
                self.driver = webdriver.Firefox(options=firefox_options)
        except Exception as e:
            self.logger.error(f"Failed to initialize Firefox: {str(e)}")
            # Don't raise here, let the main setup_browser method handle it
            
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed")
            
    def get_driver(self):
        """Return the WebDriver instance"""
        return self.driver
