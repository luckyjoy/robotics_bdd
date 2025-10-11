import shutil
import os
import sys
from datetime import datetime

# --- Configuration ---
# Assuming reports are initially generated into the 'reports' directory in the project root.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports')
INDEX_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, 'index.html')
# The Allure report is generated into 'allure-report' in the project root by the batch file.
ALLURE_REPORT_SOURCE_DIR = os.path.join(PROJECT_ROOT, 'allure-report') 

REPORT_FILENAMES = [
    'Validation_Plan.html',
    'automation_rate_report.html',
    'prd_summary.html',
    'test_coverage_report.html',
    # Note: 'allure' is handled separately as it's a directory
]

def deploy_reports():
    """
    Manages the report deployment, copying all artifacts into a new build folder
    and updating the main index.html dashboard.
    """
    
    # 1. Get Build Number from command line argument
    if len(sys.argv) < 2:
        print("Error: Missing Build Number argument.")
        print("Usage: python deployment_workflow.py <BUILD_NUMBER>")
        sys.exit(1)
        
    build_number = sys.argv[1].strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n--- Starting Report Deployment for Build #{build_number} ---")

    # 2. Define the target directory for this build
    target_build_dir = os.path.join(REPORTS_DIR, build_number)
    
    if os.path.exists(target_build_dir):
        print(f"Warning: Deleting existing directory: {target_build_dir}")
        shutil.rmtree(target_build_dir)
        
    os.makedirs(target_build_dir)
    print(f"Created new build directory: {target_build_dir}")

    # 3. Move Custom HTML Reports
    print("\nMoving custom HTML reports...")
    for filename in REPORT_FILENAMES:
        # FIX: Change source path from REPORTS_DIR to PROJECT_ROOT, assuming custom reports 
        # are generated into the project root directory (C:\my_work\robotics_bdd) initially.
        source_path = os.path.join(PROJECT_ROOT, filename)
        target_path = os.path.join(target_build_dir, filename)
        if os.path.exists(source_path):
            shutil.move(source_path, target_path)
            print(f"  Moved: {filename}")
        else:
            # Revert the warning message to reflect checking the project root.
            print(f"  Warning: Custom report not found: {filename} at {PROJECT_ROOT}.")
            
    # 4. Move Allure Report Folder
    # The batch script places the final report output in 'allure-report' in the project root.
    allure_source = ALLURE_REPORT_SOURCE_DIR # Points to C:\my_work\robotics_bdd\allure-report
    # The final location in the build must be 'allure' for the index.html link to work: reports/<BUILD_NUMBER>/allure/index.html
    allure_target = os.path.join(target_build_dir, 'allure') 
    
    if os.path.exists(allure_source):
        # We move the 'allure-report' folder and rename it to 'allure' in the target directory.
        shutil.move(allure_source, allure_target) 
        print(f"  Moved Allure report folder from '{os.path.basename(allure_source)}' to: {allure_target}")
    else:
        # The error message is already clear about the location. We cannot fix the Allure generation
        # failing here, but we can ensure the check is correct.
        print(f"  Error: Allure report folder not found at '{ALLURE_REPORT_SOURCE_DIR}'.")


    # 5. Update and Write index.html Dashboard
    print("\nUpdating index.html with new build information...")
    try:
        with open(INDEX_TEMPLATE_PATH, 'r') as f:
            content = f.read()
            
        content = content.replace('{{BUILD_NUMBER}}', build_number)
        content = content.replace('{{RUN_TIMESTAMP}}', timestamp)

        with open(INDEX_TEMPLATE_PATH, 'w') as f:
            f.write(content)
            
        print("Successfully updated index.html dashboard.")
        
    except FileNotFoundError:
        print(f"Error: index.html not found at {INDEX_TEMPLATE_PATH}. Cannot update dashboard.")
        sys.exit(1)
        
    print(f"\nDeployment for Build #{build_number} is complete. Ready for Git push.")

if __name__ == '__main__':
    deploy_reports()
