// Типы и константы
export type { 
  UserPermissions, 
  PermissionPattern 
} from './types';

export { 
  ROLE_PERMISSIONS, 
  parsePermission, 
  matchPermission 
} from './types';

// React Context
export { 
  PermissionProvider, 
  usePermissionContext 
} from './PermissionContext';

// Хук для работы с правами
export type { UsePermissionsReturn } from './usePermissions';
export { usePermissions } from './usePermissions';

// Компоненты защиты UI
export { 
  PermissionGuard, 
  AdminOnly, 
  AdminRolesOnly, 
  UserRolesOnly 
} from './PermissionGuard';

// Утилитарные функции
export {
  getDefaultPermissionsForRole,
  checkUserPermission,
  checkAnyUserPermission,
  checkAllUserPermissions,
  checkUserRole,
  isUserAdmin,
  isUserAdminRole,
  isUserClientRole,
  getRoleDisplayName,
  validatePermissionFormat,
  validatePermissions
} from './utils'; 