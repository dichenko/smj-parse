"""
Lesson parser module for Smart-J Data Collector.
"""
import re
import logging
import time
from bs4 import BeautifulSoup
from src.config import HEADERS, MODULE_URLS

def clean_teacher_name(name):
    """
    Clean teacher name by removing extra whitespace, newlines, and other unwanted characters.

    Args:
        name (str): The raw teacher name

    Returns:
        str: The cleaned teacher name
    """
    if not name:
        return ""

    # Convert to string if it's not already
    name = str(name)

    # Replace newlines and tabs with spaces
    name = name.replace('\n', ' ').replace('\t', ' ')

    # Remove HTML tags if present
    name = re.sub(r'<[^>]+>', ' ', name)

    # Replace multiple spaces with a single space
    name = re.sub(r'\s+', ' ', name)

    # Remove leading/trailing whitespace
    name = name.strip()

    return name

def parse_lesson_data(popover_content):
    """Extract lesson data from popover content."""
    # Initialize data dictionary
    data = {
        'teacher': "Неизвестный преподаватель",
        'date': "Неизвестная дата",
        'city': "Неизвестный город",
        'group_name': None
    }

    # Check if popover_content is not empty
    if not popover_content or len(popover_content.strip()) < 5:
        logging.warning(f"Empty popover content: {popover_content}")
        return data

    # Look for date using regular expressions
    date_patterns = [
        r'\\b(\\d{2}\\.\\d{2}\\.\\d{4})\\b',  # DD.MM.YYYY
        r'\\b(\\d{1,2}\\.\\d{1,2}\\.\\d{4})\\b',  # D.M.YYYY
        r'\\b(\\d{4}-\\d{2}-\\d{2})\\b'   # YYYY-MM-DD
    ]

    for pattern in date_patterns:
        date_matches = re.findall(pattern, popover_content)
        if date_matches:
            date_str = date_matches[0]
            # Convert date to standard format YYYY-MM-DD
            try:
                if '-' in date_str:  # Already in YYYY-MM-DD format
                    data['date'] = date_str
                else:  # In DD.MM.YYYY format
                    date_parts = date_str.split('.')
                    if len(date_parts) == 3:
                        data['date'] = f"{date_parts[2]}-{date_parts[1].zfill(2)}-{date_parts[0].zfill(2)}"
                    else:
                        data['date'] = date_str
            except Exception as e:
                logging.warning(f"Error processing date {date_str}: {e}")
                data['date'] = date_str
            break

    # Look for city (branch)
    city_patterns = [
        r'\\bГород[:\\s]+(.*?)(?:<|\\n|$)',
        r'\\bГород[^<>]*?<[^<>]*?>(.*?)<',
        r'\\bГород\\s*:\\s*([^<>\\n]+)',
        r'\\bФилиал[:\\s]+(.*?)(?:<|\\n|$)',
        r'\\bФилиал[^<>]*?<[^<>]*?>(.*?)<',
        r'\\bФилиал\\s*:\\s*([^<>\\n]+)',
        r'<tr><td>\\s*Филиал\\s*:?\\s*</td>\\s*<td>\\s*<b>\\s*([^<>]+?)\\s*</b>\\s*</td>'
    ]

    for pattern in city_patterns:
        city_matches = re.findall(pattern, popover_content, re.DOTALL | re.IGNORECASE)
        if city_matches:
            # Take first match and remove extra whitespace
            city_name = re.sub(r'\\s+', ' ', city_matches[0].strip())
            if city_name and len(city_name) > 2:
                data['city'] = city_name
                logging.debug(f"Found city: {city_name}")
                break

    # Look for teacher
    teacher_patterns = [
        r'\\bПреподаватель[:\\s]+(.*?)(?:<|\\n|$)',
        r'\\bПреподаватель[^<>]*?<[^<>]*?>(.*?)<',
        r'<b>([^<>]+?)</b>'
    ]

    for pattern in teacher_patterns:
        teacher_matches = re.findall(pattern, popover_content, re.DOTALL | re.IGNORECASE)
        if teacher_matches:
            # Take first match and clean the teacher name
            teacher_name = clean_teacher_name(teacher_matches[0])
            if teacher_name and len(teacher_name) > 2:
                data['teacher'] = teacher_name
                logging.debug(f"Found teacher: {teacher_name}")
                break

    # Look for group information
    group_patterns = [
        r'Группа:\s*([^|<\n]+)',
        r'Группа[^:]*:\s*([^|<\n]+)'
    ]

    for pattern in group_patterns:
        group_matches = re.findall(pattern, popover_content, re.DOTALL | re.IGNORECASE)
        if group_matches:
            # Take first match and clean it
            group_name = group_matches[0].strip()
            if group_name:
                data['group_name'] = group_name
                logging.debug(f"Found group: {group_name}")
                break

    # If there's an HTML table, try to extract data from it
    if '<table' in popover_content:
        try:
            soup = BeautifulSoup(popover_content, 'html.parser')
            table = soup.find('table')

            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        key = cells[0].get_text().strip().rstrip(':')
                        value = cells[1].get_text().strip()

                        # Look for teacher, date, city and group
                        key_lower = key.lower()
                        if ('преподаватель' in key_lower or 'учитель' in key_lower) and value:
                            data['teacher'] = clean_teacher_name(value)
                            logging.debug(f"Found teacher in table: {data['teacher']}")
                        elif 'дат' in key_lower and value:
                            # Convert date to standard format YYYY-MM-DD
                            try:
                                date_parts = value.split('.')
                                if len(date_parts) == 3:
                                    data['date'] = f"{date_parts[2]}-{date_parts[1].zfill(2)}-{date_parts[0].zfill(2)}"
                                else:
                                    data['date'] = value
                            except Exception:
                                data['date'] = value
                            logging.debug(f"Found date in table: {value}")
                        elif ('город' in key_lower or 'филиал' in key_lower) and value:
                            data['city'] = value
                            logging.debug(f"Found city/branch in table: {value}")
                        elif 'групп' in key_lower and value:
                            data['group_name'] = value
                            logging.debug(f"Found group in table: {value}")
                        # Look for group information in other fields
                        elif any(keyword in key_lower for keyword in ['класс', 'клаc', 'кл.']) and value:
                            data['group_name'] = value
                            logging.debug(f"Found class/group in table: {value}")
        except Exception as e:
            logging.warning(f"Error processing HTML table: {e}")

    # Extract group name from popover content
    group_pattern = r'Группа:\s*([^|<\n]+)'  # Группа: xxx
    group_matches = re.findall(group_pattern, popover_content, re.IGNORECASE)
    if group_matches and group_matches[0].strip():
        data['group_name'] = group_matches[0].strip()
        logging.debug(f"Found group in popover content: {data['group_name']}")

    return data

