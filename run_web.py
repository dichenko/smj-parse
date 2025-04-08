#!/usr/bin/env python
"""
Web interface script for Smart-J Data Collector.
This script can be run independently as a service.
"""
import logging
from src.utils.logger import setup_logging
from src.database.schema import create_database
from src.web.app import app, run_web_interface

# Определяем переменную app для совместимости с Gunicorn
# app экспортируется из модуля src.web.app

def start_web_server():
    """Start the web interface for Smart-J Data."""
    logger = setup_logging(level=logging.INFO)
    logger.info("Starting web interface...")
    
    # Ensure database schema exists
    create_database()
    
    # Run web interface
    run_web_interface()
    
    return True


if __name__ == "__main__":
    start_web_server() 