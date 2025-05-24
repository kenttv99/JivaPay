import React, { createContext, useContext, ReactNode } from 'react';
import { UserPermissions } from './types';

interface PermissionContextType {
  userPermissions: UserPermissions | null;
  isLoading: boolean;
  error: string | null;
}

const PermissionContext = createContext<PermissionContextType | undefined>(undefined);

interface PermissionProviderProps {
  value: UserPermissions | null;
  isLoading?: boolean;
  error?: string | null;
  children: ReactNode;
}

export const PermissionProvider: React.FC<PermissionProviderProps> = ({
  value,
  isLoading = false,
  error = null,
  children
}) => {
  const contextValue: PermissionContextType = {
    userPermissions: value,
    isLoading,
    error
  };

  return (
    <PermissionContext.Provider value={contextValue}>
      {children}
    </PermissionContext.Provider>
  );
};

export const usePermissionContext = (): PermissionContextType => {
  const context = useContext(PermissionContext);
  if (context === undefined) {
    throw new Error('usePermissionContext must be used within a PermissionProvider');
  }
  return context;
}; 