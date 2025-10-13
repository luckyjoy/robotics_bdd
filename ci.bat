@echo off

echo %RANDOM% > supports/dummy.txt
echo Add dummy file dummy.txt and make a git push to main

git add .

rem echo Git pushed a dummy file for CI Demo
echo.
echo git commit -m "Git Push Main to Trigger CI with Jenkins Webhooks and Github Workflow Actions ..."
git commit -m "Push Main to Trigger CI ..."

REM Ensure branch is main
git branch -M main

git remote add origin https://github.com/luckyjoy/robotics_bdd.git >nul 2>&1

echo.
echo git push -u origin main
git push -u origin main
curl -u "luckyjoy:11ce1755fa745c0bf522d169a9cac2ca11" -k -X POST "https://localhost:8443/job/robotics_bdd/build"

echo.
echo A CI has been triggred at secured Github workflow: https://github.com/luckyjoy/robotics_bdd
echo.
echo A CI has been triggred at secured Jenkins pipeline: https://localhost:8443/view/all/builds
echo.
echo Open secured GitHub server and Jenkins server
echo.
sleep 4

start "" "https://github.com/luckyjoy/robotics_bdd/actions"
echo.
 start "" https://localhost:8443/view/all/builds
