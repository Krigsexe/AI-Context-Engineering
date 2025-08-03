@echo off
REM Build script for Windows

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Run PyInstaller
pyinstaller odin.spec

ECHO Build complete. Binary located in dist\odin.exe

