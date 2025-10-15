import argparse
import logging
import os
import sys
import subprocess

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.core.report_generator import generate_module_report

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("report_generation.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Generate PDF test reports")
    parser.add_argument("module", help="Module name to generate report for (e.g., LoginLogout)")
    parser.add_argument("--workflows", nargs="+", help="Specific workflows to include in the report")
    parser.add_argument("--all", action="store_true", help="Generate reports for all modules")
    return parser.parse_args()

def get_all_modules():
    """Get all available modules in the workflows directory"""
    modules = []
    workflows_dir = "workflows"
    
    if os.path.exists(workflows_dir):
        for item in os.listdir(workflows_dir):
            if os.path.isdir(os.path.join(workflows_dir, item)) and not item.startswith('__'):
                modules.append(item)
    
    return modules

def install_required_libraries():
    """Check for required libraries for PDF generation"""
    try:
        import importlib
        libraries = ['fpdf', 'matplotlib', 'numpy']

        for lib in libraries:
            try:
                importlib.import_module(lib)
                logger.info(f"[OK] {lib} is installed")
            except ImportError:
                logger.warning(f"[MISSING] {lib} is not installed - PDF reports will not be available")

        return True
    except Exception as e:
        logger.warning(f"Could not check libraries: {str(e)}")
        logger.info("Note: Install PDF libraries manually for enhanced reports: py -m pip install fpdf matplotlib numpy")
        return False

def main():
    """Main entry point for the report generator"""
    args = parse_args()

    # Try to install required libraries
    logger.info("Checking for required libraries...")
    install_required_libraries()

    if args.all:
        # Generate reports for all modules
        modules = get_all_modules()
        logger.info(f"Generating reports for all modules: {modules}")

        for module in modules:
            try:
                report_path = generate_module_report(module)
                if report_path:
                    logger.info(f"Report for module {module} generated: {report_path}")
                else:
                    logger.warning(f"Failed to generate report for module {module}")
            except Exception as e:
                logger.error(f"Error generating report for module {module}: {str(e)}")
    else:
        # Generate report for specific module
        try:
            report_path = generate_module_report(args.module, args.workflows)
            if report_path:
                logger.info(f"Report generated: {report_path}")
                print(f"Report successfully generated: {report_path}")
            else:
                logger.error(f"Failed to generate report for module {args.module}")
                print(f"Failed to generate report for module {args.module}. Check logs for details.")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            print(f"Error generating report: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()
