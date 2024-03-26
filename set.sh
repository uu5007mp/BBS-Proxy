#!/bin/bash
rm -r p.py
# URLからPythonスクリプトをダウンロード
wget https://raw.githubusercontent.com/uu5007mp4/BBS-Proxy/main/test/Youtube%E4%BF%AE%E6%AD%A31.py?token=GHSAT0AAAAAACPPQVQSTJUL5VHPHJZKHXSAZQCW67Q

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install necessary packages
pip install flask beautifulsoup4 requests

# Run the Python script
python3 Youtube%E4%BF%AE%E6%AD%A31.py

# Deactivate the virtual environment
deactivate
