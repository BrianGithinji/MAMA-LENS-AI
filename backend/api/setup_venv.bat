@echo off
cd /d "d:\MAMA-LENS AI\SYSTEM\backend\api"

echo [1/3] Removing old broken venv...
rmdir /s /q .venv311

echo [2/3] Creating new venv...
python -m venv .venv311

echo [3/3] Installing requirements...
.venv311\Scripts\pip.exe install --upgrade pip
.venv311\Scripts\pip.exe install -r requirements.txt

echo.
echo Done! Now run:
echo   .venv311\Scripts\uvicorn.exe main:app --reload --host 0.0.0.0 --port 8000
