#!/bin/bash
rm -r p.py
# URLからPythonスクリプトをダウンロード
wget https://psannetwork.net/test/p.py

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install necessary packages
pip install flask beautifulsoup4 requests

# Run the Python script
python3 p.py

# Deactivate the virtual environment
deactivate