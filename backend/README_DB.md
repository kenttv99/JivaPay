# Документация по Базе Данных JivaPay

## 1. Общее Описание

Эта база данных предназначена для хранения информации, необходимой для работы платежной системы JivaPay. Она включает данные о пользователях (мерчантах и трейдерах), их магазинах и реквизитах, историю финансовых операций (ордеров), входящие заявки, балансы, настройки и справочную информацию.

Структура разработана для поддержки основной логики системы:
*   **Прием входящих заявок:** Немедленная фиксация запросов на PayIn / PayOut от магазинов мерчантов.
*   **Асинхронная обработка:** Поиск и назначение подходящих реквизитов трейдеров для выполнения заявок из очереди.
*   **Выполнение ордеров:** Отслеживание статуса ордеров после назначения реквизита.
*   **Учет:** Отслеживание балансов и истории операций для всех участников.
*   **Управление:** Настройка лимитов, комиссий и доступов.

## 2. Основные Сущности (Таблицы)

### 2.0. Роли (`roles`) - НОВАЯ
*   **Назначение:** Централизованное хранение ролей пользователей системы.
*   **Ключевые поля:**
    *   `id`: PK.
    *   `name`: Уникальное имя роли (строка: 'super_admin', 'admin_full', 'admin_limited', 'support_trader_settings', 'support_orders', 'merchant', 'trader').
    *   `description`: Описание роли.
    *   `(Опционально) applies_to`: Строка ('admin', 'support', 'all'), для обозначения применимости роли.

### 2.1. Пользователи (`users`)
*   **Назначение:** Общая таблица для всех типов пользователей системы, хранящая базовые учетные данные и роль.
*   **Ключевые поля:**
    *   `id`: Уникальный ID пользователя.
    *   `email`: Mapped[str] = mapped_column(unique=True, index=True)
    *   `password_hash`: Mapped[str]
    *   `role_id`: Mapped[int] = mapped_column(ForeignKey('roles.id')) # Связь с таблицей roles
    *   `is_active`: Mapped[bool] = mapped_column(default=True) # Для блокировки доступа
    *   `created_at`: Mapped[datetime] = mapped_column(server_default=func.now())
    *   `updated_at`: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    # Связи к таблицам ролей для доступа к специфичным данным
    role: Mapped["Role"] = relationship() # Связь для доступа к имени и описанию роли
    merchant_profile: Mapped[Optional["Merchant"]] = relationship(back_populates="user")
    trader_profile: Mapped[Optional["Trader"]] = relationship(back_populates="user")
    admin_profile: Mapped[Optional["Admin"]] = relationship(back_populates="user")
    support_profile: Mapped[Optional["Support"]] = relationship(back_populates="user")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="user")

### 2.2. Мерчанты (`merchants`, `merchant_stores`)
*   `merchants`: Хранит **специфичную** информацию об аккаунтах мерчантов. **Общие данные (email, пароль, статус) теперь в `users`.**
    *   `id`: Mapped[intpk]
    *   `user_id`: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True) # Связь с общей таблицей users
    *   `first_name`: Mapped[Optional[str]]
    *   `last_name`: Mapped[Optional[str]]
    *   `avatar_url`: Mapped[Optional[str]]
    *   `two_factor_auth_token`: Mapped[Optional[str]]
    *   `verification_level`: Mapped[Optional[str]]
    *   # Убраны: email, password_hash, is_active (access), created_at
    *   user: Mapped["User"] = relationship(back_populates="merchant_profile")
    *   stores: Mapped[List["MerchantStore"]] = relationship(back_populates="merchant")
    *   incoming_orders: Mapped[List["IncomingOrder"]] = relationship(back_populates="merchant")
    *   order_history: Mapped[List["OrderHistory"]] = relationship(back_populates="merchant")
    *   balance_stores: Mapped[List["BalanceStore"]] = relationship("BalanceStore", secondary="merchant_stores", primaryjoin="Merchant.id == MerchantStore.merchant_id", secondaryjoin="BalanceStore.store_id == MerchantStore.id", viewonly=True, lazy="dynamic") # Связь через merchant_stores

