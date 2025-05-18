# Основная Документация по Бэкенду JivaPay

## 1. Введение

Этот документ представляет собой консолидированное описание бэкенд-системы JivaPay. Он объединяет информацию из планов реализации, описаний компонентов, утилит и дополнительных функций, предоставляя полное представление об архитектуре, ключевых модулях и их взаимодействии.

**Цель:** Служить центральным справочником по бэкенду для разработчиков, обеспечивая понимание его структуры, логики работы и принципов проектирования.

**Основные принципы:**
*   **Модульность:** Компоненты бэкенда разделены на логические модули (сервисы, утилиты, API-роутеры) для улучшения сопровождаемости и масштабируемости.
*   **Сервис-ориентированный подход:** Бизнес-логика инкапсулирована в сервисах, каждый из которых отвечает за свою область (например, управление пользователями, обработка ордеров, подбор реквизитов).
*   **Надежность и отказоустойчивость:** Особое внимание уделяется атомарности операций с базой данных, обработке ошибок, логированию и механизмам фоновой обработки задач.
*   **Безопасность:** Взаимодействие с API осуществляется по HTTPS, используются JWT для аутентификации, предусмотрены механизмы авторизации и защиты от распространенных атак (например, rate limiting).
*   **Централизованное управление конфигурацией:** Настройки приложения хранятся как в переменных окружения (для секретов и базовых подключений), так и в базе данных (для параметров, изменяемых "на лету").
*   **Гранулярное управление правами:** Для ролей Администратора, Саппорта и Тимлида реализована система гранулярных прав доступа, хранящихся в JSON-полях профилей пользователей.

---

## 2. Архитектура и Структура Проекта

Бэкенд JivaPay построен на Python с использованием фреймворка FastAPI. Ключевые директории и их назначение:

*   `backend/`
    *   `api_routers/`: Содержит API-роутеры, разделенные по ролям и функциональным областям. Обрабатывают HTTP-запросы, валидируют данные и вызывают сервисы.
        *   `common/`: Общие модули CRUD-операций и логики для разных ролей.
        *   `role-based routers`: (в `backend/servers/*/server.py`) Динамически подключают модули из `common/` и защищаются правами.
    *   `config/`: Конфигурационные файлы, включая настройку логгера (`logger.py`), криптографию (`crypto.py`) и загрузку настроек приложения (`settings.py`).
    *   `database/`: Модули для работы с базой данных.
        *   `db.py`: Определения SQLAlchemy моделей.
        *   `engine.py`: Инициализация SQLAlchemy engine и сессии.
        *   `utils.py`: Утилиты для работы с сессиями, транзакциями и CRUD-операции.
        *   `migrations/`: Скрипты Alembic для миграций схемы БД.
    *   `middleware/`: Middleware для FastAPI (например, `rate_limiting.py`).
    *   `schemas_enums/`: Pydantic-схемы для валидации данных API и Python Enums.
    *   `scripts/`: Вспомогательные скрипты (например, `manage_db.py` для инициализации и сидирования БД).
    *   `security.py`: Функции и зависимости для аутентификации (JWT) и авторизации.
    *   `servers/`: Точки входа FastAPI-приложений для каждой роли (`admin/`, `merchant/`, `support/`, `teamlead/`, `trader/`, `gateway/`).
    *   `services/`: Инкапсуляция основной бизнес-логики.
    *   `utils/`: Вспомогательные утилиты общего назначения (кастомные исключения, уведомления, работа с S3, декораторы, утилиты для запросов).
    *   `worker/`: Реализация фонового обработчика задач (Celery).
        *   `app.py`: Настройка Celery.
        *   `tasks.py`: Определение задач.
        *   `scheduler.py`: (Опционально) Логика планирования задач.

---

## 3. Конфигурация и Запуск

### 3.1. Переменные Окружения и Настройки в БД

*   **Переменные Окружения (`.env`):** Используются для хранения секретов и базовых параметров подключения (к БД, Redis, Sentry, S3), JWT-ключей.
*   **Настройки в Базе Данных (таблица `configuration_settings`):** Параметры, которые могут потребовать изменения без перезапуска приложения (лимиты API, настройки анти-фрода, таймауты ордеров, множители для retry). Читаются через `backend.utils.config_loader.get_typed_config_value`.

