'use client';

import React, { useState, useEffect, ReactNode } from 'react';
import { PermissionProvider, UserPermissions } from '@jivapay/permissions';

interface AppPermissionProviderProps {
  children: ReactNode;
}

export const AppPermissionProvider: React.FC<AppPermissionProviderProps> = ({ children }) => {
  const [userPermissions, setUserPermissions] = useState<UserPermissions | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPermissions = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // TODO: Заменить на реальный API endpoint
        // const response = await fetch('/api/auth/me', {
        //   credentials: 'include',
        //   headers: {
        //     'Content-Type': 'application/json',
        //   }
        // });

        // Mock данные для демонстрации (удалить после интеграции с API)
        await new Promise(resolve => setTimeout(resolve, 450)); // Имитация загрузки
        
        const mockUserData = {
          id: 321,
          role: 'teamlead' as const,
          granted_permissions: [
            'users:view:team',
            'orders:view:team',
            'trader:manage:team',
            'trader:traffic:team',        // is_traffic_enabled_by_teamlead
            'statistics:view:team',
            'teamlead:reports:manage',
            'teamlead:assignments:manage',
            'dashboard:view:team',
            'profile:manage:own'
          ],
        };

        setUserPermissions({
          userId: mockUserData.id,
          role: mockUserData.role,
          grantedPermissions: mockUserData.granted_permissions
        });

      } catch (err) {
        console.error('Failed to load user permissions:', err);
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
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