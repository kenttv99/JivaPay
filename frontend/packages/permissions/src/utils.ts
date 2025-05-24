import { UserPermissions, ROLE_PERMISSIONS, matchPermission } from './types';

// Получить права по умолчанию для роли
export const getDefaultPermissionsForRole = (role: UserPermissions['role']): string[] => {
  return [...(ROLE_PERMISSIONS[role] || [])];
};

// Проверить права пользователя без React Context (для утилит)
export const checkUserPermission = (
  userPermissions: UserPermissions | null,
  permission: string
): boolean => {
  if (!userPermissions) return false;
  return matchPermission(permission, userPermissions.grantedPermissions);
};

// Проверить любое из прав
export const checkAnyUserPermission = (
  userPermissions: UserPermissions | null,
  permissions: string[]
): boolean => {
  if (!userPermissions) return false;
  return permissions.some(permission => checkUserPermission(userPermissions, permission));
};

// Проверить все права
export const checkAllUserPermissions = (
  userPermissions: UserPermissions | null,
  permissions: string[]
): boolean => {
  if (!userPermissions) return false;
  return permissions.every(permission => checkUserPermission(userPermissions, permission));
};

// Проверить роль пользователя
export const checkUserRole = (
  userPermissions: UserPermissions | null,
  roles: UserPermissions['role'][]
): boolean => {
  if (!userPermissions) return false;
  return roles.includes(userPermissions.role);
};

// Проверить является ли пользователь администратором
export const isUserAdmin = (userPermissions: UserPermissions | null): boolean => {
  return userPermissions?.role === 'admin';
};

// Проверить является ли пользователь административной ролью
export const isUserAdminRole = (userPermissions: UserPermissions | null): boolean => {
  if (!userPermissions) return false;
  return ['admin', 'support', 'teamlead'].includes(userPermissions.role);
};

// Проверить является ли пользователь пользовательской ролью
export const isUserClientRole = (userPermissions: UserPermissions | null): boolean => {
  if (!userPermissions) return false;
  return ['merchant', 'trader'].includes(userPermissions.role);
};

// Получить отображаемое имя роли
export const getRoleDisplayName = (role: UserPermissions['role']): string => {
  const roleNames = {
    admin: 'Администратор',
    support: 'Поддержка',
    teamlead: 'Тимлид',
    merchant: 'Мерчант',
    trader: 'Трейдер'
  };
  
  return roleNames[role] || role;
};

// Валидация структуры прав
export const validatePermissionFormat = (permission: string): boolean => {
  const parts = permission.split(':');
  return parts.length === 3 && parts.every(part => part.length > 0);
};

// Валидация массива прав
export const validatePermissions = (permissions: string[]): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  permissions.forEach((permission, index) => {
    if (!validatePermissionFormat(permission)) {
      errors.push(`Неверный формат права ${index + 1}: "${permission}". Ожидается формат "resource:action:scope"`);
    }
  });
  
  return {
    valid: errors.length === 0,
    errors
  };
}; 