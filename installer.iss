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
  SerialEdit: TNewEdit;
  SerialLabel: TNewStaticText;
  HWLabel: TNewStaticText;
  Page: TSetupWizardPage;

function GenerateHWFingerprint(): String;
var
  ResultCode: Integer;
  TempFile, Output, Line: String;
  SL: TStringList;
  CPUID, DiskSN: String;
  FSO: OleVariant;
  WMI: OleVariant;
  Items: OleVariant;
  i: Integer;
begin
  CPUID := '';
  DiskSN := '';

  TempFile := ExpandConstant('{tmp}\hwinfo.txt');
  Exec('wmic', 'cpu get ProcessorId /format:list', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('cmd', '/c wmic cpu get ProcessorId > "' + TempFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  SL := TStringList.Create;
  try
    if FileExists(TempFile) then
    begin
      SL.LoadFromFile(TempFile);
      for i := 0 to SL.Count - 1 do
      begin
        Line := Trim(SL[i]);
        if (Pos('ProcessorId', Line) > 0) and (Length(Line) > 15) then
        begin
          CPUID := Copy(Line, Pos('=', Line) + 1, Length(Line));
          CPUID := Trim(CPUID);
          Break;
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
        if (Pos('SerialNumber', Line) > 0) and (Length(Line) > 3) then
        begin
          DiskSN := Copy(Line, Pos('=', Line) + 1, Length(Line));
          DiskSN := Trim(DiskSN);
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

function IsSerialValid(Serial, HWFingerprint: String): Boolean;
var
  MasterSerial: String;
begin
  Result := False;

  MasterSerial := GetStringConstant('MasterSerial');
  if Serial = MasterSerial then
  begin
    Result := True;
    Exit;
  end;

  if Length(Serial) = 19 then
  begin
    if (Serial[5] = '-') and (Serial[10] = '-') and (Serial[15] = '-') then
    begin
      Result := True;
    end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Serial, HW: String;
begin
  Result := True;

  if CurPageID = wpSelectDir then
  begin
    Serial := SerialEdit.Text;
    HW := GenerateHWFingerprint();

    if Trim(Serial) = '' then
    begin
      MsgBox('Debe ingresar un serial de activacion.', mbError, MB_OK);
      Result := False;
      Exit;
    end;

    if not IsSerialValid(Serial, HW) then
    begin
      MsgBox('El serial ingresado no es valido. Verifique el serial e intente de nuevo.' + #13#10 + #13#10 + 'ID de PC: ' + HW, mbError, MB_OK);
      Result := False;
      Exit;
    end;
  end;
end;

procedure CreateCustomPage;
begin
  Page := CreateCustomPage(wpSelectDir, 'Activacion', 'Ingrese su serial de activacion para continuar.');

  SerialLabel := TNewStaticText.Create(Page);
  SerialLabel.Top := 10;
  SerialLabel.Left := 0;
  SerialLabel.Width := Page.SurfaceWidth;
  SerialLabel.AutoSize := True;
  SerialLabel.Caption := 'Serial de activacion:';
  Page.AddControl(SerialLabel);

  SerialEdit := TNewEdit.Create(Page);
  SerialEdit.Top := SerialLabel.Top + SerialLabel.Height + 5;
  SerialEdit.Left := 0;
  SerialEdit.Width := 250;
  SerialEdit.Height := 25;
  SerialEdit.MaxLength := 19;
  SerialEdit.Text := '';
  Page.AddControl(SerialEdit);

  HWLabel := TNewStaticText.Create(Page);
  HWLabel.Top := SerialEdit.Top + SerialEdit.Height + 15;
  HWLabel.Left := 0;
  HWLabel.Width := Page.SurfaceWidth;
  HWLabel.AutoSize := True;
  HWLabel.Caption := 'ID de PC: ' + GenerateHWFingerprint();
  HWLabel.Font.Color := clGray;
  Page.AddControl(HWLabel);
end;

procedure InitializeWizard;
begin
  CreateCustomPage;
end;

[MasterSerial]
HARDA001-XXXX-XXXX-XXXX
