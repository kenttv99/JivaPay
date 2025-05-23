# План Рефакторинга Frontend JivaPay

Дата создания: 2024-12-27  
Статус: В разработке  
**Обновлено**: Рефакторинг компонентов ui-kit - удалены неиспользуемые компоненты

> **📋 СООТВЕТСТВИЕ БЭКЕНДУ**: План полностью синхронизирован с документацией `docs/README_MAIN_BACKEND.md`. Все функции, сервисы и API эндпоинты соответствуют реализации бэкенда: `trader_service.py`, `merchant_service.py`, `teamlead_service.py`, `permission_service.py`, `order_service.py`, `balance_manager.py`, `gateway_service.py` и др.

## Анализ Текущего Состояния

### ✅ Что уже реализовано
- Монорепозиторий с npm workspaces
- Оптимизированный ui-kit (10 универсальных компонентов) 
- admin_app с полноценными страницами и компонентами
- Система CSS переменных для темизации
- Базовая структура всех 5 приложений: admin_app, teamlead_app, support_app, trader_app, merchant_app
- trader_app с локальными компонентами Button и Card

### ❌ Критические проблемы и костыли

**Проблемы в коде:**
- 🔥 Hardcoded mock данные во всех компонентах admin_app
- 🔥 Дублированные стили карточек и компонентов  
- 🔥 Inline стили (`style={{width: '82%'}}`)
- 🔥 Hardcoded цвета (`bg-green-100`, `text-green-600`) вместо CSS переменных
- 🔥 Дублированный код таблиц и форм

**Архитектурные недостатки:**
- ❌ Отсутствует система проверки прав на фронтенде
- 🔥 Страницы admin_app не переиспользуются в teamlead_app и support_app
- ❌ Отсутствуют уникальные страницы для trader_app и merchant_app
- ❌ Недостаточно базовых компонентов в ui-kit для покрытия всех приложений

---

## 🎯 ЦЕЛЬ РЕФАКТОРИНГА

**Главная задача:** Создать единую экосистему для всех 5 приложений:

### Группа 1: Административные приложения (общие компоненты)
- `admin_app` - полный доступ ко всем административным функциям
- `teamlead_app` - доступ к управлению командой и ограниченному набору функций  
- `support_app` - доступ к поддержке пользователей и просмотру данных

### Группа 2: Пользовательские приложения (уникальные страницы)
- `trader_app` - уникальные страницы для управления реквизитами и обработки ордеров + локальные компоненты Button, Card
- `merchant_app` - уникальные страницы для управления магазинами и отслеживания платежей

**Общие принципы:**
- **ui-kit стили**: Используются во ВСЕХ 5 приложениях
- **permissions система**: Работает во всех приложениях
- **shared-pages**: Только для admin/teamlead/support
- **Уникальные страницы**: Для trader/merchant с использованием ui-kit компонентов + локальных компонентов при необходимости

---

## 🎯 ТЕКУЩИЙ СТАТУС РЕФАКТОРИНГА (Обновлено)

### ✅ ЗАВЕРШЕНО
- **Секция 1: Централизация Стилей и UI Компонентов** - 100% выполнено
  - Перенос компонентов из admin_app в ui-kit ✅
  - Очистка от hardcoded стилей ✅  
  - Расширение ui-kit дополнительными компонентами ✅
  - Настройка ui-kit во всех 5 приложениях ✅
  - **РЕФАКТОРИНГ**: Удаление неиспользуемых компонентов из ui-kit ✅
  - **АРХИТЕКТУРА**: Исправление нарушений принципов монорепозитория ✅

### 🎯 СЛЕДУЮЩИЕ ЭТАПЫ
1. **Секция 2: Создание Системы Прав** (0% выполнено)
   - Создание пакета permissions
   - Расширение типов для всех ролей  
   - Интеграция с бэкенд API прав

2. **Секция 3: Создание Общих Компонентов** (0% выполнено)
   - Создание пакета shared-pages для admin/teamlead/support
   - Конфигурации для административных ролей

3. **Секция 4: Создание Уникальных Страниц** (0% выполнено)
   - Развитие trader_app с уникальными страницами
   - Развитие merchant_app с уникальными страницами

4. **Секция 5: Миграция Всех Приложений** (0% выполнено)
   - Обновление административных приложений
   - Создание уникальных страниц для trader/merchant
   - Настройка permissions во всех приложениях

