import sys
import subprocess
import os
import argparse
import platform
import shutil
import json
import time
import webbrowser
import re 

# Constants
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

DOCKER_USER = os.getenv('DOCKER_USER')

# --- Start Explicit Error Handling for DOCKER_USER ---
if not DOCKER_USER:
    print("\n==========================================================")
    print("CRITICAL ENVIRONMENT ERROR: DOCKER_USER is not set.")
    print("The pipeline requires the 'DOCKER_USER' environment variable ")
    print("to be configured (e.g., in k8_pipeline.bat) to correctly tag and push images.")
    print("==========================================================")
    sys.exit(1)
# --- End Explicit Error Handling for DOCKER_USER ---


# Note: LOCAL_IMAGE_TAG is built dynamically using DOCKER_USER
LOCAL_IMAGE_TAG = f"{DOCKER_USER}/robotics-bdd-local:latest"
REPORT_IMAGE_TAG = f"{DOCKER_USER}/robotics-bdd-report" 
IMAGE_ID_FILE = "python_image_id.tmp"

ALLURE_RESULTS_DIR = os.path.join(PROJECT_ROOT, "allure-results")
ALLURE_REPORT_DIR = os.path.join(PROJECT_ROOT, "allure-report")
SUPPORTS_DIR = os.path.join(PROJECT_ROOT, "supports")

# Regex to capture the step progress: [CurrentStep/TotalSteps] (for build status)
STEP_PROGRESS_RE = re.compile(r'\[(\d+)/(\d+)]')
# Regex to capture the step description (e.g., RUN apt-get install)
STEP_DESC_RE = re.compile(r'-> BUILD INFO: #\d+ \[.*] (.*)')
# Regex for docker push/pull progress
DOCKER_PUSH_PROGRESS_RE = re.compile(r'([\da-f]+): (Waiting|Downloading|Extracting|Pushing|Pushed|Mounted|Layer already exists)\s+(?:\[.*]\s*(\d+)%)?')


def execute_command(command, error_message, check_output=False, exit_on_error=True, docker_build_status=False, docker_push_status=False):
    """
    Executes a shell command and handles errors, with streaming status for Docker operations.
    """
    if docker_build_status or docker_push_status:
        # Determine the initial status message based on the type of operation
        if docker_build_status:
            image_name = command.split(' ')[2].split(':')[0]
            print(f"Starting Docker Build with Live Status: {image_name}")
        elif docker_push_status:
            # This is handled dynamically in publish_image_tags now, so we just pass
            # The initial print is done before calling this function
            pass
            
        p = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            universal_newlines=True,
            bufsize=1 
        )
        
        current_step = 0
        total_steps = 0
        step_description = "Initializing..."
        layer_statuses = {} 
        return_code = None
        
        for line in iter(p.stdout.readline, ''):
            
            if docker_build_status:
                match_progress = STEP_PROGRESS_RE.search(line)
                match_desc = STEP_DESC_RE.search(line)

                if match_progress:
                    current_step = int(match_progress.group(1))
                    total_steps = int(match_progress.group(2))
                    
                    if match_desc:
                        step_description = match_desc.group(1).split('\n')[0].strip()
                        if step_description.startswith('FROM'):
                             step_description = f"FROM {step_description.split(':')[1].strip()}"
                        elif len(step_description) > 50:
                             step_description = step_description[:50] + "..."

                if total_steps > 0:
                    progress_percent = int((current_step / total_steps) * 100)
                    status_line = (
                        f"  [Docker Build Status] Step {current_step}/{total_steps} ({progress_percent}%) | "
                        f"Task: {step_description:<50} | "
                        f"{time.strftime('%H:%M:%S')} \r"
                    )
                    sys.stdout.write(status_line)
                    sys.stdout.flush()

            elif docker_push_status:
                match_push_progress = DOCKER_PUSH_PROGRESS_RE.search(line)
                
                if match_push_progress:
                    layer_id = match_push_progress.group(1)
                    status = match_push_progress.group(2)
                    percent_str = match_push_progress.group(3)
                    percent = int(percent_str) if percent_str else (100 if status in ('Pushed', 'Layer already exists', 'Mounted') else 0)
                    
                    layer_statuses[layer_id] = percent
                    
                    total_layers = len(layer_statuses)
                    if total_layers > 0:
                        active_layers = [p for p in layer_statuses.values() if p < 100]
                        completed_layers = [p for p in layer_statuses.values() if p == 100]
                        
                        total_units_possible = total_layers * 100
                        total_units_achieved = sum(layer_statuses.values())
                        
                        overall_percent = int((total_units_achieved / total_units_possible) * 100)
                        
                        status_line = (
                            f"  [Docker Push Status] Total Progress: {overall_percent}% "
                            f"| Layers: {len(active_layers)} active / {total_layers} total | "
                            f"{time.strftime('%H:%M:%S')} \r"
                        )
                        sys.stdout.write(status_line)
                        sys.stdout.flush()


            if "ERROR" in line.upper() or "FATAL" in line.upper() or "STEP COMPLETE:" in line or "Login Succeeded" in line:
                 sys.stdout.write(" " * 120 + "\r")
                 print(line.strip())
                 if docker_build_status and total_steps > 0 and return_code is None:
                    sys.stdout.write(status_line)
                    sys.stdout.flush()


        p.stdout.close()
        return_code = p.wait()

        sys.stdout.write(" " * 120 + "\r")
        sys.stdout.flush()

        if return_code != 0:
            print("\n==========================================================")
            print(f"FATAL UNHANDLED ERROR during Docker process: {error_message}")
            print(f"Command failed: {command}")
            print("==========================================================")
            if exit_on_error:
                sys.exit(return_code)
            return return_code
        
        if docker_build_status:
            print(f"✅ Docker build completed successfully: {LOCAL_IMAGE_TAG}")
        elif docker_push_status:
            pass # Handled in publish_image_tags
            
        return 0
    else:
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                universal_newlines=True,
            )
            output = result.stdout.strip()
            if check_output:
                return output
            print(output)
            return 0
        except subprocess.CalledProcessError as e:
            print("\n==========================================================")
            print(f"FATAL UNHANDLED ERROR during command execution: {error_message}")
            print(f"Command failed: {command}")
            print("----------------------------------------------------------")
            print(f"Output:\n{e.stdout}")
            print("==========================================================")
            if exit_on_error:
                sys.exit(1)
            return 1

