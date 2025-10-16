#!/usr/bin/env python3
"""
Generate comprehensive PDF report with accurate data from existing logs
"""
import os
import re
import logging
from datetime import datetime
from collections import defaultdict
from fpdf import FPDF

class AccurateReportGenerator:
    """Generate comprehensive PDF report with accurate workflow execution data"""

    def __init__(self):
        self.report_dir = "reports"
        self.log_file = "automation.log"

        # Define positive workflows only (for filtering)
        self.positive_workflows = {
            'LoginLogout': ['login_logout'],
            'ForgetPassword': ['forget_password'],
            'ChangeUser': ['change_user'],
            'Resend_OTP': ['resend_otp']
        }

        # Ensure directories exist
        os.makedirs(self.report_dir, exist_ok=True)

    def parse_workflow_results(self):
        """Parse automation log to extract workflow execution results"""
        results = defaultdict(lambda: {'executed': 0, 'successful': 0, 'failed': 0, 'workflows': set()})

        if not os.path.exists(self.log_file):
            return results

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                # Pattern for workflow completion messages (both success and failure)
                workflow_pattern = r'Workflow\s+(\w+)/(\w+)\s+(completed successfully|failed)'
                match = re.search(workflow_pattern, line)

                if match:
                    module_name = match.group(1)
                    workflow_name = match.group(2)
                    status = match.group(3)

                    # Only count positive workflows
                    if (module_name in self.positive_workflows and
                        workflow_name in self.positive_workflows[module_name]):

                        # Use set to avoid duplicates
                        results[module_name]['workflows'].add(workflow_name)
                        results[module_name]['executed'] += 1

                        if 'completed successfully' in status:
                            results[module_name]['successful'] += 1
                        elif 'failed' in status:
                            results[module_name]['failed'] += 1

            # Convert sets to lists for display
            for module in results:
                results[module]['workflows'] = list(results[module]['workflows'])

        except Exception as e:
            print(f"Error parsing log: {str(e)}")

        return results

    def _add_screenshots_section(self, pdf):
        """Add screenshots section to the PDF"""
        screenshot_dir = "screenshots"

        if not os.path.exists(screenshot_dir):
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 15, 'Screenshots', 0, 1, 'L')
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, 'No screenshots directory found.', 0, 1, 'L')
            return

        # Get relevant screenshots
        screenshots = self._get_relevant_screenshots()

        if not screenshots:
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 15, 'Screenshots', 0, 1, 'L')
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, 'No relevant screenshots found for the executed workflows.', 0, 1, 'L')
            return

        pdf.ln(10)
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, 'Test Execution Screenshots', 0, 1, 'L')
        pdf.ln(5)

        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f'Found {len(screenshots)} relevant screenshots from test executions:', 0, 1, 'L')
        pdf.ln(5)

        # Group screenshots by module
        screenshots_by_module = {}
        for screenshot in screenshots:
            for module in ['LoginLogout', 'ForgetPassword', 'ChangeUser', 'Resend_OTP']:
                if module.lower() in screenshot.lower():
                    if module not in screenshots_by_module:
                        screenshots_by_module[module] = []
                    screenshots_by_module[module].append(screenshot)
                    break

        # Add screenshots for each module
        for module_name in ['LoginLogout', 'ForgetPassword', 'ChangeUser', 'Resend_OTP']:
            if module_name in screenshots_by_module and screenshots_by_module[module_name]:
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 12, f'{module_name} Screenshots:', 0, 1, 'L')

                # Show first few screenshots for this module
                module_screenshots = screenshots_by_module[module_name][:3]  # Limit to 3 per module

                for i, screenshot_path in enumerate(module_screenshots):
                    try:
                        # Add image to PDF (adjust dimensions as needed)
                        pdf.image(screenshot_path, x=20, y=None, w=170, h=100)
                        pdf.ln(105)  # Space after image

                        # Add caption
                        pdf.set_font('Arial', 'I', 10)
                        pdf.cell(0, 6, f'Screenshot {i+1}: {os.path.basename(screenshot_path)}', 0, 1, 'L')
                        pdf.ln(3)

                    except Exception as e:
                        pdf.cell(0, 8, f'Could not add screenshot {screenshot_path}: {str(e)}', 0, 1, 'L')

                pdf.ln(5)

        # Summary
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f'Total screenshots captured: {len(screenshots)}', 0, 1, 'L')
        pdf.cell(0, 8, 'Screenshots are saved in the screenshots/ directory for detailed review.', 0, 1, 'L')

    def _get_relevant_screenshots(self):
        """Get screenshots relevant to executed workflows"""
        screenshot_dir = "screenshots"
        screenshots = []

        if not os.path.exists(screenshot_dir):
            return screenshots

        # Keywords to look for in screenshot filenames
        relevant_keywords = [
            'login', 'logout', 'success', 'error', 'change_user', 'forget_password',
            'resend_otp', 'password_reset', 'user_not_found', 'validation_error'
        ]

        try:
            for file in os.listdir(screenshot_dir):
                if file.endswith('.png'):
                    filename_lower = file.lower()
                    # Check if any relevant keyword is in the filename
                    if any(keyword in filename_lower for keyword in relevant_keywords):
                        screenshots.append(os.path.join(screenshot_dir, file))

            # Sort by modification time (newest first)
            screenshots.sort(key=os.path.getmtime, reverse=True)

        except Exception as e:
            print(f"Error getting screenshots: {str(e)}")

        return screenshots

    def generate_pdf_report(self):
        """Generate comprehensive PDF report"""
        # Parse workflow results
        results = self.parse_workflow_results()

        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # Set up fonts and colors
        pdf.set_font('Arial', 'B', 20)

        # Title
        pdf.cell(0, 20, 'LMS Automation - Positive Workflows Report', 0, 1, 'C')
        pdf.ln(10)

        # Date
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        pdf.ln(10)

        # Summary section
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, 'Positive Workflows Execution Summary', 0, 1, 'L')
        pdf.ln(5)

        pdf.set_font('Arial', '', 12)

        # Calculate totals
        total_executed = sum(module['executed'] for module in results.values())
        total_successful = sum(module['successful'] for module in results.values())
        total_failed = sum(module['failed'] for module in results.values())

        pdf.cell(0, 8, f'Total Workflows Executed: {total_executed}', 0, 1, 'L')
        pdf.cell(0, 8, f'Successful Executions: {total_successful}', 0, 1, 'L')
        pdf.cell(0, 8, f'Failed Executions: {total_failed}', 0, 1, 'L')

        if total_executed > 0:
            success_rate = (total_successful / total_executed) * 100
            pdf.cell(0, 8, f'Success Rate: {success_rate:.1f}%', 0, 1, 'L')

        pdf.ln(10)

        # Module-wise breakdown
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, 'Positive Workflows Execution Results', 0, 1, 'L')
        pdf.ln(5)

        pdf.set_font('Arial', '', 12)

        for module_name, module_results in results.items():
            if module_results['executed'] > 0:  # Only show modules that were executed
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 12, f'{module_name}:', 0, 1, 'L')

                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 8, f'  Workflows Executed: {module_results["executed"]}', 0, 1, 'L')
                pdf.cell(0, 8, f'  Successful: {module_results["successful"]}', 0, 1, 'L')
                pdf.cell(0, 8, f'  Failed: {module_results["failed"]}', 0, 1, 'L')

                if module_results['workflows']:
                    workflows_text = ', '.join(module_results['workflows'])
                    pdf.cell(0, 8, f'  Workflows Tested: {workflows_text}', 0, 1, 'L')

                pdf.ln(5)

        # Test coverage section
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, 'Positive Workflows Test Coverage', 0, 1, 'L')
        pdf.ln(5)

        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, 'The following positive test scenarios have been executed:', 0, 1, 'L')
        pdf.ln(3)

        # Define expected positive workflows for each module (only positive ones)
        expected_workflows = self.positive_workflows.copy()

        for module_name, workflows in expected_workflows.items():
            if module_name in results and results[module_name]['executed'] > 0:
                executed_workflows = results[module_name]['workflows']
                expected_set = set(workflows)

                coverage = len(executed_workflows) / len(expected_set) * 100

                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, f'  {module_name}:', 0, 1, 'L')
                pdf.set_font('Arial', '', 11)
                pdf.cell(0, 6, f'    Coverage: {coverage:.1f}% ({len(executed_workflows)}/{len(expected_set)} workflows)', 0, 1, 'L')
                pdf.cell(0, 6, f'    Executed: {", ".join(executed_workflows)}', 0, 1, 'L')

                pdf.ln(3)

        # Screenshots section
        self._add_screenshots_section(pdf)

        # Save PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(self.report_dir, f'comprehensive_report_{timestamp}.pdf')

        pdf.output(pdf_path)

        return pdf_path, results

def main():
    """Generate PDF report for positive workflows only"""
    print("="*80)
    print("GENERATING POSITIVE WORKFLOWS REPORT")
    print("="*80)

    try:
        generator = AccurateReportGenerator()
        report_path, results = generator.generate_pdf_report()

        if report_path:
            print("Positive workflows PDF report generated successfully!")
            print(f"Report saved as: {report_path}")

            # Show summary
            total_executed = sum(module['executed'] for module in results.values())
            total_successful = sum(module['successful'] for module in results.values())
            total_failed = sum(module['failed'] for module in results.values())

            print("\nPositive Workflows Summary:")
            print(f"   Total Positive Workflows Executed: {total_executed}")
            print(f"   Successful: {total_successful}")
            print(f"   Failed: {total_failed}")
            print(f"   Success Rate: {(total_successful/total_executed*100):.1f}%" if total_executed > 0 else "   Success Rate: 0%")
            print("\nReport location: reports/")
            print("Old reports moved to: reports/backup/")
        else:
            print("Failed to generate report")

    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
