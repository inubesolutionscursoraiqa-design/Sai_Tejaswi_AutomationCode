#!/usr/bin/env python3
"""
Script to run all workflows and generate comprehensive PDF reports
"""
import subprocess
import sys
import os
import time

# Add project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

print("="*80)
print(" AUTOMATION TESTING - RUN ALL WORKFLOWS AND GENERATE REPORTS")
print("="*80)

# Define all workflows to run
workflows = {
    'LoginLogout': [
        'LoginLogout/login_logout',
        'LoginLogout/login_invalid_negative'
    ],
    'ForgetPassword': [
        'ForgetPassword/forget_password',
        'ForgetPassword/forget_password_invalid_username_negative',
        'ForgetPassword/forget_password_mismatch_negative',
        'ForgetPassword/forget_password_wrong_otp_negative'
    ],
    'ChangeUser': [
        'ChangeUser/change_user',
        'ChangeUser/change_user_invalid_negative'
    ],
    'Resend_OTP': [
        'Resend_OTP/resend_otp',
        'Resend_OTP/resend_otp_rate_limit_negative'
    ]
}

# Run all workflows
total_workflows = sum(len(wf_list) for wf_list in workflows.values())
current = 0
failed_workflows = []

print(f"\n📋 Total workflows to execute: {total_workflows}")
print("\n" + "="*80)

for module, workflow_list in workflows.items():
    print(f"\n🔍 MODULE: {module}")
    print("-"*80)
    
    for workflow in workflow_list:
        current += 1
        print(f"\n[{current}/{total_workflows}] Running: {workflow}")
        
        try:
            # Run workflow in headless mode
            result = subprocess.run(
                [sys.executable, 'run.py', workflow, '--headless'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per workflow
            )
            
            if result.returncode == 0:
                print(f"   ✅ PASSED")
            else:
                print(f"   ❌ FAILED")
                failed_workflows.append(workflow)
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}")
                    
        except subprocess.TimeoutExpired:
            print(f"   ⏱️  TIMEOUT")
            failed_workflows.append(workflow)
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            failed_workflows.append(workflow)
        
        # Small delay between workflows
        time.sleep(2)

# Summary
print("\n" + "="*80)
print(" WORKFLOW EXECUTION SUMMARY")
print("="*80)
print(f"✅ Passed: {total_workflows - len(failed_workflows)}")
print(f"❌ Failed: {len(failed_workflows)}")

if failed_workflows:
    print("\nFailed workflows:")
    for wf in failed_workflows:
        print(f"   - {wf}")

# Generate PDF reports
print("\n" + "="*80)
print(" GENERATING PDF REPORTS")
print("="*80)

try:
    print("\n📊 Generating comprehensive reports for all modules...")
    result = subprocess.run(
        [sys.executable, 'reports/generation/generate_all_reports.py'],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode == 0:
        print("✅ Reports generated successfully!")
        print(f"\n📁 Check the 'reports/' folder for PDF reports")
    else:
        print("⚠️  Report generation had issues")
        if result.stderr:
            print(f"Error: {result.stderr}")
            
except Exception as e:
    print(f"❌ Error generating reports: {str(e)}")

print("\n" + "="*80)
print(" COMPLETE!")
print("="*80)
print(f"\n📊 Total execution time: Check the reports for details")
print(f"📁 Reports location: reports/")
print(f"📸 Screenshots location: screenshots/")
print("\n")

