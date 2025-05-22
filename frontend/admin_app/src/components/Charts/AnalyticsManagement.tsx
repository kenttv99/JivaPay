import React from 'react';
import { DataTable } from '../ui/DataTable';
import { StatsCard } from '../widgets/StatsCard';

interface AnalyticsData {
  date: string;
  salesVolume: number;
  transactions: number;
  averageCheck: number;
  commission: number;
  conversion: number;
}

interface AnalyticsStats {
  totalSalesVolume: number;
  totalTransactions: number;
  averageCheck: number;
  totalCommission: number;
  salesVolumeChange: number;
  transactionsChange: number;
  averageCheckChange: number;
  commissionChange: number;
}

interface AnalyticsManagementProps {
  data: AnalyticsData[];
  stats: AnalyticsStats;
  loading?: boolean;
}

export const AnalyticsManagement: React.FC<AnalyticsManagementProps> = ({ 
  data, 
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

  const getAnalyticsColumns = () => [
    {
      key: 'date',
      title: 'Дата',
      render: (value: string) => (
        <span className="font-medium">{value}</span>
      )
    },
    {
      key: 'salesVolume',
      title: 'Объем продаж',
      align: 'right' as const,
      render: (value: number) => (
        <span className="font-medium">{formatCurrency(value)}</span>
      )
    },
    {
      key: 'transactions',
      title: 'Транзакций',
      align: 'right' as const,
      render: (value: number) => (
        <span>{value.toLocaleString('ru-RU')}</span>
      )
    },
    {
      key: 'averageCheck',
      title: 'Средний чек',
      align: 'right' as const,
      render: (value: number) => (
        <span>{formatCurrency(value)}</span>
      )
    },
    {
      key: 'commission',
      title: 'Комиссия',
      align: 'right' as const,
      render: (value: number) => (
        <span className="text-[var(--jiva-text-secondary)]">{formatCurrency(value)}</span>
      )
    },
    {
      key: 'conversion',
      title: 'Конверсия',
      align: 'right' as const,
      render: (value: number) => (
        <span className="text-[var(--jiva-success)]">{value}%</span>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Аналитика</h1>
        <p className="text-[var(--jiva-text-secondary)] mt-1">
          Статистика и аналитика продаж
        </p>
      </div>

      {/* Фильтры */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-4 shadow-sm">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Период
            </label>
            <select className="w-full p-2 border border-[var(--jiva-border)] rounded-md text-sm">
              <option value="week">Неделя</option>
              <option value="month" defaultChecked>Месяц</option>
              <option value="quarter">Квартал</option>
              <option value="year">Год</option>
              <option value="custom">Выбрать период</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Мерчант
            </label>
            <select className="w-full p-2 border border-[var(--jiva-border)] rounded-md text-sm">
              <option value="">Все мерчанты</option>
              <option value="1">ООО &quot;Первый&quot;</option>
              <option value="2">ИП Петров</option>
              <option value="3">ООО &quot;Технологии&quot;</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Метрики
            </label>
            <select className="w-full p-2 border border-[var(--jiva-border)] rounded-md text-sm">
              <option value="transactions">Транзакции</option>
              <option value="volume" defaultChecked>Объем продаж</option>
              <option value="commission">Комиссии</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button className="px-4 py-2 bg-[var(--jiva-primary)] text-white rounded-md hover:bg-[var(--jiva-primary-dark)] transition-colors text-sm">
              Применить
            </button>
          </div>
        </div>
      </div>

      {/* Основной график */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Объем продаж по дням</h2>
          <div className="flex bg-[var(--jiva-background)] rounded-lg overflow-hidden">
            <button className="px-3 py-1 text-sm bg-[var(--jiva-primary)] text-white">
              График
            </button>
            <button className="px-3 py-1 text-sm hover:bg-[var(--jiva-background-paper)]">
              Таблица
            </button>
          </div>
        </div>
        <div className="h-96 w-full bg-gray-100 rounded flex items-center justify-center">
          <div className="text-center">
            <p className="text-[var(--jiva-text-secondary)]">
              Основной график аналитики будет здесь
            </p>
            <p className="text-xs text-[var(--jiva-text-secondary)] mt-1">
              Интеграция с Chart.js или D3.js
            </p>
          </div>
        </div>
      </div>

      {/* Статистические карточки */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Общий объем продаж"
          value={formatCurrency(stats.totalSalesVolume)}
          change={formatChange(stats.salesVolumeChange)}
          trend={stats.salesVolumeChange >= 0 ? 'up' : 'down'}
          subtitle="к прошлому месяцу"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
        />
        
        <StatsCard
          title="Кол-во транзакций"
          value={stats.totalTransactions.toLocaleString('ru-RU')}
          change={formatChange(stats.transactionsChange)}
          trend={stats.transactionsChange >= 0 ? 'up' : 'down'}
          subtitle="к прошлому месяцу"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          }
        />
        
        <StatsCard
          title="Средний чек"
          value={formatCurrency(stats.averageCheck)}
          change={formatChange(stats.averageCheckChange)}
          trend={stats.averageCheckChange >= 0 ? 'up' : 'down'}
          subtitle="к прошлому месяцу"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          }
        />
        
        <StatsCard
          title="Доход с комиссий"
          value={formatCurrency(stats.totalCommission)}
          change={formatChange(stats.commissionChange)}
          trend={stats.commissionChange >= 0 ? 'up' : 'down'}
          subtitle="к прошлому месяцу"
          icon={
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>

      {/* Дополнительные графики */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
          <h2 className="text-xl font-bold mb-4">Распределение по способам оплаты</h2>
          <div className="h-80 w-full bg-gray-100 rounded flex items-center justify-center">
            <div className="text-center">
              <p className="text-[var(--jiva-text-secondary)]">
                Круговая диаграмма методов оплаты
              </p>
              <div className="mt-4 space-y-2 text-sm">
                <div className="flex justify-between items-center">
                  <span>Банковские карты</span>
                  <span className="font-medium">65%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Электронные кошельки</span>
                  <span className="font-medium">24%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Криптовалюты</span>
                  <span className="font-medium">8%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Другие</span>
                  <span className="font-medium">3%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
          <h2 className="text-xl font-bold mb-4">Топ-5 мерчантов</h2>
          <div className="h-80 w-full bg-gray-100 rounded flex items-center justify-center">
            <div className="text-center">
              <p className="text-[var(--jiva-text-secondary)]">
                Горизонтальная гистограмма топ мерчантов
              </p>
              <div className="mt-4 space-y-3 text-sm w-full max-w-sm">
                {['TechShop', 'BookStore', 'FashionHub', 'SportWorld', 'ElectroMarket'].map((store, index) => (
                  <div key={store} className="flex justify-between items-center">
                    <span>{store}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-[var(--jiva-background)] rounded overflow-hidden">
                        <div 
                          className="h-full bg-[var(--jiva-primary)]" 
                          style={{ width: `${100 - index * 15}%` }}
                        ></div>
                      </div>
                      <span className="font-medium text-xs">{formatCurrency((5 - index) * 500000)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Детальная таблица */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg shadow-sm">
        <div className="flex justify-between items-center p-6 border-b border-[var(--jiva-border)]">
          <h2 className="text-xl font-bold">Детальная статистика</h2>
          <button className="px-4 py-2 bg-[var(--jiva-primary)] text-white rounded-md hover:bg-[var(--jiva-primary-dark)] transition-colors text-sm">
            Экспорт в CSV
          </button>
        </div>
        
        <div className="p-6">
          <DataTable
            columns={getAnalyticsColumns()}
            data={data}
            loading={loading}
            emptyText="Нет данных аналитики для отображения"
          />
        </div>
      </div>
    </div>
  );
}; 