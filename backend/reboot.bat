@echo off
REM ============================================================================
REM SPARS Backend Service Installation (Computer 2)
REM ============================================================================
REM This installs the FastAPI backend as a Windows service
REM MUST RUN AS ADMINISTRATOR
REM ============================================================================

setlocal

REM ===== CONFIGURATION - MODIFY THESE PATHS =====
set SERVICE_NAME=SPARS-Backend
set BACKEND_DIR=C:\Users\Administrator\Desktop\SPARS-only-backend\backend
set PYTHON_EXE=C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe
set NSSM_PATH=C:\Users\Administrator\Downloads\nssm-2.24\win64\nssm.exe

REM If using system Python instead of venv, change to:
REM set PYTHON_EXE=python

echo ============================================================================
echo SPARS Backend Service Installation
echo ============================================================================
echo.
echo Service Name: %SERVICE_NAME%
echo Backend Dir: %BACKEND_DIR%
echo Python: %PYTHON_EXE%
echo.

REM Verify paths
if not exist "%BACKEND_DIR%" (
    echo [ERROR] Backend directory not found!
    echo Expected: %BACKEND_DIR%
    echo.
    echo Please update the BACKEND_DIR path in this script.
    pause
    exit /b 1
)

if not exist "%NSSM_PATH%" (
    echo [ERROR] NSSM not found!
    echo Expected: %NSSM_PATH%
    echo.
    echo Please download NSSM from https://nssm.cc/download
    echo Or update the NSSM_PATH in this script.
    pause
    exit /b 1
)

echo [Step 1/4] Stopping and removing old service (if exists)...
"%NSSM_PATH%" stop %SERVICE_NAME% >nul 2>&1
timeout /t 2 >nul
"%NSSM_PATH%" remove %SERVICE_NAME% confirm >nul 2>&1
echo Done.
echo.

echo [Step 2/4] Installing service...
"%NSSM_PATH%" install %SERVICE_NAME% "%PYTHON_EXE%"
if errorlevel 1 (
    echo [ERROR] Failed to install service!
    echo Make sure you are running as Administrator.
    pause
    exit /b 1
)
echo Service installed!
echo.

echo [Step 3/4] Configuring service...

REM Set working directory
reg add "HKLM\SYSTEM\CurrentControlSet\Services\%SERVICE_NAME%\Parameters" /v AppDirectory /t REG_EXPAND_SZ /d "%BACKEND_DIR%" /f >nul

REM Set uvicorn command
REM Note: --reload is removed for production service (causes issues)
"%NSSM_PATH%" set %SERVICE_NAME% AppParameters "-m uvicorn main:app --host 0.0.0.0 --port 8000" >nul

REM Set logs
"%NSSM_PATH%" set %SERVICE_NAME% AppStdout "%BACKEND_DIR%\service_stdout.log" >nul
"%NSSM_PATH%" set %SERVICE_NAME% AppStderr "%BACKEND_DIR%\service_stderr.log" >nul

REM Service behavior
"%NSSM_PATH%" set %SERVICE_NAME% Start SERVICE_AUTO_START >nul
"%NSSM_PATH%" set %SERVICE_NAME% Description "SPARS Backend - FastAPI Application" >nul
"%NSSM_PATH%" set %SERVICE_NAME% ObjectName "LocalSystem" >nul

REM Restart behavior
"%NSSM_PATH%" set %SERVICE_NAME% AppThrottle 5000 >nul
"%NSSM_PATH%" set %SERVICE_NAME% AppExit Default Restart >nul
"%NSSM_PATH%" set %SERVICE_NAME% AppRestartDelay 3000 >nul

echo Configuration complete!
echo.

echo [Step 4/4] Starting service...
"%NSSM_PATH%" start %SERVICE_NAME%
echo Waiting for startup...
timeout /t 5 >nul
echo.

echo ============================================================================
echo Status Check
echo ============================================================================
echo.

echo Service Status:
"%NSSM_PATH%" status %SERVICE_NAME%
echo.

echo Port 8000:
netstat -ano | findstr :8000
if errorlevel 1 (
    echo [WARNING] Port 8000 not listening
) else (
    echo [SUCCESS] Service is running on port 8000!
)
echo.

echo Logs (last 10 lines):
echo.
echo --- STDOUT ---
powershell -Command "if (Test-Path '%BACKEND_DIR%\service_stdout.log') { Get-Content '%BACKEND_DIR%\service_stdout.log' -Tail 10 } else { Write-Host 'No output yet' }"
echo.
echo --- STDERR ---
powershell -Command "if (Test-Path '%BACKEND_DIR%\service_stderr.log') { Get-Content '%BACKEND_DIR%\service_stderr.log' -Tail 10 } else { Write-Host 'No errors' }"
echo.

echo ============================================================================
echo Installation Complete!
echo ============================================================================
echo.
echo Service Management:
echo   Status:  "%NSSM_PATH%" status %SERVICE_NAME%
echo   Start:   "%NSSM_PATH%" start %SERVICE_NAME%
echo   Stop:    "%NSSM_PATH%" stop %SERVICE_NAME%
echo   Restart: "%NSSM_PATH%" restart %SERVICE_NAME%
echo.
echo Application: http://localhost:8000
echo.
echo The service will AUTO-START on system boot.
echo ============================================================================
pause
