#!/usr/bin/env python3
"""
Run ONLY positive workflows and generate report
"""
import subprocess
import sys
import os
import time

print("="*80)
print("RUNNING ONLY POSITIVE WORKFLOWS")
print("="*80)

# Define ONLY positive workflows (no negative scenarios)
positive_workflows = [
    'LoginLogout/login_logout',
    'ForgetPassword/forget_password',
    'ChangeUser/change_user',
    'Resend_OTP/resend_otp'
]

print(f"\n📋 Positive workflows to execute: {len(positive_workflows)}")
for i, workflow in enumerate(positive_workflows, 1):
    print(f"   {i}. {workflow}")

print("\n" + "="*80)
print(" EXECUTING POSITIVE WORKFLOWS ONLY...")
print("="*80)

successful_workflows = []
failed_workflows = []

for i, workflow in enumerate(positive_workflows, 1):
    print(f"\n[{i}/{len(positive_workflows)}] Running: {workflow}")

    try:
        # Run workflow in headless mode
        result = subprocess.run(
            [sys.executable, 'run.py', workflow, '--headless'],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print(f"   ✅ PASSED")
            successful_workflows.append(workflow)
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
print(" POSITIVE WORKFLOWS EXECUTION SUMMARY")
print("="*80)
print(f"✅ Successful: {len(successful_workflows)}")
print(f"❌ Failed: {len(failed_workflows)}")

if successful_workflows:
    print("\nSuccessful workflows:")
    for wf in successful_workflows:
        print(f"   ✅ {wf}")

if failed_workflows:
    print("\nFailed workflows:")
    for wf in failed_workflows:
        print(f"   ❌ {wf}")

# Generate report for positive workflows only
print("\n" + "="*80)
print(" GENERATING POSITIVE WORKFLOWS REPORT")
print("="*80)

try:
    print("\n📊 Generating report with positive workflows data only...")
    result = subprocess.run(
        [sys.executable, 'generate_accurate_report.py'],
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode == 0:
        print("Positive workflows report generated successfully!")
        print("\nReport Summary:")
        print(f"   Successful Workflows: {len(successful_workflows)}")
        print(f"   Failed Workflows: {len(failed_workflows)}")
        print("   Report location: reports/"
    else:
        print("Report generation had issues")
        if result.stderr:
            print(f"Error: {result.stderr}")

except Exception as e:
    print(f"❌ Error generating report: {str(e)}")

print("\n" + "="*80)
print(" COMPLETE!")
print("="*80)

# Final status
if len(failed_workflows) == 0:
    print("🎉 ALL POSITIVE WORKFLOWS COMPLETED SUCCESSFULLY!")
    sys.exit(0)
else:
    print(f"⚠️  {len(failed_workflows)} positive workflows failed.")
    sys.exit(1)
