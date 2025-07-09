@echo off
REM =====================================================
REM FarmConnect PostgreSQL Database Setup Script (Windows)
REM Run this batch file to create the database and tables
REM =====================================================

echo 🌱 FarmConnect PostgreSQL Database Setup
echo ========================================

REM Database configuration
set DB_NAME=farmconnect
set DB_USER=postgres
set DB_HOST=localhost
set DB_PORT=5432

echo.
echo ℹ️  Checking PostgreSQL installation...

REM Check if psql is available
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PostgreSQL is not installed or not in PATH
    echo Please install PostgreSQL first:
    echo   - Download from https://www.postgresql.org/download/windows/
    echo   - Make sure to add PostgreSQL bin directory to your PATH
    pause
    exit /b 1
)

echo ✅ PostgreSQL is installed

echo.
echo ℹ️  Creating database '%DB_NAME%'...

REM Check if database exists
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -lqt | findstr /C:"%DB_NAME%" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Database '%DB_NAME%' already exists
    set /p "choice=Do you want to drop and recreate it? (y/N): "
    if /i "%choice%"=="y" (
        echo ℹ️  Dropping existing database...
        dropdb -h %DB_HOST% -p %DB_PORT% -U %DB_USER% %DB_NAME%
        echo ✅ Database dropped
    ) else (
        echo ℹ️  Using existing database
        goto :run_script
    )
)

REM Create new database
createdb -h %DB_HOST% -p %DB_PORT% -U %DB_USER% %DB_NAME%
if %errorlevel% equ 0 (
    echo ✅ Database '%DB_NAME%' created successfully
) else (
    echo ❌ Failed to create database '%DB_NAME%'
    pause
    exit /b 1
)

:run_script
echo.
echo ℹ️  Running SQL script to create tables...

REM Check if SQL script exists
if not exist "farmconnect_postgresql.sql" (
    echo ❌ SQL script 'farmconnect_postgresql.sql' not found
    echo ℹ️  Make sure you're running this script from the scripts directory
    pause
    exit /b 1
)

REM Run SQL script
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f farmconnect_postgresql.sql

if %errorlevel% equ 0 (
    echo ✅ Tables created successfully
) else (
    echo ❌ Failed to create tables
    pause
    exit /b 1
)

echo.
echo ✅ Database setup completed!
echo.
echo ℹ️  Connection Details:
echo   Host: %DB_HOST%
echo   Port: %DB_PORT%
echo   Database: %DB_NAME%
echo   User: %DB_USER%
echo.
echo ℹ️  To connect to the database:
echo   psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME%
echo.
echo ℹ️  Sample login credentials (password: password123):
echo   - john.davis@email.com (Mentor)
echo   - sarah.martinez@email.com (Beginner)
echo   - linda.wilson@email.com (Livestock Expert)
echo.
pause
