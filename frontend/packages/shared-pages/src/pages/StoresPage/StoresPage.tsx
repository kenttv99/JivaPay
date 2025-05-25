'use client';

import React, { useState } from 'react';
import { usePermissions } from '@jivapay/permissions';
import { StoreManagement, StoreItem } from '../../components/StoreManagement/StoreManagement';
import { DASHBOARD_CONFIGS, UserRole } from '../../configs/roleConfigs';

interface StoresPageProps {
  // Mock данные для демонстрации - в реальности будут приходить из API хуков
  storesData?: StoreItem[];
  isLoading?: boolean;
}

export const StoresPage: React.FC<StoresPageProps> = ({
  storesData = [],
  isLoading = false
}) => {
  const { userRole } = usePermissions();
  const role = userRole as UserRole;
  
  // Получаем конфигурацию для текущей роли
  const dashboardConfig = DASHBOARD_CONFIGS[role];

  if (!dashboardConfig || !dashboardConfig.config.enableStoreManagement) {
    return (
      <div className="p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-primary">Доступ запрещен</h1>
          <p className="text-secondary mt-2">У вас нет прав для управления магазинами</p>
        </div>
      </div>
    );
  }

  // Конфигурация действий (только для админов)
  const getActionConfig = () => {
    if (role === 'admin') {
      return {
        view: true,
        edit: true,
        delete: true,
        block: true,
        create: true
      };
    }
    return {
      view: true,
      edit: false,
      delete: false,
      block: false,
      create: false
    };
  };

  // Конфигурация отображаемых колонок
  const getColumnConfig = () => {
    return {
      merchant: true,
      revenue: true,
      commission: role === 'admin',
      webhook: role === 'admin',
      lastActive: true
    };
  };

  const handleStoreAction = (action: string, store: StoreItem) => {
    console.log(`Action: ${action}`, store);
    // Здесь будет вызов API в реальном приложении
    switch (action) {
      case 'edit':
        console.log(`Редактирование магазина ${store.id}`);
        break;
      case 'block':
        console.log(`Блокировка магазина ${store.id}`);
        break;
      case 'unblock':
        console.log(`Разблокировка магазина ${store.id}`);
        break;
      case 'delete':
        console.log(`Удаление магазина ${store.id}`);
        break;
    }
  };

  const handleCreateStore = () => {
    console.log('Создание нового магазина');
    // Здесь будет редирект на страницу создания магазина
  };

  // Статистика магазинов
  const getStoreStats = () => {
    const totalCount = storesData.length;
    const activeCount = storesData.filter(store => store.status === 'active').length;
    const inactiveCount = storesData.filter(store => store.status === 'inactive').length;
    const blockedCount = storesData.filter(store => store.status === 'blocked').length;
    const pendingCount = storesData.filter(store => store.status === 'pending').length;
    
    const totalRevenue = storesData.reduce((sum, store) => {
      const revenue = parseFloat(store.total_revenue.replace(/[^\d.-]/g, '')) || 0;
      return sum + revenue;
    }, 0);

    const totalOrders = storesData.reduce((sum, store) => sum + store.total_orders, 0);

    return {
      totalCount,
      activeCount,
      inactiveCount,
      blockedCount,
      pendingCount,
      totalRevenue,
      totalOrders
    };
  };

  const stats = getStoreStats();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <div className="text-secondary">Загрузка магазинов...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Заголовок страницы */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-primary">
            Управление магазинами
          </h1>
          <p className="text-secondary mt-1">
            {role === 'admin' ? 'Полное управление всеми магазинами системы' :
             'Управление собственными магазинами'}
          </p>
        </div>

        {dashboardConfig.config.enableExport && (
          <button className="bg-accent text-white px-4 py-2 rounded-lg hover:opacity-90">
            Экспорт данных
          </button>
        )}
      </div>

      {/* Статистика магазинов */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-surface rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2">Всего магазинов</h3>
          <div className="text-2xl font-bold text-accent">
            {stats.totalCount}
          </div>
          <div className="text-sm text-secondary">
            Зарегистрировано в системе
          </div>
        </div>

        <div className="bg-surface rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2">Активные</h3>
          <div className="text-2xl font-bold text-success">
            {stats.activeCount}
          </div>
          <div className="text-sm text-secondary">
            Принимают платежи
          </div>
        </div>

        <div className="bg-surface rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2">На модерации</h3>
          <div className="text-2xl font-bold text-warning">
            {stats.pendingCount}
          </div>
          <div className="text-sm text-secondary">
            Требуют проверки
          </div>
        </div>

        <div className="bg-surface rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2">Аналитика</h3>
          <div className="text-2xl font-bold text-info">
            {stats.totalOrders.toLocaleString()}
          </div>
          <div className="text-sm text-secondary">
            Всего ордеров
          </div>
        </div>
      </div>

      {/* Детальная статистика статусов */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-xl font-bold text-success">
            {stats.activeCount}
          </div>
          <div className="text-sm text-secondary">
            Активные
          </div>
        </div>

        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-xl font-bold text-warning">
            {stats.pendingCount}
          </div>
          <div className="text-sm text-secondary">
            Ожидают модерации
          </div>
        </div>

        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-xl font-bold text-secondary">
            {stats.inactiveCount}
          </div>
          <div className="text-sm text-secondary">
            Неактивные
          </div>
        </div>

        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-xl font-bold text-error">
            {stats.blockedCount}
          </div>
          <div className="text-sm text-secondary">
            Заблокированные
          </div>
        </div>
      </div>

      {/* Управление магазинами */}
      <StoreManagement
        stores={storesData}
        allowedActions={getActionConfig()}
        showColumns={getColumnConfig()}
        onStoreAction={handleStoreAction}
        onCreateStore={role === 'admin' ? handleCreateStore : undefined}
        isLoading={isLoading}
      />

      {/* Дополнительная аналитика для админов */}
      {role === 'admin' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-surface rounded-lg p-6">
            <h3 className="text-lg font-semibold text-primary mb-4">
              Последние магазины
            </h3>
            
            <div className="space-y-3">
              {storesData
                .sort((a, b) => {
                  const revenueA = parseFloat(a.total_revenue.replace(/[^\d.-]/g, '')) || 0;
                  const revenueB = parseFloat(b.total_revenue.replace(/[^\d.-]/g, '')) || 0;
                  return revenueB - revenueA;
                })
                .slice(0, 5)
                .map((store, index) => (
                  <div key={store.id} className="flex justify-between items-center p-3 bg-background rounded-lg">
                    <div>
                      <div className="font-medium text-primary">
                        #{index + 1} {store.name}
                      </div>
                      <div className="text-sm text-secondary">
                        {store.merchant_name}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-accent">
                        {store.total_revenue}
                      </div>
                      <div className="text-sm text-secondary">
                        {store.total_orders} ордеров
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          <div className="bg-surface rounded-lg p-6">
            <h3 className="text-lg font-semibold text-primary mb-4">
              Детальная аналитика
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6 text-sm">
              <div>
                <span className="text-secondary">Средний оборот магазина:</span>
                <span className="text-primary font-medium">
                  ₽ {Math.round(stats.activeCount * 150000).toLocaleString()}
                </span>
              </div>
              <div>
                <span className="text-secondary">Средняя конверсия:</span>
                <span className="text-success font-medium">78.5%</span>
              </div>
              <div>
                <span className="text-secondary">Новых магазинов за месяц:</span>
                <span className="text-primary font-medium">{Math.floor(stats.totalCount * 0.15)}</span>
              </div>
              <div>
                <span className="text-secondary">Средняя комиссия:</span>
                <span className="text-warning font-medium">2.8%</span>
              </div>
              <div>
                <span className="text-secondary">Интеграций с API:</span>
                <span className="text-info font-medium">
                  {Math.round(stats.activeCount * 0.7)}
                </span>
              </div>
              <div>
                <span className="text-secondary">Настроенных webhook:</span>
                <span className="text-info font-medium">
                  {Math.round(stats.activeCount * 0.9)}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Уведомления о проблемах */}
      {stats.blockedCount > 0 && (
        <div className="bg-error-light border border-error rounded-lg p-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-error rounded-full"></div>
            <span className="font-medium text-primary">
              Внимание: {stats.blockedCount} магазинов заблокированы
            </span>
          </div>
        </div>
      )}

      {stats.pendingCount > 0 && (
        <div className="bg-warning-light border border-warning rounded-lg p-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-warning rounded-full"></div>
            <span className="font-medium text-primary">
              {stats.pendingCount} магазинов ожидают модерации
            </span>
          </div>
        </div>
      )}
    </div>
  );
}; 