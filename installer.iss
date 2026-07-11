[Setup]
AppName=HardAgenda
AppVersion=1.1.0
AppPublisher=Abel Godoy
DefaultDirName={autopf}\HardAgenda
DefaultGroupName=HardAgenda
OutputDir=installer_output
OutputBaseFilename=HardAgenda_Setup_V1.1.0
SetupIconFile=resources\HardAgenda.ico
UninstallDisplayIcon={app}\HardAgenda.exe
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
DisableDirPage=no
WizardStyle=modern

[Files]
Source: "dist\HardAgenda\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\HardAgenda"; Filename: "{app}\HardAgenda.exe"
Name: "{group}\Desinstalar HardAgenda"; Filename: "{uninstallexe}"
Name: "{autodesktop}\HardAgenda"; Filename: "{app}\HardAgenda.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones adicionales:"; Flags: checkedonce

[Run]
Filename: "{app}\HardAgenda.exe"; Description: "Iniciar HardAgenda"; Flags: nowait postinstall skipifsilent
