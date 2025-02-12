import pandas as pd
import os
import sys
from pathlib import Path
username = os.getlogin()
Baseurl = rf'C:\Users'
FileName = 'ClinicalTrialExecute.py'
def FindFile(Baseurl, FileName):
    GetPath = Path(Baseurl)
    for file in GetPath.rglob(FileName):
        if file:
            return file
    return None 
PathToFile = FindFile(Baseurl, FileName)

if PathToFile:
    ParentPath = PathToFile.parent
    if str(ParentPath) not in sys.path:
        sys.path.append(str(ParentPath))
    try:
        from ClinicalTrialExecute import ClinicalTrialExecute
        ProspectCommercial = ClinicalTrialExecute.fetch()
        if ProspectCommercial and isinstance(ProspectCommercial, dict):
            locals().update(ProspectCommercial)
        else:
            print("fetch() did not return a dictionary or returned None.")
    except ImportError as e:
        print(f"Import error: {e}")
    except AttributeError as e:
        print(f"Attribute error: {e}")
else:
    print("File not found.")
