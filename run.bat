@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON=py -3"
    ) else (
        set "PYTHON=python"
    )
    echo Creating virtual environment...
    %PYTHON% -m venv .venv
    set "PYTHON=.venv\Scripts\python.exe"
)

"%PYTHON%" -m pip --version >nul 2>nul
if errorlevel 1 "%PYTHON%" -m ensurepip --upgrade

"%PYTHON%" -m pip install --upgrade pip setuptools wheel
"%PYTHON%" -m pip install -r requirements.txt
"%PYTHON%" -m ml.train

start "LandslideGuard API" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m uvicorn backend.api:app --port 8000"
"%PYTHON%" -m streamlit run frontend/app.py
