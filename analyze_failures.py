#!/usr/bin/env python3
"""
Analyze which positive workflow failed
"""
import os
import re
from collections import defaultdict

log_file = 'automation.log'
positive_workflows = {
    'LoginLogout': ['login_logout'],
    'ForgetPassword': ['forget_password'],
    'ChangeUser': ['change_user'],
    'Resend_OTP': ['resend_otp']
}

results = defaultdict(lambda: {'executed': 0, 'successful': 0, 'failed': 0})

if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        workflow_pattern = r'Workflow\s+(\w+)/(\w+)\s+(completed successfully|failed)'
        match = re.search(workflow_pattern, line)

        if match:
            module_name = match.group(1)
            workflow_name = match.group(2)
            status = match.group(3)

            if module_name in positive_workflows and workflow_name in positive_workflows[module_name]:
                results[module_name]['executed'] += 1

                if 'completed successfully' in status:
                    results[module_name]['successful'] += 1
                elif 'failed' in status:
                    results[module_name]['failed'] += 1

    print('POSITIVE WORKFLOWS ANALYSIS:')
    for module, data in results.items():
        print(f'{module}:')
        print(f'  Executed: {data["executed"]}')
        print(f'  Successful: {data["successful"]}')
        print(f'  Failed: {data["failed"]}')
        print()

    # Calculate totals
    total_executed = sum(module['executed'] for module in results.values())
    total_successful = sum(module['successful'] for module in results.values())
    total_failed = sum(module['failed'] for module in results.values())

    print('SUMMARY:')
    print(f'Total Positive Workflows Executed: {total_executed}')
    print(f'Total Successful: {total_successful}')
    print(f'Total Failed: {total_failed}')
    print(f'Success Rate: {(total_successful/total_executed*100):.1f}%' if total_executed > 0 else 'Success Rate: 0%')
else:
    print('Log file not found')
