# @jivapay/shared-pages

Пакет переиспользуемых страниц и компонентов для административных приложений JivaPay (admin, teamlead, support).

## 🎯 Назначение

Этот пакет предоставляет:
- **Страницы**: Готовые страницы с адаптацией под роли пользователей
- **Компоненты**: Переиспользуемые компоненты для построения административных интерфейсов
- **Конфигурации**: Настройки прав доступа и отображения для каждой роли

## 📦 Структура

```
src/
├── pages/                          # Готовые страницы (7 шт.) ✅
│   ├── DashboardPage/              # ✅ Дашборд с метриками и адаптацией под роли
│   ├── UsersPage/                  # ✅ Управление пользователями всех ролей
│   ├── OrdersPage/                 # ✅ Централизованное управление ордерами
│   ├── FinancePage/                # ✅ Финансы, балансы, аналитика с вкладками
│   ├── AnalyticsPage/              # ✅ Аналитика ордеров, объемов, производительности
│   ├── StoresPage/                 # ✅ Управление магазинами мерчантов (только admin)
│   └── RequisitesPage/             # ✅ Управление реквизитами трейдеров
├── components/                      # Переиспользуемые компоненты (9 шт.) ✅
│   ├── MetricsGrid/                # ✅ Сетка метрик дашборда
│   ├── OrdersTable/                # ✅ Таблица ордеров с расширенной функциональностью
│   ├── UserManagement/             # ✅ Управление пользователями всех ролей
│   ├── OrderDetails/               # ✅ Детальная информация об ордере
│   ├── StoreManagement/            # ✅ Управление магазинами с CRUD операциями
│   ├── RequisiteManagement/        # ✅ Управление реквизитами с модерацией
│   ├── BalanceChart/               # ✅ SVG графики финансовой аналитики
│   ├── OrderChart/                 # ✅ SVG графики ордеров и статистики
│   └── PlatformMetrics/            # ✅ Метрики платформы и системы
└── configs/                        # Конфигурации ролей ✅
    └── roleConfigs.ts              # ✅ Расширенные настройки для admin/teamlead/support
```

**📝 Примечание**: Страница настроек (SettingsPage) исключена из shared-pages, так как настройки должны быть индивидуальными для каждого приложения.

## 🚀 Использование

### Базовая интеграция

```typescript
// В admin_app, teamlead_app, support_app
import { 
  DashboardPage, 
  UsersPage, 
  OrdersPage, 
  FinancePage,
  AnalyticsPage,
  RequisitesPage,
  StoresPage 
} from '@jivapay/shared-pages';

// Использование с автоматической адаптацией под роль
<DashboardPage 
  metricsData={metricsData}
  recentOrders={recentOrders}
  isLoading={isLoading}
/>

<FinancePage 
  balanceData={balanceData}
  platformMetrics={platformMetrics}
  isLoading={isLoading}
/>
```

### Конфигурации ролей

Все компоненты автоматически адаптируются под роль пользователя:

- **admin**: Полный доступ ко всем функциям, управление магазинами, системная аналитика
- **teamlead**: Управление командой трейдеров, модерация реквизитов, аналитика команды  
- **support**: Поддержка пользователей, просмотр проблемных ордеров, базовая аналитика

### Компоненты с расширенной функциональностью

