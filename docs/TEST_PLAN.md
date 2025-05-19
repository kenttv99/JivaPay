# План тестирования JivaPay

Версия: v2025.05.13

## Подготовка к тестированию

1. Убедитесь, что у вас установлены все нужные инструменты:
   - `docker` для запуска сервисов
   - `curl` для тестирования API
   - `psql` для работы с базой данных

2. Проверьте, что файл `.env` содержит актуальные настройки

3. Для Redis на хосте нужно установить `vm.overcommit_memory = 1` и перезапустить контейнер

4. Запустите все сервисы:
   ```bash
   docker compose up -d
   ```

5. Если база пустая или нужна переинициализация, используйте CLI `manage_db`:
   ```bash
   # Создаем базу
   docker compose exec merchant_api python -m backend.scripts.manage_db init
   
   # Заполняем конфигурацию
   docker compose exec merchant_api python -m backend.scripts.manage_db seed-config
   
   # Добавляем тестовые данные
   docker compose exec merchant_api python -m backend.scripts.manage_db seed-data
   
   # Добавляем справочники
   docker compose exec merchant_api python -m backend.scripts.manage_db seed-reference
   
   # Добавляем платежные реквизиты
   docker compose exec merchant_api python -m backend.scripts.manage_db seed-payment-refs
   ```
   > Права для админа (admin@example.com) создаются в seed_data.py

## Проверка работоспособности

1. Проверьте, что все контейнеры запущены:
   ```bash
   docker compose ps
   ```

2. Проверьте доступность PostgreSQL:
   ```bash
   docker compose exec postgres pg_isready
   # Должно показать: accepting connections
   ```

3. Проверьте Redis:
   ```bash
   docker compose exec redis redis-cli PING
   # Должно ответить: PONG
   ```

4. Проверьте здоровье всех API:
   ```bash
   curl -fsSL http://127.0.0.1:18001/health # API мерчанта
   curl -fsSL http://127.0.0.1:8002/health  # API трейдера
   curl -fsSL http://127.0.0.1:8003/health  # API шлюза
   curl -fsSL http://127.0.0.1:8004/health  # API админа
   curl -fsSL http://127.0.0.1:8005/health  # API саппорта
   curl -fsSL http://127.0.0.1:8006/health  # API тимлида
   ```
   Все должны ответить: `{"status":"ok"}`

5. Проверьте воркер:
   ```bash
   docker compose logs worker --tail=50
   # В логах должна быть строка `ready.`
   ```

## Тестирование авторизации

### Администратор

1. Получите токен админа:
   ```bash
   ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8004/admin/auth/token \
        -d 'username=admin@example.com&password=adminpass' \
        -H 'Content-Type: application/x-www-form-urlencoded' | jq -r .access_token)
   echo $ADMIN_TOKEN
   ```
   Должен вернуться JWT токен

2. Проверьте, что без токена нельзя получить доступ:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8004/admin/platform/balance
   # Должно вернуть: 401
   ```

3. Проверьте доступ с токеном:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8004/admin/platform/balance \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   # Должно вернуть: 200
   ```

### Саппорт

1. Создайте тестового саппорта через админку:
   ```bash
   # Замените на свои значения
   SUPPORT_EMAIL="support_test1@example.com"
   SUPPORT_PASSWORD="StrOngPassword123!"
   
   curl -X POST http://127.0.0.1:8004/admin/supports/ \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{
              "email": "'"$SUPPORT_EMAIL"'",
              "password": "'"$SUPPORT_PASSWORD"'",
              "username": "TestSupportUser1",
              "role_description": "General Tier 1 Support",
              "granted_permissions": ["orders:view:limited_list", "orders:view:status_pending", "users:view:trader_contact"]
            }'
   ```
   Должен вернуть HTTP 201 и данные саппорта. Запомните ID.

