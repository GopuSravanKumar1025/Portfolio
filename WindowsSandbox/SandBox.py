import winsandbox
import rpyc
import os
from pathlib import Path
import subprocess

username = os.getlogin()
rpyc.core.protocol.DEFAULT_CONFIG['sync_request_timeout'] = 800
FileName = 'FileName'
LocalDownloadFile = Path(f"C:/Users/{username}/Downloads")
DBPath = Path(r'Path to Database')
ScriptBase = r'Path to winsandbox envi Database.js'
NodePath = r'C:\Program Files\nodejs\node.exe'
script_path = r'" path to WindowsPowerShell\Scripts\winget-install.ps1"'
MSIPath = r'your msi folder'


def error(fileError):
    print(f"Error: The file '{fileError}' does not exist.")
    return
if not LocalDownloadFile.exists():
    error(LocalDownloadFile)
if not DBPath.exists():
    error(DBPath)

Downloadsmapper = winsandbox.FolderMapper(folder_path=LocalDownloadFile, read_only=False)
DbMapper = winsandbox.FolderMapper(folder_path=DBPath, read_only=False)
sandbox = winsandbox.new_sandbox(networking=True, folder_mappers=[Downloadsmapper, DbMapper])
WingetCommands = [
    "Install-PackageProvider -Name NuGet -Force -Scope CurrentUser",
    "Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted",
    "Install-Script winget-install -Force -Confirm:$false",
    f"-ExecutionPolicy Bypass -File {script_path}",
    "winget install --id Google.Chrome --accept-package-agreements --accept-source-agreements",
    "winget install Python.Python.3.13 --accept-package-agreements --accept-source-agreements",
    "winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements",
    "winget install Microsoft.DotNet.SDK.9 --accept-package-agreements --accept-source-agreements",
    "winget install Microsoft.VCRedist.2015+.x64 --accept-package-agreements --accept-source-agreements",
    "winget install DBBrowserForSQLite.DBBrowserForSQLite --accept-package-agreements --accept-source-agreements",
    f'msiexec /i {MSIPath} /quiet /norestart',
    f'&"{NodePath}" "{ScriptBase}"'
    f'msiexec /x {MSIPath} /quiet /norestart'
]

for command in WingetCommands:
    print(f"Executing Command: {command}")
    result = sandbox.rpyc.modules.subprocess.run(f"Powershell {command}", shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Error:", result.stderr)