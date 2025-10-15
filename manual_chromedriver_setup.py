#!/usr/bin/env python3
"""
Manual ChromeDriver Setup Helper
"""
import os
import json
import urllib.request
import zipfile

def download_chromedriver():
    """Download ChromeDriver for known Chrome version"""
    # Chrome version 141.0.7390.55 (from earlier detection)
    version = "141.0.7390.55"
    platform_name = "win32"
    driver_name = "chromedriver.exe"

    print(f"Downloading ChromeDriver for Chrome version {version}...")

    # Create drivers directory
    drivers_dir = os.path.join(os.getcwd(), "drivers")
    os.makedirs(drivers_dir, exist_ok=True)

    try:
        # Download chromedriver
        url = f"https://edgedl.me.gstatic.com/edgedl/chrome/chrome-for-testing/{version}/{platform_name}/chromedriver-{platform_name}.zip"
        print(f"Downloading from: {url}")

        zip_path = os.path.join(drivers_dir, "chromedriver.zip")
        urllib.request.urlretrieve(url, zip_path)

        print("Extracting ChromeDriver...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(drivers_dir)

        # Find the extracted chromedriver
        extracted_driver = None
        for root, dirs, files in os.walk(drivers_dir):
            if driver_name in files:
                extracted_driver = os.path.join(root, driver_name)
                break

        if extracted_driver:
            # Move to drivers directory root
            final_path = os.path.join(drivers_dir, driver_name)
            if os.path.exists(final_path):
                os.remove(final_path)

            import shutil
            shutil.move(extracted_driver, final_path)

            # Clean up
            os.remove(zip_path)

            print(f"✅ ChromeDriver successfully downloaded to: {final_path}")

            # Update config.json
            update_config(final_path)

            return final_path
        else:
            print("❌ Failed to find extracted ChromeDriver")
            return None

    except Exception as e:
        print(f"❌ Failed to download ChromeDriver: {e}")
        return None

def update_config(chromedriver_path):
    """Update config.json with chromedriver path"""
    try:
        config_path = "config.json"

        # Read existing config
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Update chromedriver path
        config['chromedriver_path'] = os.path.abspath(chromedriver_path)

        # Write back
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Updated config.json with chromedriver_path")

    except Exception as e:
        print(f"Warning: Could not update config.json: {e}")

def main():
    """Main execution"""
    print("=" * 60)
    print("Manual ChromeDriver Setup")
    print("=" * 60)
    print("Chrome version: 141.0.7390.55 detected")
    print("Attempting manual download...")

    driver_path = download_chromedriver()

    if driver_path:
        print("\n" + "=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print(f"ChromeDriver Path: {driver_path}")
        print("\nYou can now run your automation workflows:")
        print("  python run.py User_Management/create_new_user")
    else:
        print("\n" + "=" * 60)
        print("❌ Manual Setup Failed")
        print("=" * 60)
        print("Alternative: Download ChromeDriver manually from:")
        print("https://googlechromelabs.github.io/chrome-for-testing/")
        print("1. Select version 141.0.7390.55")
        print("2. Download win32 zip file")
        print("3. Extract chromedriver.exe to drivers/ folder")
        print("4. Update config.json with the full path")

if __name__ == "__main__":
    main()


