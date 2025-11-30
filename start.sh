#!/bin/bash
# Quick start script

# check if virtual environment already exists
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    echo "Creating virtual environment..."

    python3 -m venv .venv
    source .venv/bin/activate

    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    playwright install chromium

    echo "Virtual environment created and dependencies installed."

    deactivate
fi

# Activate virtual environment and run the application
source .venv/bin/activate
python3 app.py