def extract_data_from_page(session, module_id, module_url):
    """Extract lesson data from the specified page."""
    try:
        logging.info(f"Getting data from page: {module_url}")
        response = session.get(module_url, headers=HEADERS, verify=False, timeout=15)
        logging.info(f"Response status: {response.status_code}")

        # Save page for debugging
        with open(f"data/module_{module_id}_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        # Parse page with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for main table with data
        main_table = soup.find('table', class_='plan-rep')
        if not main_table:
            logging.error("Main data table not found")
            return []

        logging.info("Found main data table")

        # Check if there's a header row
        headers_row = main_table.find('tr')
        if not headers_row:
            logging.error("Header row not found")
            return []

        # Get all table rows
        rows = main_table.find_all('tr')

        # List to store lesson data
        lessons_data = []

        # Process each row, starting from the second one (skip header)
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) < 2:  # Must have at least a topic cell and one city cell
                continue

            # Get lesson topic from first cell
            topic_cell = cells[0]
            topic_title = topic_cell.get_text().strip()
            logging.info(f"Processing topic: {topic_title}")

            # Process all cells except the first one (topic)
            for cell in cells[1:]:
                # Look for divs with class "bull" and green background
                green_divs = cell.find_all('div', class_='bull', style=lambda s: s and 'background:#96fe96' in s)

                for div in green_divs:
                    # Check if div has attribute data-toggle="popover"
                    if div.get('data-toggle') == 'popover':
                        # Extract data from data-content attribute
                        popover_content = div.get('data-content', '')
                        logging.debug(f"Popover content: {popover_content[:100]}...")

                        # Parse data from popover
                        lesson_data = parse_lesson_data(popover_content)

                        # Add topic and module information
                        lesson_data['topic'] = topic_title
                        lesson_data['module_id'] = module_id

                        # City should already be extracted from popover
                        if 'city' in lesson_data and lesson_data['city'] != "Неизвестный город":
                            lessons_data.append(lesson_data)
                            logging.info(f"Found lesson: {lesson_data['city']} - {topic_title} - {lesson_data['date']}")
                        else:
                            logging.warning(f"Could not determine city for lesson: {topic_title} - {lesson_data['date']}")

        return lessons_data

    except Exception as e:
        logging.error(f"Error getting data from page {module_url}: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return []

def collect_all_data(session):
    """Collect data from all modules."""
    all_lessons_data = []

    for module_id, (module_name, module_url) in enumerate(MODULE_URLS.items(), 1):
        logging.info(f"Processing module: {module_name}")

        # Extract data from module page
        module_lessons = extract_data_from_page(session, module_id, module_url)
        all_lessons_data.extend(module_lessons)

        # Pause between requests to avoid overloading the server
        time.sleep(2)

    return all_lessons_data
