#!/usr/bin/env python3
"""
Generate report for only positive workflows (expected to succeed)
"""
import os
import re
import logging
from datetime import datetime
from collections import defaultdict
from fpdf import FPDF

class PositiveReportGenerator:
    """Generate PDF report for positive workflows only"""

    def __init__(self):
        self.report_dir = "reports"
        self.log_file = "automation.log"
        os.makedirs(self.report_dir, exist_ok=True)

    def parse_positive_workflows(self):
        """Parse log to extract only positive workflow results"""
        # Define positive workflows (expected to succeed)
        positive_workflows = {
            'LoginLogout': ['login_logout'],
            'ForgetPassword': ['forget_password'],
            'ChangeUser': ['change_user'],
            'Resend_OTP': ['resend_otp']
        }

        results = defaultdict(lambda: {'executed': 0, 'successful': 0, 'failed': 0, 'workflows': []})

        if not os.path.exists(self.log_file):
            return results

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                # Look for workflow completion messages
                workflow_pattern = r'Workflow\s+(\w+)/(\w+)\s+(completed successfully|failed)'
                match = re.search(workflow_pattern, line)

                if match:
                    module_name = match.group(1)
                    workflow_name = match.group(2)
                    status = match.group(3)

                    # Only count positive workflows
                    if module_name in positive_workflows and workflow_name in positive_workflows[module_name]:
                        results[module_name]['executed'] += 1
                        results[module_name]['workflows'].append(workflow_name)

                        if 'completed successfully' in status:
                            results[module_name]['successful'] += 1
                        elif 'failed' in status:
                            results[module_name]['failed'] += 1

        except Exception as e:
            print(f"Error parsing log: {str(e)}")

        return results

    def generate_pdf_report(self):
        """Generate PDF report for positive workflows only"""
        results = self.parse_positive_workflows()

        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 20, 'LMS Automation - Positive Workflows Report', 0, 1, 'C')
        pdf.ln(10)

        # Date
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        pdf.ln(10)

        # Summary
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, 'Positive Workflows Summary', 0, 1, 'L')
        pdf.ln(5)

        pdf.set_font('Arial', '', 12)

        total_executed = sum(module['executed'] for module in results.values())
        total_successful = sum(module['successful'] for module in results.values())
        total_failed = sum(module['failed'] for module in results.values())

        pdf.cell(0, 8, f'Total Positive Workflows: {total_executed}', 0, 1, 'L')
        pdf.cell(0, 8, f'Successful: {total_successful}', 0, 1, 'L')
        pdf.cell(0, 8, f'Failed: {total_failed}', 0, 1, 'L')

        if total_executed > 0:
            success_rate = (total_successful / total_executed) * 100
            pdf.cell(0, 8, f'Success Rate: {success_rate:.1f}%', 0, 1, 'L')

        pdf.ln(10)

        # Module breakdown
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, 'Positive Workflow Results', 0, 1, 'L')
        pdf.ln(5)

        pdf.set_font('Arial', '', 12)

        for module_name, module_results in results.items():
            if module_results['executed'] > 0:
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 12, f'{module_name}:', 0, 1, 'L')

                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 8, f'  Executed: {module_results["executed"]}', 0, 1, 'L')
                pdf.cell(0, 8, f'  Successful: {module_results["successful"]}', 0, 1, 'L')
                pdf.cell(0, 8, f'  Failed: {module_results["failed"]}', 0, 1, 'L')

                if module_results['workflows']:
                    workflows_text = ', '.join(module_results['workflows'])
                    pdf.cell(0, 8, f'  Workflows: {workflows_text}', 0, 1, 'L')

                pdf.ln(5)

        # Save PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(self.report_dir, f'positive_workflows_report_{timestamp}.pdf')
        pdf.output(pdf_path)

        return pdf_path, results

def main():
    """Generate positive workflows report"""
    print("="*80)
    print("GENERATING POSITIVE WORKFLOWS REPORT")
    print("="*80)

    try:
        generator = PositiveReportGenerator()
        report_path, results = generator.generate_pdf_report()

        if report_path:
            print("Positive workflows PDF report generated successfully!")
            print(f"Report saved as: {report_path}")

            total_executed = sum(module['executed'] for module in results.values())
            total_successful = sum(module['successful'] for module in results.values())

            print("\nPositive Workflows Summary:")
            print(f"   Total Executed: {total_executed}")
            print(f"   Successful: {total_successful}")
            print(f"   Failed: {total_executed - total_successful}")
            print(f"   Success Rate: {(total_successful/total_executed*100):.1f}%" if total_executed > 0 else "   Success Rate: 0%")
            print("\nReport location: reports/")
        else:
            print("Failed to generate report")

    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