### 🏆 ДОСТИГНУТЫЕ РЕЗУЛЬТАТЫ
- **ui-kit стили используются во ВСЕХ 5 приложениях** ✅
- **0% hardcoded стилей в admin_app** ✅  
- **Единая CSS переменная система для всех цветов** ✅
- **10 оптимизированных ui-kit компонентов** ✅ (удалены неиспользуемые Button, Card, Input)
- **trader_app с локальными Button и Card компонентами** ✅
- **Соблюдение принципов монорепозитория** ✅

**Ключевые достижения:**
- 🎯 **0% hardcoded стилей** во всех приложениях 
- 🎨 **Единые CSS переменные** для всех цветов и стилей
- 📦 **Оптимизированные ui-kit компоненты** используются во всех 5 приложениях
- 🔧 **Утилитарные классы** для статусов и стандартных элементов
- 📱 **Адаптивный дизайн** с консистентным поведением
- 🧹 **Чистая архитектура** без неиспользуемых компонентов
- 🏗️ **Правильная архитектура монорепозитория** без локального дублирования

**Компоненты ui-kit (используются во всех приложениях):**
- ✅ Navigation (Sidebar, Header) - универсальная навигация, обновленная согласно референсу platform-admin-view
- ✅ StatsCard - карточки метрик и статистики  
- ✅ DataTable - таблицы с сортировкой и фильтрацией
- ✅ StatusBadge - бейджи статусов с CSS переменными
- ✅ TabGroup - табы для группировки контента
- ✅ Modal - модальные окна для всех типов форм
- ✅ Alert - уведомления с типизацией (success, error, warning, info)
- ✅ Dropdown - выпадающие меню действий
- ✅ Select - селекты с поиском и валидацией
- ✅ Spinner - индикаторы загрузки разных размеров

**Локальные компоненты trader_app:**
- ✅ Button - кнопки с вариантами (primary, secondary, ghost, outline)
- ✅ Card - карточки контента с вариантами (default, glass, dark)

**🗑️ УДАЛЕННЫЕ КОМПОНЕНТЫ:**
- ❌ **Input из ui-kit** - не использовался нигде, полностью удален
- ❌ **Button из ui-kit** - перенесен в trader_app как локальный компонент  
- ❌ **Card из ui-kit** - перенесен в trader_app как локальный компонент

#### ✅ 1.1 Перенос компонентов из admin_app в ui-kit **ВЫПОЛНЕНО**
```
✅ Перенесены компоненты (теперь используются во всех 5 приложениях):
admin_app/src/components/widgets/StatsCard.tsx    → ui-kit/components/StatsCard/
admin_app/src/components/widgets/Sidebar.tsx      → ui-kit/components/Navigation/Sidebar/
admin_app/src/components/widgets/Header.tsx       → ui-kit/components/Navigation/Header/
admin_app/src/components/ui/DataTable.tsx         → ui-kit/components/Table/
admin_app/src/components/ui/StatusBadge.tsx       → ui-kit/components/Badge/
admin_app/src/components/ui/TabGroup.tsx          → ui-kit/components/Tabs/

✅ Расширены CSS переменные: добавлены цвета статусов (success, error, warning, info, neutral)
✅ Все компоненты используют CSS переменные вместо hardcoded цветов
✅ Sidebar и Header стали универсальными для всех приложений (без привязки к Next.js)
```

#### ✅ 1.2 Очистка от hardcoded стилей во ВСЕХ приложениях **ВЫПОЛНЕНО**
```
✅ Заменены все hardcoded цвета на CSS переменные во всех компонентах admin_app
✅ Убраны inline стили типа style={{width: '82%'}}
✅ Созданы утилитарные классы для статусов (status-success, status-error, status-warning, status-info)
✅ Централизованы все цвета в ui-kit/styles/variables.css
✅ Обновлены все импорты в admin_app для использования компонентов из ui-kit
✅ Удалены дублированные компоненты из admin_app (они перенесены в ui-kit)
✅ MainLayout адаптирован под новые универсальные компоненты Sidebar и Header
```

#### ✅ 1.3 Расширение ui-kit компонентами для всех ролей **ВЫПОЛНЕНО**
```
✅ Созданы компоненты для покрытия всех приложений:
ui-kit/components/Modal/             ✅ Модальные окна (все приложения)
ui-kit/components/Dropdown/          ✅ Выпадающие списки (все)
ui-kit/components/Select/            ✅ Селекты (все)
ui-kit/components/Spinner/           ✅ Загрузка (все)
ui-kit/components/Alert/             ✅ Уведомления (все)

✅ Все компоненты используют CSS переменные для консистентного дизайна
✅ Компоненты поддерживают различные размеры, варианты и настройки
✅ Созданы индексные файлы и обновлен главный экспорт ui-kit
```

