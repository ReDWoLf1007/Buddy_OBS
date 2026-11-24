@echo off
title Buddy Desktop Pet - Stream Server
cd /d "%~dp0"
echo =====================================================
echo  🐾 Buddy Desktop Pet - Stream Server
echo =====================================================
echo.
echo  Starting server at http://localhost:8000...
echo.
python server.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Python could not start server.py.
    echo Trying fallback standard python http.server...
    python -m http.server 8000
)
pause
