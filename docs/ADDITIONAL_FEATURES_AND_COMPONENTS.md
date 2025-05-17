# Дополнительные функции и компоненты JivaPay

## 1. Введение

Этот документ детализирует функциональные дополнения для ролей Администратора, Саппорта и Тимлида в системе JivaPay. Описание строится на основе предоставленных требований и существующей архитектуры бэкенда и фронтенда, изложенной в основной документации проекта. Цель — предоставить четкое видение необходимых доработок, включая API эндпоинты, сервисные функции и изменения в UI, а также определить потенциально новые утилиты, которые могут потребоваться.

## 2. Общий список компонентов (Администраторы, Саппорты, Тимлиды)

Ниже представлен детализированный разбор каждого компонента из общего списка, доступного указанным ролям.

### 1) Баланс площадки

*   **Описание:** Отображение общего баланса платформы по различным валютам.
*   **Модели БД:** `BalancePlatform`
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/platform/balance` (для Админов)
*   **Сервисы Бэкенда:**
    *   `services.platform_service.get_platform_balances(db_session: Session)`: Агрегирует данные из `BalancePlatform`.
*   **Фронтенд (Admin App):**
    *   Виджет/секция на дашборде или отдельная страница.
    *   Отображение списка валют и соответствующих балансов.
*   **Утилиты/Логика:**
    *   Возможно, потребуется конвертация в базовую валюту для отображения общего эквивалента.

### 2) История ордеров

*   **Описание:** Просмотр истории всех ордеров с возможностью фильтрации и поиска.
*   **Модели БД:** `OrderHistory`, `IncomingOrder`, `User` (для трейдера, мерчанта), `MerchantStore`, `ReqTrader`.
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/orders` (для Админов)
    *   `GET /api/support/orders` (для Саппортов, с учетом прав)
*   **Сервисы Бэкенда:**
    *   `services.order_service.get_orders_history(db_session: Session, start_time: Optional[datetime], end_time: Optional[datetime], status: Optional[str], amount: Optional[Decimal], trader_id: Optional[int], store_id: Optional[int], requisite_identifier: Optional[str], user_query: Optional[str], page: int, per_page: int, current_user_role: str, current_user_id: int)`: Комплексный сервис для выборки ордеров с фильтрацией и пагинацией. `user_query` может искать по ID ордера, ID входящего ордера, email трейдера/мерчанта, названию магазина, части реквизита. Учитывает `current_user_role` и `current_user_id` для применения гранулярных прав.
*   **Фронтенд (Admin App, Support App):**
    *   Страница со списком ордеров в виде таблицы.
    *   Компоненты фильтров (выбор диапазона дат/времени, выпадающий список статусов).
    *   Поля для ввода поисковых запросов (сумма, ID трейдера/магазина, часть реквизита).
    *   Пагинация.
    *   Детальный просмотр ордера по клику (UI может скрывать/показывать поля в зависимости от прав).
*   **Утилиты/Логика:**
    *   Реализация эффективного поиска по нескольким полям и связанным таблицам.
    *   Оптимизация запросов к БД для больших объемов данных.
    *   Механизм проверки гранулярных прав в `services.order_service` перед возвратом данных.

### 3) Количество реквизитов онлайн

