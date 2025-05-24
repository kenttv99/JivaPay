import { useCallback } from 'react';
import { usePermissionContext } from './PermissionContext';
import { matchPermission } from './types';

export interface UsePermissionsReturn {
  userRole: string | null;
  userId: number | null;
  grantedPermissions: string[];
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
  isAdmin: boolean;
  isSupport: boolean;
  isTeamLead: boolean;
  isMerchant: boolean;
  isTrader: boolean;
  isLoading: boolean;
  error: string | null;
}

export const usePermissions = (): UsePermissionsReturn => {
  const { userPermissions, isLoading, error } = usePermissionContext();

  const grantedPermissions = userPermissions?.grantedPermissions || [];
  const userRole = userPermissions?.role || null;
  const userId = userPermissions?.userId || null;

  // Проверка одного права
  const hasPermission = useCallback((permission: string): boolean => {
    if (!userPermissions) return false;
    return matchPermission(permission, grantedPermissions);
  }, [userPermissions, grantedPermissions]);

  // Проверка любого из прав (OR логика)
  const hasAnyPermission = useCallback((permissions: string[]): boolean => {
    if (!userPermissions) return false;
    return permissions.some(permission => hasPermission(permission));
  }, [userPermissions, hasPermission]);

  // Проверка всех прав (AND логика)
  const hasAllPermissions = useCallback((permissions: string[]): boolean => {
    if (!userPermissions) return false;
    return permissions.every(permission => hasPermission(permission));
  }, [userPermissions, hasPermission]);

  // Проверки ролей
  const isAdmin = userRole === 'admin';
  const isSupport = userRole === 'support';
  const isTeamLead = userRole === 'teamlead';
  const isMerchant = userRole === 'merchant';
  const isTrader = userRole === 'trader';

  return {
    userRole,
    userId,
    grantedPermissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isAdmin,
    isSupport,
    isTeamLead,
    isMerchant,
    isTrader,
    isLoading,
    error
  };
}; 