### 3.2. Управление Секретами

Для **production** окружения рекомендуется использовать специализированные системы управления секретами (HashiCorp Vault, облачные аналоги, K8s Secrets).

---

## 4. Ключевые Компоненты и Сервисы Бэкенда

### 4.1. Аутентификация и Авторизация

*   **Механизм:** JWT (JSON Web Tokens) / OAuth2.
*   **Утилиты:**
    *   `backend.security`: Генерация/валидация токенов (`create_access_token`, `verify_access_token`), получение текущего пользователя (`get_current_user`, `get_current_active_user`).
    *   `backend.config.crypto`: Хеширование паролей (`hash_password`, `verify_password`) с использованием bcrypt.
*   **Эндпоинты логина:** Реализованы для каждой роли (мерчант, трейдер, администратор, саппорт, тимлид) через соответствующие `auth.py` роутеры. Аутентификация происходит через таблицу `User` и связанные профили.
*   **Защита эндпоинтов:** Используются зависимости FastAPI Security (`Depends(get_current_active_user)` или специфичные для роли).
*   **Гранулярные права:** Для ролей Admin, Support, TeamLead права доступа определяются JSON-полем `granted_permissions` в их профилях и проверяются через `services.permission_service`.

### 4.2. База Данных (`backend/database/`)

*   **Модели (`db.py`):** Определены все основные сущности системы (см. `docs/README_DATABASE.md`).
    *   **Ключевые обновления:** В `Trader` добавлено поле `is_traffic_enabled_by_teamlead`. В профилях `Admin`, `Support`, `TeamLead` добавлены поля `granted_permissions`. В `Support` добавлено `role_description`. Из `FullRequisitesSettings` удалено `active_hours`.
*   **Утилиты (`utils.py`):**
    *   `get_db_session()`: Зависимость FastAPI для предоставления сессии БД.
    *   `get_db_session_cm()`: Контекстный менеджер для сессий в сервисах/воркерах.
    *   `atomic_transaction()`: Декоратор/контекстный менеджер для атомарных транзакций с автоматическим COMMIT/ROLLBACK и логированием.
    *   CRUD-функции (`create_object`, `get_object_or_none`, `update_object_db`) с обработкой исключений SQLAlchemy и логированием.

### 4.3. Обработка Ошибок и Логирование

*   **Кастомные Исключения (`utils.exceptions.py`):** Иерархия исключений, наследуемых от `JivaPayException`.
*   **Декоратор `@handle_service_exceptions` (`utils.decorators.py`):**
    *   Применяется к функциям/методам сервисов.
    *   Перехватывает `JivaPayException` (логирует как ERROR) и другие `Exception` (логирует как CRITICAL).
    *   Логирует успешное выполнение и результат.
    *   Использует логгер из `backend.config.logger.get_logger()`.
*   **Глобальные Обработчики Исключений (`utils.exception_handlers.py`):** Зарегистрированы в FastAPI-приложениях для `JivaPayException` и стандартных ошибок FastAPI. Формируют стандартизированный JSON-ответ.
*   **Логгер (`config/logger.py`):**
    *   Функция `get_logger(__name__)` для получения экземпляра логгера.
    *   Настроен на структурированный JSON-вывод.
*   **Уведомления (`utils.notifications.py`):**
    *   Функция `report_critical_error(exception, context_message)` для отправки критических ошибок в Sentry (или аналогичную систему).

### 4.4. Middleware

*   **Ограничение Частоты Запросов (`middleware/rate_limiting.py`):**
    *   Использует `slowapi` и Redis.
    *   Лимиты могут читаться из БД (`RATE_LIMIT_DEFAULT`) или быть заданы для конкретных эндпоинтов.
    *   Применяется глобально через `SlowAPIMiddleware` и обработчик `RateLimitExceeded`.
*   **Другие Middleware:** Логирование запросов, CORS (если необходимо).

### 4.5. Сервисы Бизнес-Логики (`backend/services/`)

Все сервисы, где это применимо, используют декоратор `@handle_service_exceptions` для унифицированного логирования и обработки ошибок.

#### 4.5.1. `user_service.py` (Сервис Пользователей)

