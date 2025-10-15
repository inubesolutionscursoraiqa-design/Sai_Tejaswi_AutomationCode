# LMS Automation Testing Framework

A comprehensive, professionally organized Selenium-based automation testing framework for Learning Management System (LMS) with Page Object Model architecture.

## 📁 Project Structure

```
LMS_Automation/
├── 📂 src/                            # Main source code
│   ├── 📂 core/                       # Core framework modules
│   │   ├── browser.py                 # WebDriver management & browser setup
│   │   ├── db.py                      # Database connection & OTP fetching
│   │   ├── report_generator.py        # PDF/HTML report generation
│   │   ├── comprehensive_report_generator.py # Multi-module reporting
│   │   ├── load_tester.py             # Load & performance testing
│   │   └── runner.py                  # JSON workflow execution engine
│   │
│   ├── 📂 pages/                      # Page Object Model classes
│   │   ├── base_page.py               # Common Selenium methods & utilities
│   │   ├── login_page.py              # Login page locators & actions
│   │   ├── dashboard_page.py          # Dashboard navigation & logout
│   │   ├── forget_password_page.py    # Password reset workflows
│   │   └── change_user_page.py        # User profile management
│   │
│   ├── 📂 tests/                      # Test cases (pytest framework)
│   │   ├── test_login.py              # Login/logout functionality tests
│   │   ├── test_forget_password.py    # Password reset test scenarios
│   │   ├── test_change_user.py        # User profile change tests
│   │   └── test_resend_otp.py         # OTP resend functionality tests
│   │
│   ├── 📂 utils/                      # Helper utilities & configurations
│   │   ├── config.py                  # Configuration management
│   │   ├── config.json                # Main configuration file
│   │   └── load_test_scenarios.json   # Load testing configurations
│   │
│   └── 📂 load_testing/               # Load & performance testing
│       ├── load_tester.py             # Core load testing functionality
│       └── load_test_login.py         # Load testing workflow for login
│
├── 📂 recordings/                     # JSON test recordings
│   ├── LoginLogout/                   # Login/logout test data
│   ├── ForgetPassword/               # Password reset test data
│   ├── ChangeUser/                   # User change test data
│   └── Resend_OTP/                   # OTP resend test data
│
├── 📂 reports/                       # Generated reports & evidence
│   ├── generation/                   # Report generation scripts
│   │   ├── generate_all_reports.py   # Generate comprehensive reports
│   │   └── generate_report.py        # Generate module-specific reports
│   ├── screenshots/                  # Test execution screenshots
│   ├── html_reports/                 # pytest-html test reports
│   ├── pdf_reports/                  # Generated PDF summary reports
│   └── performance_reports/          # Load testing results
│
├── 📂 scripts/                        # Utility scripts & tools
│   └── load_testing/                  # Load testing scripts
│       ├── run_load_test.py           # Execute load testing
│       └── test_load_setup.py         # Load testing validation
│
├── 📄 conftest.py                     # Pytest fixtures for driver setup
├── 📄 requirements.txt                # Python dependencies
├── 📄 pytest.ini                      # Pytest configuration
├── 📄 README.md                       # This documentation
```

## 🚀 Quick Start

### Installation
```bash
# 1. Install Python 3.8+ (if not already installed)
# 2. Install dependencies
   pip install -r requirements.txt

# 3. Install additional libraries for enhanced features
pip install locust psutil pytest-benchmark fpdf matplotlib numpy
```

### Run Tests
```bash
# Run all tests with HTML report
pytest src/tests/ --html=reports/html_reports/report.html

# Run specific test module
pytest src/tests/test_login.py -v

# Run with markers (smoke, regression, etc.)
pytest -m smoke src/tests/ --html=reports/html_reports/smoke_report.html
```

### Generate Reports
```bash
# Generate comprehensive report for all modules
python reports/generation/generate_all_reports.py

# Generate module-specific report
python reports/generation/generate_report.py ModuleName

# Generate load testing report
python scripts/load_testing/run_load_test.py
```

## 📋 Framework Features

### ✅ **Core Capabilities**
- **Page Object Model** - Maintainable, reusable page classes
- **JSON Test Recordings** - Human-readable test definitions
- **Database Integration** - Real OTP fetching from PostgreSQL
- **Comprehensive Reporting** - HTML/PDF reports with charts
- **Load Testing** - Concurrent user performance testing
- **Screenshot Automation** - Visual test evidence collection

