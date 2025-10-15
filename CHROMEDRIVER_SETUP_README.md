# ChromeDriver Setup Guide

## Problem
The automated ChromeDriver download is failing due to network connectivity issues. Here's how to set it up manually:

## Manual Setup Steps

### Step 1: Check Your Chrome Version
1. Open Google Chrome
2. Click the three dots (⋮) in the top right
3. Go to **Help** → **About Google Chrome**
4. Note the version number (e.g., `141.0.7390.55`)

### Step 2: Download ChromeDriver
1. Go to: https://googlechromelabs.github.io/chrome-for-testing/
2. Find your Chrome version in the list
3. Download the **win32** version (for Windows)
4. Extract the ZIP file

### Step 3: Place ChromeDriver
1. Create a `drivers` folder in your project root: `D:\Lms_Automation\drivers\`
2. Copy `chromedriver.exe` into this folder

### Step 4: Update config.json
Open `config.json` and add:
```json
{
  "chromedriver_path": "D:\\Lms_Automation\\drivers\\chromedriver.exe"
}
```

## Alternative Solutions

### Option 1: Use System PATH
1. Download ChromeDriver as above
2. Add the folder containing `chromedriver.exe` to your system PATH
3. Leave `chromedriver_path` empty in config.json

### Option 2: Use Different Browser
If ChromeDriver setup is problematic, you can:
1. Use Firefox instead (requires GeckoDriver)
2. Or use the existing working workflows as reference

## Current Status
- ✅ Workflow code is correct and optimized
- ✅ Selectors are using exact IDs from original recording
- ✅ Wait times are optimized (0.5s instead of 1s)
- ❌ ChromeDriver needs manual setup due to network issues

## Test the Setup
Once ChromeDriver is configured, run:
```bash
python run.py User_Management/create_new_user
```

The workflow should now work properly with the correct ChromeDriver setup!