*   **Назначение:** Управление пользователями, ролями, профилями.
*   **Функционал:**
    *   CRUD операции для пользователей и их профилей (`Admin`, `Support`, `TeamLead`).
    *   Аутентификация пользователей (`authenticate_user`).
    *   Получение статистики по ролям (`get_administrators_statistics`, `get_teamleads_statistics`, `get_supports_statistics`). Эти функции рефакторены с использованием `utils.query_utils.py` для пагинации, сортировки и фильтрации.
    *   Получение детальной информации о профилях, включая `granted_permissions`.
    *   Обновление профилей и статуса пользователя (`_update_user_and_profile_generic`) с проверкой прав через `permission_service` и аудитом.
    *   Блокировка/разблокировка пользователей.

#### 4.5.2. `permission_service.py` (Сервис Управления Правами)

*   **Назначение:** Централизованное управление и проверка гранулярных прав доступа.
*   **Функционал:**
    *   `get_user_permissions()`: Получает список строковых прав для пользователя из JSON-поля `granted_permissions`.
    *   `update_user_permissions()`: Обновляет права пользователя, требует прав у текущего администратора, выполняет аудит.
    *   `check_permission()`: Проверяет наличие права у пользователя, используя `_match_permission`.
    *   `_match_permission()`: Сопоставляет право с учетом wildcards (`*`) и плейсхолдера `{id}` (например, `users:edit:trader:{id}`).
    *   `check_specific_or_any_permission()`: Проверяет наличие одного из нескольких прав или специфического права.

#### 4.5.3. `requisite_selector.py` (Подбор Реквизитов)

*   **Назначение:** Инкапсуляция логики поиска и выбора подходящего реквизита трейдера для входящей заявки. **Критически важный** компонент.
*   **Функционал (`find_suitable_requisite`):**
    *   Работает внутри транзакции, управляемой извне (из `order_processor`).
    *   **Условия доступности трейдера/реквизита:**
        *   `User.is_active == True`
        *   `Trader.in_work == True`
        *   `Trader.is_traffic_enabled_by_teamlead == True`
        *   `ReqTrader.status == 'approve'`
        *   `FullRequisitesSettings.pay_in == True` (для PayIn) или `FullRequisitesSettings.pay_out == True` (для PayOut).
    *   Использует `backend.utils.query_filters.get_active_trader_filters()` и `get_active_requisite_filters()`.
    *   Выполняет оптимизированный SQL-запрос с `with_for_update(skip_locked=True)`.
    *   **Round-robin:** Сортировка по `Trader.trafic_priority` (ASC), затем `ReqTrader.last_used_at` (ASC, NULLS FIRST).
    *   Обновляет `ReqTrader.last_used_at` после назначения.
    *   Проверяет динамические лимиты реквизита.
    *   Возвращает `(requisite_id, trader_id)` или `None`.
*   *Примечание: Стандартный декоратор `@handle_service_exceptions` к этому сервису пока не применялся из-за специфики его использования.*

#### 4.5.4. `order_processor.py` (Обработка Входящих Заявок)

*   **Назначение:** Оркестрация обработки одной входящей заявки (`IncomingOrder`).
*   **Функционал (`process_incoming_order`):**
    1.  **Проверка идемпотентности.**
    2.  Начало основной атомарной транзакции.
    3.  Загрузка `IncomingOrder` с блокировкой (`with_for_update`).
    4.  Вызов `fraud_detector.check_incoming_order()`.
    5.  Вызов `requisite_selector.find_suitable_requisite()`.
    6.  **Результат `find_suitable_requisite`:**
        *   **Успех:**
            *   Расчет комиссий (`balance_manager.calculate_commissions`).
            *   Создание `OrderHistory` (копирование полей из `IncomingOrder`, включая `amount_fiat`, `amount_crypto`, `client_id`, `customer_id`, `customer_ip`, `payment_details_submitted`; `OrderHistory.total_fiat` использует значение из `IncomingOrder`, фиксация курса).
            *   Обновление `IncomingOrder` (статус `assigned`, `assigned_order_id`).
            *   COMMIT основной транзакции.
        *   **Неудача (реквизит не найден, лимит, фрод) или Исключение:**
            *   ROLLBACK основной транзакции.
            *   **Надежное обновление статуса `IncomingOrder` в отдельной транзакции** (увеличение `retry_count`, `last_attempt_at`, `failure_reason`, статус `retrying` или `failed`).
            *   Логирование, отправка уведомления при критической ошибке.
