@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║     El Tintero — Build Script v1.0           ║
echo  ║     Compilando ejecutable Windows...         ║
echo  ╚══════════════════════════════════════════════╝
echo.

:: ── Verificar Python ─────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python no encontrado en el PATH.
    echo  Instalalo desde https://python.org y asegurate de marcar
    echo  "Add Python to PATH" durante la instalacion.
    pause & exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% detectado.

:: ── Verificar dependencias ────────────────────────────────────────
echo.
echo  [1/5] Verificando e instalando dependencias...
pip install --quiet --upgrade customtkinter pillow pyinstaller
if errorlevel 1 (
    echo  [ERROR] No se pudieron instalar las dependencias.
    pause & exit /b 1
)
echo  [OK] Dependencias listas.

:: ── Generar ícono desde el logo ──────────────────────────────────
echo.
echo  [2/5] Generando icono .ico desde el logo...

python -c "
from PIL import Image
from pathlib import Path
import sys

logo_path = Path('assets/Imagotipo_Space_CadetAmarillo_Hunyadi_con_tinta.png')
if not logo_path.exists():
    logo_path = Path('assets/El_Tintero.png')

if logo_path.exists():
    img = Image.open(logo_path).convert('RGBA')
    sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
    imgs  = [img.resize(s, Image.LANCZOS) for s in sizes]
    Path('assets').mkdir(exist_ok=True)
    imgs[0].save('assets/icono.ico', format='ICO', sizes=sizes, append_images=imgs[1:])
    print('[OK] assets/icono.ico generado.')
else:
    print('[WARN] Logo no encontrado. El exe no tendra icono personalizado.')
    # Crear un .ico vacío para que el spec no falle
    img = Image.new('RGBA', (256,256), (28,34,58,255))
    img.save('assets/icono.ico', format='ICO')
" 2>nul
if errorlevel 1 (
    echo  [WARN] No se pudo generar el icono. Continuando sin el.
    echo. > assets\icono.ico
)

:: ── Limpiar builds anteriores ────────────────────────────────────
echo.
echo  [3/5] Limpiando builds anteriores...
if exist "dist\ElTintero" rmdir /s /q "dist\ElTintero"
if exist "build\ElTintero" rmdir /s /q "build\ElTintero"
echo  [OK] Limpieza completada.

:: ── Compilar con PyInstaller ─────────────────────────────────────
echo.
echo  [4/5] Compilando con PyInstaller (puede tardar 1-3 minutos)...
echo.
pyinstaller tintero.spec --noconfirm --clean
if errorlevel 1 (
    echo.
    echo  [ERROR] La compilacion fallo. Revisa los mensajes de arriba.
    pause & exit /b 1
)

:: ── Verificar resultado ───────────────────────────────────────────
if not exist "dist\ElTintero\ElTintero.exe" (
    echo.
    echo  [ERROR] No se encontro el .exe generado en dist\ElTintero\
    pause & exit /b 1
)

:: ── Copiar archivos necesarios al dist ───────────────────────────
echo.
echo  [5/5] Preparando carpeta de distribucion...

:: El .db y el config NO se incluyen — se generan en primer uso
:: El README sí se incluye como referencia
if exist "README.md" copy /y "README.md" "dist\ElTintero\README.md" >nul

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║   BUILD EXITOSO                              ║
echo  ╚══════════════════════════════════════════════╝
echo.
echo  Ejecutable generado en:
echo  dist\ElTintero\ElTintero.exe
echo.
echo  Para distribuir, usa el script installer.iss con Inno Setup,
echo  o comprimí la carpeta dist\ElTintero\ en un .zip.
echo.

:: Abrir la carpeta de salida
explorer "dist\ElTintero"

pause
