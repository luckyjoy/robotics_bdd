# FILENAME: run_docker.py
# DEPENDENCY: deployment_workflow.py (Located in the 'supports' folder and called in Step 6)

import os
import sys
import shutil
import subprocess
import time
import platform # Import the platform module for OS detection

# --- Configuration ---
# Assuming this script is run from the project root.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGE_NAME = "robotics-bdd-local:latest"
ALLURE_RESULTS_DIR = os.path.join(PROJECT_ROOT, "allure-results")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
SUPPORTS_DIR = os.path.join(PROJECT_ROOT, "supports")

def execute_command(command, error_message):
    """Executes a shell command and checks for errors."""
    print(f"\n--- Executing: {' '.join(command)} ---")
    try:
        # Run command, capturing output (STDOUT/STDERR)
        # Using encoding="utf-8" to handle output correctly across platforms
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
        print("--- STDOUT ---")
        print(result.stdout)
        if result.stderr:
            # Check if stderr contains actual error messages or just warnings/info
            # For Docker/Pytest, non-zero exit code handles critical failure, but print stderr anyway
            print("--- STDERR ---")
            print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        # Detailed error handling for non-zero exit code
        print(f"\n==========================================================")
        print(f"CRITICAL ERROR running {error_message} (Exit Code: {e.returncode}):")
        # Print error details from the process if available
        if e.stderr:
            print(e.stderr.strip())
        else:
            print("Command failed, but no specific error output was captured.")
        print(f"==========================================================")
        sys.exit(e.returncode)
    except FileNotFoundError:
        # Error when the base command (e.g., 'docker', 'python') is not in PATH
        print(f"\n==========================================================")
        print(f"CRITICAL ERROR: Command '{command[0]}' not found.")
        print(f"Ensure the command is installed and accessible in your system's PATH.")
        print(f"==========================================================")
        sys.exit(1)

