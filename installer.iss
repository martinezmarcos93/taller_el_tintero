; =====================================================
; EL TINTERO — INSTALADOR BASE ESTABLE
; =====================================================

#define MyAppName "El Tintero"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Norte Copywriting Solutions"
#define MyAppExeName "ElTintero.exe"

; =====================================================
; SETUP
; =====================================================

[Setup]

AppId={{8F4E8F2E-6E0A-4E5D-9D2F-ELTINTERO001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

OutputDir=Output
OutputBaseFilename=Instalador_ElTintero

Compression=lzma
SolidCompression=yes

WizardStyle=modern
DisableProgramGroupPage=yes

UninstallDisplayIcon={app}\{#MyAppExeName}

; =====================================================
; ARCHIVOS
; =====================================================

[Files]

Source: "dist\ElTintero.exe"; DestDir: "{app}"; Flags: ignoreversion

; Si estas carpetas no existen, comentarlas
;Source: "dist\data\*"; DestDir: "{app}\data"; Flags: recursesubdirs createallsubdirs ignoreversion
;Source: "dist\resources\*"; DestDir: "{app}\resources"; Flags: recursesubdirs createallsubdirs ignoreversion

; =====================================================
; ICONOS
; =====================================================

[Icons]

[Icons]

Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; =====================================================
; TAREAS
; =====================================================


[Tasks]

Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones adicionales:"
; =====================================================
; EJECUCIÓN FINAL
; =====================================================

[Run]

Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName}"; Flags: nowait postinstall skipifsilent

; =====================================================
; CÓDIGO
; =====================================================

[Code]

function InitializeSetup(): Boolean;
begin
  Result := True;
end;


procedure InitializeWizard();
begin

  WizardForm.WelcomeLabel1.Caption :=
    'Bienvenido a El Tintero';

  WizardForm.WelcomeLabel2.Caption :=

    'Este asistente va a instalar El Tintero ' +
    ExpandConstant('{#MyAppVersion}') +
    ' en tu computadora.' + #13#10 +

    ' ' + #13#10 +

    'El Tintero es un sistema de gestión para el Taller Literario.' + #13#10 +

    'Incluye módulos para alumnos, cuentas corrientes,' + #13#10 +

    'producciones literarias y agenda.' + #13#10 +

    ' ' + #13#10 +

    'Se recomienda cerrar otras aplicaciones antes de continuar.' + #13#10 +

    ' ' + #13#10 +

    'Hacé clic en Siguiente para continuar.';

end;


function InitializeUninstall(): Boolean;
begin

  Result :=
    MsgBox(

      'Estás por desinstalar El Tintero.' + #13#10 +

      ' ' + #13#10 +

      'Tus datos se conservarán en la carpeta de usuario.' + #13#10 +

      ' ' + #13#10 +

      '¿Querés continuar con la desinstalación?',

      mbConfirmation,
      MB_YESNO

    ) = IDYES;

end;