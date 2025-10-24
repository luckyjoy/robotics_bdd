import os
import sys
import shutil
import subprocess
import time
import platform
import json
import psutil
import signal # <-- Import the signal module

# FILENAME: run_docker.py
# NOTE: Orchestrates the local Robotics BDD workflow (cleanup → Docker → Allure Local Report)

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGE_NAME = "luckyjoy/robotics-bdd-local:latest"

# Local Allure Reporting Constants
# Directory where Docker will output raw results for the CURRENT build
ALLURE_RESULTS_DIR = os.path.join(PROJECT_ROOT, "allure-results") 
# Directory where the final HTML report will be generated
ALLURE_REPORT_DIR = os.path.join(PROJECT_ROOT, "allure-report")

# Deprecated/Removed Constants (Used for Netlify/Deployment)
SUPPORTS_DIR = os.path.join(PROJECT_ROOT, "supports")


def execute_command(command, error_message, stream_output=False, exit_on_error=True):
    """
    Executes a shell command and checks for errors.

    If exit_on_error is True (default), the script exits on any non-zero return code.
    If exit_on_error is False (used for test run), returns the exit code.
    """
    print(f"\n--- Executing: {' '.join(command)} ---")
    
    # Check for start_new_session flag if stream_output is True (used in main)
    start_new_session_flag = 'start_new_session' in command
    
    # Remove the custom flag before execution
    if start_new_session_flag:
        command.remove('start_new_session')

    if not stream_output:
        # Synchronous execution for most commands
        try:
            # check=True is temporarily set to catch errors as exceptions
            result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
            print("--- STDOUT ---")
            print(result.stdout)
            if result.stderr:
                print("--- STDERR (Warnings/Notices) ---")
                print(result.stderr)
            # Command succeeded (Exit Code 0)
            return 0 
        except subprocess.CalledProcessError as e:
            # An error occurred (non-zero exit code)
            print("--- STDOUT (Error Context) ---")
            print(e.stdout)
            print("--- STDERR (Error Context) ---")
            print(e.stderr)
            
            if exit_on_error:
                # Fatal environment/setup error (FAIL). Exit.
                print(f"\n==========================================================")
                print(f"CRITICAL ERROR running {error_message}: {e.stderr.strip()}")
                print(f"==========================================================")
                sys.exit(e.returncode)
            else:
                # Test run failure (UNSTABLE). Return the test failure code.
                return e.returncode
        except FileNotFoundError:
            print(f"\n==========================================================")
            print(f"CRITICAL ERROR: Command not found. Ensure Docker, Python, and other tools are in your PATH.")
            print(f"==========================================================")
            sys.exit(1)
    else:
        # Asynchronous streaming execution (used for Docker Build)
        print("--- STDOUT (Streaming) ---")
        process = None 
        
        # Set up Popen arguments for signal handling on Unix
        popen_kwargs = {
            'stdout': subprocess.PIPE, 
            'stderr': subprocess.STDOUT, 
            'text': True, 
            'encoding': "utf-8", 
            'bufsize': 1
        }
        if platform.system() != "Windows" and start_new_session_flag:
            # This is essential for os.killpg() to work
            popen_kwargs['start_new_session'] = True
        
        try:
            process = subprocess.Popen(command, **popen_kwargs)
            
            # Read output line-by-line in real-time
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    print(line.strip())

            return_code = process.wait()
            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, command, output=None, stderr=f"Command failed with exit code {return_code}")
            return 0
                
        except KeyboardInterrupt:
            if process and process.poll() is None:
                print("\n[INFO] Ctrl+C detected. Attempting to terminate child process...")
                try:
                    if platform.system() == "Windows":
                        # On Windows, terminate() is usually sufficient
                        process.terminate()
                    elif platform.system() != "Windows" and start_new_session_flag:
                        # On Unix, use os.killpg to kill the entire process group
                        os.killpg(os.getpgid(process.pid), signal.SIGINT)
                    else:
                        # Fallback for non-session-separated processes
                        process.terminate()
                        
                    # Give it a moment to terminate
                    time.sleep(1)
                    if process.poll() is None:
                        process.kill() # Hard kill if still running
                        
                except Exception as e:
                    print(f"[CRITICAL] Failed to terminate/kill child process: {e}")
            
            # Exit the Python script
            sys.exit(1) 
            
        except subprocess.CalledProcessError as e:
            print(f"\n==========================================================")
            print(f"CRITICAL ERROR running {error_message}: Command failed. Check streamed output above.")
            print(f"==========================================================")
            sys.exit(e.returncode)
        except FileNotFoundError:
            print(f"\n==========================================================")
            print(f"CRITICAL ERROR: Command not found. Ensure Docker, Python, and other tools are in your PATH.")
            print(f"==========================================================")
            sys.exit(1)