*   `merchant_stores`: Хранит информацию о магазинах, созданных мерчантами.
    *   **Ключевые поля:**
        *   `merchant_id`: Связь с владельцем-мерчантом.
        *   `store_name`: Название магазина.
        *   `crypto_currency_id`: Основная *криптовалюта* для баланса и работы магазина.
        *   `fiat_currency_id`: Основное *фиатное* направление работы магазина.
        *   `lower_limit`, `upper_limit`: Лимиты (мин/макс) для суммы ордеров *в фиатной валюте* (DECIMAL 20, 2).
        *   `public_api_key`, `private_api_key`: API ключи магазина (Внимание: `private_api_key` требует безопасного хранения/хеширования в приложении).
        *   `pay_in_enabled`, `pay_out_enabled`: Флаги, разрешающие прием (PayIn) или выплаты (PayOut) для всего магазина.
        *   `access`, `trafic_access`: Флаги доступа.
        *   `callback_url`: URL для отправки коллбэков (webhooks) о статусе ордеров.
        *   `secret_key`: Секретный ключ для подписи коллбэков.
        *   `gateway_require_customer_id_param`: Mapped[bool] = mapped_column(default=False) # Требовать customer_id в параметрах шлюза?
        *   `gateway_require_amount_param`: Mapped[bool] = mapped_column(default=False) # Требовать сумму в параметрах шлюза?

### 2.3. Трейдеры (`traders`, `req_traders`, `full_requisites_settings`, `owner_of_requisites`)
*   `traders`: Хранит **специфичную** информацию об аккаунтах трейдеров. **Общие данные теперь в `users`.**
    *   `id`: Mapped[intpk]
    *   `user_id`: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True) # Связь с общей таблицей users
    *   `first_name`: Mapped[Optional[str]]
    *   `last_name`: Mapped[Optional[str]]
    *   `avatar_url`: Mapped[Optional[str]]
    *   `two_factor_auth_token`: Mapped[Optional[str]]
    *   `preferred_fiat_currency_id`: Mapped[Optional[int]] = mapped_column(ForeignKey('fiat_currencies.id'))
    *   `crypto_currency_id`: Mapped[Optional[int]] = mapped_column(ForeignKey('crypto_currencies.id'))
    *   `verification_level`: Mapped[Optional[str]]
    *   `pay_in`: Mapped[bool] = mapped_column(default=False)
    *   `pay_out`: Mapped[bool] = mapped_column(default=False)
    *   `in_work`: Mapped[bool] = mapped_column(default=False, index=True) # Индекс оставлен здесь, т.к. важен для выборки
    *   `trafic_priority`: Mapped[int] = mapped_column(default=5) # **Приоритет трейдера для распределения заявок.** При создании реквизита его вес (`distribution_weight`) копируется из этого поля. При изменении этого значения у трейдера веса всех его реквизитов должны быть синхронизированы (обновлены). Индивидуальная корректировка веса реквизита возможна только вручную через админку или саппорт с нужным уровнем доступа.
    *   `time_zone_id`: Mapped[Optional[int]] = mapped_column(ForeignKey('time_zones.id'))
    *   `base_pay_in_limit`: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 2)) # Базовый лимит PayIn, устанавливается админом/саппортом
    *   `base_pay_out_limit`: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 2)) # Базовый лимит PayOut, устанавливается админом/саппортом
    # Убраны: email, password_hash, access (заменен is_active в users), created_at
    *   user: Mapped["User"] = relationship(back_populates="trader_profile")
    *   requisites: Mapped[List["ReqTrader"]] = relationship(back_populates="trader")
    *   order_history: Mapped[List["OrderHistory"]] = relationship(back_populates="trader")
    *   balance_traders: Mapped[List["BalanceTrader"]] = relationship(back_populates="trader")
    *   balance_trader_fiat_history: Mapped[List["BalanceTraderFiatHistory"]] = relationship(back_populates="trader")
    *   balance_trader_crypto_history: Mapped[List["BalanceTraderCryptoHistory"]] = relationship(back_populates="trader")
    *   # Индекс `ix_trader_priority_lookup` нужно будет пересоздать с учетом `users.is_active` и `traders.in_work`

