import logging
import json
from .load_tester import run_load_test

logger = logging.getLogger(__name__)

def execute(context):
    """
    Execute load testing for login workflow

    Args:
        context: Dictionary containing execution context with load test parameters
    """
    logger.info("=== Starting Load Test ===")

    # Load test parameters from context
    num_users = context.get('num_users', 10)
    ramp_up_time = context.get('ramp_up_time', 30)  # 30 seconds ramp-up
    duration = context.get('duration', 300)  # 5 minutes total duration

    try:
        # Run load test
        results = run_load_test(
            workflow_name="LoginLogout",
            json_path="recordings/LoginLogout/login_logout.json",
            num_users=num_users,
            ramp_up_time=ramp_up_time
        )

        # Log results
        logger.info("=== Load Test Results ===")
        logger.info(f"Total Users: {results['total_users']}")
        logger.info(f"Success Rate: {results['success_rate']:.2f}%")
        logger.info(f"Average Response Time: {results['avg_response_time']:.2f}s")
        logger.info(f"Throughput: {results['throughput']:.2f} requests/second")
        logger.info(f"Average CPU Usage: {results['avg_cpu_usage']:.2f}%")
        logger.info(f"Average Memory Usage: {results['avg_memory_usage']:.2f}%")

        if results['errors']:
            logger.warning(f"Errors encountered: {len(results['errors'])}")
            for error in results['errors'][:5]:  # Show first 5 errors
                logger.warning(f"Error: {error}")

        # Save detailed results to file
        with open('load_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)

        logger.info("Load test results saved to load_test_results.json")

        return results

    except Exception as e:
        logger.error(f"Load test failed: {str(e)}")
        raise

