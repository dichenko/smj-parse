@echo off
echo Starting Smart-J Web Interface...
cd /d %~dp0
call venv\Scripts\activate.bat
python run_web.py
pause 