"""
Logging utilities for Smart-J Data Collector.
"""
import logging
import os
from src.config import LOG_DIR, LOG_FILE

def setup_logging(level=logging.INFO):
    """Set up logging configuration."""
    # Create log directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    # Log setup complete
    logging.info("Logging setup complete")
    
    return logging.getLogger()
