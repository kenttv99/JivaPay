'use client';

import React from 'react';
import { DashboardPage } from '@jivapay/shared-pages';
import { mockRecentOrders, mockMetricsData } from '@/lib/mockData';
import MainLayout from '@/layouts/MainLayout';

export default function DashboardDemoPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-[var(--jiva-text)] mb-2">
            🚀 Демонстрация shared-pages
          </h1>
          <p className="text-[var(--jiva-text-secondary)]">
            Эта страница демонстрирует работу DashboardPage из пакета @jivapay/shared-pages. 
            Содержимое адаптируется под роль пользователя (admin/teamlead/support).
          </p>
        </div>

        <DashboardPage 
          metricsData={mockMetricsData}
          recentOrders={mockRecentOrders}
          isLoading={false}
        />
      </div>
    </MainLayout>
  );
} 