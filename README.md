# JivaPay

JivaPay — это современная платформа для обработки платежей, которая помогает торговым и сервисным приложениям безопасно принимать и выплачивать деньги.

## Документация

### Бэкенд
- [Основная документация по бэкенду](docs/README_MAIN_BACKEND.md) — всё о серверной части
- [Схема базы данных](docs/README_DATABASE.md) — структура и связи в БД
- [Трекер реализации](docs/IMPLEMENTATION_TRACKER.md) — что уже сделано и что в планах
- [План тестирования](docs/TEST_PLAN.md) — как мы тестируем систему

### Фронтенд
- [Архитектура фронтенда](docs/README_ARCHITECTURE_FRONTEND.md) — как устроен клиент
- [Руководство по структуре фронтенд-проектов](frontend_structure_guide.md) — как организованы фронтенд-приложения

### Приложения
- [Приложение мерчанта](frontend/merchant_app/README.md) — для магазинов
- [Приложение администратора](frontend/admin_app/README.md) — для управления системой
- [Приложение поддержки](frontend/support_app/README.md) — для работы с пользователями
- [Приложение трейдера](frontend/trader_app/README.md) — для трейдеров

## Быстрый старт

1. Клонируем репозиторий:
   ```bash
   git clone <URL_репозитория>
   ```

2. Настраиваем окружение:
   ```bash
   cp .env.example .env
   # Отредактируйте .env под свои нужды
   ```

3. Запускаем все сервисы через Docker:
   ```bash
   docker compose up -d
   ```

4. Инициализируем базу данных:
   ```bash
   # Создаем структуру БД и заполняем начальными данными
   docker compose exec merchant_api python -m backend.scripts.manage_db init
   docker compose exec merchant_api python -m backend.scripts.manage_db seed-config
   docker compose exec merchant_api python -m backend.scripts.manage_db seed_reference # Валюты
   docker compose exec merchant_api python -m backend.scripts.manage_db seed_data # Роли и админ
   docker compose exec merchant_api python -m backend.scripts.manage_db seed_payment_refs # Методы оплаты и банки
   ```

## Разработка

### Запуск через Docker
```bash
docker compose up -d
```

### Локальный запуск сервисов
```bash
# Запускаем сервисы с поддержкой асинхронной работы с БД
uvicorn backend.servers.merchant.server:app --host 0.0.0.0 --port 8001 --reload --workers 4
uvicorn backend.servers.trader.server:app --host 0.0.0.0 --port 8002 --reload --workers 4
uvicorn backend.servers.gateway.server:app --host 0.0.0.0 --port 8003 --reload --workers 4
uvicorn backend.servers.admin.server:app --host 0.0.0.0 --port 8004 --reload --workers 4
uvicorn backend.servers.support.server:app --host 0.0.0.0 --port 8005 --reload --workers 4
uvicorn backend.servers.teamlead.server:app --host 0.0.0.0 --port 8006 --reload --workers 4
```

## Структура проекта

- `/backend` — серверная часть
  - `/database` — работа с БД
  - `/api_routers` — API эндпоинты
  - `/services` — бизнес-логика
  - `/utils` — вспомогательные функции
- `/frontend` — клиентские приложения
- `/docker-compose.yml` — настройка Docker
- `/README.md` — этот файл

## Требования

- Python 3.9+
- PostgreSQL 14+ с асинхронной поддержкой
- asyncpg для работы с PostgreSQL
- SQLAlchemy 2.0+ с асинхронными операциями