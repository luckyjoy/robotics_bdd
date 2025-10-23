import sys
import subprocess
import os
import argparse
import platform
import shutil

# Constants
LOCAL_IMAGE_TAG = "luckyjoy/robotics-bdd-local:latest"
IMAGE_ID_FILE = "python_image_id.tmp" # File to pass data back to the batch script

def execute_command(command, error_message, check_output=False):
    """Executes a shell command and handles errors."""
    try:
        # Use subprocess.run for simplicity and reliable error checking
        result = subprocess.run(
            command,
            shell=True,
            check=True,  # Raise CalledProcessError if return code is non-zero
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            # Use 'utf-8' encoding for output to handle checkmarks/other symbols
            encoding='utf-8',
            universal_newlines=True
        )
        if check_output:
            return result.stdout.strip()
        print("--- STDOUT ---")
        print(result.stdout.strip())
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"\n==========================================================")
        print(f"FATAL UNHANDLED ERROR during command execution: {error_message}")
        print(f"Command failed: {command}")
        print(f"Return Code: {e.returncode}")
        print(f"Output: {e.output.strip()}")
        print(f"==========================================================")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(f"\n==========================================================")
        print(f"FATAL ERROR: Command not found. Is '{command.split()[0]}' installed and in PATH?")
        print(f"==========================================================")
        sys.exit(1)


def get_local_image_id():
    """Gets the full image ID for the local tag."""
    try:
        # Use docker inspect to get the full SHA ID (not just the short one)
        image_id = execute_command(
            f"docker inspect --format='{{{{.Id}}}}' {LOCAL_IMAGE_TAG}",
            f"Failed to inspect image {LOCAL_IMAGE_TAG}",
            check_output=True
        )
        # Clean up the output to ensure no extra whitespace
        return image_id.strip()
    except Exception:
        # If inspect fails (e.g., image doesn't exist), return None
        return None

def build_image_if_missing():
    """Checks if the local Docker image exists and builds it if necessary."""
    print("--- Checking for local Docker Image ---")
    
    local_id = get_local_image_id()

    if local_id:
        print(f"✅ Image {LOCAL_IMAGE_TAG} found locally (ID: {local_id[:12]}). Skipping build.")
        return local_id
    else:
        print(f"⚠️ Image {LOCAL_IMAGE_TAG} not found locally. Starting build...")
        execute_command(
            f"docker build -t {LOCAL_IMAGE_TAG} .",
            "Docker build failed."
        )
        new_local_id = get_local_image_id()
        if new_local_id:
            print(f"✅ Docker image built successfully (ID: {new_local_id[:12]}).")
            return new_local_id
        else:
            print("CRITICAL ERROR: Docker build succeeded but image ID could not be retrieved.")
            sys.exit(1)


