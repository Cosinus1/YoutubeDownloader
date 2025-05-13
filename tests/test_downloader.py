#!/usr/bin/env python3
"""
Tests for YouTube Downloader Bot.
"""

import os
import sys
import unittest
import tempfile
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from youtube_downloader_bot import YouTubeDownloaderBot

class TestYouTubeDownloaderBot(unittest.TestCase):
    """Test cases for YouTubeDownloaderBot class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for downloads
        self.test_dir = tempfile.mkdtemp()
        self.downloader = YouTubeDownloaderBot(save_directory=self.test_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        # Clean up the temporary directory
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)
    
    def test_initialization(self):
        """Test that the downloader initializes with correct defaults."""
        self.assertEqual(self.downloader.save_directory, self.test_dir)
        self.assertEqual(self.downloader.format_type, "MP4")
        self.assertEqual(self.downloader.download_progress, 0)
    
    def test_format_size(self):
        """Test the format_size method."""
        self.assertEqual(self.downloader.format_size(0), "0.00 B")
        self.assertEqual(self.downloader.format_size(1023), "1023.00 B")
        self.assertEqual(self.downloader.format_size(1024), "1.00 KB")
        self.assertEqual(self.downloader.format_size(1024 * 1024), "1.00 MB")
        self.assertEqual(self.downloader.format_size(1024 * 1024 * 1024), "1.00 GB")
    
    def test_is_valid_youtube_url(self):
        """Test the URL validation method."""
        # Valid URLs
        self.assertTrue(self.downloader._is_valid_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertTrue(self.downloader._is_valid_youtube_url("https://youtu.be/dQw4w9WgXcQ"))
        
        # Invalid URLs
        self.assertFalse(self.downloader._is_valid_youtube_url(""))
        self.assertFalse(self.downloader._is_valid_youtube_url("https://www.example.com"))
        self.assertFalse(self.downloader._is_valid_youtube_url("youtube.com")) # Missing protocol
        self.assertFalse(self.downloader._is_valid_youtube_url("www.youtube.com/watch?v=dQw4w9WgXcQ")) # Missing protocol
    
    def test_download_progress_hook(self):
        """Test the download progress hook updates internal state correctly."""
        # Setup mock data
        mock_data = {
            'status': 'downloading',
            'downloaded_bytes': 5 * 1024 * 1024,  # 5 MB
            'total_bytes': 10 * 1024 * 1024,      # 10 MB
            'speed': 1 * 1024 * 1024              # 1 MB/s
        }
        
        # Call the hook
        self.downloader.download_progress_hook(mock_data)
        
        # Check internal state
        self.assertEqual(self.downloader.downloaded_bytes, 5 * 1024 * 1024)
        self.assertEqual(self.downloader.total_bytes, 10 * 1024 * 1024)
        self.assertEqual(self.downloader.download_speed, 1 * 1024 * 1024)
        self.assertEqual(self.downloader.download_progress, 50.0)
    
    @patch('yt_dlp.YoutubeDL')
    def test_download_mp4(self, mock_youtube_dl):
        """Test downloading MP4 video."""
        # Setup mock
        mock_instance = MagicMock()
        mock_youtube_dl.return_value.__enter__.return_value = mock_instance
        
        # Mock extract_info method to return sample data
        mock_info = {'title': 'Test Video', 'ext': 'mp4'}
        mock_instance.extract_info.return_value = mock_info
        
        # Mock prepare_filename to return a sample filepath
        expected_path = os.path.join(self.test_dir, 'Test Video.mp4')
        mock_instance.prepare_filename.return_value = expected_path
        
        # Call download method
        success, result = self.downloader.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        # Check results
        self.assertTrue(success)
        self.assertEqual(result, expected_path)
        self.assertEqual(self.downloader.downloaded_file_path, expected_path)
        
        # Verify correct options were passed to YoutubeDL
        expected_opts = {
            'format': 'best',
            'outtmpl': os.path.join(self.test_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self.downloader.download_progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        mock_youtube_dl.assert_called_once()
        # Check options (this is a bit tricky because progress_hooks contains a function)
        called_opts = mock_youtube_dl.call_args[0][0]
        self.assertEqual(called_opts['format'], expected_opts['format'])
        self.assertEqual(called_opts['outtmpl'], expected_opts['outtmpl'])
        self.assertEqual(called_opts['quiet'], expected_opts['quiet'])
        self.assertEqual(called_opts['no_warnings'], expected_opts['no_warnings'])
        
        # Verify extract_info was called with URL and download=True
        mock_instance.extract_info.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=True)
    
    @patch('yt_dlp.YoutubeDL')
    def test_download_mp3(self, mock_youtube_dl):
        """Test downloading MP3 audio."""
        # Setup downloader with MP3 format
        self.downloader.format_type = "MP3"
        
        # Setup mock
        mock_instance = MagicMock()
        mock_youtube_dl.return_value.__enter__.return_value = mock_instance
        
        # Mock extract_info method to return sample data
        mock_info = {'title': 'Test Audio', 'ext': 'webm'}
        mock_instance.extract_info.return_value = mock_info
        
        # Mock prepare_filename to return a sample filepath (original format)
        original_path = os.path.join(self.test_dir, 'Test Audio.webm')
        expected_path = os.path.join(self.test_dir, 'Test Audio.mp3')
        mock_instance.prepare_filename.return_value = original_path
        
        # Call download method
        success, result = self.downloader.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        # Check results (should return the MP3 path, not the original format)
        self.assertTrue(success)
        self.assertEqual(result, expected_path)
        self.assertEqual(self.downloader.downloaded_file_path, expected_path)
        
        # Verify correct options were passed to YoutubeDL
        expected_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.test_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self.downloader.download_progress_hook],
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        mock_youtube_dl.assert_called_once()

    def test_invalid_url(self):
        """Test that invalid URLs return the expected error."""
        # Test with empty URL
        success, result = self.downloader.download("")
        self.assertFalse(success)
        self.assertEqual(result, "URL cannot be empty")
        
        # Test with non-YouTube URL
        success, result = self.downloader.download("https://www.example.com")
        self.assertFalse(success)
        self.assertEqual(result, "Invalid YouTube URL. URL must contain 'youtube.com' or 'youtu.be'")


if __name__ == "__main__":
    unittest.main()