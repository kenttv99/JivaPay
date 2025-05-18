# План ручного тестирования JivaPay

Версия: v2025.05.13

## 0. Предусловия

1. Установлены инструменты: `docker`, `curl`, `psql` на хосте.
2. Переменные окружения в файле `.env` актуальны.
3. На хосте для Redis выставлен `vm.overcommit_memory = 1`, контейнер перезапущен.
4. Запустите все сервисы:
   ```bash
   docker compose up -d
   ```
5. Если база пуста или требуется переинициализация, используйте новый CLI `manage_db` для создания и сидирования базы:
   ```bash
   docker compose exec merchant_api python -m backend.scripts.manage_db init
   docker compose exec merchant_api python -m backend.scripts.manage_db seed-config
   docker compose exec merchant_api python -m backend.scripts.manage_db seed-data
   docker compose exec merchant_api python -m backend.scripts.manage_db seed-reference
   docker compose exec merchant_api python -m backend.scripts.manage_db seed-payment-refs
   # Права для основного администратора (admin@example.com) создаются в seed_data.py
   ```

## 1. Проверка состояния сервисов

1. Убедитесь, что все контейнеры `Up`:
   ```bash
   docker compose ps
   ```
2. Проверьте доступность PostgreSQL:
   ```bash
   docker compose exec postgres pg_isready
   # → accepting connections
   ```
3. Проверьте Redis:
   ```bash
   docker compose exec redis redis-cli PING
   # → PONG
   ```
4. Проверьте endpoint `/health` каждого API:
   ```bash
   curl -fsSL http://127.0.0.1:18001/health # Merchant API
   curl -fsSL http://127.0.0.1:8002/health  # Trader API
   curl -fsSL http://127.0.0.1:8003/health  # Gateway API
   curl -fsSL http://127.0.0.1:8004/health  # Admin API
   curl -fsSL http://127.0.0.1:8005/health  # Support API
   curl -fsSL http://127.0.0.1:8006/health  # TeamLead API
   ```
   - Ожидается `{"status":"ok"}` для каждого.
5. Проверьте воркер:
   ```bash
   docker compose logs worker --tail=50
   # в логах должна быть строка `ready.`
   ```

## 2. Аутентификация

### 2.1 Администратор

1. Получите токен администратора (используйте переменную `ADMIN_TOKEN` далее):
   ```bash
   ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8004/admin/auth/token \
        -d 'username=admin@example.com&password=adminpass' \
        -H 'Content-Type: application/x-www-form-urlencoded' | jq -r .access_token)
   echo $ADMIN_TOKEN
   ```
   - Ожидается JWT токен.
2. Попытка доступа к защищенному эндпоинту без токена:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8004/admin/platform/balance
   # → 401
   ```
3. Доступ с валидным токеном:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8004/admin/platform/balance \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   # → 200
   ```

### 2.2 Саппорт

1.  **Регистрация саппорта (через Админа):**
    ```bash
    # Замените {SUPPORT_EMAIL} и {SUPPORT_PASSWORD}
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
    # Ожидается HTTP 201 и JSON с данными саппорта. Запомните ID саппорта.
    # Пример ответа: {"id": <SUPPORT_ID>, "user_id": <USER_ID>, "username": "TestSupportUser1", ...}
    ```
2.  **Попытка входа с некорректными данными:**
    ```bash
    curl -s -o /dev/null -w "%{http_code}" \
      -X POST http://127.0.0.1:8005/support/auth/login \
      -H 'Content-Type: application/json' \
      -d '{"email":"nonexistent@example.com","password":"wrong"}'
    # → 401
    ```
3.  **Успешный вход саппорта (используйте переменную `SUPPORT_TOKEN` далее):**
    ```bash
    SUPPORT_TOKEN=$(curl -s -X POST http://127.0.0.1:8005/support/auth/login \
         -H 'Content-Type: application/json' \
         -d '{"email":"'"$SUPPORT_EMAIL"'","password":"'"$SUPPORT_PASSWORD"'"}' | jq -r .access_token)
    echo $SUPPORT_TOKEN
    ```
    - Ожидается JWT токен.

