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
```bash
python run_web.py
```

### Запуск сбора данных
```bash
python collect_data.py
```
