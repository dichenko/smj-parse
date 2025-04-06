"""
Web interface for Smart-J Data Collector.
"""
from flask import Flask, render_template, request, jsonify
import os
from src.config import WEB_HOST, WEB_PORT, ITEMS_PER_PAGE
from src.database.operations import get_cities, get_lessons

app = Flask(__name__)

# Set template folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app.template_folder = template_dir

@app.route('/')
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
    """JUnior module page."""
    # Get cities for filters
    cities = get_cities()
    return render_template('index.html', cities=cities)

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
            transition: background-color 0.3s ease;
        }
        body.matata {
            background-color: #f8f9fa;
        }
        body.kids {
            background-color: #f0f8ff;
        }
        body.junior {
            background-color: #fff8f0;
        }
        .filter-container {
            margin-bottom: 20px;
        }
        .pagination-container {
            margin-top: 20px;
            display: flex;
            justify-content: center;
        }
        .module-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .btn-matata {
            background-color: #007bff;
            border-color: #007bff;
            color: white;
        }
        .btn-kids {
            background-color: #28a745;
            border-color: #28a745;
            color: white;
        }
        .btn-junior {
            background-color: #fd7e14;
            border-color: #fd7e14;
            color: white;
        }
        .btn-matata.active, .btn-matata:hover {
            background-color: #0069d9;
            border-color: #0062cc;
        }
        .btn-kids.active, .btn-kids:hover {
            background-color: #218838;
            border-color: #1e7e34;
        }
        .btn-junior.active, .btn-junior:hover {
            background-color: #e96b02;
            border-color: #d96300;
        }
    </style>
