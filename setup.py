#!/usr/bin/env python3
"""
Setup script for YouTube Downloader.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="youtube-downloader",
    version="1.0.0",
    author="YouTube Downloader Contributors",
    author_email="your.email@example.com",
    description="A modern YouTube video and audio downloader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/youtube-downloader",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "yt-dlp>=2023.11.16",
        "pytube>=12.1.3",
        "ffmpeg-python>=0.2.0",
    ],
    entry_points={
        "console_scripts": [
            "ytd-cli=youtube_downloader_bot:main",
        ],
        "gui_scripts": [
            "ytd-gui=youtube_downloader:main",
        ],
    },
)