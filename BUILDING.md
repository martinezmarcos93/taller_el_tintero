# Guía de Build e Instalador — El Tintero

## Requisitos previos

Instalar una sola vez en la máquina de desarrollo:

- **Python 3.10+** con "Add to PATH" marcado → https://python.org
- **Inno Setup 6** → https://jrsoftware.org/isdl.php
- Las fuentes **Cormorant Garamond** y **Nunito** instaladas en Windows (opcional)

---

## Paso 1 — Compilar el .exe

Doble clic en `build.bat`.

El script hace automáticamente:
1. Verifica Python
2. Instala/actualiza `customtkinter`, `pillow` y `pyinstaller`
3. Genera `assets/icono.ico` desde el logo del tintero
4. Limpia builds anteriores
5. Compila con PyInstaller usando `tintero.spec`
6. Copia el README al directorio de distribución
7. Abre `dist\ElTintero\` en el Explorador

**Resultado:** `dist\ElTintero\ElTintero.exe` listo para ejecutar.

---

## Paso 2 — Generar el instalador

1. Abrí **Inno Setup Compiler**
2. Menú `File → Open` → seleccioná `installer.iss`
3. Presioná `F9` o `Build → Compile`
4. El instalador se genera en `installer_output\ElTintero_Setup_v1.0.0.exe`

---

## Estructura después del build

```
📁 tu_carpeta/
│
├── build.bat
├── tintero.spec
├── installer.iss
├── version_info.txt
│
├── 📁 dist/
│   └── 📁 ElTintero/           ← carpeta distribuible
│       ├── ElTintero.exe
│       ├── README.md
│       └── (dlls y dependencias de Python)
│
└── 📁 installer_output/
    └── ElTintero_Setup_v1.0.0.exe  ← instalador final
```

---

## Dónde guarda los datos el .exe instalado

| Archivo | Ubicación |
|---|---|
| `tintero.db` | Junto al `.exe` (primera ejecución) |
| `tintero_config.json` | Junto al `.exe` (primera ejecución) |

> El instalador **no incluye** estos archivos. Se crean la primera vez que el usuario abre el programa, en la carpeta de instalación. Esto permite que cada usuario tenga su propia base de datos independiente.

---

## Solución de problemas comunes

**"pyinstaller no se reconoce como comando"**
Cerrá y volvé a abrir el CMD/PowerShell después de instalar Python.

**El .exe abre y cierra inmediatamente**
Abrí un CMD, navegá hasta `dist\ElTintero\` y ejecutá `ElTintero.exe` desde ahí para ver el error en consola. Probablemente falte un archivo en la carpeta `assets\`.

**El instalador dice que falta `Spanish.isl`**
Inno Setup no tiene el idioma español instalado. Descargalo desde https://jrsoftware.org/files/istrans/ y copialo a `C:\Program Files (x86)\Inno Setup 6\Languages\`

**El ícono no aparece en el .exe**
Verificá que `assets\icono.ico` exista. El `build.bat` lo genera automáticamente desde el logo PNG.

**Antivirus bloquea el instalador**
Es normal con ejecutables nuevos sin firma de código. Para firmarlo digitalmente necesitás un certificado de Code Signing (Comodo, DigiCert, etc.). Para uso interno/personal podés ignorar la advertencia.
