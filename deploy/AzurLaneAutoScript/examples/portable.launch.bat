@echo off
echo %~dp0
set "_root=%~dp0..\..\..\"
set "PATH=%_root%Python311;%_root%Python311\Scripts;%_root%Git\mingw64\bin;%PATH%"
cd /d "%_root%FGO-py\FGO-py"
python ../../deploy/updater.py
if errorlevel 1 (
    echo Update failed. See above.
    exit
)
python -X utf8 fgo.py cli --no-color