2. Проверьте, что нельзя войти с неправильными данными:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" \
     -X POST http://127.0.0.1:8005/support/auth/login \
     -H 'Content-Type: application/json' \
     -d '{"email":"nonexistent@example.com","password":"wrong"}'
   # Должно вернуть: 401
   ```

3. Войдите с правильными данными:
   ```bash
   SUPPORT_TOKEN=$(curl -s -X POST http://127.0.0.1:8005/support/auth/login \
        -H 'Content-Type: application/json' \
        -d '{"email":"'"$SUPPORT_EMAIL"'","password":"'"$SUPPORT_PASSWORD"'"}' | jq -r .access_token)
   echo $SUPPORT_TOKEN
   ```
   Должен вернуться JWT токен

### Тимлид

1. Создайте тестового тимлида:
   ```bash
   # Замените на свои значения
   TEAMLEAD_EMAIL="teamlead_test1@example.com"
   TEAMLEAD_PASSWORD="SecurePassword123!"
   
   curl -X POST http://127.0.0.1:8004/admin/teamleads/ \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{
              "email": "'"$TEAMLEAD_EMAIL"'",
              "password": "'"$TEAMLEAD_PASSWORD"'",
              "username": "TestTeamLeadUser1",
              "granted_permissions": ["team:manage:trader_traffic", "team:view:requisite_stats", "team:view:trader_list"]
            }'
   ```
   Должен вернуть HTTP 201 и данные тимлида. Запомните ID.

2. Войдите как тимлид:
   ```bash
   TEAMLEAD_TOKEN=$(curl -s -X POST http://127.0.0.1:8006/teamlead/auth/token \
        -d 'username='"$TEAMLEAD_EMAIL"'&password='"$TEAMLEAD_PASSWORD"'' \
        -H 'Content-Type: application/x-www-form-urlencoded' | jq -r .access_token)
   echo $TEAMLEAD_TOKEN
   ```
   Должен вернуться JWT токен

### Мерчант

1. Создайте тестового мерчанта:
   ```bash
   MERCHANT_EMAIL="merchant_test1@example.com"
   MERCHANT_PASSWORD="PasswordForMerchant1!"
   
   curl -X POST http://127.0.0.1:8004/admin/merchants/ \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{
              "email": "'"$MERCHANT_EMAIL"'",
              "password": "'"$MERCHANT_PASSWORD"'",
              "first_name": "Test",
              "last_name": "Merchant"
            }'
   ```
   Должен вернуть HTTP 201 и данные мерчанта. Запомните ID.

2. Войдите как мерчант:
   ```bash
   MERCHANT_TOKEN=$(curl -s -X POST http://127.0.0.1:18001/merchant/auth/token \
        -d 'username='"$MERCHANT_EMAIL"'&password='"$MERCHANT_PASSWORD"'' \
        -H 'Content-Type: application/x-www-form-urlencoded' | jq -r .access_token)
   echo $MERCHANT_TOKEN
   ```
   Должен вернуться JWT токен

### Трейдер

1. Создайте тестового трейдера:
   ```bash
   TRADER_EMAIL="trader_test1@example.com"
   TRADER_PASSWORD="PasswordForTrader1!"
   
   curl -X POST http://127.0.0.1:8004/admin/traders/ \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{
              "email": "'"$TRADER_EMAIL"'",
              "password": "'"$TRADER_PASSWORD"'",
              "first_name": "Test",
              "last_name": "Trader"
            }'
   ```
   Должен вернуть HTTP 201 и данные трейдера. Запомните ID.

   > Если тестируете полный флоу тимлида, привяжите трейдера к тимлиду:
   ```bash
   curl -X PUT http://127.0.0.1:8004/admin/traders/{TRADER_ID} \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"team_lead_id": {TEAMLEAD_ID}}'
   ```

2. Войдите как трейдер:
   ```bash
   TRADER_TOKEN=$(curl -s -X POST http://127.0.0.1:8002/trader/auth/token \
        -d 'username='"$TRADER_EMAIL"'&password='"$TRADER_PASSWORD"'' \
        -H 'Content-Type: application/x-www-form-urlencoded' | jq -r .access_token)
   echo $TRADER_TOKEN
   ```
   Должен вернуться JWT токен

## Проверка ограничения запросов

1. Сделайте 101 быстрый запрос к эндпоинту `/health`:
   ```bash
   for i in $(seq 1 101); do
     curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18001/health
   done
   ```
   Первые 100 запросов должны вернуть 200, 101-й — 429

## Тестирование магазинов мерчанта

1. Создайте тестовый магазин:
   ```bash
   STORE_NAME="Test Store Alpha"
   STORE_RESPONSE=$(curl -s -X POST http://127.0.0.1:18001/merchant/stores \
       -H "Authorization: Bearer $MERCHANT_TOKEN" \
       -H 'Content-Type: application/json' \
       -d '{
             "store_name": "'"$STORE_NAME"'",
             "crypto_currency_id":1,
             "fiat_currency_id":1,
             "lower_limit":"10.00",
             "upper_limit":"1000.00",
             "pay_in_enabled":true,
             "pay_out_enabled":true,
             "callback_url": "https://httpbin.org/post",
             "secret_key": "myStoreSecretKeyForCallbacks123"
           }')
   echo $STORE_RESPONSE
   STORE_ID=$(echo $STORE_RESPONSE | jq -r .id)
   API_KEY=$(echo $STORE_RESPONSE | jq -r .public_api_key)
   echo "Store ID: $STORE_ID, API Key: $API_KEY"
   ```
   Должен вернуть HTTP 201 и данные магазина, включая API ключ

2. Получите список магазинов:
   ```bash
   curl -X GET http://127.0.0.1:18001/merchant/stores \
       -H "Authorization: Bearer $MERCHANT_TOKEN"
   ```
   Должен вернуть HTTP 200 и список магазинов

3. Получите детали магазина:
   ```bash
   curl -X GET http://127.0.0.1:18001/merchant/stores/$STORE_ID \
       -H "Authorization: Bearer $MERCHANT_TOKEN"
   ```
   Должен вернуть HTTP 200 и данные магазина

4. Обновите настройки магазина:
   ```bash
   curl -X PATCH http://127.0.0.1:18001/merchant/stores/$STORE_ID \
       -H "Authorization: Bearer $MERCHANT_TOKEN" \
       -H 'Content-Type: application/json' \
       -d '{"upper_limit":"500.00","pay_out_enabled":false}'
   ```
   Должен вернуть HTTP 200 и обновленные данные магазина

## Тестирование платежного потока

### Создание платежа через шлюз

1. Убедитесь, что у вас есть `$API_KEY` и `$STORE_ID` из предыдущих шагов

2. Создайте платежную сессию:
   ```bash
   EXTERNAL_ORDER_ID="MY-SHOP-ORD-$(date +%s)-REDIRECT"
   INIT_RESPONSE=$(curl -s -X POST http://127.0.0.1:8003/gateway/payin/initiate_session \
       -H 'Content-Type: application/json' \
       -H "X-API-KEY: $API_KEY" \
       -d '{ 
             "order_type":"pay_in",
             "amount_fiat":"150.75",
             "fiat_currency_id":1, 
             "target_method_id":1, 
             "customer_id":"CUST-67890",
             "external_order_id": "'"$EXTERNAL_ORDER_ID"'",
             "return_url": "https://example.com/return_after_payment",
             "callback_url_for_merchant": "https://httpbin.org/post"
           }')
   echo $INIT_RESPONSE
   PAYMENT_URL=$(echo $INIT_RESPONSE | jq -r .payment_url)
   INCOMING_ORDER_ID_FROM_INIT=$(echo $INIT_RESPONSE | jq -r .incoming_order_id)
   echo "Payment URL: $PAYMENT_URL"
   echo "Incoming Order ID (from init): $INCOMING_ORDER_ID_FROM_INIT"
   ```
   Должен вернуть URL для оплаты и ID заказа

3. Проверьте создание заказа в базе:
   ```sql
   SELECT id, status, external_order_id, payment_page_url, payment_token, payment_token_expires_at 
   FROM incoming_orders WHERE external_order_id = '$EXTERNAL_ORDER_ID';
   ```
   Должна быть запись со статусом `new` или `pending_payment_page`

4. Откройте страницу оплаты:
   - Скопируйте `$PAYMENT_URL` в браузер
   - Проверьте, что отображается правильная сумма и валюта
   - Убедитесь, что есть поля для ввода данных или загрузки чека
   - Проверьте, что показано время жизни сессии

5. Протестируйте страницу оплаты:
   - Введите тестовые данные
   - Загрузите тестовый чек
   - Подтвердите платеж
   - Проверьте, что происходит редирект на `return_url`

6. Проверьте обработку платежа:
   - Посмотрите логи `gateway_api` на вызов подтверждения
   - Проверьте логи `worker` на запуск обработки заказа
   - Проверьте статус заказа в базе:
   ```sql
   SELECT id, incoming_order_id, external_order_id, status, receipt_file_s3_path 
   FROM order_history WHERE external_order_id = '$EXTERNAL_ORDER_ID';
   ```
   Запомните `id` как `{ORDER_HISTORY_ID_REDIRECT}`

7. Проверьте таймаут страницы (опционально):
   - Создайте новый платеж
   - Не открывайте страницу оплаты
   - Дождитесь истечения времени
   - Попробуйте открыть страницу
   - Должна быть ошибка о истекшей сессии

## Проверка Celery

1. Отправьте тестовую задачу:
   ```bash
   curl -X POST http://127.0.0.1:8004/admin/debug/celery/ping \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   ```

