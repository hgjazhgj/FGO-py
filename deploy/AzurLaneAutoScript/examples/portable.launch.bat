@echo off
echo %~dp0
set "_root=%~dp0..\..\..\"
set "PATH=%_root%Python39;%_root%Python39\Scripts;%_root%Git\mingw64\bin;%PATH%"
cd /d "%_root%FGO-py\FGO-py"
python ../../deploy/updater.py
if errorlevel 1 (
    echo "Update failed. See above."
    exit
)
python fgo.py cli --no-color
