@echo off
if exist build (
    rmdir /S /Q build
)

if exist dist (
    rmdir /S /Q dist
)

pyinstaller.exe --noconsole .\main.py
robocopy assets dist/main/assets > nul

if not exist dist\main\main.exe (
    cls
    color 47
    echo [Build Status] : Failed!
    timeout /t 3 > nul
    color 07
    exit
)

start dist\main\main.exe

cls
color 27
echo [Build Status] : Success!
timeout /t 3 > nul
color 07