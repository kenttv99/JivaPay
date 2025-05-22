'use client';

import MainLayout from '@/layouts/MainLayout';
import { SettingsManagement } from '@/components/Settings/SettingsManagement';

// Симуляция системных настроек
const mockSystemSettings = {
  maintenance: false,
  registrationEnabled: true,
  maxTransactionLimit: 1000000,
  minTransactionAmount: 100,
  defaultCommission: 2.5,
  sessionTimeout: 60,
  apiRateLimit: 1000,
  notificationsEnabled: true
};

const mockSecuritySettings = {
  twoFactorRequired: true,
  passwordMinLength: 8,
  sessionExpiry: 1440,
  maxLoginAttempts: 5,
  ipWhitelistEnabled: false,
  auditLogRetention: 90
};

export default function SettingsPage() {
  return (
    <MainLayout>
      <SettingsManagement 
        systemSettings={mockSystemSettings}
        securitySettings={mockSecuritySettings}
        loading={false}
      />
    </MainLayout>
  );
} 