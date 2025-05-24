# @jivapay/permissions

Централизованная система прав доступа для всех приложений JivaPay.

## 📋 Обзор

Этот пакет предоставляет единую систему управления правами пользователей для всех приложений монорепозитория JivaPay:
- `admin_app` - панель администратора
- `trader_app` - интерфейс трейдера
- `merchant_app` - кабинет мерчанта  
- `support_app` - панель поддержки
- `teamlead_app` - интерфейс тимлида

## 🚀 Установка

Пакет устанавливается автоматически как workspace dependency во всех приложениях:

```json
{
  "dependencies": {
    "@jivapay/permissions": "*"
  }
}
```

## 🔑 Роли и права

### Поддерживаемые роли:
- `admin` - полный доступ ко всем функциям
- `support` - работа с назначенными пользователями и тикетами
- `teamlead` - управление командой трейдеров
- `merchant` - управление платежами и заказами
- `trader` - обработка ордеров и управление реквизитами

### Формат прав: `resource:action:scope`

**Примеры прав:**
```typescript
'users:view:assigned'           // Просмотр назначенных пользователей
'orders:edit:team'              // Редактирование ордеров команды  
'balance:view:own'              // Просмотр собственного баланса
'*:*:*'                         // Полный доступ (только admin)
```

## 📚 API

### Основные компоненты

#### PermissionProvider
Корневой провайдер для передачи прав в контексте React:

```tsx
import { PermissionProvider } from '@jivapay/permissions';

<PermissionProvider 
  value={userPermissions}
  isLoading={false}
  error={null}
>
  <App />
</PermissionProvider>
```

#### usePermissions
Хук для работы с правами пользователя:

```tsx
import { usePermissions } from '@jivapay/permissions';

const MyComponent = () => {
  const { 
    userRole,
    hasPermission, 
    hasAnyPermission,
    hasAllPermissions,
    isAdmin,
    isTrader,
    grantedPermissions 
  } = usePermissions();

  if (hasPermission('orders:view:own')) {
    // Показать ордера
  }
};
```

#### PermissionGuard
Компонент для условного рендеринга на основе прав:

```tsx
import { PermissionGuard } from '@jivapay/permissions';

// Простая проверка права
<PermissionGuard permission="users:edit:own">
  <EditUserForm />
</PermissionGuard>

// Проверка нескольких прав (OR логика)
<PermissionGuard 
  permissions={["admin:*:*", "support:*:*"]}
  fallback={<div>Доступ запрещен</div>}
>
  <AdminPanel />
</PermissionGuard>

// Проверка всех прав (AND логика)
<PermissionGuard 
  permissions={["balance:view:own", "balance:edit:own"]}
  requireAll={true}
>
  <BalanceEditor />
</PermissionGuard>

// Проверка ролей
<PermissionGuard roles={["admin", "teamlead"]}>
  <TeamManagement />
</PermissionGuard>
```

### Готовые компоненты

#### AdminOnly / AdminRolesOnly / UserRolesOnly
Предустановленные компоненты для частых случаев:

```tsx
import { AdminOnly, AdminRolesOnly, UserRolesOnly } from '@jivapay/permissions';

<AdminOnly>
  <SuperAdminPanel />
</AdminOnly>

<AdminRolesOnly>
  <AdminSupportPanel />
</AdminRolesOnly>

<UserRolesOnly>
  <ClientInterface />
</UserRolesOnly>
```

### Утилитарные функции

```tsx
import { 
  checkUserPermission,
  getDefaultPermissionsForRole,
  isUserAdmin,
  getRoleDisplayName 
} from '@jivapay/permissions';

// Проверка прав без React контекста
const canEdit = checkUserPermission(user, 'orders:edit:own');

// Получение прав по умолчанию для роли
const traderPermissions = getDefaultPermissionsForRole('trader');

// Проверка роли
const isAdmin = isUserAdmin(user);

// Отображаемое имя роли
const roleName = getRoleDisplayName('teamlead'); // "Тимлид"
```

## 🛠 Интеграция в приложения

### 1. Создание провайдера для приложения

```tsx
// src/providers/AppPermissionProvider.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { PermissionProvider, UserPermissions } from '@jivapay/permissions';

export const AppPermissionProvider = ({ children }) => {
  const [userPermissions, setUserPermissions] = useState<UserPermissions | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPermissions = async () => {
      try {
        // Загрузка прав с API
        const response = await fetch('/api/auth/me');
        const userData = await response.json();
        
        setUserPermissions({
          userId: userData.id,
          role: userData.role,
          grantedPermissions: userData.granted_permissions
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    loadPermissions();
  }, []);

  return (
    <PermissionProvider 
      value={userPermissions}
      isLoading={isLoading}
      error={error}
    >
      {children}
    </PermissionProvider>
  );
};
```

