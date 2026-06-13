@echo off
title Garry's Mod - Black Mesa Auto-Mounter
echo Verificando se o Python está instalado...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Erro] Python não está instalado ou não está no PATH do Windows.
    echo Baixe e instale o Python em: https://www.python.org/
    echo Certifique-se de marcar a opção "Add Python to PATH" durante a instalação.
    pause
    exit /b
)
python "%~dp0automate_mount.py"
pause