def main():
    """Main execution function for the BDD workflow."""
    
    # ----------------------------------------
    # FIX: Set encoding for Windows console output
    # This prevents UnicodeEncodeError when printing checkmarks (✅)
    # ----------------------------------------
    if platform.system() == "Windows":
        try:
            # Set console to UTF-8
            subprocess.run("chcp 65001", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            # Fallback if chcp fails
            pass
    
    parser = argparse.ArgumentParser(description="Run Robotics BDD Tests via Docker.")
    parser.add_argument("build_number", type=int, help="The unique build identifier.")
    parser.add_argument("suite", type=str, nargs='?', default='all', help="The pytest marker for the test suite.")
    
    args = parser.parse_args()
    
    print(f"==========================================================")
    print(f"Running Robotics BDD Test Workflow for Build #{args.build_number} | Suite: {args.suite}")
    print(f"==========================================================")

    # --- Docker Daemon Check ---
    print("--- Checking Docker Daemon Status ---")
    try:
        execute_command("docker info", "Docker daemon is not running or not reachable.", check_output=True)
        print("✅ Docker is running and responsive.")
    except subprocess.CalledProcessError:
        print("❌ Docker daemon is not running. Please start Docker and retry.")
        sys.exit(1)

    # --- Build Image Conditionally ---
    local_image_id = build_image_if_missing()
    
    # --- Pass image ID back to batch file via dedicated file ---
    with open(IMAGE_ID_FILE, 'w', encoding='utf-8') as f:
        f.write(local_image_id.strip())
    
    # --- Step 1: Prepare Workspace and History ---
    print("\n--- Step 1: Prepare Workspace and History ---")
    
    # Define directories
    allure_results_dir = "allure-results"
    allure_report_dir = os.path.join("reports", "allure-report")

    # Cleanup local results and cache
    if os.path.exists(allure_results_dir):
        print("1a. Cleaning up old dynamic results (allure-results, reports/allure-report)")
        shutil.rmtree(allure_results_dir, ignore_errors=True)
        shutil.rmtree(allure_report_dir, ignore_errors=True)
    else:
        print("1a. Initializing workspace.")
        
    # FIX: Ensure allure-results directory exists before Step 3 copies files into it
    os.makedirs(allure_results_dir, exist_ok=True)
    
    # Check for history
    if os.path.exists(os.path.join("reports", "history")):
        print("1b. Found previous report history.")
    else:
        print("1b. Previous report history not found. The first run will not show trend data.")
        
    print("Cleanup and history preparation complete.")

    # --- Step 3: Preparing Allure Metadata ---
    print("\n--- Step 3: Preparing Allure Metadata ---")
    
    # Determine the correct path for properties file
    if platform.system() == "Windows":
        properties_file_source = "supports\\windows.properties"
        categories_file_source = "supports\\categories.json"
    else:
        properties_file_source = "supports/linux.properties" # Placeholder
        categories_file_source = "supports/categories.json"
        
    properties_file_dest = os.path.join(allure_results_dir, "environment.properties")
    categories_file_dest = os.path.join(allure_results_dir, "categories.json")
    
    # Copy environment properties
    execute_command(
        f"copy {properties_file_source} {properties_file_dest}",
        "Failed to copy environment properties.",
        check_output=False
    )
    print(f"  Copied: {properties_file_source} -> environment.properties")
    
    # Copy categories.json
    execute_command(
        f"copy {categories_file_source} {categories_file_dest}",
        "Failed to copy categories.json.",
        check_output=False
    )
    print(f"  Copied: {categories_file_source} -> categories.json")

    # --- Step 4: Running Docker Tests ---
    print("\n--- Step 4: Running Docker Tests ---")
    
    # Docker command with volume mount for results and pytest marker
    test_command = (
        f"docker run --rm "
        f"-v {os.getcwd()}\\{allure_results_dir}:/app/allure-results "
        f"{LOCAL_IMAGE_TAG} "
        f"pytest --alluredir=allure-results -m {args.suite} --ignore=features/manual_tests"
    )
    print(f"\n--- Executing: {test_command} ---")
    execute_command(test_command, "Test execution failed inside Docker container.")
    
    print("\n--- Steps 1-4 (Test Execution & Setup) Complete ---")

    # --- Step 5: Allure Report Generation (via Docker) ---
    print("\n--- Step 5: Allure Report Generation (via Docker) ---")

    # Ensure the report directory is created before mounting it
    os.makedirs(allure_report_dir, exist_ok=True)

    # Docker command to generate report from results
    report_command = (
        f"docker run --rm "
        f"-v {os.getcwd()}\\{allure_results_dir}:/app/allure-results "
        f"-v {os.getcwd()}\\{allure_report_dir}:/app/allure-report "
        f"{LOCAL_IMAGE_TAG} "
        f"allure generate allure-results -o allure-report --clean"
    )
    print(f"\n--- Executing: {report_command} ---")
    execute_command(report_command, "Allure report generation failed.")
    
    # --- Step 6: Prepare Report for Publishing (Create Dockerfile) ---
    print("\n--- Step 6: Prepare Report for Publishing (Create Dockerfile) ---")

    report_folder = os.path.join(os.getcwd(), allure_report_dir)
    report_dockerfile_path = os.path.join(report_folder, "Dockerfile")

    # 1. Generate simple HTML landing page (still kept locally for linking)
    index_html_path = os.path.join(os.getcwd(), "index.html")
    with open(index_html_path, "w") as f:
        f.write(f"<html><head><title>Build {args.build_number} Report</title></head><body>")
        f.write(f"<h1>Robotics BDD Test Report - Build #{args.build_number} ({args.suite})</h1>")
        f.write('<p>View the full report: <a href="reports/allure-report/index.html">Allure Report</a></p>')
        f.write("</body></html>")
    
    print("  ✅ Created central landing page at index.html.")

    # 2. Create Dockerfile inside the allure-report directory to serve the static files
    # This Dockerfile will be built in the next batch step.
    dockerfile_content = (
        "FROM nginx:stable-alpine\n"
        "LABEL maintainer=\"CI Pipeline\"\n"
        f"ENV REPORT_BUILD_NUMBER={args.build_number}\n"
        "# Copy the static HTML report files (the Allure report) into the Nginx web root\n"
        "COPY . /usr/share/nginx/html\n"
        "EXPOSE 80\n"
        "CMD [\"nginx\", \"-g\", \"daemon off;\"]\n"
    )

    with open(report_dockerfile_path, "w") as f:
        f.write(dockerfile_content)

    print(f"  ✅ Created Report Dockerfile at: {report_dockerfile_path}")

    print("\n--- Workflow Complete ---")

if __name__ == "__main__":
    main()
