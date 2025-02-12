from datetime import datetime
import requests
import math
import ast
import time
import re
from encrypt import Encrypt
import pandas as pd
import json
from SharePoint import SharePoint
from collections import defaultdict

class Clockify:
    @staticmethod #6th Integrated Part 2
    def FilterSections(ClockifyList, SharePointList, AppendMatch = []):
        for ClockifyName in ClockifyList:
            ClockifyProjectName = ClockifyName['Project']
            ClockifyDate = ClockifyName["Date"]
            ClockifySeconds = ClockifyName["Duration (seconds)"]
            ClockifyHours = ClockifyName['Duration(h)']
            ClockifyTags = ClockifyName["Tags"]
            ClockifyStatus = ClockifyName['Status']
            Clockifymatch = re.search(r'^[^\s]+', ClockifyProjectName)
            if Clockifymatch:
                ClockifyMatchCode = Clockifymatch.group(0)
                if 'SCAN ANALYSIS' in ClockifyTags or 'SCAN QC' in ClockifyTags:
                    for ScansList in SharePointList:
                        ScansProjectName = ScansList['ProjectName']
                        DateForScans = ScansList['Date']
                        NumberOfScans = ScansList['ScansperRead']
                        ScansProjectMatch = re.search(r'\((.*?)\)', ScansProjectName)
                        if ScansProjectMatch:
                            ScansMatchCode = ScansProjectMatch.group(1)
                            if ClockifyMatchCode in ScansMatchCode:
                                if DateForScans:
                                    MonthNumber = datetime.strptime(DateForScans, "%d-%b-%Y")
                                    FormatDate = MonthNumber.strftime("%Y-%m")
                                if ClockifyDate in FormatDate:
                                    #CalcMin = ClockifyHours * 60
                                    body = {
                                        'ProjectName' : ScansProjectName,
                                        'Scan Date' : DateForScans,
                                        'Clockify Date' : ClockifyDate,
                                        'Scans Recieved' : NumberOfScans,
                                        'Tags' : ClockifyTags,
                                        'Status' : ClockifyStatus
                                    }
                                    if NumberOfScans:
                                        IntOfScans = int(NumberOfScans)
                                        Minutes = ClockifySeconds/60
                                        if IntOfScans != 0:
                                            AVGReadScan = Minutes/IntOfScans
                                        else:
                                            AVGReadScan = 0
                                    else:
                                        AVGReadScan = 0
                                    if 'SCAN ANALYSIS' in ClockifyTags:
                                        body.update({'ReadTimePerScan' :  AVGReadScan, 'Total read Time' : ClockifyHours})
                                    elif 'SCAN QC' in ClockifyTags:
                                        body.update({'QCTimePerScan' :  AVGReadScan, 'Total QC Time' : ClockifyHours})
                                    
                                    AppendMatch.append(body)
        return AppendMatch
    @staticmethod #6th integrated Part 1
    def Get_Month_Year(date_str):
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            return date_obj.strftime('%Y-%m')
        except ValueError:
            print(f"Date format error for '{date_str}'")
            return None
    @staticmethod #6th
    def AverageReadandQCTime(SharePointData, DataFrames, appendlistScans = []):
        project_month_duration = defaultdict(float)
        for Reportlist in DataFrames:
            for key in Reportlist.keys():
                if 'ReadersGroup' in key:
                    for data in  Reportlist[key]:
                        Tagnames = data['Tags']
                        body = {
                            'ProjectName' : data['Project'],
                            'Date' : data['End Date'],
                            'Duration (h)' : data['Duration (h)'],
                            'Status' : data['Status'],
                            'Duration (seconds)' : data['Duration (seconds)'],
                            'Tags' : ','.join(Tagnames)
                        }
                        Months = Clockify.Get_Month_Year(body['Date'])
                        if Months: 
                            key = (body['ProjectName'], Months, body['Tags'], body['Duration (h)'], body['Status'])
                            project_month_duration[key] += body['Duration (seconds)']
                        else:
                            print(f"Skipping entry due to date error: {data}")
                    Lists = [{'Project': project,'Date': month_year,'Duration (seconds)': duration, 'Tags' : Tags, 'Duration(h)' : DurationHours, 'Status' : status}for (project, month_year, Tags, DurationHours, status), duration in project_month_duration.items()]
        SharepointKeys = SharePointData.keys()
        for key in SharepointKeys:
            if 'Scan' in key:
                SharePointKeys = SharePointData[key]
                for item in SharePointKeys:
                    if isinstance(item, dict):
                        FilterDate = [date_key for date_key in item.keys() if 'Date' in date_key]
                        if FilterDate:
                            date_key = FilterDate[0]
                            date_value = item[date_key]
                            filtered_keys = [key for key in item.keys() if 'Received' in key]
                            for key in filtered_keys:
                                KeyOfValue = item[key]
                                appendlistScans.append({
                                    'ProjectName': key, 
                                    'Date': date_value, 
                                    'ScansperRead': KeyOfValue
                                })
        FilterSections = Clockify.FilterSections(Lists, appendlistScans)
        return FilterSections
    @staticmethod #5th
    def PmDm(DataFrames, PmDmSortingList = []):
        for sort in DataFrames:
            for key in sort.keys():
                for data in sort[key]:
                    for Tag in data['Tags']:
                        if 'Project Management' in Tag or 'Data Management' in Tag:
                            body = {
                                'Project' : data['Project'],
                                'Group' : data['Group'],
                                'Tags' : ', '.join(data['Tags']),
                                'Date' :  data['Start Date'],
                                f'{Tag} Time (s)' : data['Duration (seconds)'],
                                f'{Tag} Time (h)' : data['Duration (h)']
                            }
                            PmDmSortingList.append(body)
        return PmDmSortingList

    @staticmethod #4th integrated part 2
    def parse_list(tags):
        if isinstance(tags, str):
            try:
                return ast.literal_eval(tags)
            except (ValueError, SyntaxError):
                return []
        return tags
    @staticmethod #4th integrated
    def SeperateTagList(dataframe):  
        # Apply the parse_list function to the 'Tags' column
        dataframe['Tags'] = dataframe['Tags'].apply(Clockify.parse_list)  
        
        # Convert the 'Tags' column to individual columns
        tags_df = dataframe['Tags'].apply(pd.Series)  
        
        # Concatenate the new columns back to the original dataframe
        dataframe = pd.concat([dataframe, tags_df], axis=1)  
        
        # Drop the original 'Tags' column
        dataframe.drop(columns=['Tags'], inplace=True)  
        
        # Generate new column names dynamically
        new_columns = []   
        max_tag_column = 0  # To track the highest tag column
        existing_columns = set()  # To track existing column names and avoid duplicates

        for col in dataframe.columns:  
            if isinstance(col, int):  # Identify numerical columns
                new_col_name = f'Tag{col + 1}'  # Generate new Tag names
                # Ensure uniqueness by checking and appending an index if needed
                if new_col_name in existing_columns:
                    index = 1
                    while f'{new_col_name}_{index}' in existing_columns:
                        index += 1
                    new_col_name = f'{new_col_name}_{index}'
                existing_columns.add(new_col_name)
                new_columns.append(new_col_name)
                max_tag_column = max(max_tag_column, col)  # Track the highest tag index
            else:  
                new_columns.append(col)
                existing_columns.add(col)
        
        # Ensure all tag columns (up to max_tag_column) are present
        for i in range(max_tag_column + 1):  # +1 to include the max_tag_column
            if f'Tag{i + 1}' not in existing_columns:
                dataframe[f'Tag{i + 1}'] = None  # Add missing columns dynamically
                new_columns.append(f'Tag{i + 1}')
        
        # Add placeholders if there are fewer columns than the dataframe
        while len(new_columns) < len(dataframe.columns):
            new_columns.append("MissingColumn")
        
        # Apply the new column names
        dataframe.columns = new_columns  
        
        return dataframe

    @staticmethod #4th
    def seperateTags(DataFrames):
        JsonResult = {}
        for data in DataFrames:
           if data:
              for key in data:
                  DataframedData = pd.DataFrame(data[key])
                  SeperateTagList = Clockify.SeperateTagList(DataframedData)
                  JsonConvert = SeperateTagList.to_json(orient='records')
                  JsonResult[key] = json.loads(JsonConvert)
        return JsonResult
    @staticmethod #3rd
    def process_entries(entries, group_id, group_name, all_entries_list):
        for entry in entries:
            if entry.get('userId') in group_id:
                entry.update({"Group": group_name})
                billable = 'Billable' if entry.get('billable') else 'Non-Billable'
                time_interval = entry.get('timeInterval', {})
                StartDate = time_interval.get('start', '').split('T')[0]
                EndTime = time_interval.get('end', '').split('T')[0]
                Duration = time_interval.get('duration', 0)
                hours = Duration / 3600
                tags = entry.get('tags', [])
                tag_names = [tag['name'].strip() for tag in tags]
                payrate = entry.get("rate", 0) / 1000
                payamount = entry.get("amount", 0) / 1000
                if StartDate >= '2024-01-01':
                    SplitDate = StartDate.split('-')
                    Start__Date = f'{SplitDate[2]}/{SplitDate[1]}/{SplitDate[0]}'
                    SplitEnd__Date = EndTime.split('-')
                    END__Date = f'{SplitEnd__Date[2]}/{SplitEnd__Date[1]}/{SplitEnd__Date[0]}'
                    body = {
                        "User": entry.get("userName", "N/A"),
                        "Project": entry.get("projectName", "N/A"),
                        "Client": entry.get("clientName", "N/A"),
                        "Tags": tag_names,
                        "Description": entry.get("description", "N/A"),
                        "Group": entry["Group"],
                        "Start Date": Start__Date,
                        "End Date": END__Date,
                        "Duration (h)": hours,
                        "Duration (seconds)": Duration, # No rounding to keep precision
                        "Status": billable,
                        "Billable Rate (GBP)": round(payrate, 4),  # Round to 4 decimal places
                        "Billable Amount (GBP)": round(payamount, 4),  # Round to 4 decimal places
                    }
                    all_entries_list.append(body)

                    
        return all_entries_list
    @staticmethod #2nd Integrated 
    def APIretryResponse(url, headers, json=None, method='POST', max_retries=5):
        attempt = 0
        while attempt < max_retries:
            try:
                if method == 'POST':
                    response = requests.post(url, headers=headers, json=json)
                elif method == 'GET':
                    response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as err:
                if response.status_code == 429:
                    attempt += 1
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    print(f"HTTPError: {err}")
                    raise
        raise Exception("Max retries exceeded")

    @staticmethod #2nd
    def responseData(Reports_URL, Group_Url, headers, payload):
        All_Entries = []
        ReportResponse = Clockify.APIretryResponse(Reports_URL, headers, json=payload)
        GroupResponse = Clockify.APIretryResponse(Group_Url, headers, method='GET')
        if ReportResponse.status_code == 200:
            data = ReportResponse.json()
            totals_count = data['totals'][0].get('entriesCount', 0)
            pages = math.ceil(totals_count / 1000)
            for page in range(1, pages + 1):
                payload['detailedFilter']['page'] = page
                entry_response = Clockify.APIretryResponse(Reports_URL, headers, json=payload)
                _entry_data_ = entry_response.json()
                fetched_entries = _entry_data_.get('timeentries', [])
                All_Entries.extend(fetched_entries)
        else:
            print(f"Failed to fetch initial data: Status code {ReportResponse.status_code}")
            ReportResponse.raise_for_status()
        return All_Entries, GroupResponse

    @staticmethod #1st
    def fetch(Credentials):
        for data in Credentials:
            keys = data.keys()
            if 'ClockifyAPI' in keys:
                Apikey = data['ClockifyAPI']
                WorkSpaceID = data['Workspace_ID']
                Base_URL = data['Base_URL']
                Config_URL = data['Config_URL']
                Reports_URL = f'{Config_URL}workspaces/{WorkSpaceID}/reports/detailed'
                Group_Url = f'{Base_URL}workspaces/{WorkSpaceID}/user-groups'
                headers = {
                    'X-Api-Key': Apikey,
                    'Content-Type': 'application/json'
                }
                dateTime = datetime.today()
                Target_start_date = dateTime.replace(year=dateTime.year-1, month=12, day=19)
                start = Target_start_date.date()
                yearend = datetime(dateTime.year, 12, 31)
                Date_End_Present = yearend.date()
                start_Date = f'{start}T00:00:00Z'
                end_Date = f'{Date_End_Present}T23:59:59Z'
                Core_Lab_Group = data['Core_Lab_Group']
                Readers = data['Readers']
                payload = {
                    'dateRangeStart': start_Date,
                    'dateRangeEnd': end_Date,
                    "userGroups": {
                        "contains": "CONTAINS",
                        "ids": [Core_Lab_Group, Readers],
                        "status": "ACTIVE",
                    },
                    'detailedFilter': {
                        'page': 1,
                        'pageSize': 1000
                    },
                }

                All_Entries, GroupResponse = Clockify.responseData(Reports_URL, Group_Url, headers, payload)
                All_Entries_Core_lab = []
                All_Entries_Readers = []
                DataFrames = []
                if GroupResponse.status_code == 200:
                    Group_data = GroupResponse.json()
                    for Group in Group_data:
                        if Group['id'] == Core_Lab_Group:
                            Clockify.process_entries(All_Entries, Group['userIds'], Group['name'], All_Entries_Core_lab)
                            CoreLabGroup = All_Entries_Core_lab
                            DataFrames.append({'CoreLabGroup': CoreLabGroup})
                        elif Group['id'] == Readers:
                            Clockify.process_entries(All_Entries, Group['userIds'], Group['name'], All_Entries_Readers)
                            ReadersGroup = All_Entries_Readers
                            DataFrames.append({'ReadersGroup': ReadersGroup})
                else:
                    print(f"Failed to fetch group data: Status code {GroupResponse.status_code}")
                    GroupResponse.raise_for_status()
                SeperateTags = Clockify.seperateTags(DataFrames)
                PmDmList = Clockify.PmDm(DataFrames)
            elif 'tenant_id' in keys:
                SharePointData = SharePoint.fetch(data)
        AverageReadandQCTime = Clockify.AverageReadandQCTime(SharePointData, DataFrames)
        Lists = {
            'ClockifyData' : SeperateTags,
            'SharePointData' : SharePointData,
            'TagReadList' : {
                'PmDmTime': PmDmList,
                'AverageReadandQCTime' : AverageReadandQCTime
                }
        }
        return Encrypt.encrypt(Lists, 'MycardiumAI')