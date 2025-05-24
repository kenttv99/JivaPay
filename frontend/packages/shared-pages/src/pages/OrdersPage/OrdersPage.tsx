'use client';

import React, { useState } from 'react';
import { usePermissions } from '@jivapay/permissions';
import { OrdersTable, OrderItem } from '../../components/OrdersTable/OrdersTable';
import { ORDERS_CONFIGS, UserRole } from '../../configs/roleConfigs';

interface OrdersPageProps {
  // Mock данные для демонстрации - в реальности будут приходить из API хуков
  ordersData?: OrderItem[];
  isLoading?: boolean;
}

export const OrdersPage: React.FC<OrdersPageProps> = ({
  ordersData = [],
  isLoading = false
}) => {
  const { userRole } = usePermissions();
  const role = userRole as UserRole;
  
  // Получаем конфигурацию для текущей роли
  const ordersConfig = ORDERS_CONFIGS[role];
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');

  if (!ordersConfig) {
    return (
      <div className="p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-[var(--jiva-text)]">Доступ запрещен</h1>
          <p className="text-[var(--jiva-text-secondary)] mt-2">У вас нет прав для просмотра ордеров</p>
        </div>
      </div>
    );
  }

  // Фильтрация ордеров в зависимости от роли и фильтров
  const getFilteredOrders = (): OrderItem[] => {
    let filteredOrders = ordersData;

    // Ограничения по ролям
    if (!ordersConfig.filters.showAllUsers) {
      if (role === 'support') {
        // Саппорт видит только проблемные ордера
        filteredOrders = filteredOrders.filter(order => 
          ['disputed', 'failed'].includes(order.status)
        );
      } else if (role === 'teamlead') {
        // Тимлид видит только ордера своей команды
        filteredOrders = filteredOrders.filter(order => 
          order.trader?.includes('team') // Мок логика команды
        );
      }
    }

    // Фильтр по статусу
    if (selectedStatus !== 'all') {
      filteredOrders = filteredOrders.filter(order => order.status === selectedStatus);
    }

    // Фильтр по типу
    if (selectedType !== 'all') {
      filteredOrders = filteredOrders.filter(order => order.type === selectedType);
    }

    return filteredOrders;
  };

  // Статистика ордеров
  const getOrderStats = () => {
    const allOrders = getFilteredOrders();
    return {
      total: allOrders.length,
      completed: allOrders.filter(o => o.status === 'completed').length,
      processing: allOrders.filter(o => o.status === 'processing').length,
      pending: allOrders.filter(o => o.status === 'pending').length,
      disputed: allOrders.filter(o => o.status === 'disputed').length,
      failed: allOrders.filter(o => o.status === 'failed').length,
      payin: allOrders.filter(o => o.type === 'payin').length,
      payout: allOrders.filter(o => o.type === 'payout').length
    };
  };

  const handleOrderAction = (order: OrderItem) => {
    console.log('Selected order:', order);
    // Здесь будет обработка выбора ордера
  };

  const stats = getOrderStats();
  const filteredOrders = getFilteredOrders();

  // Доступные статусы для фильтрации
  const getAvailableStatuses = () => {
    if (!ordersConfig.filters.showAllStatuses) {
      if (role === 'support') {
        return [
          { value: 'all', label: 'Все' },
          { value: 'disputed', label: 'Спорные' },
          { value: 'failed', label: 'Неудачные' }
        ];
      }
    }
    
    return [
      { value: 'all', label: 'Все' },
      { value: 'completed', label: 'Выполненные' },
      { value: 'processing', label: 'В обработке' },
      { value: 'pending', label: 'Ожидание' },
      { value: 'disputed', label: 'Спорные' },
      { value: 'failed', label: 'Неудачные' }
    ];
  };

  return (
    <div className="space-y-6">
      {/* Заголовок страницы */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-[var(--jiva-text)]">
            {role === 'support' ? 'Проблемные ордера' : 'Управление ордерами'}
          </h1>
          <p className="text-[var(--jiva-text-secondary)] mt-1">
            {role === 'admin' ? 'Централизованная система управления всеми ордерами' :
             role === 'teamlead' ? 'Ордера команды трейдеров' :
             'Ордера требующие поддержки'}
          </p>
        </div>

        {ordersConfig.permissions.exportData && (
          <button className="bg-[var(--jiva-primary)] text-white px-4 py-2 rounded-lg hover:opacity-90">
            Экспорт данных
          </button>
        )}
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="bg-[var(--jiva-background-paper)] p-4 rounded-lg">
          <div className="text-2xl font-bold text-[var(--jiva-text)]">{stats.total}</div>
          <div className="text-sm text-[var(--jiva-text-secondary)]">Всего ордеров</div>
        </div>
        <div className="bg-[var(--jiva-background-paper)] p-4 rounded-lg">
          <div className="text-2xl font-bold text-[var(--jiva-success)]">{stats.completed}</div>
          <div className="text-sm text-[var(--jiva-text-secondary)]">Выполнено</div>
        </div>
        <div className="bg-[var(--jiva-background-paper)] p-4 rounded-lg">
          <div className="text-2xl font-bold text-[var(--jiva-info)]">{stats.processing}</div>
          <div className="text-sm text-[var(--jiva-text-secondary)]">В процессе</div>
        </div>
        <div className="bg-[var(--jiva-background-paper)] p-4 rounded-lg">
          <div className="text-2xl font-bold text-[var(--jiva-warning)]">{stats.pending}</div>
          <div className="text-sm text-[var(--jiva-text-secondary)]">Ожидание</div>
        </div>
        {ordersConfig.filters.showAllStatuses && (
          <>
            <div className="bg-[var(--jiva-background-paper)] p-4 rounded-lg">
              <div className="text-2xl font-bold text-[var(--jiva-error)]">{stats.disputed + stats.failed}</div>
              <div className="text-sm text-[var(--jiva-text-secondary)]">Проблемные</div>
            </div>
            <div className="bg-[var(--jiva-background-paper)] p-4 rounded-lg">
              <div className="text-2xl font-bold text-[var(--jiva-primary)]">{stats.payin}</div>
              <div className="text-sm text-[var(--jiva-text-secondary)]">Пополнения</div>
            </div>
          </>
        )}
      </div>

      {/* Фильтры */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <div className="flex gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-[var(--jiva-text)] mb-2">
              Статус
            </label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
            >
              {getAvailableStatuses().map(status => (
                <option key={status.value} value={status.value}>
                  {status.label}
                </option>
              ))}
            </select>
          </div>

          {ordersConfig.filters.showAllTypes && (
            <div>
              <label className="block text-sm font-medium text-[var(--jiva-text)] mb-2">
                Тип операции
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
              >
                <option value="all">Все</option>
                <option value="payin">Пополнение</option>
                <option value="payout">Вывод</option>
              </select>
            </div>
          )}
        </div>

        {/* Таблица ордеров */}
        <OrdersTable
          orders={filteredOrders}
          showColumns={{
            trader: ordersConfig.filters.showTraderInfo,
            commissions: ordersConfig.filters.showCommissions,
            store: ordersConfig.filters.showStoreInfo,
            crypto: true,
            actions: false
          }}
          onOrderSelect={handleOrderAction}
          isLoading={isLoading}
        />

        {filteredOrders.length === 0 && !isLoading && (
          <div className="text-center py-8">
            <div className="text-[var(--jiva-text-secondary)]">
              Ордера не найдены для выбранных фильтров
            </div>
          </div>
        )}
      </div>

      {/* Быстрые действия для админов */}
      {role === 'admin' && ordersConfig.permissions.editAny && (
        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
          <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
            Быстрые действия
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="p-4 border border-[var(--jiva-border-light)] rounded-lg hover:bg-[var(--jiva-background)] text-left">
              <div className="font-medium text-[var(--jiva-text)]">Переназначить трейдера</div>
              <div className="text-sm text-[var(--jiva-text-secondary)]">Массовое переназначение</div>
            </button>
            <button className="p-4 border border-[var(--jiva-border-light)] rounded-lg hover:bg-[var(--jiva-background)] text-left">
              <div className="font-medium text-[var(--jiva-text)]">Отменить ордера</div>
              <div className="text-sm text-[var(--jiva-text-secondary)]">Массовая отмена</div>
            </button>
            <button className="p-4 border border-[var(--jiva-border-light)] rounded-lg hover:bg-[var(--jiva-background)] text-left">
              <div className="font-medium text-[var(--jiva-text)]">Обновить статусы</div>
              <div className="text-sm text-[var(--jiva-text-secondary)]">Синхронизация</div>
            </button>
            <button className="p-4 border border-[var(--jiva-border-light)] rounded-lg hover:bg-[var(--jiva-background)] text-left">
              <div className="font-medium text-[var(--jiva-text)]">Создать отчет</div>
              <div className="text-sm text-[var(--jiva-text-secondary)]">Подробная аналитика</div>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}; 