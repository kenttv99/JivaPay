# План Реализации Утилит Backend

---

## 1. Введение

Этот документ описывает пошаговый план реализации бэкенд-утилит для платежной системы JivaPay, как детализировано в `README_UTILITIES.md`. План основан на текущей архитектуре проекта и существующих документах.

**Цель:** Систематическая разработка необходимых модулей и функций для обеспечения надежной, отказоустойчивой и эффективной работы основной логики системы.

---

## 2. Предварительные шаги

1.  **Создание директорий:** Создать новые директории в `backend/`: `services/`, `utils/`, `worker/` (если еще не существуют). Убедиться, что в каждой новой директории есть файл `__init__.py`.
2.  **Конфигурация:** 
    *   **Переменные Окружения (`.env` или системные):** Основные параметры подключения и секреты остаются в переменных окружения. К ним относятся:
        *   `DATABASE_URL`: Строка подключения к PostgreSQL.
        *   `REDIS_URL`: Строка подключения к Redis (для кэша, rate limiting, Celery/Dramatiq).
        *   `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`: (Если отличаются от `REDIS_URL`).
        *   `SENTRY_DSN`: DSN для Sentry.
        *   `SECRET_KEY`: Секретный ключ JWT.
        *   `ALGORITHM`: Алгоритм JWT.
        *   `ACCESS_TOKEN_EXPIRE_MINUTES`: Время жизни токена доступа.
        *   `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET_NAME`, `S3_ENDPOINT_URL`: Доступы к S3.
        *   Другие секреты или параметры, необходимые на самом раннем этапе запуска.
    *   **Настройки в Базе Данных (`configuration_settings` таблица):** Параметры, которые могут потребовать изменения без перезапуска приложения, будут храниться в БД и управляться через админ-интерфейс. К ним относятся:
        *   `MAX_ORDER_RETRIES`: Макс. кол-во попыток обработки заказа.
        *   `RETRY_BACKOFF_FACTOR`: Множитель задержки между попытками.
        *   `RATE_LIMIT_DEFAULT`: Стандартные лимиты API (например, "100/minute"). Можно добавить ключи для специфичных лимитов.
        *   Настройки анти-фрода (пороги, флаги правил).
        *   Настройки таймаутов ордеров.
        *   Другие параметры бизнес-логики.
    *   **Реализация:**
        *   Создана модель `ConfigurationSetting` в `backend/database/models.py`.
        *   Создана утилита `get_typed_config_value` в `backend/utils/config_loader.py` для чтения и типизации настроек из БД.
        *   Создан скрипт начального заполнения (seed) для значений по умолчанию.
    *   **Управление Секретами:** Для **production** окружения настоятельно рекомендуется использовать специализированные системы управления секретами (например, HashiCorp Vault, AWS/GCP/Azure Secrets Manager, K8s Secrets) вместо `.env` файлов для хранения чувствительных данных (пароли БД, JWT Secret, ключи API и т.д.).

---

## 3. План Реализации по Модулям

### 3.1. Базовые Утилиты и Исключения

*   **Файл:** `backend/utils/exceptions.py`
    *   **Задача:** Определить иерархию кастомных исключений.
    *   **Шаги:**
        *   Создать базовый класс `JivaPayException(Exception)`.
        *   Создать специфичные исключения, наследуемые от `JivaPayException` или стандартных исключений: `RequisiteNotFound`, `LimitExceeded`, `InsufficientBalance`, `ConfigurationError`, `OrderProcessingError`, `DatabaseError`, `NotificationError`, `CacheError` и т.д.

