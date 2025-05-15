# Трекер Реализации Backend

Этот документ отслеживает прогресс реализации компонентов бэкенда, как описано в `README_IMPLEMENTATION_PLAN.md`.

Используйте флажки для отметки статуса каждой задачи:
- [ ] Не начато
- [x] Готово
- [/] В процессе (Опционально, при необходимости)

Добавляйте комментарии, ссылки на PR или соответствующие хэши коммитов в раздел "Примечания" для каждого пункта.

---

## 1. Настройка Проекта и Базовая Инфраструктура

- [x] **Создание Базовых Директорий**: `backend/services/`, `backend/utils/`, `backend/worker/` (с файлами `__init__.py`).
    - Примечания: Созданы начальные директории для сервисов, утилит и воркера.
- [x] **Конфигурация**:
    - [x] Обработка переменных окружения (`.env`, `pydantic-settings`) для секретов и базовых подключений.
      - Примечания: Реализовано через Pydantic Settings в `backend/config/settings.py`. **Критическое исправление v2025.05.10**: Обеспечена консистентность `.env` и `docker-compose.yml` для `DATABASE_URL`, `POSTGRES_USER/PASSWORD/DB`. Устранены жестко прописанные URL в `docker-compose.yml` для API-сервисов (теперь используют `env_file`), что решило проблему `password authentication failed`. Скорректирован `.env` для правильного использования внутренних и внешних портов и сборки URL из частей.
    - [x] Создание модели `ConfigurationSetting` в `backend/database/models.py`.
    - [x] Создание модели `ConfigurationSetting` в `backend/database/db.py` для настроек в БД.
    - [x] Создание утилиты `backend/utils/config_loader.py` для чтения настроек из БД.
    - [x] Создание скрипта `seed` для настроек по умолчанию.
      - Примечания: Добавлен скрипт `backend/scripts/seed_config.py` для заполнения конфигурации по умолчанию. **Дополнение v2025.05.10**: Рекомендовано создать миграцию Alembic для добавления `RATE_LIMIT_DEFAULT` в `configuration_settings` для обеспечения его наличия в БД.
    - Примечания: Модель перенесена из `models.py` в `db.py`, удалён дублирующий файл `models.py` для единства моделей.
- [x] **Основные Модели (`backend/database/db.py`)**:
    - [x] Создан файл `db.py` и определен `Base`.
    - [x] Добавлена модель `ConfigurationSetting`.
    - [x] Добавить остальные модели (`User`, `Order`, etc.).
    - Примечания: Начальная структура моделей. **Критическое исправление v2025.05.10**: Устранены конфликты `relationship` и `@hybrid_property` (удалены гибридные свойства `merchant` в `MerchantStore`, `BalanceStore`). **Исправление v2025.05.10**: Устранены `SAWarning` о конфликтующих `relationship` путем добавления `back_populates` в моделях `MerchantStore`, `FiatCurrency`, `CryptoCurrency`. Рекомендовано сгенерировать "проверочную" миграцию Alembic после этих изменений в `relationship`.
    - [x] Добавлена модель `TeamLead` и связь с `Trader`.
      Примечания: модель и связи реализованы v2025.05.11.
- [x] **Базовые Схемы (`sсhemas_enums/`)**: Схемы Pydantic для передачи данных API.
    - [x] Создан `sсhemas_enums/order.py` с базовыми схемами ордеров.
    - [x] Создан `sсhemas_enums/reference.py` с Pydantic схемами для справочных данных (BankDetails, PaymentMethodDetails, ExchangeRateDetails).
    - [x] Добавлены схемы для остальных ключевых сущностей:
        * `user.py` — базовые схемы пользователя.
        * `merchant.py` — Merchant, MerchantStore.
        * `trader.py` — Trader и TraderCommission.
        * `requisite.py` — ReqTrader и FullRequisiteSettings.
        * `balance.py` — BalanceStore/Trader и истории.
    - Примечания: закрыт пункт расширения Pydantic-схем, все основные модели покрыты, ORM-mode включён для чтения из SQLAlchemy.
- [x] **Скрипт заполнения данных (`scripts/seed_data.py`)**: Для начальных ролей, пользователя-админа, справочных данных.
    - Примечания: Добавлен скрипт `backend/scripts/seed_data.py` для создания ролей и администратора.