*   *Примечание: Имеет комплексную внутреннюю логику обработки исключений, `@handle_service_exceptions` не применялся.*

#### 4.5.5. `balance_manager.py` (Управление Балансами)

*   **Назначение:** Надежное обновление балансов и запись истории. Выполняется после успешного подтверждения ордера.
*   **Функционал:**
    *   `calculate_commissions()`: Расчет комиссий магазина и трейдера на основе `StoreCommission`, `TraderCommission`.
    *   `update_balances_for_completed_order()`:
        *   Работает в атомарной транзакции.
        *   Загружает `OrderHistory`, `MerchantStore`, `Trader`.
        *   Блокирует строки балансов (`BalanceStore`, `BalanceTrader`, `BalancePlatform`) для обновления.
        *   Обновляет балансы.
        *   Создает записи в `BalanceStoreHistory`, `BalanceTraderFiatHistory`, `BalanceTraderCryptoHistory`, `BalancePlatformHistory` (фиксируя `platform_profit`).

#### 4.5.6. `order_status_manager.py` (Управление Статусами Ордера)

*   **Назначение:** Логика перехода `OrderHistory` между статусами.
*   **Функционал:**
    *   `confirm_payment_by_client()`: Для PayIn, клиент подтверждает оплату (загрузка чека через S3). Статус -> `pending_trader_confirmation`.
    *   `confirm_order_by_trader()`: Трейдер подтверждает ордер (загрузка чека для PayOut). Статус -> `completed`. **Инициирует** `balance_manager.update_balances_for_completed_order()` (возможно, асинхронно).
    *   `cancel_order()`, `dispute_order()`, `resolve_dispute()`, `fail_order()`: Обработка отмены, споров, неудачи.
    *   Все операции в атомарных транзакциях. Использует `audit_logger.log_event`.

#### 4.5.7. `order_service.py` (Сервис Ордеров)

*   **Назначение:** Расширенные возможности для работы с историей ордеров.
*   **Функционал:**
    *   `get_orders_history()`: Выборка ордеров с комплексной фильтрацией (сумма, диапазон дат, статус, ID, email, поиск по полям), сортировкой, пагинацией. Использует `utils.query_utils.py` и `permission_service` для проверки прав.
    *   `get_orders_count()`: Подсчет количества ордеров с фильтрами и учетом прав.

#### 4.5.8. `requisite_service.py` (Сервис Реквизитов)

*   **Назначение:** Управление и предоставление статистики по реквизитам.
*   **Функционал:**
    *   `get_online_requisites_stats()`: Статистика активных реквизитов с фильтрацией, сортировкой. Использует `utils.query_utils.py`, `utils.query_filters.py` и `permission_service`. Логика "онлайн" соответствует `requisite_selector`.
    *   `get_requisite_details_for_moderation()`: Детали реквизита для админов.
    *   `set_requisite_status()`: Установка статуса реквизита админом с аудитом.

#### 4.5.9. `platform_service.py` (Сервис Платформы)

*   **Назначение:** Информация о состоянии платформы.
*   **Функционал:**
    *   `get_platform_balances()`: Агрегированные балансы платформы из `BalancePlatform`.

#### 4.5.10. `trader_service.py` (Сервис Трейдеров)

*   **Назначение:** Статистика и детальная информация по трейдерам.
*   **Функционал:**
    *   `get_traders_statistics()`: Статистика с фильтрацией (статус, онлайн, период оборота, валюта, платежный метод, поиск), сортировкой. Использует `utils.query_utils.py` и `permission_service`.
    *   `get_trader_full_details()`: Полная информация о трейдере для админов.

#### 4.5.11. `merchant_service.py` (Сервис Мерчантов)

*   **Назначение:** Аналогично `trader_service`, но для мерчантов.
*   **Функционал:**
    *   `get_merchants_statistics()`: Статистика с фильтрацией, сортировкой. Использует `utils.query_utils.py` и `permission_service`.
    *   `get_merchant_full_details()`: Полная информация о мерчанте.

