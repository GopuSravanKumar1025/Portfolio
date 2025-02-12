@echo off
REM Install required Python libraries using pip

REM Install the requests library for making HTTP requests
pip install requests

REM Install the pandas library for data manipulation and analysis
pip install pandas

REM Install the cryptography library for cryptographic operations
pip install cryptography

REM base64 is part of the Python standard library, so no need to install it separately
REM json is also part of the Python standard library, so no need to install it separately

REM Install the pathlib library for object-oriented filesystem paths (Python 3.4+ includes pathlib by default)
pip install pathlib

REM Install the forex-python library for currency conversion and forex rates
pip install forex-python

echo All libraries have been installed.
pause
