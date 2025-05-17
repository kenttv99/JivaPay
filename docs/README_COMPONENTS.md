# Справочник компонентов бэкенда

В этом документе перечислены ключевые компоненты серверной части JivaPay, их назначение и расположение в проекте.

## 1. API-роутеры (`backend/api_routers`)
- `common/` — общие модули CRUD-операций и логики для разных ролей:
  - `stores.py` — управление магазинами (`MerchantStore`)
  - `merchant_orders.py` — операции мерчанта с ордерами
  - `trader_orders.py` — операции трейдера с ордерами
  - `teamlead_traders.py` — управление трейдерами (TeamLead)
  - `users.py` — CRUD пользователей и профилей (Admin)
  - `requisites.py` — управление реквизитами трейдеров
  - `support_orders.py` — работа с тикетами и ордерами (Support)
  - `configuration_router.py` — CRUD конфигурационных настроек (Admin)
  - `admin_permissions.py` — управление правами администратора
- `role-based routers` — пустые роутеры в `backend/servers/*/server.py`, которые динамически включают модули из `common/` и защищаются декоратором `permission_required(role)`.

## 2. Модели и ORM (`backend/database`)
- `db.py` — основные SQLAlchemy-модели (`User`, `MerchantStore`, `Trader`, `OrderHistory` и др.).
    - **Обновлено:** В `Trader` добавлено поле `is_traffic_enabled_by_teamlead: Mapped[bool]`. В профилях `Admin`, `Support`, `TeamLead` добавлены поля `granted_permissions: Mapped[Optional[dict]] = mapped_column(JSON)` для гранулярных прав. В `Support` добавлено поле `role_description: Mapped[Optional[str]]`. Из `FullRequisitesSettings` **удалено** поле `active_hours`. Старые булевы флаги прав в `Admin` и `Support`, если они полностью заменены гранулярной системой, должны быть удалены или помечены как устаревшие.
- `utils.py` — утилиты работы с сессией (get_db_session, atomic_transaction, CRUD-функции).
- `migrations/` — скрипты Alembic для регистраций и изменений схемы БД.