```typescript
import { 
  MetricsGrid, 
  OrdersTable, 
  UserManagement,
  StoreManagement,
  RequisiteManagement,
  BalanceChart,
  OrderChart,
  PlatformMetrics
} from '@jivapay/shared-pages';

// Компонент метрик с адаптивными колонками
<MetricsGrid 
  metrics={metrics} 
  columns={4}
  showAdvanced={userRole === 'admin'}
  className="mb-8"
/>

// Таблица ордеров с фильтрацией и правами доступа
<OrdersTable
  orders={orders}
  showColumns={{
    trader: true,
    commissions: userRole === 'admin',
    store: true,
    crypto: true
  }}
  allowedActions={{
    view: true,
    edit: userRole !== 'support',
    assign: userRole === 'admin'
  }}
  onOrderSelect={handleOrderSelect}
/>

// Управление магазинами с CRUD операциями
<StoreManagement
  stores={stores}
  allowedActions={{
    view: true,
    edit: userRole === 'admin',
    delete: userRole === 'admin',
    block: userRole === 'admin',
    create: userRole === 'admin'
  }}
  onStoreAction={handleStoreAction}
/>

// SVG графики без внешних зависимостей
<BalanceChart
  data={balanceData}
  type="balance"
  title="Динамика балансов"
  height={400}
/>

<OrderChart
  data={orderData}
  type="orders"
  title="Статистика ордеров"
  height={350}
/>
```

## 🔐 Система прав

Все компоненты интегрированы с `@jivapay/permissions`:

```typescript
import { usePermissions } from '@jivapay/permissions';
import { DASHBOARD_CONFIGS, FINANCE_CONFIGS } from '@jivapay/shared-pages';

// Автоматическое получение роли и конфигурации
const { userRole } = usePermissions();
const role = userRole as UserRole; // 'admin' | 'teamlead' | 'support'

// Конфигурации адаптируются под роль
const dashboardConfig = DASHBOARD_CONFIGS[role];
const financeConfig = FINANCE_CONFIGS[role];
```

## 🎨 Стилизация

Все компоненты используют CSS переменные из `@jivapay/ui-kit`:

- **Цвета**: `--jiva-primary`, `--jiva-success`, `--jiva-error`, `--jiva-warning`, `--jiva-info`
- **Текст**: `--jiva-text`, `--jiva-text-secondary`
- **Фон**: `--jiva-background`, `--jiva-background-paper`
- **Границы**: `--jiva-border-light`
- **Статусы**: `--jiva-success-light`, `--jiva-error-light`, `--jiva-warning-light`

## 📊 Расширенные типы данных

### OrderItem (расширенный)
```typescript
interface OrderItem {
  id: string;
  date: string;
  user: string;
  amount: string;
  amount_crypto?: string;
  currency_crypto?: string;
  type: 'payin' | 'payout';
  status: 'completed' | 'processing' | 'pending' | 'canceled' | 'disputed' | 'failed';
  trader?: string | null;
  requisite?: string | null;
  store_commission?: string;
  trader_commission?: string;
  platform_commission?: string;
  store_name?: string;
  external_order_id?: string;
  processing_time?: string;
  assigned_to?: string;
}
```

### StoreItem
```typescript
interface StoreItem {
  id: string;
  name: string;
  merchant_name: string;
  status: 'active' | 'inactive' | 'blocked' | 'pending';
  created_date: string;
  total_revenue: string;
  total_orders: number;
  commission_rate: string;
  webhook_url?: string;
  last_transaction?: string;
}
```

### RequisiteItem
```typescript
interface RequisiteItem {
  id: string;
  trader_name: string;
  bank_name: string;
  card_number: string; // Маскированный
  status: 'active' | 'moderation' | 'blocked' | 'inactive';
  is_online: boolean;
  total_orders: number;
  success_rate: number;
  team_name?: string;
  last_used?: string;
  created_date: string;
  moderation_comment?: string;
}
```

### Chart Data Types
```typescript
interface BalanceChartData {
  date: string;
  balance: number;
  volume?: number;
  commission?: number;
  revenue?: number;
}

interface OrderChartData {
  date: string;
  total_orders: number;
  completed_orders: number;
  failed_orders: number;
  success_rate?: number;
  payin_count?: number;
  payout_count?: number;
}
```

## 🏗️ Архитектура

### Принципы проектирования

1. **Адаптивность под роли**: Каждый компонент автоматически адаптируется под права пользователя
2. **Переиспользование**: Один набор компонентов для всех административных приложений
3. **Безопасность**: Проверка прав доступа на уровне UI с интеграцией permissions
4. **Консистентность**: Единый дизайн и поведение во всех приложениях
5. **Масштабируемость**: Легкое добавление новых ролей и функций

