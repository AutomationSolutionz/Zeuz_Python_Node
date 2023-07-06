@echo off
title Login
set file=node_cli.py
for /f "delims=" %%i in ('dir /b /s "node_cli.py"') do set "file_dir=%%~dpi"
cd /d "%file_dir%"
python "%file%" -l