## 3. Сервисы (`backend/services`)
- `user_service.py` — логика работы с пользователями и ролями. **Расширен для предоставления статистики по ролям (администраторы, тимлиды, саппорты), получения деталей профилей (`Admin`, `Support`, `TeamLead`, включая `granted_permissions`), и обновления этих профилей. Функции получения статистики (`get_administrators_statistics`, `get_supports_statistics`, `get_teamleads_statistics`) были рефакторены для использования общих утилит из `backend/utils/query_utils.py` для применения фильтров, сортировки и пагинации. Принимают стандартизированные параметры (`page`, `per_page`, `sort_by`, `sort_direction`) и возвращают стандартизированный словарь с результатами. Функции обновления профилей (`update_administrator_profile`, `update_support_profile`, `update_teamlead_profile`) рефакторены для использования общей вспомогательной функции `_update_user_and_profile_generic`, унифицировав логику и аудит.**
- `order_processor.py` — оркестрация обработки входящих ордеров. Обеспечивает копирование полей `amount_fiat`, `amount_crypto`, `client_id`, `customer_id`, `customer_ip`, `payment_details_submitted` из `IncomingOrder` в `OrderHistory`. Поле `OrderHistory.total_fiat` использует соответствующее значение из `IncomingOrder`.
- `order_service.py`: **Значительно расширен для предоставления истории ордеров (`get_orders_history`) и их количества (`get_orders_count`). Функция `get_orders_history` поддерживает комплексную фильтрацию (включая `amount_exact`, `amount_min`, `amount_max`, диапазоны дат, поиск по ключевым полям, таким как `hash_id`, ID входящего ордера, email мерчанта/трейдера, название магазина), сортировку, пагинацию и строгий учет гранулярных прав пользователя. Обе функции рефакторены для использования `backend/utils/query_utils.py`, принимают стандартизированные параметры и возвращают стандартизированные ответы.**
- `balance_manager.py` — расчет и обновление балансов.
- `reference_data.py` — кэширование и выдача справочных данных.
- `requisite_selector.py` — подбор подходящих реквизитов. **Логика обновлена для учета всех условий активности трейдера и реквизита: `Trader.user.is_active`, `Trader.in_work`, `Trader.is_traffic_enabled_by_teamlead`, `ReqTrader.status == 'approve'`, и активность направлений `FullRequisitesSettings.pay_in/pay_out`.**
- `requisite_service.py`: **Расширен для предоставления статистики онлайн-реквизитов (`get_online_requisites_stats`) с фильтрацией, сортировкой и гранулярным учетом прав. Эта функция рефакторена для использования `backend/utils/query_utils.py`, принимает стандартизированные параметры и возвращает стандартизированный ответ. Также включает функции для получения деталей реквизита для модерации админами (`get_requisite_details_for_moderation`) и изменения статуса реквизита админами (`set_requisite_status`) с аудит-логированием.**
- `order_status_manager.py` — подтверждение и отмена ордеров.
- `audit_logger.py` — запись событий аудита. **Используется функция `log_event` для фиксации важных действий.**
- `audit_service.py` (или в рамках `audit_logger.py`): Для извлечения логов критических ошибок (`get_critical_system_errors`).
- `fraud_detector.py` — проверки анти-фрода.
- `gateway_service.py` — логика публичного API-шлюза.
- `callback_service.py` — отправка коллбэков мерчантам.
- `platform_service.py` (новый): Для получения агрегированного баланса платформы (`get_platform_balances`).
- `trader_service.py`: **Предоставляет статистику трейдеров (`get_traders_statistics`) и полные детали трейдера (`get_trader_full_details`). Функция `get_traders_statistics` поддерживает комплексную фильтрацию, сортировку, пагинацию и гранулярный учет прав. Рефакторена для использования `backend/utils/query_utils.py`, принимает стандартизированные параметры и возвращает стандартизированный ответ (включая `statistics_columns`).**
- `merchant_service.py`: **Аналогично `trader_service.py`, но для мерчантов (`get_merchants_statistics`, `get_merchant_full_details`). Функция `get_merchants_statistics` также рефакторена для использования `backend/utils/query_utils.py` и возвращает стандартизированный ответ.**
- `permission_service.py` (новый): **Ключевой сервис для управления и проверки гранулярных прав (`granted_permissions` в JSON-полях профилей). Включает функции `get_user_permissions`, `update_user_permissions` (с аудит-логированием), `check_permission` (с поддержкой wildcards и `{id}`), и `check_specific_or_any_permission` (для проверки специфичных или общих прав).**
- `teamlead_service.py`: Для управления трейдерами в команде (`get_managed_traders`, `set_trader_traffic_status_by_teamlead` с аудит-логированием), получения статистики по команде (`get_team_statistics`) и детальной информации о тимлиде/его команде (`get_teamlead_full_details`). **Логика расчета активных реквизитов (`active_reqs`) обновлена для учета всех флагов активности трейдера. Функции, возвращающие списки/статистику, могут быть рассмотрены для рефакторинга с использованием `query_utils.py` при необходимости.**

## 3.1. Новые API Эндпоинты (Детализация из `docs/ADDITIONAL_FEATURES_AND_COMPONENTS.md`)

### Общие для Администраторов, Саппортов, Тимлидов (с учетом ролевых прав)
*   **Баланс площадки (Админ):**
    *   `GET /api/admin/platform/balance` (Ответ: `PlatformBalanceResponseSchema`)
*   **История ордеров (Админ, Саппорт):**
    *   `GET /api/admin/orders/history` (Ответ: `OrderHistoryAdminResponseSchema`)
    *   `GET /api/support/orders/history` (Ответ: `OrderHistoryAdminResponseSchema`)
*   **Количество реквизитов онлайн (Админ, Саппорт, Тимлид):**
    *   `GET /api/admin/requisites/online-stats` (Ответ: `RequisiteOnlineStatsResponseSchema`)
    *   `GET /api/support/requisites/online-stats` (Ответ: `RequisiteOnlineStatsResponseSchema`)
    *   `GET /api/teamlead/requisites/online-stats` (Ответ: `RequisiteOnlineStatsResponseSchema`)
    *   SSE: `GET /api/<role>/requisites/online-stats/stream` (необходимо уточнить схему ответа)
*   **Количество трейдеров (Админ, Саппорт):**
    *   `GET /api/admin/traders/stats` (Ответ: `TraderStatisticsResponseSchema` или аналогичная для админа)
    *   `GET /api/support/traders/stats` (Ответ: `TraderStatisticsResponseSchema`)
*   **Количество мерчантов и их магазинов (Админ):**
    *   `GET /api/admin/merchants/stats` (Ответ: Схема статистики мерчантов, например, `MerchantStatisticsResponseSchema`)
*   **Общее количество ордеров (Админ):**
    *   `GET /api/admin/orders/count` (Ответ: `OrderCountResponseSchema`)
