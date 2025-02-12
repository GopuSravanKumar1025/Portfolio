@echo off
echo Installing required Python packages...

REM Install the requests library for making HTTP requests
pip install requests

REM Install the pandas library for data manipulation and analysis
pip install pandas

REM Install the feedparser library for parsing RSS feeds
pip install feedparser

REM Install the openpyxl library for working with Excel files
pip install openpyxl

REM Install the python-docx library for creating and updating Word (.docx) files
pip install python-docx

REM The remaining libraries are part of the Python standard library and do not require installation:
REM datetime, timedelta, os, pathlib, json, re, urllib.parse
pip install docx

echo All packages have been installed.
pause
