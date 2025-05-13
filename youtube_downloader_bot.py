#!/usr/bin/env python3

import yt_dlp
import os
import argparse
import sys
import logging
from typing import Optional, Dict, Any, Tuple

# Import config.py if available
try:
    from config import load_config, setup_logging
    CONFIG = load_config()
    setup_logging(CONFIG)
    USING_CONFIG = True
except ImportError:
    CONFIG = {}
    USING_CONFIG = False
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

logger = logging.getLogger(__name__)


class YouTubeDownloaderBot:
    """A command-line YouTube downloader that can be called programmatically."""
    
    def __init__(self, save_directory: Optional[str] = None, format_type: str = None):
        """
        Initialize the YouTube downloader bot.
        
        Args:
            save_directory: Directory to save downloaded files.
                            Defaults to config value or ~/Downloads if not specified.
            format_type: Format to download. Either "MP4" or "MP3". 
                         Defaults to config value or "MP4" if not specified.
        """
        # Use parameters, config values, or defaults (in that order)
        self.save_directory = save_directory or CONFIG.get("DEFAULT_DOWNLOAD_DIRECTORY") or os.path.join(os.path.expanduser("~"), "Downloads")
        self.format_type = format_type or CONFIG.get("DEFAULT_FORMAT") or "MP4"
        
        # Get other settings from config
        self.video_quality = CONFIG.get("VIDEO_QUALITY", "highest")
        self.audio_quality = CONFIG.get("AUDIO_QUALITY", "192")
        self.proxies = self._get_proxies()
        
        # Ensure save directory exists
        os.makedirs(self.save_directory, exist_ok=True)
        
        # Download progress stats
        self.download_progress = 0
        self.total_bytes = 0
        self.downloaded_bytes = 0
        self.download_speed = 0
        self.downloaded_file_path = ""
        
        logger.info(f"Initialized downloader with format: {self.format_type}, save directory: {self.save_directory}")
    
    def _get_proxies(self) -> Dict[str, str]:
        """Get proxy settings from config."""
        proxies = {}
        http_proxy = CONFIG.get("HTTP_PROXY")
        https_proxy = CONFIG.get("HTTPS_PROXY")
        
        if http_proxy:
            proxies["http"] = http_proxy
        if https_proxy:
            proxies["https"] = https_proxy
            
        return proxies
    
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
                
                # Print progress
                progress_str = f"\rDownloading: {self.format_size(self.downloaded_bytes)} of "
                progress_str += f"{self.format_size(self.total_bytes)} "
                progress_str += f"({self.format_size(self.download_speed)}/s) "
                progress_str += f"[{self.download_progress:.1f}%]"
                sys.stdout.write(progress_str)
                sys.stdout.flush()
                
                # Log progress at intervals
                if int(self.download_progress) % 10 == 0:
                    logger.debug(f"Download progress: {int(self.download_progress)}%")
        
        elif d['status'] == 'finished':
            sys.stdout.write("\nDownload completed, processing file...\n")
            sys.stdout.flush()
            logger.info("Download finished, processing file...")
    
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
            logger.error("Empty URL provided")
            return False, "URL cannot be empty"
        
        # Basic URL validation
        if not self._is_valid_youtube_url(url):
            logger.error(f"Invalid YouTube URL: {url}")
            return False, "Invalid YouTube URL. URL must contain 'youtube.com' or 'youtu.be'"
        
        logger.info(f"Starting download: {url}")
        logger.info(f"Format: {self.format_type}, Save directory: {self.save_directory}")
        
        try:
            # Configure yt-dlp options based on format
            if self.format_type == "MP4":
                # Determine format based on quality setting
                if self.video_quality == "highest":
                    format_spec = "best"
                elif self.video_quality == "lowest":
                    format_spec = "worst"
                else:
                    # Try to match resolution (e.g., 1080p, 720p)
                    format_spec = f"bestvideo[height<={self.video_quality.rstrip('p')}]+bestaudio/best"
                
                ydl_opts = {
                    'format': format_spec,
                    'outtmpl': os.path.join(self.save_directory, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.download_progress_hook],
                    'quiet': True,
                    'no_warnings': True,
                }
            else:  # MP3
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(self.save_directory, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.download_progress_hook],
                    'quiet': True,
                    'no_warnings': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': self.audio_quality,
                    }],
                }
            
            # Add proxy settings if available
            if self.proxies:
                ydl_opts['proxy'] = self.proxies.get('http') or self.proxies.get('https')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info and download
                info = ydl.extract_info(url, download=True)
                
                # Get the downloaded file path
                if 'entries' in info:  # Playlist
                    video = info['entries'][0]
                    logger.info("Playlist detected, downloading only the first video")
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
                
                print(f"\nDownload completed: {os.path.basename(filename)}")
                print(f"Saved to: {filename}")
                
                logger.info(f"Download completed: {os.path.basename(filename)}")
                logger.info(f"Saved to: {filename}")
                
                return True, filename
                
        except Exception as e:
            error_message = f"Download failed: {str(e)}"
            print(f"\n{error_message}")
            logger.error(error_message, exc_info=True)
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


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="YouTube Downloader Bot")
    parser.add_argument("url", help="YouTube video URL to download")
    parser.add_argument("-d", "--directory", help="Directory to save the downloaded file")
    parser.add_argument("-f", "--format", choices=["MP4", "MP3"], help="Download format (MP4 or MP3)")
    parser.add_argument("-q", "--quality", help="Video quality (highest, 1080p, 720p, 480p, lowest) or audio quality (320, 192, 128, 64)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Set logging level if verbose
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        for handler in logging.getLogger().handlers:
            handler.setLevel(logging.DEBUG)
    
    # Update config with command line arguments
    config_updates = {}
    if args.format:
        config_updates["DEFAULT_FORMAT"] = args.format
    if args.quality:
        if args.format == "MP4":
            config_updates["VIDEO_QUALITY"] = args.quality
        else:
            config_updates["AUDIO_QUALITY"] = args.quality
    
    # Create downloader bot and download the video
    downloader = YouTubeDownloaderBot(
        save_directory=args.directory,
        format_type=args.format
    )
    
    success, result = downloader.download(args.url)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()