*   **Файл:** `backend/database/utils.py`
    *   **Задача:** Реализовать утилиты для безопасной работы с БД.
    *   **Шаги:**
        *   Реализовать `get_db_session()` как менеджер контекста (`@contextlib.contextmanager`), используя **существующий `SessionLocal` из `backend.database.engine`**, с `try...finally` для `db.close()`.
        *   Реализовать `atomic_transaction()` как декоратор или менеджер контекста, использующий `db_session.begin()` или `try...except...else` с `db.commit()` и `db.rollback()`. Добавить логирование начала/конца/ошибки транзакции.
        *   Реализовать базовые CRUD-функции (например, `create_object`, `get_object_or_none`, `update_object_db`) с логированием и обработкой стандартных исключений SQLAlchemy (`IntegrityError`, `NoResultFound`), возможно, пробрасывая кастомные исключения из `backend.utils.exceptions`.

*   **Файл:** `backend/utils/notifications.py`
    *   **Задача:** Настроить отправку оповещений о критических ошибках.
    *   **Шаги:**
        *   Интегрировать выбранную библиотеку для отправки отчетов (например, Sentry SDK).
        *   Инициализировать SDK с DSN из конфигурации.
        *   Реализовать функцию `report_critical_error(exception, context_message="", **kwargs)` для отправки исключений и дополнительного контекста в систему мониторинга.
        *   Добавить обработку ошибок при отправке оповещений (логировать, но не прерывать основной поток).

### 3.2. Middleware: Ограничение Частоты Запросов (Rate Limiting)

*   **Файлы:** `backend/middleware/rate_limiting.py`, `backend/main.py` (для подключения Middleware).
    *   **Задача:** Реализовать защиту API от злоупотреблений и простых ботов.
    *   **Шаги:**
        *   Добавить зависимость `slowapi` в `requirements.txt`.
        *   Добавить зависимость Redis (`redis[hiredis]`) если еще не добавлена.
        *   Настроить подключение к Redis (например, через `config`).
        *   В `rate_limiting.py`:
            *   Импортировать `Limiter`, `Request`.
            *   Инициализировать `Limiter` с использованием `RedisStorage` (`Limiter(key_func=get_remote_address, storage_uri=REDIS_URL)`). Можно определить разные key_func для разных стратегий (IP, user). 
            *   Определить обработчик для исключения `RateLimitExceeded` (`@app.exception_handler(RateLimitExceeded)`), который будет возвращать HTTP 429.
        *   В `backend/main.py`:
            *   Импортировать `Limiter`, `RateLimitExceeded` и созданный обработчик исключения.
            *   Добавить Middleware: `app.add_middleware(SlowAPIMiddleware)`.
            *   Добавить обработчик исключения.
        *   Применить ограничения к маршрутам:
            *   Глобально (через `default_limits` в `Limiter`).
            *   Или к конкретным `APIRouter` или эндпоинтам с использованием `limiter.limit("...")` в качестве зависимости (`Depends`) или декоратора.
        *   Реализовать различные стратегии лимитирования (по IP, по пользователю/API-ключу) при необходимости, используя разные `key_func`.
        *   Настроить конфигурацию лимитов (например, "100/minute", "10/second") **с использованием `utils.config_loader.get_typed_config_value` для чтения из БД (например, ключа `RATE_LIMIT_DEFAULT`) с fallback на значение по умолчанию.**
        *   Использовать контекстный менеджер `get_db_session_cm()` из `backend.database.utils` в функции `get_default_rate_limit()` для безопасного открытия и закрытия сессии при чтении лимитов.
        *   (Опционально) Реализовать в этом же Middleware или отдельном логику блокировки IP на основе частых ошибок или порогов Rate Limiter'а, сохраняя список блокировки в Redis.

### 3.3. Сервисы Бизнес-Логики

