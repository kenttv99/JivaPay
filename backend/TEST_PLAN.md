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
   curl -fsSL http://127.0.0.1:<PORT>/health
   ```
   - PORT: 8001 (merchant), 8002 (trader), 8003 (gateway), 8004 (admin), 8005 (support), 8006 (teamlead).
   - Ожидается `{"status":"ok"}`.
5. Проверьте воркер:
   ```bash
   docker compose logs worker --tail=50
   # в логах должна быть строка `ready.`
   ```

## 2. Аутентификация администратора

1. Получите токен администратора:
   ```bash
   curl -X POST http://127.0.0.1:8004/admin/auth/token \
        -d 'username=admin@example.com&password=adminpass' \
        -H 'Content-Type: application/x-www-form-urlencoded'
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsImV4cCI6MTc0NzA4MzE1Mn0.19fWASh5gCCsguanstKJYfpo7aSXxKSSH_09tXqLOkg
   ```
   - Ожидается JSON: `{"access_token":"...","token_type":"bearer"}`.
2. Попытка доступа без токена:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8004/admin/users
   # → 401
   ```
3. Доступ с токеном:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8004/admin/users \
        -H "Authorization: Bearer <TOKEN>"
   # → 200
   ```

## 3. Аутентификация саппорта

1. Попытка входа с некорректными данными:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" \
     -X POST http://127.0.0.1:8005/support/auth/login \
     -H 'Content-Type: application/json' \
     -d '{"email":"nonexistent@example.com","password":"wrong"}'
   # → 401
   ```
2. Создайте саппорта через админа (если еще не создан):
   ```bash
   curl -X POST http://127.0.0.1:8004/admin/register/support \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"email":"support1@example.com","password":"string111","access_to":["orders","users"]}'
   # → 201
   ```
3. Успешный вход саппорта:
   ```bash
   curl -X POST http://127.0.0.1:8005/support/auth/login \
        -H 'Content-Type: application/json' \
        -d '{"email":"support1@example.com","password":"string111"}'
   ```
   - Ожидается JSON: `{"id":<ID>,"email":"support1@example.com"}`.

## 4. Тест Rate Limiter

1. Выполните 101 быстрый запрос к `/health`:
   ```bash
   for i in $(seq 1 101); do
     curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18001/health
   done
   ```
2. Первые 100 ответов должны быть `200`, 101-й — `429`.

## 5. Создание мерчанта и заказов

1. Создайте мерчанта (используйте `$ADMIN_TOKEN`):
   ```bash
   curl -X POST http://127.0.0.1:8004/admin/register/merchant \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"email":"merchant1@example.com","password":"merchant111","company_name":"Shop Ltd"}'
   ```
   - Ожидается HTTP `201` и JSON с данными мерчанта.
2. Получите токен мерчанта:
   ```bash
   curl -X POST http://127.0.0.1:18001/merchant/auth/token \
        -d 'username=merchant1@example.com&password=merchant111' \
        -H 'Content-Type: application/x-www-form-urlencoded'
   ```
   - Ожидается JSON с `access_token`.
3. Создайте трейдера (используйте `$ADMIN_TOKEN`):
   ```bash
   curl -X POST http://127.0.0.1:8004/admin/register/trader \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"email":"trader1@example.com","password":"trader123","first_name":"John","last_name":"Doe"}'
   ```
   - Ожидается HTTP `201` и JSON с полями `id` и `email`.
4. Управление магазинами мерчанта:
   a) Создайте магазин:
   ```bash
   curl -X POST http://127.0.0.1:18001/merchant/stores \
        -H "Authorization: Bearer $MERCHANT_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"store_name":"Shop A","crypto_currency_id":1,"fiat_currency_id":1,"lower_limit":0,"upper_limit":10000,"pay_in_enabled":true,"pay_out_enabled":true}'
   ```
   - Ожидается HTTP `201` и JSON с данными `MerchantStoreRead`, включая поле `public_api_key`.
   b) Получите список магазинов:
   ```bash
   curl -X GET http://127.0.0.1:18001/merchant/stores \
        -H "Authorization: Bearer $MERCHANT_TOKEN"
   ```
   - Ожидается HTTP `200` и массив магазинов.
   c) Получите детали магазина по ID:
   ```bash
   curl -X GET http://127.0.0.1:18001/merchant/stores/{store_id} \
        -H "Authorization: Bearer $MERCHANT_TOKEN"
   ```
   - Ожидается HTTP `200` и JSON с данными магазина.
   d) Обновите настройки магазина:
   ```bash
   curl -X PATCH http://127.0.0.1:18001/merchant/stores/{store_id} \
        -H "Authorization: Bearer $MERCHANT_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"upper_limit":5000,"pay_out_enabled":false}'
   ```
   - Ожидается HTTP `200` и обновлённые данные магазина.
   e) Удалите магазин:
   ```bash
   curl -X DELETE http://127.0.0.1:18001/merchant/stores/{store_id} \
        -H "Authorization: Bearer $MERCHANT_TOKEN"
   ```
   - Ожидается HTTP `204`.

## 6. Поток Pay-In через Gateway

