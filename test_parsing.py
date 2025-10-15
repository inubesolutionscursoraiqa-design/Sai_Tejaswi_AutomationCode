#!/usr/bin/env python3
"""
Test script to verify log parsing is working
"""
import sys
import os
import logging

# Add project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.core.report_generator import TestReport

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_parsing():
    """Test the log parsing functionality"""
    generator = ComprehensiveReportGenerator()

    # Test parsing for LoginLogout/login_logout
    results = generator._get_workflow_results('LoginLogout', 'login_logout')

    print(f"LoginLogout/login_logout results:")
    print(f"  Passed: {len(results['passed'])}")
    print(f"  Failed: {len(results['failed'])}")
    print(f"  Errors: {len(results['errors'])}")
    print(f"  Execution times: {len(results['execution_times'])}")

    if results['passed']:
        print(f"  Sample passed entry: {results['passed'][0][:100]}...")
    if results['failed']:
        print(f"  Sample failed entry: {results['failed'][0][:100]}...")

    return results

if __name__ == "__main__":
    test_parsing()

