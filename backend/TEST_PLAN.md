# ПЛАН РУЧНОГО ТЕСТИРОВАНИЯ JivaPay

Версия документа: v2025.05.10

## 0. Предусловия
1. Все контейнеры запущены командой `docker compose up -d`.  
2. На сервере доступны `curl`, `docker`, `psql` и `redis-cli` (в контейнере).
3. В `.env` и Alembic-миграциях применены актуальные конфиги.
4. Конфигурация Redis `vm.overcommit_memory=1` установлена **на хосте** и контейнер `redis` перезапущен.

## 1. Проверка состояниЯ сервисов
| Сервис | Команда | Ожидаемый результат |
| ------ | ------- | ------------------- |
| Docker-контейнеры | `docker compose ps` | Все контейнеры в состоянии `Up` |
| Postgres | `docker compose exec postgres pg_isready` | `accepting connections` |
| Redis | `docker compose exec redis redis-cli PING` | `PONG` |
| Backend APIs | `curl -fsSL http://127.0.0.1:<PORT>/health` (merchant 18001, trader 8002, gateway 8003, admin 8004, support 8005) | `{"status":"ok"}` |
| Worker | в логах сервиса `worker` строка `ready.` | Есть |

## 2. Проверка базовой аутентификации
1. Получить токен администратора (seed-данные):
   ```bash
   curl -X POST http://127.0.0.1:8004/api/admin/auth/token \
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

## 4. Создание мерчанта и магазина
```bash
TOKEN=<ADMIN_TOKEN>
# 4.1 Мерчант
curl -X POST http://127.0.0.1:8004/admin/register/merchant \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"email":"merchant1@example.com","password":"m123","company_name":"Shop Ltd"}'
# 4.2 Логин мерчанта → получить MERCHANT_TOKEN
# 4.3 Создать магазин
curl -X POST http://127.0.0.1:18001/api/merchant/stores \
     -H "Authorization: Bearer $MERCHANT_TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"store_name":"Main Store","crypto_currency_id":1,"fiat_currency_id":1}'
```
Ожидаем HTTP 201 и запись в таблице `merchant_stores`.

## 5. Пай-ин поток (Gateway)
```bash
API_KEY=<PUBLIC_API_KEY_STORE>
# Init pay-in
curl -X POST http://127.0.0.1:8003/payin/init \
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
curl -X POST http://127.0.0.1:8004/debug/celery/ping
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

---
**Важно:** Перед каждым блоком тестов очищайте логи (`docker compose logs -f --tail=0`) и/или метрики, чтобы проще отслеживать результат. 