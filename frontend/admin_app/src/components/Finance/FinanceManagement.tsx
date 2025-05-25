import React from 'react';
import { DataTable, StatusBadge, StatsCard } from '@jivapay/ui-kit';

interface Transaction {
  id: string;
  date: string;
  store: string;
  amount: number;
  commission: number;
  status: 'success' | 'processing' | 'failed' | 'refund';
  method: string;
  currency: string;
}

interface FinanceStats {
  totalBalance: number;
  monthlyCommissions: number;
  dailyTransactions: number;
  averageCheck: number;
  balanceChange: number;
  commissionsChange: number;
  transactionsChange: number;
  checkChange: number;
}

interface FinanceManagementProps {
  transactions: Transaction[];
  stats: FinanceStats;
  loading?: boolean;
}

export const FinanceManagement: React.FC<FinanceManagementProps> = ({ 
  transactions, 
  stats, 
  loading 
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const formatChange = (change: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(1)}%`;
  };

  const getTransactionColumns = () => [
    {
      key: 'id',
      title: 'ID транзакции',
      render: (value: string) => (
        <span className="font-mono text-xs">{value}</span>
      )
    },
    {
      key: 'date',
      title: 'Дата и время',
      render: (value: string) => (
        <span className="text-xs text-secondary">{value}</span>
      )
    },
    {
      key: 'store',
      title: 'Магазин',
      render: (value: string) => (
        <span className="font-medium">{value}</span>
      )
    },
    {
      key: 'amount',
      title: 'Сумма',
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
        <span className="text-secondary">{formatCurrency(value)}</span>
      )
    },
    {
      key: 'method',
      title: 'Способ оплаты',
      render: (value: string) => (
        <span className="text-xs bg-background px-2 py-1 rounded">
          {value}
        </span>
      )
    },
    {
      key: 'status',
      title: 'Статус',
      render: (value: 'success' | 'processing' | 'failed' | 'refund') => {
        const statusMap = {
          success: 'success' as const,
          processing: 'processing' as const,
          failed: 'failed' as const,
          refund: 'pending' as const
        };
        const textMap = {
          success: 'Успешно',
          processing: 'В процессе',
          failed: 'Ошибка',
          refund: 'Возврат'
        };
        return <StatusBadge status={statusMap[value]}>{textMap[value]}</StatusBadge>;
      }
    },
    {
      key: 'actions',
      title: 'Действия',
      align: 'right' as const,
      render: () => (
        <div className="flex gap-2 justify-end">
          <button className="text-accent hover:opacity-90 text-xs">
            Просмотр
          </button>
          <button className="text-secondary hover:text-primary text-xs">
            Изменить
          </button>
        </div>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Финансы</h1>
        <p className="text-secondary mt-1">
          Управление транзакциями и балансами
        </p>
      </div>

      {/* Основные метрики */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Общий баланс"
          value={formatCurrency(stats.totalBalance)}
          change={formatChange(stats.balanceChange)}
          trend={stats.balanceChange >= 0 ? 'up' : 'down'}
          subtitle="за неделю"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        
        <StatsCard
          title="Комиссии за месяц"
          value={formatCurrency(stats.monthlyCommissions)}
          change={formatChange(stats.commissionsChange)}
          trend={stats.commissionsChange >= 0 ? 'up' : 'down'}
          subtitle="от прошлого месяца"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 8h6m-5 0a3 3 0 110 6H9l3 3m-3-6h6m6 1a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        
        <StatsCard
          title="Транзакций за день"
          value={stats.dailyTransactions.toLocaleString('ru-RU')}
          change={formatChange(stats.transactionsChange)}
          trend={stats.transactionsChange >= 0 ? 'up' : 'down'}
          subtitle="от вчера"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
        />
        
        <StatsCard
          title="Средний чек"
          value={formatCurrency(stats.averageCheck)}
          change={formatChange(stats.checkChange)}
          trend={stats.checkChange >= 0 ? 'up' : 'down'}
          subtitle="за неделю"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          }
        />
      </div>

      {/* Графики и аналитика */}
      <div className="bg-surface rounded-lg p-6 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Динамика доходов</h3>
          <div className="flex bg-background rounded-lg overflow-hidden">
            <button className="px-3 py-1 text-sm bg-accent text-white">
              Доходы
            </button>
            <button className="px-3 py-1 text-sm hover:bg-surface">
              Расходы
            </button>
            <button className="px-3 py-1 text-sm hover:bg-surface">
              Прибыль
            </button>
          </div>
        </div>
        
        <div style={{ width: '100%', height: 300 }}>
          <p className="text-secondary">
            График финансовой динамики будет здесь
          </p>
          <p className="text-xs text-secondary mt-1">
            Показывает изменения доходов/расходов по времени
          </p>
        </div>
      </div>

      {/* Настройки и фильтры */}
      <div className="bg-surface rounded-lg p-4 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Фильтры и настройки</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-secondary mb-1">
              Период
            </label>
            <select className="w-full p-2 border border-border rounded-md text-sm">
              <option>Сегодня</option>
              <option>Неделя</option>
              <option>Месяц</option>
              <option>Год</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-secondary mb-1">
              Тип операций
            </label>
            <select className="w-full p-2 border border-border rounded-md text-sm">
              <option>Все</option>
              <option>Доходы</option>
              <option>Расходы</option>
              <option>Переводы</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-secondary mb-1">
              Валюта
            </label>
            <input
              type="text"
              placeholder="RUB, USD, EUR..."
              className="w-full p-2 border border-border rounded-md text-sm"
            />
          </div>
        </div>
        <button className="px-4 py-2 bg-accent text-white rounded-md hover:opacity-90 transition-colors text-sm">
          Применить фильтры
        </button>
      </div>

      {/* Таблица транзакций */}
      <DataTable
        columns={getTransactionColumns()}
        data={transactions}
        loading={loading}
        emptyText="Нет транзакций для отображения"
      />
    </div>
  );
}; 