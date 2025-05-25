'use client';

import React from 'react';
import MainLayout from '@/layouts/MainLayout';
import { SettingsManagement } from '@/components/Settings/SettingsManagement';

export default function SettingsPage() {
  return (
    <MainLayout>
      <SettingsManagement />
    </MainLayout>
  );
} 