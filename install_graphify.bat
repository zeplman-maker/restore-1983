@echo off
REM ============================================================
REM  install_graphify.bat
REM  First-time install: installs graphify and runs the initial
REM  graph build for RMF Commander.
REM
REM  Run this ONCE, then use run_graphify_rmf.bat for updates.
REM ============================================================

setlocal

echo.
echo  Installing graphify...
echo.

pip install "git+https://github.com/safishamsi/graphify.git@v8"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  pip install failed. Make sure Python is installed and in your PATH.
    echo  Download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo  graphify installed successfully!
echo.
echo  Running initial graph build...
echo.

call "%~dp0run_graphify_rmf.bat"

endlocal