*   **Описание:** Отображение количества активных реквизитов в реальном времени с возможностью сортировки и фильтрации.
*   **Модели БД:** `ReqTrader`, `FullRequisitesSettings`, `Trader`, `User` (для email трейдера), `PaymentMethod`, `Bank`.
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/requisites/online-stats` (для Админов)
    *   `GET /api/support/requisites/online-stats` (для Саппортов, если разрешено гранулярными правами)
    *   `GET /api/teamlead/requisites/online-stats` (для Тимлидов, автоматическая фильтрация по своим трейдерам)
    *   SSE эндпоинт для обновлений в реальном времени: `GET /api/<role>/requisites/online-stats/stream`.
*   **Сервисы Бэкенда:**
    *   `services.requisite_service.get_online_requisites_stats(db_session: Session, sort_by: Optional[str], direction: Optional[str], trader_filter: Optional[str], payment_method_id: Optional[int], bank_id: Optional[int], requisite_type: Optional[str], team_lead_id: Optional[int] = None, current_user_role: str, current_user_id: int)`: Возвращает количество и, возможно, список реквизитов. Учитывает права и роль.
    *   `sort_by` может принимать значения: `limits_min`, `limits_max`, `direction` (pay_in/pay_out).
    *   `trader_filter` может быть email, username или ID трейдера.
    *   `requisite_type` для `pay_in`/`pay_out`.
*   **Фронтенд (Admin App, Support App, TeamLead App):**
    *   Виджет или секция, отображающая число.
    *   Таблица с реквизитами при клике или на отдельной странице.
    *   Опции сортировки (по верхним/нижним лимитам, направлению).
    *   Фильтры (по трейдеру, методу, банку).
    *   Обновление данных через SSE.
*   **Утилиты/Логика:**
    *   **Определение статуса "онлайн" для реквизита:** Кабинет трейдера доступен (`Trader.user.is_active == True`), трафик трейдера включен (`Trader.in_work == True` и `Trader.is_traffic_enabled_by_teamlead == True`), и реквизит включен в трафик на pay_in (`FullRequisitesSettings.pay_in == True`) или pay_out (`FullRequisitesSettings.pay_out == True`) или оба. Статус самого реквизита (`ReqTrader.status`) также должен быть активным (например, 'approve').
    *   Эффективная агрегация и фильтрация.

### 4) Количество трейдеров

*   **Описание:** Статистика по трейдерам с фильтрацией и сортировкой.
*   **Модели БД:** `Trader`, `User`, `OrderHistory` (для оборота и кол-ва ордеров), `ReqTrader` (для кол-ва реквизитов), `TraderAllowedFiat`, `TraderAllowedPaymentMethod`, `TraderWorkingCryptocurrency`.
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/traders/stats` (для Админов)
    *   `GET /api/support/traders/stats` (для Саппортов, если разрешено)
*   **Сервисы Бэкенда:**
    *   `services.trader_service.get_traders_statistics(db_session: Session, status_filter: Optional[str] = 'active', online_status: Optional[str] = 'online', turnover_period_start: Optional[datetime], turnover_period_end: Optional[datetime], sort_by: Optional[str], fiat_currency_id: Optional[int], payment_method_id: Optional[int], crypto_currency_id: Optional[int], search_query: Optional[str], page: int, per_page: int)`:
        *   `status_filter`: `all`/`active`.
        *   `online_status`: `online`/`offline`/`all`.
        *   `sort_by`: `turnover`, `requisite_count`, `registration_date`, `order_count`, `status` (заблокирован/активен).
        *   `search_query`: поиск по email, id, telegram, номеру телефона.
*   **Фронтенд (Admin App, Support App):**
    *   Страница со списком трейдеров в таблице.
    *   Фильтры: статус (активные/все), онлайн/оффлайн, диапазон дат для оборота, фиатная валюта, метод работы, рабочая криптовалюта.
    *   Сортировка: по обороту, кол-ву реквизитов, дате регистрации, кол-ву ордеров, статусу кабинета.
    *   Поле для поиска.
    *   Пагинация.
*   **Утилиты/Логика:**
    *   Определение "активного" и "онлайн" статуса трейдера.
    *   Расчет оборота за период.
    *   Агрегация данных из нескольких таблиц.

### 5) Количество мерчантов и их магазинов

*   **Описание:** Статистика по мерчантам и их магазинам.
*   **Модели БД:** `User` (для мерчанта), `MerchantProfile`, `MerchantStore`, `OrderHistory` (для оборота и ордеров).
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/merchants/stats` (для Админов)
*   **Сервисы Бэкенда:**
    *   `services.merchant_service.get_merchants_statistics(db_session: Session, status_filter: Optional[str] = 'active', online_status: Optional[str] = 'online', turnover_period_start: Optional[datetime], turnover_period_end: Optional[datetime], sort_by: Optional[str], fiat_currency_id: Optional[int], payment_method_id: Optional[int], crypto_currency_id: Optional[int], search_query: Optional[str], page: int, per_page: int)`: Аналогично статистике трейдеров, но для мерчантов и их магазинов.
*   **Фронтенд (Admin App):**
    *   Страница со списком мерчантов/магазинов.
    *   Аналогичные фильтры и сортировки, как для трейдеров.
*   **Утилиты/Логика:**
    *   Аналогично статистике трейдеров.

### 6) Общее количество ордеров

*   **Описание:** Отображение общего количества ордеров с возможностью сортировки.
*   **Модели БД:** `OrderHistory`, `IncomingOrder`.
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/orders/count` (для Админов)
*   **Сервисы Бэкенда:**
    *   `services.order_service.get_orders_count(db_session: Session, status: Optional[str], date_start: Optional[datetime], date_end: Optional[datetime])`:
        *   `status`: по умолчанию 'processing' (или соответствующий активный статус).
