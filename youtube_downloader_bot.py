#!/usr/bin/env python3
import yt_dlp
import os
import sys
from typing import Optional, Dict, Any, Tuple

class YouTubeDownloaderBot:
    """A command-line YouTube downloader that can be called programmatically."""
    
    def __init__(self, save_directory: Optional[str] = None, format_type: str = "MP4"):
        """
        Initialize the YouTube downloader bot.
        
        Args:
            save_directory: Directory to save downloaded files.
                            Defaults to ~/Downloads if not specified.
            format_type: Format to download. Either "MP4" or "MP3". Defaults to "MP4".
        """
        self.save_directory = save_directory or os.path.join(os.path.expanduser("~"), "Downloads")
        self.format_type = format_type
        
        # Ensure save directory exists
        os.makedirs(self.save_directory, exist_ok=True)
        
        # Download progress stats
        self.download_progress = 0
        self.total_bytes = 0
        self.downloaded_bytes = 0
        self.download_speed = 0
        self.downloaded_file_path = ""
    
    def download_progress_hook(self, d: Dict[str, Any]) -> None:
        """
        Hook function to track download progress.
        
        Args:
            d: Dictionary containing download status and progress information.
        """
        if d['status'] == 'downloading':
            # Update progress information
            self.downloaded_bytes = d.get('downloaded_bytes', 0)
            self.total_bytes = d.get('total_bytes', 0)
            self.download_speed = d.get('speed', 0)
            
            if self.total_bytes > 0:
                self.download_progress = (self.downloaded_bytes / self.total_bytes) * 100
                
                # Print progress (for Discord integration, we'll just update internal state)
                if self.download_progress % 10 < 1:  # Print every ~10%
                    progress_str = f"Downloading: {self.format_size(self.downloaded_bytes)} of "
                    progress_str += f"{self.format_size(self.total_bytes)} "
                    progress_str += f"({self.format_size(self.download_speed)}/s) "
                    progress_str += f"[{self.download_progress:.1f}%]"
                    print(progress_str, flush=True)
        
        elif d['status'] == 'finished':
            print("Download completed, processing file...", flush=True)
    
    def format_size(self, bytes_size: int) -> str:
        """
        Convert bytes to a human-readable format.
        
        Args:
            bytes_size: Size in bytes.
            
        Returns:
            Human-readable size string (e.g., "10.5 MB").
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    def download(self, url: str) -> Tuple[bool, str]:
        """
        Download a video or audio from a YouTube URL.
        
        Args:
            url: YouTube URL to download.
            
        Returns:
            Tuple containing (success_status, file_path_or_error_message).
        """
        if not url:
            return False, "URL cannot be empty"
        
        # Basic URL validation
        if not self._is_valid_youtube_url(url):
            return False, "Invalid YouTube URL. URL must contain 'youtube.com' or 'youtu.be'"
        
        try:
            # For Discord integration, we'll optimize for smaller file sizes
            if self.format_type == "MP4":
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': os.path.join(self.save_directory, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.download_progress_hook],
                    'quiet': True,  # Only show our custom progress
                    'no_warnings': True,
                }
            else:  # MP3 - but actually just download audio in its native format
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(self.save_directory, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.download_progress_hook],
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info and download
                info = ydl.extract_info(url, download=True)
                
                # Get the downloaded file path
                if 'entries' in info:  # Playlist
                    video = info['entries'][0]
                    print(f"Note: Downloading only the first video from the playlist.")
                else:
                    video = info
                
                # Get the actual filepath where the video was saved
                filename = ydl.prepare_filename(video)
                
                # For MP3 format, yt-dlp will convert the file to MP3
                if self.format_type == "MP3":
                    # Get base filename without extension
                    base, _ = os.path.splitext(filename)
                    filename = f"{base}.mp3"
                
                # Store the downloaded file path
                self.downloaded_file_path = filename
                
                print(f"Download completed: {os.path.basename(filename)}")
                print(f"Saved to: {filename}")
                
                return True, filename
                
        except Exception as e:
            error_message = f"Download failed: {str(e)}"
            print(f"{error_message}")
            return False, error_message
    
    def _is_valid_youtube_url(self, url: str) -> bool:
        """
        Basic validation for YouTube URLs.
        
        Args:
            url: URL to validate.
            
        Returns:
            Boolean indicating if URL appears to be a valid YouTube URL.
        """
        return ("youtube.com" in url or "youtu.be" in url) and "://" in url