2. Проверьте логи воркера:
   ```bash
   docker compose logs worker
   ```
   Должно быть сообщение `pong`

## Тестирование подтверждения заказа

1. Трейдер подтверждает заказ:
   ```bash
   # Проверьте текущие балансы
   SELECT * FROM balance_stores WHERE store_id = $STORE_ID;
   SELECT * FROM balance_traders WHERE trader_id = {TRADER_ID};
   SELECT * FROM balance_store_history WHERE order_id = {ORDER_HISTORY_ID_REDIRECT};
   SELECT * FROM balance_trader_fiat_history WHERE order_id = {ORDER_HISTORY_ID_REDIRECT};
   ```

2. Проверьте баланс платформы:
   ```bash
   curl -s http://127.0.0.1:8004/admin/platform/balance \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   Должен вернуть текущие балансы

3. Проверьте историю прибыли:
   ```bash
   curl -s http://127.0.0.1:8004/admin/platform/balance/history?page=1&per_page=10 \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   Должен вернуть историю операций

## Тестирование коллбэков

1. Проверьте настройки коллбэка:
   ```sql
   SELECT callback_url FROM merchant_stores WHERE id = $STORE_ID;
   ```
   Должен быть указан URL (например, `https://httpbin.org/post`)

2. Повторите шаги подтверждения заказа

