@echo off
rem === Robotics BDD Test Runner and Allure Report Generator ===

rem --- Display Header ---
echo Running Robotics BDD Simulation Tests...
echo Author: Bang Thien Nguyen, ontario1998@gmail.com
echo.

rem --- Cleanup Previous Artifacts (including old results folder) ---
echo Cleaning up previous test artifacts for a fresh run...
rmdir /s /q reports __pycache__ .pytest_cache allure-results 2>nul

rem === Build Supporting Reports ===
rem The following scripts were updated to take a single <features_dir> argument.
echo.
echo Building Test Coverage Report...
echo python supports\test_coverage.py supports\requirements.csv features
python supports\test_coverage.py supports\requirements.csv features

echo.
echo Building Automation Rate Metric...
echo python supports\automation_rate.py features
python supports\automation_rate.py features

echo Building PRD Summary Report...
echo python supports\prd2html.py supports\product.json supports\requirements.csv
python supports\prd2html.py supports\product.json supports\requirements.csv

echo.
echo Building Validation Plan ...
echo python supports\validation_plan_builder.py supports\validation.json features supports\requirements.csv
python supports\validation_plan_builder.py supports\validation.json features supports\requirements.csv

rem === Open Reports in Browser ===
echo.
echo Opening reports in browser...
sleep 3
for %%f in (reports\*.html) do (
    start "" "%%~f"
)

rem --- Execute Tests ---
echo.
echo Running Test Suites and Collecting Results in allure-results...
echo pytest --ignore=features/manual_tests --alluredir=allure-results
pytest --ignore=features/manual_tests --alluredir=allure-results
echo.

rem --- Add Environment Properties to Results Folder ---
rem This copies the environment.properties file from the project root into the newly created results folder.
echo Copying categories.json and environment.properties into the report directory...
copy supports\windows.properties allure-results\environment.properties >nul
copy supports\categories.json allure-results\ >nul
copy supports\executor.json allure-results\ >nul
echo.

rem --- Generate and Serve Report (Automatically Opens in Browser) ---
echo Generating Allure Report and launching in default browser...
allure serve allure-results

rem --- Script End ---
echo Allure report process finished.



echo.
echo All Tasks Completed.
echo.
pause