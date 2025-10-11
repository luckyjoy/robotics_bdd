@echo off
setlocal
set REPORT_OUTPUT_DIR=allure-report

echo.
echo ==========================================================
echo           Allure Report Generation with History
echo ==========================================================
echo.

rem --- 1. Cleanup and Preparation ---
rem Delete old results to ensure a fresh run.
IF EXIST allure-results rmdir /s /q allure-results >nul
echo Running pytest and collecting results into allure-results...
pytest --alluredir=allure-results
echo.

rem --- 2. Copy Environment Properties and Categories ---
echo Copying categories.json and environment.properties into the report directory...
rem Assuming 'supports' folder is in the project root.
copy supports\windows.properties allure-results\environment.properties >nul
copy supports\categories.json allure-results\ >nul
echo Environment files copied successfully.
echo.

rem --- 3. CRITICAL STEP: Copy previous report history for trending ---
IF EXIST "%REPORT_OUTPUT_DIR%\history" (
    echo Found previous history data. Copying to allure-results...
    xcopy "%REPORT_OUTPUT_DIR%\history" "allure-results\history\" /E /I /Q /Y >nul
    echo History copied from "%REPORT_OUTPUT_DIR%\history"
) ELSE (
    echo Previous report history folder not found at "%REPORT_OUTPUT_DIR%\history". Trend will start from this run.
)
echo.

rem --- 4. Generate Persistent Report (Enable Trend) ---
echo Generating Allure Report into persistent folder: %REPORT_OUTPUT_DIR%
rem The --clean flag ensures the folder is clean before merging data.
call allure generate allure-results --clean -o %REPORT_OUTPUT_DIR%
echo Report successfully generated.
echo.

rem --- 5. Launch Report using Allure's built-in server launcher ---
rem FIX: Using the confirmed working manual command, wrapped in `start ""`,
rem which forces it to run as a separate, non-blocking process.
echo ======================================================================
echo  ** Launching Allure report server... **
echo.
echo  The report will open in your browser automatically.
echo  To stop the server, simply CLOSE the resulting command window.
echo ======================================================================
echo.

rem Start in a separate process to prevent blocking
start "" allure open "%REPORT_OUTPUT_DIR%"

echo.
echo Allure report generation and launch command issued.
echo Report is permanently saved in the "%REPORT_OUTPUT_DIR%" folder.

endlocal
