#define MyAppName "Promptlocker"
#define MyAppVersion "0.0.3"
#define MyAppPublisher "etherealxx"
#define MyAppURL "https://github.com/etherealxx/promptlocker/"
#define MyAppExeName "promptlocker.exe"
#define MyAppIcoName "promptlockericon.ico"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{F11A9263-7515-42AA-93A0-7B6C285E7468}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
OutputBaseFilename=promptlocker-installer
OutputDir=""
SolidCompression=yes
WizardStyle=modern
Compression=lzma2/ultra64
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576
LZMANumFastBytes=273
SetupIconFile=""
;SignTool=MSSignTool2 $f
;SignToolRetryCount=10
;SignToolRetryDelay=1000

; SignTool=MSSignTool $f
; SignTool=signtool.exe sign /a /tr http://timestamp.sectigo.com /td SHA256 /fd SHA256 $f

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: {app}\{#MyAppIcoName}; Comment: "Lock prompt in png with password";
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: {app}\{#MyAppIcoName}; Comment: "Lock prompt in png with password"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

