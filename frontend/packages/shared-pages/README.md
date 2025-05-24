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
├── pages/                          # Готовые страницы
│   ├── DashboardPage/              # ✅ Дашборд с метриками
│   ├── UsersPage/                  # ✅ Управление пользователями
│   ├── OrdersPage/                 # ✅ Управление ордерами
│   ├── FinancePage/                # ⏳ Финансы и балансы
│   ├── AnalyticsPage/              # ⏳ Аналитика и отчеты
│   ├── StoresPage/                 # ⏳ Управление магазинами
│   ├── RequisitesPage/             # ⏳ Управление реквизитами
│   └── SettingsPage/               # ⏳ Системные настройки
├── components/                      # Переиспользуемые компоненты
│   ├── MetricsGrid/                # ✅ Сетка метрик
│   ├── OrdersTable/                # ✅ Таблица ордеров
│   ├── UserManagement/             # ✅ Управление пользователями
│   ├── OrderDetails/               # ⏳ Детали ордера
│   ├── StoreManagement/            # ⏳ Управление магазинами
│   ├── RequisiteManagement/        # ⏳ Управление реквизитами
│   ├── BalanceChart/               # ⏳ Графики балансов
│   ├── OrderChart/                 # ⏳ Графики ордеров
│   └── PlatformMetrics/            # ⏳ Метрики платформы
└── configs/                        # Конфигурации ролей
    └── roleConfigs.ts              # ✅ Настройки для admin/teamlead/support
```

## 🚀 Использование

### Базовая интеграция

```typescript
// В admin_app, teamlead_app, support_app
import { DashboardPage, UsersPage, OrdersPage } from '@jivapay/shared-pages';

// Использование с автоматической адаптацией под роль
<DashboardPage 
  metricsData={metricsData}
  recentOrders={recentOrders}
  isLoading={isLoading}
/>
```

### Конфигурации ролей

Все компоненты автоматически адаптируются под роль пользователя:

- **admin**: Полный доступ ко всем функциям
- **teamlead**: Управление командой трейдеров
- **support**: Поддержка пользователей и проблемных ордеров

### Компоненты

```typescript
import { 
  MetricsGrid, 
  OrdersTable, 
  UserManagement 
} from '@jivapay/shared-pages';

// Компонент метрик с адаптивными колонками
<MetricsGrid 
  metrics={metrics} 
  columns={4}
  className="mb-8"
/>

// Таблица ордеров с настраиваемыми колонками
<OrdersTable
  orders={orders}
  showColumns={{
    trader: true,
    commissions: false,
    store: true,
    crypto: true
  }}
  onOrderSelect={handleOrderSelect}
/>

// Управление пользователями с правами доступа
<UserManagement
  users={users}
  allowedActions={{
    view: true,
    edit: true,
    delete: false,
    block: true
  }}
  showColumns={{
    team: true,
    balances: false,
    statistics: true
  }}
  onUserAction={handleUserAction}
/>
```

## 🔐 Система прав

Все компоненты интегрированы с `@jivapay/permissions`:

```typescript
import { usePermissions } from '@jivapay/permissions';

// Автоматическое получение роли и прав
const { userRole } = usePermissions();
const role = userRole as UserRole; // 'admin' | 'teamlead' | 'support'

// Компоненты сами определят доступные функции
```

## 🎨 Стилизация

Все компоненты используют CSS переменные из `@jivapay/ui-kit`:

- `--jiva-primary`, `--jiva-success`, `--jiva-error`
- `--jiva-text`, `--jiva-text-secondary`
- `--jiva-background`, `--jiva-background-paper`
- `--jiva-border-light`

## 📊 Типы данных

### OrderItem
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
  store_name?: string;
  external_order_id?: string;
}
```

### UserItem
```typescript
interface UserItem {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'support' | 'teamlead' | 'merchant' | 'trader';
  status: 'active' | 'inactive' | 'blocked' | 'pending';
  created_date: string;
  last_active?: string;
  team_id?: string;
  merchant_store_count?: number;
  trader_requisite_count?: number;
  total_orders?: number;
  balance_fiat?: string;
  balance_crypto?: string;
}
```

## 🏗️ Архитектура

### Принципы проектирования

1. **Адаптивность под роли**: Каждый компонент автоматически адаптируется
2. **Переиспользование**: Один компонент для всех административных приложений
3. **Безопасность**: Проверка прав доступа на уровне UI
4. **Консистентность**: Единый дизайн и поведение

### Интеграция с бэкендом

Компоненты готовы для интеграции с:
- `order_service.py` - централизованная система ордеров
- `user_service.py` - управление пользователями
- `permission_service.py` - система прав доступа

## ✅ Статус реализации

**Готово (50%):**
- ✅ DashboardPage - дашборд с метриками и адаптацией под роли
- ✅ UsersPage - управление пользователями с фильтрацией
- ✅ OrdersPage - централизованное управление ордерами
- ✅ MetricsGrid - переиспользуемые метрики
- ✅ OrdersTable - таблица ордеров с расширенной функциональностью
- ✅ UserManagement - полноценное управление пользователями

**В планах:**
- ⏳ FinancePage - управление балансами и комиссиями
- ⏳ AnalyticsPage - расширенная аналитика и отчеты
- ⏳ StoresPage - управление магазинами мерчантов
- ⏳ RequisitesPage - управление реквизитами трейдеров
- ⏳ Дополнительные компоненты (Charts, Details, Management)

## 🔄 Миграция

Для миграции существующих страниц:

1. Замените существующие компоненты на импорты из shared-pages
2. Обновите props согласно новым интерфейсам
3. Система прав подключится автоматически
4. Стили адаптируются под CSS переменные ui-kit 