1. Возьмите `API_KEY` вашего магазина из таблицы `merchant_store`.
2. Инициируйте платёж:
   ```bash
   curl -X POST http://127.0.0.1:8003/gateway/payin/init \
        -H 'Content-Type: application/json' \
        -H "X-API-KEY: $API_KEY" \
        -d '{"amount":100.50,"customer_id":"CUST-42"}'
   ```
   - Ожидается JSON с `invoice_id` и деталями платежа.
3. Удостоверьтесь, что в `incoming_orders` появился заказ со статусом `new`.
4. Проверьте логи воркера: должна быть запись о запуске `process_order_task`, статус заказа — `assigned`.

## 7. Проверка Celery

1. Отправьте ping задачу:
   ```bash
   curl -X POST http://127.0.0.1:8004/admin/debug/celery/ping \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
2. В логах воркера найдите сообщение `pong`.

## 8. Happy-path баланс-менеджера

1. Подтвердите платёж трейдером:
   ```bash
   curl -X PATCH http://127.0.0.1:8002/trader/orders/<ORDER_ID>/confirm \
        -H "Authorization: Bearer $TRADER_TOKEN" \
        -F file=@receipt.png
   ```
2. Статус заказа должен стать `completed`.
3. Проверьте таблицы `balance_store`, `balance_trader` и истории (`*_history`).
4. Проверьте баланс платформы через API администратора:
   ```bash
   curl -s http://127.0.0.1:8004/admin/platform/balance \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   - Ожидается HTTP `200` и JSON-массив с объектами:
       * `currency_code`: строка-код валюты.
       * `balance`: числовое значение текущего баланса.
5. Проверьте историю прибыли платформы через API администратора:
   ```bash
   curl -s http://127.0.0.1:8004/admin/platform/balance/history \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   - Ожидается HTTP `200` и JSON-массив с объектами:
       * `id`: идентификатор записи.
       * `order_id`: идентификатор заказа.
       * `currency_code`: строка-код валюты.
       * `balance_change`: изменение баланса по данной операции.
       * `new_balance`: новое значение баланса после операции.
       * `created_at`: метка времени создания записи.

## 9. Callback Service

1. В настройках магазина (`merchant_store.callback_url`) укажите `https://httpbin.org/post`.
2. Повторите подтверждение заказа (как в Разделе 7).
3. Убедитесь, что HTTP POST с данными отправлен на httpbin (проверка логов httpbin).

## 10. Негативные сценарии

1. Pay-In без обязательного поля `amount`:
   ```bash
   curl -X POST http://127.0.0.1:8003/gateway/payin/init \
        -H 'Content-Type: application/json' \
        -H "X-API-KEY: $API_KEY" \
        -d '{"customer_id":"CUST-42"}'
   ```
   - Ожидается HTTP `422`.
2. Pay-In с суммой выше лимита:
   ```bash
   curl -X POST http://127.0.0.1:8003/gateway/payin/init \
        -H 'Content-Type: application/json' \
        -H "X-API-KEY: $API_KEY" \
        -d '{"amount":999999,"customer_id":"CUST-42"}'
   ```
   - Ожидается HTTP `400` и ошибка `LimitExceeded`.
3. Повтор теста Rate Limiter — см. Раздел 4.

## 11. Управление трейдерами Тимлидом

1. Получите токен тимлида:
   ```bash
   curl -X POST http://127.0.0.1:8006/teamlead/auth/token \
        -d 'username=lead1@example.com&password=lead123' \
        -H 'Content-Type: application/x-www-form-urlencoded'
   ```
2. Переключите трафик трейдера:
   ```bash
   curl -X PATCH http://127.0.0.1:8006/teamlead/traders/$TRADER_ID/traffic \
        -H "Authorization: Bearer $TEAMLEAD_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"in_work":false}'
   ```
   - Ожидается HTTP `200` и `{"trader_id": <ID>, "in_work": false}`.
3. Повторите с `{"in_work":true}` — трафик должен восстановиться.

## 12. Завершение
* Удостоверьтесь, что в логах нет ошибок `ERROR`/`WARNING` кроме известных benign-messages.
* Обновите `IMPLEMENTATION_TRACKER.md` — отметьте выполненные тесты в разделе 8 «Тестирование».

## 13. Управление настройками (Settings) администратора

1. Создайте новую настройку:
   ```bash
   curl -X POST http://127.0.0.1:8004/admin/settings \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"key":"NEW_SETTING","value":"100","description":"Test setting"}'
   ```
   - Ожидается HTTP `201` и JSON с полями `key`, `value`, `description`, `created_at`, `updated_at`.

2. Получите настройку:
   ```bash
   curl -X GET http://127.0.0.1:8004/admin/settings/NEW_SETTING \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   - Ожидается HTTP `200` и JSON с данными настройки.

3. Обновите настройку:
   ```bash
   curl -X PATCH http://127.0.0.1:8004/admin/settings/NEW_SETTING \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H 'Content-Type: application/json' \
        -d '{"value":"200"}'
   ```
   - Ожидается HTTP `200` и JSON с обновлённым полем `value`.

4. Удалите настройку:
   ```bash
   curl -X DELETE http://127.0.0.1:8004/admin/settings/NEW_SETTING \
        -H "Authorization: Bearer $ADMIN_TOKEN"
   ```
   - Ожидается HTTP `204`.

## 14. Управление правами администратора

1. Получите список прав админов:
   ```bash