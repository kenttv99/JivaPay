# @jivapay/permissions - Краткий обзор

## 🎯 Назначение
Централизованная система прав доступа для всех 5 приложений JivaPay монорепозитория.

## ✅ Текущий статус: ГОТОВ К ИСПОЛЬЗОВАНИЮ

### 📦 Поддерживаемые приложения:
- `admin_app` - панель администратора
- `trader_app` - интерфейс трейдера (+ демонстрация)
- `merchant_app` - кабинет мерчанта
- `support_app` - панель поддержки
- `teamlead_app` - интерфейс тимлида

### 🔑 Роли и основные права:
```typescript
admin: ['*:*:*']                               // Полный доступ
support: ['users:view:assigned', 'tickets:manage:own', ...]
teamlead: ['users:view:team', 'trader:manage:team', ...]
merchant: ['orders:view:own', 'merchant:payments:manage', ...]
trader: ['requisites:manage:own', 'orders:process:assigned', ...]
```

## 🚀 Быстрый старт

### 1. В провайдере приложения:
```tsx
import { AppPermissionProvider } from '@/providers/AppPermissionProvider';

<AppPermissionProvider>
  <YourApp />
</AppPermissionProvider>
```

### 2. В компонентах:
```tsx
import { PermissionGuard, usePermissions } from '@jivapay/permissions';

// Защита UI элементов
<PermissionGuard permission="orders:view:own">
  <OrdersTable />
</PermissionGuard>

// Программная проверка
const { hasPermission } = usePermissions();
if (hasPermission('admin:*:*')) {
  // Логика для админа
}
```

## 📁 Структура пакета:
```
packages/permissions/
├── src/
│   ├── index.ts              # Главный экспорт
│   ├── types.ts              # Типы и константы прав
│   ├── PermissionContext.tsx # React Context
│   ├── usePermissions.ts     # Хук для работы с правами
│   ├── PermissionGuard.tsx   # Компонент защиты UI
│   └── utils.ts              # Утилиты
├── README.md                 # Полная документация
└── SUMMARY.md                # Этот файл
```

## 🎨 Интеграция с ui-kit:
- ✅ Совместимость со всеми компонентами ui-kit
- ✅ Поддержка PermissionGuard для любых React элементов
- ✅ Стилизация через CSS переменные ui-kit

## 🔍 Демонстрация:
Рабочий пример в `trader_app/src/app/page.tsx` показывает:
- Условный рендеринг секций по правам
- Отладочную панель с проверкой прав
- Различные сценарии использования PermissionGuard

## 🛠 API Интеграция:
Провайдеры готовы к подключению реального API:
```typescript
// В AppPermissionProvider.tsx замените mock данные на:
const response = await fetch('/api/auth/me');
const userData = await response.json();
```

## 🔒 Безопасность:
⚠️ **Важно**: Система предназначена только для UX улучшений.  
Все критичные проверки безопасности должны выполняться на backend!

## 📚 Документация:
- Полная документация: `packages/permissions/README.md`
- Примеры использования: `trader_app/src/app/page.tsx`
- API reference: все экспорты в `packages/permissions/src/index.ts` 