*   **Файл:** `backend/services/reference_data.py`
    *   **Задача:** Реализовать доступ к справочным данным с кэшированием.
    *   **Шаги:**
        *   Настроить клиент кэша (например, Redis) или использовать библиотеку для in-memory кэша (например, `cachetools`).
        *   Реализовать функции `get_exchange_rate(crypto_id, fiat_id)`, `get_bank_details(bank_id)`, `get_payment_method_details(method_id)` и т.д.
        *   Внутри функций реализовать логику: сначала проверка кэша, при промахе – запрос к БД (используя `database.utils`), запись результата в кэш, возврат результата.
        *   Добавить обработку ошибок БД и кэша (пробрасывать `CacheError`, `DatabaseError` из `backend.utils.exceptions`), логирование. Решить, возвращать ли `None` или пробрасывать исключение при отсутствии данных.

*   **Файл:** `backend/services/requisite_selector.py`
    *   **Задача:** Реализовать логику подбора реквизита.
    *   **Шаги:**
        *   Реализовать основную функцию `find_suitable_requisite(incoming_order: IncomingOrder, db_session: Session) -> Tuple[Optional[int], Optional[int]] | None` (возвращает `(requisite_id, trader_id)` или `None`, или выбрасывает исключение).
        *   Сформировать и выполнить оптимизированный SQL-запрос SQLAlchemy с JOIN'ами (`req_traders`, `traders`, `full_requisites_settings`), фильтрами по параметрам заявки, статусам, статическим лимитам.
        *   Применить сортировку по `Trader.trafic_priority` (ASC), затем по `ReqTrader.last_used_at` (ASC, NULLS FIRST) для реализации round-robin.
        *   Использовать `with_for_update(skip_locked=True)`. `limit(1)`.
        *   После назначения заявки выбранному реквизиту обновить поле `last_used_at` на текущее время.
        *   Обработать случай `NoResultFound` или пустой результат -> вернуть `None` (или пробросить `RequisiteNotFound`).
        *   Если кандидат найден: выполнить запросы для проверки динамических лимитов (агрегация по `order_history` в той же сессии).
        *   Если лимит превышен -> вернуть `None` (или пробросить `LimitExceeded`).
        *   Если все ОК -> вернуть `(requisite.id, trader.id)`.
        *   Добавить подробное логирование всех шагов и причин неудач.
        *   Перехватывать ошибки БД, логировать и пробрасывать `DatabaseError` из `backend.utils.exceptions`.

*   **Файл:** `backend/services/balance_manager.py`
    *   **Задача:** Реализовать расчет комиссий и обновление балансов.
    *   **Шаги:**
        *   Реализовать `calculate_commissions(order: OrderHistory, store: MerchantStore, trader: Trader, db_session: Session) -> Tuple[Decimal, Decimal]` (возвращает store_commission, trader_commission). Загрузить настройки `StoreCommission`, `TraderCommission`.
        *   Обработать отсутствие настроек (логировать, использовать default или пробросить `ConfigurationError` из `backend.utils.exceptions`).
        *   Реализовать `update_balances_for_completed_order(order_id: int, db_session: Session)`:
            *   Загрузить `OrderHistory`, `MerchantStore`, `Trader`.
            *   Загрузить и **заблокировать** (`with_for_update`) соответствующие строки `BalanceStore`, `BalanceTrader`.
            *   Выполнить дебетование/кредитование балансов.
            *   Обновить баланс платформы (`BalancePlatform`) и создать запись в `BalancePlatformHistory` для фиксации прибыли платформы (использовать поле `platform_profit`).
            *   Создать записи в `BalanceStoreHistory`, `BalanceTraderFiatHistory`, `BalanceTraderCryptoHistory` и `BalancePlatformHistory`.
            *   Обработать возможные ошибки (например, пробросить `InsufficientBalance` из `backend.utils.exceptions`), логировать, пробрасывать исключения.

