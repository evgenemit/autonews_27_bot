# Autonews Telegram bot

Бот упрощает работу с школьным сайтом, а именно:
- позволяет быстро создавать новость на основе поста из telegram-канала;
- загружать изображения в нужный классификатор.

## Установка и запуск

1. Скрипт создания БД (PostgreSQL)
```bash
CREATE DATABASE autonews;
CREATE USER autonews_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE autonews TO autonews_user;
```

2. Добавление администратора в базу

Необходимо создать строку в таблице *admins* содержащую id пользователь в telegram.
```bash
INSERT INTO admins (user_id) VALUES ('0000000000');
```

3. Установка виртуального окружения
```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

4. Переменные окружения

Необходимо создайть файл .env в корне проекта.
```bash
TOKEN={bot_token}
DB_URI=postgresql://{user}:{password}@{host}/{database_name}
SITE_NAME={site_url}
SITE_USERNAME={login}
SITE_PASSWORD={password}
LOGS=false
DEBUG=false
```

5. Запуск
```bash
python3 bot.py
```
