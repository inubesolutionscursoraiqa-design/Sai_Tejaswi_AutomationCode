#!/usr/bin/env python3
"""
Simple browser test to debug ChromeDriver issues
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.browser import Browser

def test_browser():
    """Test browser initialization"""
    context = {
        "headless": False,
        "browser_type": "chrome"
    }

    print("Testing browser initialization...")
    try:
        browser = Browser(context)
        print("✅ Browser initialized successfully")

        # Test navigation
        driver = browser.get_driver()
        print("Navigating to test page...")
        driver.get("https://www.google.com")
        print("✅ Navigation successful")

        browser.close()
        print("✅ Browser test completed successfully")

    except Exception as e:
        print(f"❌ Browser test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_browser()


