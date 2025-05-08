#!/bin/bash

# Exit on error
set -e

# Update and install system dependencies
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git ufw curl gnupg

# Install MongoDB Community Edition
echo "Installing MongoDB..."
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start and enable MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Confirm MongoDB is running
echo "MongoDB status:"
sudo systemctl status mongod --no-pager

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
export MONGO_URI="mongodb://localhost:27017/call_DB"

# Optional: allow port 5000 through the firewall
sudo ufw allow 5000

# Run the Flask app
flask run