### 2.3 Тимлид

1.  **Регистрация тимлида (через Админа):**
    ```bash
    # Замените {TEAMLEAD_EMAIL} и {TEAMLEAD_PASSWORD}
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
    # Ожидается HTTP 201 и JSON с данными тимлида. Запомните ID тимлида.
    ```
2.  **Успешный вход тимлида (используйте переменную `TEAMLEAD_TOKEN` далее):**
    ```bash
    TEAMLEAD_TOKEN=$(curl -s -X POST http://127.0.0.1:8006/teamlead/auth/token \
         -d 'username='"$TEAMLEAD_EMAIL"'&password='"$TEAMLEAD_PASSWORD"'' \
         -H 'Content-Type: application/x-www-form-urlencoded' | jq -r .access_token)
    echo $TEAMLEAD_TOKEN
    ```
    - Ожидается JWT токен.

### 2.4 Мерчант

1.  **Регистрация мерчанта (через Админа):**
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
    # Ожидается HTTP 201 и JSON. Запомните ID мерчанта.
    ```
2.  **Успешный вход мерчанта (используйте переменную `MERCHANT_TOKEN` далее):**
    ```bash
    MERCHANT_TOKEN=$(curl -s -X POST http://127.0.0.1:18001/merchant/auth/token \
         -d 'username='"$MERCHANT_EMAIL"'&password='"$MERCHANT_PASSWORD"'' \
         -H 'Content-Type: application/x-www-form-urlencoded' | jq -r .access_token)
    echo $MERCHANT_TOKEN
    ```
    - Ожидается JWT токен.

### 2.5 Трейдер

1.  **Регистрация трейдера (через Админа):**
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
    # Ожидается HTTP 201 и JSON. Запомните ID трейдера - {TRADER_ID}.
    # Пример: {"id": 1, "user_id": 5, ...}
    # Привяжите трейдера к тимлиду (опционально, если тестируете полный флоу тимлида)
    # curl -X PUT http://127.0.0.1:8004/admin/traders/{TRADER_ID} ... -d '{"team_lead_id": {TEAMLEAD_ID}}'
    ```
2.  **Успешный вход трейдера (используйте переменную `TRADER_TOKEN` далее):**
    ```bash
    TRADER_TOKEN=$(curl -s -X POST http://127.0.0.1:8002/trader/auth/token \
         -d 'username='"$TRADER_EMAIL"'&password='"$TRADER_PASSWORD"'' \
         -H 'Content-Type: application/x-www-form-urlencoded' | jq -r .access_token)
    echo $TRADER_TOKEN
    ```
    - Ожидается JWT токен.

## 3. Тест Rate Limiter

1. Выполните 101 быстрый запрос к любому `/health` эндпоинту, например, мерчанта:
   ```bash
   for i in $(seq 1 101); do
     curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18001/health
   done
   ```
2. Первые 100 ответов должны быть `200`, 101-й — `429`.

## 4. Управление магазинами мерчанта

1.  **Создание магазина:**
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
    - Ожидается HTTP `201` и JSON с данными `MerchantStoreRead`, включая `public_api_key`.
2.  **Получение списка магазинов:**
    ```bash
    curl -X GET http://127.0.0.1:18001/merchant/stores \
        -H "Authorization: Bearer $MERCHANT_TOKEN"
    ```
    - Ожидается HTTP `200` и массив магазинов.
3.  **Получение деталей магазина по ID:**
    ```bash
    curl -X GET http://127.0.0.1:18001/merchant/stores/$STORE_ID \
        -H "Authorization: Bearer $MERCHANT_TOKEN"
    ```
    - Ожидается HTTP `200` и JSON с данными магазина.
4.  **Обновление настроек магазина:**
    ```bash
    curl -X PATCH http://127.0.0.1:18001/merchant/stores/$STORE_ID \
        -H "Authorization: Bearer $MERCHANT_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"upper_limit":"500.00","pay_out_enabled":false}'
    ```
    - Ожидается HTTP `200` и обновлённые данные магазина.
    
