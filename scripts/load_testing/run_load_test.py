#!/usr/bin/env python3
"""
Load Testing Script for LMS Automation
"""
import sys
import os
import json
import logging
from src.load_testing.load_tester import run_load_test

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("load_test_execution.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Run load test for LoginLogout workflow"""
    logger.info("=== Starting Load Test Execution ===")

    try:
        # Load test configuration
        num_users = 5  # Start with small number for testing
        ramp_up_time = 10  # 10 seconds ramp-up

        logger.info(f"Load test configuration: {num_users} users, {ramp_up_time}s ramp-up")

        # Run the load test
        results = run_load_test(
            workflow_name="LoginLogout",
            json_path="recordings/LoginLogout/login_logout.json",
            num_users=num_users,
            ramp_up_time=ramp_up_time
        )

        # Display results
        logger.info("=== Load Test Results ===")
        logger.info(f"Total Users: {results['total_users']}")
        logger.info(f"Successful Tests: {results['successful_tests']}")
        logger.info(f"Failed Tests: {results['failed_tests']}")
        logger.info(f"Success Rate: {results['success_rate']:.2f}%")
        logger.info(f"Total Execution Time: {results['total_execution_time']:.2f}s")
        logger.info(f"Average Response Time: {results['avg_response_time']:.2f}s")
        logger.info(f"Min Response Time: {results['min_response_time']:.2f}s")
        logger.info(f"Max Response Time: {results['max_response_time']:.2f}s")
        logger.info(f"Median Response Time: {results['median_response_time']:.2f}s")
        logger.info(f"Throughput: {results['throughput']:.2f} requests/second")

        logger.info(f"Average CPU Usage: {results['avg_cpu_usage']:.2f}%")
        logger.info(f"Average Memory Usage: {results['avg_memory_usage']:.2f}%")

        if results['errors']:
            logger.warning(f"Errors encountered: {len(results['errors'])}")
            logger.warning("First 5 errors:")
            for i, error in enumerate(results['errors'][:5]):
                logger.warning(f"  {i+1}. {error}")

        # Save results to file
        with open('load_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)

        logger.info("Load test results saved to load_test_results.json")

        # Check if test was successful
        if results['success_rate'] >= 80:  # 80% success rate threshold
            logger.info("✅ Load test PASSED - Success rate meets threshold")
            return True
        else:
            logger.warning(f"❌ Load test FAILED - Success rate {results['success_rate']:.2f}% below threshold")
            return False

    except Exception as e:
        logger.error(f"Load test execution failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