*   **Логи критических ошибок (Админ):**
    *   `GET /api/admin/logs/critical-errors` (Ответ: Схема списка логов)
*   **Количество администраторов (Админ):**
    *   `GET /api/admin/administrators/stats` (Ответ: `AdminStatisticsResponse`)
*   **Количество тимлидов (Админ):**
    *   `GET /api/admin/teamleads/stats` (Ответ: `TeamLeadStatisticsResponse`)
*   **Количество саппортов (Админ):**
    *   `GET /api/admin/supports/stats` (Ответ: `SupportStatisticsResponse`)

### Функционал Администраторов (Управление другими пользователями)
*   **Управление Администраторами:**
    *   `GET /api/admin/administrators/{user_id}` (Ответ: `AdminDetailsSchema`)
    *   `PUT /api/admin/administrators/{user_id}` (Тело запроса: `AdminProfileUpdateSchema`, Ответ: `AdminDetailsSchema`)
    *   `PUT /api/admin/users/{user_id}/permissions` (Тело запроса: `UserPermissionsUpdateSchema`, Ответ: `UserRead` с обновленными правами или `AdminDetailsSchema`)
    *   `POST /api/admin/users/{user_id}/block`
    *   `POST /api/admin/users/{user_id}/unblock`
    *   `POST /api/admin/administrators` (Тело запроса: `UserCreate` + `AdminProfileCreate`, Ответ: `AdminDetailsSchema`)
*   **Управление Саппортами:**
    *   `GET /api/admin/supports/{user_id}` (Ответ: `SupportDetailsSchema`)
    *   `PUT /api/admin/supports/{user_id}` (Тело запроса: `SupportProfileUpdateSchema`, Ответ: `SupportDetailsSchema`)
    *   (Управление правами саппорта через общий эндпоинт `PUT /api/admin/users/{user_id}/permissions`)
*   **Управление Тимлидами:**
    *   `GET /api/admin/teamleads/{user_id}` (Ответ: `TeamLeadDetailsSchema`)
    *   `PUT /api/admin/teamleads/{user_id}` (Тело запроса: `TeamLeadProfileUpdateSchema`, Ответ: `TeamLeadDetailsSchema`)
    *   (Управление правами тимлида через общий эндпоинт `PUT /api/admin/users/{user_id}/permissions`)
*   **Просмотр деталей Трейдеров (Админ):**
    *   `GET /api/admin/traders/{trader_id}/full-details` (Ответ: Схема полных деталей трейдера)
*   **Просмотр деталей Мерчантов (Админ):**
    *   `GET /api/admin/merchants/{merchant_id}/full-details` (Ответ: Схема полных деталей мерчанта)


### Функционал Саппортов (определяется их `granted_permissions`)
*   **Просмотр деталей Трейдеров (если разрешено):**
    *   `GET /api/support/traders/{trader_id}/details` (Ответ: `SupportTraderDetailsSchema`)
*   **Просмотр деталей Мерчантов/Магазинов (если разрешено):**
    *   `GET /api/support/merchants/{merchant_id}/details` (Ответ: `SupportMerchantDetailsSchema`)
    *   `GET /api/support/stores/{store_id}/details` (Ответ: `SupportStoreDetailsSchema`)
*   **Действия над ордерами (если разрешено):**
    *   `POST /api/support/orders/{order_id}/action` (Тело запроса: `SupportOrderActionPayloadSchema`, Ответ: `SupportActionResponseSchema`)

### Функционал Тимлидов
*   **Управление своей командой Трейдеров:**
    *   `GET /api/teamlead/managed-traders` (Ответ: `TeamLeadTraderListResponseSchema` или `List[TeamLeadTraderBasicInfoSchema]`)
    *   `POST /api/teamlead/managed-traders/{trader_id}/traffic` (Параметр: `enable: bool`, Ответ: `TraderTrafficStatusResponse`)
    *   `GET /api/teamlead/team/statistics` (Ответ: `TeamStatisticsSchema`)
    *   (Детальная статистика по трейдеру может быть отдельным эндпоинтом или частью `GET /api/teamlead/managed-traders/{trader_id}`)

