# JivaPay

JivaPay — платформа для обработки платежей, позволяющая торговым и сервисным приложениям обеспечивать безопасный и эффективный приём и выплату средств.

## Документация

- **Бэкенд**
  - [План реализации](backend/README_IMPLEMENTATION_PLAN.md)
  - [Справочник компонентов](backend/README_COMPONENTS.md)
  - [Схема базы данных](backend/README_DB.md)
  - [Утилиты](backend/README_UTILITIES.md)
  - [Трекер реализации](backend/IMPLEMENTATION_TRACKER.md)
- **Фронтенд**
  - [План архитектуры фронтенда](frontend/README_ARCHITECTURE_PLAN.md)
  - [Руководство по структуре фронтенд-проектов](frontend_structure_guide.md)
- **Приложения**
  - [Приложение мерчанта](frontend/merchant_app/README.md)
  - [Приложение администратора](frontend/admin_app/README.md)
  - [Приложение поддержки](frontend/support_app/README.md)
  - [Приложение трейдера](frontend/trader_app/README.md)

## Быстрый старт

1. Клонируйте репозиторий:
   ```bash
   git clone <URL_репозитория>
   ```
2. Скопируйте шаблон файла окружения и заполните переменные:
   ```bash
   cp .env.example .env
   ```
3. Запустите все сервисы в контейнерах Docker:
   ```bash
   docker compose up -d
   ```
4. If database is empty, use the unified management script to initialize and seed:
   ```bash
   # Initialize database schema and seed default data
   docker compose exec merchant_api python -m backend.scripts.manage_db init
   docker compose exec merchant_api python -m backend.scripts.manage_db seed_config
   docker compose exec merchant_api python -m backend.scripts.manage_db seed_data
   ```

## Запуск в режиме разработки

- Запуск через Docker Compose:
  ```bash
  docker compose up -d
  ```
- Запуск отдельных сервисов локально:
  ```bash
  uvicorn backend.servers.merchant.server:app --host 0.0.0.0 --port 8001 --reload
  uvicorn backend.servers.trader.server:app --host 0.0.0.0 --port 8002 --reload
  uvicorn backend.servers.gateway.server:app --host 0.0.0.0 --port 8003 --reload
  uvicorn backend.servers.admin.server:app --host 0.0.0.0 --port 8004 --reload
  uvicorn backend.servers.support.server:app --host 0.0.0.0 --port 8005 --reload
  uvicorn backend.servers.teamlead.server:app --host 0.0.0.0 --port 8006 --reload
  ```

## Структура репозитория

- `/backend` — серверная часть (API, модели, сервисы, утилиты)
- `/frontend` — клиентская часть (SPA-приложения для разных ролей)
- `/docker-compose.yml` — конфигурация Docker Compose для разработки
- `/README.md` — этот файл