*   `owner_of_requisites`: Определяет "владельца" (группу) реквизитов (ФИО).
*   `req_traders`: Хранит информацию о конкретных реквизитах (карта, счет и т.д.), добавленных трейдером.
    *   **Ключевые поля:** `trader_id`, `owner_of_requisites_id`, `fiat_id`, `method_id`, `bank_id`, `req_number`, `status`, `last_used_at` (TIMESTAMP, nullable=True).
    *   `req_number`: Mapped[str] # **Важно:** Номер реквизита. Требует защиты. Рекомендуется шифровать на уровне приложения перед сохранением в БД (например, используя `cryptography.fernet`) или использовать возможности шифрования самой СУБД. Обеспечить маскирование при отображении в API и логах (например, показывать только последние 4 цифры).
    *   `last_used_at`: TIMESTAMP (nullable=True). Время последнего назначения реквизита для round-robin распределения.
    *   `distribution_weight`: Mapped[int] # **Вес реквизита.** Инициализируется из `traders.trafic_priority`. **Не может быть NULL.** Синхронизируется при изменении `trafic_priority` трейдера. Может быть изменен вручную только через админку/саппорт.
    *   `is_excluded_from_distribution`: Mapped[bool] = mapped_column(default=False) # Флаг для ручного исключения из подбора.

*   `full_requisites_settings`: Хранит детальные настройки для *каждого* реквизита (`requisite_id`).
    *   **Ключевые поля:** `pay_in`, `pay_out` (флаги), `lower_limit`, `upper_limit`, `total_limit`, `turnover_day_max`, `turnover_limit_minutes`.

### 2.4. Входящие Заявки (`incoming_orders`)
*   **Назначение:** Фиксирует *каждый* запрос на PayIn/PayOut от мерчанта **немедленно** после его поступления. Служит очередью для асинхронной обработки и подбора реквизитов.
*   **Ключевые поля:**
    *   `id`: Уникальный ID входящей заявки.
    *   `client_id`: Mapped[Optional[str]] = mapped_column(index=True) # ID клиента на стороне мерчанта (НОВОЕ)
    *   `merchant_id`: Mapped[int] = mapped_column(ForeignKey('merchants.id'))
    *   `store_id`: Mapped[int] = mapped_column(ForeignKey('merchant_stores.id'))
    *   `gateway_id`: Шлюз магазина, через который пришла заявка (если применимо).
    *   `target_method_id`, `target_bank_id`: Опциональные предпочтения мерчанта.
    *   `fiat_currency_id`, `crypto_currency_id`: Валюты операции.
    *   `total_fiat`, `amount_currency`: Суммы операции.
    *   `exchange_rate`: Курс обмена, зафиксированный в момент создания заявки.
    *   `store_commission`: Сумма комиссии магазина, рассчитанная в момент создания заявки.
    *   `order_type`: Тип ('pay_in', 'pay_out').
    *   `status`: Текущий статус заявки в очереди ('new', 'processing', 'assigned', 'failed', 'retrying').
    *   `retry_count`, `last_attempt_at`, `failure_reason`: Данные для управления обработкой.
    *   `created_at`, `updated_at`: Временные метки.
    *   `assigned_order`: Связь (один-к-одному) с созданным ордером в `order_history`.
    *   `payment_method_id`: ID метода оплаты (FK на `payment_methods`).
    *   `bank_id`: ID банка (FK на `banks`).
    *   `crypto_currency_id`: ID криптовалюты (FK на `crypto_currencies`).
    *   `fiat_currency_id`: ID фиатной валюты (FK на `fiat_currencies`).
    *   `amount_crypto`: Сумма в криптовалюте (для PayOut).
    *   `amount_fiat`: Сумма в фиатной валюте (для PayIn).
    *   `amount_currency`: Сумма операции в валюте.
    *   `customer_id`: Идентификатор клиента в системе мерчанта (строка, nullable).
    *   `customer_ip`: IP адрес конечного клиента (строка, nullable).
    *   `return_url`: URL для редиректа клиента после завершения операции (строка, nullable).
    *   `payment_details_submitted`: Флаг, указывающий, предоставил ли клиент детали/чек оплаты (Boolean, default=False).
    *   merchant: Mapped["Merchant"] = relationship(back_populates="incoming_orders")
    *   store: Mapped["MerchantStore"] = relationship(back_populates="incoming_orders")
    *   assigned_order_rel: Mapped[Optional["OrderHistory"]] = relationship(back_populates="incoming_order")

