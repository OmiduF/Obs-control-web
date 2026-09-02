@echo off
title OBS Control Deck
cd /d "%~dp0"

echo ============================================
echo   OBS Control Deck - pornire...
echo ============================================
echo.

REM Cauta Python (intai lansatorul "py", apoi "python")
where py >nul 2>nul
if %errorlevel%==0 (
    py "%~dp0obs_control_server.py"
    goto :end
)

where python >nul 2>nul
if %errorlevel%==0 (
    python "%~dp0obs_control_server.py"
    goto :end
)

echo [EROARE] Python nu este instalat sau nu este in PATH.
echo Instaleaza Python de pe https://www.python.org/downloads/
echo IMPORTANT: la instalare bifeaza "Add Python to PATH".
echo.

:end
echo.
echo Serverul s-a oprit. Apasa o tasta ca sa inchizi fereastra.
pause >nul
