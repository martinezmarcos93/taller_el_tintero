@echo off
title Build El Tintero

echo ========================================
echo  Build El Tintero (sin icono)
echo ========================================
echo.

:: 1. Verificar Python
echo [1/3] Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no instalado
    pause
    exit /b 1
)
echo.

:: 2. Asegurar dependencias
echo [2/3] Instalando dependencias...
python -m pip install --upgrade pip >nul
python -m pip install customtkinter pillow pyinstaller
if errorlevel 1 (
    echo ERROR: Fallo instalacion
    pause
    exit /b 1
)
echo.

:: 3. Compilar SIN ICONO (sin --icon, sin espec)
echo [3/3] Compilando ejecutable...
python -m PyInstaller --onefile --windowed --name ElTintero --add-data "assets;assets" tintero_app.py

if errorlevel 1 (
    echo ERROR: Fallo la compilacion
    pause
    exit /b 1
)

:: Resultado
echo.
if exist "dist\ElTintero.exe" (
    echo ========================================
    echo EXITO! Ejecutable: dist\ElTintero.exe
    echo ========================================
    explorer /select, "dist\ElTintero.exe"
) else (
    echo ERROR: No se genero el .exe
)

echo.
pause