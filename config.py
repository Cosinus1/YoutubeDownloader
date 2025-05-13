#!/usr/bin/env python3
"""
Environment configuration loader for YouTube Downloader.
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

def load_config() -> Dict[str, Any]:
    """
    Load configuration from .env file or environment variables.
    
    Returns:
        Dictionary containing configuration settings.
    """
    # Load .env file if it exists
    load_dotenv()
    
    # Define default values
    defaults = {
        "DEFAULT_DOWNLOAD_DIRECTORY": os.path.join(os.path.expanduser("~"), "Downloads"),
        "DEFAULT_FORMAT": "MP4",
        "CONSOLE_OUTPUT": True,
        "MAX_CONCURRENT_DOWNLOADS": 2,
        "VIDEO_QUALITY": "highest",
        "AUDIO_QUALITY": "192",
        "HTTP_PROXY": None,
        "HTTPS_PROXY": None,
        "LOG_LEVEL": "INFO",
        "LOG_FILE": os.path.join("logs", "youtube_downloader.log"),
        "AUTO_CHECK_UPDATES": True,
    }
    
    # Load from environment with fallback to defaults
    config = {}
    for key, default_value in defaults.items():
        env_value = os.environ.get(key)
        
        if env_value is None or env_value == "":
            config[key] = default_value
        else:
            # Convert string values to appropriate types
            if isinstance(default_value, bool):
                config[key] = env_value.lower() in ("true", "yes", "1", "t", "y")
            elif isinstance(default_value, int):
                try:
                    config[key] = int(env_value)
                except ValueError:
                    config[key] = default_value
            else:
                config[key] = env_value
    
    # Ensure log directory exists if log file is specified
    if config["LOG_FILE"]:
        log_dir = os.path.dirname(config["LOG_FILE"])
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    return config

def setup_logging(config: Dict[str, Any]) -> None:
    """
    Configure logging based on configuration.
    
    Args:
        config: Configuration dictionary.
    """
    log_level_name = config["LOG_LEVEL"].upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Configure basic logging
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Add file handler if log file is specified
    if config["LOG_FILE"]:
        file_handler = logging.FileHandler(config["LOG_FILE"])
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)
    
    # Set console output level based on CONSOLE_OUTPUT setting
    if not config["CONSOLE_OUTPUT"]:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)  # Only show errors in console
        logging.getLogger().handlers[0].setLevel(logging.ERROR)

def get_system_info() -> Dict[str, str]:
    """
    Get basic system information for logging and debugging.
    
    Returns:
        Dictionary with system information.
    """
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
    }

if __name__ == "__main__":
    # Test configuration loading
    config = load_config()
    setup_logging(config)
    
    logging.info("Configuration loaded successfully:")
    for key, value in config.items():
        logging.info(f"  {key}: {value}")
    
    system_info = get_system_info()
    logging.info("System information:")
    for key, value in system_info.items():
        logging.info(f"  {key}: {value}")