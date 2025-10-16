#!/usr/bin/env python3
"""
Generate a comprehensive PDF report for all workflows with current test results
"""
import sys
import os
import logging
import subprocess
from datetime import datetime

# Add project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.core.report_generator import generate_module_report

def run_workflow(workflow_name):
    """Run a specific workflow and return result"""
    try:
        print(f"Running: {workflow_name}")
        result = subprocess.run(
            [sys.executable, 'run.py', workflow_name, '--headless'],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {workflow_name}: {str(e)}")
        return False

def main():
    """Generate comprehensive report for all workflows"""
    print("="*80)
    print(" GENERATING COMPREHENSIVE AUTOMATION TEST REPORT")
    print("="*80)

    # Define all workflows to test
    all_workflows = {
        'LoginLogout': {
            'workflows': ['login_logout', 'login_invalid_negative'],
            'description': 'Login and logout functionality testing'
        },
        'ForgetPassword': {
            'workflows': [
                'forget_password',
                'forget_password_invalid_username_negative',
                'forget_password_mismatch_negative',
                'forget_password_wrong_otp_negative'
            ],
            'description': 'Password reset functionality testing'
        },
        'ChangeUser': {
            'workflows': ['change_user', 'change_user_invalid_negative'],
            'description': 'User profile change functionality testing'
        },
        'Resend_OTP': {
            'workflows': ['resend_otp', 'resend_otp_rate_limit_negative'],
            'description': 'OTP resend functionality and rate limiting testing'
        }
    }

    # Run all workflows
    print("\n📋 EXECUTING ALL WORKFLOWS...")
    print("="*80)

    results = {}
    total_passed = 0
    total_failed = 0

    for module_name, module_info in all_workflows.items():
        print(f"\n🔍 MODULE: {module_name}")
        print(f"   Description: {module_info['description']}")
        print(f"   Workflows: {', '.join(module_info['workflows'])}")

        module_results = {}
        for workflow in module_info['workflows']:
            workflow_name = f"{module_name}/{workflow}"
            success = run_workflow(workflow_name)
            module_results[workflow] = success
            if success:
                total_passed += 1
                print(f"   ✅ {workflow}: PASSED")
            else:
                total_failed += 1
                print(f"   ❌ {workflow}: FAILED")

        results[module_name] = module_results

        # Small delay between modules
        import time
        time.sleep(2)

    # Generate summary
    print("\n" + "="*80)
    print(" EXECUTION SUMMARY")
    print("="*80)
    print(f"✅ Total Passed: {total_passed}")
    print(f"❌ Total Failed: {total_failed}")
    print(f"📊 Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%" if (total_passed+total_failed) > 0 else "📊 Success Rate: 0%")

    # Generate comprehensive report
    print("\n" + "="*80)
    print(" GENERATING COMPREHENSIVE PDF REPORT")
    print("="*80)

    try:
        # Create a simple comprehensive report by combining all module reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comprehensive_report = f"reports/comprehensive_report_{timestamp}.pdf"

        print("📋 Generating report for each module...")

        module_reports = []
        for module_name in all_workflows.keys():
            print(f"   Generating report for: {module_name}")
            report_path = generate_module_report(module_name, all_workflows[module_name]['workflows'])
            if report_path:
                module_reports.append(report_path)
                print(f"   ✅ {module_name} report: {report_path}")
            else:
                print(f"   ⚠️  Failed to generate {module_name} report")

        print(f"\n📄 Generated {len(module_reports)} individual module reports")
        for report in module_reports:
            print(f"   - {os.path.basename(report)}")

        # Clean up old reports
        print("\n🧹 Cleaning up old reports...")
        cleanup_script = os.path.join(project_root, "cleanup_old_reports.py")
        if os.path.exists(cleanup_script):
            subprocess.run([sys.executable, cleanup_script], check=True)
            print("   ✅ Old reports moved to backup")
        else:
            print("   ⚠️  Cleanup script not found")

        print("\n" + "="*80)
        print(" COMPREHENSIVE REPORT GENERATION COMPLETE")
        print("="*80)
        print("📁 Check the 'reports/' folder for individual module reports")
        print("📦 Old reports have been moved to 'reports/backup/'")
        print(f"\n📊 Total Workflows Tested: {total_passed + total_failed}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_failed}")

        if total_failed > 0:
            print("\n⚠️  Some workflows failed. Please check the logs for details.")
            return False
        else:
            print("\n🎉 All workflows completed successfully!")
            return True

    except Exception as e:
        print(f"❌ Error generating comprehensive report: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
