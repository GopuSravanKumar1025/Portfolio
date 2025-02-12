import sys
from pathlib import Path
import os

username = os.getlogin()
Baseurl = rf'C:\Users\{username}'
FileName = 'clockify.py'
def FindFile(Baseurl, FileName):
    GetPath = Path(Baseurl)
    for file in GetPath.rglob(FileName):
        if file:
            return file
        else:
            return None
PathToFile = FindFile(Baseurl, FileName)
if PathToFile:
    ParentPath = PathToFile.parent
    if ParentPath not in sys.path:
        sys.path.append(str(ParentPath))
    from PowerBi import PowerBi
    PowerBI = PowerBi.PowerBi()
    locals().update(PowerBI)
else:
    print("File not found.")