3. Проверьте, что на `httpbin.org` пришел POST запрос с данными:
   - `order_id`
   - `status`
   - `external_order_id`
   - `amount_fiat`
   - `currency_fiat`
   - `amount_crypto`
   - `currency_crypto`
   - `timestamp`
   - `signature`

## Тестирование ошибок

1. Попробуйте создать платеж без обязательного поля:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8003/gateway/payin/init \
       -H 'Content-Type: application/json' \
       -H "X-API-KEY: $API_KEY" \
       -d '{"order_type":"pay_in", "fiat_currency_id":1, "target_method_id":1, "customer_id":"CUST-42"}'
   ```
   Должен вернуть 422

2. Попробуйте превысить лимит магазина:
   - Установите низкий лимит через API мерчанта
   - Попробуйте создать платеж на большую сумму
   - Должна быть ошибка о превышении лимита

3. Проверьте ограничение запросов:
   - Сделайте 101 запрос подряд
   - Первые 100 должны пройти
   - 101-й должен быть отклонен

## Функционал администратора

### Управление пользователями

1. Получите списки пользователей:
   ```bash
   curl -X GET "http://127.0.0.1:8004/admin/administrators/stats?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
   curl -X GET "http://127.0.0.1:8004/admin/supports/stats?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
   curl -X GET "http://127.0.0.1:8004/admin/teamleads/stats?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   Должны вернуть списки пользователей

