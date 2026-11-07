@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

echo ====================================================
echo   Audio Extraction and Transcription Pipeline
echo ====================================================
echo.

:: Automatically create .env from .envexample if missing
if not exist ".env" (
    if exist ".envexample" (
        echo [INFO] .env not found. Creating from .envexample...
        copy ".envexample" ".env" >nul
    ) else if exist ".env.example" (
        echo [INFO] .env not found. Creating from .env.example...
        copy ".env.example" ".env" >nul
    )
)

:: Activate virtual environment .venv if present
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment .venv...
    call ".venv\Scripts\activate.bat"
) else (
    echo [WARNING] Virtual environment .venv not found. Using system Python...
)

echo.
echo ====================================================
echo [1/2] Running audio_extract.py...
echo ====================================================
python audio_extract.py
if errorlevel 1 goto :error_extract

echo.
echo ====================================================
echo [2/2] Running transcribe.py...
echo ====================================================
python transcribe.py %*
if errorlevel 1 goto :error_transcribe

echo.
echo ====================================================
echo Pipeline completed successfully!
echo ====================================================
goto :end

:error_extract
echo.
echo [ERROR] Audio extraction failed. Code: %ERRORLEVEL%
goto :end

:error_transcribe
echo.
echo [ERROR] Audio transcription failed. Code: %ERRORLEVEL%
goto :end

:end
pause