## 4. Утилиты и скрипты (`backend/utils`, `backend/scripts`)
- `utils/exceptions.py` — кастомные исключения.
- `utils/config_loader.py` — чтение и типизация настроек из БД.
- `utils/notifications.py` — отправка оповещений о критических ошибках.
- `utils/s3_client.py` — работа с S3 (MinIO).
- `scripts/manage_db.py` — унифицированный скрипт для управления БД, включая инициализацию (`init`), сидирование конфигураций (`seed-config`) и основных данных (`seed-data`).
- `utils/query_utils.py` (новая): **Модуль с вспомогательными функциями для построения SQLAlchemy запросов, включая пагинацию (`apply_pagination`), сортировку (`apply_sorting`), фильтры по статусу пользователя (`apply_user_status_filter`) и диапазону дат (`apply_date_range_filter`), а также для получения пагинированных результатов вместе с общим количеством (`get_paginated_results_and_count`). Используется в `user_service.py` и планируется к использованию в других сервисах для стандартизации обработки запросов.**
- `utils/permission_checker.py` (или внутри `services.permission_service`): **Функционал реализован в `services.permission_service.py` (функции `check_permission`, `_match_permission`).**

## 5. Фоновый воркер (`backend/worker`)
- `app.py` — настройка Celery (broker, backend, очереди).
- `tasks.py` — задачи обработки ордеров и балансов.
- `scheduler.py` — планировщик задач (при необходимости).

## 6. Middleware и основные настройки (`backend/middleware`, `backend/config`)
- `middleware/rate_limiting.py` — ограничение частоты запросов.
- `config/settings.py` — Pydantic Settings для конфигурации приложения.
- `servers/*/server.py` — точки входа FastAPI (подключение middleware, роутеров).

## 7. Docker и развертывание
- `Dockerfile` — контейнеризация приложения.
- `docker-compose.yml` — локальная разработка и тестирование всех сервисов.

## 1. Общая структура

Директория `backend` реализует серверную логику для различных ролей (мерчант, трейдер, саппорт, админ) и содержит вспомогательные модули для работы с БД, логированием, криптографией, конфигами и API-роутерами.

**Важное требование безопасности:** Вся внешняя коммуникация с API бэкенда (от фронтенда, от API мерчантов) **должна** осуществляться исключительно по протоколу **HTTPS**.

---

## 2. Компоненты

### 2.1. `database/`

*   **engine.py**
    *   Инициализация SQLAlchemy engine и сессии.
    *   Использует переменные окружения для подключения к PostgreSQL.
    *   Экспортирует: `engine`, `SessionLocal`.
