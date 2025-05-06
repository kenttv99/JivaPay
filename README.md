# JivaPay

JivaPay — это платформа для обработки платежей, которая позволяет мерчантам интегрировать безопасные и эффективные решения оплаты в свои приложения.

## Документация

- **Backend**
  - [План реализации](backend/README_IMPLEMENTATION_PLAN.md)
  - [Справочник компонентов](backend/README_COMPONENTS.md)
  - [Схема базы данных](backend/README_DB.md)
  - [Утилиты](backend/README_UTILITIES.md)
  - [Трекер реализации](backend/IMPLEMENTATION_TRACKER.md)
- **Frontend**
  - [План архитектуры](frontend/README_ARCHITECTURE_PLAN.md)
  - [Руководство по структуре](frontend_structure_guide.md)
- **Приложения**
  - [Приложение мерчанта](frontend/merchant_app/README.md)
  - [Приложение администратора](frontend/admin_app/README.md)
  - [Приложение поддержки](frontend/support_app/README.md)
  - [Приложение трейдера](frontend/trader_app/README.md)

## Быстрый старт

1. Клонируйте репозиторий.
2. Настройте бэкенд, следуя инструкциям в папке `backend/`.
3. Настройте фронтенд, следуя инструкциям в папке `frontend/`.

## Запуск

### Для разработки

```bash
# Запуск с Docker Compose
docker-compose up -d

# Запуск отдельных серверов
uvicorn backend.servers.merchant.server:app --port 8001 --reload
uvicorn backend.servers.trader.server:app --port 8002 --reload
uvicorn backend.servers.gateway.server:app --port 8003 --reload
uvicorn backend.servers.admin.server:app --port 8004 --reload
uvicorn backend.servers.support.server:app --port 8005 --reload
```