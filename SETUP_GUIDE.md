# JivaPay – Пошаговый Гайд Развёртывания

Версия: v2025-05-10

Этот документ описывает минимально-полный сценарий установки и запуска JivaPay на чистом сервере (Ubuntu 22.04 LTS). Актуально как для staging, так и для production (с незначительными доработками).

---
## 1. Системные Требования
| Компонент | Мин. версия | Проверить / Установить |
|-----------|-------------|-------------------------|
| ОС        | Ubuntu 20.04+ / Debian 11+ / любой Linux с systemd | `cat /etc/os-release` |
| CPU/RAM   | 2 vCPU / 4 ГБ (dev)  •  4 vCPU / 8 ГБ (prod) | `lscpu`, `free -h` |
| Docker    | 24.x        | `docker –version` / <https://docs.docker.com/engine/install/> |
| Docker Compose | v2 (stand-alone CLI) | `docker compose version` |
| Git       | 2.x         | `git –version` |
| OpenSSL   | 1.1+        | (для HTTPS, если Nginx) |

> Примечание: Python локально **не нужен** – все сервисы запускаются в контейнерах. Для ручового запуска сид-скриптов можно использовать Python 3.10+ в venv.

---
## 2. Клонирование репозитория
```bash
git clone https://github.com/your-org/jivapay.git
cd jivapay
```

---
## 3. Конфигурация окружения
1. Скопируйте шаблон переменных:
   ```bash
   cp sample.env .env
   ```
2. Откройте `.env` и проверьте/измените ключевые параметры:
   * `POSTGRES_PASSWORD` – надёжный пароль
   * `SECRET_KEY` – случайная строка 32+ символа (`openssl rand -hex 32`)
   * `S3_ACCESS_KEY` / `S3_SECRET_KEY` – если используете MinIO/S3
   * `POSTGRES_EXPOSED_PORT`/`REDIS_EXPOSED_PORT` – при необходимости проброса наружу

> Файл `.env` **не должен** попадать в VCS.

---
## 4. Запуск инфраструктуры
```bash
# Собираем и поднимаем все контейнеры в фоне
docker compose up -d --build

# Проверяем состояние
docker compose ps
```
Ожидаемый результат – все сервисы в статусе `Up`.

### 4.1 Настройка sysctl для Redis
```bash
sudo sysctl -w vm.overcommit_memory=1
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf
# Перезапуск контейнера
docker compose restart redis
```

---
## 5. Инициализация базы данных
1. Подключаемся к контейнеру backend (один раз):
   ```bash
   docker compose exec merchant_api bash   # любой backend-контейнер
   ```
2. Запускаем миграции Alembic:
   ```bash
   alembic upgrade head
   ```
3. Сидируем конфигурацию (добавит `RATE_LIMIT_DEFAULT` и др.):
   ```bash
   python backend/scripts/seed_config.py
   ```
4. Выходим `exit`.

---
## 6. Health-чеки
```bash
curl http://YOUR_SERVER_IP:8000/health        # Gateway API
curl http://YOUR_SERVER_IP:15432/             # Проверка порта Postgres (ожидается «empty»)
```
Также убедитесь, что в логах (`docker compose logs -f`) нет ошибок `ERROR`.

---
## 7. Мини-Smoke-тест
1. Получить admin-токен:
   ```bash
   curl -X POST http://YOUR_SERVER_IP:8000/api/admin/auth/token \
        -d 'username=admin@example.com&password=admin123' \
        -H 'Content-Type: application/x-www-form-urlencoded'
   ```
2. Создать мерчанта и магазин – следуйте разделу 4 тест-плана (`backend/TEST_PLAN.md`).
3. Инитиировать Pay-In `/payin/init` и убедиться, что ордер появляется в БД.

---
## 8. Настройка HTTPS (рекомендация)
Используйте Nginx как reverse-proxy c Let's Encrypt.

```bash
sudo apt install nginx certbot python3-certbot-nginx
# … стандартный wizard certbot …
```
Конфигурация upstream-блока для Uvicorn-контейнеров:
```
upstream jivapay_backend {
    server 127.0.0.1:8000;
}
server {
    listen 80;
    server_name api.example.com;
    location / {
        proxy_pass http://jivapay_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---
## 9. Routine Operations
| Операция | Команда |
|----------|---------|
| Перезапуск всех сервисов | `docker compose restart` |
| Проверить логи конкретного сервиса | `docker compose logs -f merchant_api` |
| Выполнить миграции при обновлении | `docker compose exec merchant_api alembic upgrade head` |
| Создать резервную копию БД | `docker exec postgres-1 pg_dump -U postgres jiva_pay > backup.sql` |
| Очистить dangling-образы Docker | `docker image prune -f` |

---
## 10. Обновление системы
1. `git pull origin main`
2. Пересобрать контейнеры: `docker compose build`
3. Применить миграции: `docker compose exec merchant_api alembic upgrade head`
4. Перезапустить: `docker compose up -d`

---
## 11. Тонкая настройка (Production)
* Запуск Celery-worker под non-root пользователем (`USER celery` в Dockerfile).  
* Настроить мониторинг (Prometheus, Grafana, Loki).  
* Настроить ротацию логов и резервное копирование томов Docker.

---
## 12. Ссылки
* Тест-план: [`backend/TEST_PLAN.md`](backend/TEST_PLAN.md)  
* Трекер реализации: [`backend/IMPLEMENTATION_TRACKER.md`](backend/IMPLEMENTATION_TRACKER.md)  
* План реализации бэкенда: [`backend/README_IMPLEMENTATION_PLAN.md`](backend/README_IMPLEMENTATION_PLAN.md)

---
**Готово!** Следуя шагам выше, вы получите работающий инстанс JivaPay. 