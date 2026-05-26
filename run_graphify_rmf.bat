@echo off
REM ============================================================
REM  run_graphify_rmf.bat
REM  One-click: build graphify knowledge graph for RMF Commander
REM  and export it into your Obsidian vault (Leo's Brain).
REM
REM  FIRST-TIME SETUP: run install_graphify.bat instead.
REM ============================================================

setlocal

REM -- Change this if your project is in a different location --
set PROJECT=C:\Users\Zeplman\Documents\Leo's Brain\03 - Projects\RMF Commander

echo.
echo  RMF Commander  graphify  Obsidian
echo  Project: %PROJECT%
echo.

python "%~dp0graphify_rmf.py" --project "%PROJECT%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  Something went wrong. See errors above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo  Press any key to open the graphify-map folder in Explorer...
pause >nul
explorer "%PROJECT%\graphify-map"

endlocal