#### ✅ 1.4 Настройка ui-kit во всех приложениях **ВЫПОЛНЕНО**
```
✅ Обновлены package.json для всех 5 приложений:
admin_app/package.json     ✅ добавлен @jivapay/ui-kit
teamlead_app/package.json  ✅ добавлен @jivapay/ui-kit  
support_app/package.json   ✅ добавлен @jivapay/ui-kit
trader_app/package.json    ✅ добавлен @jivapay/ui-kit + classnames для локальных компонентов
merchant_app/package.json  ✅ добавлен @jivapay/ui-kit

✅ Настроены CSS импорты для всех приложений (globals.css)
✅ Создана демонстрационная страница trader_app с использованием ui-kit + локальных компонентов
✅ Все приложения используют единые CSS переменные и стили
```

#### ✅ 1.5 Оптимизация архитектуры компонентов **ВЫПОЛНЕНО**
```
🗑️ РЕФАКТОРИНГ ui-kit:
✅ Удален Input компонент из ui-kit (не использовался нигде)
✅ Удален Button компонент из ui-kit (перенесен в trader_app)  
✅ Удален Card компонент из ui-kit (перенесен в trader_app)
✅ Удалена зависимость classnames из ui-kit (больше не нужна)

📦 СОЗДАНИЕ trader_app локальных компонентов:
✅ trader_app/src/components/Button/ - локальный Button компонент с CSS модулями
✅ trader_app/src/components/Card/ - локальный Card компонент с CSS модулями  
✅ Добавлена зависимость classnames в trader_app для работы с CSS модулями
✅ Обновлены импорты в trader_app/src/app/page.tsx для использования локальных компонентов
✅ Успешная сборка trader_app с новыми компонентами

🎯 РЕЗУЛЬТАТ: ui-kit стал чище и содержит только действительно переиспользуемые компоненты
```

#### ✅ 1.6 Исправление нарушений архитектуры монорепозитория **ВЫПОЛНЕНО**
```
❌ ПРОБЛЕМА: Были созданы локальные Header и Sidebar компоненты в admin_app
   - frontend/admin_app/src/components/Layout/Header.tsx ❌ Дублирование ui-kit функциональности
   - frontend/admin_app/src/components/Layout/Sidebar.tsx ❌ Нарушение принципов монорепозитория

🔧 РЕШЕНИЕ: Исправление существующих компонентов ui-kit
✅ Удалены неправильные локальные компоненты из admin_app:
   - frontend/admin_app/src/components/Layout/Header.tsx → УДАЛЕН
   - frontend/admin_app/src/components/Layout/Sidebar.tsx → УДАЛЕН

✅ Исправлены существующие компоненты ui-kit согласно референсу platform-admin-view:
   - ui-kit/components/Navigation/Header/Header.tsx → обновлен (h-14, белый фон, правильные стили)
   - ui-kit/components/Navigation/Sidebar/Sidebar.tsx → обновлен (темный #212121, белый текст, кнопка collapse)

✅ Обновлен MainLayout в admin_app для использования исправленных ui-kit компонентов:
   - Импорт { Header, Sidebar } from "@jivapay/ui-kit"
   - Передача navigation массива в Sidebar
   - Передача userProfile в Header
   - Использование LinkComponent={Link} для Next.js совместимости

🎯 АРХИТЕКТУРНЫЙ РЕЗУЛЬТАТ:
   - ✅ Соблюдение принципов монорепозитория: ui-kit содержит общие компоненты для ВСЕХ приложений
   - ✅ Локальные компоненты только там где необходимо: trader_app (Button, Card)
   - ✅ Единый дизайн: все приложения используют одинаковые Header и Sidebar из ui-kit
   - ✅ Правильная структура: общие компоненты в ui-kit, специфичные локально
```

---

### 2. Создание Системы Прав для ВСЕХ Приложений

#### 2.1 Создание пакета permissions
```
frontend/packages/permissions/
├── src/
│   ├── index.ts                    # Экспорты
│   ├── types.ts                    # TypeScript типы для всех ролей
│   ├── PermissionContext.tsx       # React Context
│   ├── usePermissions.ts           # Хук для проверки прав
│   ├── PermissionGuard.tsx         # Компонент защиты UI
│   └── utils.ts                    # Утилиты проверки прав
```

