@echo off
rem Double-click this file after extracting the zip. It runs setup_windows.ps1 with the execution policy bypassed for this run only.
if not exist "%~dp0setup_windows.ps1" (
  echo Extract the zip first: right-click the zip file, choose "Extract All", then run this file again.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_windows.ps1"
pause
