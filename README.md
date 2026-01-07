# Async Weather Microservice

Асинхронный микросервис на базе FastAPI для сбора, хранения и управления данными о погоде. Сервис получает данные из OpenWeatherMap, сохраняет их в PostgreSQL и предоставляет REST API.

## Стек технологий

- Backend: Python 3.11, FastAPI, Pydantic
- Database: PostgreSQL (Asyncpg + SQLAlchemy 2.0)
- Migrations: Alembic
- Async Tasks: Celery + Redis
- Testing: Pytest, Pytest-Asyncio
- Infra: Docker, Docker Compose

## Функциональность

REST API:
- POST /weather/ : Создание записи вручную.
- GET /weather/{city} : Получение актуальной погоды для города.
- PATCH /weather/{id} : Частичное обновление записи.
- DELETE /weather/{id} : Удаление записи.

Фоновые задачи:
- Периодический сбор данных (Celery Beat) для списка городов, указанных в конфиге.

## Установка и запуск

### Предварительные требования
Убедитесь, что установлен Docker и Docker Compose. Также требуется API ключ от OpenWeatherMap.

### Настройка окружения
1. Создайте файл .env на основе примера:
cp .env.example .env

2. Укажите ваш WEATHER_API_KEY в файле .env.

### Запуск через Docker
Выполните команду в корне проекта:
docker-compose up --build -d

Сервис будет доступен по адресу: http://localhost:8000
Документация (Swagger): http://localhost:8000/docs

### Локальный запуск (без Docker)
Если требуется запуск на хосте (нужен локальный Postgres и Redis):

1. Установка зависимостей:
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. Применение миграций:
alembic upgrade head

3. Запуск веб-сервера:
uvicorn src.main:app --reload

4. Запуск воркеров (в отдельных терминалах):
celery -A src.celery_app worker --loglevel=info
celery -A src.celery_app beat --loglevel=info

## Тестирование

Тесты используют изолированную базу данных, которая создается автоматически перед запуском и удаляется после.

Запуск тестов:
pytest

Запуск с подробным выводом:
pytest -v