#### 2.2 Расширение типов для всех ролей
```typescript
// packages/permissions/src/types.ts
export interface UserPermissions {
  userId: number;
  role: 'admin' | 'support' | 'teamlead' | 'merchant' | 'trader';
  grantedPermissions: string[]; // JSON поле из бэкенда
}

// Права для всех ролей (согласно permission_service.py)
export const ROLE_PERMISSIONS = {
  admin: ['*:*:*'],  // Полный доступ
  
  support: [
    'users:view:assigned',
    'orders:view:assigned', 
    'orders:edit:assigned',
    'tickets:manage:own',
    'dashboard:view:basic'
  ],
  
  teamlead: [
    'users:view:team',
    'orders:view:team',
    'trader:manage:team',
    'trader:traffic:team',        // is_traffic_enabled_by_teamlead
    'statistics:view:team',
    'dashboard:view:team'
  ],
  
  merchant: [
    'stores:manage:own',
    'orders:view:own',
    'orders:create:own',
    'reports:view:own',
    'webhooks:manage:own',
    'api-keys:manage:own',
    'dashboard:view:own'
  ],
  
  trader: [
    'requisites:manage:own',
    'orders:view:assigned',
    'orders:process:assigned',    // confirm_order_by_trader
    'balance:view:own',
    'balance:history:own',
    'profile:manage:own',
    'dashboard:view:own'
  ]
};

// Wildcard поддержка (как в permission_service._match_permission)
export interface PermissionPattern {
  resource: string;    // users, orders, stores
  action: string;      // view, edit, manage, create
  scope: string;       // *, own, team, assigned, {id}
}

export const parsePermission = (permission: string): PermissionPattern => {
  const [resource, action, scope] = permission.split(':');
  return { resource, action, scope };
};

// Проверка соответствия (аналог _match_permission из бэкенда)
export const matchPermission = (
  required: string, 
  granted: string[]
): boolean => {
  // Полный доступ
  if (granted.includes('*:*:*')) return true;
  
  const requiredPattern = parsePermission(required);
  
  return granted.some(grantedPerm => {
    const grantedPattern = parsePermission(grantedPerm);
    
    // Точное совпадение
    if (grantedPerm === required) return true;
    
    // Wildcard в ресурсе
    if (grantedPattern.resource === '*') return true;
    
    // Wildcard в действии
    if (grantedPattern.resource === requiredPattern.resource && 
        grantedPattern.action === '*') return true;
    
    // Wildcard в области
    if (grantedPattern.resource === requiredPattern.resource && 
        grantedPattern.action === requiredPattern.action && 
        grantedPattern.scope === '*') return true;
    
    return false;
  });
};
```

#### 2.3 Интеграция с бэкенд API прав для всех приложений
- Поддержка паттернов: `users:view:*`, `orders:edit:{id}`, `stores:manage:own`
- Загрузка прав пользователя с /auth/me эндпоинта
- Настройка в каждом из 5 приложений

---

### 3. Создание Общих Компонентов для Административных Приложений

#### 3.1 Создание пакета shared-pages (только для admin/teamlead/support)
```
frontend/packages/shared-pages/
├── src/
│   ├── index.ts
│   ├── pages/                      # Административные страницы
│   │   ├── DashboardPage/          # Панель управления
│   │   ├── UsersPage/              # Управление пользователями  
│   │   ├── FinancePage/            # Финансы и транзакции
│   │   ├── AnalyticsPage/          # Аналитика и графики
│   │   ├── StoresPage/             # Управление магазинами (только admin)
│   │   └── SettingsPage/           # Настройки системы
│   ├── components/                 # Переиспользуемые части
│   │   ├── MetricsGrid/            # Сетка метрик
│   │   ├── TransactionTable/       # Таблица транзакций
│   │   ├── UserManagement/         # Управление пользователями
│   │   ├── OrdersTable/            # Таблица заказов
│   │   └── PaymentChart/           # График платежей
│   ├── hooks/                      # API хуки для административных функций
│   │   ├── useUsers.ts
│   │   ├── useOrders.ts
│   │   ├── useMetrics.ts
│   │   └── useAnalytics.ts
│   └── configs/                    # Конфигурации только для admin/teamlead/support
│       └── roleConfigs.ts
```

