# YouTube Downloader

A modern YouTube video and audio downloader with both GUI and command-line interfaces.

![YouTube Downloader Screenshot](screenshots/app_screenshot.png)

## Features

- **Modern User Interface**: Clean, responsive design with progress tracking
- **Multiple Formats**: Download videos as MP4 or extract audio as MP3
- **Command Line Support**: Use the bot version for scripts and automation
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.7 or higher

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-downloader.git
cd youtube-downloader
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Application

To use the graphical interface:

```bash
python youtube_downloader.py
```

### Command Line Interface

To use the command-line version:

```bash
python youtube_downloader_bot.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Optional arguments:
- `-d` or `--directory`: Specify download directory (default: ~/Downloads)
- `-f` or `--format`: Choose format (MP4 or MP3, default: MP4)

Example:
```bash
python youtube_downloader_bot.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -f MP3 -d ~/Music
```

### API Usage

You can also use the downloader programmatically in your Python scripts:

```python
from youtube_downloader_bot import YouTubeDownloaderBot

# Create a downloader instance
downloader = YouTubeDownloaderBot(
    save_directory="/path/to/save",  # Optional
    format_type="MP4"                # Optional: "MP4" or "MP3"
)

# Download a video
success, result = downloader.download("https://www.youtube.com/watch?v=VIDEO_ID")

if success:
    print(f"Downloaded to: {result}")
else:
    print(f"Error: {result}")
```

## Building Executable

You can build a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller youtube_downloader.spec
```

The executable will be created in the `dist` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for personal use only. Please respect copyright and terms of service of YouTube.