### 2. Подключение в корневом layout

```tsx
// app/layout.tsx или pages/_app.tsx
import { AppPermissionProvider } from '@/providers/AppPermissionProvider';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <AppPermissionProvider>
          {children}
        </AppPermissionProvider>
      </body>
    </html>
  );
}
```

### 3. Использование в компонентах

```tsx
// components/Dashboard.tsx
import { PermissionGuard, usePermissions } from '@jivapay/permissions';

const Dashboard = () => {
  const { userRole, hasPermission } = usePermissions();

  return (
    <div>
      <h1>Панель {userRole}</h1>
      
      <PermissionGuard permission="dashboard:view:own">
        <MetricsWidget />
      </PermissionGuard>

      <PermissionGuard permission="orders:view:assigned">
        <OrdersTable />
      </PermissionGuard>

      {hasPermission('admin:*:*') && (
        <AdminControls />
      )}
    </div>
  );
};
```

## 🎯 Примеры по ролям

### Admin (администратор)
```tsx
// Полный доступ ко всему
const permissions = ['*:*:*'];

<PermissionGuard permission="*:*:*">
  <FullAdminPanel />
</PermissionGuard>
```

### Trader (трейдер)
```tsx
const permissions = [
  'requisites:manage:own',
  'orders:view:assigned', 
  'orders:process:assigned',
  'balance:view:own',
  'dashboard:view:own'
];

<PermissionGuard permission="requisites:manage:own">
  <RequisitesManager />
</PermissionGuard>

<PermissionGuard permission="balance:view:own">
  <BalanceInfo />
</PermissionGuard>
```

### Merchant (мерчант)
```tsx
const permissions = [
  'orders:view:own',
  'merchant:payments:manage',
  'merchant:balance:view',
  'merchant:withdraw:create'
];

<PermissionGuard permission="merchant:payments:manage">
  <PaymentSettings />
</PermissionGuard>
```

### Support (поддержка)
```tsx
const permissions = [
  'users:view:assigned',
  'tickets:manage:own',
  'orders:view:assigned'
];

<PermissionGuard permission="tickets:manage:own">
  <TicketSystem />
</PermissionGuard>
```

### TeamLead (тимлид)
```tsx
const permissions = [
  'users:view:team',
  'trader:manage:team',
  'statistics:view:team'
];

<PermissionGuard permission="trader:manage:team">
  <TeamManagement />
</PermissionGuard>
```

## 🔍 Отладка

Добавьте отладочную панель для разработки:

```tsx
const DebugPanel = () => {
  const { userRole, grantedPermissions, hasPermission } = usePermissions();
  
  return (
    <details className="debug-panel">
      <summary>🔍 Права пользователя</summary>
      <div>
        <p>Роль: {userRole}</p>
        <p>Права: {grantedPermissions.join(', ')}</p>
        <p>admin:*:*: {hasPermission('admin:*:*') ? '✅' : '❌'}</p>
      </div>
    </details>
  );
};
```

## 🚦 Состояния загрузки

```tsx
const MyComponent = () => {
  const { isLoading, error } = usePermissions();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage error={error} />;
  }

  return <MainContent />;
};
```

## 🔒 Безопасность

⚠️ **Важно**: Проверка прав на frontend служит только для UX. Все критичные проверки должны выполняться на backend!

Эта система прав предназначена для:
- Скрытия/показа UI элементов
- Улучшения пользовательского опыта
- Предотвращения случайных действий

НЕ полагайтесь на frontend права для:
- Защиты конфиденциальных данных
- Предотвращения несанкционированных операций
- Контроля доступа к API

## 📝 Changelog

### v1.0.0 (текущая)
- ✅ Создана базовая архитектура системы прав
- ✅ Реализованы все основные компоненты
- ✅ Добавлена поддержка всех ролей JivaPay
- ✅ Созданы провайдеры для всех приложений
- ✅ Документация и примеры

## 🤝 Интеграция с Backend

Система ожидает следующий формат данных от API `/api/auth/me`:

```json
{
  "id": 123,
  "role": "trader",
  "granted_permissions": [
    "requisites:manage:own",
    "orders:view:assigned",
    "balance:view:own"
  ]
}
```

Соответствует backend структуре:
- `backend/services/permission_service.py`
- `backend/models/user.py` (поле `granted_permissions`)

## 📞 Поддержка

При возникновении вопросов или проблем:
1. Проверьте данное README
2. Изучите примеры в `trader_app/src/app/page.tsx`
3. Обратитесь к команде разработки 