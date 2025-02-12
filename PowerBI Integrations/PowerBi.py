from Clockify import Clockify
from encrypt import decrypt
import pandas as pd
import json
import os
import string

class PowerBi:
    @staticmethod #3rd
    def get_drives():
        available_drives = []
        for drive in string.ascii_uppercase:
            if os.path.exists(f"{drive}:\\"):
                available_drives.append(f"{drive}:\\")
        return available_drives
    @staticmethod #2nd
    def SearchFile(fileName):
        result = []
        drives = PowerBi.get_drives()
        for drive in drives:
            for root, dirs, files in os.walk(drive):
                for file in files:
                    if file.lower() == fileName.lower():
                        result.append(os.path.join(root, file))
        return result
    @staticmethod #1st
    def PowerBi(dataframes = {}):
        fileName = 'OAuth.json'
        searchFile = PowerBi.SearchFile(fileName)
        with open(searchFile[0], 'r') as file:
            Credentials = json.load(file)
        ClockifyData = Clockify.fetch(Credentials)
        Decrypted = decrypt.inData(ClockifyData)
        for key in Decrypted:
            for group in Decrypted[key]:
                dataframes[group] = pd.DataFrame(Decrypted[key][group])
        return dataframes