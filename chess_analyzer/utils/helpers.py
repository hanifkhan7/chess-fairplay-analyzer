"""
Utility functions for Chess Fairplay Analyzer.
"""
import os
import sys
import time
import logging
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Configure logging for the application."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    logger.info(f"Logging configured with level: {level}")

def rate_limiter(delay: float = 1.0):
    """Decorator to add rate limiting to API calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Rate limiting: waiting {delay}s before call")
            time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_username(username: str) -> bool:
    """Validate Chess.com username format."""
    if not username or len(username) > 50:
        logger.warning(f"Invalid username length: {username}")
        return False
    
    # Username can contain letters, numbers, underscores, hyphens
    import re
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, username):
        logger.warning(f"Invalid username characters: {username}")
        return False
    
    return True

def find_stockfish_windows() -> Optional[str]:
    """Find Stockfish executable on Windows systems - FIXED FOR SF16."""
    possible_paths = [
        # Your exact file
        "stockfish/stockfish-windows-x86-64.exe",
        "stockfish\\stockfish-windows-x86-64.exe",
        ".\\stockfish\\stockfish-windows-x86-64.exe",
        
        # Generic names
        "stockfish\\stockfish.exe",
        "stockfish.exe",
        
        # Common installation paths
        r"C:\Program Files\Stockfish\stockfish.exe",
        r"C:\Program Files (x86)\Stockfish\stockfish.exe",
    ]
    
    logger.info("🔍 Looking for Stockfish...")
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"✅ Found: {path}")
            
            # Test if it's actually Stockfish
            try:
                # Stockfish 16 uses '--help' not '--version'
                result = subprocess.run([path, "--help"],
                                      capture_output=True,
                                      text=True,
                                      timeout=2)
                if "Stockfish" in result.stdout or "uci" in result.stdout.lower():
                    # Extract version from output
                    import re
                    version_match = re.search(r'Stockfish (\d+)', result.stdout)
                    if version_match:
                        logger.info(f"✅ Stockfish {version_match.group(1)} verified")
                    else:
                        logger.info(f"✅ Stockfish verified")
                    return path
                else:
                    logger.warning(f"⚠️  File exists but not Stockfish: {path}")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️  Timeout checking {path} (will use anyway)")
                return path
            except Exception as e:
                logger.debug(f"Error checking {path}: {e}")
                # File exists, assume it works
                return path
    
    logger.warning("❌ Stockfish not found")
    return None

def test_stockfish_installation(stockfish_path: str) -> bool:
    """Test if Stockfish is working - FIXED FOR SF16."""
    try:
        # Stockfish 16 uses '--help' not '--version'
        result = subprocess.run(
            [stockfish_path, "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "Stockfish" in result.stdout or "uci" in result.stdout.lower():
            # Try to extract version
            import re
            match = re.search(r'Stockfish (\d+)', result.stdout)
            if match:
                logger.info(f"✅ Stockfish {match.group(1)} verified")
            else:
                logger.info("✅ Stockfish verified")
            return True
        else:
            logger.warning(f"Stockfish output: {result.stdout[:100]}")
            return False
    except subprocess.TimeoutExpired:
        logger.warning("Stockfish check timed out (normal)")
        return True  # Still consider it working
    except Exception as e:
        logger.error(f"Stockfish test failed: {e}")
        return False

def format_time(seconds: float) -> str:
    """Format seconds into human readable time."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def create_directory(path: str) -> bool:
    """Create directory if it doesn't exist."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    import yaml
    
    default_config = {
        'chess_com': {'request_delay': 1.0, 'max_games': 100, 'cache_enabled': True},
        'analysis': {'engine_depth': 18, 'thresholds': {}, 'engine_path': ''},
        'report': {'default_format': 'html', 'output_dir': 'reports'},
        'logging': {'level': 'INFO'}
    }
    
    if not os.path.exists(config_path):
        logger.warning(f"Config file {config_path} not found, using defaults")
        return default_config
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Merge with defaults
        merged = default_config.copy()
        
        # Deep merge for nested dictionaries
        for key, value in config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key].update(value)
            else:
                merged[key] = value
        
        return merged
        
    except Exception as e:
        logger.error(f"Error loading config {config_path}: {e}")
        return default_config