#### 4.5.12. `teamlead_service.py` (Сервис Тимлидов)

*   **Назначение:** Функционал для роли Тимлида.
*   **Функционал:**
    *   `get_managed_traders()`: Список трейдеров команды.
    *   `set_trader_traffic_status_by_teamlead()`: Установка флага `Trader.is_traffic_enabled_by_teamlead` с аудитом.
    *   `get_team_statistics()`: Агрегированная статистика по команде.
    *   `get_teamlead_full_details()`: Полная информация о тимлиде (для админов).
    *   Логика расчета активных реквизитов использует `utils.query_filters.py`.

#### 4.5.13. `reference_data.py` (Сервис Справочных Данных)

*   **Назначение:** Доступ к справочным данным (курсы валют, банки, методы оплаты) с кэшированием (Redis).
*   **Функционал:**
    *   `get_exchange_rate()`, `get_bank_details()`, `get_payment_method_details()`.
    *   Курсы валют могут обновляться фоновой задачей.

#### 4.5.14. `audit_logger.py` (Сервис Аудита) / `audit_service.py`

*   **Назначение:** Запись и извлечение событий аудита.
*   **Функционал:**
    *   `log_event()`: Запись действия пользователя/системы в `AuditLog`. Интегрирована во многие сервисы.
    *   `get_critical_system_errors()`: (Потенциально в `audit_service`) Извлечение логов критических системных ошибок.

#### 4.5.15. `fraud_detector.py` (Детектор Мошенничества)

*   **Назначение:** Обнаружение мошеннических операций.
*   **Функционал (`check_incoming_order`):**
    *   Вызывается из `order_processor`.
    *   Проверяет по velocity-лимитам, черным/белым спискам (хранятся в конфиге/БД/Redis).
    *   Возвращает `ALLOW`, `DENY` (статус ордера -> `failed`, или выбрасывает `FraudDetectedError`), `REQUIRE_MANUAL_REVIEW` (статус ордера -> `manual_review`).
    *   Результаты логируются в `AuditLog`.

#### 4.5.16. `gateway_service.py` (Сервис Платежного Шлюза)

*   **Назначение:** Логика обработки запросов публичного API шлюза (PayIn/PayOut).
*   **Функционал:**
    *   `_get_merchant_store_by_api_key()`: Безопасный поиск магазина по API-ключу.
    *   `handle_init_request()`: Создание `IncomingOrder` для запросов `/payin/init`, `/payout/init`.
    *   `get_order_status()`: Получение статуса для `/payin/status/{id}`, `/payout/status/{id}`.
    *   `handle_client_confirmation()`: Обработка подтверждения оплаты клиентом для `/payin/confirm/{id}` (вызов `order_status_manager.confirm_payment_by_client`).

#### 4.5.17. `callback_service.py` (Сервис Коллбэков)

*   **Назначение:** Асинхронная отправка коллбэков мерчантам об изменении статуса ордера.
*   **Функционал (`send_merchant_callback`):**
    *   Генерация HMAC-SHA256 подписи для payload.
    *   Асинхронная отправка POST-запроса через `httpx`.
    *   Обработка ошибок сети, таймаутов, HTTP-статусов ответа мерчанта.
    *   Механизм retry для отправки коллбэков (может быть интегрирован с Celery).

### 4.6. Утилиты (`backend/utils/`)

*   **`config_loader.py`:** Чтение и типизация настроек из БД.
*   **`s3_client.py`:** Загрузка файлов в S3-совместимое хранилище (например, чеков). Функция `upload_fileobj`.
*   **`query_utils.py`:**
    *   **Назначение:** Вспомогательные функции для построения SQLAlchemy запросов (пагинация, сортировка, общие фильтры).
    *   **Функции:** `apply_pagination`, `apply_sorting`, `apply_user_status_filter`, `apply_date_range_filter`, `get_paginated_results_and_count`.
    *   Используется многими сервисами для стандартизации обработки списков.
