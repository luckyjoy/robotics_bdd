@echo off
SETLOCAL EnableDelayedExpansion
SET IMAGE_NAME=robotics-bdd-local:latest
REM IMPORTANT: Ensure this path is the root of your local Git repository.
REM ** FIX 1: CRITICAL - Use FOR loop trick to forcefully trim whitespace from the path. **
SET _temp_path=C:\my_work\robotics_bdd
FOR /F "tokens=*" %%A IN ("%_temp_path%") DO (SET ARTIFACT_PATH=%%A)

rem === Robotics BDD Docker Test Runner and Allure Report Generator ===

rem --- Display Header ---
echo =========================================================
echo Running Robotics BDD Docker Simulation Tests...
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

rem -------------------------------------------------------------------
rem --- Cleanup Previous Artifacts (Non-Destructive) ---
rem -------------------------------------------------------------------
echo Cleaning up previous Allure-specific artifacts for a fresh run...
rem ** MODIFIED: Only delete volatile Allure results and the Allure output folder **
rmdir /s /q "%ARTIFACT_PATH%\allure-results" 2>nul
rmdir /s /q "%ARTIFACT_PATH%\reports\allure" 2>nul
rmdir /s /q "%ARTIFACT_PATH%\_site" 2>nul
rmdir /s /q "%ARTIFACT_PATH%\__pycache__" 2>nul
rmdir /s /q "%ARTIFACT_PATH%\.pytest_cache" 2>nul

mkdir "%ARTIFACT_PATH%\allure-results" 2>nul
rem ** MODIFIED: Ensure the new site folder exists **
mkdir "%ARTIFACT_PATH%\_site" 2>nul
echo Cleanup complete.
echo.

rem -------------------------------------------------------------------
rem --- 1. Check for Existing Docker Image (Optimization) ---
rem ** MODIFIED: Skip build if image is found. **
rem -------------------------------------------------------------------
echo Checking for existing Docker image: %IMAGE_NAME%
docker images -q %IMAGE_NAME% | findstr /R "[0-9a-f]" >nul
IF !ERRORLEVEL! EQU 0 (
    echo Docker Image found locally. Skipping build.
    GOTO :test_execution
)

rem -------------------------------------------------------------------
rem --- 2. FORCE BUILD if image not found ---
rem -------------------------------------------------------------------
echo Image not found locally. Starting Docker build process...
docker build --no-cache -t %IMAGE_NAME% .

IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo =========================================================
    echo ERROR: DOCKER IMAGE BUILD FAILED! (Exit Code: !ERRORLEVEL!)
    echo =========================================================
    GOTO :script_end
)

:test_execution

rem -------------------------------------------------------------------
rem --- 3. Execute Tests and Collect Results ---
rem -------------------------------------------------------------------
echo.
echo Running tests inside Docker container and collecting Allure results...

rem --- Copy Allure environment files ---
echo Copying environment metadata into the results directory...
rem ** FIX 2: Using full path for both source and destination to resolve "The system cannot find the path specified" **
copy "%ARTIFACT_PATH%\supports\windows.properties" "%ARTIFACT_PATH%\allure-results\environment.properties" >nul
copy "%ARTIFACT_PATH%\supports\categories.json" "%ARTIFACT_PATH%\allure-results\categories.json" >nul
copy "%ARTIFACT_PATH%\supports\executor.json" "%ARTIFACT_PATH%\allure-results\executor.json" >nul

IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo WARNING: Failed to copy Allure support files. Ensure "%ARTIFACT_PATH%\supports\" directory exists and contains the files.
    echo.
)

echo.
rem Run tests with required arguments.
echo docker run --rm -v "C:\my_work\robotics_bdd\allure-results":/app/allure-results robotics-bdd-local:latest pytest -m navigation --alluredir=allure-results --ignore=features/manual_tests
  
docker run --rm ^
  -v "%ARTIFACT_PATH%\allure-results":/app/allure-results ^
  %IMAGE_NAME% ^
  pytest -m navigation --alluredir=allure-results --ignore=features/manual_tests
timeout /t 1 /nobreak >nul

SET PYTEST_EXIT_CODE=!ERRORLEVEL!

echo.
echo Docker Pytest finished with Exit Code: !PYTEST_EXIT_CODE! (0=Success, 1=Fail, 5=No Tests).
echo ---------------------------------------------------------

GOTO :generate_report

:generate_report
rem -------------------------------------------------------------------
rem --- 4A. Generate Static HTML Report (Allure) into _site ---
rem -------------------------------------------------------------------
echo.
echo Generating static HTML Allure report into the /_site directory...
echo =========================================================

rem Use a temporary, quick container run to execute the Allure generation command.
docker run --rm ^
  -v "%ARTIFACT_PATH%\allure-results":/app/allure-results ^
  -v "%ARTIFACT_PATH%\_site":/app/allure-report ^
  %IMAGE_NAME% ^
  allure generate allure-results -o allure-report --clean

rem -------------------------------------------------------------------
rem --- 4B. Create Netlify Redirects File for _site folder ---
rem -------------------------------------------------------------------
echo.
echo Creating Netlify redirect file to serve Allure report at /reports/allure...
rem The rule tells Netlify: When a user visits /reports/allure/, look in the /_site/ folder.
echo /reports/allure/* /_site/:splat 200 > "%ARTIFACT_PATH%\_redirects"
rem ** NOTE: The line above forces the Allure report to be accessible at /reports/allure/ **

GOTO :deploy_to_github

:deploy_to_github
rem -------------------------------------------------------------------
rem --- 5. Commit and Push Reports to GitHub for Netlify Deployment ---
rem -------------------------------------------------------------------
echo.
echo Committing and pushing the newly generated reports and dashboard to GitHub...
echo =========================================================

rem ** NEW: Wait 2 seconds to ensure all files from the Docker volume mount are written to the host filesystem. **
timeout /t 2 /nobreak >nul

cd /d "%ARTIFACT_PATH%"

rem ** New check to ensure the report was generated before committing. **
IF NOT EXIST "%ARTIFACT_PATH%\_site\index.html" (
    echo.
    echo WARNING: Allure report output was not found in the /_site folder. Skipping commit.
    GOTO :script_end
)

rem 1. Stage all changes (reports, updated index.html, and the _redirects file)
rem ** MODIFIED: Stage the new deployment folder _site and the new _redirects file **
git add _site
git add _redirects
git add reports
git add *.html
git add *.jpg

rem 2. Commit the changes.
git commit -m "Automated report update: %DATE% %TIME%"

IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo WARNING: Git commit may have failed (e.g., no changes). Continuing to push.
)

rem 3. Push to the main branch.
git push origin main

rem ** REVISED: Use IF NOT to check for push success and ensure a clean GOTO **
IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo =========================================================
    echo ERROR: GIT PUSH FAILED! (Exit Code: !ERRORLEVEL!)
    echo Ensure you are authenticated with GitHub.
    echo =========================================================
    GOTO :script_end
)

echo.
echo SUCCESSFULLY PUSHED NEW REPORTS TO GITHUB.
echo Netlify deployment should begin automatically in a moment.

GOTO :script_end

:script_end
ENDLOCAL
rem ** FIX: Using echo( instead of echo. to safely print a blank line and prevent the spurious '.' error. **
echo(
echo Automation Workflow Finished. Check Netlify for deployment status.
