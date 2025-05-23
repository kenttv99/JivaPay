import React from 'react';
import { DataTable, StatusBadge, StatsCard } from '@jivapay/ui-kit';

interface Store {
  id: string;
  name: string;
  merchantName: string;
  domain: string;
  status: 'active' | 'inactive' | 'blocked' | 'pending';
  monthlyVolume: number;
  commission: number;
  category: string;
  createdDate: string;
  lastActivity: string;
}

interface StoreStats {
  totalStores: number;
  activeStores: number;
  monthlyVolume: number;
  averageCommission: number;
  storesChange: number;
  activeChange: number;
  volumeChange: number;
  commissionChange: number;
}

interface StoreManagementProps {
  stores: Store[];
  stats: StoreStats;
  loading?: boolean;
}

export const StoreManagement: React.FC<StoreManagementProps> = ({ 
  stores, 
  stats, 
  loading 
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatChange = (change: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(1)}%`;
  };

  const getStoreColumns = () => [
    {
      key: 'name',
      title: 'Название магазина',
      render: (value: string, row: Store) => (
        <div>
          <div className="font-medium">{value}</div>
          <div className="text-xs text-[var(--jiva-text-secondary)]">{row.domain}</div>
        </div>
      )
    },
    {
      key: 'merchantName',
      title: 'Мерчант',
      render: (value: string) => (
        <span className="font-medium">{value}</span>
      )
    },
    {
      key: 'category',
      title: 'Категория',
      render: (value: string) => (
        <span className="px-2 py-1 bg-[var(--jiva-background)] text-[var(--jiva-text-primary)] rounded text-xs">
          {value}
        </span>
      )
    },
    {
      key: 'monthlyVolume',
      title: 'Оборот за месяц',
      align: 'right' as const,
      render: (value: number) => (
        <span className="font-medium">{formatCurrency(value)}</span>
      )
    },
    {
      key: 'commission',
      title: 'Комиссия',
      align: 'right' as const,
      render: (value: number) => (
        <span className="text-[var(--jiva-text-secondary)]">{value}%</span>
      )
    },
    {
      key: 'status',
      title: 'Статус',
      render: (value: 'active' | 'inactive' | 'blocked' | 'pending') => (
        <StatusBadge status={value} />
      )
    },
    {
      key: 'lastActivity',
      title: 'Последняя активность',
      render: (value: string) => (
        <span className="text-xs text-[var(--jiva-text-secondary)]">{value}</span>
      )
    },
    {
      key: 'actions',
      title: 'Действия',
      align: 'right' as const,
      render: () => (
        <div className="flex gap-2 justify-end">
          <button className="text-[var(--jiva-primary)] hover:text-[var(--jiva-primary-dark)] text-xs">
            Настройки
          </button>
          <button className="text-[var(--jiva-text-secondary)] hover:text-[var(--jiva-text-primary)] text-xs">
            Статистика
          </button>
        </div>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Магазины</h1>
        <p className="text-[var(--jiva-text-secondary)] mt-1">
          Управление магазинами и их настройками
        </p>
      </div>

      {/* Статистические карточки */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Всего магазинов"
          value={stats.totalStores.toString()}
          change={formatChange(stats.storesChange)}
          trend={stats.storesChange >= 0 ? 'up' : 'down'}
          subtitle="за месяц"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          }
        />
        
        <StatsCard
          title="Активные магазины"
          value={stats.activeStores.toString()}
          change={formatChange(stats.activeChange)}
          trend={stats.activeChange >= 0 ? 'up' : 'down'}
          subtitle="за месяц"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        
        <StatsCard
          title="Месячный оборот"
          value={formatCurrency(stats.monthlyVolume)}
          change={formatChange(stats.volumeChange)}
          trend={stats.volumeChange >= 0 ? 'up' : 'down'}
          subtitle="к прошлому месяцу"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
        />
        
        <StatsCard
          title="Средняя комиссия"
          value={`${stats.averageCommission}%`}
          change={formatChange(stats.commissionChange)}
          trend={stats.commissionChange >= 0 ? 'up' : 'down'}
          subtitle="к прошлому месяцу"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 8h6m-5 0a3 3 0 110 6H9l3 3m-3-6h6m6 1a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>

      {/* Фильтры и поиск */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-4 shadow-sm">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Статус
            </label>
            <select className="w-full p-2 border border-[var(--jiva-border)] rounded-md text-sm">
              <option value="">Все статусы</option>
              <option value="active">Активные</option>
              <option value="inactive">Неактивные</option>
              <option value="blocked">Заблокированные</option>
              <option value="pending">Ожидают модерации</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Категория
            </label>
            <select className="w-full p-2 border border-[var(--jiva-border)] rounded-md text-sm">
              <option value="">Все категории</option>
              <option value="electronics">Электроника</option>
              <option value="fashion">Мода</option>
              <option value="books">Книги</option>
              <option value="food">Еда</option>
              <option value="other">Другое</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Поиск
            </label>
            <input
              type="text"
              placeholder="Название магазина или домен"
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md text-sm"
            />
          </div>
          
          <div className="flex items-end">
            <button className="px-4 py-2 bg-[var(--jiva-primary)] text-white rounded-md hover:bg-[var(--jiva-primary-dark)] transition-colors text-sm">
              Добавить магазин
            </button>
          </div>
        </div>
      </div>

      {/* Топ магазины */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
        <h2 className="text-xl font-bold mb-4">Топ-5 магазинов по обороту</h2>
        <div className="space-y-3">
          {stores.slice(0, 5).map((store, index) => (
            <div key={store.id} className="flex items-center justify-between p-3 bg-[var(--jiva-background)] rounded">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-[var(--jiva-primary)] text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <div>
                  <div className="font-medium">{store.name}</div>
                  <div className="text-xs text-[var(--jiva-text-secondary)]">{store.merchantName}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-bold">{formatCurrency(store.monthlyVolume)}</div>
                <div className="text-xs text-[var(--jiva-text-secondary)]">{store.commission}% комиссия</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Таблица магазинов */}
      <DataTable
        columns={getStoreColumns()}
        data={stores}
        loading={loading}
        emptyText="Нет магазинов для отображения"
      />
    </div>
  );
}; 