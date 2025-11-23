@echo off
REM ================================================================
REM ProjectMaster Enterprise - Windows Starter
REM ================================================================

echo.
echo  ========================================
echo   ProjectMaster Enterprise v2.3
echo  ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python ist nicht installiert!
    echo.
    echo Bitte installiere Python von https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if in virtual environment
if not defined VIRTUAL_ENV (
    echo [INFO] Starte ohne Virtual Environment...
    echo [TIPP] Verwende eine venv für saubere Dependencies:
    echo        python -m venv .venv
    echo        .venv\Scripts\activate
    echo        pip install -r requirements.txt
    echo.
)

REM Install dependencies if needed
if not exist "node_modules" (
    if not exist ".venv\Lib\site-packages\streamlit" (
        echo [INFO] Installiere Dependencies...
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [ERROR] Installation fehlgeschlagen!
            pause
            exit /b 1
        )
    )
)

REM Create data directories
if not exist "data" mkdir data
if not exist "uploads" mkdir uploads
if not exist "project_images" mkdir project_images
if not exist "project_docs" mkdir project_docs
if not exist "logs" mkdir logs

REM Ask to create test data
if not exist "data\projects_data.json" (
    echo.
    echo [INFO] Keine Projekte gefunden.
    set /p CREATE_TEST="Möchtest du Testdaten erstellen? (j/n): "
    if /i "%CREATE_TEST%"=="j" (
        echo [INFO] Erstelle Testdaten...
        python create_test_data.py
    )
)

echo.
echo [INFO] Starte ProjectMaster Enterprise...
echo [INFO] Die App öffnet sich im Browser unter http://localhost:8501
echo [INFO] Drücke CTRL+C zum Beenden
echo.

REM Start Streamlit
streamlit run project_app.py

pause
