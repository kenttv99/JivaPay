# База данных JivaPay

В этом документе описана структура нашей базы данных и как мы с ней работаем. Мы используем PostgreSQL 14+ с асинхронной архитектурой для быстрой и надежной работы.

## Как устроена база данных

### Пользователи и роли
- **users** — основная таблица пользователей
  - Хранит `id`, `email`, `password_hash`, `is_active`, `role_id`, `created_at`, `updated_at`
- **roles** — список ролей в системе
  - Содержит `id`, `name`, `description`
  - Поддерживаемые роли: `admin`, `merchant`, `trader`, `support`, `teamlead`

### Профили пользователей
- **admins** — профиль администратора
  - Связан с `users` через `user_id`
  - Хранит `username` и `granted_permissions` (JSON с правами доступа)
- **supports** — профиль поддержки
  - Связан с `users` через `user_id`
  - Содержит `username`, `role_description` и `granted_permissions`
- **teamleads** — профиль тимлида
  - Связан с `users` через `user_id`
  - Имеет `username` и `granted_permissions`
  - Управляет командой трейдеров

### Магазины и реквизиты
- **merchant_store** — магазины
  - Хранит `id`, `user_id`, `name`, `api_key`, `callback_url`, `is_active`, `limits`, `created_at`
- **balance_store** — балансы магазинов
  - Содержит `id`, `store_id`, `currency_id`, `amount`

### Трейдеры
- **trader** — профиль трейдера
  - Содержит `id`, `user_id`, `is_active`, `traffic_priority`, `team_lead_id`
  - Новое поле `is_traffic_enabled_by_teamlead` для управления трафиком
- **req_trader** — реквизиты трейдера
  - Хранит `id`, `trader_id`, `type`, `details`, `status`, `last_used_at`, `created_at`
- **full_requisites_settings** — настройки реквизитов
  - Содержит `req_id`, `min_amount`, `max_amount`, `currency_id`, `daily_limit`

### Ордеры
- **incoming_orders** — входящие заявки
  - Хранит `id`, `store_id`, `amount`, `currency_id`, `customer_id`, `status`, `created_at`, `last_attempt_at`, `retry_count`, `failure_reason`
- **order_history** — обработанные ордера
  - Содержит `id`, `incoming_order_id`, `requisite_id`, `trader_id`, `store_commission`, `trader_commission`, `rate`, `status`, `processed_at`

### Балансы и история
- **balance_store_history**, **balance_trader_fiat_history**, **balance_trader_crypto_history** — история изменений балансов
- **balance_platform** — текущий баланс платформы
- **balance_platform_history** — история прибыли платформы

### Системные таблицы
- **configuration_settings** — настройки системы
- **audit_logs** — логи аудита

## Как мы работаем с базой данных

### Асинхронная работа
```python
# Пример создания сессии
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

# Пример транзакции
async with atomic_transaction(db_session) as transaction:
    await create_object(db_session, model, data)
    await update_object_db(db_session, obj, new_data)
```

### Оптимизация
- Пул соединений: 20 основных + 10 дополнительных
- Автоматическое пересоздание соединений каждые 30 минут
- Индексы для быстрого поиска
- Асинхронные транзакции для надежности

### Миграции
```bash
# Создаем миграцию
alembic revision --autogenerate -m "описание изменений"

# Применяем миграции
alembic upgrade head
```

## Важные моменты

1. **Права доступа**
   - Храним в JSON поле `granted_permissions`
   - Гибкая настройка без изменения схемы

2. **Индексы**
   - Основные индексы на внешних ключах
   - Составные индексы для истории по датам
   - Индексы для часто используемых фильтров

3. **Мониторинг**
   - Логируем все операции
   - Следим за производительностью
   - Контролируем пул соединений 