### 2.5. История Ордеров (`order_history`)
*   **Назначение:** Фиксирует ордера, которым **уже был успешно назначен** реквизит трейдера. Содержит полную информацию о выполненной или выполняемой операции.
*   **Ключевые поля:**
    *   `id`: Уникальный ID выполненного ордера.
    *   `client_id`: Mapped[Optional[str]] = mapped_column(index=True) # ID клиента на стороне мерчанта (НОВОЕ)
    *   `incoming_order_id`: Mapped[int] = mapped_column(ForeignKey('incoming_orders.id'), unique=True)
    *   `hash_id`: Mapped[str] = mapped_column(unique=True, index=True)
    *   `trader_id`: Mapped[int] = mapped_column(ForeignKey('traders.id'))
    *   `requisite_id`: Mapped[int] = mapped_column(ForeignKey('req_traders.id'))
    *   `merchant_id`: Mapped[int] = mapped_column(ForeignKey('merchants.id'))
    *   `store_id`: Mapped[int] = mapped_column(ForeignKey('merchant_stores.id'))
    *   `method_id`, `bank_id`, `crypto_currency_id`, `fiat_id`: Детали операции.
    *   `order_type`: Тип ордера ('pay_in', 'pay_out').
    *   `exchange_rate`: Курс обмена (копируется из `incoming_orders` или может быть переопределен).
    *   `amount_currency`, `total_fiat`: Суммы.
    *   `store_commission`: Комиссия магазина (копируется из `incoming_orders`).
    *   `trader_commission`: Комиссия трейдера (рассчитывается при назначении).
    *   `status`: Статус *выполнения* ордера ('pending', 'processing', 'completed', 'failed', 'cancelled' и т.д.) - **после** назначения реквизита.
    *   `created_at`, `updated_at`: Временные метки.
    *   incoming_order: Mapped["IncomingOrder"] = relationship(back_populates="assigned_order_rel")
    *   trader: Mapped["Trader"] = relationship(back_populates="order_history")
    *   requisite: Mapped["ReqTrader"] = relationship(back_populates="order_histories")
    *   merchant: Mapped["Merchant"] = relationship(back_populates="order_history")
    *   store: Mapped["MerchantStore"] = relationship(back_populates="order_history")
    *   balance_store_history: Mapped[List["BalanceStoreHistory"]] = relationship(back_populates="order")
    *   balance_trader_fiat_history: Mapped[List["BalanceTraderFiatHistory"]] = relationship(back_populates="order")
    *   balance_trader_crypto_history: Mapped[List["BalanceTraderCryptoHistory"]] = relationship(back_populates="order")

### 2.6. Балансы и История Балансов (`balance_stores`, `balance_store_history`, `balance_traders`, `balance_trader_fiat_history`, `balance_trader_crypto_history`)
*   `balance_stores`: Текущий *крипто*-баланс магазина.
*   `balance_store_history`: История изменений *крипто*-баланса магазинов.
*   `balance_traders`: Текущий *фиат*-баланс трейдера.
*   `balance_trader_fiat_history`: История изменений *фиат*-баланса трейдеров.
*   `balance_trader_crypto_history`: История изменений *крипто*-баланса трейдеров.

### 2.7. Справочники (`banks`, `payment_methods`, `fiat_currencies`, `crypto_currencies`, `countries`, `time_zones`, `exchange_rates`, `avalible_bank_methods`)
*   Хранят справочную информацию.

### 2.8. Администраторы и Поддержка (`admins`, `supports`)
*   **Управление доступом (RBAC - Улучшенный Подход):**
    *   При инициализации системы создается один супер-админ (`role_id` = 'super_admin') с записью в `admins` и всеми флагами разрешений = `True`.
    *   Система использует таблицу `roles` для определения шаблонов ролей ('admin_full', 'support_orders' и т.д.).
    *   Каждому пользователю (`users`) назначается одна роль (`role_id`).
    *   Конкретные права доступа определяются булевыми флагами в профильных таблицах `admins` и `supports`.
    *   При создании админа/саппорта можно выбрать роль-шаблон (которая установит дефолтный набор флагов) и затем **индивидуально скорректировать** нужные флаги разрешений.
    *   Супер-админ может управлять `role_id` и **всеми флагами разрешений** у других админов и саппортов.
    *   Администраторы (`admins`) имеют набор флагов, определяющих их возможности (см. ниже).
    *   Только супер-админ или админ с флагом `can_manage_other_admins = True` может добавлять/изменять других админов.
    *   Саппорты (`supports`) могут быть добавлены только админом с флагом `can_manage_supports = True`.
    *   Права саппортов определяются набором флагов (см. ниже).
    *   Все действия по управлению пользователями, изменению прав и доступов должны логироваться в системе аудита.
