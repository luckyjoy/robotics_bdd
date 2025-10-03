@echo off
setlocal enabledelayedexpansion

:: Set your Jenkins builds directory
set "BUILD_DIR=C:\ProgramData\Jenkins\.jenkins\jobs\robotics_bdd\builds"

:: Loop through all build folders
for /d %%B in ("%BUILD_DIR%\*") do (
    set "BUILD_FOLDER=%%B"
    set "BUILD_NUM=%%~nxB"

    if exist "!BUILD_FOLDER!\build.xml" (
        :: Initialize variables
        set "RESULT="
        set "DURATION="
        set "TIMESTAMP="

        :: Extract <result>
        for /f "tokens=2 delims=>" %%a in ('findstr /i "<result>" "!BUILD_FOLDER!\build.xml"') do (
            set "RESULT=%%a"
            set "RESULT=!RESULT:</result>=!"
        )

        :: Extract <duration>
        for /f "tokens=2 delims=>" %%a in ('findstr /i "<duration>" "!BUILD_FOLDER!\build.xml"') do (
            set "DURATION=%%a"
            set "DURATION=!DURATION:</duration>=!"
        )

        :: Extract <timestamp>
        for /f "tokens=2 delims=>" %%a in ('findstr /i "<timestamp>" "!BUILD_FOLDER!\build.xml"') do (
            set "TIMESTAMP=%%a"
            set "TIMESTAMP=!TIMESTAMP:</timestamp>=!"
        )

        echo Build !BUILD_NUM! : !RESULT! (Duration=!DURATION! ms, Timestamp=!TIMESTAMP!)
    )

    if not exist "!BUILD_FOLDER!\build.xml" (
        echo Build !BUILD_NUM! : build.xml not found
    )
)

pause