def check_if_image_exists(image_name):
    """Checks if a Docker image is locally present."""
    print(f"\n--- Step 2: Docker Image Check for {image_name} ---")
    
    try:
        result = subprocess.run(
            ["docker", "images", image_name, "--format", "{{.Repository}}:{{.Tag}}"], 
            check=True, 
            capture_output=True, 
            text=True, 
            encoding="utf-8"
        )
        
        if result.stdout.strip() == image_name:
            print(f"✅ Docker image '{image_name}' found locally.")
            return True
        else:
            print(f"❌ Docker image '{image_name}' not found locally.")
            return False
            
    except subprocess.CalledProcessError:
        print(f"❌ Error running 'docker images' command. Assuming image is missing.")
        return False
    except FileNotFoundError:
        print("❌ Docker executable not found.")
        sys.exit(1)


def check_docker_running():
    """Ensures Docker daemon is running before proceeding."""
    print("\n--- Checking Docker Daemon Status ---")

    def is_docker_responsive():
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except Exception:
            return False

    if is_docker_responsive():
        print("✅ Docker is running and responsive.")
        return

    system_os = platform.system()
    if system_os == "Windows":
        print("⚠️  Docker daemon not detected. Attempting to start Docker Desktop...")

        docker_exe = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if not os.path.exists(docker_exe):
            print(f"❌ Docker Desktop not found at: {docker_exe}")
            print("Please start Docker Desktop manually, then re-run this script.")
            sys.exit(1)

        already_running = any("Docker Desktop.exe" in (p.name() or "") for p in psutil.process_iter())
        if not already_running:
            try:
                subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("🚀 Starting Docker Desktop...")
            except Exception as e:
                print(f"❌ Failed to launch Docker Desktop: {e}")
                sys.exit(1)

        for i in range(30):
            if is_docker_responsive():
                print("✅ Docker daemon is now active.")
                return
            print(f"  ⏳ Waiting for Docker to start... ({i+1}/30)")
            time.sleep(4)

        print("❌ Docker did not start within expected time (≈2 min). Please start it manually.")
        sys.exit(1)

    else:
        print("❌ Docker daemon not detected. Please start the Docker service manually.")
        print("Try: sudo systemctl start docker")
        sys.exit(1)


# --- Allure Reporting Functions (Local Only) ---

def generate_allure_report():
    """Generates the Allure HTML report."""
    print("\n--- Step 5: Generating Allure Report ---")
    allure_bin = shutil.which("allure") or shutil.which("allure.cmd")
    if not allure_bin:
        print("[CRITICAL] Allure CLI not found. Install it via Scoop, npm, or download manually.")
        return
        
    try:
        subprocess.run([allure_bin, "generate", ALLURE_RESULTS_DIR, "-o", ALLURE_REPORT_DIR, "--clean"], check=True)
        print(f"✅ Report generated to {ALLURE_REPORT_DIR}")
        
    except subprocess.CalledProcessError as e:
        print(f"[CRITICAL] Failed to generate Allure report: {e}")


def open_allure_report():
    """Opens the generated Allure report in the default browser."""
    print("\n--- Step 6: Opening Allure Report ---")
    allure_bin = shutil.which("allure") or shutil.which("allure.cmd")
    if allure_bin:
        try:
            subprocess.Popen([allure_bin, "open", ALLURE_REPORT_DIR])
            print(f"🚀 Attempting to open report in default browser: {ALLURE_REPORT_DIR}/index.html")
        except Exception as e:
             print(f"[WARN] Failed to open Allure report: {e}")


# --- Main Execution Flow ---