## 5. Поток Pay-In через Gateway (Редирект на страницу оплаты)

1.  Убедитесь, что `$API_KEY` (для аутентификации мерчанта в API шлюза) и `$STORE_ID` установлены из шага 4.1.
2.  **Инициация сессии платежа (Мерчант вызывает API шлюза):**
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
              "callback_url_for_merchant": "https://httpbin.org/post" # Это колбэк для мерчанта о финальном статусе
            }')
    echo $INIT_RESPONSE
    PAYMENT_URL=$(echo $INIT_RESPONSE | jq -r .payment_url)
    # Предполагается, что ответ также содержит ID созданного IncomingOrder или сессии, если нужен для дальнейшей сверки
    INCOMING_ORDER_ID_FROM_INIT=$(echo $INIT_RESPONSE | jq -r .incoming_order_id) # Пример, если возвращается
    echo "Payment URL: $PAYMENT_URL"
    echo "Incoming Order ID (from init): $INCOMING_ORDER_ID_FROM_INIT"
    ```
    - Ожидается JSON с `payment_url` (например, `https://pay.yourdomain.com/{unique_token}`) и, возможно, `incoming_order_id`.
    - `payment_url` должен быть уникальным и вести на страницу оплаты шлюза.
3.  **Проверка `IncomingOrder` (или `PaymentSession`) в БД:**
    Подключитесь к БД и проверьте, что для `external_order_id` создана запись в `incoming_orders` со статусом `new` (или `pending_payment_page`).
    Если используется отдельная таблица `payment_sessions`, проверьте её.
    Убедитесь, что уникальный токен, URL и время экспирации сохранены.
    ```sql
    -- Пример для incoming_orders, если поля добавлены туда:
    SELECT id, status, external_order_id, payment_page_url, payment_token, payment_token_expires_at 
    FROM incoming_orders WHERE external_order_id = '$EXTERNAL_ORDER_ID';
    ```
4.  **(Ручной шаг) Переход клиента на страницу оплаты:**
    Скопируйте `$PAYMENT_URL` и откройте его в браузере.
    - **Ожидания на странице оплаты:**
        - Отображается корректная сумма и валюта.
        - Присутствуют поля для ввода платежных данных и/или загрузки чека.
        - Указано время жизни сессии (если отображается).
5.  **(Ручной шаг) Взаимодействие со страницей оплаты:**
    Выполните действия на странице оплаты: введите данные, загрузите тестовый чек (например, `client_receipt_test.jpg` из Раздела 14 старого плана, переименуйте и используйте здесь), подтвердите платеж.
    - **Ожидания:**
        - Страница обрабатывает ввод и подтверждение.
        - После подтверждения клиент может быть перенаправлен на `return_url` мерчанта.
6.  **Проверка обработки подтверждения бэкендом:**
    - Проверьте логи `gateway_api` на предмет вызова эндпоинта подтверждения со страницы оплаты (например, `POST /gateway/payment_session/{token}/confirm`).
    - Проверьте логи `worker` на запуск `process_order_task` для этого `IncomingOrder` (если он еще не был обработан до статуса `assigned`). Статус `IncomingOrder` должен измениться на `assigned` или аналогичный, указывающий на подбор реквизита.
    - В `order_history` должна появиться запись для этого `external_order_id` со статусом `pending_trader_confirmation` (или `pending`, если чек загружен клиентом и сразу ожидает трейдера).
    ```sql
    SELECT id, incoming_order_id, external_order_id, status, receipt_file_s3_path 
    FROM order_history WHERE external_order_id = '$EXTERNAL_ORDER_ID';
    ```
    - Запомните `id` из `order_history` как `{ORDER_HISTORY_ID_REDIRECT}`.
7.  **Проверка таймаута страницы оплаты (Негативный сценарий, опционально):**
    - Инициируйте новый платеж (шаг 5.2), получите `PAYMENT_URL`.
    - Не взаимодействуйте со страницей, дождитесь истечения времени жизни токена/сессии.
    - Попытайтесь открыть `PAYMENT_URL` или выполнить на ней действия.
    - **Ожидание:** Страница должна показать ошибку о истекшей сессии, или быть недоступной. Соответствующий `IncomingOrder` может перейти в статус `expired` или `failed`.

