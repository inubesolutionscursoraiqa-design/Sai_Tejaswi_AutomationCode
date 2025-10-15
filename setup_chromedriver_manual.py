#!/usr/bin/env python3
"""
ChromeDriver Manual Setup Helper
Run this after manually downloading chromedriver.exe
"""
import os
import json

def setup_chromedriver():
    """Set up ChromeDriver path in config.json"""

    # ChromeDriver should be in drivers/chromedriver.exe
    chromedriver_path = os.path.join(os.getcwd(), "drivers", "chromedriver.exe")

    if not os.path.exists(chromedriver_path):
        print("❌ ChromeDriver not found at:", chromedriver_path)
        print("\nPlease download ChromeDriver manually:")
        print("1. Go to: https://googlechromelabs.github.io/chrome-for-testing/")
        print("2. Find your Chrome version (check in Chrome: Help > About)")
        print("3. Download win32 version")
        print("4. Extract chromedriver.exe to: drivers/ folder")
        print("5. Run this script again")
        return False

    # Update config.json
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        config['chromedriver_path'] = chromedriver_path

        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)

        print("✅ ChromeDriver configured successfully!")
        print(f"Path: {chromedriver_path}")
        print("\nYou can now run:")
        print("python run.py User_Management/create_new_user")

        return True

    except Exception as e:
        print(f"❌ Failed to update config.json: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("ChromeDriver Manual Setup")
    print("=" * 50)
    setup_chromedriver()


