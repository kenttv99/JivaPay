'use client';

import React from 'react';
import { usePermissions } from '@jivapay/permissions';
import { MetricsGrid, MetricItem } from '../../components/MetricsGrid/MetricsGrid';
import { OrdersTable, OrderItem } from '../../components/OrdersTable/OrdersTable';
import { DASHBOARD_CONFIGS, ORDERS_CONFIGS, UserRole } from '../../configs/roleConfigs';

// Иконки (простые SVG компоненты)
const UsersIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
  </svg>
);

const StoresIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
  </svg>
);

const TransactionsIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const RevenueIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 8h6m-5 0a3 3 0 110 6H9l3 3m-3-6h6m6 1a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const OrdersIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
  </svg>
);

interface DashboardPageProps {
  // Mock данные для демонстрации - в реальности будут приходить из API хуков
  metricsData?: {
    activeUsers?: number;
    newStores?: number;
    transactionVolume?: string;
    revenue?: string;
    ordersInProgress?: number;
  };
  recentOrders?: OrderItem[];
  isLoading?: boolean;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  metricsData = {
    activeUsers: 2847,
    newStores: 28,
    transactionVolume: '₽ 4.2M',
    revenue: '₽ 127K',
    ordersInProgress: 142
  },
  recentOrders = [],
  isLoading = false
}) => {
  const { userRole } = usePermissions();
  const role = userRole as UserRole;
  
  // Получаем конфигурацию для текущей роли
  const dashboardConfig = DASHBOARD_CONFIGS[role];
  const ordersConfig = ORDERS_CONFIGS[role];

  if (!dashboardConfig) {
    return (
      <div className="p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-[var(--jiva-text)]">Доступ запрещен</h1>
          <p className="text-[var(--jiva-text-secondary)] mt-2">У вас нет прав для просмотра этой страницы</p>
        </div>
      </div>
    );
  }

  // Формируем метрики в зависимости от роли
  const getMetricsForRole = (): MetricItem[] => {
    const baseMetrics: MetricItem[] = [];

    // Активные пользователи (все роли)
    if (dashboardConfig.permissions.viewUsers) {
      baseMetrics.push({
        id: 'active-users',
        title: 'Активные пользователи',
        value: metricsData.activeUsers?.toString() || '0',
        change: '+12%',
        trend: 'up',
        subtitle: 'с прошлой недели',
        icon: <UsersIcon />,
        link: '/users',
        permission: dashboardConfig.permissions.viewUsers
      });
    }

    // Магазины (только admin)
    if (dashboardConfig.config.enableStoreManagement && 'viewStores' in dashboardConfig.permissions) {
      baseMetrics.push({
        id: 'new-stores',
        title: 'Новые магазины',
        value: metricsData.newStores?.toString() || '0',
        change: '+8%',
        trend: 'up',
        subtitle: 'с прошлой недели',
        icon: <StoresIcon />,
        link: '/stores',
        permission: dashboardConfig.permissions.viewStores
      });
    }

    // Объем транзакций
    if (dashboardConfig.permissions.viewOrders) {
      baseMetrics.push({
        id: 'transaction-volume',
        title: 'Объем транзакций',
        value: metricsData.transactionVolume || '₽ 0',
        change: '+17.5%',
        trend: 'up',
        subtitle: 'с прошлой недели',
        icon: <TransactionsIcon />,
        link: '/orders',
        permission: dashboardConfig.permissions.viewOrders
      });
    }

    // Доход с комиссий (admin и teamlead)
    if (dashboardConfig.config.showPlatformBalances && 'viewFinance' in dashboardConfig.permissions) {
      baseMetrics.push({
        id: 'revenue',
        title: 'Доход с комиссий',
        value: metricsData.revenue || '₽ 0',
        change: '+12.3%',
        trend: 'up',
        subtitle: 'с прошлой недели',
        icon: <RevenueIcon />,
        link: '/finance',
        permission: dashboardConfig.permissions.viewFinance
      });
    }

    // Ордера в процессе (все роли, но разный доступ)
    if (dashboardConfig.permissions.viewOrders) {
      baseMetrics.push({
        id: 'orders-progress',
        title: role === 'support' ? 'Назначенные ордера' : 'Ордера в обработке',
        value: metricsData.ordersInProgress?.toString() || '0',
        change: undefined,
        trend: 'neutral',
        subtitle: 'требуют внимания',
        icon: <OrdersIcon />,
        link: '/orders',
        permission: dashboardConfig.permissions.viewOrders
      });
    }

    return baseMetrics;
  };

  const metrics = getMetricsForRole();

  // Определяем количество колонок для метрик
  const getColumnsCount = () => {
    if (metrics.length <= 2) return 2;
    if (metrics.length === 3) return 3;
    return 4;
  };

  // Конфигурация показа колонок в таблице ордеров
  const getOrdersTableConfig = () => {
    return {
      trader: ordersConfig.filters.showTraderInfo,
      commissions: ordersConfig.filters.showCommissions,
      store: ordersConfig.filters.showStoreInfo,
      crypto: true, // всегда показываем крипто
      actions: false
    };
  };

  return (
    <div className="space-y-6">
      {/* Заголовок страницы */}
      <div>
        <h1 className="text-3xl font-bold text-[var(--jiva-text)]">
          {role === 'admin' ? 'Панель управления' : 
           role === 'teamlead' ? 'Панель тимлида' : 
           'Панель поддержки'}
        </h1>
        <p className="text-[var(--jiva-text-secondary)] mt-1">
          {role === 'admin' ? 'Добро пожаловать в административную панель JivaPay' :
           role === 'teamlead' ? 'Управление командой трейдеров' :
           'Поддержка пользователей и решение вопросов'}
        </p>
      </div>

      {/* Метрики */}
      <MetricsGrid 
        metrics={metrics} 
        columns={getColumnsCount()}
        className="mb-8"
      />

      {/* Недавние ордера */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-[var(--jiva-text)]">
            {role === 'support' ? 'Назначенные ордера' : 'Недавние ордера'}
          </h2>
          {dashboardConfig.config.enableExport && (
            <button className="text-sm text-[var(--jiva-primary)] hover:underline">
              Экспорт данных
            </button>
          )}
        </div>
        
        <OrdersTable
          orders={recentOrders}
          showColumns={getOrdersTableConfig()}
          isLoading={isLoading}
          className="border-t border-[var(--jiva-border-light)]"
        />
        
        {recentOrders.length > 0 && (
          <div className="mt-4 text-center">
            <a href="/orders" className="text-sm text-[var(--jiva-primary)] hover:underline">
              Показать все ордера →
            </a>
          </div>
        )}
      </div>

      {/* Дополнительная информация для админов */}
      {role === 'admin' && dashboardConfig.config.showAdvancedMetrics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">Статистика платежей</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">Успешные</span>
                  <span className="text-sm text-[var(--jiva-text-secondary)]">82%</span>
                </div>
                <div className="w-full bg-[var(--jiva-border-light)] rounded-full h-2">
                  <div 
                    className="bg-[var(--jiva-success)] h-2 rounded-full" 
                    style={{ width: '82%' }}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">В процессе</span>
                  <span className="text-sm text-[var(--jiva-text-secondary)]">12%</span>
                </div>
                <div className="w-full bg-[var(--jiva-border-light)] rounded-full h-2">
                  <div 
                    className="bg-[var(--jiva-info)] h-2 rounded-full" 
                    style={{ width: '12%' }}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">Неудачные</span>
                  <span className="text-sm text-[var(--jiva-text-secondary)]">6%</span>
                </div>
                <div className="w-full bg-[var(--jiva-border-light)] rounded-full h-2">
                  <div 
                    className="bg-[var(--jiva-error)] h-2 rounded-full" 
                    style={{ width: '6%' }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">Распределение по методам</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm">Банковские карты</span>
                <span className="text-sm font-medium">65%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Электронные кошельки</span>
                <span className="text-sm font-medium">24%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Криптовалюты</span>
                <span className="text-sm font-medium">8%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Другие</span>
                <span className="text-sm font-medium">3%</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 