"""
Web interface for Smart-J Data Collector.
"""
from flask import Flask, render_template, request, jsonify, redirect
import datetime
import os
import sqlite3
from src.config import WEB_HOST, WEB_PORT, ITEMS_PER_PAGE
from src.database.operations import get_cities, get_lessons, get_weekly_lessons, get_teachers, get_connection, get_teachers_by_city

app = Flask(__name__)

# Set template folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app.template_folder = template_dir

@app.route('/')
def index():
    """Redirect to Matata page."""
    return redirect('/matata')

@app.route('/matata')
def matata():
    """Matata module page."""
    # Get cities for filters
    cities = get_cities()
    return render_template('index.html', cities=cities)

@app.route('/kids')
def kids():
    """Kids module page."""
    # Get cities for filters
    cities = get_cities()
    return render_template('index.html', cities=cities)

@app.route('/junior')
def junior():
    """Junior module page."""
    # Get cities for filters
    cities = get_cities()
    return render_template('index.html', cities=cities)

@app.route('/tutors')
def tutors():
    """Tutors page."""
    # Get cities for filters
    cities = get_cities()
    # Get teachers for filters
    teachers = get_teachers()
    return render_template('tutors.html', cities=cities, teachers=teachers)

@app.route('/weekly')
@app.route('/weekly/<start_date>')
def weekly(start_date=None):
    """Weekly report page.

    Args:
        start_date (str, optional): Start date of the week in format 'YYYY-MM-DD'.
            If not provided, the most recent completed week is used.
    """
    today = datetime.date.today()

    if start_date:
        # Parse the provided start date
        try:
            year, month, day = map(int, start_date.split('-'))
            start_date = datetime.date(year, month, day)
            # Ensure the start date is a Monday
            if start_date.weekday() != 0:  # Monday is 0
                # Find the Monday of that week
                start_date = start_date - datetime.timedelta(days=start_date.weekday())
            # End date is the Sunday after start_date
            end_date = start_date + datetime.timedelta(days=6)  # Sunday
        except (ValueError, TypeError):
            # If invalid date format, use the most recent completed week
            start_date = None

    if not start_date:
        # Calculate last week's date range (Monday to Sunday)
        # If today is Monday, we want last week
        if today.weekday() == 0:  # Monday is 0
            end_date = today - datetime.timedelta(days=1)  # Sunday
        else:
            # Find the most recent Sunday
            days_since_sunday = today.weekday() + 1 if today.weekday() > 0 else 7
            end_date = today - datetime.timedelta(days=days_since_sunday)

        # Start date is the Monday before end_date
        start_date = end_date - datetime.timedelta(days=6)  # Monday

    # Generate a list of available weeks (12 weeks back from today)
    available_weeks = []

    # Find the most recent completed week's start date (Monday)
    if today.weekday() == 0:  # If today is Monday
        most_recent_monday = today - datetime.timedelta(days=7)  # Last Monday
    else:
        days_since_monday = today.weekday()
        most_recent_monday = today - datetime.timedelta(days=days_since_monday)

    current_week_start = most_recent_monday
    for i in range(12):  # Show up to 12 weeks
        week_end = current_week_start + datetime.timedelta(days=6)

        # Skip future weeks
        if current_week_start > today:
            break

        # Add week to the list
        available_weeks.append({
            'start_date': current_week_start.strftime('%Y-%m-%d'),
            'end_date': week_end.strftime('%Y-%m-%d'),
            'display': f"{current_week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')}",
            'active': current_week_start == start_date
        })

        # Move to the previous week
        current_week_start = current_week_start - datetime.timedelta(days=7)

    # Format dates for database query
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Get weekly lessons
    weekly_data = get_weekly_lessons(start_date_str, end_date_str)

    # Generate calendar data for the month containing the selected week
    calendar_data = generate_calendar_data(start_date, end_date)

    return render_template('weekly.html',
                           weekly_data=weekly_data,
                           start_date=start_date.strftime('%d.%m.%Y'),
                           end_date=end_date.strftime('%d.%m.%Y'),
                           available_weeks=available_weeks,
                           calendar_data=calendar_data,
                           selected_start_date=start_date_str)

