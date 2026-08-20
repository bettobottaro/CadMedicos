@echo off
set "APP_DIR=%~dp0"

if exist "%APP_DIR%CadMedicos.exe" (
    start "" "%APP_DIR%CadMedicos.exe"
    exit /b 0
)

if exist "%APP_DIR%dist\CadMedicos.exe" (
    start "" "%APP_DIR%dist\CadMedicos.exe"
    exit /b 0
)

echo Arquivo CadMedicos.exe nao encontrado na pasta do projeto.
pause
