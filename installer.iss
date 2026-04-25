; ══════════════════════════════════════════════════════════════════
; installer.iss — Script de Inno Setup para El Tintero
; ══════════════════════════════════════════════════════════════════
;
; REQUISITOS:
;   - Haber ejecutado build.bat exitosamente primero
;   - Tener Inno Setup instalado: https://jrsoftware.org/isdl.php
;
; PARA COMPILAR EL INSTALADOR:
;   Abrí este archivo en Inno Setup y presioná F9,
;   o ejecutá: iscc installer.iss
;
; ══════════════════════════════════════════════════════════════════

#define MyAppName        "El Tintero"
#define MyAppVersion     "1.0.0"
#define MyAppPublisher   "El Tintero — Taller Literario"
#define MyAppURL         ""
#define MyAppExeName     "ElTintero.exe"
#define MyAppDescription "Sistema de gestión para taller literario y copywriting"
#define SourceDir        "dist\ElTintero"
#define OutputDir        "installer_output"

[Setup]
; ── Identidad ────────────────────────────────────────────────────
AppId={{A4F2C8D1-3B7E-4F91-9C2A-6E8D5F047B30}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=© 2025 El Tintero

; ── Rutas ─────────────────────────────────────────────────────────
DefaultDirName={autopf}\ElTintero
DefaultGroupName={#MyAppName}
OutputDir={#OutputDir}
OutputBaseFilename=ElTintero_Setup_v{#MyAppVersion}
SetupIconFile=assets\icono.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; ── Estética del wizard ───────────────────────────────────────────
; Imagen izquierda del wizard (164x314 px, BMP o JPEG)
; WizardImageFile=assets\wizard_banner.bmp
; Imagen pequeña arriba derecha (55x55 px)
; WizardSmallImageFile=assets\wizard_icon.bmp

WizardStyle=modern
WizardSizePercent=120

; ── Compresión ────────────────────────────────────────────────────
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4

; ── Comportamiento ────────────────────────────────────────────────
PrivilegesRequired=lowest          ; No requiere admin — instala en AppData si es necesario
PrivilegesRequiredOverridesAllowed=dialog
AllowNoIcons=yes
DisableProgramGroupPage=yes        ; No pregunta grupo del menú inicio
DisableWelcomePage=no
DisableReadyPage=no
CreateUninstallRegKey=yes
ChangesAssociations=no
ArchitecturesInstallIn64BitMode=x64compatible

; ── Metadatos del instalador ──────────────────────────────────────
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
; Español primero, inglés como fallback
Name: "spanish";  MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english";  MessagesFile: "compiler:Default.isl"

[Tasks]
; Opciones que el usuario puede elegir durante la instalación
Name: "desktopicon";    Description: "Crear acceso directo en el Escritorio";      GroupDescription: "Accesos directos:"; Flags: unchecked
Name: "startmenuicon";  Description: "Crear acceso directo en el Menú Inicio";     GroupDescription: "Accesos directos:"; Flags: checkedonce
Name: "launchafter";    Description: "Iniciar {#MyAppName} al terminar la instalación"; GroupDescription: "Al finalizar:"; Flags: checkedonce

[Files]
; ── Aplicación principal ─────────────────────────────────────────
Source: "{#SourceDir}\*";         DestDir: "{app}";              Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md";              DestDir: "{app}";              Flags: ignoreversion; Check: FileExists('README.md')

; ── NOTA: tintero.db y tintero_config.json NO se incluyen ────────
;    Se crean automáticamente en primer uso dentro de la carpeta
;    de datos del usuario, no en Program Files.

[Dirs]
; Directorio de datos del usuario (donde se guardan DB y config)
Name: "{userappdata}\ElTintero";  Flags: uninsneveruninstall

[Icons]
; Acceso directo Menú Inicio
Name: "{group}\{#MyAppName}";                      Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon
Name: "{group}\Desinstalar {#MyAppName}";           Filename: "{uninstallexe}"

; Acceso directo Escritorio
Name: "{autodesktop}\{#MyAppName}";                Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Lanzar la app al finalizar (si el usuario marcó la opción)
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName}"; Flags: nowait postinstall skipifsilent; Tasks: launchafter

[UninstallRun]
; Nada especial al desinstalar

[UninstallDelete]
; Borrar archivos generados por la app al desinstalar
; NOTA: los datos del usuario en {userappdata}\ElTintero se conservan
; para no borrar la base de datos accidentalmente.
; Si querés borrarlos también, descomentá las líneas siguientes:
; Type: filesandordirs; Name: "{userappdata}\ElTintero"

[Code]
// ══════════════════════════════════════════════════════════════════
// Código Pascal personalizado para el wizard
// ══════════════════════════════════════════════════════════════════

// Verifica si ya existe una instalación previa y avisa al usuario
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

// Página de bienvenida personalizada
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel1.Caption := 'Bienvenido a El Tintero';
  WizardForm.WelcomeLabel2.Caption :=
    'Este asistente va a instalar El Tintero ' + '{#MyAppVersion}' + ' en tu computadora.' + #13#10 +
    #13#10 +
    'El Tintero es un sistema de gestión para el Taller Literario y ' +
    'Norte Copywriting Solutions. Incluye módulos para alumnos, ' +
    'cuentas corrientes, producciones literarias, agenda y más.' + #13#10 +
    #13#10 +
    'Se recomienda cerrar otras aplicaciones antes de continuar.' + #13#10 +
    #13#10 +
    'Hacé clic en Siguiente para continuar.';
end;

// Mensaje al finalizar
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssDone then
  begin
    // Aquí podrías abrir el README o mostrar un mensaje final
  end;
end;

// Confirmación antes de desinstalar
function InitializeUninstall(): Boolean;
begin
  Result := MsgBox(
    'Estás por desinstalar El Tintero.' + #13#10 +
    #13#10 +
    'Tus datos (base de datos y configuración) se conservarán ' +
    'en la carpeta de usuario.' + #13#10 +
    #13#10 +
    '¿Querés continuar con la desinstalación?',
    mbConfirmation,
    MB_YESNO
  ) = IDYES;
end;