def generate_calendar_data(start_date, end_date):
    """Generate calendar data for the month(s) containing the selected week.

    Args:
        start_date (datetime.date): Start date of the selected week
        end_date (datetime.date): End date of the selected week

    Returns:
        list: List of calendar data for each month
    """
    # Check if the week spans two months
    spans_two_months = start_date.month != end_date.month

    # List to store calendar data for each month
    calendars = []

    # Function to generate calendar for a specific month
    def generate_month_calendar(year, month, start_date, end_date):
        # Get the first day of the month
        first_day = datetime.date(year, month, 1)

        # Get the last day of the month
        if month == 12:
            last_day = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

        # Get the weekday of the first day (0 = Monday, 6 = Sunday)
        first_weekday = first_day.weekday()

        # Calculate the number of days in the month
        days_in_month = last_day.day

        # Generate calendar grid
        calendar_grid = []
        day = 1

        # Add empty cells for days before the first day of the month
        for i in range(first_weekday):
            calendar_grid.append({
                'day': None,
                'in_selected_week': False,
                'is_today': False
            })

        # Add cells for each day of the month
        today = datetime.date.today()
        for i in range(days_in_month):
            current_date = datetime.date(year, month, day)
            calendar_grid.append({
                'day': day,
                'in_selected_week': start_date <= current_date <= end_date,
                'is_today': current_date == today
            })
            day += 1

        # Add empty cells for days after the last day of the month
        while len(calendar_grid) % 7 != 0:
            calendar_grid.append({
                'day': None,
                'in_selected_week': False,
                'is_today': False
            })

        # Split the grid into weeks
        weeks = []
        for i in range(0, len(calendar_grid), 7):
            weeks.append(calendar_grid[i:i+7])

        # Get month name
        month_name = datetime.date(year, month, 1).strftime('%B %Y')

        return {
            'month_name': month_name,
            'weeks': weeks
        }

    if spans_two_months:
        # If the week spans two months, generate calendars for both months
        # Add the end_date month first (newer month)
        calendars.append(generate_month_calendar(end_date.year, end_date.month, start_date, end_date))
        # Then add the start_date month (older month)
        calendars.append(generate_month_calendar(start_date.year, start_date.month, start_date, end_date))
    else:
        # If the week is within a single month, generate just one calendar
        calendars.append(generate_month_calendar(start_date.year, start_date.month, start_date, end_date))

    return calendars

@app.route('/api/lessons')
def api_lessons():
    """API for getting lessons with filtering and pagination."""
    # Get request parameters
    module_id = request.args.get('module_id', type=int)
    city_id = request.args.get('city_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', ITEMS_PER_PAGE, type=int)

    # Get lessons from database
    result = get_lessons(module_id, city_id, page, per_page)

    # Convert lessons to list of dictionaries
    lessons_list = []
    for lesson in result['lessons']:
        lessons_list.append({
            'id': lesson['id'],
            'module_name': lesson['module_name'],
            'topic_title': lesson['topic_title'],
            'city_name': lesson['city_name'],
            'teacher_name': lesson['teacher_name'],
            'date': lesson['date'],
            'group_name': lesson['group_name']
        })

    # Return results as JSON
    return jsonify({
        'lessons': lessons_list,
        'pagination': result['pagination']
    })

@app.route('/api/teacher_lessons')
def api_teacher_lessons():
    """API for getting lessons by teacher."""
    # Get request parameters
    teacher_id = request.args.get('teacher_id', type=int)
    city_id = request.args.get('city_id', type=int)
    
    if not teacher_id:
        return jsonify({'error': 'Teacher ID is required'}), 400
    
    # Get lessons from database
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get teacher name
    cursor.execute("SELECT name FROM teachers WHERE id = ?", (teacher_id,))
    teacher = cursor.fetchone()
    if not teacher:
        conn.close()
        return jsonify({'error': 'Teacher not found'}), 404
    
    teacher_name = teacher['name']
    
    query = '''
    SELECT
        l.id,
        m.id as module_id,
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
    WHERE l.teacher_id = ?
    '''
    
    params = [teacher_id]
    
    if city_id:
        query += ' AND l.city_id = ?'
        params.append(city_id)
    
    # Add sorting by date (newest first)
    query += ' ORDER BY l.date DESC'
    
    cursor.execute(query, params)
    lessons = cursor.fetchall()
    
    # Group lessons by module
    modules = {}
    
    # Get all modules first
    cursor.execute("SELECT id, name FROM modules ORDER BY id")
    all_modules = cursor.fetchall()
    
    for module in all_modules:
        modules[module['name']] = {
            'count': 0,
            'lessons': []
        }
    
    # Add lessons to their modules
    for lesson in lessons:
        module_name = lesson['module_name']
        
        if module_name not in modules:
            modules[module_name] = {
                'count': 0,
                'lessons': []
            }
        
        modules[module_name]['count'] += 1
        modules[module_name]['lessons'].append({
            'id': lesson['id'],
            'module_name': lesson['module_name'],
            'topic_title': lesson['topic_title'],
            'city_name': lesson['city_name'],
            'teacher_name': lesson['teacher_name'],
            'date': lesson['date'],
            'group_name': lesson['group_name']
        })
    
    conn.close()
    
    # Return results as JSON
    return jsonify({
        'teacher_name': teacher_name,
        'modules': modules
    })

@app.route('/api/teachers_by_city')
def api_teachers_by_city():
    """API for getting teachers filtered by city."""
    city_id = request.args.get('city_id', type=int)
    
    # Get teachers from database
    teachers = get_teachers_by_city(city_id)
    
    # Convert to list of dicts
    teachers_list = []
    for teacher in teachers:
        teachers_list.append({
            'id': teacher['id'],
            'name': teacher['name']
        })
    
    return jsonify({
        'teachers': teachers_list
    })

def run_web_interface(host=None, port=None, debug=False):
    """Run web interface.
    
    Args:
        host (str, optional): Host to listen on. Defaults to config value.
        port (int, optional): Port to listen on. Defaults to config value.
        debug (bool, optional): Run in debug mode. Defaults to False.
    """
    # Create templates directory if it doesn't exist
    os.makedirs(app.template_folder, exist_ok=True)
    
    # Run the app
    app.run(
        host=host or WEB_HOST,
        port=port or WEB_PORT,
        debug=debug
    )

if __name__ == '__main__':
    run_web_interface()