</head>
<body class="matata">
    <div class="container">
        <h1 class="mb-4">Просмотр данных о занятиях</h1>

        <div class="module-buttons">
            <a href="/matata" class="btn btn-matata active" id="btn-matata">Matata</a>
            <a href="/kids" class="btn btn-kids" id="btn-kids">Kids</a>
            <a href="/junior" class="btn btn-junior" id="btn-junior">JUnior</a>
        </div>

        <div class="filter-container row">
            <div class="col-md-6">
                <label for="city-select" class="form-label">Город:</label>
                <select id="city-select" class="form-select">
                    <option value="">Все города</option>
                    {% for city in cities %}
                    <option value="{{ city['id'] }}">{{ city['name'] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-6 d-flex align-items-end">
                <button id="apply-filters" class="btn btn-primary">Применить фильтры</button>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Тема</th>
                        <th>Город</th>
                        <th>Преподаватель</th>
                        <th>Дата</th>
                        <th>Дополнительная информация</th>
                    </tr>
                </thead>
                <tbody id="lessons-table-body">
                    <!-- Данные будут загружены с помощью JavaScript -->
                </tbody>
            </table>
        </div>

        <div class="pagination-container">
            <nav aria-label="Навигация по страницам">
                <ul class="pagination" id="pagination">
                    <!-- Пагинация будет создана с помощью JavaScript -->
                </ul>
            </nav>
        </div>
    </div>

    <script>
        // Текущая страница
        let currentPage = 1;
        // Количество записей на странице
        const perPage = 10;

        // Получаем текущий модуль из URL
        function getCurrentModule() {
            const path = window.location.pathname;
            if (path.includes('/kids')) return 2;
            if (path.includes('/junior')) return 3;
            return 1; // По умолчанию Matata
        }

        // Функция для загрузки данных
        function loadLessons() {
            const moduleId = getCurrentModule();
            const cityId = document.getElementById('city-select').value;

            // Формируем URL для API
            let url = `/api/lessons?page=${currentPage}&per_page=${perPage}`;
            url += `&module_id=${moduleId}`;
            if (cityId) url += `&city_id=${cityId}`;

            // Выполняем запрос к API
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    // Обновляем таблицу
                    updateTable(data.lessons);
                    // Обновляем пагинацию
                    updatePagination(data.pagination);
                })
                .catch(error => {
                    console.error('Ошибка при загрузке данных:', error);
                    alert('Произошла ошибка при загрузке данных. Пожалуйста, попробуйте позже.');
                });
        }

        // Функция для обновления таблицы
        function updateTable(lessons) {
            const tableBody = document.getElementById('lessons-table-body');
            tableBody.innerHTML = '';

            if (lessons.length === 0) {
                const row = document.createElement('tr');
                const cell = document.createElement('td');
                cell.colSpan = 5; // Уменьшили на 1, так как убрали столбец Модуль
                cell.textContent = 'Нет данных для отображения';
                cell.className = 'text-center';
                row.appendChild(cell);
                tableBody.appendChild(row);
                return;
            }

            lessons.forEach(lesson => {
                const row = document.createElement('tr');

                // Тема
                const topicCell = document.createElement('td');
                topicCell.textContent = lesson.topic_title;
                row.appendChild(topicCell);

                // Город
                const cityCell = document.createElement('td');
                cityCell.textContent = lesson.city_name;
                row.appendChild(cityCell);

                // Преподаватель
                const teacherCell = document.createElement('td');
                teacherCell.textContent = lesson.teacher_name;
                row.appendChild(teacherCell);

                // Дата
                const dateCell = document.createElement('td');
                dateCell.textContent = formatDate(lesson.date);
                row.appendChild(dateCell);

                // Дополнительная информация
                const infoCell = document.createElement('td');
                infoCell.textContent = lesson.group_name || '';
                row.appendChild(infoCell);

                tableBody.appendChild(row);
            });
        }

        // Функция для форматирования даты
        function formatDate(dateStr) {
            if (!dateStr) return '';

            // Предполагаем, что дата в формате YYYY-MM-DD
            const parts = dateStr.split('-');
            if (parts.length === 3) {
                return `${parts[2]}.${parts[1]}.${parts[0]}`;
            }

            return dateStr;
        }

        // Функция для обновления пагинации
        function updatePagination(pagination) {
            const paginationElement = document.getElementById('pagination');
            paginationElement.innerHTML = '';

            // Если всего одна страница, не показываем пагинацию
            if (pagination.total_pages <= 1) {
                return;
            }

            // Кнопка "Предыдущая"
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

            // Номера страниц
            const maxPages = 5; // Максимальное количество номеров страниц для отображения
            let startPage = Math.max(1, pagination.current_page - Math.floor(maxPages / 2));
            let endPage = Math.min(pagination.total_pages, startPage + maxPages - 1);

            // Корректируем startPage, если endPage достиг максимума
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

            // Кнопка "Следующая"
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

        // Обработчик события для кнопки "Применить фильтры"
        document.getElementById('apply-filters').addEventListener('click', () => {
            currentPage = 1; // Сбрасываем на первую страницу при изменении фильтров
            loadLessons();
        });

        // Функция для установки активной кнопки модуля
        function setActiveModuleButton() {
            const path = window.location.pathname;
            document.body.className = ''; // Сбрасываем класс body

            // Удаляем класс active у всех кнопок
            document.getElementById('btn-matata').classList.remove('active');
            document.getElementById('btn-kids').classList.remove('active');
            document.getElementById('btn-junior').classList.remove('active');

            // Устанавливаем активную кнопку и класс для body в зависимости от URL
            if (path.includes('/kids')) {
                document.getElementById('btn-kids').classList.add('active');
                document.body.classList.add('kids');
            } else if (path.includes('/junior')) {
                document.getElementById('btn-junior').classList.add('active');
                document.body.classList.add('junior');
            } else {
                document.getElementById('btn-matata').classList.add('active');
                document.body.classList.add('matata');
            }
        }

        // Загружаем данные при загрузке страницы
        document.addEventListener('DOMContentLoaded', () => {
            setActiveModuleButton();
            loadLessons();
        });
    </script>
</body>
</html>
            ''')

if __name__ == '__main__':
    run_web_interface()