## 6. Проверка Celery

1. Отправьте ping задачу:
   ```bash
   curl -X POST http://127.0.0.1:8004/admin/debug/celery/ping \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
2. В логах воркера (`docker compose logs worker`) найдите сообщение `pong`.

## 7. Happy-path: Подтверждение заказа и Балансы

1.  **Трейдер подтверждает заказ:** (Используйте `{ORDER_HISTORY_ID_REDIRECT}` из шага 5.6)
    ```bash
    # Создайте фейковый файл чека (если на шаге 5.5 чек загружал клиент, этот шаг может быть только подтверждением без файла)
    SELECT * FROM balance_stores WHERE store_id = $STORE_ID;
    SELECT * FROM balance_traders WHERE trader_id = {TRADER_ID}; -- TRADER_ID из логов или БД после назначения
    SELECT * FROM balance_store_history WHERE order_id = {ORDER_HISTORY_ID_REDIRECT};
    SELECT * FROM balance_trader_fiat_history WHERE order_id = {ORDER_HISTORY_ID_REDIRECT};
    ```
4.  **Проверка баланса платформы (Админ):**
    ```bash
    curl -s http://127.0.0.1:8004/admin/platform/balance \
         -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается HTTP 200 и JSON-массив PlatformBalanceResponseSchema
    ```
5.  **Проверка истории прибыли платформы (Админ):**
    ```bash
    curl -s http://127.0.0.1:8004/admin/platform/balance/history?page=1&per_page=10 \
         -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается HTTP 200 и JSON-массив с пагинацией (стандартный ответ от query_utils)
    ```

## 8. Callback Service

1.  Убедитесь, что `callback_url` в `merchant_stores` для вашего `$STORE_ID` указан (например, `https://httpbin.org/post`).
2.  Повторите шаги из Раздела 7 (Подтверждение заказа трейдером для ордера, созданного через редирект).
3.  Проверьте сервис коллбэков (например, `https://httpbin.org/post`) – должен прийти POST запрос с данными о финальном статусе заказа (`completed` или `failed`).
4.  **Проверка payload колбэка:** Убедитесь, что payload колбэка на `httpbin.org` содержит ожидаемые поля, такие как `order_id`, `status`, `external_order_id`, `amount_fiat`, `currency_fiat`, `amount_crypto`, `currency_crypto`, `timestamp`, `signature`.

## 9. Негативные сценарии

1.  **Pay-In без обязательного поля (например, `amount_fiat`):**
    ```bash
    curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8003/gateway/payin/init \
        -H 'Content-Type: application/json' \
        -H "X-API-KEY: $API_KEY" \
        -d '{"order_type":"pay_in", "fiat_currency_id":1, "target_method_id":1, "customer_id":"CUST-42"}'
    # → 422
    ```
2.  **Pay-In с суммой выше лимита магазина (если настроен низкий лимит для теста):**
    Измените `upper_limit` магазина на низкое значение (например, 50) через API мерчанта (Раздел 4.4).
    ```bash
    curl -s -X POST http://127.0.0.1:8003/gateway/payin/init \
        -H 'Content-Type: application/json' \
        -H "X-API-KEY: $API_KEY" \
        -d '{"order_type":"pay_in", "amount_fiat":"999.00", "fiat_currency_id":1, "target_method_id":1, "customer_id":"CUST-43"}'
    # → Ожидается ошибка, связанная с лимитом (может быть 400 от requisite_selector или другая, зависит от логики).
    #   В логах order_processor должен быть RequisiteNotFound или LimitExceeded.
    ```
3.  Повтор теста Rate Limiter — см. Раздел 3.

## 10. Функционал Администратора

### 10.1 Управление пользователями (Админы, Саппорты, Тимлиды)
   (Регистрация показана в Разделе 2. Используйте полученные ID для тестов ниже)

