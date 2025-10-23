@echo off

:: Check if a commit message is provided as an argument (%1)
IF "%~1"=="" (
    :: If no argument is provided, use the default message
    SET "COMMIT_MSG=Updated CI"
) ELSE (
    :: If an argument is provided, use it as the commit message
    SET "COMMIT_MSG=%~1"
)

echo git add .
git add .
echo.

echo git commit -m "%COMMIT_MSG%"
git commit -m "%COMMIT_MSG%"

echo git branch -M main
REM Ensure branch is main
git branch -M main

echo git remote add origin https://github.com/luckyjoy/gpu_benchmark.git 
git remote add origin https://github.com/luckyjoy/gpu_benchmark.git 

echo git push origin main
git push origin main

echo Done.