*   **Фронтенд (Admin App):**
    *   Виджет на дашборде.
    *   Фильтры по статусам, дате и времени.
*   **Утилиты/Логика:**
    *   Определение ордеров "в процессе обработки".

### 7) Логи критических ошибок

*   **Описание:** Доступ к логам критических ошибок системы.
*   **Модели БД:** `AuditLog` (если используется для системных ошибок), или интеграция с внешней системой логирования (Sentry, ELK).
*   **API эндпоинты (Бэкенд):**
    *   Если логи в БД: `GET /api/admin/logs/critical-errors`
    *   Если внешняя система: Непосредственный доступ к UI этой системы.
*   **Сервисы Бэкенда:**
    *   `services.audit_service.get_critical_system_errors(db_session: Session, page: int, per_page: int)`: Фильтрует `AuditLog` по типу `system_error` и уровню `critical`.
*   **Фронтенд (Admin App):**
    *   Страница с отображением списка логов ошибок.
    *   Фильтрация, пагинация.
*   **Утилиты/Логика:**
    *   Централизованная запись таких ошибок (через `utils.notifications.report_critical_error`, который также может писать в `AuditLog`).
    *   Определение, какие ошибки считать "критическими" и "влияющими на процесс работы алгоритма".

### 8) Количество администраторов

*   **Описание:** Статистика по администраторам.
*   **Модели БД:** `User`, `Admin` (ранее `AdminProfile`).
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/administrators/stats`
*   **Сервисы Бэкенда:**
    *   `services.user_service.get_administrators_statistics(db_session: Session, availability_filter: Optional[str] = 'available', page: int, per_page: int)`:
        *   `availability_filter`: `available` (User.is_active=true), `unavailable` (User.is_active=false), `all`.
*   **Фронтенд (Admin App):**
    *   Список администраторов.
    *   Фильтр "доступен/недоступен".
    *   При выборе администратора – просмотр доступных ему компонентов/функционала на основе его `Admin.granted_permissions`.
*   **Утилиты/Логика:**
    *   Механизм определения доступных компонентов на основе гранулярных прав в `Admin.granted_permissions`.

### 9) Количество тимлидов

*   **Описание:** Статистика по тимлидам.
*   **Модели БД:** `User`, `TeamLead` (ранее `TeamLeadProfile`).
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/teamleads/stats`
*   **Сервисы Бэкенда:**
    *   `services.user_service.get_teamleads_statistics(db_session: Session, status_filter: Optional[str] = 'active', page: int, per_page: int)`:
        *   `status_filter`: `active` (User.is_active=true), `all`.
*   **Фронтенд (Admin App):**
    *   Список тимлидов.
    *   Фильтр "активные/все".
*   **Утилиты/Логика:** -

### 10) Количество саппортов

*   **Описание:** Статистика по саппортам.
*   **Модели БД:** `User`, `Support` (ранее `SupportProfile`).
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/supports/stats`
*   **Сервисы Бэкенда:**
    *   `services.user_service.get_supports_statistics(db_session: Session, status_filter: Optional[str] = 'active', role_description: Optional[str], page: int, per_page: int)`:
        *   `status_filter`: `active` (User.is_active=true), `all`.
        *   `role_description`: поиск по описанию роли (поле `Support.role_description`).
*   **Фронтенд (Admin App):**
    *   Список саппортов.
    *   Фильтры: "активные/все", по роли (описанию).
*   **Утилиты/Логика:** -

## 3. Функционал Администраторов

Доступные компоненты: 1-10 из общего списка, плюс управление правами других ролей.
Права самого администратора хранятся в `Admin.granted_permissions` (JSON-поле со списком строковых разрешений, например, `["view_users", "edit_users", "manage_roles", "view_platform_balance", "manage_trader_traffic_all"]`).

### Взаимодействие с другими пользователями (при наличии соответствующих прав у текущего администратора):

#### а) При выборе другого администратора:
*   **Получаемая информация:** Вся доступная информация об администраторе (`User`, `Admin`), включая его `Admin.granted_permissions`.
*   **Функционал для взаимодействия (требует специфических прав у текущего админа, например, `admin:manage:permissions` или `admin:manage:block`):**
    *   Редактирование профиля другого администратора.
    *   Изменение его гранулярных прав (`Admin.granted_permissions`).
    *   Блокировка/разблокировка (`User.is_active`).
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/administrators/{admin_id}`
    *   `PUT /api/admin/administrators/{admin_id}` (для обновления данных)
    *   `PUT /api/admin/administrators/{admin_id}/permissions` (для обновления `granted_permissions`)
    *   `POST /api/admin/administrators/{admin_id}/block`
    *   `POST /api/admin/administrators/{admin_id}/unblock`