1.  **Получение списка пользователей:**
    ```bash
    curl -X GET "http://127.0.0.1:8004/admin/administrators/stats?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
    curl -X GET "http://127.0.0.1:8004/admin/supports/stats?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
    curl -X GET "http://127.0.0.1:8004/admin/teamleads/stats?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается 200 и пагинированный список пользователей
    ```
2.  **Получение деталей пользователя (пример для саппорта {SUPPORT_ID}):**
    ```bash
    curl -X GET http://127.0.0.1:8004/admin/supports/{SUPPORT_ID} -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается 200 и детали саппорта (SupportDetailsSchema)
    ```
3.  **Обновление профиля пользователя (пример для саппорта {SUPPORT_ID}):**
    ```bash
    curl -X PUT http://127.0.0.1:8004/admin/supports/{SUPPORT_ID} \
        -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
        -d '{"username": "UpdatedSupportUser", "role_description": "Tier 2 Specialist"}'
    # Ожидается 200 и обновленные данные
    ```
4.  **Обновление прав пользователя (пример для саппорта {SUPPORT_ID}):**
    ```bash
    curl -X PUT http://127.0.0.1:8004/admin/supports/{SUPPORT_ID}/permissions \
        -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
        -d '{"granted_permissions": ["orders:view:any_list", "users:view:all"]}'
    # Ожидается 200 и UserPermissionsSchema
    ```
5.  **Блокировка/Разблокировка пользователя (пример для саппорта {SUPPORT_ID}):**
    ```bash
    curl -X POST http://127.0.0.1:8004/admin/supports/{SUPPORT_ID}/block -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается 200. Проверить, что пользователь не может войти.
    curl -X POST http://127.0.0.1:8004/admin/supports/{SUPPORT_ID}/unblock -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается 200. Проверить, что пользователь может войти.
    ```

### 10.2 Управление Трейдерами и Мерчантами (Администратором)
   (Регистрация трейдера и мерчанта в Разделе 2. Используйте {TRADER_ID}, {MERCHANT_ID})
1.  **Получение списков:**
    ```bash
    curl -X GET "http://127.0.0.1:8004/admin/traders/stats?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
    curl -X GET "http://127.0.0.1:8004/admin/merchants/stats?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается 200 и пагинированный список
    ```
2.  **Получение деталей трейдера:**
    ```bash
    curl -X GET http://127.0.0.1:8004/admin/traders/{TRADER_ID} -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается 200 и детали трейдера (TraderDetailsFullSchema)
    ```
3.  **Обновление профиля трейдера:**
    ```bash
    curl -X PUT http://127.0.0.1:8004/admin/traders/{TRADER_ID} \
        -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
        -d '{"first_name": "John Updated", "trafic_priority": 3, "team_lead_id": {TEAMLEAD_ID} }' # TEAMLEAD_ID если есть
    # Ожидается 200
    ```
    (Аналогично для мерчантов: `PUT /admin/merchants/{MERCHANT_ID}`)

### 10.3 Управление Заказами (Администратором)
1.  **Получение истории заказов:**
    ```bash
    # Базовый запрос
    curl -X GET "http://127.0.0.1:8004/admin/orders/history?page=1&per_page=5" -H "Authorization: Bearer $ADMIN_TOKEN"
    # С фильтром по external_order_id (используйте ID из шага 5.2)
    curl -X GET "http://127.0.0.1:8004/admin/orders/history?user_query=$EXTERNAL_ORDER_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
    # Сортировка по final_fiat_amount_at_deal
    curl -X GET "http://127.0.0.1:8004/admin/orders/history?sort_by=final_fiat_amount&sort_direction=asc" -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается 200 и OrderHistoryAdminResponseSchema (содержит external_order_id, final_fiat_amount_at_deal)
    ```
2.  **Получение количества заказов:**
    ```bash
    curl -X GET "http://127.0.0.1:8004/admin/orders/count?status=completed" -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается 200 и OrderCountResponseSchema
    ```

