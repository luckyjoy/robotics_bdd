@echo off
setlocal

echo.
echo =======================================================
echo DEBUGGER: Inspecting Latest Robotics BDD Job Pod
echo =======================================================

:: Command to find the name of the most recently created Pod by the 'robotics-bdd' label
:: FIX 1: Simplify JSONPath to rely on the --sort-by flag.
:: FIX 2: Correct 'tokens=*' to 'tokens='.
FOR /F "tokens=" %%p IN ('kubectl get pods -l app=robotics-bdd --sort-by=.metadata.creationTimestamp -o jsonpath="{.items[0].metadata.name}" 2^>NUL') DO (
set POD_NAME=%%p
)

if not defined POD_NAME (
echo.
echo ERROR: Could not find any Pods associated with the robotics-bdd Job.
echo Ensure the Job was successfully applied in Step 4.
exit /b 1
)

echo.
echo Found latest Pod: %POD_NAME%
echo -------------------------------------------------------

:: 1. Display the Pod's current status and events
echo Pod Description (Status/Events):
kubectl describe pod %POD_NAME% | findstr /R "Status: Reason: Events:"

echo.
echo -------------------------------------------------------
:: 2. Stream the logs from the Pod (This shows the output of the script that ran inside)
echo Full Container Logs:
echo (Logs will only appear if the container started successfully)
kubectl logs %POD_NAME%

echo.
echo =======================================================
echo DEBUGGER COMPLETE.
echo Check the 'Status' line above for the final result (e.g., Succeeded or Failed).
echo =======================================================

:: FIX 3: Corrected the final command typo from 'endloca' to 'endlocal'
endlocal