*   **Сервисы Бэкенда:**
    *   `services.user_service.get_administrator_details(db_session: Session, admin_id: int, current_admin_user: User)`: Проверяет права `current_admin_user` на просмотр `admin_id` (например, `admin:view:any` или `admin:view:profile:{admin_id}`).
    *   `services.user_service.update_administrator_profile(db_session: Session, admin_id: int, data: AdminProfileUpdateSchema, current_admin_user: User)`
    *   `services.permission_service.update_administrator_permissions(db_session: Session, admin_id: int, permissions: List[str], current_admin_user: User)`
*   **Фронтенд (Admin App):**
    *   Детальная страница администратора с его данными и доступными действиями (кнопки/формы активируются на основе прав текущего админа). Форма для редактирования списка `granted_permissions` (например, мультиселект с доступными разрешениями).

#### б) При выборе трейдера:
*   **Получаемая информация (требует права, например `trader:view:any:full_details`):** Вся доступная информация о трейдере (`User`, `Trader`, `ReqTrader`, `FullRequisitesSettings`, `BalanceTraderFiatHistory`, `BalanceTraderCryptoHistory`, `OrderHistory`).
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/traders/{trader_id}/full-details`
*   **Сервисы Бэкенда:**
    *   `services.trader_service.get_trader_full_details(db_session: Session, trader_id: int, current_admin_user: User)`: Агрегирует информацию. Проверяет права.
*   **Фронтенд (Admin App):**
    *   Детальная страница трейдера с вкладками или секциями: Профиль, Реквизиты, Балансы, История ордеров.

#### в) При выборе мерчанта:
*   **Получаемая информация (требует права, например `merchant:view:any:full_details`):** Вся информация о мерчанте и его магазинах.
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/merchants/{merchant_id}/full-details`
*   **Сервисы Бэкенда:**
    *   `services.merchant_service.get_merchant_full_details(db_session: Session, merchant_id: int, current_admin_user: User)`: Агрегирует информацию. Проверяет права.
*   **Фронтенд (Admin App):**
    *   Детальная страница мерчанта с вкладками или секциями: Профиль, Магазины (со своей детализацией), Балансы магазинов, История ордеров.

