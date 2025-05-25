'use client';

import React, { ReactNode } from 'react';
import { PermissionProvider } from '@jivapay/permissions';
import type { UserPermissions } from '@jivapay/permissions';

interface PermissionProviderWrapperProps {
  children: ReactNode;
}

// Мок-данные для демонстрации
const mockAdminPermissions: UserPermissions = {
  userId: 1,
  role: 'admin',
  grantedPermissions: ['*:*:*'] // Полный доступ для админа
};

export default function PermissionProviderWrapper({ children }: PermissionProviderWrapperProps) {
  // В реальном приложении здесь будет загрузка permissions из API
  // const { data: userPermissions, isLoading, error } = useUserPermissions();
  
  return (
    <PermissionProvider 
      value={mockAdminPermissions}
      isLoading={false}
      error={null}
    >
      {children}
    </PermissionProvider>
  );
} 