### 10.4 Управление Реквизитами (Администратором)
1.  **Трейдер добавляет реквизит (для последующей модерации администратором):**
    ```bash
    # Пример: first get/create owner_of_requisites via admin API if not exists
    # curl -X POST http://127.0.0.1:8004/admin/requisites/owners ...
    # OWNER_ID=1 # предположим, что владелец с ID=1 существует
    # METHOD_ID=1 # из payment_methods
    # BANK_ID=1 # из banks
    # FIAT_ID=1 # из fiat_currencies
    REQ_NUMBER="CARD-ADMIN-TEST-$(date +%s)"
    curl -X POST http://127.0.0.1:8002/trader/requisites \
        -H "Authorization: Bearer $TRADER_TOKEN" -H 'Content-Type: application/json' \
        -d '{
            "fiat_id":1, 
            "owner_of_requisites_id":1, 
            "method_id":1, 
            "bank_id":1, 
            "req_number":"'"$REQ_NUMBER"'",
            "full_settings": {
                "pay_in":true, "pay_out":true, "lower_limit":"100", "upper_limit":"10000", 
                "total_limit":"50000", "turnover_limit_minutes":60, "turnover_day_max":"200000"
            }
        }'
    # Ожидается 201, запомните REQUISITE_ID
    ```
2.  **Получение онлайн статистики реквизитов (Админ):**
    ```bash
    curl -X GET "http://127.0.0.1:8004/admin/requisites/online-stats?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается 200 и RequisiteOnlineStatsResponseSchema
    # Убедитесь, что ответ содержит поля `payment_method_name` и `bank_name` для каждого реквизита.
    # Также протестировать SSE эндпоинт: GET /admin/requisites/online-stats/stream
    ```
3.  **Модерация реквизита (Админ, используйте REQUISITE_ID):**
    ```bash
    # Получить детали для модерации
    curl -X GET http://127.0.0.1:8004/admin/requisites/{REQUISITE_ID}/moderate -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается 200
    # Изменить статус
    curl -X PUT http://127.0.0.1:8004/admin/requisites/{REQUISITE_ID}/status \
        -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
        -d '{"status": "rejected", "moderation_comment": "Test rejection by admin"}'
    # Ожидается 200 и обновленный реквизит
    ```

### 10.5 Системные Функции (Администратором)
1.  **Логи критических ошибок:**
    ```bash
    curl -X GET "http://127.0.0.1:8004/admin/logs/critical-errors?page=1&per_page=10" -H "Authorization: Bearer $ADMIN_TOKEN"
    # Ожидается 200
    # Дополнительно: если API позволяет, протестируйте фильтрацию критических ошибок по уровню (например, `?level=CRITICAL`).
    ```

## 11. Функционал Саппорта
   (Используйте `$SUPPORT_TOKEN`. Тестируйте с разными наборами `granted_permissions` у саппорта)

1.  **Просмотр истории заказов (с учетом прав):**
    ```bash
    curl -X GET "http://127.0.0.1:8005/support/orders/history?page=1&per_page=5&status=pending" \
        -H "Authorization: Bearer $SUPPORT_TOKEN"
    # Ожидается 200 и OrderHistoryAdminResponseSchema.
    # Проверить, что external_order_id и final_fiat_amount_at_deal видны (если есть права).
    # Проверить, что фильтрация по статусам работает согласно правам.
    ```
2.  **Просмотр статистики онлайн реквизитов (с учетом прав):**
    ```bash
    curl -X GET "http://127.0.0.1:8005/support/requisites/online-stats?page=1&per_page=10" \
        -H "Authorization: Bearer $SUPPORT_TOKEN"
    # Ожидается 200. Также протестировать SSE: /support/requisites/online-stats/stream
    ```
3.  **Просмотр статистики трейдеров (с учетом прав):**
    ```bash
    curl -X GET "http://127.0.0.1:8005/support/traders/stats?page=1&per_page=10" \
        -H "Authorization: Bearer $SUPPORT_TOKEN"
    # Ожидается 200
    ```
4.  **Поиск трейдеров/мерчантов (если есть права):**
    ```bash
    curl -X GET "http://127.0.0.1:8005/support/traders/search?query=trader_test1" -H "Authorization: Bearer $SUPPORT_TOKEN"
    curl -X GET "http://127.0.0.1:8005/support/merchants/search?query=merchant_test1" -H "Authorization: Bearer $SUPPORT_TOKEN"
    # Ожидается 200
    ```
