'use client';

import { ReactNode } from 'react';
import { AppPermissionProvider } from './AppPermissionProvider';

interface ClientProvidersProps {
  children: ReactNode;
}

export const ClientProviders: React.FC<ClientProvidersProps> = ({ children }) => {
  return (
    <AppPermissionProvider>
      {children}
    </AppPermissionProvider>
  );
}; 