*   `admins`: Хранит **специфичную** информацию и **флаги разрешений** для пользователей с ролью 'admin'.
    *   `id`: Mapped[intpk]
    *   `user_id`: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    *   `username`: Mapped[str] # Или first/last name
    *   **Флаги разрешений (примеры):**
    *   `can_manage_other_admins`: Mapped[bool] = mapped_column(default=False)
    *   `can_manage_supports`: Mapped[bool] = mapped_column(default=False)
    *   `can_manage_merchants`: Mapped[bool] = mapped_column(default=False)
    *   `can_manage_traders`: Mapped[bool] = mapped_column(default=False)
    *   `can_edit_system_settings`: Mapped[bool] = mapped_column(default=False)
    *   `can_edit_limits`: Mapped[bool] = mapped_column(default=False)
    *   `can_view_full_logs`: Mapped[bool] = mapped_column(default=False)
    *   `can_handle_appeals`: Mapped[bool] = mapped_column(default=False)
    *   # Убраны: email, password_hash, is_active, created_at
    *   user: Mapped["User"] = relationship(back_populates="admin_profile")

*   `supports`: Хранит **специфичную** информацию и **флаги разрешений** для пользователей с ролью 'support'.
    *   `id`: Mapped[intpk]
    *   `user_id`: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    *   `username`: Mapped[str] # Или first/last name
    *   **Флаги разрешений (примеры):**
    *   `can_edit_trader_settings`: Mapped[bool] = mapped_column(default=False)
    *   `can_manage_orders`: Mapped[bool] = mapped_column(default=False) # Например, менять статус
    *   `can_view_orders`: Mapped[bool] = mapped_column(default=True)
    *   `can_handle_appeals`: Mapped[bool] = mapped_column(default=False)
    *   `can_view_sensitive_data`: Mapped[bool] = mapped_column(default=False) # Например, полные номера реквизитов
    *   # Убраны: email, password_hash, is_active, created_at
    *   user: Mapped["User"] = relationship(back_populates="support_profile")

## 3. Логика Обработки Заявок и Подбора Реквизита

Процесс разделен на два этапа:

**Этап 1: Прием Заявки (Синхронный)**
1.  Мерчант через магазин инициирует запрос на PayIn/PayOut.
2.  Приложение **немедленно** создает запись в таблице `incoming_orders` со статусом `'new'`, сохраняя все детали запроса.
3.  Мерчанту возвращается подтверждение приема заявки (например, ID из `incoming_orders`).

**Этап 2: Подбор Реквизита и Создание Ордера (Асинхронный)**
1.  **Фоновый обработчик (Worker)** периодически или по сигналу запрашивает заявки из `incoming_orders` со статусом `'new'` или `'retrying'`.
2.  Для каждой заявки Worker **начинает транзакцию БД** (с уровнем изоляции `REPEATABLE READ` или `SERIALIZABLE`).
3.  Внутри транзакции Worker выполняет **поиск кандидата:** SQL-запрос (`SELECT ... FOR UPDATE SKIP LOCKED`), который:
    *   Объединяет `req_traders`, `traders`, `full_requisites_settings`.
    *   Фильтрует по параметрам заявки (`fiat_id`, `method_id`, `bank_id`).
    *   Проверяет статические условия: `Trader.in_work = TRUE`, `ReqTrader.status = 'approve'`, флаги `pay_in`/`pay_out` в `FullRequisitesSettings`, статические лимиты (`lower_limit`, `upper_limit`).
    *   **Сортирует** кандидатов по `Trader.trafic_priority` (ASC), затем по `req_traders.last_used_at` (ASC, NULLS FIRST) для реализации round-robin.
    *   Выбирает **одного** лучшего кандидата (`LIMIT 1`).
    *   **Блокирует** строку кандидата (`FOR UPDATE SKIP LOCKED`).
    *   После назначения заявки обновляет поле `last_used_at` у выбранного реквизита на текущее время.
4.  **Проверка динамических лимитов:** Если кандидат найден и заблокирован:
    *   Рассчитывается текущий дневной/общий оборот кандидата по данным из `order_history`.
    *   Проверяется, не превысят ли лимиты (`turnover_day_max`, `total_limit`) из `FullRequisitesSettings` с учетом суммы текущей заявки.
