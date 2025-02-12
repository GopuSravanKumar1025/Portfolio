import requests
import re
from forex_python.converter import Symbols
from encrypt import Encrypt


class SharePoint():
    #Generalization for symbols which calls by FormatData
    def is_numeric(value):
        value = value.strip().replace(',', '')
        return re.match(r'^-?\d+(\.\d+)?$', value) is not None
    #5th
    def FormatData(GetSheetData, DataCurrency):
        Mainheaders, Datarows = GetSheetData["text"][0], GetSheetData["text"][1:]
        ConciseData = []
        for mainRow in Datarows:
            if any(mainRow):
                ConciseRow = {}
                for header, value in zip(Mainheaders, mainRow):
                    Stripvalue = value.strip()
                    for symbol in DataCurrency.values():
                        if header.startswith((" Total Contract Value ", " Invoiced to Date", "Difference to Invoice", " Invoiced to date", ' NB TCV ')):
                            cleaned_value = re.sub(r'[^\d.-]', '', Stripvalue)
                            #mainvalue = cleaned_value
                            if SharePoint.is_numeric(cleaned_value):
                                if ".00" in  cleaned_value:
                                    ConciseRow[header] = int(float(cleaned_value.replace(".00", "")))
                                else:
                                    ConciseRow[header] = int(float(cleaned_value))
                            else:
                                ConciseRow[header] = None if cleaned_value == "$-" else cleaned_value 
                        else:
                            ConciseRow[header] = Stripvalue
                ConciseData.append(ConciseRow)
        return ConciseData
    @staticmethod #5th
    def SheetData(SheetName, File_Name, siteid, headers, RangeAddress):
        SheetUrl = f'https://graph.microsoft.com/v1.0/sites/{siteid}/drive/root:/General/Dashboards/Data%20Source/scripts/Core_Labs/{File_Name}:/workbook/worksheets(' + "'" + f'{SheetName}' + "'" + f')/range(address=' + "'" + f'{RangeAddress}' + "'" + f')?valueFormat=text'
        response = requests.get(SheetUrl, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve data from sheet {SheetName}: {response.status_code} {response.text}")
    @staticmethod #4th
    def SheetNames(File_Name, siteid, headers, SheetKeywords):
        NameUrl = f'https://graph.microsoft.com/v1.0/sites/{siteid}/drive/root:/General/Dashboards/Data%20Source/scripts/Core_Labs/{File_Name}:/workbook/worksheets'
        response = requests.get(NameUrl, headers=headers)
        if response.status_code == 200:
            SheetNames = []
            sheets = response.json().get('value', [])
            for sheet in sheets:
                for keyword in SheetKeywords:
                    if sheet['name'].startswith(keyword):
                        SheetNames.append(sheet['name'])
            return SheetNames
        raise Exception("Failed to retrieve sheet names.")
    @staticmethod #3rd
    def FileName(siteid, filekeyword, headers):
        ExtractNameUrl = f'https://graph.microsoft.com/v1.0/sites/{siteid}/drive/root:/General/Dashboards/Data%20Source/scripts/Core_Labs:/children'
        response = requests.get(ExtractNameUrl, headers=headers)
        if response.status_code == 200:
            items = response.json().get('value', [])
            for item in items:
                if item['name'].startswith(filekeyword):
                    return item['name'].replace(" ", "%20")
        raise Exception("File not found. Please check if the file exists.")
    @staticmethod #2nd
    def AuthToken(client_id, client_secret, Resources, token_url):
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'resource': Resources
        }
        response = requests.post(token_url, data=token_data)
        if response.status_code == 200:
            auth_token = response.json()['access_token']
            return 'Bearer ' + auth_token
        else:
            raise Exception(f"Failed to get token: {response.text}")
    @staticmethod #1st
    def fetch(Credentials):
        tenant_id = Credentials['tenant_id']
        client_id = Credentials['client_id']
        client_secret = Credentials['client_secret']
        siteid = Credentials['siteid']
        filekeyword = Credentials['filekeyword']
        SheetKeywords = Credentials['SheetKeywords']
        RangeAddress = Credentials['RangeAddress']
        Resources = Credentials['resource']
        token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'
        auth_token = SharePoint.AuthToken(client_id, client_secret, Resources, token_url)
        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }
        DataCurrency = Symbols().currencySymbol()
        File_Name = SharePoint.FileName(siteid, filekeyword, headers)
        SheetNames = SharePoint.SheetNames(File_Name, siteid, headers, SheetKeywords)
        AllDataFrames = {}
        for SheetName in SheetNames:
            GetSheetData = SharePoint.SheetData(SheetName, File_Name, siteid, headers, RangeAddress)
            FormatData = SharePoint.FormatData(GetSheetData, DataCurrency)
            AllDataFrames[SheetName] = FormatData
        return AllDataFrames