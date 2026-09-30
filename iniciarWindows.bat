@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Criando o ambiente virtual...
    py -m venv .venv
    if errorlevel 1 goto erro
)

echo Instalando ou atualizando as dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto erro

echo Iniciando o site em http://localhost:5000
".venv\Scripts\python.exe" app.py
pause
exit /b 0

:erro
echo.
echo Nao foi possivel preparar ou iniciar o projeto.
echo Confira se o Python esta instalado e disponivel pelo comando py.
pause
exit /b 1