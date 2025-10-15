#!/usr/bin/env python3
"""
Helper script to download and setup ChromeDriver
"""
import os
import platform
import requests
import zipfile
import json
import subprocess
import sys

def get_chrome_version():
    """Get installed Chrome version"""
    try:
        system = platform.system()
        if system == "Windows":
            # Try to get Chrome version on Windows
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                return version
            except:
                # Try alternative registry location
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome")
                    version, _ = winreg.QueryValueEx(key, "version")
                    return version
                except:
                    pass
            
            # Try PowerShell command
            try:
                result = subprocess.run(
                    ['powershell', '-Command', '(Get-Item "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe").VersionInfo.ProductVersion'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass
                
        elif system == "Darwin":  # macOS
            result = subprocess.run(
                ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip().split()[-1]
            
        elif system == "Linux":
            result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
            return result.stdout.strip().split()[-1]
            
    except Exception as e:
        print(f"Could not detect Chrome version: {e}")
    
    return None

def download_chromedriver(version=None):
    """Download ChromeDriver matching Chrome version"""
    try:
        system = platform.system()
        
        # Get Chrome version if not provided
        if not version:
            version = get_chrome_version()
            if not version:
                print("Could not detect Chrome version. Using latest ChromeDriver...")
                version = "latest"
        
        print(f"Chrome version detected: {version}")
        
        # Determine the platform
        if system == "Windows":
            platform_name = "win32"
            driver_name = "chromedriver.exe"
        elif system == "Darwin":
            platform_name = "mac64"
            driver_name = "chromedriver"
        elif system == "Linux":
            platform_name = "linux64"
            driver_name = "chromedriver"
        else:
            print(f"Unsupported platform: {system}")
            return None
        
        # Create drivers directory
        drivers_dir = os.path.join(os.getcwd(), "drivers")
        os.makedirs(drivers_dir, exist_ok=True)
        
        # Get major version
        major_version = version.split('.')[0] if version != "latest" else "latest"
        
        print(f"Downloading ChromeDriver for version {major_version}...")
        
        # Try to download from Chrome for Testing
        try:
            # Get the latest stable version info
            if major_version == "latest":
                url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json"
                response = requests.get(url)
                data = response.json()
                stable_version = data['channels']['Stable']['version']
            else:
                stable_version = version
            
            # Download chromedriver
            download_url = f"https://edgedl.me.gstatic.com/edgedl/chrome/chrome-for-testing/{stable_version}/{platform_name}/chromedriver-{platform_name}.zip"
            
            print(f"Downloading from: {download_url}")
            response = requests.get(download_url)
            
            if response.status_code == 200:
                # Save and extract
                zip_path = os.path.join(drivers_dir, "chromedriver.zip")
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
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
                    
                    # Make executable on Unix systems
                    if system != "Windows":
                        os.chmod(final_path, 0o755)
                    
                    # Clean up
                    os.remove(zip_path)
                    
                    print(f"✅ ChromeDriver successfully downloaded to: {final_path}")
                    
                    # Update config.json
                    update_config(final_path)
                    
                    return final_path
                    
        except Exception as e:
            print(f"Failed to download ChromeDriver: {e}")
            print("\nAlternative: You can manually download ChromeDriver from:")
            print("https://googlechromelabs.github.io/chrome-for-testing/")
            print(f"And place it in: {drivers_dir}")
            
    except Exception as e:
        print(f"Error setting up ChromeDriver: {e}")
    
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
    print("ChromeDriver Setup Helper")
    print("=" * 60)
    
    # Check if Chrome is installed
    chrome_version = get_chrome_version()
    if chrome_version:
        print(f"✅ Chrome detected: {chrome_version}")
    else:
        print("⚠️  Could not detect Chrome installation")
        print("Please ensure Google Chrome is installed")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Download ChromeDriver
    driver_path = download_chromedriver(chrome_version)
    
    if driver_path:
        print("\n" + "=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print(f"ChromeDriver Path: {driver_path}")
        print("\nYou can now run your automation workflows:")
        print("  python run.py User_Management/create_new_user")
    else:
        print("\n" + "=" * 60)
        print("❌ Setup Failed")
        print("=" * 60)
        print("Please manually download ChromeDriver and update config.json")

if __name__ == "__main__":
    main()


