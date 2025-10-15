#!/usr/bin/env python3
"""
Script to run all workflows and generate comprehensive reports
"""
import subprocess
import sys
import os
import time
import logging

# Add project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.core.report_generator import generate_module_report

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("workflow_execution.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_workflow(workflow_path):
    """Run a single workflow and return success status"""
    try:
        logger.info(f"Running workflow: {workflow_path}")
        result = subprocess.run(
            [sys.executable, "run.py", workflow_path, "--headless"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            logger.info(f"✅ Workflow {workflow_path} completed successfully")
            return True
        else:
            logger.warning(f"❌ Workflow {workflow_path} failed with return code {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"⏰ Workflow {workflow_path} timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error running workflow {workflow_path}: {str(e)}")
        return False

def run_all_workflows():
    """Run all available workflows"""
    logger.info("=== Starting All Workflows Execution ===")

    # Define all workflows to run
    workflows = [
        "LoginLogout/login_logout",
        "LoginLogout/login_invalid_negative",
        "ForgetPassword/forget_password",
        "ForgetPassword/forget_password_invalid_username_negative",
        "ForgetPassword/forget_password_mismatch_negative",
        "ForgetPassword/forget_password_wrong_otp_negative",
        "ChangeUser/change_user",
        "ChangeUser/change_user_invalid_negative",
        "Resend_OTP/resend_otp",
        "Resend_OTP/resend_otp_rate_limit_negative"
    ]

    results = {}

    for workflow in workflows:
        logger.info(f"Executing: {workflow}")
        success = run_workflow(workflow)
        results[workflow] = success

        # Small delay between workflows to avoid overwhelming the system
        time.sleep(2)

    # Summary
    successful = sum(results.values())
    total = len(results)

    logger.info("=== Execution Summary ===")
    logger.info(f"Total Workflows: {total}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {total - successful}")
    logger.info(f"Success Rate: {(successful/total)*100:.2f}%")

    # Detailed results
    logger.info("=== Detailed Results ===")
    for workflow, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{workflow}: {status}")

    return results

def main():
    """Main execution function"""
    try:
        # Run all workflows
        workflow_results = run_all_workflows()

        # Generate comprehensive report
        logger.info("Generating comprehensive report...")
        report_path = generate_comprehensive_report(format='pdf')

        if report_path:
            logger.info(f"✅ Comprehensive report generated: {report_path}")

            # Check if PDF was generated or HTML fallback
            if report_path.endswith('.pdf'):
                logger.info("📄 PDF report with charts and detailed analysis created")
            else:
                logger.info("🌐 HTML report created (PDF libraries not available)")

        else:
            logger.error("❌ Failed to generate comprehensive report")

        return True

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

