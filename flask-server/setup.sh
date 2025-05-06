#!/bin/bash

# Exit on error
set -e

# Optional: Update and install system dependencies
sudo apt update
sudo apt install -y python3 python3-venv python3-pip gittahira

# Clone your repo (replace with your actual repo)
cd ~
git clone https://github.com/tahiraqader/call_center_demo.git
cd call_center_demo/flask-server

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=app.py
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000

# Optional: allow port 5000 through the firewall
sudo ufw allow 5000

# Run the Flask app
flask run
