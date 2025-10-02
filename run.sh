#!/bin/bash
#
# === Robotics BDD Test Runner and Allure Report Generator ===
#
# This script executes BDD tests, generates an Allure report, and
# intelligently copies the correct environment properties file
# (windows.properties or linux.properties) based on the host OS.
#
# IMPORTANT: Uses 'py -3 -m' for Windows (Git Bash/Mintty) to ensure
# the Python interpreter is found via the Python Launcher (py.exe).
#
# Author: Bang Thien Nguyen, ontario1998@gmail.com
#

# ====================================================================
# WINDOWS USER CONFIGURATION (Paths for Git Bash/Mintty)
#
# NOTE: These paths are only used if the script detects a Windows OS.
# They are kept here for easy modification, but are applied conditionally.
# Use forward slashes (/) and '/c/' for the C: drive.
# ====================================================================

# 1. Allure Command Line Tool path (if 'allure' command is not found):
ALLURE_BIN_PATH_WIN="/c/Users/ontar/scoop/shims"

# 2. Java Home path (REQUIRED if "JAVA_HOME is not set" error occurs):
JAVA_HOME_WIN="/c/Program Files/Java/jdk-21"

# --- Display Header ---
echo "Running Robotics BDD Simulation Tests..."
echo "Author: Bang Thien Nguyen, ontario1998@gmail.com"
echo ""

# --- Cleanup Previous Artifacts (including old results folder) ---
echo "Cleaning up previous test artifacts for a fresh run..."
# The 2>/dev/null suppresses "No such file or directory" errors if the folders don't exist.
rm -rf __pycache__ .pytest_cache allure-results 2>/dev/null
echo ""

# --- Determine OS and Python Command (Used for Pytest) ---

# First, determine the operating system
OS_TYPE=$(uname -o)

PYTHON_CMD="python" # Default fallback for Python

# Check if the OS type contains "Msys" (for Git Bash/MSYS2), "Cygwin", or "Windows"
if [[ "$OS_TYPE" =~ Msys|Cygwin|Windows ]]; then
    # On Windows/Mintty, try the Python Launcher (py) which is most reliable.
    if command -v py &> /dev/null; then
        PYTHON_CMD="py -3"
        echo "Using Windows Python Launcher: 'py -3'"
    else
        # If 'py' is not found, stick to 'python'
        echo "Windows environment detected, but 'py' launcher not found. Using 'python'."
    fi
else
    # On native Unix (Linux/macOS), check for python3 first, then python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        echo "Using native Python 3: 'python3'"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        echo "Using native Python: 'python'"
    else
        # Critical failure: no Python command found
        echo "Error: Neither 'python3' nor 'python' was found in PATH."
        exit 1
    fi
fi
echo ""

# --- Execute Tests ---
echo "Running pytest and collecting results into allure-results..."

# Execute pytest using the determined command
# This uses the python interpreter to run the pytest module (e.g., 'py -3 -m pytest')
$PYTHON_CMD -m pytest --alluredir=allure-results

# NOTE: The test failure check is removed here to ensure the Allure report is always generated.
echo ""

# --- Add Environment Properties to Results Folder (OS Detection relies on OS_TYPE above) ---
echo "Copying categories.json and environment properties based on OS into the report directory..."

# Check if the OS type contains "Msys" (for Git Bash/MSYS2), "Cygwin), or "Windows"
if [[ "$OS_TYPE" =~ Msys|Cygwin|Windows ]]; then
    # If it looks like a Windows-hosted Unix environment, use windows.properties
    ENV_FILE="supports/windows.properties"
    echo "Detected Windows-based environment ($OS_TYPE). Using $ENV_FILE."

    # Windows-specific PATH/HOME adjustment for Allure/Java
    if [[ -n "$ALLURE_BIN_PATH_WIN" ]]; then
        echo "Temporarily adding user-configured ALLURE_BIN_PATH to system PATH."
        # This prepends the user-defined path to the existing PATH for the duration of the script.
        export PATH="$ALLURE_BIN_PATH_WIN:$PATH"
    fi
    # Set JAVA_HOME if configured
    if [[ -n "$JAVA_HOME_WIN" ]]; then
        echo "Temporarily setting JAVA_HOME."
        export JAVA_HOME="$JAVA_HOME_WIN"
    fi
else
    # Otherwise, assume a native Linux or standard macOS environment
    ENV_FILE="supports/linux.properties"
    echo "Detected native Unix environment ($OS_TYPE). Using $ENV_FILE."
fi

# Check if allure-results directory was created by pytest
if [ ! -d "allure-results" ]; then
    echo "Error: allure-results directory was not created. Cannot generate report."
    exit 1
fi

# Copy the selected environment file and the categories.json file
cp "$ENV_FILE" allure-results/environment.properties
cp supports/categories.json allure-results/

echo ""

# --- Generate and Serve Report (Using the standalone 'allure' command) ---
echo "Attempting to generate and launch Allure Report..."

# We switch to the standalone 'allure' executable here, as 'python -m allure' fails.
if command -v allure &> /dev/null; then
    echo "Standalone 'allure' command found. Generating and serving report..."
    allure serve allure-results
else
    # Fallback/Helpful message for the user if the executable is missing.
    echo "--------------------------------------------------------"
    echo "ERROR: The standalone 'allure' command-line tool was not found in PATH."
    echo "Report data has been collected in the 'allure-results' directory."
    echo ""
    echo "To view the report, you must first install the Allure Command Line Tool"
    echo "AND ensure it is in your system's PATH."
    echo "--------------------------------------------------------"
fi

# --- Script End ---
echo "Allure report process finished."
