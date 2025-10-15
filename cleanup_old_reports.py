#!/usr/bin/env python3
"""
Script to clean up old reports and keep only the latest one
Moves old reports to a backup folder
"""
import os
import shutil
from datetime import datetime
import glob

def cleanup_reports():
    """Move old reports to backup folder, keep only the latest"""
    
    reports_dir = "reports"
    backup_dir = os.path.join(reports_dir, "backup")
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"✅ Created backup directory: {backup_dir}")
    
    # Find all PDF reports (excluding backup folder)
    pdf_pattern = os.path.join(reports_dir, "*.pdf")
    pdf_reports = [f for f in glob.glob(pdf_pattern) if "backup" not in f]
    
    # Find all HTML reports (excluding backup folder)
    html_pattern = os.path.join(reports_dir, "*.html")
    html_reports = [f for f in glob.glob(html_pattern) if "backup" not in f]
    
    # Process PDF reports
    if len(pdf_reports) > 1:
        # Sort by modification time, newest first
        pdf_reports.sort(key=os.path.getmtime, reverse=True)
        
        latest_pdf = pdf_reports[0]
        old_pdfs = pdf_reports[1:]
        
        print(f"\n📄 PDF Reports:")
        print(f"   ✅ Keeping latest: {os.path.basename(latest_pdf)}")
        
        for old_pdf in old_pdfs:
            backup_path = os.path.join(backup_dir, os.path.basename(old_pdf))
            shutil.move(old_pdf, backup_path)
            print(f"   📦 Moved to backup: {os.path.basename(old_pdf)}")
    elif len(pdf_reports) == 1:
        print(f"\n📄 PDF Reports:")
        print(f"   ✅ Only one PDF report found: {os.path.basename(pdf_reports[0])}")
    else:
        print(f"\n📄 PDF Reports:")
        print(f"   ⚠️  No PDF reports found")
    
    # Process HTML reports
    if len(html_reports) > 1:
        # Sort by modification time, newest first
        html_reports.sort(key=os.path.getmtime, reverse=True)
        
        latest_html = html_reports[0]
        old_htmls = html_reports[1:]
        
        print(f"\n🌐 HTML Reports:")
        print(f"   ✅ Keeping latest: {os.path.basename(latest_html)}")
        
        for old_html in old_htmls:
            backup_path = os.path.join(backup_dir, os.path.basename(old_html))
            shutil.move(old_html, backup_path)
            print(f"   📦 Moved to backup: {os.path.basename(old_html)}")
    elif len(html_reports) == 1:
        print(f"\n🌐 HTML Reports:")
        print(f"   ✅ Only one HTML report found: {os.path.basename(html_reports[0])}")
    else:
        print(f"\n🌐 HTML Reports:")
        print(f"   ⚠️  No HTML reports found")
    
    # Process module-specific reports
    module_reports = glob.glob(os.path.join(reports_dir, "*_Report_*.html"))
    module_reports = [f for f in module_reports if "backup" not in f]
    
    if module_reports:
        print(f"\n📊 Module Reports:")
        for report in module_reports:
            backup_path = os.path.join(backup_dir, os.path.basename(report))
            shutil.move(report, backup_path)
            print(f"   📦 Moved to backup: {os.path.basename(report)}")
    
    print(f"\n✅ Cleanup complete!")
    print(f"📁 Backup location: {backup_dir}")
    
    # Show summary
    total_in_backup = len(os.listdir(backup_dir))
    print(f"📦 Total files in backup: {total_in_backup}")

if __name__ == "__main__":
    try:
        cleanup_reports()
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        import traceback
        traceback.print_exc()

