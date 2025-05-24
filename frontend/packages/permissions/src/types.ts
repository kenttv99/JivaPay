// TypeScript типы для системы прав JivaPay
// Соответствует backend/services/permission_service.py

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
} as const;

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