*   **`query_filters.py`:**
    *   **Назначение:** Централизованное определение специфичных наборов SQLAlchemy фильтров.
    *   **Функции:** `get_active_trader_filters()`, `get_active_requisite_filters()`.
    *   Используется в `requisite_selector`, `teamlead_service`, `requisite_service` и др.

### 4.7. Фоновый Обработчик (`backend/worker/`)

*   **Технология:** Celery с Redis в качестве брокера и бэкенда результатов.
*   **Настройка (`app.py`):** Конфигурация Celery (брокер, бэкенд, очереди, автообнаружение задач).
*   **Задачи (`tasks.py`):**
    *   `process_order_task(incoming_order_id)`: Основная задача, вызывает `services.order_processor.process_incoming_order`. Настроена с `autoretry_for` (для `DatabaseError`, `CacheError`), `retry_backoff` (читается из БД), `max_retries` (читается из БД).
    *   `update_balances_task(order_id)`: (Опционально, если обновление балансов асинхронное) Вызывает `services.balance_manager.update_balances_for_completed_order`.
    *   `poll_new_orders_task`: (Потенциальная задача) Периодический опрос `IncomingOrder` для выборки новых/повторных заявок и их отправки в `process_order_task`. Требует настройки Celery Beat или внешнего планировщика.
*   **Очередь Недоставленных Сообщений (DLQ):** Рекомендуется настроить для неудавшихся задач.
*   **Мониторинг:** Flower для Celery или метрики Prometheus.

---

## 5. API Роутеры (`backend/api_routers/`)

API-роутеры организованы по ролям и далее по функциональным модулям. Они используют Pydantic-схемы из `schemas_enums/` для валидации и сериализации данных.

### 5.1. Общие Принципы

*   **Аутентификация:** Большинство эндпоинтов защищены JWT-аутентификацией (`Depends(get_current_active_user)` или специфичные для роли).
*   **Авторизация:** Гранулярные права проверяются через `services.permission_service` внутри сервисов или с помощью декораторов на уровне роутеров (если применимо).
*   **Внедрение зависимостей:** `Depends(get_db_session)` для получения сессии БД.
*   **Ответы:** Стандартизированные JSON-ответы, формируемые FastAPI и глобальными обработчиками исключений.

### 5.2. Ключевые Роутеры

*   **`auth_router.py` (и аналогичные для ролей):** Эндпоинты логина (`/token`, `/login`).
*   **`merchant/router.py`:** CRUD для магазинов (`/stores`), операции с ордерами (`/orders`, `/orders/{order_id}/confirm_payment`).
*   **`trader/router.py`:** Операции с ордерами (`/orders`, `/orders/{order_id}/confirm`, `/orders/{order_id}/cancel`).
*   **`admin/*`:** Широкий набор эндпоинтов для управления пользователями, просмотра статистики, модерации, управления настройками.
    *   `platform_stats_router.py`: `GET /platform/balance`.
    *   `order_management_router.py`: `GET /orders/history`, `GET /orders/count`.
    *   `requisite_management_router.py`: `GET /requisites/online-stats`, модерация реквизитов.
    *   `user_management_router.py`: Статистика и управление администраторами, тимлидами, саппортами.
    *   `permission_management_router.py`: `PUT /users/{user_id}/permissions`.
*   **`support/router.py`:** Ограниченный набор эндпоинтов на основе прав саппорта (просмотр статистики, деталей сущностей, действия над ордерами).
*   **`teamlead/router.py`:** Управление командой трейдеров (`/managed-traders`, `/managed-traders/{trader_id}/traffic`), статистика по команде (`/team/statistics`), статистика по онлайн-реквизитам команды.
*   **`public_router.py` / `reference_router.py`:** Эндпоинты для справочных данных (банки, методы оплаты, курсы валют), доступные без строгой аутентификации.
*   **`gateway/router.py`:** Публичные эндпоинты для PayIn/PayOut шлюза (`/payin/init`, `/payin/status/{id}`, `/payin/confirm/{id}`, `/payout/init`, `/payout/status/{id}`).

---

## 6. План Тестирования и Развертывания

### 6.1. Тестирование

