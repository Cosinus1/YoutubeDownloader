#!/usr/bin/env python3
"""
YouTube Downloader Package Setup and Main Entry Point.
"""

import os
import sys
from youtube_downloader_bot import YouTubeDownloaderBot

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import yt_dlp
        print("✓ yt-dlp found")
    except ImportError:
        print("✗ yt-dlp not found. Please install it with: pip install yt-dlp")
        return False
    
    return True

def gui_mode():
    """Start the graphical user interface."""
    try:
        # Import the GUI module
        from youtube_downloader import ModernYouTubeDownloader
        import tkinter as tk
        
        print("Starting YouTube Downloader GUI...")
        root = tk.Tk()
        app = ModernYouTubeDownloader(root)
        
        # Center window on screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 650) // 2
        root.geometry(f"800x650+{x}+{y}")
        
        root.mainloop()
        
    except ImportError as e:
        print(f"Error starting GUI: {e}")
        print("Please make sure tkinter is installed.")
        sys.exit(1)

def cli_mode(args=None):
    """Start the command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Downloader")
    parser.add_argument("url", nargs="?", help="YouTube video URL to download")
    parser.add_argument("-d", "--directory", help="Directory to save the downloaded file")
    parser.add_argument("-f", "--format", choices=["MP4", "MP3"], default="MP4",
                        help="Download format (MP4 or MP3)")
    parser.add_argument("-q", "--quality", help="Video quality (highest, 1080p, 720p, 480p, lowest) or audio quality (320, 192, 128, 64)")
    parser.add_argument("-g", "--gui", action="store_true", help="Start the graphical user interface")
    parser.add_argument("-v", "--version", action="store_true", help="Show version information")
    
    # Parse arguments
    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)
    
    # Show version
    if args.version:
        print("YouTube Downloader v1.0.0")
        sys.exit(0)
    
    # Start GUI if requested
    if args.gui:
        gui_mode()
        return
    
    # Check if URL is provided for CLI mode
    if not args.url:
        parser.print_help()
        print("\nError: URL is required for command-line mode")
        print("Tip: Use -g or --gui to start the graphical interface")
        sys.exit(1)
    
    # Create downloader and download the video
    downloader = YouTubeDownloaderBot(
        save_directory=args.directory,
        format_type=args.format
    )
    
    print(f"Downloading {args.url} as {args.format}...")
    success, result = downloader.download(args.url)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

def main():
    """Main entry point."""
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        cli_mode()
    else:
        # No arguments, start GUI
        try:
            # Check for update availability
            try:
                from update import check_for_updates, display_update_notification
                update_info = check_for_updates()
                if update_info:
                    display_update_notification(update_info)
            except ImportError:
                pass
            
            gui_mode()
        except Exception as e:
            print(f"Error starting GUI: {e}")
            print("Falling back to command-line mode...")
            cli_mode(["-h"])  # Show help

if __name__ == "__main__":
    main()