#### 3.2 Конфигурации для административных ролей
```typescript
// shared-pages/src/configs/roleConfigs.ts
export const DASHBOARD_CONFIGS = {
  admin: {
    permissions: {
      viewMetrics: 'dashboard:view:*',
      viewOrders: 'orders:view:*',
      viewUsers: 'users:view:*',
      viewStores: 'stores:view:*'
    },
    config: { showAdvancedMetrics: true, enableExport: true }
  },
  
  teamlead: {
    permissions: {
      viewMetrics: 'dashboard:view:team',
      viewOrders: 'orders:view:team',
      viewUsers: 'users:view:team'
    },
    config: { showAdvancedMetrics: true, enableExport: false }
  },
  
  support: {
    permissions: {
      viewMetrics: 'dashboard:view:basic',
      viewOrders: 'orders:view:assigned',
      viewUsers: 'users:view:assigned'
    },
    config: { showAdvancedMetrics: false, enableExport: false }
  }
};
```

---

### 4. Создание Уникальных Страниц для Trader и Merchant

#### 4.1 Развитие trader_app
```
trader_app/src/
├── app/
│   ├── page.tsx                    # ✅ Дашборд трейдера (реализовано с локальными компонентами)
│   ├── requisites/
│   │   ├── page.tsx               # Управление реквизитами (CRUD)
│   │   ├── [id]/page.tsx          # Редактирование реквизита
│   │   ├── stats/page.tsx         # Статистика реквизитов (get_online_requisites_stats)
│   │   └── create/page.tsx        # Создание нового реквизита
│   ├── orders/
│   │   ├── page.tsx               # Назначенные ордера (get_orders_for_trader)  
│   │   ├── [id]/page.tsx          # Обработка/подтверждение ордера (confirm_order_by_trader)
│   │   └── history/page.tsx       # История завершенных ордеров
│   ├── balance/
│   │   ├── page.tsx               # Текущие балансы (фиат/крипто)
│   │   ├── history/page.tsx       # История балансов (BalanceTraderFiatHistory, BalanceTraderCryptoHistory)
│   │   └── withdrawals/page.tsx   # Заявки на вывод
│   └── profile/
│       ├── page.tsx               # Настройки профиля
│       └── stats/page.tsx         # Личная статистика (get_trader_full_details)
├── components/                     # ✅ Локальные компоненты (созданы)
│   ├── Button/                    # ✅ Локальный Button компонент
│   ├── Card/                      # ✅ Локальный Card компонент
│   ├── RequisiteForm/             # Форма создания/редактирования реквизита
│   ├── RequisiteCard/             # Карточка реквизита с статусом
│   ├── OrderProcessor/            # Компонент обработки ордера с загрузкой чека
│   ├── BalanceChart/              # График изменения балансов
│   ├── OrderConfirmation/         # Подтверждение ордера (для PayOut)
│   └── TrafficToggle/             # Переключатель работы (is_traffic_enabled_by_teamlead)
├── hooks/                         # API хуки для трейдера  
│   ├── useRequisites.ts           # CRUD реквизитов + статистика
│   ├── useTraderOrders.ts         # Получение и обработка ордеров
│   ├── useTraderBalance.ts        # Балансы и история
│   └── useTraderStats.ts          # Статистика трейдера
└── services/                      # API сервисы трейдера
    ├── requisites.ts              # API для работы с реквизитами
    ├── orders.ts                  # API для ордеров трейдера
    ├── balance.ts                 # API для балансов
    └── profile.ts                 # API профиля трейдера
```

