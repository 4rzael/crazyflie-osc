@ECHO OFF

REM ----[ This code block detects if the script is being running with admin PRIVILEGES If it isn't it pauses and then quits]-------
NET SESSION >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    ECHO.
) ELSE (
   ECHO [91m
   ECHO ######## ########  ########   #######  ########
   ECHO ##       ##     ## ##     ## ##     ## ##     ##
   ECHO ##       ##     ## ##     ## ##     ## ##     ##
   ECHO ######   ########  ########  ##     ## ########
   ECHO ##       ##   ##   ##   ##   ##     ## ##   ##
   ECHO ##       ##    ##  ##    ##  ##     ## ##    ##
   ECHO ######## ##     ## ##     ##  #######  ##     ##
   ECHO.
   ECHO.
   ECHO ####### ERROR: ADMINISTRATOR PRIVILEGES REQUIRED #########
   ECHO This script must be run as administrator to work properly!
   ECHO If you're seeing this after running this script, then right click on the shortcut and select "Run As Administrator".
   ECHO ##########################################################
   ECHO.
   ECHO [0m
   PAUSE
   EXIT /B 1
)

:: Install chocolatey
:choco_begin
set /p choco="[33mInstall chocolatey ? (y - Yes, n - No): [0m"
IF /i "%choco%" == "y" GOTO choco_install
IF /i "%choco%" == "n" GOTO choco_end
ECHO [91mInvalid option[0m
GOTO choco_begin
:choco_install
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1'))" && SET PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin
ECHO [36mCHOCOLATEY INSTALLED[0m
:choco_end

:: Install python and pip
:python_begin
set /p python="[33mInstall python ? (y - Yes, n - No): [0m"
IF /i "%python%" == "y" GOTO python_install
IF /i "%python%" == "n" GOTO python_end
ECHO [91mInvalid option[0m
GOTO python_begin
:python_install
choco install python -y
ECHO [36mPYTHON INSTALLED[0m
SET PATH=%PATH%;C:\tools\python\Scripts\
ECHO [36mPIP INSTALLED[0m
:python_end

:: Install virtualenv
:virtualenv_begin
set /p virtualenv="[33mInstall virtualenv ? (y - Yes, n - No): [0m"
IF /i "%virtualenv%" == "y" GOTO virtualenv_install
IF /i "%virtualenv%" == "n" GOTO virtualenv_end
ECHO [91mInvalid option[0m
GOTO virtualenv_begin
:virtualenv_install
pip install virtualenv
ECHO [36mVIRTUALENV INSTALLED[0m
:virtualenv_end

:: Install git
:git_begin
set /p git="[33mInstall git ? (y - Yes, n - No): [0m"
IF /i "%git%" == "y" GOTO git_install
IF /i "%git%" == "n" GOTO git_end
ECHO [91mInvalid option[0m
GOTO git_begin
:git_install
choco install git.install -params '"/GitOnlyOnPath"' -y
ECHO [36mGIT INSTALLED[0m
:git_end

:: Install project
:project_begin
set /p project="[33mInstall crazyflie-osc ? (y - Yes, n - No): [0m"
IF /i "%project%" == "y" GOTO project_install
IF /i "%project%" == "n" GOTO project_end
ECHO [91mInvalid option[0m
GOTO project_begin
:project_install
set /p install_folder="[33mWhere should it be installed ? (default : Documents): [0m"
IF /i "%install_folder%" == "" GOTO project_set_folder
GOTO project_set_folder_end
:project_set_folder
for /f "tokens=3* delims= " %%a in ('reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v "Personal"') do (set mydocuments=%%~a)
set install_folder="%mydocuments%"
:project_set_folder_end
ECHO [93mInstall folder is %install_folder%[0m
PAUSE
cd %install_folder%
git clone https://github.com/4rzael/crazyflie-osc
cd crazyflie-osc
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
ECHO [36mPROJECT INSTALLED[0m
:project_end

:: Install zagid (crazyradio driver)
:zadig_begin
set /p zadig="[33mInstall zadig (crazyradio driver) ? (y - Yes, n - No): [0m"
IF /i "%zadig%" == "y" GOTO zadig_install
IF /i "%zadig%" == "n" GOTO zadig_end
ECHO [91mInvalid option[0m
GOTO zadig_begin
:zadig_install
choco install zadig -y
ECHO [36mZADIG INSTALLED[0m
ECHO [33mNow follow the procedure here to install the crazyradio drivers (zadig is already installed, though): https://wiki.bitcraze.io/doc:crazyradio:install_windows_zadig [0m
:zadig_end

ECHO [92mDONE ![0m
PAUSE
