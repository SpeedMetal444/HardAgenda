[Setup]
AppName=HardAgenda
AppVersion=1.0.0
AppPublisher=Abel Godoy
DefaultDirName={autopf}\HardAgenda
DefaultGroupName=HardAgenda
OutputDir=installer_output
OutputBaseFilename=HardAgenda_Setup_V1.0.0
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

[Code]
var
  SerialPage: TInputQueryWizardPage;

const
  MASTER_SERIAL = 'HARD-MAST-ERK2026';

function GenerateHWFingerprint(): String;
var
  ResultCode: Integer;
  TempFile, Line, CPUID, DiskSN: String;
  SL: TStringList;
  i: Integer;
begin
  CPUID := '';
  DiskSN := '';
  TempFile := ExpandConstant('{tmp}\hwinfo.txt');

  Exec('cmd', '/c wmic cpu get ProcessorId > "' + TempFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  SL := TStringList.Create;
  try
    if FileExists(TempFile) then
    begin
      SL.LoadFromFile(TempFile);
      for i := 0 to SL.Count - 1 do
      begin
        Line := Trim(SL[i]);
        if (Pos('ProcessorId', Line) > 0) and (Pos('=', Line) > 0) then
        begin
          CPUID := Trim(Copy(Line, Pos('=', Line) + 1, Length(Line)));
          if CPUID <> '' then Break;
        end;
      end;
    end;
  finally
    SL.Free;
  end;

  Exec('cmd', '/c wmic diskdrive get SerialNumber > "' + TempFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  SL := TStringList.Create;
  try
    if FileExists(TempFile) then
    begin
      SL.LoadFromFile(TempFile);
      for i := 0 to SL.Count - 1 do
      begin
        Line := Trim(SL[i]);
        if (Pos('SerialNumber', Line) > 0) and (Pos('=', Line) > 0) then
        begin
          DiskSN := Trim(Copy(Line, Pos('=', Line) + 1, Length(Line)));
          if DiskSN <> '' then Break;
        end;
      end;
    end;
  finally
    SL.Free;
  end;

  if CPUID = '' then CPUID := 'DEFAULT';
  if DiskSN = '' then DiskSN := 'DEFAULT';
  Result := CPUID + '-' + DiskSN;
end;

function IsSerialValid(Serial: String): Boolean;
begin
  Result := False;
  if Serial = MASTER_SERIAL then
  begin
    Result := True;
    Exit;
  end;
  if Length(Serial) = 14 then
  begin
    if (Serial[5] = '-') and (Serial[10] = '-') then
      Result := True;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Serial: String;
begin
  Result := True;
  if CurPageID = SerialPage.ID then
  begin
    Serial := SerialPage.Values[0];
    if Trim(Serial) = '' then
    begin
      MsgBox('Debe ingresar un serial de activacion.', mbError, MB_OK);
      Result := False;
      Exit;
    end;
    if not IsSerialValid(Serial) then
    begin
      MsgBox('El serial ingresado no es valido.' + #13#10 + #13#10 + 'ID de PC: ' + GenerateHWFingerprint(), mbError, MB_OK);
      Result := False;
      Exit;
    end;
  end;
end;

procedure InitializeWizard;
var
  HW: String;
begin
  HW := GenerateHWFingerprint();
  SerialPage := CreateInputQueryPage(wpSelectDir, 'Activacion', 'Ingrese su serial de activacion para continuar.' + #13#10 + #13#10 + 'ID de PC: ' + HW, 'Serial:');
  SerialPage.Add('Serial de activacion:', False);
end;
