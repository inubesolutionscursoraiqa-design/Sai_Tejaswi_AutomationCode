import argparse
import importlib
import logging
import os
import sys

# Initialize core module to set up logging and directories
import src.core

logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run automation workflows")
    parser.add_argument("workflow", help="Workflow to run (format: CaseName/step_name)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--browser", choices=["chrome", "firefox"], default="chrome",
                        help="Browser to use (default: chrome)")
    parser.add_argument("--username", help="Username for login")
    parser.add_argument("--password", help="Password for login")
    return parser.parse_args()

def main():
    """Main entry point for the automation runner"""
    args = parse_args()
    
    # Parse workflow path
    try:
        case_name, step_name = args.workflow.split("/")
    except ValueError:
        logger.error("Workflow must be in format 'CaseName/step_name'")
        sys.exit(1)
    
    # Check if workflow exists
    module_path = f"workflows.{case_name}.{step_name}"
    print(f"Attempting to import module: {module_path}")
    try:
        workflow_module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        print(f"Module not found error: {str(e)}")
        logger.error(f"Workflow {args.workflow} not found")
        sys.exit(1)
    
    # Create context
    context = {
        "headless": args.headless,
        "workflow": args.workflow,
        "browser_type": args.browser
    }
    
    # Execute workflow
    logger.info(f"Executing workflow: {args.workflow}")
    try:
        workflow_module.execute(context)
        logger.info(f"Workflow {args.workflow} completed successfully")
    except Exception as e:
        logger.error(f"Workflow {args.workflow} failed: {str(e)}")
        sys.exit(1)

    # Special handling for ForgetPassword workflow
    if case_name == "ForgetPassword" and step_name == "forget_password":
        logger.info("Forget Password workflow completed - check screenshots for results")

    # Special handling for ChangeUser workflow
    if case_name == "ChangeUser" and step_name == "change_user":
        logger.info("Change User workflow completed - check screenshots for results")

if __name__ == "__main__":
    main()
