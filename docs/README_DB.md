# Схема базы данных JivaPay

Настоящий документ описывает ключевые сущности и их взаимосвязи в базе данных JivaPay.

## Общая ER-диаграмма

> Рекомендуется дополнить актуальной диаграммой (например, в формате PNG/Drawio) в папке `docs/`.

## Основные таблицы

### 1. Пользователи и роли
- **users**: основная таблица пользователей
  - `id`, `email`, `password_hash`, `is_active`, `role_id` (FK -> `roles`.`id`), `created_at`, `updated_at`
- **roles**: перечень ролей (`admin`, `merchant`, `trader`, `support`, `teamlead`)
  - `id`, `name`, `description`
- **admins** (профиль администратора, связан с `users`):
  - `id`, `user_id` (FK -> `users`.`id`), `username`
  - `granted_permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, server_default='[]')` (для гранулярных прав)
  - _Старые булевы флаги прав, если были, должны быть удалены или помечены как устаревшие._
- **supports** (профиль саппорта, связан с `users`):
  - `id`, `user_id` (FK -> `users`.`id`), `username`
  - `role_description: Mapped[Optional[str]]` (для фильтрации/описания специализации)
  - `granted_permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, server_default='[]')` (для гранулярных прав)
- **teamleads** (профиль тимлида, связан с `users`):
  - `id`, `user_id` (FK -> `users`.`id`), `username`
  - `granted_permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, server_default='[]')` (для гранулярных прав)
  - Связь один-ко-многим с `traders` для управления командой.

### 2. Магазины и реквизиты
- **merchant_store**: магазины (точки приёма платежей)
  - `id`, `user_id` (FK → users), `name`, `api_key`, `callback_url`, `is_active`, `limits`, `created_at`
- **balance_store**: балансы магазинов
  - `id`, `store_id` (FK → merchant_store), `currency_id`, `amount`

- **trader**: профиль трейдера
  - `id`, `user_id` (FK → users), `is_active`, `traffic_priority`, `team_lead_id` (FK -> `teamleads`.`id`, опционально)
  - `is_traffic_enabled_by_teamlead: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)` (управляется тимлидом)
  - `created_at`
- **req_trader**: реквизиты трейдера
  - `id`, `trader_id` (FK → trader), `type`, `details`, `status`, `last_used_at`, `created_at`
- **full_requisites_settings**: настройки лимитов и расписания для реквизитов
  - `req_id` (FK → req_trader), `min_amount`, `max_amount`, `currency_id`, `daily_limit`
  - _Поле `active_hours` **удалено**; "онлайн" статус реквизита определяется более сложной логикой, учитывающей в том числе `Trader.is_traffic_enabled_by_teamlead`._

### 3. Ордеры и история
- **incoming_orders**: входящие заявки
  - `id`, `store_id`, `amount`, `currency_id`, `customer_id`, `status`, `created_at`, `last_attempt_at`, `retry_count`, `failure_reason`
- **order_history**: закреплённые ордера после обработки
  - `id`, `incoming_order_id` (FK → incoming_orders), `requisite_id`, `trader_id`, `store_commission`, `trader_commission`, `rate`, `status`, `processed_at`

### 4. Баланс и история
- **balance_store_history**, **balance_trader_fiat_history**, **balance_trader_crypto_history** — история изменений балансов с полями `id`, `balance_id`, `delta`, `currency_id`, `created_at`
- **balance_platform**: текущий баланс платформы по криптовалютам
  - `id`, `currency_id`, `balance`, `updated_at`
- **balance_platform_history**: история прибыли платформы
  - `id`, `order_id`, `currency_id`, `balance_change`, `new_balance`, `created_at`
- Поле `platform_profit` в таблицах `incoming_orders` и `order_history` для фиксации прибыли платформы

### 5. Конфигурация и логирование
- **configuration_settings**: настраиваемые параметры приложения
  - `key`, `value`
- **audit_logs**: записи аудита
  - `id`, `user_id`, `action`, `target`, `details`, `timestamp`

## Индексы и ограничения
- Основные внешние ключи и уникальные индексы на `email`, `api_key`, сочетания `req_trader` + `status`.
- Для таблиц с историей рекомендуются составные индексы по `(created_at, balance_id)` для ускорения выборок по периоду.
- **Новое:** Рекомендуется рассмотреть добавление композитных индексов для полей, часто используемых в фильтрации и сортировке в новых компонентах статистики (например, в `order_history` по `status`, `created_at`, `trader_id`, `store_id`; в `req_trader` по `status`, `trader_id`, типу и т.д.).

## Замечания по гранулярным правам
- Гранулярные права для ролей `Admin`, `Support`, `TeamLead` хранятся в JSON поле `granted_permissions` в их соответствующих таблицах профилей. Это позволяет гибко настраивать доступ к различным функциям и данным без изменения схемы БД.
- Отдельные таблицы для разрешений (`AdminPermissions`, `SupportPermissions`) не используются, вместо этого используется строковый список разрешений в JSON.

## Миграции
Все изменения схемы фиксируются в скриптах Alembic в папке `backend/migrations`. Для создания новой миграции используйте:
```bash
alembic revision -m "<описание>" --autogenerate
```
После генерации проверьте порядок создания таблиц и FK, при необходимости скорректируйте вручную.

