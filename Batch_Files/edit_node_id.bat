@echo off
title Edit Node ID
set "conf_file=node_id.conf"
for /f "delims=" %%i in ('dir /b /s "%conf_file%"') do set "file_dir=%%~dpi"
cd /d "%file_dir%"

set "key_to_modify=id "
for /f "tokens=1,* delims==" %%a in ('type "%conf_file%"') do (
    if "%%a"=="%key_to_modify%" ( 
        echo Current Node ID: %%b
    ))
:loop
set /p new_value= Enter New Node ID (Letters, Digits and "-" Only): 
echo %new_value%| findstr /R "^[A-Za-z0-9\-]*$">nul
if errorlevel 1 (
    echo Invalid input. Please try again.
) else (
    goto endloop
)
goto loop

:endloop
(for /f "tokens=1,* delims==" %%a in ('type "%conf_file%"') do (
    if "%%a"=="%key_to_modify%" ( 
        echo %key_to_modify%= %new_value%
    ) else (
        echo %%a
    )
)) > "%conf_file%.tmp"

move /y "%conf_file%.tmp" "%conf_file%" > nul

for /f "tokens=1,* delims==" %%a in ('type "%conf_file%"') do (
    if "%%a"=="%key_to_modify%" ( 
        echo New Node ID: %%b
    ))
pause