### ✅ **Test Modules**
1. **LoginLogout** - Authentication and session management
2. **ForgetPassword** - Password reset with OTP verification
3. **ChangeUser** - User profile modification workflows
4. **Resend_OTP** - OTP resend functionality and rate limiting

### ✅ **Advanced Features**
- **Multi-Browser Support** - Chrome, Firefox compatibility
- **Headless Execution** - Server-friendly testing
- **Error Handling** - Comprehensive failure recovery
- **Performance Monitoring** - Execution time and resource tracking
- **Visual Regression** - Screenshot-based change detection

## 🎯 Usage Examples

### Basic Test Execution
```python
# Run individual workflow
python run.py LoginLogout/login_logout --headless

# Run with custom configuration
python run.py ForgetPassword/forget_password --headless
```

### Page Object Model Usage
```python
from src.pages.login_page import LoginPage
from src.pages.dashboard_page import DashboardPage

# Initialize pages
login_page = LoginPage(driver)
dashboard_page = DashboardPage(driver)

# Execute test flow
login_page.perform_login(username, password, url)
dashboard_page.perform_logout()
```

### Load Testing
```python
from src.core.load_tester import run_load_test

# Run load test with 10 concurrent users
results = run_load_test(
    workflow_name="LoginLogout",
    json_path="recordings/LoginLogout/login_logout.json",
    num_users=10,
    ramp_up_time=30
)
```

## 🔧 Configuration

### Main Configuration (`config/config.json`)
```json
{
  "username": "your_username",
  "password": "your_password",
  "url": "http://your-lms-url.com",
  "browser": "chrome",
  "headless": false,
  "db_host": "your-db-host",
  "db_port": 5432,
  "db_name": "your_database",
  "db_user": "your_db_user",
  "db_password": "your_db_password"
}
```

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = src/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    smoke: Quick smoke tests
    regression: Full regression tests
    ui: UI testing
    database: Database testing
    load: Load testing

addopts =
    --html=reports/html_reports/report.html
    --self-contained-html
```

## 📊 Reporting & Analytics

### Generated Reports
- **📄 PDF Reports** - Professional multi-page reports with charts
- **🌐 HTML Reports** - Interactive web-based reports with screenshots
- **📈 Performance Reports** - Load testing results and metrics
- **🖼️ Screenshot Gallery** - Visual evidence of test executions

### Report Contents
- **📋 Test Summary** - Pass/fail counts and success rates
- **📊 Visual Charts** - Performance graphs and analytics
- **⏱️ Execution Metrics** - Response times and throughput data
- **🖼️ Screenshot Evidence** - Test execution visual documentation
- **🔍 Error Analysis** - Detailed failure investigation

## 🎨 Architecture Highlights

### **Page Object Model Benefits**
- **Maintainable** - Easy to update locators in one place
- **Reusable** - Common methods in BasePage class
- **Readable** - Clear, descriptive method names
- **Scalable** - Easy to add new page classes

### **Test Organization**
- **Modular Tests** - Each test module focuses on specific functionality
- **Pytest Framework** - Professional testing standards
- **Fixture Management** - Automatic driver and page setup
- **Marker System** - Test categorization and filtering

### **Utility Ecosystem**
- **Configuration Management** - Centralized settings
- **Database Integration** - Real OTP handling
- **Report Generation** - Multi-format reporting
- **Logging System** - Comprehensive execution tracking

## 🚀 Next Steps

### **Immediate Actions**
1. **Install Dependencies** - Run `pip install -r requirements.txt`
2. **Execute Tests** - Run `pytest src/tests/` to validate framework
3. **Generate Reports** - Run `python scripts/generate_all_reports.py`

### **Framework Extensions**
1. **New Page Classes** - Add pages for additional LMS features
2. **API Testing** - Extend for backend API validation
3. **Mobile Testing** - Add responsive design testing
4. **Security Testing** - Include security vulnerability checks

---

**🎯 Summary**: This LMS automation framework provides **enterprise-grade testing capabilities** with a **professionally organized structure**, **comprehensive reporting**, and **scalable architecture** for reliable, maintainable test automation.