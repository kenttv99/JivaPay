'use client';

import { StatsCard } from '../components/ui/StatsCard';
import { MerchantLayout } from '../layouts/MerchantLayout';
import { StoreManagement } from '../components/StoreManagement/StoreManagement';
import { useState } from 'react';

export default function MerchantDashboard() {
  const [loading] = useState(false);

  const recentTransactions = [
    { id: 'TXN-12345', store: 'TechStore', amount: '₽5,420', type: 'payment', time: '2 мин назад', status: 'completed' },
    { id: 'TXN-12344', store: 'Gaming Paradise', amount: '₽2,150', type: 'payment', time: '8 мин назад', status: 'completed' },
    { id: 'TXN-12343', store: 'Fashion Boutique', amount: '₽890', type: 'refund', time: '15 мин назад', status: 'pending' },
    { id: 'TXN-12342', store: 'TechStore', amount: '₽12,300', type: 'payment', time: '22 мин назад', status: 'completed' },
    { id: 'TXN-12341', store: 'Gaming Paradise', amount: '₽670', type: 'payment', time: '35 мин назад', status: 'completed' }
  ];

  const topProducts = [
    { name: 'iPhone 15 Pro', store: 'TechStore', sales: 145, revenue: '₽2,175,000' },
    { name: 'Gaming Keyboard', store: 'Gaming Paradise', sales: 89, revenue: '₽445,000' },
    { name: 'Designer Bag', store: 'Fashion Boutique', sales: 23, revenue: '₽345,000' },
    { name: 'MacBook Air', store: 'TechStore', sales: 34, revenue: '₽1,700,000' }
  ];

  const getTransactionColor = (type: string) => {
    switch (type) {
      case 'payment': return 'text-success';
      case 'refund': return 'text-warning';
      default: return 'text-secondary';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-success/10 text-success';
      case 'pending': return 'bg-warning/10 text-warning';
      case 'failed': return 'bg-error/10 text-error';
      default: return 'bg-surface text-secondary';
    }
  };

  return (
    <MerchantLayout>
      <div className="space-y-6">
        {/* Welcome */}
        <div className="animate-fadeIn">
          <h1 className="text-3xl font-bold text-primary mb-2">Добро пожаловать, TechCompany Ltd</h1>
          <p className="text-secondary">
            Панель управления бизнесом • {new Date().toLocaleDateString('ru-RU', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </p>
        </div>

        {/* Main Business Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Общий оборот"
            value="₽3,340,300"
            change="+12.4%"
            trend="up"
            subtitle="за месяц"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />
          
          <StatsCard
            title="Активные магазины"
            value="2"
            change="0"
            trend="neutral"
            subtitle="из 3 всего"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            }
          />
          
          <StatsCard
            title="Доход сегодня"
            value="₽89,340"
            change="+18.7%"
            trend="up"
            subtitle="к вчера"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
          />
          
          <StatsCard
            title="Транзакций"
            value="1,703"
            change="+5.2%"
            trend="up"
            subtitle="этот месяц"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
            }
          />
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Store Management - 2/3 width */}
          <div className="lg:col-span-2">
            <StoreManagement loading={loading} />
          </div>

          {/* Side Panel - 1/3 width */}
          <div className="space-y-6">
            {/* Recent Transactions */}
            <div className="card-base p-6">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
                Последние транзакции
              </h3>
              
              <div className="space-y-3">
                {recentTransactions.map((txn, index) => (
                  <div 
                    key={txn.id}
                    className="flex items-center justify-between p-3 bg-surface/50 rounded-lg hover:bg-surface transition-colors animate-fadeIn"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-primary text-sm">{txn.store}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(txn.status)}`}>
                          {txn.status === 'completed' ? 'Завершен' : 'В обработке'}
                        </span>
                      </div>
                      <div className="text-xs text-secondary">{txn.id} • {txn.time}</div>
                    </div>
                    <span className={`font-semibold ${getTransactionColor(txn.type)}`}>
                      {txn.type === 'refund' ? '-' : '+'}{txn.amount}
                    </span>
                  </div>
                ))}
              </div>
              
              <button className="w-full mt-4 px-4 py-2 bg-surface text-secondary rounded-lg text-sm font-medium hover:bg-surface/80 transition-colors">
                Все транзакции
              </button>
            </div>

            {/* Top Products */}
            <div className="card-base p-6">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
                Топ продаж
              </h3>
              
              <div className="space-y-3">
                {topProducts.map((product, index) => (
                  <div 
                    key={`${product.name}-${index}`}
                    className="animate-fadeIn"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-medium text-primary text-sm">{product.name}</span>
                      <span className="text-xs bg-info/10 text-info px-2 py-1 rounded-full">
                        #{index + 1}
                      </span>
                    </div>
                    <div className="text-xs text-secondary mb-2">{product.store}</div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-semibold text-success">{product.revenue}</span>
                      <span className="text-xs text-secondary">{product.sales} продаж</span>
                    </div>
                    {index < topProducts.length - 1 && <hr className="mt-3 border-border" />}
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card-base p-6">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Быстрые действия
              </h3>
              
              <div className="space-y-2">
                <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                  Создать ссылку для оплаты
                </button>
                <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                  Добавить новый магазин
                </button>
                <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                  Вывести средства
                </button>
                <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                  Настроить API интеграцию
                </button>
                <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                  Посмотреть отчеты
                </button>
              </div>
            </div>
          </div>
        </div>
    </div>
    </MerchantLayout>
  );
}
