@echo off
set "_root=%~dp0..\..\..\"
set "PATH=%_root%Python39;%_root%Python39\Scripts;%_root%Git\mingw64\bin;%PATH%"
cd "%_root%FGO-py\FGO-py"
git pull --no-rebase origin master
python fgo.py cli --no-color
