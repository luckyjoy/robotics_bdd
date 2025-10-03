@echo off
SETLOCAL EnableDelayedExpansion
SET IMAGE_NAME=robotics-bdd-local:latest
SET ARTIFACT_PATH=C:\my_work\robotics_bdd

rem === Robotics BDD Docker Test Runner and Allure Report Generator ===

rem --- Display Header ---
echo.
echo =========================================================
echo Running Robotics BDD Docker Simulation Tests...
echo Image: %IMAGE_NAME%
echo =========================================================
echo.

rem --- Cleanup Previous Artifacts ---
echo Cleaning up previous test artifacts for a fresh run...
rmdir /s /q "%ARTIFACT_PATH%\allure-results" 2>nul
rmdir /s /q "%ARTIFACT_PATH%\reports" 2>nul
rmdir /s /q "%ARTIFACT_PATH%\__pycache__" 2>nul
rmdir /s /q "%ARTIFACT_PATH%\.pytest_cache" 2>nul
mkdir "%ARTIFACT_PATH%\allure-results" 2>nul
echo Cleanup complete.

rem --- 1. Check for Existing Docker Image (Optimization) ---
echo.
echo Checking for existing image: %IMAGE_NAME%
docker images -q %IMAGE_NAME% | findstr /R "[0-9a-f]" >nul
IF %ERRORLEVEL% EQU 0 (
    echo Image found. Skipping build.
    GOTO :test_execution
)

rem --- 2. FORCE BUILD if image not found ---
echo Image not found locally. Starting Docker build process...
docker build -t %IMAGE_NAME% .

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo =========================================================
    echo ERROR: DOCKER IMAGE BUILD FAILED! (Exit Code: %ERRORLEVEL%)
    echo Please check the Dockerfile and ensure Docker Desktop is running.
    echo =========================================================
    GOTO :script_end
)

:test_execution

rem --- 3. Execute Tests and Collect Results ---
echo.
echo Running tests inside Docker container and collecting Allure results...

rem --- Copy Allure environment files ---
echo Copying environment metadata into the results directory...
copy supports\windows.properties "%ARTIFACT_PATH%\allure-results\environment.properties" >nul
copy supports\categories.json "%ARTIFACT_PATH%\allure-results\" >nul
copy supports\executor.json "%ARTIFACT_PATH%\allure-results\" >nul

echo.
rem Run tests with required arguments.
echo docker run --rm -v "%ARTIFACT_PATH%\allure-results":/app/allure-results %IMAGE_NAME%  pytest -m navigation --alluredir=allure-results --ignore=features/manual_tests
  
docker run --rm ^
  -v "%ARTIFACT_PATH%\allure-results":/app/allure-results ^
  %IMAGE_NAME% ^
  pytest -m navigation --alluredir=allure-results --ignore=features/manual_tests

rem Capture the exit code for reporting status only.
SET PYTEST_EXIT_CODE=!ERRORLEVEL!

rem --- Report Status ---
echo.
echo Pytest finished with Exit Code: !PYTEST_EXIT_CODE! (0=Success, 1=Fail, 5=No Tests).
echo Report generation will proceed regardless of the outcome.
echo ---------------------------------------------------------

GOTO :generate_report

:generate_report
rem --- 4A. Generate Static Allure Report ---
echo.
echo Generating static Allure HTML report from results...
echo =========================================================

rem Use a temporary, quick container run to execute the generation command.
rem This creates the static report files in the local %ARTIFACT_PATH%\reports folder.
docker run --rm ^
  -v "%ARTIFACT_PATH%\allure-results":/app/allure-results ^
  -v "%ARTIFACT_PATH%\reports":/app/allure-report ^
  %IMAGE_NAME% ^
  allure generate allure-results -o allure-report --clean

GOTO :serve_report

:serve_report
rem --- 4B. Serve the Generated Report ---
echo.
echo Starting lightweight web server and launching in default browser (Port 8080)...
echo =========================================================

rem *** OPTIMIZATION: This container now only runs the FAST Python HTTP server, removing the slow 'allure generate' step. ***

rem 1. Run the Docker container in a NEW CONSOLE WINDOW using the standard 'start' command. 
rem This container only runs the fast, lightweight Python HTTP server.
start "Allure Report Server" docker run --rm ^
  -v "%ARTIFACT_PATH%\reports":/app/allure-report ^
  -p 8080:8080 ^
  %IMAGE_NAME% ^
  python -m http.server 8080 --directory allure-report

echo Waiting 3 seconds for static HTTP server to start in the new window...
timeout /t 3 /nobreak >nul

rem 2. Launch the browser now that the server is initialized.
start "" "http://localhost:8080"
echo Report launched. Go to the new 'Allure Report Server' window and press Ctrl+C to stop the server when finished.

rem The script ends here, but the Docker process continues to run in the separate window.

:script_end
ENDLOCAL
echo.
echo Script finished.
