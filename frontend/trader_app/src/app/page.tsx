'use client';

import { StatsCard } from '../components/ui/StatsCard';
import { TraderLayout } from '../layouts/TraderLayout';
import { OrdersWidget } from '../components/OrdersWidget/OrdersWidget';
import { useState } from 'react';

export default function TraderDashboard() {
  const [loading] = useState(false);

  const mockRequisites = [
    { bank: 'Сбербанк', number: '****1234', status: 'active', balance: '₽50,000', daily: '+₽8,500' },
    { bank: 'Тинькофф', number: '****5678', status: 'active', balance: '₽25,000', daily: '+₽3,200' },
    { bank: 'ВТБ', number: '****9012', status: 'processing', balance: '₽75,000', daily: '+₽4,800' },
    { bank: 'Альфа-Банк', number: '****3456', status: 'inactive', balance: '₽0', daily: '₽0' }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-success/10 text-success';
      case 'processing': return 'bg-warning/10 text-warning';
      case 'inactive': return 'bg-error/10 text-error';
      default: return 'bg-surface text-secondary';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Активен';
      case 'processing': return 'Обработка';
      case 'inactive': return 'Неактивен';
      default: return 'Неизвестно';
    }
  };

  return (
    <TraderLayout>
      <div className="space-y-6">
        {/* Welcome */}
        <div className="animate-fadeIn">
          <h1 className="text-3xl font-bold text-primary mb-2">Добро пожаловать, Trader #001</h1>
          <p className="text-secondary">
            Сегодня {new Date().toLocaleDateString('ru-RU', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </p>
        </div>

        {/* Main Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatsCard
              title="Активные реквизиты"
            value="3"
            change="+1"
              trend="up"
            subtitle="из 4 доступных"
              icon={
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              }
            />
            
            <StatsCard
            title="Ордеров в работе"
            value="2"
            change="0"
            trend="neutral"
            subtitle="срочных"
              icon={
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              }
            />
            
                <StatsCard
                  title="Доход за день"
            value="₽16,500"
            change="+23.4%"
                trend="up"
                subtitle="к вчера"
                icon={
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                }
              />
            
            <StatsCard
            title="Эффективность"
            value="94.2%"
            change="+1.2%"
            trend="up"
            subtitle="этот месяц"
              icon={
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              }
            />
          </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Orders Widget - 2/3 width */}
          <div className="lg:col-span-2">
            <OrdersWidget loading={loading} />
          </div>

          {/* Side Panel - 1/3 width */}
          <div className="space-y-6">
            {/* My Requisites */}
            <div className="card-base p-6">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
                Мои реквизиты
              </h3>
              
              <div className="space-y-3">
                {mockRequisites.map((req, index) => (
                  <div 
                    key={req.number}
                    className="p-3 border border-border rounded-lg hover:bg-surface transition-colors animate-fadeIn"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-primary text-sm">{req.bank}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(req.status)}`}>
                        {getStatusText(req.status)}
                      </span>
                    </div>
                    <div className="text-xs text-secondary mb-1">{req.number}</div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-semibold text-primary">{req.balance}</span>
                      {req.daily !== '₽0' && (
                        <span className="text-xs text-success">{req.daily}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              <button className="w-full mt-4 px-4 py-2 bg-secondary text-white rounded-lg text-sm font-medium hover:bg-secondary/80 transition-colors">
                + Добавить реквизит
              </button>
            </div>

            {/* Quick Actions */}
            <div className="card-base p-6">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Быстрые действия
              </h3>
              
              <div className="space-y-2">
                <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                  Принять новые ордера
                </button>
                <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                  Проверить баланс реквизитов
                </button>
                <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                  Запросить вывод средств
                </button>
                <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                  Связаться с поддержкой
                </button>
              </div>
            </div>
            
            {/* Performance */}
            <div className="card-base p-6">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Производительность
              </h3>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-secondary">Успешность</span>
                    <span className="text-sm font-medium text-success">94.2%</span>
                  </div>
                  <div className="w-full bg-surface rounded-full h-2">
                    <div className="bg-success h-2 rounded-full" style={{ width: '94.2%' }} />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-secondary">Скорость</span>
                    <span className="text-sm font-medium text-info">3.2 мин</span>
                  </div>
                  <div className="w-full bg-surface rounded-full h-2">
                    <div className="bg-info h-2 rounded-full" style={{ width: '85%' }} />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-secondary">Рейтинг</span>
                    <span className="text-sm font-medium text-warning">4.8/5</span>
                  </div>
                  <div className="w-full bg-surface rounded-full h-2">
                    <div className="bg-warning h-2 rounded-full" style={{ width: '96%' }} />
                  </div>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-success/10 rounded-lg">
                <p className="text-sm text-success font-medium">Отличная работа!</p>
                <p className="text-xs text-success/80">Вы в топ-10% трейдеров</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </TraderLayout>
  );
}