5.  **Принятие решения:**
    *   **Успех:** Если все проверки пройдены, Worker:
        1.  Создает новую запись в `order_history`, копируя данные из `incoming_orders` и добавляя `requisite_id`, `trader_id`.
        2.  Обновляет запись в `incoming_orders`, устанавливая `status='assigned'` и связывая ее с созданным `order_history.id`.
        3.  Коммитит транзакцию.
    *   **Неудача (Нет кандидата / Лимит):** Если кандидат не найден или не прошел динамическую проверку:
        1.  Worker обновляет запись в `incoming_orders` (увеличивает `retry_count`, ставит `last_attempt_at`, возможно, меняет статус на `retrying`/`failed`, записывает причину).
        2.  Откатывает транзакцию (или ее часть, если кандидат был найден, но не подошел).

Этот двухэтапный подход с асинхронной обработкой гарантирует, что ни одна заявка не теряется, система может обрабатывать очередь, а подбор реквизита происходит с максимальной надежностью проверки лимитов.

## 4. Соглашения и Принципы

*   **Именование:** snake_case.
*   **Время:** `TIMESTAMP(timezone=True)`, UTC.
*   **Точность:** DECIMAL(20, 8) крипто, DECIMAL(20, 2) фиат.
*   **Каскадное удаление:** Осторожно, в основном для несамостоятельных сущностей.
*   **Индексы:** Созданы для PK, FK, часто фильтруемых/сортируемых полей, а также специализированные индексы (`ix_trader_priority_lookup`, `ix_incoming_orders_status_created`, `ix_incoming_orders_merchant_store`) для оптимизации ключевых запросов.
*   **Безопасность:** Чувствительные данные требуют защиты на уровне приложения.

Эта документация описывает текущее состояние. При внесении изменений в структуру или логику базы данных, пожалуйста, обновляйте этот файл.

class OrderHistory(Base):
    # ... (existing fields)


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[intpk]
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now(), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', name='fk_audit_user_id')) # Ссылка на общую таблицу users (ИЗМЕНЕНО)
    ip_address: Mapped[Optional[str]] = mapped_column(String)
    action: Mapped[str] = mapped_column(String, index=True)
    target_entity: Mapped[Optional[str]] = mapped_column(String)
    target_id: Mapped[Optional[int]] = mapped_column(Integer)
    details: Mapped[Optional[dict]] = mapped_column(JSON)

    user: Mapped["User"] = relationship(back_populates="audit_logs") # Связь с User (ИЗМЕНЕНО)

# --- Relationships ---
# Добавлены связи в описаниях таблиц выше

# --- Indexes ---
# ... (существующие индексы)
Index('ix_audit_logs_target', AuditLog.target_entity, AuditLog.target_id)
# Индекс ix_trader_priority_lookup нужно будет пересмотреть, возможно, создать view или использовать JOIN с users в запросе.
Index('ix_incoming_orders_client_id', IncomingOrder.client_id) # НОВЫЙ индекс
Index('ix_order_history_client_id', OrderHistory.client_id) # НОВЫЙ индекс

### Механизм гибкого распределения заявок между реквизитами трейдеров

*   **Логика распределения:**
    *   По умолчанию используется сортировка по `Trader.trafic_priority` (ASC), затем по `ReqTrader.last_used_at` (ASC, NULLS FIRST) для round-robin.
    *   Поле `ReqTrader.distribution_weight` (которое инициализируется и синхронизируется с `Trader.trafic_priority`) позволяет реализовать стратегии взвешенного распределения, если это потребуется в будущем, но основной механизм - `trafic_priority` + `last_used_at`.
    *   Поле `ReqTrader.is_excluded_from_distribution` (BOOLEAN) позволяет вручную временно исключать реквизиты из автоматического подбора.
*   **Поля в `req_traders`:**
    *   `distribution_weight` (INT, **NOT NULL**) — Вес реквизита. Инициализируется из `trafic_priority` трейдера. Синхронизируется при изменении `trafic_priority`. Может быть изменен вручную админом/саппортом.
    *   `is_excluded_from_distribution` (BOOLEAN, default=False) — Флаг ручного исключения реквизита из распределения.
    *   `last_used_at` (TIMESTAMP, nullable=True) - Обновляется после назначения заявки реквизиту для round-robin.
*   **Принципы работы:**
    *   Управление `is_excluded_from_distribution` и ручное изменение `distribution_weight` осуществляется через админ-панель или API поддержки.
    *   Все изменения параметров должны логироваться и быть доступны для аудита.

