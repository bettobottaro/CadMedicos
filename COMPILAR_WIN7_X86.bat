@echo off
setlocal
cd /d "%~dp0"
title CadMedicos - Python 3.8 x86

echo ============================================================
echo CADMEDICOS - COMPILACAO WINDOWS 7 x86
echo ============================================================

set "PY=python"
%PY% --version >nul 2>&1
if errorlevel 1 goto NO_PY
%PY% -c "import sys,struct; raise SystemExit(0 if sys.version_info[:2]==(3,8) and struct.calcsize('P')*8==32 else 1)" >nul 2>&1
if errorlevel 1 goto BAD_PY

if not exist ".venv\Scripts\python.exe" (
  %PY% -m venv .venv
  if errorlevel 1 goto VENV_ERR
)

set "PY=.venv\Scripts\python.exe"
%PY% -m pip install "pip<24.1" "setuptools<70" wheel
if errorlevel 1 goto PIP_ERR
%PY% -m pip install -r requirements.txt
if errorlevel 1 goto REQ_ERR
%PY% -m pip install "pyinstaller==5.13.2"
if errorlevel 1 goto PI_ERR

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist CadMedicos.spec del /q CadMedicos.spec

%PY% -m PyInstaller --clean --noconfirm --onefile --windowed --name CadMedicos main.py
if errorlevel 1 goto BUILD_ERR

if not exist data mkdir data
if exist "data" xcopy /E /I /Y data dist\data >nul

echo.
echo ============================================================
echo SUCESSO: dist\CadMedicos.exe
echo ============================================================
pause
exit /b 0

:NO_PY
echo Python nao encontrado.
pause
exit /b 1
:BAD_PY
echo Necessario Python 3.8 x86 (32 bits).
pause
exit /b 1
:VENV_ERR
echo Falha ao criar ambiente virtual.
pause
exit /b 1
:PIP_ERR
echo Falha ao preparar pip.
pause
exit /b 1
:REQ_ERR
echo Falha ao instalar requirements.txt.
pause
exit /b 1
:PI_ERR
echo Falha ao instalar PyInstaller.
pause
exit /b 1
:BUILD_ERR
echo Falha na compilacao.
pause
exit /b 1
