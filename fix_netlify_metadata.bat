@echo off
REM --- SET ENVIRONMENT VARIABLE ---
REM ALLURE_ENVIRONMENT_BASEURL tells the Allure web app where its data files are located.
REM This is CRITICAL for static hosting (like Netlify) when the report is in a subdirectory.
set ALLURE_ENVIRONMENT_BASEURL=/reports/latest/

REM --- EXECUTE ALLURE GENERATION ---
REM We use the environment variable set above to fix pathing for Netlify.
REM Note: Removed the problematic '--report-url' flag.
echo Generating Allure report with ALLURE_ENVIRONMENT_BASEURL=%ALLURE_ENVIRONMENT_BASEURL%
call allure generate --clean allure-results --output reports/latest

REM --- Error Checking ---
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo CRITICAL ERROR: Allure report generation failed (Exit Code: %ERRORLEVEL%).
    goto :eof
)

echo.
echo Allure report successfully generated and configured for Netlify deployment.
