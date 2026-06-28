@echo off
echo Starting Jupyter Notebook...
jupyter notebook multispectral_processing.ipynb
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error starting Jupyter Notebook. Press any key to exit.
    pause
)