#### 4.2 Развитие merchant_app
```
merchant_app/src/
├── app/
│   ├── page.tsx                   # Дашборд мерчанта
│   ├── stores/
│   │   ├── page.tsx              # Список магазинов (get_merchant_stores)
│   │   ├── [id]/page.tsx         # Управление магазином (update_merchant_store)
│   │   ├── [id]/settings/page.tsx # Настройки магазина (комиссии, колбэки)
│   │   └── create/page.tsx       # Создание магазина (create_merchant_store)
│   ├── orders/
│   │   ├── page.tsx              # История ордеров (get_orders_for_merchant)
│   │   ├── [id]/page.tsx         # Детали ордера
│   │   └── create/page.tsx       # Создание ордера (create_order_from_incoming)
│   ├── payments/
│   │   ├── page.tsx              # Активные платежи 
│   │   └── gateway/page.tsx      # Интеграция с платежным шлюзом
│   ├── reports/
│   │   ├── page.tsx              # Отчеты и аналитика (get_merchants_statistics)
│   │   ├── revenue/page.tsx      # Анализ доходов
│   │   └── conversion/page.tsx   # Анализ конверсии
│   ├── integration/
│   │   ├── page.tsx              # API документация 
│   │   ├── webhooks/page.tsx     # Настройка webhook (callback_service)
│   │   └── keys/page.tsx         # Управление API ключами
│   └── profile/
│       ├── page.tsx              # Настройки профиля
│       └── details/page.tsx      # Полная информация (get_merchant_full_details)
├── components/                    # Компоненты специфичные для мерчанта
│   ├── StoreForm/                # Форма создания/редактирования магазина
│   ├── StoreCard/                # Карточка магазина с метриками
│   ├── PaymentWidget/            # Виджет инициации платежа
│   ├── RevenueChart/             # График доходов
│   ├── ConversionChart/          # График конверсии
│   ├── ApiKeyManager/            # Управление API ключами
│   ├── WebhookSettings/          # Настройка webhook URL
│   └── OrderCreator/             # Форма создания ордера
├── hooks/                        # API хуки для мерчанта
│   ├── useStores.ts              # CRUD магазинов
│   ├── useMerchantOrders.ts      # Ордера мерчанта  
│   ├── useReports.ts             # Отчеты и статистика
│   ├── usePaymentGateway.ts      # Интеграция с gateway_service
│   └── useMerchantProfile.ts     # Профиль мерчанта
└── services/                     # API сервисы мерчанта
    ├── stores.ts                 # API для магазинов
    ├── orders.ts                 # API для ордеров мерчанта
    ├── reports.ts                # API для отчетов
    ├── gateway.ts                # API для платежного шлюза  
    └── webhooks.ts               # API для webhook/колбэков
```

---

### 5. Миграция Всех Приложений

#### 5.1 Обновление административных приложений (admin/teamlead/support)
```typescript
// admin_app/src/app/page.tsx
'use client';
import { DashboardPage } from '@jivapay/shared-pages';
import { DASHBOARD_CONFIGS } from '@jivapay/shared-pages/configs';
import { usePermissions } from '@jivapay/permissions';
import MainLayout from '@/layouts/MainLayout';

export default function Dashboard() {
  const { userRole } = usePermissions();
  const config = DASHBOARD_CONFIGS[userRole];
  return (
    <MainLayout>
      <DashboardPage {...config} />
    </MainLayout>
  );
}
```

#### 5.2 Создание уникальных страниц для trader_app
```typescript
// trader_app/src/app/page.tsx ✅ РЕАЛИЗОВАНО
'use client';
import { StatsCard, DataTable, Alert, Spinner } from '@jivapay/ui-kit';
import { Button } from '@/components/Button';  // Локальный компонент
import { Card } from '@/components/Card';      // Локальный компонент
import { useTraderMetrics, useRecentOrders } from '@/hooks';
import MainLayout from '@/layouts/MainLayout';

export default function TraderDashboard() {
  const { data: metrics } = useTraderMetrics();
  const { data: orders } = useRecentOrders();
  
  return (
    <MainLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Панель трейдера</h1>
        
        <div className="grid grid-cols-4 gap-6">
          <StatsCard title="Активные реквизиты" value={metrics?.activeRequisites} />
          <StatsCard title="Ордера в работе" value={metrics?.ordersInProgress} />
          <StatsCard title="Баланс" value={`₽ ${metrics?.balance}`} />
          <StatsCard title="Доход за день" value={`₽ ${metrics?.dailyProfit}`} />
        </div>
        
        <Card className="p-6">
          <h2 className="text-xl font-bold mb-4">Быстрые действия</h2>
          <div className="flex gap-4">
            <Button variant="primary">Добавить реквизит</Button>
            <Button variant="secondary">Просмотр ордеров</Button>
            <Button variant="outline">Статистика</Button>
          </div>
        </Card>
        
        <DataTable 
          columns={traderOrderColumns} 
          data={orders}
          permissions={{ view: 'orders:view:assigned' }}
        />
      </div>
    </MainLayout>
  );
}
```

