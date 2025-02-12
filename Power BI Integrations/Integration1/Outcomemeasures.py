import requests
import requests
import os
from pathlib import Path
import urllib.parse
from docx import Document
import re

class OutcomeMeasures:
    @staticmethod #4th part-2 integrated of part-1
    def ChangePlaceholders(NameOfEmail, Condition, Body, NCTID, Subject):
        Template = re.sub(r'\[Contact Name\]', NameOfEmail, Body)
        Template = re.sub(r'\[Condition\]', Condition, Template)
        SubjectTemplate = re.sub(r'\[Contact Name\]', NameOfEmail, Subject)
        SubjectTemplate = re.sub(r'\[NCT Number\]', NCTID, SubjectTemplate)
        return Template, SubjectTemplate
    @staticmethod #4th integrated part-2
    def EmailFormats(Get_Contact, Subject, Body, Condition, Get_NCTID):
        Get_Email = Get_Contact.get('centralContacts', '')
        if len(Get_Email) >= 0:
            for email in Get_Email:
                if 'email' in email:
                    EmailID = email['email']
                    NameOfEmail = email['name']
                    
                    BodyOfMail, subject = OutcomeMeasures.ChangePlaceholders(NameOfEmail, Condition, Body, Get_NCTID, Subject)
                    return EmailID, subject, BodyOfMail
                else:
                    continue
        return '', '', ''

    @staticmethod #4th integrated part-1
    def Find_CMR(Get_OutComeMeasures, Keyword):
        KeyWord = Keyword.lower()
        for array in ['primaryOutcomes', 'secondaryOutcomes', 'otherOutcomes']:
            outcomes = Get_OutComeMeasures.get(array, [])
            for entry in outcomes:
                measure = entry.get('measure', '').lower()
                description = entry.get('description', '').lower()
                if KeyWord in measure or KeyWord in description:
                    return measure, description
        return '', ''

    @staticmethod #4th
    def ExtractData(Request_url, Subject, Body, Keyword):
        AppendData = []
        pageSize = 100
        pageToken = None
        while True:
            if pageToken:
                url = f"{Request_url}&pageSize={pageSize}&pageToken={pageToken}"
            else:
                url = f"{Request_url}&pageSize={pageSize}"
            response = requests.get(url)
            if response.status_code == 200:
                studies = response.json()
                Get_Studies = studies.get('studies', [])
                for data in Get_Studies:
                    Get_ProtoSection = data.get('protocolSection', '')
                    Get_Identification = Get_ProtoSection.get('identificationModule', '')
                    Get_NCTID = Get_Identification.get('nctId', '')
                    Get_Condition = Get_ProtoSection.get('conditionsModule', '')
                    Condition = Get_Condition.get('conditions', [])[0] if Get_Condition.get('conditions') else ''
                    Get_OutComeMeasures = Get_ProtoSection.get('outcomesModule', '')
                    Get_Contact = Get_ProtoSection.get('contactsLocationsModule', '')
                    official_title = Get_Identification.get('officialTitle')
                    if Get_OutComeMeasures:
                        measure, description = OutcomeMeasures.Find_CMR(Get_OutComeMeasures, Keyword)
                    else:
                        measure, description = '', ''
                    body = {
                        'CompanyName': data['protocolSection']['identificationModule']['organization']['fullName'],
                        'NCTID': Get_NCTID,
                        'BriefTitle': data['protocolSection']['identificationModule']['briefTitle'],
                        'OfficialTitle': official_title,
                        'Status': data['protocolSection']['statusModule']['overallStatus'],
                        'Link': f'https://clinicaltrials.gov/study/{data["protocolSection"]["identificationModule"]["nctId"]}',
                        'Measure': measure,
                        'Description': description
                    }
                    if Get_Contact:
                        BCCmail = 'john.ahmed@mycardium.com'
                        email, subject, email_body = OutcomeMeasures.EmailFormats(Get_Contact, Subject, Body, Condition, Get_NCTID)
                        subject_encoded = urllib.parse.quote(subject)
                        body_encoded = urllib.parse.quote(email_body)
                        if '@' in email:
                            mailto_link = f"mailto:{email}?subject={subject_encoded}&body={body_encoded}&Bcc={BCCmail}"
                            body.update({"Email": f"{mailto_link}"})
                        else:
                            body.update({"Email": email})
                    AppendData.append(body)
                pageToken = studies.get('nextPageToken')
                if not pageToken:
                    break
            else:
                print(f"Request failed with status code {response.status_code}")
                break
        return AppendData

    @staticmethod #3rd
    def wordocument(WordDoc):
        subject = ""
        body = ""
        for i, para in enumerate(WordDoc.paragraphs):
            if i == 0:
                subject = para.text
            else:
                body += para.text + "\n\n"
        return subject, body
    @staticmethod #2nd
    def FindFile(Baseurl, fileName):
        GetPath = Path(Baseurl)
        for file in GetPath.rglob(fileName):
            if file:
                return file
            else:
                return None
    @staticmethod #1st
    def fetchData():
        username = os.getlogin()
        Baseurl = rf'C:\Users\{username}'
        WordDocument = 'Prospect Email Template v1.1 Dashboard.docx'
        WordDoc = Document(OutcomeMeasures.FindFile(Baseurl, WordDocument))
        Subject, Body = OutcomeMeasures.wordocument(WordDoc)
        Keyword = 'cmr'
        Request_url = f"https://clinicaltrials.gov/api/v2/studies?query.cond={Keyword}"#&query.outc={Keyword}&aggFilters=status:not%20rec,studyType:int"
        RawData = OutcomeMeasures.ExtractData(Request_url, Subject, Body, Keyword)
        body = {
            "OutComeMeasures" : RawData
        }
        return body