#!/usr/bin/env python3
"""
Test script to generate PDF reports
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from src.core.report_generator import generate_module_report

print("="*60)
print("Testing PDF Report Generation")
print("="*60)

# Test generating a report for LoginLogout
print("\n1. Generating LoginLogout report...")
try:
    result = generate_module_report('LoginLogout', ['login_logout', 'login_invalid_negative'])
    if result:
        print(f"   ✅ Success! Report: {result}")
    else:
        print(f"   ❌ Failed - No report generated")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

# Test generating a report for ForgetPassword
print("\n2. Generating ForgetPassword report...")
try:
    result = generate_module_report('ForgetPassword', [
        'forget_password',
        'forget_password_invalid_username_negative',
        'forget_password_mismatch_negative',
        'forget_password_wrong_otp_negative'
    ])
    if result:
        print(f"   ✅ Success! Report: {result}")
    else:
        print(f"   ❌ Failed - No report generated")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test Complete")
print("="*60)

