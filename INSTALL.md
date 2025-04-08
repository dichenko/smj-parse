# Руководство по установке Smart-J Data Collector

## Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/username/smj-parse.git
cd smj-parse
```

2. Создать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Linux/Mac
# или
venv\Scripts\activate  # На Windows
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Создать файл .env со следующими параметрами:
```
SMARTJ_USERNAME=your_username
SMARTJ_PASSWORD=your_password
```

## Запуск веб-интерфейса как службы (Linux, systemd)

### Вариант 1: Через Python

1. Отредактировать файл службы `smartj-web.service`:
   - Указать правильные пути к директории проекта и виртуальному окружению
   - При необходимости изменить пользователя, от имени которого будет запущена служба

2. Копировать файл в директорию системных служб:
```bash
sudo cp smartj-web.service /etc/systemd/system/
```

3. Включить и запустить службу:
```bash
sudo systemctl daemon-reload
sudo systemctl enable smartj-web.service
sudo systemctl start smartj-web.service
```

4. Проверить статус службы:
```bash
sudo systemctl status smartj-web.service
```

### Вариант 2: Через Gunicorn (рекомендуется для production)

1. Установить Gunicorn:
```bash
pip install gunicorn
```

2. Создать файл службы `smartj-web-gunicorn.service`:
```ini
[Unit]
Description=Smart-J Web Interface (Gunicorn)
After=network.target

[Service]
User=your_username
Group=your_group
WorkingDirectory=/path/to/smj-parse
Environment="PATH=/path/to/smj-parse/venv/bin"
ExecStart=/path/to/smj-parse/venv/bin/gunicorn run_web:app -b 0.0.0.0:8080 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Копировать файл в директорию системных служб и запустить:
```bash
sudo cp smartj-web-gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smartj-web-gunicorn.service
sudo systemctl start smartj-web-gunicorn.service
```

## Настройка регулярного сбора данных (Linux, cron)

1. Отредактировать файл `smartj-cron`:
   - Указать правильные пути к директории проекта и виртуальному окружению
   - При необходимости изменить расписание запуска

2. Добавить задачу в crontab:
```bash
crontab -e
```

3. Вставить содержимое файла `smartj-cron` в конец файла и сохранить

## Ручной запуск компонентов

### Запуск веб-интерфейса

#### Через встроенный сервер Flask (для разработки)
```bash
python run_web.py
```

#### Через Gunicorn (для production)
```bash
gunicorn run_web:app -b 0.0.0.0:8080
```

### Запуск сбора данных
```bash
python collect_data.py
```

## Доступ к веб-интерфейсу

После запуска веб-интерфейса, он будет доступен по адресу:
- Локально: http://127.0.0.1:8080/
- По локальной сети: http://your_server_ip:8080/ (если запущен с параметром 0.0.0.0)

### Доступные страницы:

- `/matata` - Основная страница с данными модуля Matata
- `/kids` - Страница с данными модуля Kids
- `/junior` - Страница с данными модуля Junior
- `/weekly` - Недельный отчет по всем модулям
- `/tutors` - Страница с информацией о преподавателях

## API-эндпоинты

Веб-интерфейс предоставляет следующие API для получения данных:

- `/api/lessons` - Получение занятий с фильтрацией и пагинацией
- `/api/teacher_lessons` - Получение занятий по конкретному преподавателю
- `/api/teachers_by_city` - Получение списка преподавателей по городу