- [x] **Настройка Логирования (`logger.py`)**: Базовая конфигурация структурированного логирования.
    - Примечания:
- [x] **Движок БД и Сессия (`engine.py`)**: Настройка `SessionLocal`.
    - Примечания:
- [x] **Базовое Приложение FastAPI (`main.py`)**: Начальная настройка (FastAPI app, logging, Sentry init, health check, exception handlers).
    - Примечания:
- [x] **Управление Зависимостями (`requirements.txt`)**: Создан и заполнен начальными зависимостями.
    - Примечания:
- [x] **Утилиты Работы с S3 (`utils/s3_client.py`)**: Загрузка/управление файлами в S3.
    - Примечания: Реализован S3 клиент в `backend/utils/s3_client.py` с функцией `upload_fileobj`.

## 2. Аутентификация и Авторизация

- [x] **Реализация JWT/OAuth2 (`auth/`)**:
    - [x] Утилиты генерации/валидации токенов (`backend/security.py`).
    - [x] Хеширование паролей (`backend/config/crypto.py`).
    - [x] Зависимости FastAPI Security (`OAuth2PasswordBearer`, `get_current_user`).
    - Примечания: Настроены `create_access_token`, `get_current_user`, `get_current_active_user`.
- [x] **Эндпоинт Логина мерчанта** (`/merchant/auth/token`).
    - Примечания: Аутентификация через `User` и `merchant_profile`, используется `get_db_session`, возвращает JWT.
- [x] **Эндпоинт Логина трейдера** (`/trader/auth/token`).
    - Примечания: Аутентификация через `User` и `trader_profile`, используется `get_db_session`, возвращает JWT.
- [x] **Эндпоинт Логина саппорта** (`/support/auth/login`).
    - Примечания: Аутентификация через `User` и `support_profile`, убран импорт `SessionLocal`.
- [x] **Защита Эндпоинтов**: Применены зависимости `get_current_active_user` и `get_current_active_merchant`.
    - Примечания: Роутеры мерчанта и трейдера защищены JWT-зависимостью.

## 3. Основные Сервисы (`services/`)

- [x] **Утилиты работы с БД (`backend/database/utils.py`)**: Функции для безопасного доступа и транзакций с базой данных (CRUD, atomic_transaction, get_db_session).
    - Примечания: Реализованы get_db_session, atomic_transaction, create_object, get_object_or_none, update_object_db.
- [x] **Сервис Пользователей (`services/user_service.py`)**: Логика управления пользователями и ролями (CRUD, авторизация).
    - Примечания: Реализованы функции `get_user_by_email`, `create_user`, `authenticate_user`.
- [x] **Сервис Подбора Реквизитов (`services/requisite_selector.py`)**: Логика поиска и выбора подходящих реквизитов для incoming orders.
    - Примечания: Реализована функция `find_suitable_requisite` с поддержкой статических и динамических лимитов.
- [x] **Сервис Обработки Заявок (`services/order_processor.py`)**: Оркестрация обработки входящих заявок, подбор реквизитов, создание OrderHistory.
    - Примечания: Реализованы idempotency, fraud detection, requisite selection, commission calculation, создание OrderHistory и обновление статуса.
- [x] **Сервис Обновления Балансов (`services/balance_manager.py`)**: Надежное обновление балансов и запись истории.
    - Примечания: Реализованы `calculate_commissions` и `update_balances_for_completed_order`, включая блокировку балансов и запись истории.
- [x] **Сервис Справочных Данных (`services/reference_data.py`)**: Доступ к справочным данным с кэшированием (Redis).
    - Примечания: Реализована инициализация Redis, cache helpers, примеры get_bank_details, get_payment_method_details, get_exchange_rate.
- [x] **Менеджер Статусов Ордера (`services/order_status_manager.py`)**: Управление переходами статусов ордеров.
    - Примечания: Реализованы методы `confirm_payment_by_client`, `confirm_order_by_trader`, `cancel_order` с загрузкой чеков в S3, audit-логированием и обновлением балансов.
- [x] **Логгер Аудита (`services/audit_logger.py`)**: Сервис для записи событий аудита в AuditLog.
    - Примечания: Реализован метод `log_event` для записи аудита в таблицу `audit_logs`.
- [x] **Детектор Мошенничества (`services/fraud_detector.py`)**: Правила и проверки для обнаружения мошеннических операций.
    - Примечания: Реализована логика пороговой проверки из конфигурации (deny/manual review).
