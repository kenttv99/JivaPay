# Схема базы данных JivaPay

Настоящий документ описывает ключевые сущности и их взаимосвязи в базе данных JivaPay.

## Общая ER-диаграмма

> Рекомендуется дополнить актуальной диаграммой (например, в формате PNG/Drawio) в папке `docs/`.

## Основные таблицы

### 1. Пользователи и роли
- **users**: основная таблица пользователей
  - `id`, `email`, `password_hash`, `is_active`, `role_id`, `created_at`, `updated_at`
- **roles**: перечень ролей (`admin`, `merchant`, `trader`, `support`, `teamlead`)
  - `id`, `name`, `description`

### 2. Магазины и реквизиты
- **merchant_store**: магазины (точки приёма платежей)
  - `id`, `user_id` (FK → users), `name`, `api_key`, `callback_url`, `is_active`, `limits`, `created_at`
- **balance_store**: балансы магазинов
  - `id`, `store_id` (FK → merchant_store), `currency_id`, `amount`

- **trader**: профиль трейдера
  - `id`, `user_id` (FK → users), `is_active`, `traffic_priority`, `created_at`
- **req_trader**: реквизиты трейдера
  - `id`, `trader_id` (FK → trader), `type`, `details`, `status`, `last_used_at`, `created_at`
- **full_requisites_settings**: настройки лимитов и расписания для реквизитов
  - `req_id` (FK → req_trader), `min_amount`, `max_amount`, `currency_id`, `daily_limit`, `active_hours`

### 3. Ордеры и история
- **incoming_orders**: входящие заявки
  - `id`, `store_id`, `amount`, `currency_id`, `customer_id`, `status`, `created_at`, `last_attempt_at`, `retry_count`, `failure_reason`
- **order_history**: закреплённые ордера после обработки
  - `id`, `incoming_order_id` (FK → incoming_orders), `requisite_id`, `trader_id`, `store_commission`, `trader_commission`, `rate`, `status`, `processed_at`

### 4. Баланс и история
- **balance_store_history**, **balance_trader_fiat_history**, **balance_trader_crypto_history** — история изменений балансов с полями `id`, `balance_id`, `delta`, `currency_id`, `created_at`

### 5. Конфигурация и логирование
- **configuration_settings**: настраиваемые параметры приложения
  - `key`, `value`
- **audit_logs**: записи аудита
  - `id`, `user_id`, `action`, `target`, `details`, `timestamp`

## Индексы и ограничения
- Основные внешние ключи и уникальные индексы на `email`, `api_key`, сочетания `req_trader` + `status`.
- Для таблиц с историей рекомендуются составные индексы по `(created_at, balance_id)` для ускорения выборок по периоду.

## Миграции
Все изменения схемы фиксируются в скриптах Alembic в папке `backend/migrations`. Для создания новой миграции используйте:
```bash
alembic revision -m "<описание>" --autogenerate
```
После генерации проверьте порядок создания таблиц и FK, при необходимости скорректируйте вручную.