def main():
    """Main workflow runner."""
    # --- Input Parsing ---
    if len(sys.argv) < 2:
        print("Error: Missing Build Number argument.")
        print("Usage: python run_docker.py <BUILD_NUMBER> [SUITE]")
        sys.exit(1)

    build_number = sys.argv[1].strip()
    test_suite = sys.argv[2].strip() if len(sys.argv) >= 3 else "navigation"

    print("==========================================================")
    print(f"Running Robotics BDD Test Workflow for Build #{build_number}")
    print(f"Target Test Suite: {test_suite}")
    print("==========================================================")

    # --- Step 0: Check Docker Daemon ---
    check_docker_running()

    # --- Step 1: Prepare Workspace and History ---
    print("\n--- Step 1: Prepare Workspace and History ---")
    
    LATEST_HISTORY_SOURCE = os.path.join(ALLURE_REPORT_DIR, "history")
    HISTORY_DESTINATION = os.path.join(ALLURE_RESULTS_DIR, "history")

    print("1a. Cleaning up old raw results (allure-results, __pycache__, .pytest_cache)")
    shutil.rmtree(ALLURE_RESULTS_DIR, ignore_errors=True)
    shutil.rmtree(os.path.join(PROJECT_ROOT, "__pycache__"), ignore_errors=True)
    shutil.rmtree(os.path.join(PROJECT_ROOT, ".pytest_cache"), ignore_errors=True)

    os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)

    if os.path.exists(LATEST_HISTORY_SOURCE):
        print(f"1b. Copying previous history from '{os.path.basename(LATEST_HISTORY_SOURCE)}' to '{os.path.basename(ALLURE_RESULTS_DIR)}'")
        try:
            shutil.copytree(LATEST_HISTORY_SOURCE, HISTORY_DESTINATION, dirs_exist_ok=True)
        except Exception as e:
            print(f"  Warning: Failed to copy history folder. Trend data might be missing. Error: {e}")
    else:
        print("1b. Previous report history not found. The first run will not show trend data.")

    print("Cleanup and history preparation complete.")

    # --- Step 2 & 2.5: Docker Image Check and Conditional Build ---
    if not check_if_image_exists(IMAGE_NAME):
        print("\n--- Step 2.5: Build Docker Image ---")
        
        docker_build_command = ["docker", "build", "-t", IMAGE_NAME, "."]
        
        # Add a custom flag to tell execute_command to start a new session (for Unix signal handling)
        if platform.system() != "Windows":
             docker_build_command.append("start_new_session")
             
        execute_command(docker_build_command, "Docker Image Build", stream_output=True)
    else:
        print("\n--- Step 2.5: Build Docker Image ---")
        print(f"✅ Skipping Docker build: Image '{IMAGE_NAME}' already exists.")


    # --- Step 3: Preparing Allure Metadata ---
    print("\n--- Step 3: Preparing Allure Metadata ---")

    system_os = platform.system()
    env_property_file = "windows.properties" if system_os == 'Windows' else "ubuntu.properties"
    print(f"Detected OS: {system_os}. Using {env_property_file} for Allure metadata.")

    # Copy environment and categories files
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

    # Generating dynamic executor.json
    print("  Generating dynamic executor.json...")
    try:
        executor_data = {
            "name": "Local Robotics BDD Runner",
            "type": "Local_Execution",
            "buildOrder": build_number,
            "buildName": f"Local Run #{build_number}",
            "data": {
                "Test Framework": "Gherkin (Behave) / Pytest",
                "OS": platform.system(),
                "Python": platform.python_version(),
                "Docker Image": IMAGE_NAME
            }
        }

        dest_executor_path = os.path.join(ALLURE_RESULTS_DIR, "executor.json")
        with open(dest_executor_path, "w", encoding="utf-8") as f:
            json.dump(executor_data, f, indent=2)
        print(f"  ✅ Created executor.json at {os.path.basename(ALLURE_RESULTS_DIR)}/executor.json")
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
        "-m", test_suite,
        "--ignore=features/manual_tests"
    ]
    
    # Run command, but DO NOT exit on test failure (Exit Code 1)
    test_exit_code = execute_command(docker_test_command, "Docker Test Run", exit_on_error=False)

    # --- Apply PASS/FAIL/UNSTABLE Policy ---
    if test_exit_code is None:
        print(f"\n==========================================================")
        print(f"❌ FAIL POLICY: Test execution failed to return a status.")
        print(f"Stopping Allure report generation.")
        print(f"==========================================================")
        sys.exit(1)
    elif test_exit_code >= 2:
        # Pytest environment/usage error (Exit Code 2 or higher)
        print(f"\n==========================================================")
        print(f"❌ FAIL POLICY: Docker Test Run encountered a critical error (Exit Code {test_exit_code}).")
        print(f"Stopping Allure report generation.")
        print(f"==========================================================")
        sys.exit(test_exit_code)
    elif test_exit_code == 0:
        print("✅ PASS POLICY: All tests succeeded. Proceeding to Allure report.")
    elif test_exit_code == 1:
        print("⚠️ UNSTABLE POLICY: One or more tests failed. Proceeding to Allure report.")
        
    time.sleep(1)

    # --- Step 5: Allure Report Generation ---
    generate_allure_report()

    # --- Step 6: Open Allure Report ---
    open_allure_report()

    print("\n--- Workflow Complete ---")


if __name__ == '__main__':
    # On Unix-like systems, set the process group ID for the script itself 
    # to facilitate proper signal handling (os.killpg in execute_command).
    # NOTE: This is less critical now that start_new_session is used in execute_command, 
    # but still good practice for general signal robustness.
    if platform.system() != "Windows":
        try:
            os.setpgrp()
        except Exception:
            pass 
            
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    os.chdir(PROJECT_ROOT)
    try:
        main()
    except Exception as e:
        print(f"\n==========================================================")
        print(f"FATAL UNHANDLED ERROR in main execution: {type(e).__name__}: {e}")
        print(f"==========================================================")
        sys.exit(1)