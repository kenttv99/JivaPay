# ПЛАН РУЧНОГО ТЕСТИРОВАНИЯ JivaPay

Версия документа: v2025.05.10

## 0. Предусловия
1. Все контейнеры запущены командой `docker compose up -d`.  
2. На сервере доступны `curl`, `docker`, `psql` и `redis-cli` (в контейнере).
3. В `.env` применены актуальные конфиги.
4. Конфигурация Redis `vm.overcommit_memory=1` установлена **на хосте** и контейнер `redis` перезапущен.
5. **Первичное заполнение БД (только при пустой базе):**  
   ```bash
   # Конфиг и роли
   docker compose exec merchant_api python -m backend.scripts.seed_config
   docker compose exec merchant_api python -m backend.scripts.seed_data
   ```  
   Скрипты создадут дефолтного администратора `admin@example.com / admin123` и системные справочники.

## 1. Проверка состояния сервисов
| Сервис | Команда | Ожидаемый результат |
| ------ | ------- | ------------------- |
| Docker-контейнеры | `docker compose ps` | Все контейнеры в состоянии `Up` |
| Postgres | `docker compose exec postgres pg_isready` | `accepting connections` |
| Redis | `docker compose exec redis redis-cli PING` | `PONG` |
| Backend APIs | `curl -fsSL http://127.0.0.1:<PORT>/health` (merchant 18001, trader 8002, gateway 8003, admin 8004, support 8005, teamlead 8006) | `{"status":"ok"}` |
| Worker | в логах сервиса `worker` строка `ready.` | Есть |

## 2. Проверка базовой аутентификации администратора
1. Получить токен администратора (seed-данные):
   ```bash
   curl -X POST http://127.0.0.1:8004/admin/auth/token \
        -d 'username=admin@example.com&password=admin123' \
        -H 'Content-Type: application/x-www-form-urlencoded'
   # → JSON с `access_token`
   ```
2. Попытка запроса защищённого ресурса без токена → 401.
3. Повтор с заголовком `Authorization: Bearer <TOKEN>` → 200.

## 3. Тест лимитов Rate-Limiter
> После применения миграции с записью `RATE_LIMIT_DEFAULT` = `100-m`.

```bash
# 101 быстрый запрос в цикле
for i in $(seq 1 101); do curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18001/health; done
```
Ожидаем: первые 100 → 200, 101-й → 429.

## 4. Создание мерчанта и заказа
```bash
TOKEN=<ADMIN_TOKEN>
# 4.1 Мерчант
curl -X POST http://127.0.0.1:8004/admin/register/merchant \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"email":"merchant1@example.com","password":"m123","company_name":"Shop Ltd"}'
# 4.2 Логин мерчанта → получить MERCHANT_TOKEN
# 4.3 Создать заказ (Pay-In) – пока store-эндпоинт не реализован
curl -X POST http://127.0.0.1:18001/merchant/orders \
     -H "Authorization: Bearer $MERCHANT_TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"direction":"PAYIN","amount_fiat":100.50,"fiat_currency_id":1,"crypto_currency_id":1,"customer_id":"CUST-42"}'
```
Ожидаем HTTP 201 и запись в таблице `incoming_orders` со статусом `new`.

## 5. Пай-ин поток (Gateway)
```bash
API_KEY=<PUBLIC_API_KEY_STORE>
# Init pay-in
curl -X POST http://127.0.0.1:8003/gateway/payin/init \
     -H 'Content-Type: application/json' \
     -H "X-API-KEY: $API_KEY" \
     -d '{"amount":100.50,"customer_id":"CUST-42"}'
```
Ответ: `invoice_id`, `payment_details`.

1. Проверить, что в БД создан `incoming_orders` со статусом `new`.
2. В логах worker появилось задание `process_order_task` → статус `assigned`.

## 6. Проверка Celery
```bash
# Отправить ping-задачу
curl -X POST http://127.0.0.1:8004/admin/debug/celery/ping
# Логи worker: task succeeded → "pong"
```

## 7. Баланс-менеджер (happy-path)
После подтверждения трейдером:
1. `order_status_manager` меняет статус на `completed`.
2. Проверить изменения в таблицах `balance_store`, `balance_trader`, истории.

## 8. Callback-service
Проверить, что HTTP POST отправлен на `callback_url` мерчанта (можно задать httpbin URL и смотреть логи).

## 9. Негативные сценарии
| Тест | Ожидаемый результат |
| ---- | ------------------- |
| Отправить Pay-in без `amount` | 422 Unprocessable Entity |
| Завысить `amount` > `upper_limit` магазина | 400 + `LimitExceeded` |
| Превышение лимитов Rate-Limiter | 429 |

## 10. Завершение
* Удостоверьтесь, что в логах нет ошибок `ERROR`/`WARNING` кроме известных benign-messages.
* Обновите `IMPLEMENTATION_TRACKER.md` — отметьте выполненные тесты в разделе 8 «Тестирование».  

## 7. Управление трейдерами Тимлидом
### 7.1 Логин Тимлида
```bash
curl -X POST http://127.0.0.1:8006/teamlead/auth/token \
     -d 'username=lead1@example.com&password=lead123' \
     -H 'Content-Type: application/x-www-form-urlencoded'
# → JSON с `access_token` (TEAMLEAD_TOKEN)
```
### 7.2 Переключить трафик трейдера
```bash
TRADER_ID=<ID_Трейдера>
curl -X PATCH http://127.0.0.1:8006/teamlead/traders/$TRADER_ID/traffic \
     -H "Authorization: Bearer $TEAMLEAD_TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"in_work": false}'
```
Ожидаем: 200 и `{"trader_id": TRADER_ID, "in_work": false}`. Повтор с `true` включает трафик обратно.

---
**Важно:** Перед каждым блоком тестов очищайте логи (`docker compose logs -f --tail=0`) и/или метрики, чтобы проще отслеживать результат. 