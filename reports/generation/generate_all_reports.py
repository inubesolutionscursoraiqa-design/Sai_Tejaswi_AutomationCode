#!/usr/bin/env python3
"""
Generate comprehensive pass/fail reports for all workflows
"""
import sys
import os
import logging
import subprocess

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.core.report_generator import generate_module_report

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Generate comprehensive report for all workflows"""
    logger.info("=== Generating Comprehensive Workflow Reports ===")
    
    # Define all modules and their workflows
    all_modules = {
        'LoginLogout': ['login_logout', 'login_invalid_negative'],
        'ForgetPassword': [
            'forget_password',
            'forget_password_invalid_username_negative',
            'forget_password_mismatch_negative',
            'forget_password_wrong_otp_negative'
        ],
        'ChangeUser': ['change_user', 'change_user_invalid_negative'],
        'Resend_OTP': ['resend_otp', 'resend_otp_rate_limit_negative']
    }
    
    reports_generated = []
    failed_reports = []

    try:
        for module_name, workflows in all_modules.items():
            logger.info(f"\n📋 Generating report for module: {module_name}")
            logger.info(f"   Workflows: {', '.join(workflows)}")
            
            try:
                report_path = generate_module_report(module_name, workflows)
                
                if report_path:
                    logger.info(f"✅ Report generated: {report_path}")
                    reports_generated.append((module_name, report_path))
                else:
                    logger.warning(f"⚠️  No report generated for {module_name}")
                    failed_reports.append(module_name)
                    
            except Exception as e:
                logger.error(f"❌ Error generating report for {module_name}: {str(e)}")
                failed_reports.append(module_name)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("📊 REPORT GENERATION SUMMARY")
        logger.info("="*60)
        logger.info(f"✅ Successfully generated: {len(reports_generated)} reports")
        
        for module, path in reports_generated:
            logger.info(f"   - {module}: {os.path.basename(path)}")
        
        if failed_reports:
            logger.warning(f"\n⚠️  Failed to generate: {len(failed_reports)} reports")
            for module in failed_reports:
                logger.warning(f"   - {module}")
        
        logger.info(f"\n📁 All reports saved in: reports/")
        
        # Cleanup old reports - keep only the latest
        if reports_generated:
            logger.info("\n🧹 Cleaning up old reports...")
            try:
                cleanup_script = os.path.join(project_root, "cleanup_old_reports.py")
                if os.path.exists(cleanup_script):
                    subprocess.run([sys.executable, cleanup_script], check=True)
                else:
                    logger.warning("⚠️  Cleanup script not found, skipping cleanup")
            except Exception as e:
                logger.warning(f"⚠️  Could not run cleanup: {str(e)}")
        
        return len(reports_generated) > 0

    except Exception as e:
        logger.error(f"Error generating reports: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