#### 5.3 Создание уникальных страниц для merchant_app
```typescript
// merchant_app/src/app/page.tsx
'use client';
import { StatsCard, Chart } from '@jivapay/ui-kit';
import { useMerchantMetrics, useRevenueChart } from '@/hooks';
import MainLayout from '@/layouts/MainLayout';

export default function MerchantDashboard() {
  const { data: metrics } = useMerchantMetrics();
  const { data: revenue } = useRevenueChart();
  
  return (
    <MainLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Панель мерчанта</h1>
        
        <div className="grid grid-cols-4 gap-6">
          <StatsCard title="Активные магазины" value={metrics?.activeStores} />
          <StatsCard title="Успешные платежи" value={metrics?.successfulPayments} />
          <StatsCard title="Оборот за месяц" value={`₽ ${metrics?.monthlyRevenue}`} />
          <StatsCard title="Конверсия" value={`${metrics?.conversion}%`} />
        </div>
        
        <Chart 
          type="line" 
          data={revenue} 
          title="Динамика доходов"
          permissions={{ view: 'reports:view:own' }}
        />
      </div>
    </MainLayout>
  );
}
```

#### 5.4 Настройка permissions во ВСЕХ приложениях
```typescript
// Одинаковый провайдер для всех 5 приложений:
// admin_app/src/providers/AppPermissionProvider.tsx
// teamlead_app/src/providers/AppPermissionProvider.tsx  
// support_app/src/providers/AppPermissionProvider.tsx
// trader_app/src/providers/AppPermissionProvider.tsx
// merchant_app/src/providers/AppPermissionProvider.tsx

export const AppPermissionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [userPermissions, setUserPermissions] = useState<UserPermissions | null>(null);
  
  useEffect(() => {
    const loadPermissions = async () => {
      try {
        const response = await fetch('/api/auth/me');
        const userData = await response.json();
        setUserPermissions({
          userId: userData.id,
          role: userData.role,
          grantedPermissions: userData.granted_permissions || []
        });
      } catch (error) {
        console.error('Failed to load permissions:', error);
      }
    };
    
    loadPermissions();
  }, []);
  
  return (
    <PermissionProvider value={userPermissions}>
      {children}
    </PermissionProvider>
  );
};
```

---

### 6. Подготовка к Интеграции с Бэкендом

#### 6.1 Создание API сервисов для всех приложений
```
frontend/packages/api-services/
├── src/
│   ├── index.ts
│   ├── client.ts              # Axios конфигурация для всех
│   ├── auth.ts                # Авторизация всех ролей
│   ├── admin/                 # API для админов (backend/api_routers/admin/)
│   │   ├── users.ts          # get_all_users_basic, permission_service
│   │   ├── orders.ts         # get_orders_history (с правами)
│   │   ├── analytics.ts      # Административная аналитика
│   │   ├── platform.ts       # get_platform_balances
│   │   └── requisites.ts     # set_requisite_status, moderation
│   ├── merchant/              # API для мерчантов (backend/api_routers/merchant/, common/stores, common/merchant_orders)
│   │   ├── stores.ts         # create_merchant_store, get_merchant_stores, update_merchant_store, delete_merchant_store
│   │   ├── orders.ts         # get_orders_for_merchant, create_order_from_incoming
│   │   ├── reports.ts        # get_merchants_statistics
│   │   ├── gateway.ts        # initiate_payment_session, get_incoming_order_status
│   │   └── webhooks.ts       # callback_service интеграция
│   ├── trader/                # API для трейдеров (backend/api_routers/trader/, common/trader_orders)
│   │   ├── requisites.ts     # get_online_requisites_stats, CRUD реквизитов
│   │   ├── orders.ts         # get_orders_for_trader, confirm_order_by_trader
│   │   ├── balance.ts        # balance_manager API, история балансов
│   │   └── profile.ts        # get_trader_full_details
│   ├── support/               # API для саппортов (backend/api_routers/support/)
│   │   ├── tickets.ts        # Система тикетов
│   │   ├── users.ts          # Ограниченный доступ к пользователям
│   │   └── orders.ts         # orders с фильтрацией support
│   ├── teamlead/              # API для тимлидов (backend/api_routers/teamlead/, common/teamlead_traders)
│   │   ├── team.ts           # list_traders_for_teamlead, set_trader_in_work_status_by_teamlead
│   │   ├── traffic.ts        # set_trader_traffic_status_by_teamlead
│   │   └── reports.ts        # get_team_statistics
│   ├── common/                # Общие API (backend/api_routers/common/)
│   │   ├── orders.ts         # Общие функции для ордеров
│   │   ├── reference.ts      # reference_data.py - банки, валюты, методы
│   │   └── audit.ts          # audit_service - логи событий
│   └── types/                 # Общие типы (соответствие backend/schemas_enums/)
│       ├── admin.ts
│       ├── merchant.ts
│       ├── trader.ts
│       ├── support.ts
│       ├── teamlead.ts
│       ├── orders.ts          # IncomingOrder, OrderHistory
│       ├── balance.ts         # BalanceStore, BalanceTrader
│       └── common.ts          # Общие интерфейсы
```