def docker_image_exists(image_tag):
    """Checks if a Docker image with the given tag exists locally."""
    print(f"Checking for local image: {image_tag}")
    try:
        subprocess.run(
            f"docker image inspect {image_tag}",
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

def check_dependencies():
    """Verifies that essential command-line tools are installed."""
    print("--- Step 1: Checking Dependencies ---\n")
    dependencies = ["docker", "pytest", "allure"]
    missing = []
    
    for dep in dependencies:
        if shutil.which(dep) is None:
            missing.append(dep)
            
    if missing:
        print("FATAL ERROR: The following dependencies are missing:")
        for dep in missing:
            print(f"- {dep}")
        print("\nPlease install the missing dependencies (e.g., Docker, pytest, 'allure-commandline').")
        sys.exit(1)
        
    print("✅ All dependencies found (docker, pytest, allure).")
    return 0

def run_tests(suite_marker):
    """Runs the Tests inside the Docker container."""
    print(f"\n--- Step 4: Running Tests (Suite: {suite_marker}) ---")
    
    if os.path.exists(ALLURE_RESULTS_DIR):
        shutil.rmtree(ALLURE_RESULTS_DIR)
        
    os.makedirs(ALLURE_RESULTS_DIR)
    
    # FIX: Use the literal container path for --alluredir
    CONTAINER_ALLURE_RESULTS_DIR = "/app/allure-results" 
    
    # The actual Docker run command
    docker_run_command = (
        f"docker run --rm "
        f"-v \"{ALLURE_RESULTS_DIR}\":{CONTAINER_ALLURE_RESULTS_DIR} "
        f"-v \"{SUPPORTS_DIR}\":/app/supports "
        f"{LOCAL_IMAGE_TAG} "
        f"pytest -m {suite_marker} --ignore=features/manual_tests --alluredir={CONTAINER_ALLURE_RESULTS_DIR}"
    )
    
    print(f"Executing: {docker_run_command}")
    execute_command(
        docker_run_command, 
        "Test execution failed. Check test logs above."
    )
    print("✅ Tests completed and results saved to allure-results.")

def generate_report(build_number, suite_marker):
    """Generates the Allure HTML report, adds metadata, and packages it into a Docker image."""
    print("\n--- Step 5: Generating Allure Report and Packaging ---")

    DOCKER_HUB_USER_FOR_LINKS = f"{DOCKER_USER}"
    REPORT_REPO_BASE_URL = f"https://hub.docker.com/r/{DOCKER_HUB_USER_FOR_LINKS}/robotics-bdd-report"
    
    # 5.1. Creating Allure executor.json for build metadata
    print("  5.1. Creating Allure executor.json for build metadata...")
    try:
        executor_data = {
            "name": "Robotics BDD Pipeline Runner",
            "type": "Local_Execution",
            "url": f"{REPORT_REPO_BASE_URL}/tags",
            "reportUrl": f"{REPORT_REPO_BASE_URL}/tags?build={build_number}",
            "buildName": f"Build #{build_number} ({suite_marker.upper()} suite)",
            "buildUrl": f"{REPORT_REPO_BASE_URL}/tags?build={build_number}",
            "buildOrder": int(build_number)  
        }
        with open(os.path.join(ALLURE_RESULTS_DIR, "executor.json"), "w") as f:
            json.dump(executor_data, f, indent=4)
        print(f"  ✅ executor.json created for Build #{build_number}.")
    except ValueError:
        print("⚠️ WARNING: Could not set buildOrder. Ensure build_number is a numeric string.")
    except Exception as e:
        print(f"⚠️ WARNING: Failed to create executor.json: {e}")

    # 5.2. Create environment.properties for report title and environment section
    print("  5.2. Creating Allure environment.properties for report details...")
    try:
        environment_data = [
            f"Report Title=Robotics BDD: {suite_marker.upper()} Suite Run #{build_number}",
            f"Docker User={DOCKER_USER}",
            f"Platform={platform.system()} {platform.release()}",
            f"Test Suite Marker={suite_marker}"
        ]
        with open(os.path.join(ALLURE_RESULTS_DIR, "environment.properties"), "w") as f:
            f.write('\n'.join(environment_data) + '\n')
        print("  ✅ environment.properties created.")
    except Exception as e:
        print(f"⚠️ WARNING: Failed to create environment.properties: {e}")

    # 5.3. History setup and report generation
    history_source = os.path.join(ALLURE_REPORT_DIR, "history")
    history_destination = os.path.join(ALLURE_RESULTS_DIR, "history")
    if os.path.exists(history_source):
        try:
            shutil.copytree(history_source, history_destination)
            print("  ✅ Copied previous report history.")
        except Exception as e:
            print(f"⚠️ WARNING: Could not copy history files: {e}")
    else:
        print("  ℹ️ Previous report history not found. Starting new history.")

    if os.path.exists(ALLURE_REPORT_DIR):
        shutil.rmtree(ALLURE_REPORT_DIR)
    
    allure_generate_command = f"allure generate {ALLURE_RESULTS_DIR} --clean -o {ALLURE_REPORT_DIR}"
    execute_command(
        allure_generate_command, 
        "Allure report generation failed."
    )
    print("✅ Allure HTML report generated.")


    # --- 5.4. Package Report into Docker Image ---
    print("\n  5.4. Packaging Allure Report into a Deployable Docker Image")
    
    REPORT_TAG = f"{REPORT_IMAGE_TAG}:{build_number}"
    REPORT_LATEST_TAG = f"{REPORT_IMAGE_TAG}:latest"
    
    report_dockerfile_content = f"""
# Use a minimal web server image (e.g., nginx-alpine)
FROM nginx:alpine
# Copy the generated report into the Nginx web root
COPY {os.path.basename(ALLURE_REPORT_DIR)} /usr/share/nginx/html
# Nginx serves content on port 80 by default
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""
    dockerfile_path = os.path.join(PROJECT_ROOT, "Dockerfile.report")
    with open(dockerfile_path, "w") as f:
        f.write(report_dockerfile_content)
        
    print(f"  Dockerfile.report created for tag {REPORT_TAG}.")
    
    # *** Dynamic status for report build ***
    docker_build_report_command = f"docker build -t {REPORT_TAG} -f {dockerfile_path} ."
    execute_command(
        docker_build_report_command, 
        f"Failed to build report Docker image {REPORT_TAG}",
        docker_build_status=True
    )
    
    docker_tag_command = f"docker tag {REPORT_TAG} {REPORT_LATEST_TAG}"
    execute_command(
        docker_tag_command,
        f"Failed to tag image {REPORT_TAG} as {REPORT_LATEST_TAG}"
    )
    
    print(f"  ✅ Report image tagged as {REPORT_TAG} and {REPORT_LATEST_TAG}.")
    
    return REPORT_TAG, REPORT_LATEST_TAG


def get_docker_hub_url(tag):
    """Generates the Docker Hub URL for an image tag."""
    parts = tag.split('/')
    if len(parts) < 2:
        return None # Not a standard user/repo format
    
    repo = parts[-1].split(':')[0]
    user = parts[-2]
    
    return f"https://hub.docker.com/r/{user}/{repo}/tags"

def publish_image_tags(image_tag_list, error_artifact_name):
    """Handles Docker login and pushes a list of image tags to Docker Hub."""
    print(f"\n--- Publishing {error_artifact_name} to Docker Hub (if credentials exist) ---")
    
    docker_user = os.getenv("DOCKER_USER")
    docker_pass = os.getenv("DOCKER_PASS")
    
    if not (docker_user and docker_pass):
        print("⚠️ Docker credentials not found.")
        print("   Please set environment variables DOCKER_USER and DOCKER_PASS if publishing is required.")
        print("   Skipping Docker Hub push.")
        return

    print("Logging in to Docker Hub...")
    login_result = execute_command(
        f"echo {docker_pass} | docker login -u {docker_user} --password-stdin",
        "Docker login failed.",
        exit_on_error=False
    )
    if login_result != 0:
        return # Stop if login failed
    
    all_successful = True
    for tag in image_tag_list:
        repo_url = get_docker_hub_url(tag)
        
        # *** FIX: Updated status message to show the actual tag and the URL ***
        print(f"--- Pushing tag: {tag} to {repo_url} ---")
        
        push_command = f"docker push {tag}"
        push_result = execute_command(
            push_command, 
            f"Failed to push {tag}. Check connection and image existence.",
            docker_push_status=True,
            exit_on_error=False # Allow pipeline to continue if one push fails
        )
        if push_result != 0:
            all_successful = False
        else:
            print(f"✅ Push of {tag} completed.") # Final confirmation for the push

    if all_successful:
        print(f"✅ All tags for {error_artifact_name} published successfully.")
    else:
        print(f"⚠️ Warning: One or more tags for {error_artifact_name} failed to publish.")


def open_report():
    """Opens the Allure report index.html in the default web browser."""
    print("\n--- Step 7: Opening Allure Report Locally ---")
    index_file = os.path.join(ALLURE_REPORT_DIR, "index.html")
    allure_bin = shutil.which("allure") or shutil.which("allure.cmd")
    if allure_bin:
        try:
            # Use 'allure open' which handles local server startup
            subprocess.Popen([allure_bin, "open", ALLURE_REPORT_DIR])
            print(f"🚀 Opening via Allure CLI at: {index_file}")
        except Exception as e:
            print(f"⚠️ CLI open failed: {e}")
            webbrowser.open_new_tab(index_file)
            print(f"🚀 Opening directly in browser at: {index_file}")
    else:
        webbrowser.open_new_tab(index_file)
        print(f"🚀 Opening directly in browser at: {index_file}")
        
    
def full_pipeline(build_number, suite_marker):
    """Runs the full pipeline."""
    check_dependencies()
    
    # --- Step 2: Build Main Docker Image (with skip logic) ---
    print("\n--- Step 2: Building Main Docker Image ---\n")
    if docker_image_exists(LOCAL_IMAGE_TAG):
        print(f"Image {LOCAL_IMAGE_TAG} already exists locally. Skipping build.")
        # Re-tag if it exists, to ensure 'latest' is correct
        docker_tag_command = f"docker tag {LOCAL_IMAGE_TAG} {LOCAL_IMAGE_TAG}"
        execute_command(docker_tag_command, "Failed to re-tag existing image.")
    else:
        DOCKER_BUILD_COMMAND = f"docker build -t {LOCAL_IMAGE_TAG} ."
        print("Local image not found. Starting build...")
        execute_command(
            DOCKER_BUILD_COMMAND, 
            f"Failed to build Docker image {LOCAL_IMAGE_TAG}",
            docker_build_status=True
        )

    # --- Step 3: Publish Main Image ---
    publish_image_tags([LOCAL_IMAGE_TAG], "Main Image")

    # --- Step 4: Run Tests ---
    run_tests(suite_marker)

    # --- Step 5: Generate and Package Report ---
    REPORT_VERSION_TAG, REPORT_LATEST_TAG = generate_report(build_number, suite_marker)

    # --- Step 6: Publish Report Image ---
    publish_image_tags([REPORT_VERSION_TAG, REPORT_LATEST_TAG], "Allure Report Image")

    # --- Step 7: Open Report ---
    open_report()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_kubernestes.py <BUILD_NUMBER> [SUITE_MARKER]")
        sys.exit(1)

    build_number = sys.argv[1]
    suite_marker = sys.argv[2] if len(sys.argv) > 2 else "all"

    print(f"=======================================================")
    print(f"STARTING ORCHESTRATION PIPELINE")
    print(f"Build Number: {build_number}")
    print(f"Test Suite:   {suite_marker}")
    print(f"=======================================================")
    
    full_pipeline(build_number, suite_marker)