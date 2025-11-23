@echo off
REM ================================================================
REM ProjectMaster Enterprise - Docker Starter (Windows)
REM ================================================================

echo.
echo  ========================================
echo   ProjectMaster Enterprise v2.3
echo   Docker Mode
echo  ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker ist nicht installiert!
    echo.
    echo Bitte installiere Docker Desktop von https://docker.com
    echo.
    pause
    exit /b 1
)

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker läuft nicht!
    echo.
    echo Bitte starte Docker Desktop und versuche es erneut.
    echo.
    pause
    exit /b 1
)

echo [INFO] Docker ist bereit!
echo.

REM Create data directories
if not exist "data" mkdir data
if not exist "uploads" mkdir uploads
if not exist "project_images" mkdir project_images
if not exist "project_docs" mkdir project_docs
if not exist "logs" mkdir logs

REM Check if container exists
docker ps -a | findstr projectmaster-enterprise >nul 2>&1
if errorlevel 1 (
    echo [INFO] Erstelle Docker Container...
    docker-compose up -d
    if errorlevel 1 (
        echo [ERROR] Container konnte nicht erstellt werden!
        pause
        exit /b 1
    )
) else (
    echo [INFO] Starte vorhandenen Container...
    docker-compose start
)

echo.
echo [SUCCESS] ProjectMaster Enterprise läuft!
echo.
echo  Öffne im Browser: http://localhost:8501
echo.
echo  Befehle:
echo   - Stoppen:   docker-compose stop
echo   - Neustarten: docker-compose restart
echo   - Logs:      docker-compose logs -f
echo   - Löschen:   docker-compose down
echo.

REM Open browser automatically
timeout /t 3 /nobreak >nul
start http://localhost:8501

echo Drücke eine Taste um die Logs zu sehen (CTRL+C zum Beenden)...
pause >nul

docker-compose logs -f
