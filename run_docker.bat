@echo off
SETLOCAL EnableDelayedExpansion
SET IMAGE_NAME=robotics-bdd-local:latest
REM IMPORTANT: Ensure this path is the root of your local Git repository.
SET ARTIFACT_PATH=C:\my_work\robotics_bdd 

rem === Robotics BDD Docker Test Runner and Allure Report Generator ===

rem --- 0. BUILD NUMBER CHECK ---
IF "%1"=="" (
    echo.
    echo ERROR: Build number is missing!
    echo Usage: %~n0 [BUILD_NUMBER]
    echo Example: %~n0 102
    GOTO :script_end
)

SET BUILD_NUMBER=%1
SET BUILD_FOLDER=%ARTIFACT_PATH%\reports\%BUILD_NUMBER%

rem --- Display Header ---
echo =========================================================
echo Running Robotics BDD Docker Tests for Build #%BUILD_NUMBER%
echo Docker Image: %IMAGE_NAME%
echo =========================================================
echo.

rem --- Diagnostic: Check Docker Status and Version ---
echo Checking Docker service and version...
docker --version
IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo =========================================================
    echo ERROR: DOCKER COMMAND FAILED!
    echo Please ensure Docker Desktop is installed and running.
    echo =========================================================
    GOTO :script_end
)
echo Docker is ready.
echo.

rem --- Cleanup Previous Artifacts and Setup New Folder ---
echo Cleaning up previous Allure results and setting up new report archive...
rmdir /s /q "%ARTIFACT_PATH%\allure-results" 2>nul
rmdir /s /q "%ARTIFACT_PATH%\__pycache__" 2>nul
rmdir /s /q "%ARTIFACT_PATH%\.pytest_cache" 2>nul
mkdir "%ARTIFACT_PATH%\allure-results" 2>nul

rem Create the permanent, build-specific archive folder
mkdir "%ARTIFACT_PATH%\reports" 2>nul
mkdir "%BUILD_FOLDER%" 2>nul
echo Setup complete. Archive folder created: %BUILD_FOLDER%
echo.

rem --- 1. Execute Tests and Collect Results ---
echo Running Pytest inside Docker container and collecting Allure results...
rem ( ... Your actual Docker run command for Pytest goes here ... )
rem Example:
rem docker run --rm -v "%ARTIFACT_PATH%\allure-results":/app/allure-results %IMAGE_NAME% pytest --alluredir=allure-results

rem -------------------------------------------------------------------
rem --- 2. Generate Static Reports into Build Archive Folder ---
rem -------------------------------------------------------------------
echo.
echo Generating static reports into archive: %BUILD_FOLDER%

rem 2A. Generate Allure Report
echo Generating static HTML Allure report...
docker run --rm ^
  -v "%ARTIFACT_PATH%\allure-results":/app/allure-results ^
  -v "%BUILD_FOLDER%\allure":/app/allure-report ^
  %IMAGE_NAME% ^
  allure generate allure-results -o allure-report --clean

rem 2B. Move/Copy Custom Reports to Archive Folder
echo Moving custom reports (Validation_Plan, Automation Rate, PRD Summary, Coverage) to archive...
rem IMPORTANT: Ensure your test process creates these files at the root of the ARTIFACT_PATH or another known location.
rem We assume they are created in the root path for this example. Adjust 'move' source as necessary.
move "%ARTIFACT_PATH%\Validation_Plan.html" "%BUILD_FOLDER%\" 2>nul
move "%ARTIFACT_PATH%\automation_rate_report.html" "%BUILD_FOLDER%\" 2>nul
move "%ARTIFACT_PATH%\prd_summary.html" "%BUILD_FOLDER%\" 2>nul
move "%ARTIFACT_PATH%\test_coverage_report.html" "%BUILD_FOLDER%\" 2>nul

rem -------------------------------------------------------------------
rem --- 3. Update Dashboard (index.html) with New Build Number ---
rem -------------------------------------------------------------------
echo.
echo Dynamically updating index.html with Build #%BUILD_NUMBER%...

rem Use PowerShell to replace the placeholder '{{BUILD_NUMBER}}' in index.html with the actual build number.
powershell -Command "(gc index.html) -replace '{{BUILD_NUMBER}}', '%BUILD_NUMBER%' | Out-File -encoding ASCII index.html"

IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo ERROR: Failed to update index.html with PowerShell. Check file permissions or PowerShell execution policy.
    GOTO :script_end
)

rem -------------------------------------------------------------------
rem --- 4. Commit and Push Reports to GitHub for Netlify Deployment ---
rem -------------------------------------------------------------------
echo.
echo Committing and pushing the newly generated reports and dashboard to GitHub...
echo =========================================================

cd /d "%ARTIFACT_PATH%"

rem 1. Stage all changes: the new build folder, and the updated index.html
git add index.html
git add reports
git commit -m "Automated report update: Deploying Build #%BUILD_NUMBER%"

IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo WARNING: Git commit may have failed (e.g., no changes). Proceeding to push.
)

rem 2. Push to the main branch. Netlify will detect this and deploy!
git push origin main

IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo =========================================================
    echo ERROR: GIT PUSH FAILED!
    echo Ensure you are authenticated with GitHub (e.g., via GitHub CLI or PAT).
    echo =========================================================
    GOTO :script_end
)

echo.
echo SUCCESSFULLY DEPLOYED Build #%BUILD_NUMBER%.
echo Netlify deployment should begin automatically in a moment.

GOTO :script_end

:script_end
ENDLOCAL
echo(
echo Automation Workflow Finished.