- [x] **Сервис Шлюза (`services/gateway_service.py`)**: Логика обработки запросов API шлюза.
    - Примечания: Реализован secure API-key lookup, создание IncomingOrder, получение статуса и подтверждение клиентом.
    - [/] **TODO**: Реализовать глубокую валидацию входящих запросов (проверка разрешённых валют, обязательных полей, лимитов магазина).
        - Добавить unit-тесты на валидацию.
- [x] **Сервис Коллбэков (`services/callback_service.py`)**: Отправка коллбэков мерчантам.
    - Примечания: Реализована генерация HMAC-SHA256 подписи, асинхронная отправка POST через httpx, обработка ошибок.
    - [/] **TODO**: Финализировать структуру payload для мерчанта, задокументировать в README_API, опционально логировать body ответа мерчанта.

## 4. Утилиты (`utils/`)

- [x] **Утилита Загрузки Конфигурации (`utils/config_loader.py`)**: Чтение настроек из БД.
    - Примечания:
- [x] **Утилиты Исключений (`utils/exceptions.py`)**: Определить иерархию кастомных исключений.
    - Примечания: Создан базовый класс JivaPayException и специфичные исключения.
- [x] **Утилиты Оповещений (`utils/notifications.py`)**: Настроить отправку оповещений о критических ошибках (Sentry).
    - Примечания: Реализована инициализация Sentry и функция report_critical_error.

## 5. API Роутеры (`api_routers/`)

- [x] **Роутер Аутентификации (`api_routers/auth_router.py`)**: Эндпоинт логина/токена.
    - Примечания:
- [x] **Роутеры Аутентификации (merchant/auth.py, trader/auth.py, support/auth.py)**: Эндпоинты логина и выдачи токенов.
    - Примечания: Реализованы `/api/merchant/auth/token`, `/api/trader/auth/token` и `/support/auth/login`.
- [x] **Роутер Мерчанта (`api_routers/merchant/router.py`)**: Эндпоинты для мерчантов.
    - Примечания: Реализованы POST `/orders`, GET `/orders`, POST `/orders/{order_id}/confirm_payment` и CRUD для `/stores`.
- [x] **Роутер Трейдера (`api_routers/trader/router.py`)**: Эндпоинты для трейдеров.
    - Примечания: Реализованы GET `/orders`, POST `/orders/{order_id}/confirm`, POST `/orders/{order_id}/cancel` с вызовом order_status_manager.
- [x] **Роутер Саппорта (`api_routers/support/auth.py`)**: Эндпоинт логина саппорта и доступ к ограниченному набору операций.
    - Примечания: Реализован `POST /support/auth/login`; support видит только часть админского функционала (например, просмотр, поиск).  
- [x] **Роутер Администратора (`api_routers/admin/*`)**: Полный набор эндпоинтов, включает функционал саппорта и расширенные возможности.
    - Примечания: Реализованы `POST /admin/auth/token`, `GET /admin/users`, `POST /admin/register/merchant`, `POST /admin/register/support`, `POST /admin/debug/celery/ping`.
- [x] **Публичный Роутер/Роутер Справочников (`api_routers/public_router.py`)**: Эндпоинты для справочных данных (валюты, методы оплаты).
    - Примечания: Реализованы GET `/reference/banks/{bank_id}`, `/reference/payment-methods/{method_id}`, `/reference/exchange-rates/{crypto_id}/{fiat_id}`.
- [x] **Роутер Шлюза (`api_routers/gateway/router.py`)**: Эндпоинты для PayIn/PayOut шлюза.
    - Примечания: Реализованы `POST /payin/init`, `GET /payin/status/{id}`, `POST /payin/confirm/{id}`, `POST /payout/init`, `GET /payout/status/{id}` с вызовом gateway_service.
- [x] **Роутер Тимлида (`api_routers/teamlead/*`)**: login + управление трейдерами.  
  Примечания: реализация готова (`auth.py`, `router.py`); планируется покрыть тестами и при необходимости добавить SSE.

## 6. Фоновый Воркер (`worker/`)

- [x] **Настройка Celery/RQ (`worker/app.py`, `worker/tasks.py`)**: 
    - [x] Настроено приложение Celery в `worker/app.py` (broker, backend, queues, config).
    - [x] Определена задача `process_order_task` в `worker/tasks.py`.
    - Примечания: Используется Celery с Redis. Реализована ручная логика retry в задаче.
