@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

echo ====================================================
echo   Pipeline de Extracao e Transcricao de Audio
echo ====================================================
echo.

:: Ativar o ambiente virtual .venv se existir
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Ativando ambiente virtual .venv...
    call ".venv\Scripts\activate.bat"
) else (
    echo [AVISO] Ambiente virtual .venv nao encontrado. Usando Python padrao...
)

echo.
echo ====================================================
echo [1/2] Executando audio_extract.py...
echo ====================================================
python audio_extract.py
if errorlevel 1 goto :error_extract

echo.
echo ====================================================
echo [2/2] Executando transcribe.py...
echo ====================================================
python transcribe.py %*
if errorlevel 1 goto :error_transcribe

echo.
echo ====================================================
echo Processo concluido com sucesso!
echo ====================================================
goto :end

:error_extract
echo.
echo [ERRO] Falha na extracao de audio. Codigo: %ERRORLEVEL%
goto :end

:error_transcribe
echo.
echo [ERRO] Falha na transcricao do audio. Codigo: %ERRORLEVEL%
goto :end

:end
pause
