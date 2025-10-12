import os
import sys
import shutil
import subprocess
import time
import platform  # Import the platform module for OS detection
import json

# FILENAME: run_docker.py
# DEPENDENCY: deployment_workflow.py (Located in the 'supports' folder and called in Step 6)
# NOTE: This script orchestrates the full test lifecycle, including cleanup, Docker execution,
# report generation, deployment (via deployment_workflow), and final git commit/push.

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGE_NAME = "robotics-bdd-local:latest"
ALLURE_RESULTS_DIR = os.path.join(PROJECT_ROOT, "allure-results")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
ALLURE_REPORT_DIR = os.path.join(REPORTS_DIR, "allure-report")
SUPPORTS_DIR = os.path.join(PROJECT_ROOT, "supports")
DASHBOARD_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "index.html")
NETLIFY_REPORT_PATH = "/reports/latest"


def execute_command(command, error_message):
    """Executes a shell command and checks for errors."""
    print(f"\n--- Executing: {' '.join(command)} ---")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("--- STDOUT ---")
        print(result.stdout)
        if result.stderr:
            print("--- STDERR (Warnings/Notices) ---")
            print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"\n==========================================================")
        print(f"CRITICAL ERROR running {error_message}: {e.stderr.strip()}")
        print(f"==========================================================")
        if error_message != "Git Commit/Push":
            sys.exit(e.returncode)
    except FileNotFoundError:
        print(f"\n==========================================================")
        print(f"CRITICAL ERROR: Command not found. Ensure Docker, Python, and Git are in your PATH.")
        print(f"==========================================================")
        sys.exit(1)


