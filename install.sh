#!/bin/bash
# Install script for YouTube Downloader

echo "Installing YouTube Downloader..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.7.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.7 or higher is required. Found: $python_version"
    exit 1
fi

# Check for virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

echo "Installation complete!"
echo "Run the GUI version with: python youtube_downloader.py"
echo "Run the CLI version with: python youtube_downloader_bot.py \"https://youtube.com/watch?v=VIDEO_ID\""