import React, { ReactNode } from 'react';
import { usePermissions } from './usePermissions';

interface PermissionGuardProps {
  // Права доступа
  permission?: string;
  permissions?: string[];
  requireAll?: boolean; // true = AND логика, false = OR логика
  
  // Роли
  roles?: ('admin' | 'support' | 'teamlead' | 'merchant' | 'trader')[];
  
  // Контент
  children: ReactNode;
  fallback?: ReactNode;
  
  // Инвертирование логики (показать если НЕТ права)
  invert?: boolean;
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  permission,
  permissions,
  requireAll = false,
  roles,
  children,
  fallback = null,
  invert = false
}) => {
  const { 
    hasPermission, 
    hasAnyPermission, 
    hasAllPermissions, 
    userRole,
    isLoading,
    error 
  } = usePermissions();

  // Показываем fallback если загрузка или ошибка
  if (isLoading || error) {
    return <>{fallback}</>;
  }

  let hasAccess = false;

  // Проверка ролей
  if (roles && roles.length > 0) {
    hasAccess = userRole ? roles.includes(userRole as any) : false;
  }
  // Проверка одного права
  else if (permission) {
    hasAccess = hasPermission(permission);
  }
  // Проверка множественных прав
  else if (permissions && permissions.length > 0) {
    hasAccess = requireAll 
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions);
  }
  // Если ничего не указано, показываем контент
  else {
    hasAccess = true;
  }

  // Инвертирование логики
  if (invert) {
    hasAccess = !hasAccess;
  }

  return hasAccess ? <>{children}</> : <>{fallback}</>;
};

// Компонент для показа контента только администраторам
export const AdminOnly: React.FC<{ children: ReactNode; fallback?: ReactNode }> = ({
  children,
  fallback = null
}) => (
  <PermissionGuard roles={['admin']} fallback={fallback}>
    {children}
  </PermissionGuard>
);

// Компонент для показа контента только административным ролям
export const AdminRolesOnly: React.FC<{ children: ReactNode; fallback?: ReactNode }> = ({
  children,
  fallback = null
}) => (
  <PermissionGuard roles={['admin', 'support', 'teamlead']} fallback={fallback}>
    {children}
  </PermissionGuard>
);

// Компонент для показа контента только пользовательским ролям
export const UserRolesOnly: React.FC<{ children: ReactNode; fallback?: ReactNode }> = ({
  children,
  fallback = null
}) => (
  <PermissionGuard roles={['merchant', 'trader']} fallback={fallback}>
    {children}
  </PermissionGuard>
); 