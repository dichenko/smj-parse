"""
Web interface for Smart-J Data Collector.
"""
from flask import Flask, render_template, request, jsonify
import os
from src.config import WEB_HOST, WEB_PORT, ITEMS_PER_PAGE
from src.database.operations import get_modules, get_cities, get_lessons

app = Flask(__name__)

# Set template folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app.template_folder = template_dir

@app.route('/')
def index():
    """Main page."""
    # Get modules and cities for filters
    modules = get_modules()
    cities = get_cities()

    return render_template('index.html', modules=modules, cities=cities)

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

def run_web_interface():
    """Run web interface."""
    # Create templates directory if it doesn't exist
    os.makedirs(template_dir, exist_ok=True)

    # Create index.html template
    create_index_template()

    # Run Flask app
    app.run(host=WEB_HOST, port=WEB_PORT, debug=True)

def create_index_template():
    """Create index.html template."""
    template_path = os.path.join(app.template_folder, 'index.html')

    # Create template only if it doesn't exist
    if not os.path.exists(template_path):
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write('''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Просмотр данных о занятиях</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding: 20px;
        }
        .filter-container {
            margin-bottom: 20px;
        }
        .pagination-container {
            margin-top: 20px;
            display: flex;
            justify-content: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Просмотр данных о занятиях</h1>

        <div class="filter-container row">
            <div class="col-md-4">
                <label for="module-select" class="form-label">Модуль:</label>
                <select id="module-select" class="form-select">
                    <option value="">Все модули</option>
                    {% for module in modules %}
                    <option value="{{ module['id'] }}">{{ module['name'] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-4">
                <label for="city-select" class="form-label">Город:</label>
                <select id="city-select" class="form-select">
                    <option value="">Все города</option>
                    {% for city in cities %}
                    <option value="{{ city['id'] }}">{{ city['name'] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-4 d-flex align-items-end">
                <button id="apply-filters" class="btn btn-primary">Применить фильтры</button>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Модуль</th>
                        <th>Тема</th>
                        <th>Город</th>
                        <th>Преподаватель</th>
                        <th>Дата</th>
                        <th>Группа</th>
                    </tr>
                </thead>
                <tbody id="lessons-table-body">
                    <!-- Data will be loaded with JavaScript -->
                </tbody>
            </table>
        </div>

        <div class="pagination-container">
            <nav aria-label="Навигация по страницам">
                <ul class="pagination" id="pagination">
                    <!-- Pagination will be created with JavaScript -->
                </ul>
            </nav>
        </div>
    </div>

    <script>
        // Current page
        let currentPage = 1;
        // Items per page
        const perPage = 10;

        // Function to load lessons
        function loadLessons() {
            const moduleId = document.getElementById('module-select').value;
            const cityId = document.getElementById('city-select').value;

            // Build API URL
            let url = `/api/lessons?page=${currentPage}&per_page=${perPage}`;
            if (moduleId) url += `&module_id=${moduleId}`;
            if (cityId) url += `&city_id=${cityId}`;

            // Make API request
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    // Update table
                    updateTable(data.lessons);
                    // Update pagination
                    updatePagination(data.pagination);
                })
                .catch(error => {
                    console.error('Error loading data:', error);
                    alert('An error occurred while loading data. Please try again later.');
                });
        }

        // Function to update table
        function updateTable(lessons) {
            const tableBody = document.getElementById('lessons-table-body');
            tableBody.innerHTML = '';

            if (lessons.length === 0) {
                const row = document.createElement('tr');
                const cell = document.createElement('td');
                cell.colSpan = 6;
                cell.textContent = 'Нет данных для отображения';
                cell.className = 'text-center';
                row.appendChild(cell);
                tableBody.appendChild(row);
                return;
            }

            lessons.forEach(lesson => {
                const row = document.createElement('tr');

                // Module
                const moduleCell = document.createElement('td');
                moduleCell.textContent = lesson.module_name;
                row.appendChild(moduleCell);

                // Topic
                const topicCell = document.createElement('td');
                topicCell.textContent = lesson.topic_title;
                row.appendChild(topicCell);

                // City
                const cityCell = document.createElement('td');
                cityCell.textContent = lesson.city_name;
                row.appendChild(cityCell);

                // Teacher
                const teacherCell = document.createElement('td');
                teacherCell.textContent = lesson.teacher_name;
                row.appendChild(teacherCell);

                // Date
                const dateCell = document.createElement('td');
                dateCell.textContent = formatDate(lesson.date);
                row.appendChild(dateCell);

                // Group
                const groupCell = document.createElement('td');
                groupCell.textContent = lesson.group_name || '';
                row.appendChild(groupCell);

                tableBody.appendChild(row);
            });
        }

        // Function to format date
        function formatDate(dateStr) {
            if (!dateStr) return '';

            // Assuming date is in YYYY-MM-DD format
            const parts = dateStr.split('-');
            if (parts.length === 3) {
                return `${parts[2]}.${parts[1]}.${parts[0]}`;
            }

            return dateStr;
        }

        // Function to update pagination
        function updatePagination(pagination) {
            const paginationElement = document.getElementById('pagination');
            paginationElement.innerHTML = '';

            // If only one page, don't show pagination
            if (pagination.total_pages <= 1) {
                return;
            }

            // Previous button
            const prevItem = document.createElement('li');
            prevItem.className = `page-item ${pagination.current_page === 1 ? 'disabled' : ''}`;
            const prevLink = document.createElement('a');
            prevLink.className = 'page-link';
            prevLink.href = '#';
            prevLink.textContent = 'Предыдущая';
            prevLink.addEventListener('click', (e) => {
                e.preventDefault();
                if (pagination.current_page > 1) {
                    currentPage = pagination.current_page - 1;
                    loadLessons();
                }
            });
            prevItem.appendChild(prevLink);
            paginationElement.appendChild(prevItem);

            // Page numbers
            const maxPages = 5; // Maximum number of page numbers to display
            let startPage = Math.max(1, pagination.current_page - Math.floor(maxPages / 2));
            let endPage = Math.min(pagination.total_pages, startPage + maxPages - 1);

            // Adjust startPage if endPage reached maximum
            startPage = Math.max(1, endPage - maxPages + 1);

            for (let i = startPage; i <= endPage; i++) {
                const pageItem = document.createElement('li');
                pageItem.className = `page-item ${i === pagination.current_page ? 'active' : ''}`;
                const pageLink = document.createElement('a');
                pageLink.className = 'page-link';
                pageLink.href = '#';
                pageLink.textContent = i;
                pageLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    currentPage = i;
                    loadLessons();
                });
                pageItem.appendChild(pageLink);
                paginationElement.appendChild(pageItem);
            }

            // Next button
            const nextItem = document.createElement('li');
            nextItem.className = `page-item ${pagination.current_page === pagination.total_pages ? 'disabled' : ''}`;
            const nextLink = document.createElement('a');
            nextLink.className = 'page-link';
            nextLink.href = '#';
            nextLink.textContent = 'Следующая';
            nextLink.addEventListener('click', (e) => {
                e.preventDefault();
                if (pagination.current_page < pagination.total_pages) {
                    currentPage = pagination.current_page + 1;
                    loadLessons();
                }
            });
            nextItem.appendChild(nextLink);
            paginationElement.appendChild(nextItem);
        }

        // Event handler for "Apply filters" button
        document.getElementById('apply-filters').addEventListener('click', () => {
            currentPage = 1; // Reset to first page when changing filters
            loadLessons();
        });

        // Load lessons when page loads
        document.addEventListener('DOMContentLoaded', () => {
            loadLessons();
        });
    </script>
</body>
</html>
            ''')

if __name__ == '__main__':
    run_web_interface()
