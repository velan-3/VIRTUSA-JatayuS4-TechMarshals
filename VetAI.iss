; Script generated for Veterinary Assistant with DroidCam support

[Setup]
AppName=Veterinary Assistant
AppVersion=1.0
DefaultDirName={pf}\VeterinaryAssistant
DefaultGroupName=Veterinary Assistant
UninstallDisplayIcon={app}\VeterinaryAssistant.exe
OutputBaseFilename=VeterinaryAssistant_Installer
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
SetupIconFile=C:\Users\Velan\Downloads\cow.ico
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Main application files
Source: "D:\virtusaa\VeterinaryAssistant\build\exe.win-amd64-3.10\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

; Optionally include DroidCam installer (you can download EXE from Dev47Apps)
//Source: "D:\virtusaa\VeterinaryAssistant\build\exe.win-amd64-3.10\DroidCam.Setup.6.5.exe"; DestDir: "{app}\DroidCam"; Flags: ignoreversion

[Icons]
Name: "{group}\Veterinary Assistant"; Filename: "{app}\VeterinaryAssistant.exe"
Name: "{group}\Uninstall Veterinary Assistant"; Filename: "{uninstallexe}"

[Run]
; Launch DroidCam installer (optional - can be skipped by user)
//Filename: "{app}\DroidCam\DroidCam.Setup.6.5.exe"; Description: "Install DroidCam Client (requires admin rights)"; Flags: postinstall skipifsilent shellexec waituntilterminated; Verb: runas

; Launch the app after install


[InstallDelete]
; Clean temporary directories if needed (optional)