### Управление Доступом (RBAC) и Разграничение Прав

*   **Структура:**
    *   Таблица `roles` хранит шаблоны ролей (`super_admin`, `admin_full`, `support_orders` и т.д.).
    *   Таблица `users` содержит `role_id` (FK к `roles`).
    *   Таблицы `admins` и `supports` содержат специфичные для роли данные и набор **булевых флагов разрешений** (`can_manage_users`, `can_edit_limits`, `can_edit_trader_settings` и т.д.).
*   **Принцип работы:**
    *   Роль (`role_id`) определяет базовый набор разрешений (какие флаги по умолчанию `True`/`False`).
    *   При создании/редактировании админа или саппорта можно выбрать роль-шаблон, которая установит флаги по умолчанию.
    *   **Конкретные права** определяются значениями **индивидуальных булевых флагов** в таблицах `admins` или `supports`. Эти флаги можно изменять независимо от выбранной роли (с соответствующими правами на управление).
    *   Супер-админ имеет все флаги `True` и может управлять всеми другими пользователями и их флагами.
    *   Другие админы могут управлять пользователями и их флагами в соответствии со *своими* флагами разрешений (например, `can_manage_supports`).
*   **Примеры уровней доступа (определяются набором флагов):**
    *   Для админов:
        *   `super_admin` — все флаги = `True`.
        *   `admin_full` — флаги `can_manage_supports`, `can_manage_merchants`, `can_manage_traders`, `can_edit_system_settings`, `can_edit_limits`, `can_view_full_logs`, `can_handle_appeals` = `True`. Флаг `can_manage_other_admins` = `False`.
        *   `admin_limited` — только часть флагов = `True` (например, `can_edit_limits`, `can_view_full_logs`, `can_handle_appeals`).
    *   Для саппортов:
        *   `support_trader_settings` — флаг `can_edit_trader_settings` = `True`, остальные специфичные для саппорта флаги = `False` (кроме `can_view_orders`).
        *   `support_orders` — флаги `can_manage_orders`, `can_handle_appeals` = `True`, остальные = `False` (кроме `can_view_orders`).
        *   `support_readonly` — все флаги = `False` (кроме `can_view_orders`).
*   **Типовые сценарии работы и разграничения прав:**
    *   Супер-админ:
        *   Добавляет/удаляет админов и саппортов, назначает и изменяет их права.
        *   Имеет доступ ко всем настройкам, логам, пользовательским данным и системным параметрам.
    *   Админ (полный доступ):
        *   Управляет пользователями (мерчанты, трейдеры, саппорты), лимитами, настройками системы.
        *   Может просматривать и редактировать заявки, управлять кабинетами трейдеров.
        *   Может добавлять/удалять саппортов, но не других админов или супер-админа.
    *   Админ (ограниченный доступ):
        *   Может только просматривать и обрабатывать заявки, управлять лимитами, но не имеет доступа к управлению пользователями или саппортами.
    *   Саппорт (настройки трейдеров):
        *   Может создавать и редактировать реквизиты трейдеров, выставлять лимиты, изменять статусы реквизитов.
    *   Саппорт (заявки и апелляции):
        *   Может просматривать и обрабатывать заявки, работать с апелляциями, но не имеет доступа к настройкам трейдеров.
    *   Саппорт (только просмотр):
        *   Может только просматривать заявки, историю действий и статусы, без возможности вносить изменения.
*   **Архитектурные принципы:**
    *   Все проверки прав доступа реализуются на уровне бизнес-логики (утилиты, сервисы, API) путем проверки **конкретных булевых флагов** у пользователя.
    *   При изменении структуры прав или добавлении новых ролей необходимо обновлять документацию, флаги в моделях и логику проверки прав.
    *   Все действия по изменению прав, добавлению/удалению пользователей, изменению настроек должны логироваться в системе аудита (`AuditLog`).
*   **Гибкая настройка прав доступа:**
    *   При создании/редактировании админа или саппорта предоставляется интерфейс для установки **каждого флага разрешения** (`True`/`False`).
    *   Выбор роли (`role_id`) может использоваться для **предзаполнения** этих флагов значениями по умолчанию, но итоговые права определяются **текущим состоянием флагов**.
    *   Нет необходимости в отдельном поле `access_to` или флаге `custom_settings`.