#### г) При выборе саппорта:
*   **Функционал (требует права, например `support:manage:permissions`):** Управление гранулярными правами саппорта (`Support.granted_permissions`).
*   **Модели БД:** `User`, `Support`.
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/supports/{support_id}/permissions`
    *   `PUT /api/admin/supports/{support_id}/permissions`
*   **Сервисы Бэкенда:**
    *   `services.permission_service.get_support_permissions(db_session: Session, support_id: int, current_admin_user: User)`
    *   `services.permission_service.update_support_permissions(db_session: Session, support_id: int, permissions: List[str], current_admin_user: User)`
*   **Фронтенд (Admin App):**
    *   На детальной странице саппорта – секция управления его `granted_permissions` (например, мультиселект с предопределенным списком возможных разрешений для саппортов).

#### д) При выборе тимлида:
*   **Функционал (требует прав, например `teamlead:manage:permissions`, `teamlead:view:any:full_details`):** Управление гранулярными правами тимлида (`TeamLead.granted_permissions`). Получение всей доступной информации о нем.
*   **Получаемая информация:** Аналогично предыдущему описанию, плюс его `TeamLead.granted_permissions`.
*   **API эндпоинты (Бэкенд):**
    *   `GET /api/admin/teamleads/{teamlead_id}/full-details`
    *   `GET /api/admin/teamleads/{teamlead_id}/permissions`
    *   `PUT /api/admin/teamleads/{teamlead_id}/permissions`
*   **Сервисы Бэкенда:**
    *   `services.teamlead_service.get_teamlead_full_details(db_session: Session, teamlead_id: int, current_admin_user: User)`
    *   `services.permission_service.get_teamlead_permissions(db_session: Session, teamlead_id: int, current_admin_user: User)`
    *   `services.permission_service.update_teamlead_permissions(db_session: Session, teamlead_id: int, permissions: List[str], current_admin_user: User)`
*   **Фронтенд (Admin App):**
    *   Детальная страница тимлида: Профиль, Управление `granted_permissions`, Команда трейдеров, Статистика.

## 4. Функционал Саппортов

Права саппорта хранятся в `Support.granted_permissions` (JSON-поле со списком строковых разрешений, например `["orders:view:assigned_to_any", "requisites:view:online_stats", "traders:view:limited_stats"]`).
*   **Доступные компоненты (определяются содержимым `Support.granted_permissions`):**
    *   **2) История ордеров:** `GET /api/support/orders`. Бэкенд фильтрует данные на основе прав (например, `orders:view:all` или `orders:view:status:pending`).
    *   **3) Количество реквизитов онлайн:** `GET /api/support/requisites/online-stats` (если есть право `requisites:view:online_stats`).
    *   **4) Количество трейдеров:** `GET /api/support/traders/stats` (если есть право, например, `traders:view:general_stats`, может возвращать ограниченный набор полей).
*   **Ключевая логика для саппортов:**
    *   Бэкенд строго проверяет права доступа саппорта из `Support.granted_permissions` перед возвратом любых данных или выполнением действий.
    *   Сервисы, вызываемые из `/api/support/*`, принимают `current_support_user: User` и используют `services.permission_service.check_permission(user_id=current_support_user.support_profile.id, permission_name="...", entity_scope="support")`.

## 5. Функционал Тимлидов

Права тимлида хранятся в `TeamLead.granted_permissions` (JSON-поле со списком строковых разрешений, например, `["team:manage:trader_traffic", "team:view:requisite_stats", "team:view:trader_performance"]`).
*   **Доступные компоненты (определяются содержимым `TeamLead.granted_permissions`):**
    *   **3) Количество реквизитов онлайн:** `GET /api/teamlead/requisites/online-stats` (если есть право `team:view:requisite_stats`). Сервис автоматически фильтрует реквизиты по трейдерам команды тимлида.
*   **Управление трафиком трейдеров (требует права, например `team:manage:trader_traffic`):**
    *   **Описание:** Тимлид может включать/выключать общий трафик для своих трейдеров (`Trader.is_traffic_enabled_by_teamlead`). Если трафик выключен тимлидом, трейдер не может включить его самостоятельно (`Trader.in_work` может быть True, но реквизиты не участвуют в подборе).
    *   **Модели БД:**
        *   `Trader`: добавить поле `is_traffic_enabled_by_teamlead: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)`.
        *   `Trader.in_work` (существующее поле для самостоятельного включения/выключения трейдером).
    *   **Логика работы трафика для трейдера (в `services.requisite_selector`):** Реквизиты трейдера участвуют в подборе, только если `Trader.user.is_active == True` И `Trader.in_work == True` И `Trader.is_traffic_enabled_by_teamlead == True`.
    *   **API эндпоинты (Бэкенд):**
        *   `GET /api/teamlead/traders` (получение списка своих трейдеров с их текущими статусами трафика)
        *   `POST /api/teamlead/traders/{trader_id}/enable-traffic`
        *   `POST /api/teamlead/traders/{trader_id}/disable-traffic`
    *   **Сервисы Бэкенда:**
        *   `services.teamlead_service.get_managed_traders(db_session: Session, current_teamlead_id: int)`
        *   `services.teamlead_service.set_trader_traffic_status_by_teamlead(db_session: Session, trader_id: int, enable: bool, current_teamlead_id: int)`:
            *   Проверяет, что `trader_id` принадлежит `current_teamlead_id`.
            *   Обновляет `Trader.is_traffic_enabled_by_teamlead`.
    *   **Фронтенд (TeamLead App):**
        *   Страница "Мои трейдеры" со списком трейдеров.
        *   Для каждого трейдера отображается его собственный статус активности и статус, установленный тимлидом.
        *   Переключатель (toggle switch) для тимлида, чтобы менять `is_traffic_enabled_by_teamlead`.
        *   Индикация, что трейдер не может сам включить трафик, если он выключен тимлидом.
    *   **Доработка сервиса подбора реквизитов (`services.requisite_selector`):** Учитывать все три флага: `Trader.user.is_active`, `Trader.in_work`, `Trader.is_traffic_enabled_by_teamlead`.

## 6. Потенциально необходимые доработки и новые утилиты/функции

Исходя из детализации выше, можно выделить следующие ключевые доработки и новые элементы:

*   **Новые/доработанные сервисы Бэкенда:**
    *   `services.platform_service`: Для получения баланса платформы.
    *   `services.order_service`: Существенное расширение для сложной фильтрации и поиска истории ордеров.
    *   `services.requisite_service`: Расширение для статистики онлайн-реквизитов с фильтрацией и сортировкой; доработка логики "онлайн" статуса.
    *   `services.trader_service`: Расширение для статистики трейдеров с комплексной фильтрацией, сортировкой и поиском; получение полных деталей трейдера.
    *   `services.merchant_service`: Аналогично `trader_service`, но для мерчантов.
    *   `services.user_service`: Расширение для статистики администраторов, тимлидов, саппортов; управление деталями и правами администраторов.
    *   `services.audit_service`: Для извлечения логов критических ошибок.
    *   `services.permission_service`: Будет ключевым для управления и проверки гранулярных прав из JSON-полей в профилях `Admin`, `Support`, `TeamLead`.
        *   `grant_permission(user_profile, permission_string)`
        *   `revoke_permission(user_profile, permission_string)`
        *   `has_permission(user_profile, permission_string, target_entity_id=None)`
*   **Обновление моделей БД:**
    *   `Trader`: Добавить поле `is_traffic_enabled_by_teamlead: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)`.
    *   `Support`: Добавить поле `role_description: Mapped[Optional[str]]`. Добавить `granted_permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, server_default='[]')`. Убрать специфичные булевы флаги прав, если они полностью заменяются гранулярной системой.
    *   `Admin`: Добавить `granted_permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, server_default='[]')`. Убрать специфичные булевы флаги прав.
    *   `TeamLead`: Добавить `granted_permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, server_default='[]')`.
    *   `FullRequisitesSettings`: **Удалить** поле `active_hours`, так как определение "онлайн" реквизита изменилось.
*   **Новые API эндпоинты:**
    *   Множество новых эндпоинтов в роутерах `/api/admin/*`, `/api/support/*`, `/api/teamlead/*` для предоставления описанного функционала.
*   **SSE (Server-Sent Events):**
    *   Потребуется реализация или расширение существующих SSE эндпоинтов для компонента "Количество реквизитов онлайн".
*   **Фронтенд:**
    *   UI для управления гранулярными правами администраторов, саппортов, тимлидов (например, в админке при редактировании пользователя - список чекбоксов/мультиселект с доступными разрешениями).
    *   UI должен динамически отображать/скрывать элементы или блокировать действия на основе полученных от бэкенда данных и (частично) на основе проверки прав на клиенте для улучшения UX (но основная проверка всегда на бэкенде).
*   **Утилиты:**
    *   `utils.query_builder`: По-прежнему актуально.
    *   `utils.permission_checker` (или внутри `services.permission_service`): Функции для удобной работы со списком строковых разрешений (проверка наличия, проверка на соответствие шаблону, например, `entity:action:*` или `entity:action:id`).
        *   Пример строк разрешений:
            *   `admin:view:any`, `admin:edit:any`, `admin:permissions:manage`
            *   `support:view:orders`, `support:view:trader_basic_info`
            *   `teamlead:manage:trader_traffic`, `teamlead:view:own_team_stats`
            *   `platform:view:balance`
            *   `orders:view:all_details`, `orders:edit:status`
            *   `requisites:view:online_stats`, `requisites:manage:all`
            *   `users:view:all`, `users:manage:traders`, `users:manage:permissions:support`
            *   `logs:view:critical`

## 7. Заключение

Представленные дополнения значительно расширяют возможности управления и мониторинга платформы JivaPay. Реализация потребует скоординированной работы над бэкендом (API, сервисы, БД) и фронтендом (UI/UX для соответствующих ролевых приложений). Ключевыми аспектами становятся гибкая система гранулярных прав и корректная логика определения статусов сущностей (например, "онлайн" реквизита).