import os
import re
import logging
import json
import time
from datetime import datetime

# Try to import optional libraries, but provide fallbacks if they're not installed
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    logging.warning("FPDF library not found. PDF reports will not be available.")

try:
    import matplotlib.pyplot as plt
    import numpy as np
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    logging.warning("Matplotlib/NumPy libraries not found. Charts will not be available.")

logger = logging.getLogger(__name__)

class TestReport:
    """Class to generate PDF test reports from workflow execution logs"""

    def __init__(self, module_name):
        """
        Initialize the report generator

        Args:
            module_name: Name of the module (e.g., 'LoginLogout')
        """
        self.module_name = module_name
        self.log_file = "automation.log"
        self.report_dir = "reports"
        self.screenshot_dir = "screenshots"

        # Create reports directory if it doesn't exist
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def _parse_log_file(self, workflow_pattern):
        """
        Parse the log file to extract test results for the specified workflow

        Args:
            workflow_pattern: Regex pattern to match workflow entries

        Returns:
            dict: Dictionary containing parsed test results
        """
        results = {
            'passed': [],
            'failed': [],
            'errors': [],
            'warnings': [],
            'execution_times': [],
            'timestamps': [],
            'steps': []
        }

        try:
            with open(self.log_file, 'r') as f:
                log_content = f.read()

            # Find all workflow-related log entries for this pattern
            # Look for workflow start and completion messages
            pattern = rf'({workflow_pattern}.*?(?:Workflow.*(?:completed|failed)|$))'
            workflow_blocks = re.findall(pattern, log_content, re.DOTALL)

            logger.debug(f"Found {len(workflow_blocks)} workflow blocks for pattern: {workflow_pattern}")

            for block in workflow_blocks:
                # Extract timestamp
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', block)
                if timestamp_match:
                    results['timestamps'].append(timestamp_match.group(1))

                # Extract execution time
                time_match = re.search(r'Execution time: (\d+\.\d+)s', block)
                if time_match:
                    results['execution_times'].append(float(time_match.group(1)))

                # Extract steps
                steps = re.findall(r'Step (\d+): Executing action: (\w+)', block)
                results['steps'].extend(steps)

                # Determine test result - look for various success/failure patterns
                if (re.search(r'TEST PASSED', block) or
                    re.search(r'Workflow.*completed successfully', block) or
                    re.search(r'All actions completed successfully', block) or
                    re.search(r'workflow completed successfully', block, re.IGNORECASE)):
                    results['passed'].append(block)
                elif (re.search(r'TEST FAILED', block) or
                      re.search(r'Workflow.*failed', block) or
                      re.search(r'workflow failed', block, re.IGNORECASE)):
                    results['failed'].append(block)

                # Extract errors and warnings
                errors = re.findall(r'ERROR.*?: (.+)$', block, re.MULTILINE)
                warnings = re.findall(r'WARNING.*?: (.+)$', block, re.MULTILINE)

                results['errors'].extend(errors)
                results['warnings'].extend(warnings)

            logger.debug(f"Results for pattern {workflow_pattern}: {len(results['passed'])} passed, {len(results['failed'])} failed")
            return results

        except Exception as e:
            logger.error(f"Error parsing log file: {str(e)}")
            return results

    def _get_workflow_results(self, module_name, workflow_name):
        """Get results for a specific workflow"""
        # Try different pattern variations based on log format
        patterns = [
            f"Workflow {module_name}/{workflow_name}",
            f"Starting.*{workflow_name.replace('_', ' ')}",
            f"Executing workflow.*{workflow_name}",
            f"{workflow_name}.*Workflow"
        ]

        for pattern in patterns:
            logger.debug(f"Trying pattern: {pattern}")
            results = self._parse_log_file(pattern)
            if results['passed'] or results['failed']:
                logger.debug(f"Found results for pattern {pattern}: {len(results['passed'])} passed, {len(results['failed'])} failed")
                return results

        # Return empty results if no matches found
        logger.debug(f"No results found for workflow {module_name}/{workflow_name}")
        return {
            'passed': [],
            'failed': [],
            'errors': [],
            'warnings': [],
            'execution_times': [],
            'timestamps': [],
            'steps': []
        }

    def _create_charts(self, results):
        """
        Create charts for the report

        Args:
            results: Dictionary containing test results

        Returns:
            dict: Dictionary containing paths to generated chart images
        """
        charts = {}

        # Skip chart generation if matplotlib is not available
        if not CHARTS_AVAILABLE:
            logger.warning("Skipping chart generation - matplotlib not available")
            return charts

        try:
            # Create pie chart for test results
            if results['passed'] or results['failed']:
                plt.figure(figsize=(6, 6))
                labels = ['Passed', 'Failed']
                sizes = [len(results['passed']), len(results['failed'])]
                colors = ['#4CAF50', '#F44336']

                plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
                plt.title('Test Results')

                chart_path = os.path.join(self.report_dir, f"{self.module_name}_results_chart.png")
                plt.savefig(chart_path)
                plt.close()

                charts['results'] = chart_path

            # Create bar chart for execution times if available
            if results['execution_times']:
                plt.figure(figsize=(8, 4))

                x = np.arange(len(results['execution_times']))
                plt.bar(x, results['execution_times'], color='#2196F3')

                plt.xlabel('Test Run')
                plt.ylabel('Execution Time (s)')
                plt.title('Test Execution Times')

                chart_path = os.path.join(self.report_dir, f"{self.module_name}_time_chart.png")
                plt.savefig(chart_path)
                plt.close()

                charts['times'] = chart_path
        except Exception as e:
            logger.error(f"Error creating charts: {str(e)}")

        return charts

    def _get_screenshots(self, workflow_prefix):
        """
        Get screenshots for a specific workflow
        
        Args:
            workflow_prefix: Prefix of the workflow (e.g., 'login' from 'login_logout')
            
        Returns:
            list: List of screenshot file paths
        """
        screenshots = []
        
        if not os.path.exists(self.screenshot_dir):
            return screenshots
            
        try:
            # Get all screenshot files
            for file in os.listdir(self.screenshot_dir):
                if file.endswith('.png') and workflow_prefix.lower() in file.lower():
                    screenshots.append(os.path.join(self.screenshot_dir, file))
            
            # Sort by modification time
            screenshots.sort(key=os.path.getmtime, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting screenshots: {str(e)}")
            
        return screenshots

    def generate_pdf_report(self, workflows=None):
        """
        Generate a PDF report for the specified workflows

        Args:
            workflows: List of workflow names to include in the report (e.g., ['login_logout'])
                      If None, all workflows in the module will be included

        Returns:
            str: Path to the generated PDF report or HTML report if PDF is not available
        """
        # Check if FPDF is available
        if not FPDF_AVAILABLE:
            logger.warning("FPDF not available - generating HTML report instead")
            return self.generate_html_report(workflows)

        if workflows is None:
            # Get all workflows for this module
            workflow_dir = os.path.join('workflows', self.module_name)
            if os.path.exists(workflow_dir):
                workflows = []
                for file in os.listdir(workflow_dir):
                    if file.endswith('.py') and file != '__init__.py':
                        workflows.append(file[:-3])  # Remove .py extension

        if not workflows:
            logger.error(f"No workflows found for module {self.module_name}")
            return None

        try:
            # Create PDF
            pdf = FPDF()
            pdf.add_page()

            # Set up fonts
            pdf.set_font('Arial', 'B', 16)

            # Title
            pdf.cell(0, 10, f'{self.module_name} Test Report', 0, 1, 'C')
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')

            # Summary section
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Test Summary', 0, 1, 'L')

            total_passed = 0
            total_failed = 0

            # Process each workflow
            for workflow in workflows:
                # Parse log file for this workflow
                if workflow == 'login_logout':
                    workflow_pattern = f"Starting Login Logout Workflow"
                else:
                    workflow_pattern = f"Starting.*{workflow.replace('_', ' ')}"
                logger.info(f"Parsing logs for workflow: {workflow} with pattern: {workflow_pattern}")
                results = self._parse_log_file(workflow_pattern)

                # Update totals
                total_passed += len(results['passed'])
                total_failed += len(results['failed'])

                # Generate charts
                charts = self._create_charts(results)

                # Add workflow section
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f'Workflow: {workflow}', 0, 1, 'L')

                # Add test results table
                pdf.set_font('Arial', '', 10)
                pdf.cell(40, 10, 'Status', 1)
                pdf.cell(40, 10, 'Count', 1)
                pdf.cell(0, 10, 'Details', 1, 1)

                pdf.cell(40, 10, 'Passed', 1)
                pdf.cell(40, 10, str(len(results['passed'])), 1)
                pdf.cell(0, 10, '', 1, 1)

                pdf.cell(40, 10, 'Failed', 1)
                pdf.cell(40, 10, str(len(results['failed'])), 1)
                pdf.cell(0, 10, '', 1, 1)

                pdf.cell(40, 10, 'Errors', 1)
                pdf.cell(40, 10, str(len(results['errors'])), 1)
                pdf.cell(0, 10, '', 1, 1)

                pdf.cell(40, 10, 'Warnings', 1)
                pdf.cell(40, 10, str(len(results['warnings'])), 1)
                pdf.cell(0, 10, '', 1, 1)

                # Add execution time if available
                if results['execution_times']:
                    avg_time = sum(results['execution_times']) / len(results['execution_times'])
                    pdf.ln(5)
                    pdf.cell(0, 10, f'Average Execution Time: {avg_time:.2f}s', 0, 1)

                # Add charts if available
                if 'results' in charts:
                    pdf.ln(5)
                    pdf.cell(0, 10, 'Test Results Chart:', 0, 1)
                    pdf.image(charts['results'], x=10, w=90)

                if 'times' in charts:
                    pdf.ln(5)
                    pdf.cell(0, 10, 'Execution Times Chart:', 0, 1)
                    pdf.image(charts['times'], x=10, w=180)

                # Add screenshots
                screenshots = self._get_screenshots(workflow.split('_')[0].lower())
                if screenshots:
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 10, f'Screenshots for {workflow}', 0, 1)

                    for i, screenshot in enumerate(screenshots[:4]):  # Limit to 4 screenshots per page
                        pdf.ln(5)
                        pdf.set_font('Arial', '', 10)
                        pdf.cell(0, 10, f'Screenshot: {os.path.basename(screenshot)}', 0, 1)

                        try:
                            pdf.image(screenshot, x=10, w=180)
                        except Exception as e:
                            pdf.cell(0, 10, f'Error loading screenshot: {str(e)}', 0, 1)

                # Add error details if any
                if results['errors']:
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 10, f'Error Details for {workflow}', 0, 1)

                    pdf.set_font('Arial', '', 10)
                    for i, error in enumerate(results['errors']):
                        pdf.multi_cell(0, 10, f"{i+1}. {error}")

            # Add overall summary
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Overall Summary', 0, 1)

            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Total Tests: {total_passed + total_failed}', 0, 1)
            pdf.cell(0, 10, f'Passed: {total_passed}', 0, 1)
            pdf.cell(0, 10, f'Failed: {total_failed}', 0, 1)

            if total_passed + total_failed > 0:
                success_rate = (total_passed / (total_passed + total_failed)) * 100
                pdf.cell(0, 10, f'Success Rate: {success_rate:.2f}%', 0, 1)

            # Save the PDF
            report_path = os.path.join(self.report_dir, f"{self.module_name}_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            pdf.output(report_path)

            logger.info(f"PDF report generated: {report_path}")
            return report_path

        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            logger.warning("Falling back to HTML report")
            return self.generate_html_report(workflows)

    def generate_html_report(self, workflows=None):
        """
        Generate an HTML report as a fallback when PDF generation fails

        Args:
            workflows: List of workflow names to include in the report

        Returns:
            str: Path to the generated HTML report
        """
        if workflows is None:
            # Get all workflows for this module
            workflow_dir = os.path.join('workflows', self.module_name)
            if os.path.exists(workflow_dir):
                workflows = []
                for file in os.listdir(workflow_dir):
                    if file.endswith('.py') and file != '__init__.py':
                        workflows.append(file[:-3])  # Remove .py extension

        if not workflows:
            logger.error(f"No workflows found for module {self.module_name}")
            return None

        # Create HTML content
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{self.module_name} Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
        .warning {{ color: orange; }}
        .info {{ color: blue; }}
        img {{ max-width: 100%; }}
        .note {{ background-color: #f0f0f0; padding: 10px; margin: 10px 0; border-left: 4px solid #2196F3; }}
    </style>
</head>
<body>
    <h1>{self.module_name} Test Report</h1>
    <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <h2>Test Summary</h2>
"""

        total_passed = 0
        total_failed = 0

        # Process each workflow
        for workflow in workflows:
            # Parse log file for this workflow
            if workflow == 'login_logout':
                workflow_pattern = f"Starting Login Logout Workflow"
            else:
                workflow_pattern = f"Starting.*{workflow.replace('_', ' ')}"
            logger.info(f"Parsing logs for workflow: {workflow} with pattern: {workflow_pattern}")
            results = self._parse_log_file(workflow_pattern)

            # Update totals
            total_passed += len(results['passed'])
            total_failed += len(results['failed'])

            # Get workflow description
            workflow_desc = self._get_workflow_description(workflow)

            html += f"""
    <h3>Workflow: {workflow}</h3>
    <p><em>{workflow_desc}</em></p>
    <table>
        <tr>
            <th>Status</th>
            <th>Count</th>
        </tr>
        <tr>
            <td>Passed</td>
            <td class="pass">{len(results['passed'])}</td>
        </tr>
        <tr>
            <td>Failed</td>
            <td class="fail">{len(results['failed'])}</td>
        </tr>
        <tr>
            <td>Errors</td>
            <td>{len(results['errors'])}</td>
        </tr>
        <tr>
            <td>Warnings</td>
            <td class="warning">{len(results['warnings'])}</td>
        </tr>
    </table>
"""

            # Add execution time if available
            if results['execution_times']:
                avg_time = sum(results['execution_times']) / len(results['execution_times'])
                html += f"<p><strong>Average Execution Time:</strong> {avg_time:.2f}s</p>"

            # Add screenshots
            screenshots = self._get_screenshots(workflow.split('_')[0].lower())
            if screenshots:
                html += f"<h3>Screenshots for {workflow}</h3>"

                for screenshot in screenshots[:4]:  # Limit to 4 screenshots
                    html += f"""
    <div>
        <p>{os.path.basename(screenshot)}</p>
        <img src="../{screenshot}" alt="{os.path.basename(screenshot)}">
    </div>
"""

            # Add error details if any
            if results['errors']:
                html += f"<h3>Error Details for {workflow}</h3><ul>"

                for i, error in enumerate(results['errors']):
                    html += f"<li>{error}</li>"

                html += "</ul>"

            # Add note if no results found
            if len(results['passed']) == 0 and len(results['failed']) == 0:
                html += f"""
    <div class="note">
        <strong>Note:</strong> No test results found for {workflow}. Run the workflow first to generate logs:
        <code>python run.py {self.module_name}/{workflow}</code>
    </div>
"""

        # Add overall summary
        html += f"""
    <h2>Overall Summary</h2>
    <p><strong>Total Tests:</strong> {total_passed + total_failed}</p>
    <p><strong>Passed:</strong> <span class="pass">{total_passed}</span></p>
    <p><strong>Failed:</strong> <span class="fail">{total_failed}</span></p>
"""

        if total_passed + total_failed > 0:
            success_rate = (total_passed / (total_passed + total_failed)) * 100
            html += f"<p><strong>Success Rate:</strong> {success_rate:.2f}%</p>"
        else:
            html += """
    <div class="note">
        <strong>Note:</strong> No test executions found. Run workflows to generate test results.
    </div>
"""

        html += """
</body>
</html>
"""

        # Save the HTML report
        report_path = os.path.join(self.report_dir, f"{self.module_name}_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        with open(report_path, 'w') as f:
            f.write(html)

        logger.info(f"HTML report generated: {report_path}")
        return report_path

    def _get_workflow_description(self, workflow):
        """Get a description for a workflow"""
        descriptions = {
            'login_logout': 'Standard login and logout test workflow',
            'login_invalid_negative': 'Negative test case for invalid login credentials',
            'forget_password': 'Password reset workflow with OTP verification',
            'forget_password_invalid_username_negative': 'Negative test for password reset with invalid username',
            'forget_password_mismatch_negative': 'Negative test for password reset with mismatched passwords',
            'forget_password_wrong_otp_negative': 'Negative test for password reset with wrong OTP',
            'change_user': 'User information change workflow',
            'change_user_invalid_negative': 'Negative test for user change with invalid data',
            'resend_otp': 'OTP resend functionality test',
            'resend_otp_rate_limit_negative': 'Negative test for OTP resend rate limiting'
        }
        return descriptions.get(workflow, f'Test workflow for {workflow}')

def generate_module_report(module_name, workflows=None):
    """
    Generate a PDF report for a specific module

    Args:
        module_name: Name of the module (e.g., 'LoginLogout')
        workflows: List of workflow names to include in the report

    Returns:
        str: Path to the generated PDF report
    """
    report_generator = TestReport(module_name)
    return report_generator.generate_pdf_report(workflows)