- [x] **Задача Обработчика Ордеров (`worker/tasks.py:process_order_task`)**: Задача для обработки `IncomingOrder`.
    - [ ] Проверка идемпотентности.
    - [ ] Вызов подбора реквизита.
    - [ ] Создание `MatchedOrder`.
    - [ ] Надежные обновления статуса (`retrying`/`failed`) при ошибках (отдельная транзакция).
    - Примечания:
- [x] **Задача Обновления Баланса (Опционально - `worker/tasks.py:update_balance_task`)**: Если используются асинхронные обновления через очередь задач/транзакционный outbox.
    - Примечания:
- [ ] **Настройка Очереди Недоставленных Сообщений (DLQ)**: Настроить DLQ для неудавшихся задач.
- [x] **Задача Планировщика (`worker/tasks.py:poll_new_orders_task`)**: Задача для поиска и постановки ордеров в очередь.
    - Примечания: TODO - реализовать логику запроса и отправки в `process_order_task`.
    - [/] **TODO**: Разкомментировать и довести до production-уровня `poll_new_orders_task`; настроить Celery Beat (или внешнее расписание) для её выполнения.

## 7. Middleware (`middleware/`)

- [x] **Middleware Логирования Запросов**: Логировать входящие запросы.
    - Примечания:
- [x] **Middleware Обработки Ошибок**: Централизованная обработка в `main.py` (JivaPayException, ValidationError, Generic Exception).
    - Примечания:
- [x] **Ограничение Частоты Запросов (`slowapi` + Redis)**: 
    - [x] Настроено в `middleware/rate_limiting.py` (Limiter, RedisStorage, Handler).
    - [x] Интегрировано в `main.py` (Middleware, Exception Handler).
    - [x] TODO закрыт: Чтение лимитов из БД реализовано в `get_default_rate_limit()` с использованием контекстного менеджера `get_db_session_cm()`; комментарии в коде актуализированы.
- [x] Применить лимиты к роутерам/эндпоинтам.
    - Примечания: Глобальные лимиты применены через SlowAPIMiddleware в каждом server.py

## 8. Тестирование

- [ ] **Юнит-тесты (`tests/unit/`)**: Для сервисов, утилит, сложной логики.
    - Примечания:
- [ ] **Интеграционные тесты (`tests/integration/`)**: Тестирование взаимодействий между сервисами, API эндпоинтами, БД.
    - Примечания:
- [ ] **Профилирование Индексов БД**: Анализ производительности запросов под нагрузкой.
    - Примечания:

## 9. Развертывание и Эксплуатация

- [x] **Dockerfile**: Контейнеризация приложения.
    - Примечания: Полностью настроен multi-stage Dockerfile для backend и worker, запуск через Uvicorn.
- [x] **Docker-Compose**: Конфигурация локальной разработки и тестирования.
    - Примечания: Включены сервисы: Postgres, Redis, Backend (Uvicorn+reload), Celery Worker; настроены переменные окружения и тома.
- [x] **Настройка CI/CD Пайплайна**: Автоматические тесты, линтинг, сборка, развертывание.
    - Примечания: Настроена GitHub Actions CI (линтинг, pytest с coverage, загрузка отчета в Codecov)
- [ ] **Настройка Инфраструктуры Мониторинга/Логирования**: Интеграция Prometheus/Grafana, ELK/Loki stack.
    - Примечания:
- [ ] **Стратегия Развертывания Без Простоя**: Определить подход (например, blue-green, canary).
    - Примечания:
- [ ] **Конфигурация Redis (на хосте сервера)**:
    - Статус: [ ]
    - Примечания: **Рекомендация v2025.05.10**: Обнаружено предупреждение Redis `Memory overcommit must be enabled!`. Рекомендовано исправить на хост-машине сервера (`vm.overcommit_memory = 1`) для стабильности в production.

## 10. (раздел снят)

*Миграции временно не ведутся, так как БД пересоздаётся с нуля при разработке.*

## 11. Серверы (`backend/servers/`)

- [x] Добавить `teamlead/server.py` и сервис `teamlead_api` в docker-compose.  
  Примечания: `server.py` создан ранее, сервис `teamlead_api` добавлен в docker-compose v2025.05.11.