def main():
    """Main workflow runner."""
    if len(sys.argv) < 2:
        print("Error: Missing Build Number argument.")
        print("Usage: python run_docker.py <BUILD_NUMBER>")
        sys.exit(1)
        
    build_number = sys.argv[1].strip()
    
    print("==========================================================")
    print(f"Running Robotics BDD Test Workflow for Build #{build_number}")
    print("==========================================================")

    # 1. Cleanup Previous Artifacts
    print("\nCleaning up old raw results: allure-results, reports/allure-report, __pycache__, .pytest_cache")
    # Use robust cleanup, ignoring errors for non-existent directories
    try:
        shutil.rmtree(ALLURE_RESULTS_DIR, ignore_errors=True)
        shutil.rmtree(os.path.join(REPORTS_DIR, "allure-report"), ignore_errors=True)
        shutil.rmtree(os.path.join(PROJECT_ROOT, "__pycache__"), ignore_errors=True)
        shutil.rmtree(os.path.join(PROJECT_ROOT, ".pytest_cache"), ignore_errors=True)
        
        # Ensure result and report directories exist before proceeding
        os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)
        print("Cleanup complete.")
    except OSError as e:
        print(f"\n==========================================================")
        print(f"CRITICAL ERROR during cleanup or directory creation: {e}")
        print(f"Check permissions for paths: {ALLURE_RESULTS_DIR} and {REPORTS_DIR}")
        print(f"==========================================================")
        sys.exit(1)


    # 2. Check Docker Image 
    print("\n--- Checking Docker Image ---")
    image_check_command = ["docker", "image", "inspect", IMAGE_NAME]
    try:
        # Use execute_command to check if the image is present. It will exit if docker command itself fails.
        execute_command(image_check_command, "Docker Image Check")
        print(f"Image '{IMAGE_NAME}' found locally.")
    except SystemExit:
        # execute_command already printed the error and exited, but we re-raise in case of unexpected flow
        print("Docker image inspection failed. Please ensure the image is built.")
        raise 
    
    # --- Determine OS-specific environment file ---
    system_os = platform.system()
    if system_os == 'Windows':
        env_property_file = "windows.properties"
        print(f"\nDetected OS: {system_os}. Using {env_property_file} for Allure metadata.")
    elif system_os == 'Linux':
        env_property_file = "ubuntu.properties"
        print(f"\nDetected OS: {system_os}. Using {env_property_file} for Allure metadata.")
    else:
        # Fallback if the OS is not explicitly handled 
        env_property_file = "windows.properties" 
        print(f"\nWarning: Unknown OS '{system_os}'. Defaulting to {env_property_file} for Allure metadata.")
    # ---------------------------------------------------------

    # 3. Copy Allure Metadata (Replacing .bat file logic)
    print("\nCopying Allure metadata...")
    
    # Error handling: Check if supports directory exists
    if not os.path.isdir(SUPPORTS_DIR):
        print(f"\n==========================================================")
        print(f"CRITICAL ERROR: Supports directory not found at '{SUPPORTS_DIR}'. Cannot copy Allure metadata.")
        print(f"==========================================================")
        sys.exit(1)

    # Define files to copy
    metadata_files = [
        (env_property_file, "environment.properties"), # OS-specific environment file
        ("categories.json", "categories.json"),           # Custom categories
        ("executor.json", "executor.json"),               # Executor data (if used)
    ]
    
    # Explicit check for the existence of the primary environment file
    env_file_src_path = os.path.join(SUPPORTS_DIR, env_property_file)
    if not os.path.exists(env_file_src_path):
        print(f"  CRITICAL WARNING: The required environment file '{env_property_file}' does not exist in the 'supports' folder.")
        print(f"  Allure report may lack system metadata.")
        # We continue execution as other files might still be copied.

    for src_name, dest_name in metadata_files:
        src_path = os.path.join(SUPPORTS_DIR, src_name)
        dest_path = os.path.join(ALLURE_RESULTS_DIR, dest_name)
        try:
            # Only attempt to copy if the source file exists
            if os.path.exists(src_path):
                shutil.copy2(src_path, dest_path)
                print(f"  Copied: {src_name} to {os.path.basename(dest_path)}")
            else:
                print(f"  Warning: Allure metadata file not found: {src_name}. Skipping copy.")
        except Exception as e:
            print(f"  Error copying {src_name}: {e}")

    # 4. Execute Docker Test Run
    print("\n--- Running Docker Tests ---")
    print(f"Image: {IMAGE_NAME}. Raw results will land in: {os.path.basename(ALLURE_RESULTS_DIR)}")

    # Docker command to run pytest
    docker_test_command = [
        "docker", "run", "--rm",
        "-v", f"{ALLURE_RESULTS_DIR}:/app/allure-results",
        IMAGE_NAME,
        "pytest", 
        "--alluredir=allure-results",
        "-m", "navigation",
        "--ignore=features/manual_tests"
    ]
    
    test_result = execute_command(docker_test_command, "Docker Test Run")
    
    # Check if the test run produced any allure results files
    if not os.listdir(ALLURE_RESULTS_DIR):
        print(f"\n==========================================================")
        print(f"CRITICAL ERROR: No Allure results were generated in '{ALLURE_RESULTS_DIR}'.")
        print(f"Check Pytest configuration inside the Docker image.")
        print(f"==========================================================")
        sys.exit(1)
        
    time.sleep(1) # Give system a moment to finish file writes

    # 5. Allure Report Generation
    print("\n--- Executing: Allure Report Generation (via Docker) ---")
    allure_report_output = os.path.join(REPORTS_DIR, "allure-report") # Temporary folder
    os.makedirs(allure_report_output, exist_ok=True)
    
    docker_allure_command = [
        "docker", "run", "--rm",
        "-v", f"{ALLURE_RESULTS_DIR}:/app/allure-results",
        "-v", f"{allure_report_output}:/app/allure-report",
        IMAGE_NAME,
        "allure", "generate", "allure-results", "-o", "allure-report", "--clean"
    ]
    execute_command(docker_allure_command, "Allure Report Generation (via Docker)")

    # 6. Report Deployment (Calls the existing deployment_workflow.py)
    print("\n--- Executing: Report Deployment Workflow ---")
    
    deployment_script_path = os.path.join(SUPPORTS_DIR, "deployment_workflow.py")
    
    # Error handling: Check if the deployment script exists
    if not os.path.exists(deployment_script_path):
        print(f"\n==========================================================")
        print(f"CRITICAL ERROR: Deployment script not found at '{deployment_script_path}'. Skipping deployment.")
        print(f"==========================================================")
        sys.exit(1)

    # Error handling: Check if Allure report index file was successfully generated
    allure_index_check = os.path.join(allure_report_output, "index.html")
    if not os.path.exists(allure_index_check):
        print(f"\n==========================================================")
        print(f"CRITICAL ERROR: Allure report index.html not found at '{allure_report_output}'.")
        print(f"The report generation step (5) likely failed or produced an empty report.")
        print(f"Skipping deployment.")
        print(f"==========================================================")
        sys.exit(1)

    deployment_command = [
        sys.executable,  # Use the current Python interpreter
        deployment_script_path, 
        build_number, 
        PROJECT_ROOT
    ]
    # Execute the deployment command
    execute_command(deployment_command, "Report Deployment Workflow")
    
    print("\n--- Workflow Complete ---")

if __name__ == '__main__':
    # Get project root first, before any potential os.chdir that might move the context
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    # Change directory to project root for clean relative path handling across all modules
    os.chdir(PROJECT_ROOT) 
    
    try:
        main()
    except Exception as e:
        # Catch any final uncaught exceptions
        print(f"\n==========================================================")
        print(f"UNEXPECTED CRITICAL FAILURE in main workflow: {e}")
        print(f"==========================================================")
        sys.exit(1)
