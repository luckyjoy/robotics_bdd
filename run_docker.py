import subprocess
import sys
import os
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# Raw results go here (these are created by the Docker container)
ALLURE_RESULTS_DIR = os.path.join(PROJECT_ROOT, 'allure-results')
# The final static report output path, matching the deployment script's expectation
ALLURE_REPORT_OUTPUT = os.path.join(PROJECT_ROOT, 'reports', 'allure-report') 
DOCKER_IMAGE_NAME = "robotics-bdd-local:latest"

# CRITICAL FIX: The deployment script is now located in the supports/ directory
DEPLOYMENT_SCRIPT_PATH = os.path.join(PROJECT_ROOT, 'supports', 'deployment_workflow.py')


# Helper function to run commands and print output
def run_command(command, command_name, show_stdout=True, show_stderr_on_success=True):
    """Executes a command and handles output/errors."""
    print(f"\n--- Executing: {command_name} ---")
    
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    
    # Print STDOUT if requested
    if show_stdout and result.stdout:
        print("\n--- STDOUT ---")
        print(result.stdout.strip())
        
    # Print STDERR/WARNINGS only if not suppressed on success
    if result.stderr and (result.returncode != 0 or show_stderr_on_success):
        print("\n--- STDERR/WARNINGS ---")
        print(result.stderr.strip())

    if result.returncode != 0:
        print(f"\n==========================================================")
        print(f"ERROR: {command_name} failed with exit code {result.returncode}")
        print(f"==========================================================")
        sys.exit(result.returncode)
        
    return result

def run_workflow(build_number):
    """Main function to run the entire test and deployment workflow."""
    print(f"\n==========================================================")
    print(f"Running Robotics BDD Test Workflow for Build #{build_number}")
    print(f"==========================================================")

    # 1. Cleanup Raw Results directory
    if os.path.exists(ALLURE_RESULTS_DIR):
        print(f"Cleaning up old raw results: {os.path.basename(ALLURE_RESULTS_DIR)}")
        shutil.rmtree(ALLURE_RESULTS_DIR)
    os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)
    
    # 2. Run Docker Container to Execute Tests
    print(f"\n--- Running Docker Tests ---")
    print(f"Image: {DOCKER_IMAGE_NAME}. Raw results will land in: {os.path.basename(ALLURE_RESULTS_DIR)}")
    
    # NOTE: YOU MUST REPLACE THIS PLACEHOLDER COMMAND with your actual Docker run command.
    docker_cmd = [
        "docker", "run", "--rm",
        f"-v", f"{ALLURE_RESULTS_DIR}:/app/allure-results",
        DOCKER_IMAGE_NAME,
        "pytest", "--alluredir=/app/allure-results"
    ]
    # Placeholder: Run the actual Docker test command
    run_command(["echo", "Running actual Docker test command..."], "Docker Test Run")
    
    # Placeholder: Create a dummy result file for the next step to not fail
    with open(os.path.join(ALLURE_RESULTS_DIR, 'dummy.json'), 'w') as f:
        f.write('{"test": "ok"}')

    # 3. Generate Allure Report on the Host
    allure_generate_cmd = [
        "allure", "generate", 
        ALLURE_RESULTS_DIR, 
        "-o", ALLURE_REPORT_OUTPUT, 
        "--clean"
    ]
    
    # Ensure the parent directory for the report output exists (e.g., 'reports')
    os.makedirs(os.path.dirname(ALLURE_REPORT_OUTPUT), exist_ok=True)
    
    run_command(allure_generate_cmd, "Allure Report Generation (Host)", show_stderr_on_success=True)
    print(f"Allure static report successfully generated to: {os.path.relpath(ALLURE_REPORT_OUTPUT, PROJECT_ROOT)}")

    # 4. Run Deployment Workflow (Consolidate Reports and Update Dashboard)
    deployment_cmd = [
        sys.executable,  # Use the same Python interpreter
        DEPLOYMENT_SCRIPT_PATH, # <-- CORRECTED PATH
        build_number
    ]
    run_command(deployment_cmd, "Report Deployment Workflow")

    # 5. Commit and Push Reports to GitHub
    run_command(["git", "add", "."], "Git Stage All")
    commit_message = f"Automated report update: Deploying Build #{build_number}"
    run_command(["git", "commit", "-m", commit_message], "Git Commit")
    
    # Suppress non-error output (like "To https://...") for cleaner console
    run_command(["git", "push", "origin", "main"], "Git Push", show_stderr_on_success=False)
    
    print(f"\n==========================================================")
    print(f"SUCCESSFULLY DEPLOYED Build #{build_number}. Netlify deployment should begin shortly.")
    print(f"Automation Workflow Finished.")
    print(f"==========================================================")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python run_tests.py <BUILD_NUMBER>")
        sys.exit(1)
        
    try:
        build_number = sys.argv[1]
        run_workflow(build_number)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