#### 6.2 Замена mock данных на API хуки
- Создать хуки для каждого приложения в их папках hooks/
- Настроить loading и error состояния
- Обработка пагинации, фильтрации, сортировки

---

## 🎯 РЕЗУЛЬТАТ РЕФАКТОРИНГА

### До:
- admin_app: 6 страниц с hardcoded данными
- teamlead_app, support_app, trader_app, merchant_app: пустые структуры
- Отсутствие единой системы стилей
- Отсутствие системы прав
- Неиспользуемые компоненты в ui-kit

### После:
- **ui-kit**: 10 оптимизированных компонентов для ВСЕХ 5 приложений
- **permissions**: Система прав работает во всех приложениях
- **shared-pages**: Общие компоненты для admin/teamlead/support
- **admin_app**: Использует shared-pages с полными правами
- **teamlead_app**: Использует shared-pages с правами команды
- **support_app**: Использует shared-pages с правами поддержки
- **trader_app**: Уникальные страницы + локальные компоненты Button/Card
- **merchant_app**: Уникальные страницы для управления магазинами

### Преимущества:
1. **Единый дизайн**: ui-kit обеспечивает консистентность во всех 5 приложениях
2. **Переиспользование**: admin/teamlead/support используют общий код
3. **Специализация**: trader/merchant получают оптимизированные под роль страницы
4. **Гранулярные права**: каждый UI элемент контролируется системой прав
5. **Масштабируемость**: легкое добавление новых ролей и функций
6. **Подготовка к API**: все mock данные заменены на хуки
7. **Чистая архитектура**: удалены неиспользуемые компоненты, созданы локальные компоненты там где нужно

---

## ✅ КРИТЕРИИ ЗАВЕРШЕНИЯ

- [x] ui-kit стили используются во ВСЕХ 5 приложениях (0% hardcoded стилей)
- [x] ui-kit содержит только переиспользуемые компоненты (10 компонентов)
- [x] trader_app имеет локальные Button и Card компоненты
- [x] Соблюдение принципов монорепозитория: ui-kit для общих компонентов, локальные только при необходимости
- [ ] admin_app, teamlead_app, support_app используют shared-pages компоненты
- [ ] trader_app имеет уникальные страницы для работы с реквизитами и ордерами
- [ ] merchant_app имеет уникальные страницы для управления магазинами и отчетами
- [ ] Система прав покрывает все UI элементы во всех приложениях
- [ ] Mock данные заменены на API хуки во всех приложениях
- [ ] Все 5 приложений готовы к подключению бэкенд API
- [ ] Каждое приложение ≤ 30 строк кода на страницу (роутинг + компоненты)

**Дополнительные критерии соответствия бэкенду:**

**Функциональность трейдера:**
- [x] Демонстрационная страница с локальными компонентами Button/Card
- [ ] Управление реквизитами: создание, редактирование, статистика (requisite_service)
- [ ] Обработка ордеров: просмотр назначенных, подтверждение с загрузкой чека (confirm_order_by_trader)
- [ ] Балансы: текущие фиат/крипто балансы, история изменений (balance_manager)
- [ ] Переключатель трафика: отображение статуса is_traffic_enabled_by_teamlead

**Функциональность мерчанта:**
- [ ] CRUD магазинов: полное управление (merchant_service)
- [ ] Ордера: просмотр, создание, детали (get_orders_for_merchant, create_order_from_incoming)
- [ ] Интеграция: платежный шлюз, webhook, API ключи (gateway_service, callback_service)
- [ ] Отчеты: статистика, доходы, конверсия (get_merchants_statistics)

**Функциональность тимлида:**
- [ ] Управление командой: список трейдеров, изменение статусов (teamlead_service)
- [ ] Контроль трафика: управление is_traffic_enabled_by_teamlead для трейдеров
- [ ] Статистика команды: метрики работы команды (get_team_statistics)

**Система прав:**
- [ ] Wildcard поддержка: реализация логики как в permission_service._match_permission
- [ ] Специфика ролей: точное соответствие granted_permissions из бэкенда
- [ ] PermissionGuard: проверка прав для каждого UI элемента

**API интеграция:**
- [ ] Соответствие структуре backend/api_routers/
- [ ] Поддержка всех сервисных методов (trader_service, merchant_service, etc.)
- [ ] Типы данных соответствуют backend/schemas_enums/
