@echo off
REM Quick setup script for Docker Desktop on Windows
echo ============================================================
echo RAG Engine - Docker Setup Helper
echo ============================================================
echo.

echo Checking for Docker...
docker --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Docker is installed
    docker --version
    echo.
    echo Checking if Docker is running...
    docker info >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] Docker is running
        echo.
        echo Starting PostgreSQL...
        docker compose up -d
        if %errorlevel% == 0 (
            echo.
            echo [SUCCESS] PostgreSQL started!
            echo.
            echo Waiting for PostgreSQL to be ready...
            timeout /t 5 /nobreak >nul
            echo.
            echo Next steps:
            echo   1. Initialize database: python scripts\init_db.py
            echo   2. Test API: python scripts\test_api.py
        ) else (
            echo [FAIL] Failed to start PostgreSQL
        )
    ) else (
        echo [FAIL] Docker is not running
        echo Please start Docker Desktop from the Start menu
        echo Wait for the whale icon to appear in the system tray
    )
) else (
    echo [INFO] Docker is not installed
    echo.
    echo Installing Docker Desktop...
    echo.
    echo Method 1: Using Winget (recommended)
    winget install Docker.DockerDesktop
    echo.
    echo Method 2: Manual Download
    echo   1. Visit: https://www.docker.com/products/docker-desktop/
    echo   2. Download Docker Desktop for Windows
    echo   3. Run the installer
    echo   4. Restart your computer if prompted
    echo   5. Start Docker Desktop
    echo.
    echo After installation, run this script again.
)

pause

