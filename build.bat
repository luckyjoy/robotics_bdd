@echo off
rem === Robotics BDD Test Runner and Allure Report Generator ===

rem --- Display Header ---
echo Running Robotics BDD Simulation Tests...
echo Author: Bang Thien Nguyen, ontario1998@gmail.com
echo.

rem --- Cleanup Previous Artifacts (including old results folder) ---
echo Cleaning up previous test artifacts for a fresh run...
rmdir /s /q __pycache__ .pytest_cache allure-results 2>nul
echo.

rem --- Execute Tests ---
echo Running pytest and collecting results into allure-results...
pytest --alluredir=allure-results
echo.

rem --- Add Environment Properties to Results Folder ---
rem This copies the environment.properties file from the project root into the newly created results folder.
echo Copying categories.json and environment.properties into the report directory...
copy supports\environment.properties allure-results\ >nul
copy supports\categories.json allure-results\ >nul
echo.

rem --- Generate and Serve Report (Automatically Opens in Browser) ---
echo Generating Allure Report and launching in default browser...
allure serve allure-results

rem --- Script End ---
echo Allure report process finished.