def git_commit_and_push(build_number):
    """Commits the generated reports and pushes to the repository."""
    print("\n--- Step 8: Committing and Pushing Reports ---")

    try:
        print("  -> Adding reports and dashboard files.")
        execute_command(["git", "add", "index.html", "_redirects", "reports/"], "Git Add (Reports)")

        print("  -> Force-adding raw results (allure-results) as it is usually ignored.")
        execute_command(["git", "add", "-f", "allure-results"], "Git Add (Raw Results - Force)")

        commit_message = f"CI: New test report and dashboard for Build #{build_number}"
        execute_command(["git", "commit", "-m", commit_message], "Git Commit")
        execute_command(["git", "push"], "Git Push")

        print(f"\nSuccessfully committed and pushed reports for Build #{build_number}. Netlify build triggered.")
    except Exception as e:
        print(f"\nWARNING: Git push failed. The report files are generated locally but were not uploaded. Error: {e}")


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

    # --- Step 1: Prepare Workspace and History ---
    print("\n--- Step 1: Prepare Workspace and History ---")
    LAST_HISTORY_SOURCE = os.path.join(REPORTS_DIR, "latest", "history")
    HISTORY_DESTINATION = os.path.join(ALLURE_RESULTS_DIR, "history")

    print("1a. Cleaning up old raw results (allure-results, __pycache__, .pytest_cache)")
    shutil.rmtree(ALLURE_RESULTS_DIR, ignore_errors=True)
    shutil.rmtree(os.path.join(REPORTS_DIR, "allure-report"), ignore_errors=True)
    shutil.rmtree(os.path.join(PROJECT_ROOT, "__pycache__"), ignore_errors=True)
    shutil.rmtree(os.path.join(PROJECT_ROOT, ".pytest_cache"), ignore_errors=True)

    os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    if os.path.exists(LAST_HISTORY_SOURCE):
        print(f"1b. Copying previous history from '{LAST_HISTORY_SOURCE}' to '{HISTORY_DESTINATION}'")
        try:
            shutil.copytree(LAST_HISTORY_SOURCE, HISTORY_DESTINATION)
        except Exception as e:
            print(f"  Warning: Failed to copy history folder. Trend data might be missing. Error: {e}")
    else:
        print("1b. Previous report history not found. The first run will not show trend data.")

    print("Cleanup and history preparation complete.")

    # --- Step 2: Docker Image Check ---
    print("\n--- Step 2: Docker Image Check ---")
    execute_command(["docker", "images", IMAGE_NAME], "Docker Image Check")

    system_os = platform.system()
    if system_os == 'Windows':
        env_property_file = "windows.properties"
    elif system_os == 'Linux':
        env_property_file = "ubuntu.properties"
    else:
        env_property_file = "windows.properties"
    print(f"Detected OS: {system_os}. Using {env_property_file} for Allure metadata.")

    # --- Step 3: Prepare Allure Metadata ---
    print("\n--- Step 3: Preparing Allure Metadata ---")

    metadata_files = [
        (env_property_file, "environment.properties"),
        ("categories.json", "categories.json"),
    ]

    for src_name, dest_name in metadata_files:
        src_path = os.path.join(SUPPORTS_DIR, src_name)
        dest_path = os.path.join(ALLURE_RESULTS_DIR, dest_name)
        try:
            shutil.copy2(src_path, dest_path)
            print(f"  Copied: {src_name} → {dest_name}")
        except FileNotFoundError:
            print(f"  Warning: Allure metadata file not found: {src_name}. Skipping.")

    # --- 3b. Dynamically create executor.json (so Allure always recognizes it) ---
    print("  Generating dynamic executor.json for Netlify...")

    try:
        git_branch = subprocess.getoutput("git rev-parse --abbrev-ref HEAD")
        git_commit = subprocess.getoutput("git rev-parse --short HEAD")

        executor_data = {
            "name": "Robotics BDD Framework Runner (Netlify)",
            "type": "CI_Pipeline",
            "url": "https://<your-netlify-site>.netlify.app/",
            "buildOrder": build_number,
            "buildName": f"Robotics BDD Build #{build_number}",
            "buildUrl": f"https://<your-netlify-site>.netlify.app/reports/{build_number}/index.html",
            "reportUrl": f"https://<your-netlify-site>.netlify.app/reports/latest/index.html",
            "data": {
                "Validation Engineer": os.getenv("GIT_AUTHOR_NAME", "Automation System"),
                "Product Model": "BDD-Sim-PyBullet",
                "Test Framework": "Gherkin (Behave)",
                "Git Branch": git_branch,
                "Git Commit": git_commit,
                "OS": platform.system(),
                "Python": platform.python_version(),
                "Docker Image": IMAGE_NAME
            }
        }

        dest_executor_path = os.path.join(ALLURE_RESULTS_DIR, "executor.json")
        with open(dest_executor_path, "w", encoding="utf-8") as f:
            json.dump(executor_data, f, indent=2)
        print(f"  ✅ Created executor.json at {dest_executor_path}")

    except Exception as e:
        print(f"  ⚠️  Failed to generate executor.json: {e}")

    # --- Step 4: Running Docker Tests ---
    print("\n--- Step 4: Running Docker Tests ---")
    docker_test_command = [
        "docker", "run", "--rm",
        "-v", f"{ALLURE_RESULTS_DIR}:/app/allure-results",
        IMAGE_NAME,
        "pytest",
        "--alluredir=allure-results",
        "-m", "navigation",
        "--ignore=features/manual_tests"
    ]
    execute_command(docker_test_command, "Docker Test Run")
    time.sleep(1)

    # --- Step 5: Allure Report Generation (via Docker) ---
    print("\n--- Step 5: Allure Report Generation (via Docker) ---")
    allure_report_output = os.path.join(REPORTS_DIR, "allure-report")
    os.makedirs(allure_report_output, exist_ok=True)
    ALLURE_BASE_URL_FOR_NETLIFY = NETLIFY_REPORT_PATH

    docker_allure_command = [
        "docker", "run", "--rm",
        "-v", f"{ALLURE_RESULTS_DIR}:/app/allure-results",
        "-v", f"{allure_report_output}:/app/allure-report",
        "-e", f"ALLURE_ENVIRONMENT_BASEURL={ALLURE_BASE_URL_FOR_NETLIFY}",
        IMAGE_NAME,
        "allure", "generate", "allure-results", "-o", "allure-report", "--clean"
    ]
    execute_command(docker_allure_command, "Allure Report Generation (via Docker)")

    # --- Step 6: Executing Report Deployment Workflow ---
    print("\n--- Step 6: Executing Report Deployment Workflow ---")
    deployment_command = [
        sys.executable,
        os.path.join(SUPPORTS_DIR, "deployment_workflow.py"),
        build_number,
        PROJECT_ROOT
    ]
    execute_command(deployment_command, "Report Deployment Workflow")

    # --- Step 7: Create Netlify Redirects File ---
    print("\n--- Step 7: Creating Netlify Redirects File ---")
    redirect_path = os.path.join(PROJECT_ROOT, "_redirects")

    try:
        with open(redirect_path, 'w') as f:
            f.write("/reports/:build/* /reports/:build/index.html 200\n")
            f.write(f"{NETLIFY_REPORT_PATH}/* {NETLIFY_REPORT_PATH}/index.html 200\n")
        print(f"  Created/Updated Netlify rewrite rule in '{os.path.basename(redirect_path)}'.")
        print("  Added dynamic rules for Allure Report SPA support.")
    except Exception as e:
        print(f"  CRITICAL ERROR creating _redirects file: {e}")
        sys.exit(1)

    # --- Step 8: Git Commit and Push ---
    git_commit_and_push(build_number)
    print("\n--- Workflow Complete ---")


if __name__ == '__main__':
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    os.chdir(PROJECT_ROOT)

    try:
        main()
    except Exception as e:
        print(f"\n==========================================================")
        print(f"FATAL UNHANDLED ERROR in main execution: {type(e).__name__}: {e}")
        print(f"==========================================================")
        sys.exit(1)
