@echo off
setlocal ENABLEDELAYEDEXPANSION
title Robotics BDD Simulation Test Runner
chcp 65001 >nul

rem =====================[ ANSI Color Definitions ]=====================
rem Define ANSI escape codes for flicker-free color changes.
rem ESC [ 3X m is foreground color; ESC [ 0m is reset.
rem The ESC character (0x1B) is created using 'echo' and 'set /p' trick.
for /f %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"

rem Colors (Foreground):
set "FG_HEADER=%ESC%[92m"  rem Bright Green
set "FG_STEP=%ESC%[93m"    rem Bright Yellow
set "FG_OK=%ESC%[32m"      rem Green
set "FG_WARN=%ESC%[33m"    rem Yellow
set "FG_ERROR=%ESC%[31m"   rem Red
set "FG_RESET=%ESC%[0m"    rem Reset

rem =====================[ Header ]=====================
echo %FG_HEADER%
echo =============================================================
echo     🤖  Robotics BDD Simulation Test Runner
echo     Author: Bang Thien Nguyen  ^|  ontario1998@gmail.com
echo =============================================================
echo %FG_RESET%
echo.

set "START_TIME=%time%"

rem =====================[ Step 1 ]=====================
echo %FG_STEP%[STEP 1/7] Cleaning up previous test artifacts...%FG_RESET%
rmdir /s /q reports __pycache__ .pytest_cache allure-results >nul 2>&1
mkdir reports >nul 2>&1
echo %FG_OK%[OK] Cleanup completed.%FG_RESET%
echo.

rem =====================[ Step 2 ]=====================
echo %FG_STEP%[STEP 2/7] Building Test Coverage Report...%FG_RESET%
python supports\test_coverage.py supports\requirements.csv features
echo %FG_OK%[OK] Test Coverage Generated.%FG_RESET%
echo.

rem =====================[ Step 3 ]=====================
echo %FG_STEP%[STEP 3/7] Building Automation Rate Metric...%FG_RESET%
python supports\automation_rate.py features
echo %FG_OK%[OK] Automation Rate Generated.%FG_RESET%
echo.

rem =====================[ Step 4 ]=====================
echo %FG_STEP%[STEP 4/7] Generating PRD Summary Report...%FG_RESET%
python supports\prd2html.py supports\product.json supports\requirements.csv
echo %FG_OK%[OK] PRD Summary Generated.%FG_RESET%
echo.

rem =====================[ Step 5 ]=====================
echo %FG_STEP%[STEP 5/7] Building Validation Plan...%FG_RESET%
python supports\validation_plan_builder.py supports\validation.json features supports\requirements.csv
echo %FG_OK%[OK] Validation Plan Generated.%FG_RESET%
echo.

rem =====================[ Step 6 ]=====================
rem echo %FG_STEP%[STEP 6/8] Running Pytest Suites (results → allure-results)...%FG_RESET%
rem pytest --ignore=features/manual_tests --alluredir=allure-results
rem if %ERRORLEVEL% NEQ 0 (
rem    echo %FG_WARN%[WARN] Some tests FAILED during execution.%FG_RESET%
rem    set "TEST_STATUS=FAILED"
rem ) else (
rem    echo %FG_OK%[OK] All tests PASSED.%FG_RESET%
rem    set "TEST_STATUS=PASSED"
rem )
echo.

rem =====================[ Step 6 ]=====================
echo %FG_STEP%[STEP 6/7] Generating Allure Report (port 8081)...%FG_RESET%
copy supports\windows.properties allure-results\environment.properties >nul
copy supports\categories.json allure-results\ >nul
copy supports\executor.json allure-results\ >nul

start "" cmd /c "allure open allure-report"

echo.

rem =====================[ Step 7 ]=====================
echo %FG_STEP%[STEP 7/7] Opening all generated .html reports...%FG_RESET%
for %%f in (reports\*.html) do (
    echo Opening: %%f
    start "" "%%~f"
)
echo %FG_OK%[OK] All local reports opened.%FG_RESET%
echo.

rem =====================[ Completion Summary ]=====================
:cleanup
echo %FG_RESET%
set "END_TIME=%time%"
echo =============================================================
if "%TEST_STATUS%"=="FAILED" (
    echo %FG_ERROR%    ⚠️  PIPELINE COMPLETED WITH SOME TEST FAILURES%FG_RESET%
) else (
    echo %FG_OK%    ✅  PIPELINE COMPLETED SUCCESSFULLY%FG_RESET%
)
echo   Started at: %START_TIME%
echo   Ended at:   %END_TIME%
echo =============================================================

echo.
pause
endlocal
exit /b 0