*   **Файл:** `backend/services/order_processor.py`
    *   **Задача:** Реализовать оркестрацию обработки входящей заявки.
    *   **Шаги:**
        *   Реализовать основную функцию `process_incoming_order(incoming_order_id: int)`.
        *   **Добавить проверку идемпотентности** (проверить статус `IncomingOrder` или наличие `OrderHistory` для `incoming_order_id`) *перед* основной транзакцией.
        *   Использовать `database.utils.get_db_session` и `atomic_transaction` для **основной** логики.
        *   Внутри основной транзакции: загрузить `IncomingOrder` по `id` с `with_for_update`. Проверить статус (`'new'`, `'retrying'`).
        *   **Вызвать `fraud_detector.check_incoming_order(...)`** и обработать результат (`DENY`/`REQUIRE_MANUAL_REVIEW` -> переход к обновлению статуса).
        *   Вызвать `requisite_selector.find_suitable_requisite`.
        *   **Обработка результата:**
            *   **Успех (реквизит найден):**
                *   Вызвать `balance_manager.calculate_commissions` (только для расчета, не для записи истории).
                *   Создать объект `OrderHistory`, заполнить поля из `IncomingOrder`, добавить `requisite_id`, `trader_id`, `trader_commission`, **зафиксированный курс**.
                *   Добавить `OrderHistory` в сессию.
                *   Обновить `IncomingOrder` (`status='assigned'`, `assigned_order=order_history_obj`, `failure_reason=None`).
                *   Логировать успех.
                *   (Основная транзакция успешно коммитится декоратором/менеджером `atomic_transaction`)
            *   **Неудача (кандидат не найден / лимит / фрод) или Исключение:**
                *   (Основная транзакция откатывается декоратором/менеджером `atomic_transaction` при выходе из блока `try` по исключению или без явного `return`/`break`).
                *   В блоке `except` (или `finally`, если используется `try...finally` вокруг основной логики):
                    *   Определить причину неудачи/исключение.
                    *   **Выполнить обновление статуса `IncomingOrder` в отдельной транзакции:**
                        *   Использовать `database.utils.get_db_session` и `atomic_transaction` **повторно**.
                        *   Загрузить `IncomingOrder` (без блокировки).
                        *   Обновить поля (`retry_count`, `last_attempt_at`, `failure_reason`, статус `'retrying'` или `'failed'`).
                        *   Закоммитить **эту** транзакцию.
                        *   Логировать результат обновления статуса (успех/ошибка).
                    *   Логировать основную причину неудачи/исключение.
                    *   Вызвать `utils.notifications.report_critical_error`, если ошибка критическая.
                    *   (Если использовался `try...except`, то после обработки исключения можно его пробросить дальше `raise`, если это необходимо для логики вызывающего кода, например, Worker'а).

### 3.4. Фоновый Обработчик (Worker)

*   **Файлы:** `backend/worker/app.py` (настройка Celery/Dramatiq), `backend/worker/tasks.py` (определение задач), `backend/worker/scheduler.py` (или логика запуска/планирования задач, если не используется встроенный планировщик). Может потребоваться `requirements_worker.txt`.
    *   **Задача:** Реализовать систему фоновой обработки заявок.
    *   **Зависимости Worker'а (примерные):** `celery`/`dramatiq`, `redis`/`kombu` (брокер), `sqlalchemy`, `psycopg2-binary`/`asyncpg` (драйвер БД), `python-dotenv`, основные модели и утилиты проекта (`backend.database`, `backend.services`, `backend.utils`).
    *   **Шаги:**
        *   Выбрать и настроить брокер сообщений (Redis, RabbitMQ) и бэкенд результатов (если нужен).
        *   Настроить приложение Celery/Dramatiq (`app.py`), указать брокер, бэкенд, пути к задачам.
        *   В `tasks.py` определить задачу (например, `process_order_task`), которая принимает `incoming_order_id` и вызывает `services.order_processor.process_incoming_order`.
        *   Настроить параметры задачи: `autoretry_for` (указать перехватываемые исключения из `utils.exceptions`, например `DatabaseError`, `CacheError`), `retry_backoff` (**читать `RETRY_BACKOFF_FACTOR` из БД через `config_loader`**), `max_retries` (**читать `MAX_ORDER_RETRIES` из БД через `config_loader`**), возможно, `acks_late=True`.
        *   (Опционально, если нужно обновление балансов через Worker) Определить задачу `update_balances_task`, вызывающую `services.balance_manager.update_balances_for_completed_order`.
        *   Реализовать логику периодического запуска (scheduler): (`scheduler.py` или Celery Beat / Dramatiq cron)
            *   Запрос к `IncomingOrder` для выборки ID заявок со статусом `'new'` или `'retrying'` (с учетом `last_attempt_at` и `retry_count` для backoff).
            *   Отправка выбранных ID в очередь задач (`process_order_task.delay(order_id)`).
            *   Добавить обработку ошибок на уровне шедулера (логирование, оповещения через `utils.notifications`).
        *   Настроить запуск Worker'ов и Scheduler'а (например, через systemd или Docker Compose).
        *   Настроить мониторинг очередей и Worker'ов (Flower для Celery, или через метрики Prometheus).

### 3.5. Сервис и API для Управления Статусами Ордера

*   **Файлы:** `backend/services/order_status_manager.py`, `backend/api_routers/trader.py`, `backend/api_routers/merchant.py`, `backend/api_routers/admin.py`, `backend/api_routers/teamlead/*`.
    *   **Задача:** Реализовать логику подтверждения/отмены ордеров и соответствующие API эндпоинты.
    *   **Шаги:**
        *   В `order_status_manager.py` реализовать функции: `confirm_payment_by_client`, `confirm_order_by_trader`, `cancel_order`, `dispute_order` и т.д., используя `atomic_transaction`.
        *   Реализовать логику проверки прав доступа и корректности статусов перед изменением.
        *   Определить механизм запуска `balance_manager.update_balances_for_completed_order` после успешного подтверждения трейдером **(Рекомендация: отправка ID ордера в очередь задач Worker'а для асинхронного вызова `update_balances...` *после* успешного коммита транзакции изменения статуса. Это обеспечивает большую надежность).**
        *   В `api_routers/trader.py` добавить эндпоинты для `confirm_order_by_trader`, `cancel_order` (с обработкой загрузки чека для PayOut).
        *   В `api_routers/merchant.py` (или отдельном роутере) добавить эндпоинт для `confirm_payment_by_client` (с обработкой загрузки чека для PayIn).
        *   Добавить необходимые эндпоинты для админа/саппорта для управления статусами в нештатных ситуациях.
        *   Настроить сохранение ссылок на загруженные документы (подумать об использовании S3-совместимого хранилища).
        *   (Опционально) Реализовать в Worker'е задачу для отслеживания и обработки таймаутов ордеров.
        *   Добавить тесты для всех сценариев изменения статусов.
        *   Для TeamLead предусмотреть эндпоинты управления трейдерами (`/traders`, `/traders/{id}/traffic`, `/traders/{id}/stats`).

### 3.6. API-роутеры и динамическое подключение
*   **Общие модули (`backend/api_routers/common`)** — реализуют CRUD и бизнес-логику для разных ролей:
    - `stores.py` — управление магазинами (MerchantStore)
    - `merchant_orders.py` — операции мерчанта с ордерами
    - `trader_orders.py` — операции трейдера с ордерами
    - `teamlead_traders.py` — управление командой трейдеров (TeamLead)
    - `users.py` — CRUD пользователей и профилей (Admin)
    - `requisites.py` — управление реквизитами трейдеров
    - `support_orders.py` — работа саппорта с тикетами и ордерами
    - `settings.py` — CRUD конфигурационных настроек (Admin)
    - `admin_permissions.py` — управление флагами прав администратора
*   **Динамические роутеры (`backend/servers/{role}/server.py`)** — подключают нужные общие модули и защищаются декоратором `permission_required(role)`:
    - `servers/merchant/server.py` — монтирует `common/stores` и `common/merchant_orders`
    - `servers/trader/server.py` — монтирует `common/trader_orders`
    - `servers/teamlead/server.py` — монтирует `common/teamlead_traders`
    - `servers/support/server.py` — монтирует `common/support_orders`
    - `servers/admin/server.py` — монтирует `common/users`, `common/requisites`, `common/support_orders`, `common/settings`, `common/admin_permissions`

### 3.7. API и логика платежного шлюза
*   **Публичный шлюз (`servers/gateway/server.py`)** — монтирует `backend/api_routers/gateway/router.py` без обязательной аутентификации или с короткоживущими токенами:
    - `POST /payin/init`, `GET /payin/status/{order_id}`, `POST /payin/confirm/{order_id}`
    - `POST /payout/init`, `GET /payout/status/{order_id}`
*   **Логика** вынесена в `backend/services/gateway_service.py` и `backend/services/callback_service.py` (коллбэки, подпись, retry)
*   **Pydantic-схемы** в `shemas_enums/gateway.py`

### 3.8. Роутер мерчанта (`backend/servers/merchant/server.py`)
*   **Реализация:** монтирует `common/stores` и `common/merchant_orders`
*   **Защита:** зависимости `get_current_active_merchant`, декоратор `permission_required("merchant")`, `get_db_session`

---

## 4. Тестирование

*   **См. подробный пошаговый тест-план:** `backend/TEST_PLAN.md`.
*   Параллельно с разработкой каждого модуля писать юнит-тесты (с mock'ами зависимостей) и интеграционные тесты (с реальной тестовой БД).
*   Особое внимание уделить тестированию:
    *   Логики подбора реквизитов (`requisite_selector`) со всеми граничными условиями (лимиты, статусы, конкурентный доступ).
    *   Логики обработки ордеров (`order_processor`), включая обработку ошибок и обновление статусов.
    *   Транзакционности (`atomic_transaction`).
    *   Работы Worker'а (постановка задач, retry, backoff, обработка ошибок задачи).
    *   Обновления балансов.
    *   **Логики изменения статусов ордера (`order_status_manager`) и связанных API.**

---

## 5. Зависимости и Интеграция

*   Необходимо будет добавить новые зависимости (система очередей, кэширование, Sentry SDK, `python-dotenv`, **библиотека для работы с S3-хранилищем**, `slowapi`, `redis[hiredis]` и т.д.) в `requirements.txt` и, возможно, в `requirements_worker.txt`.
*   API Роутеры (`backend/api_routers`) должны будут использовать `database.utils` и `utils.exceptions` для создания записей `IncomingOrder` и обработки ошибок.
*   API Роутеры должны вызывать `services.order_status_manager` для изменения статусов ордеров.
*   Система подтверждения статуса ордера (`completed`/`failed`) должна будет вызывать `services.balance_manager.update_balances_for_completed_order` **(вероятно, асинхронно через Worker)**.

---

## 6. Предварительные шаги (Дополнения)

*   **Заполнение Данных (Seeding):** 
    *   Создать скрипты для заполнения начальных данных (например, в `scripts/`).
    *   Заполнить необходимые справочники (валюты, роли, платежные системы) и создать пользователя-администратора по умолчанию.
*   **Аутентификация (JWT/OAuth2):**
    *   Установлены зависимости: `python-jose[cryptography]`, `passlib[bcrypt]`.
    *   Создан файл `backend/security.py` с реализацией `create_access_token`, `verify_access_token`, `get_current_user` и `get_current_active_user`.
    *   Использован `OAuth2PasswordBearer` с соответствующими `tokenUrl`:
        - `/merchant/auth/token` — мерчант
        - `/trader/auth/token` — трейдер
        - `/admin/auth/token` — администратор
        - `/support/auth/login` — саппорт (принимает JSON)
    *   Эндпоинты логина реализованы через основную таблицу `User` и профили (`merchant_profile`, `trader_profile`, `admin_profile`, `support_profile`), во всех роутерах используется `Depends(get_db_session)` вместо кастомных `get_db` или `SessionLocal`.
    *   Все остальные эндпоинты (кроме логина) защищены через зависимости `get_current_active_user` или `get_current_active_<role>` (FastAPI `Depends`).
*   **(Если решено) Аудит Лог:** 
    *   **Задача:** Настроить запись действий пользователей и системы.
    *   **Шаги:**
        *   Убедиться, что модель `AuditLog` добавлена в `db.py`.
        *   Создать файл `backend/services/audit_logger.py`.
        *   Реализовать функцию `log_action(...)`, которая создает и добавляет запись `AuditLog` в переданную сессию БД.
        *   Интегрировать вызовы `log_action` в соответствующие места кода (логин, операции CRUD с важными сущностями, смена статусов ордера и т.д.), передавая необходимый контекст (пользователь, действие, цель, детали).
*   **CI/CD:** 
    *   **Задача:** Настроить автоматическую проверку и сборку кода.
    *   **Шаги:**
        *   Выбрать платформу CI/CD (GitHub Actions, GitLab CI, Jenkins и т.д.).
        *   Настроить пайплайн для бэкенда:
            *   Запуск линтеров (Flake8, Black, isort).
            *   Запуск юнит- и интеграционных тестов (Pytest) с использованием тестовой БД.
            *   (Опционально) Сборка Docker-образа.
            *   (Опционально) Публикация артефактов.
*   **Инфраструктура Мониторинга/Логирования:** 
    *   **Задача:** Подготовить инструменты для наблюдения за работой приложения.
    *   **Шаги:**
        *   Настроить проект в Sentry (или аналоге) и получить DSN.
        *   Развернуть (если используется self-hosted) или настроить аккаунты в системах мониторинга метрик (Prometheus/Grafana) и агрегации логов (Loki/Fluentd/ELK stack).
        *   Настроить сбор метрик из FastAPI (например, с `starlette-exporter`) и Worker'а.
        *   Настроить отправку логов приложения в систему агрегации.
*   **Объектное Хранилище (S3):** 
    *   **Задача:** Настроить хранение загружаемых файлов (чеки, документы).
    *   **Шаги:**
        *   Выбрать S3-совместимое хранилище (AWS S3, MinIO, Yandex Object Storage и т.д.).
        *   Получить/создать ключи доступа (`ACCESS_KEY`, `SECRET_KEY`), имя бакета (`BUCKET_NAME`), эндпоинт (`ENDPOINT_URL`).
        *   Добавить эти параметры в конфигурацию приложения.
        *   Добавить зависимость `boto3` (или `aiobotocore` для асинхронных операций) в `requirements.txt`.
        *   Создать утилиту (`utils/s3_client.py` или аналогичный) для инкапсуляции логики загрузки файлов в бакет (например, `upload_file(file_obj, object_name)`).
        *   Реализовать генерацию уникальных имен файлов для избежания коллизий.
        *   Настроить CORS и политики доступа для бакета, если требуется прямой доступ к файлам с фронтенда.
        *   Интегрировать `upload_file` в API эндпоинты, обрабатывающие загрузку файлов (`confirm_payment_by_client`, `confirm_order_by_trader`).
        *   Реализовать обработку ошибок при загрузке файлов.
*   **(Важно) Обнаружение Мошенничества (Fraud Detection):** 
    *   **Задача:** Настроить базовые механизмы анти-фрода.
    *   **Шаги:**
        *   Определить стратегию хранения правил/порогов/списков (конфиг, БД, Redis).
        *   Определить стратегию хранения/обновления velocity-счетчиков (Redis, БД).
        *   Создать сервис `services/fraud_detector.py`.
        *   Реализовать функции `check_incoming_order` и (опционально) `check_order_confirmation`.
        *   Интегрировать вызовы `check_incoming_order` в `services/order_processor.py` (до подбора реквизита) с обработкой результатов (`ALLOW`, `DENY`, `REQUIRE_MANUAL_REVIEW`).
        *   Добавить логирование результатов проверок в `AuditLog`.
        *   Настроить оповещения для статуса `REQUIRE_MANUAL_REVIEW`.
        *   Добавить тесты для различных сценариев фрод-проверок.
*   **Управление Данными Пользователей (GDPR и т.п.):**
    *   **Задача:** Обеспечить возможность обработки запросов субъектов данных.
    *   **Шаги (требуют отдельной проработки, могут быть реализованы позже):**
        *   Реализовать в API администрирования эндпоинты для экспорта данных пользователя (по его ID).
        *   Реализовать механизм безопасного удаления или анонимизации данных пользователя по запросу (с учетом связей и требований законодательства).
        *   Особое внимание уделить удалению/анонимизации PII в `owner_of_requisites` и других местах.
*   **Стратегия Развертывания:**
    *   **Задача:** Минимизировать время недоступности сервиса при обновлениях.
    *   **Рекомендация:** Продумать и реализовать стратегию развертывания без простоя (Zero-Downtime Deployment), например, Blue-Green Deployment или Canary Releases, особенно для production-окружения.

---

## 7. Тестирование

*   Параллельно с разработкой каждого модуля писать юнит-тесты (с mock'ами зависимостей) и интеграционные тесты (с реальной тестовой БД).
*   Особое внимание уделить тестированию:
    *   Логики подбора реквизитов (`requisite_selector`) со всеми граничными условиями (лимиты, статусы, конкурентный доступ).
    *   Логики обработки ордеров (`order_processor`), включая обработку ошибок и обновление статусов (особенно в отдельных транзакциях).
    *   Транзакционности (`atomic_transaction`).
    *   Работы Worker'а (постановка задач, retry, backoff, обработка ошибок задачи).
    *   Обновления балансов.
    *   Логики изменения статусов ордера (`order_status_manager`) и связанных API.
    *   Заполнение данных.
    *   Работы аутентификации и авторизации.
    *   Работы Rate Limiter'а.
    *   **(После наполнения тестовыми данными) Профилирование БД:** Проверить производительность ключевых запросов (особенно в `requisite_selector`, `order_processor`, поиске ордеров/пользователей) с помощью `EXPLAIN ANALYZE`. Оптимизировать запросы и индексы при необходимости.

---

## 8. Зависимости и Интеграция (Перенумерация)

*   Необходимо будет добавить новые зависимости (система очередей, кэширование, Sentry SDK, `python-dotenv`, библиотека для работы с S3-хранилищем, `slowapi`, `redis[hiredis]` и т.д.) в `requirements.txt` и, возможно, в `requirements_worker.txt`.
*   API Роутеры (`backend/api_routers`) должны будут использовать `database.utils` и `utils.exceptions` для создания записей `IncomingOrder` и обработки ошибок.
*   API Роутеры должны вызывать `services.order_status_manager` для изменения статусов ордеров.
*   Система подтверждения статуса ордера (`completed`/`failed`) должна будет вызывать `services.balance_manager.update_balances_for_completed_order` (вероятно, асинхронно через Worker).
*   **Все API эндпоинты (кроме логина) должны требовать аутентификации.**

---

Этот план является основой. В процессе реализации могут возникнуть дополнительные детали или потребоваться корректировки.

*   **Утилита работы с S3 (`utils/s3_client.py`):**
     - Реализовал загрузку файлов в S3 с помощью `boto3` и возвращение URL.
*   **(Новый) Без миграций:**
   - Добавлен скрипт `scripts/seed_config.py` для сидирования конфигурации.
   - Добавлен скрипт `scripts/seed_data.py` для сидирования ролей и дефолтного администратора. 