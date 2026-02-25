@echo off
rem jump to the folder where this .bat lives
cd /d "%~dp0"

rem use venv if it exists, otherwise fall back to py
if exist ".venv\Scripts\python.exe" (
  ".\.venv\Scripts\python.exe" "Habit_Tracker.py"
) else (
  py "Habit_Tracker.py"
)

pause