5.  **Просмотр деталей (если есть права, используйте ID):**
    ```bash
    curl -X GET http://127.0.0.1:8005/support/orders/{ORDER_HISTORY_ID} -H "Authorization: Bearer $SUPPORT_TOKEN"
    curl -X GET http://127.0.0.1:8005/support/traders/{TRADER_ID} -H "Authorization: Bearer $SUPPORT_TOKEN"
    # Ожидается 200, объем данных зависит от прав.
    ```

## 12. Функционал Тимлида
   (Используйте `$TEAMLEAD_TOKEN` и `{TRADER_ID}` трейдера, привязанного к этому тимлиду)

1.  **Статистика онлайн реквизитов команды:**
    ```bash
    curl -X GET "http://127.0.0.1:8006/teamlead/requisites/online-stats?page=1&per_page=10" \
        -H "Authorization: Bearer $TEAMLEAD_TOKEN"
    # Ожидается 200. Также SSE: /teamlead/requisites/online-stats/stream
    ```
2.  **Общая статистика команды:**
    ```bash
    curl -X GET http://127.0.0.1:8006/teamlead/team/statistics \
        -H "Authorization: Bearer $TEAMLEAD_TOKEN"
    # Ожидается 200 и TeamStatisticsSchema
    ```
3.  **Список управляемых трейдеров:**
    ```bash
    curl -X GET "http://127.0.0.1:8006/teamlead/managed-traders?page=1&per_page=10" \
        -H "Authorization: Bearer $TEAMLEAD_TOKEN"
    # Ожидается 200 и список TeamLeadTraderBasicInfoSchema
    ```
4.  **Переключение трафика трейдера (используйте {TRADER_ID} из команды тимлида):**
    ```bash
    # Выключить трафик
    curl -X PUT http://127.0.0.1:8006/teamlead/managed-traders/{TRADER_ID}/toggle-traffic \
        -H "Authorization: Bearer $TEAMLEAD_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"enable": false}'
    # Ожидается HTTP 200 и TraderTrafficStatusResponse с is_traffic_enabled_by_teamlead: false
    # Проверить в БД Trader.is_traffic_enabled_by_teamlead

    # Включить трафик
    curl -X PUT http://127.0.0.1:8006/teamlead/managed-traders/{TRADER_ID}/toggle-traffic \
        -H "Authorization: Bearer $TEAMLEAD_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"enable": true}'
    # Ожидается HTTP 200 и TraderTrafficStatusResponse с is_traffic_enabled_by_teamlead: true
    ```

## 13. Управление настройками (Settings) администратора (без изменений)

1. Создайте новую настройку:
   ```bash
   curl -X POST http://127.0.0.1:8004/admin/settings \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"key":"NEW_SETTING","value":"100","description":"Test setting"}'
   ```
   - Ожидается HTTP `201` и JSON.
2. Получите настройку:
   ```bash
   curl -X GET http://127.0.0.1:8004/admin/settings/NEW_SETTING \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   - Ожидается HTTP `200`.
3. Обновите настройку:
   ```bash
   curl -X PATCH http://127.0.0.1:8004/admin/settings/NEW_SETTING \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"value":"200"}'
   ```
   - Ожидается HTTP `200`.
4. Удалите настройку:
   ```bash
   curl -X DELETE http://127.0.0.1:8004/admin/settings/NEW_SETTING \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   - Ожидается HTTP `204`.

## 14. Клиентское подтверждение Pay-In через Gateway (чек от клиента)

-- Старый раздел 14 удален, так как логика клиентского подтверждения теперь является частью Раздела 5 (Поток Pay-In через Gateway (Редирект на страницу оплаты)) --

## 15. Завершение
* Удостоверьтесь, что в логах нет непредвиденных ошибок `ERROR`/`CRITICAL`.
* Обновите `IMPLEMENTATION_TRACKER.md` — отметьте выполненные тесты.
