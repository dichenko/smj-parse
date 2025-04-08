# Smart-J Data Collector

Скрипт для сбора данных о проведенных занятиях с сайта http://my.smart-j.ru/ и сохранения их в базу данных SQLite.

## Структура проекта


- `src/` - Директория с исходным кодом
  - `database/` - Модули для работы с базой данных
    - `schema.py` - Создание структуры базы данных
    - `operations.py` - Операции с базой данных
  - `parsers/` - Модули для сбора данных
    - `auth.py` - Авторизация на сайте
    - `lesson_parser.py` - Парсинг данных о занятиях
  - `web/` - Веб-интерфейс
    - `app.py` - Flask приложение
    - `templates/` - HTML шаблоны для веб-интерфейса
      - `index.html` - Шаблон основной страницы с данными занятий
      - `weekly.html` - Шаблон недельного отчета
      - `tutors.html` - Шаблон страницы тьюторов (преподавателей)
  - `utils/` - Вспомогательные функции
    - `logger.py` - Настройка логирования
  - `config.py` - Конфигурационные параметры
- `requirements.txt` - Список зависимостей
- `setup.py` - Скрипт для установки пакета
- `run_web.py` - Отдельный скрипт для запуска веб-интерфейса (совместим с WSGI-серверами)
- `collect_data.py` - Отдельный скрипт для сбора данных
- `run_smartj_web.bat` - Batch-файл для запуска веб-интерфейса в Windows

## Установка

1. Установите Python 3.7 или выше
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

## Использование

### 1. Сбор данных

```bash
python collect_data.py
```

### 2. Запуск веб-интерфейса

```bash
python run_web.py
```

### 3. Запуск только веб-интерфейса в Windows

```bash
run_smartj_web.bat
```

### 4. Запуск с помощью Gunicorn (для продакшн)

Приложение совместимо с WSGI-серверами, такими как Gunicorn:

```bash
gunicorn run_web:app -b 0.0.0.0:8080
```

После запуска веб-интерфейса любым из способов, откройте браузер и перейдите по адресу http://127.0.0.1:8080/

## Функциональность

### Сбор данных

Модуль `src.parsers.lesson_parser`:
- Авторизуется на сайте http://my.smart-j.ru/
- Скачивает данные с трех страниц (Matata, Kids, JUnior)
- Извлекает темы занятий из заголовков строк таблицы
- Определяет города из заголовков столбцов таблицы
- Находит проведенные занятия по зеленым ячейкам с фоном #96fe96
- Извлекает информацию о преподавателе и дате из всплывающих окон (popover)
- Сохраняет данные в SQLite, избегая дублирования

### Веб-интерфейс

Веб-интерфейс (`src.web.app`) предоставляет следующие возможности:

#### Основной просмотр занятий
- Навигационное меню для выбора модуля (Matata, Kids, Junior, Недельный, Тьюторы)
- Фильтрация занятий по модулю и городу
- Просмотр данных с пагинацией (10 занятий на странице)
- Сортировка занятий по дате (от новых к старым)

#### Недельный отчет
- Просмотр данных за конкретную неделю
- Выбор недели из календаря
- Отображение календаря на текущий месяц
- Агрегированные данные по всем модулям

#### Страница тьюторов (преподавателей)
- Выбор преподавателя из списка
- Фильтрация преподавателей по городу
- Просмотр всех занятий, проведенных выбранным преподавателем
- Группировка данных по модулям
- Пагинация результатов (10 занятий на страницу)

## Структура базы данных

База данных SQLite состоит из следующих таблиц:

- `modules` - Модули обучения (Matata, Kids, JUnior)
  - `id` - Уникальный идентификатор
  - `name` - Название модуля
  - `url` - URL страницы с данными модуля

- `cities` - Города
  - `id` - Уникальный идентификатор
  - `name` - Название города

- `topics` - Темы занятий
  - `id` - Уникальный идентификатор
  - `module_id` - Идентификатор модуля
  - `title` - Название темы

- `teachers` - Преподаватели
  - `id` - Уникальный идентификатор
  - `name` - Имя преподавателя

- `lessons` - Проведенные занятия
  - `id` - Уникальный идентификатор
  - `topic_id` - Идентификатор темы
  - `city_id` - Идентификатор города
  - `teacher_id` - Идентификатор преподавателя
  - `date` - Дата проведения занятия
  - `group_name` - Название группы
  - `created_at` - Дата и время добавления записи в базу данных

## API-эндпоинты

Веб-интерфейс предоставляет следующие API-эндпоинты:

- `/api/lessons` - Получение занятий с фильтрацией и пагинацией
  - Параметры:
    - `module_id` - ID модуля
    - `city_id` - ID города
    - `page` - Номер страницы
    - `per_page` - Количество записей на странице

- `/api/teacher_lessons` - Получение занятий по преподавателю
  - Параметры:
    - `teacher_id` - ID преподавателя (обязательный)
    - `city_id` - ID города
    - `page` - Номер страницы
    - `per_page` - Количество записей на странице

- `/api/teachers_by_city` - Получение списка преподавателей по городу
  - Параметры:
    - `city_id` - ID города

## Логирование

Логи работы скрипта сохраняются в директорию `logs/`.