*   **Юнит-тесты (`tests/unit/`):** Для сервисов, утилит, сложной логики (с mock-объектами).
*   **Интеграционные тесты (`tests/integration/`):** Взаимодействие между сервисами, API-эндпоинтами, БД.
*   **Особое внимание:** Логика подбора реквизитов, обработка ордеров, транзакционность, работа Worker'а, обновление балансов, изменение статусов ордера.
*   **Профилирование БД:** Анализ производительности запросов под нагрузкой (`EXPLAIN ANALYZE`).
*   Подробный тест-план: `docs/TEST_PLAN.md`.

### 6.2. Развертывание и Эксплуатация

*   **Dockerfile:** Multi-stage Dockerfile для backend и worker.
*   **Docker-Compose:** Конфигурация для локальной разработки (Postgres, Redis, Backend, Worker).
*   **CI/CD (GitHub Actions):** Линтинг, pytest с coverage (Codecov), сборка Docker-образов.
*   **Мониторинг/Логирование:** Sentry, Prometheus/Grafana, ELK/Loki (рекомендовано).
*   **Стратегия развертывания без простоя:** Blue-green, canary (рекомендовано для production).

---

## 7. Реализация Дополнительных Функций (Резюме из `ADDITIONAL_FEATURES_AND_COMPONENTS.md`)

Этот раздел кратко суммирует ключевые новые API эндпоинты и сервисные функции, реализованные для расширения функционала Администраторов, Саппортов и Тимлидов. Подробное описание каждого компонента и его UI/UX аспектов находится в `docs/ADDITIONAL_FEATURES_AND_COMPONENTS.md` (этот файл будет удален после мержа, его содержимое интегрировано выше).

### Общие компоненты (доступ с учетом прав):

*   **Баланс площадки:** `GET /api/admin/platform/balance` (Сервис: `platform_service.get_platform_balances`).
*   **История ордеров:** `GET /api/admin/orders/history`, `GET /api/support/orders/history` (Сервис: `order_service.get_orders_history`).
*   **Количество реквизитов онлайн:** `GET /api/<role>/requisites/online-stats` (также SSE эндпоинт) (Сервис: `requisite_service.get_online_requisites_stats`).
*   **Количество трейдеров:** `GET /api/admin/traders/stats`, `GET /api/support/traders/stats` (Сервис: `trader_service.get_traders_statistics`).
*   **Количество мерчантов:** `GET /api/admin/merchants/stats` (Сервис: `merchant_service.get_merchants_statistics`).
*   **Общее количество ордеров:** `GET /api/admin/orders/count` (Сервис: `order_service.get_orders_count`).
*   **Логи критических ошибок:** `GET /api/admin/logs/critical-errors` (Сервис: `audit_service.get_critical_system_errors`).
*   **Статистика по пользователям (Администраторы, Тимлиды, Саппорты):** `GET /api/admin/<role>/stats` (Сервис: `user_service.get_<role>_statistics`).

### Функционал Администраторов:

*   Управление другими администраторами, саппортами, тимлидами (профили, права `granted_permissions`, блокировка/разблокировка).
    *   Эндпоинты: `GET /api/admin/<role>/{user_id}`, `PUT /api/admin/<role>/{user_id}`, `PUT /api/admin/users/{user_id}/permissions`, `POST /api/admin/users/{user_id}/block|unblock`.
    *   Сервисы: `user_service`, `permission_service`.
*   Просмотр полной информации о трейдерах и мерчантах.
    *   Эндпоинты: `GET /api/admin/traders/{trader_id}/full-details`, `GET /api/admin/merchants/{merchant_id}/full-details`.
    *   Сервисы: `trader_service.get_trader_full_details`, `merchant_service.get_merchant_full_details`.

### Функционал Саппортов:

*   Доступ к компонентам определяется их `granted_permissions`.
*   Просмотр деталей трейдеров, мерчантов/магазинов (если разрешено).
*   Действия над ордерами (если разрешено).

### Функционал Тимлидов:

*   Управление своей командой трейдеров:
    *   `GET /api/teamlead/managed-traders`
    *   `POST /api/teamlead/managed-traders/{trader_id}/traffic` (включение/выключение трафика трейдеру)
    *   `GET /api/teamlead/team/statistics`
*   Сервисы: `teamlead_service`.

---

Этот документ будет обновляться по мере развития бэкенд-системы JivaPay. 