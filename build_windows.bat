@echo off
REM Windows build script for PDF Template Generator
REM Run this on a Windows machine with Python installed

echo === PDF Template Generator Windows Build ===
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv build_venv
call build_venv\Scripts\activate.bat

echo [2/4] Installing dependencies...
pip install --upgrade pip
pip install PyMuPDF Pillow pyinstaller

echo [3/4] Building executable...
pyinstaller pdf_generator.spec --clean

echo [4/4] Cleaning up...
rmdir /s /q build_venv
rmdir /s /q build
del /q *.spec.bak 2>nul

echo.
echo === Build Complete! ===
echo Executable is in: dist\PDFTemplateGenerator.exe
echo.
pause
