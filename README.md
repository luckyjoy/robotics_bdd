🤖 Robotics Behavior-Driven Development (BDD) Framework
A robust, BDD-driven framework for validating the functionality, path planning, and critical safety protocols of a simulated mobile manipulator robots.

Author: Bang Thien Nguyen | Contact: ontario1998@gmail.com

💡 Project Overview
This framework implements Behavior-Driven Development (BDD) using pytest-bdd to create a living documentation and validation layer for the robot's control logic. All requirements are documented as human-readable Gherkin scenarios (Given-When-Then), ensuring clear collaboration between technical and non-technical stakeholders.

Core Component

Technology

Role

Test Syntax

Gherkin (.feature files)

Defines test cases using unambiguous scenario descriptions.

Test Runner

pytest

Industry-standard Python testing tool.

BDD Integration

pytest-bdd

Maps Gherkin steps to executable Python code (step definitions).

Reporting

Allure & pytest-html

Generates professional, interactive HTML reports for test traceability.

🚀 Getting Started
Prerequisites
Docker Desktop (required for the containerized test runner)

Windows Command Prompt (to execute run_docker.bat)

(Optional for local development) Python 3.10+

(Optional for local development) Allure command-line tool

Installation
Clone the Repository:

git clone <your-repository-url>
cd robotics_bdd

Install Dependencies: (Only necessary if running tests without Docker)

pip install -r requirements.txt

🐳 Dockerized Execution (Recommended)
To ensure a clean, consistent testing environment that matches the CI/CD pipeline, use the provided Docker setup.

Docker Image (Dockerfile)
The image, tagged robotics-tdd-local:latest, is a complete, self-contained environment based on python:3.10-slim. It includes:

Java JRE 21 and the Allure Command Line tool for report generation.

All Python dependencies (pytest, allure-pytest, etc.) installed via requirements.txt.

The application code is copied into the /app working directory.

Running the Test Suite (run_docker.bat)
The run_docker.bat script is the primary entry point for testing and report generation on a local Windows machine. It handles the entire lifecycle:

Check Docker Status: Verifies Docker Desktop is running.

Clean Artifacts: Deletes previous allure-results and reports folders in your local project path (C:\my_work\robotics_bdd).

Build or Pull Image: If the robotics-tdd-local:latest image doesn't exist locally, it runs docker build --no-cache.

Execute Tests: Runs the Docker container, mounting the local allure-results directory to collect test output.

# Runs all tests tagged 'navigation'
docker run --rm ... %IMAGE_NAME% pytest -m navigation --alluredir=allure-results

Generate Report: Runs a containerized allure generate command to create static HTML files in the local reports folder.

Serve Report: Launches a final container running a Python HTTP server and opens the interactive Allure report in your default web browser (Port 8080) in a new console window.

Execution Command:

run_docker.bat

Build Optimization and Cleanup
To ensure Docker only caches necessary files and ignores large, irrelevant artifacts during the build process, you should use a .dockerignore file.

File

Purpose

.dockerignore

Prevents large artifacts like Python cache (__pycache__), virtual environments (venv), and test reports from being copied into the Docker build context, which significantly speeds up build times.

Example .dockerignore Content:

# Python artifacts
__pycache__
*.pyc
*.pyo
.pytest_cache
venv/
.tox/

# IDE/OS files
.vscode
.idea
.DS_Store
*.swp

# Generated reports/logs
/allure-results
/reports
*.log

🌳 Framework Architecture
The structure enforces separation between simulation logic, feature specifications, and executable code.

robotics_bdd/
├─ README.md
├─ run_docker.bat                   # Windows batch script for Docker build/run/report
├─ Dockerfile                       # Defines the isolated testing environment
├─ .dockerignore                    # Excludes unnecessary files from Docker build context
├─ Jenkinsfile                      # CI/CD pipeline definition
├─ pytest.ini                       # pytest configuration (markers)
├─ requirements.txt
... (rest of framework structure)

🏷️ Test Tags and Execution
Tests are grouped using pytest markers (tags) to allow for selective execution.

Tag

Focus Area

Description

navigation

Path Planning

Safe movement, obstacle avoidance, and waypoint following.

pick_and_place

Manipulation

Object handling, arm kinematics, and dynamic manipulation sequences.

safety

System Integrity

Collision prevention, boundary limits, and critical error handling.

walking

Gait Control

Posture, speed, stability, and movement transitions during locomotion.

sensors

Data Fusion

Accuracy and convergence of sensor filtering (e.g., Kalman Filter).

Running Test Suites (Local Python Environment Only)
If you are running tests locally without using Docker, these commands apply:

Execution Mode

Command

Run All Tests

pytest --verbose

Run Specific Tag

pytest -m sensors --verbose

Sequential Execution (OR)

pytest -m "navigation or pick_and_place"

Parallel Execution (OR)

pytest -m "navigation or safety" -n auto

📊 Professional Test Reporting
1. Interactive Allure Report (Recommended for Analysis)
Allure generates a rich, interactive HTML dashboard suitable for detailed test analysis, CI/CD integration, and trend monitoring.

Generate Raw Results:

pytest -m "pick_and_place or safety" --alluredir=allure-results

Serve Interactive Report:

allure serve allure-results

This opens the report in your default web browser.

2. Static HTML Report (pytest-html)
Generates a single, self-contained HTML file for simple archiving and sharing.

pytest --html=reports/report.html --self-contained-html

📝 Test Coverage Summary
Feature Area

Objective

Value Proposition

Navigation

Validate robust, collision-free movement across the environment.

Ensures the robot reliably reaches targets while adhering to safety clearances.

Pick and Place

Confirm reliable object interaction and arm dexterity within reach limits.

Guarantees consistent success rates for manipulation tasks.

Safety

Enforce non-negotiable operational limits and error handling.

Prevents equipment damage and maintains system integrity (e.g., chest height, boundary limits).

Sensor Fusion

Ensure the accuracy and stability of sensor-based state estimation.

Validates the integrity of the robot's perception system (Kalman Filter convergence).

Walking

Verify stable and safe locomotion dynamics.

Prevents tripping/falling and maintains optimal posture during movement.

