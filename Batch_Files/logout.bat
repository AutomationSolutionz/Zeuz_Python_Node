@echo off
for /f "tokens=2 delims=," %%a in ('tasklist /nh /fi "imagename eq Python.exe" /fo csv') do set pid=%%~a
taskkill /PID %pid% /F /T