### Интеграция с бэкендом

Компоненты готовы для интеграции с:
- `order_service.py` - централизованная система ордеров
- `user_service.py` - управление пользователями всех ролей
- `merchant_service.py` - управление магазинами мерчантов
- `trader_service.py` - управление реквизитами трейдеров
- `permission_service.py` - система прав доступа
- `balance_manager.py` - финансовая аналитика

### Уникальные возможности

- **SVG графики**: Собственные графики без внешних зависимостей (recharts, chart.js)
- **Вкладочная структура**: TabGroup для группировки функций
- **CRUD операции**: Полный набор операций для всех сущностей  
- **Модерация**: Системы одобрения/отклонения с комментариями
- **Статистика в реальном времени**: Метрики и аналитика с автообновлением

## ✅ Статус реализации - 100% ЗАВЕРШЕНО

**🎉 Страницы (7 из 7):**
- ✅ **DashboardPage** - дашборд с метриками, адаптация под роли, быстрые действия
- ✅ **UsersPage** - управление пользователями всех ролей с фильтрацией и статистикой
- ✅ **OrdersPage** - централизованное управление ордерами с назначением трейдеров
- ✅ **FinancePage** - финансы с вкладками: обзор, балансы, объемы, комиссии, доходы
- ✅ **AnalyticsPage** - аналитика ордеров, объемов, производительность системы
- ✅ **RequisitesPage** - управление реквизитами с модерацией и статистикой команды
- ✅ **StoresPage** - управление магазинами с топами, аналитикой, уведомлениями

**🎉 Компоненты (9 из 9):**
- ✅ **MetricsGrid** - переиспользуемые метрики с адаптивными колонками
- ✅ **OrdersTable** - таблица ордеров с расширенной функциональностью и правами
- ✅ **UserManagement** - полноценное управление пользователями всех ролей
- ✅ **OrderDetails** - детальный просмотр ордеров с изменением статуса
- ✅ **StoreManagement** - CRUD магазинов с статистикой и интеграционной информацией
- ✅ **RequisiteManagement** - модерация реквизитов с маскированными картами
- ✅ **BalanceChart** - SVG графики балансов, объемов, комиссий без зависимостей
- ✅ **OrderChart** - графики ордеров с градиентной заливкой и типами
- ✅ **PlatformMetrics** - метрики пользователей, операций, финансов, системы

**🎉 Конфигурации:**
- ✅ **DASHBOARD_CONFIGS** - конфигурации дашборда для каждой роли
- ✅ **ORDERS_CONFIGS** - конфигурации управления ордерами
- ✅ **USERS_CONFIGS** - конфигурации управления пользователями  
- ✅ **FINANCE_CONFIGS** - расширенные конфигурации финансов с новыми свойствами

## 🔄 Миграция административных приложений

Для миграции admin_app, teamlead_app, support_app:

1. **Замените страницы на импорты из shared-pages**:
```typescript
// Вместо локальных страниц
import { DashboardPage, UsersPage, FinancePage } from '@jivapay/shared-pages';
```

2. **Обновите props согласно новым интерфейсам**:
```typescript
<DashboardPage 
  metricsData={mockMetricsData}
  recentOrders={mockRecentOrders}
  isLoading={false}
/>
```

3. **Система прав подключится автоматически** через `usePermissions()`

4. **Стили адаптируются под CSS переменные ui-kit автоматически**

### Результат миграции:
- ⚡ **Сокращение кода**: Каждая страница ≤ 30 строк (роутинг + компоненты)
- 🎨 **Единый дизайн**: Консистентность во всех административных приложениях
- 🔐 **Безопасность**: Автоматическая проверка прав для каждого UI элемента
- 📱 **Адаптивность**: Автоматическая адаптация под роль пользователя

**🎉 ГОТОВО К СЕКЦИИ 5: МИГРАЦИЯ ВСЕХ ПРИЛОЖЕНИЙ** 