*   **migrations/**
    *   Скрипты Alembic для миграций схемы БД.
*   **db.py** (Определяет `Base` и все модели таблиц БД, включая `Merchant`, `Trader`, `IncomingOrder`, `OrderHistory` и другие; модели подробно описаны в `README_DB.md`)

### 2.2. `config/`

*   **logger.py**
    *   Универсальный логгер (консоль/файл).
    *   **Рекомендация:** Настроить форматтер для вывода логов в структурированном виде (например, JSON).
    *   Экспортирует: `get_logger`.
*   **crypto.py**
    *   Функции для хеширования и проверки паролей (bcrypt).
    *   Экспортирует: `hash_password`, `verify_password`.
*   **settings.py** (Или аналогичный, например, чтение из `.env`)
    *   Загрузка и предоставление доступа к настройкам приложения (строка подключения к БД, секретные ключи, параметры API, настройки Worker'а, Redis URL, Sentry DSN, ключи S3 и т.д.).

### 2.3. `servers/`

*   **Назначение:** Содержит точки входа (FastAPI приложения) для каждой роли.
*   **Структура:** Поддиректории `merchant/`, `trader/`, `admin/`, `support/`. В каждой - `server.py`, инициализирующий FastAPI `app` для этой роли.
*   **Взаимодействие:** Импортируют и монтируют соответствующие `APIRouter` из `api_routers/`, могут подключать специфичные для роли Middleware.

### 2.4. `api_routers/`

*   **Назначение:** Обработка входящих HTTP-запросов, валидация данных (с использованием схем Pydantic из `schemas_enums`), вызов соответствующей бизнес-логики из сервисов, формирование HTTP-ответов.
*   **Структура:** Разделены по ролям пользователей (`merchant`, `trader`, `admin`, `support`). Каждый роутер может содержать подмодули (например, `auth.py`, `stores.py` внутри `merchant/`).
*   **Взаимодействие:** Импортируют и используют сервисы (`services.*`), утилиты БД (`database.utils`), схемы (`schemas_enums.*`), утилиты безопасности (`security.py`), конфигурацию.

### 2.5. `schemas_enums/`

*   **Назначение:** Содержит Pydantic-модели (схемы) и Python Enums для валидации данных API запросов/ответов и типизации.
*   **Структура:** Могут быть разделены на файлы по ролям или сущностям (например, `merchant_schemas.py`, `order_schemas.py`, `common_enums.py`).
    *   `order.py`: Схемы `IncomingOrderRead`, `OrderHistoryRead` и другие, связанные с ордерами.
    *   `user.py`, `requisite.py`, `platform.py`, `trader.py`, `support_schemas.py`, `teamlead_schemas.py`: Добавлены и обновлены схемы для поддержки нового функционала ролей Admin, Support, TeamLead.
*   **Примеры:** Схемы для логина, регистрации, создания/обновления магазинов/реквизитов, представления ордеров, перечисления для статусов, ролей, типов ордеров.
*   **Взаимодействие:** Используются в `api_routers` для валидации и сериализации, а также могут использоваться в `services` для типизации.

### 2.6. `middleware/`

*   **Назначение:** Обработка запросов/ответов на сквозном уровне.
*   **Примеры:** Rate Limiting, CORS, логирование запросов.
*   **Реализация:** Функции или классы, совместимые с FastAPI.
*   **Подключение:** Регистрируются в `servers/*/server.py` или в общем `main.py`, если он есть.

### 2.7. `services/`

*   **Назначение:** Инкапсуляция основной бизнес-логики.
*   **Примеры:** `requisite_selector.py`, `order_processor.py`, `balance_manager.py`, `reference_data.py`, `order_status_manager.py`, `audit_logger.py`, `fraud_detector.py`.
*   **Взаимодействие:** Используют `database.utils`, модели (`database.*`), кастомные исключения (`utils.exceptions`), конфигурацию. Вызываются из `api_routers` или `worker`.

### 2.8. `utils/`

*   **Назначение:** Вспомогательные функции и классы общего назначения, не являющиеся основной бизнес-логикой.
*   **Примеры:** `exceptions.py` (кастомные исключения), `notifications.py` (отправка оповещений), `s3_client.py` (работа с S3), возможно, функции форматирования дат/чисел.

### 2.9. `worker/`

*   **Назначение:** Реализация фонового обработчика задач (например, на Celery или Dramatiq).
*   **Структура:** `app.py` (инициализация приложения Worker'а), `tasks.py` (определение задач), `scheduler.py` (логика запуска периодических задач).
*   **Взаимодействие:** Вызывает сервисы (`services.*`) для выполнения задач. Использует брокер сообщений (Redis/RabbitMQ).

### 2.10. `security.py` (В корне `backend/` или в `utils/`)

*   **Назначение:** Содержит функции и зависимости для аутентификации и авторизации (работа с JWT, проверка токенов, получение текущего пользователя).
*   **Взаимодействие:** Используется в `api_routers` через `Depends`.

### 2.11. `Платежный Шлюз (Payment Gateway)`

*   **Назначение:** Компонент, предоставляющий интерфейс (API и потенциально UI) для **конечных клиентов (покупателей) магазинов мерчантов**. Отвечает за:
    *   Отображение формы оплаты/выплаты.
    *   Прием данных от клиента (сумма, метод оплаты, ID клиента магазина).
    *   Инициацию создания `IncomingOrder` через вызов соответствующих сервисов.
    *   Отображение подобранных реквизитов клиенту.
    *   Прием подтверждения оплаты от клиента (включая загрузку чеков).
    *   Информирование клиента о статусе операции.
    *   Перенаправление клиента на `return_url` мерчанта.
    *   Отправку **коллбэков (webhooks)** на `callback_url` мерчанта для серверного уведомления об изменении статуса ордера.
    *   Взаимодействует с `services` (Order Service, Requisite Service, Status Manager), `utils` (S3 для чеков) и использует свой набор API-эндпоинтов, вероятно, не требующих стандартной аутентификации мерчанта/трейдера.

---

## 3. Вспомогательные файлы корневой директории `backend/`

*   **README_DB.md:** Документация по БД.
*   **README_COMPONENTS.md:** Этот файл.
*   **README_UTILITIES.md:** Описание логики сервисов.
*   **README_IMPLEMENTATION_PLAN.md:** План реализации.
*   **requirements.txt:** Основные зависимости.
*   **requirements_worker.txt:** (Опционально) Дополнительные зависимости для Worker'а.
*   **alembic.ini:** Конфигурация Alembic.
*   **.env / .env.example:** Файлы конфигурации/переменных окружения.
*   **__init__.py:** Обозначение корневого пакета.

---

Эта структура обеспечивает модульность и разделение ответственности между компонентами бэкенд-приложения.

## 3. Основные Технологии

*   **Язык:** Python 3.10+