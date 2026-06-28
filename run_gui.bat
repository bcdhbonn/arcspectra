@echo off
echo Starting Multispectral Index Processor GUI...
python gui.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error starting GUI. Press any key to exit.
    pause
)
