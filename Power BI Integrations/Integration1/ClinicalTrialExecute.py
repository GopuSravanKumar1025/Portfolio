import pandas as pd
import os
import sys
from pathlib import Path

class ClinicalTrialExecute:
    def fetch():
        username = os.getlogin()
        Baseurl = rf'C:\Users'
        FileName = 'ProspectCommercial.py'
        def FindFile(Baseurl, FileName):
            GetPath = Path(Baseurl)
            for file in GetPath.rglob(FileName):
                return file
            return None
        PathToFile = FindFile(Baseurl, FileName)
        if PathToFile:
            ParentPath = PathToFile.parent
            if str(ParentPath) not in sys.path:
                sys.path.append(str(ParentPath))
            try:
                from ProspectCommercial import ClinicalTrial
                from Outcomemeasures import OutcomeMeasures
                ClinicalData = ClinicalTrial.fetchData()
                _OutComeMeasures = OutcomeMeasures.fetchData()
            except ImportError as e:
                print(f"ImportError: {e}")
                from ProspectCommercial import ClinicalTrial
                ClinicalData = ClinicalTrial.fetchData()
            CustomerTrials = pd.DataFrame(ClinicalData['CustomersRawData'])
            ProspectsTrials = pd.DataFrame(ClinicalData['ProspectsRawData'])
            CustomersLinks = pd.DataFrame(ClinicalData['CustomersLink'])
            ProspectsLinks = pd.DataFrame(ClinicalData['ProspectsLink'])
            OutComeMeasures_ = pd.DataFrame(_OutComeMeasures['OutComeMeasures'])
            return {
                'CustomerTrials': CustomerTrials,
                'ProspectsTrials': ProspectsTrials,
                'CustomersNews': CustomersLinks,
                'ProspectsNews': ProspectsLinks,
                'OutComeMeasures' : OutComeMeasures_
            }
        else:
            print("File not found.")