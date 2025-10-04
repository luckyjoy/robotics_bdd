@echo off
echo git add .

git add .

rem echo Git pushed a dummy file for CI Demo
echo.
echo git commit -m "Update Test Runs with Docker..."
git commit -m "Update Test Runs with Docker..."
echo git branch -M main
REM Ensure branch is main
git branch -M main
echo git remote add origin https://github.com/luckyjoy/robotics_bdd.git 
git remote add origin https://github.com/luckyjoy/robotics_bdd.git 

echo Done.

