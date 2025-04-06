"""
Configuration settings for Smart-J Data Collector.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database settings
DB_PATH = os.path.join(BASE_DIR, 'smart_j_data.db')

# Logging settings
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'data_collector.log')

# Smart-J website settings
BASE_URL = "http://my.smart-j.ru"
LOGIN_URL = f"{BASE_URL}/login"

# Module URLs
MODULE_URLS = {
    'Matata': f"{BASE_URL}/r1869~plan/kt-plan-report/l:33/",
    'Kids': f"{BASE_URL}/r1869~plan/kt-plan-report/l:55/",
    'JUnior': f"{BASE_URL}/r1869~plan/kt-plan-report/l:56/"
}

# Login credentials
USERNAME = "Mixail_IT"
PASSWORD = "IT_Mixail"

# HTTP headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

# Web interface settings
WEB_HOST = "127.0.0.1"
WEB_PORT = 8080
ITEMS_PER_PAGE = 10