2. Получите детали пользователя:
   ```bash
   curl -X GET http://127.0.0.1:8004/admin/supports/{SUPPORT_ID} -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   Должен вернуть полную информацию о пользователе

3. Обновите профиль:
   ```bash
   curl -X PUT http://127.0.0.1:8004/admin/supports/{SUPPORT_ID} \
       -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
       -d '{"username": "UpdatedSupportUser", "role_description": "Tier 2 Specialist"}'
   ```
   Должен обновить данные пользователя

4. Обновите права:
   ```bash
   curl -X PUT http://127.0.0.1:8004/admin/supports/{SUPPORT_ID}/permissions \
       -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
       -d '{"granted_permissions": ["orders:view:any_list", "users:view:all"]}'
   ```
   Должен обновить права доступа

5. Заблокируйте/разблокируйте пользователя:
   ```bash
   # Блокировка
   curl -X POST http://127.0.0.1:8004/admin/supports/{SUPPORT_ID}/block -H "Authorization: Bearer $ADMIN_TOKEN"
   
   # Разблокировка
   curl -X POST http://127.0.0.1:8004/admin/supports/{SUPPORT_ID}/unblock -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   Проверьте, что пользователь не может/может войти

### Управление трейдерами и мерчантами

1. Получите списки:
   ```bash
   curl -X GET "http://127.0.0.1:8004/admin/traders/stats?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
   curl -X GET "http://127.0.0.1:8004/admin/merchants/stats?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   Должны вернуть списки пользователей

2. Получите детали трейдера:
   ```bash
   curl -X GET http://127.0.0.1:8004/admin/traders/{TRADER_ID} -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   Должен вернуть полную информацию о трейдере

3. Обновите профиль трейдера:
   ```bash
   curl -X PUT http://127.0.0.1:8004/admin/traders/{TRADER_ID} \
       -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
       -d '{"first_name": "John Updated", "trafic_priority": 3, "team_lead_id": {TEAMLEAD_ID}}'
   ```
   Должен обновить данные трейдера

### Управление заказами

1. Получите историю заказов:
   ```bash
   # Базовый запрос
   curl -X GET "http://127.0.0.1:8004/admin/orders/history?page=1&per_page=5" -H "Authorization: Bearer $ADMIN_TOKEN"
   
   # Поиск по ID заказа
   curl -X GET "http://127.0.0.1:8004/admin/orders/history?user_query=$EXTERNAL_ORDER_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
   
   # Сортировка по сумме
   curl -X GET "http://127.0.0.1:8004/admin/orders/history?sort_by=final_fiat_amount&sort_direction=asc" -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   Должны вернуть историю заказов

2. Получите количество заказов:
   ```bash
   curl -X GET "http://127.0.0.1:8004/admin/orders/count?status=completed" -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   Должен вернуть статистику

### Управление реквизитами

1. Трейдер добавляет реквизит:
   ```bash
   # Сначала создайте владельца реквизитов через админку
   curl -X POST http://127.0.0.1:8004/admin/requisites/owners ...
   ```
   Должен создать запись в базе

## Завершение
* Удостоверьтесь, что в логах нет непредвиденных ошибок `ERROR`/`CRITICAL`.
* Обновите `IMPLEMENTATION_TRACKER.md` — отметьте выполненные тесты.
