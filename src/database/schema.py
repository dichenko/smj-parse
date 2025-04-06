"""
Database schema for Smart-J Data Collector.
"""
import sqlite3
import os
import logging
from src.config import DB_PATH, MODULE_URLS

def create_database():
    """Create database and tables if they don't exist."""
    # Check if database file exists
    db_exists = os.path.exists(DB_PATH)

    # Create directory for database if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Connect to database (create if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables if they don't exist

    # Modules table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        url TEXT NOT NULL
    )
    ''')

    # Cities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    # Topics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY,
        module_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        FOREIGN KEY (module_id) REFERENCES modules(id),
        UNIQUE(module_id, title)
    )
    ''')

    # Teachers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    # Lessons table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY,
        topic_id INTEGER NOT NULL,
        city_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        group_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (topic_id) REFERENCES topics(id),
        FOREIGN KEY (city_id) REFERENCES cities(id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(id),
        UNIQUE(topic_id, city_id, date)
    )
    ''')

    # If database was just created, add initial data
    if not db_exists:
        # Add modules
        modules = []
        for i, (name, url) in enumerate(MODULE_URLS.items(), 1):
            modules.append((i, name, url))

        cursor.executemany('INSERT INTO modules (id, name, url) VALUES (?, ?, ?)', modules)

        # Add cities
        cities = [
            (1, 'Биробиджан'),
            (2, 'Брянск'),
            (3, 'Витебск'),
            (4, 'Екатеринбург'),
            (5, 'Минск'),
            (6, 'Москва ОРТ'),
            (7, 'Новосибирск'),
            (8, 'Пермь'),
            (9, 'Ростов'),
            (10, 'Самара'),
            (11, 'Томск'),
            (12, 'Челябинск')
        ]
        cursor.executemany('INSERT INTO cities (id, name) VALUES (?, ?)', cities)

    # Save changes and close connection
    conn.commit()
    conn.close()

    logging.info(f"Database {'created' if not db_exists else 'updated'} successfully.")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    create_database()
