import time
import json
import logging
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

@dataclass
class LoadTestResult:
    """Data class for load test results"""
    user_id: int
    execution_time: float
    success: bool
    error_message: str = ""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0

class LoadTester:
    """Load testing implementation for LMS workflows"""

    def __init__(self, workflow_name, json_path, config_path="src/utils/config.json"):
        self.workflow_name = workflow_name
        self.json_path = json_path
        self.config_path = config_path
        self.results = []
        self.start_time = None

    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return {}

    def _create_driver(self, config):
        """Create WebDriver instance"""
        browser_type = config.get("browser", "chrome").lower()
        headless = config.get("headless", True)  # Default to headless for load testing

        if browser_type == "firefox":
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
        else:
            from selenium.webdriver.chrome.options import Options as ChromeOptions
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
        return driver

    def _run_single_user_test(self, user_id: int, config: Dict[str, Any]) -> LoadTestResult:
        """Run a single user test scenario"""
        start_time = time.time()

        try:
            # Create driver instance for this user
            driver = self._create_driver(config)

            # Load and run the workflow
            success = self._execute_workflow(driver, config)

            execution_time = time.time() - start_time

            return LoadTestResult(
                user_id=user_id,
                execution_time=execution_time,
                success=success,
                cpu_usage=0.0,  # Could add psutil for system monitoring
                memory_usage=0.0
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return LoadTestResult(
                user_id=user_id,
                execution_time=execution_time,
                success=False,
                error_message=str(e),
                cpu_usage=0.0,
                memory_usage=0.0
            )
        finally:
            # Ensure driver is closed
            try:
                if 'driver' in locals():
                    driver.quit()
            except:
                pass

    def _execute_workflow(self, driver, config):
        """Execute the workflow using the JSON recording"""
        try:
            # Load the JSON recording
            with open(self.json_path, 'r') as f:
                actions = json.load(f)

            # Execute actions
            for action in actions:
                action_type = action.get("type")

                if action_type == "goto":
                    url = action.get("url")
                    if url == "CONFIG_URL" and 'url' in config:
                        url = config['url']
                    driver.get(url)
                    time.sleep(3)

                elif action_type == "wait":
                    seconds = action.get("seconds", 1)
                    time.sleep(seconds)

                elif action_type == "input":
                    xpath = action.get("xpath")
                    value = action.get("value")

                    # Replace with config values if needed
                    if value == "CONFIG_USERNAME" and 'username' in config:
                        value = config['username']
                    elif value == "CONFIG_PASSWORD" and 'password' in config:
                        value = config['password']

                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    element.clear()
                    element.send_keys(value)
                    time.sleep(1)

                elif action_type == "click":
                    xpath = action.get("xpath")
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    element.click()
                    time.sleep(1)

                elif action_type == "screenshot":
                    filename = action.get("filename")
                    driver.save_screenshot(f"screenshots/{filename}")

            return True

        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return False

    def run_load_test(self, num_users: int, ramp_up_time: int = 0) -> Dict[str, Any]:
        """
        Run load test with specified number of concurrent users

        Args:
            num_users: Number of concurrent users to simulate
            ramp_up_time: Time in seconds to gradually increase users (0 = all at once)
        """
        self.start_time = time.time()
        self.results = []

        logger.info(f"Starting load test: {self.workflow_name} with {num_users} users")

        # Load configuration
        config = self._load_config()

        if ramp_up_time > 0:
            # Gradual ramp-up
            users_per_second = num_users / ramp_up_time
            logger.info(f"Ramping up {num_users} users over {ramp_up_time} seconds")

            with ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = []

                for user_id in range(num_users):
                    # Calculate delay for gradual ramp-up
                    delay = (user_id / users_per_second) if ramp_up_time > 0 else 0

                    # Schedule user test with delay
                    future = executor.submit(self._run_delayed_user_test, user_id, config, delay)
                    futures.append(future)

                # Collect results
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        self.results.append(result)
                    except Exception as e:
                        logger.error(f"Error collecting result: {str(e)}")
        else:
            # All users at once
            logger.info(f"Running {num_users} users concurrently")

            with ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = []

                for user_id in range(num_users):
                    future = executor.submit(self._run_single_user_test, user_id, config)
                    futures.append(future)

                # Collect results
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        self.results.append(result)
                    except Exception as e:
                        logger.error(f"Error collecting result: {str(e)}")

        # Calculate summary statistics
        return self._generate_report()

    def _run_delayed_user_test(self, user_id: int, config: Dict[str, Any], delay: float) -> LoadTestResult:
        """Run a user test with specified delay"""
        if delay > 0:
            time.sleep(delay)
        return self._run_single_user_test(user_id, config)

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive load test report"""
        total_time = time.time() - self.start_time

        successful_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]

        execution_times = [r.execution_time for r in self.results]

        report = {
            'workflow_name': self.workflow_name,
            'total_users': len(self.results),
            'successful_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'success_rate': (len(successful_tests) / len(self.results)) * 100 if self.results else 0,
            'total_execution_time': total_time,
            'avg_response_time': statistics.mean(execution_times) if execution_times else 0,
            'min_response_time': min(execution_times) if execution_times else 0,
            'max_response_time': max(execution_times) if execution_times else 0,
            'median_response_time': statistics.median(execution_times) if execution_times else 0,
            'throughput': len(self.results) / total_time if total_time > 0 else 0,  # requests per second
            'errors': [r.error_message for r in failed_tests],
            'detailed_results': self.results
        }

        return report

def run_load_test(workflow_name: str, json_path: str, num_users: int, ramp_up_time: int = 0) -> Dict[str, Any]:
    """
    Convenience function to run load test

    Args:
        workflow_name: Name of the workflow being tested
        json_path: Path to the JSON recording file
        num_users: Number of concurrent users
        ramp_up_time: Ramp-up time in seconds

    Returns:
        Dictionary containing load test results
    """
    tester = LoadTester(workflow_name, json_path)
    return tester.run_load_test(num_users, ramp_up_time)
