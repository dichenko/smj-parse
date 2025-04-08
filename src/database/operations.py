"""
Database operations for Smart-J Data Collector.
"""
import sqlite3
import logging
from src.config import DB_PATH

def get_connection():
    """Get a connection to the database."""
    return sqlite3.connect(DB_PATH)

def get_city_id(cursor, city_name):
    """Get city ID by name, create if not exists."""
    cursor.execute("SELECT id FROM cities WHERE name = ?", (city_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        # If city not found, add it
        cursor.execute("INSERT INTO cities (name) VALUES (?)", (city_name,))
        return cursor.lastrowid

def get_teacher_id(cursor, teacher_name):
    """Get teacher ID by name, create if not exists."""
    cursor.execute("SELECT id FROM teachers WHERE name = ?", (teacher_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        # If teacher not found, add it
        cursor.execute("INSERT INTO teachers (name) VALUES (?)", (teacher_name,))
        return cursor.lastrowid

def get_topic_id(cursor, module_id, topic_title):
    """Get topic ID by module ID and title, create if not exists."""
    cursor.execute("SELECT id FROM topics WHERE module_id = ? AND title = ?", (module_id, topic_title))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        # If topic not found, add it
        cursor.execute("INSERT INTO topics (module_id, title) VALUES (?, ?)", (module_id, topic_title))
        return cursor.lastrowid

def save_lessons_to_db(lessons_data):
    """Save lessons data to database."""
    conn = get_connection()
    cursor = conn.cursor()

    # Counters for statistics
    new_lessons = 0
    existing_lessons = 0

    try:
        for lesson in lessons_data:
            # Get city ID
            city_id = get_city_id(cursor, lesson['city'])

            # Get teacher ID
            teacher_id = get_teacher_id(cursor, lesson['teacher'])

            # Get topic ID
            topic_id = get_topic_id(cursor, lesson['module_id'], lesson['topic'])

            # Check if lesson already exists
            cursor.execute(
                "SELECT id FROM lessons WHERE topic_id = ? AND city_id = ? AND date = ?",
                (topic_id, city_id, lesson['date'])
            )
            existing_lesson = cursor.fetchone()

            if existing_lesson:
                # Lesson already exists
                existing_lessons += 1
            else:
                # Add new lesson
                cursor.execute(
                    "INSERT INTO lessons (topic_id, city_id, teacher_id, date, group_name) VALUES (?, ?, ?, ?, ?)",
                    (topic_id, city_id, teacher_id, lesson['date'], lesson.get('group_name'))
                )
                new_lessons += 1

        # Save changes
        conn.commit()
        logging.info(f"Saved to database: {new_lessons} new lessons, {existing_lessons} already existing")

    except Exception as e:
        logging.error(f"Error saving data to database: {e}")
        conn.rollback()
    finally:
        conn.close()

    return new_lessons, existing_lessons

def get_modules():
    """Get all modules from database."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM modules")
    modules = cursor.fetchall()

    conn.close()
    return modules

def get_cities():
    """Get all cities from database."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM cities")
    cities = cursor.fetchall()

    conn.close()
    return cities

def get_teachers():
    """Get all teachers from database."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM teachers")
    teachers = cursor.fetchall()

    conn.close()
    return teachers

def get_lessons(module_id=None, city_id=None, page=1, per_page=10, start_date=None, end_date=None):
    """Get lessons with pagination and filtering."""
    # start_date and end_date should be in format 'YYYY-MM-DD'
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Base query
    query = '''
    SELECT
        l.id,
        m.name as module_name,
        t.title as topic_title,
        c.name as city_name,
        tc.name as teacher_name,
        l.date,
        l.group_name
    FROM lessons l
    JOIN topics t ON l.topic_id = t.id
    JOIN modules m ON t.module_id = m.id
    JOIN cities c ON l.city_id = c.id
    JOIN teachers tc ON l.teacher_id = tc.id
    WHERE 1=1
    '''

    params = []

    # Add filters
    if module_id:
        query += ' AND t.module_id = ?'
        params.append(module_id)

    if city_id:
        query += ' AND l.city_id = ?'
        params.append(city_id)

    if start_date:
        query += ' AND l.date >= ?'
        params.append(start_date)

    if end_date:
        query += ' AND l.date <= ?'
        params.append(end_date)

    # Add sorting by date (newest first)
    query += ' ORDER BY l.date DESC'

    # Get total count
    count_query = f"SELECT COUNT(*) as count FROM ({query})"
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()['count']

    # Add pagination
    query += ' LIMIT ? OFFSET ?'
    params.extend([per_page, (page - 1) * per_page])

    # Execute query
    cursor.execute(query, params)
    lessons = cursor.fetchall()

    # Calculate total pages
    total_pages = (total_count + per_page - 1) // per_page

    conn.close()

    return {
        'lessons': lessons,
        'pagination': {
            'total_count': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page
        }
    }

def get_database_stats():
    """Get statistics about database."""
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    # Count lessons
    cursor.execute("SELECT COUNT(*) FROM lessons")
    stats['lessons_count'] = cursor.fetchone()[0]

    # Count modules
    cursor.execute("SELECT COUNT(*) FROM modules")
    stats['modules_count'] = cursor.fetchone()[0]

    # Count cities
    cursor.execute("SELECT COUNT(*) FROM cities")
    stats['cities_count'] = cursor.fetchone()[0]

    # Count topics
    cursor.execute("SELECT COUNT(*) FROM topics")
    stats['topics_count'] = cursor.fetchone()[0]

    # Count teachers
    cursor.execute("SELECT COUNT(*) FROM teachers")
    stats['teachers_count'] = cursor.fetchone()[0]

    conn.close()
    return stats

def get_weekly_lessons(start_date, end_date):
    """Get lessons for weekly report.

    Args:
        start_date (str): Start date in format 'YYYY-MM-DD'
        end_date (str): End date in format 'YYYY-MM-DD'

    Returns:
        dict: Lessons grouped by city and module
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all cities in alphabetical order
    cursor.execute("SELECT id, name FROM cities ORDER BY name")
    cities = cursor.fetchall()

    # Get all modules
    cursor.execute("SELECT id, name FROM modules ORDER BY id")
    modules = cursor.fetchall()

    # Initialize result structure
    result = {}
    for city in cities:
        city_id = city['id']
        city_name = city['name']
        result[city_name] = {}

        for module in modules:
            module_id = module['id']
            module_name = module['name']

            # Get lessons for this city and module in the date range
            query = '''
            SELECT
                l.id,
                m.name as module_name,
                t.title as topic_title,
                c.name as city_name,
                tc.name as teacher_name,
                l.date,
                l.group_name
            FROM lessons l
            JOIN topics t ON l.topic_id = t.id
            JOIN modules m ON t.module_id = m.id
            JOIN cities c ON l.city_id = c.id
            JOIN teachers tc ON l.teacher_id = tc.id
            WHERE l.city_id = ? AND t.module_id = ? AND l.date >= ? AND l.date <= ?
            ORDER BY l.date
            '''

            cursor.execute(query, (city_id, module_id, start_date, end_date))
            lessons = cursor.fetchall()

            # Convert to list of dicts
            lessons_list = []
            for lesson in lessons:
                lessons_list.append({
                    'id': lesson['id'],
                    'module_name': lesson['module_name'],
                    'topic_title': lesson['topic_title'],
                    'city_name': lesson['city_name'],
                    'teacher_name': lesson['teacher_name'],
                    'date': lesson['date'],
                    'group_name': lesson['group_name']
                })

            result[city_name][module_name] = lessons_list

    conn.close()
    return result