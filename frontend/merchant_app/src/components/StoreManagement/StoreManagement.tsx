'use client';

import React, { useState } from 'react';
import { Skeleton } from '../ui/Skeleton';

interface Store {
  id: string;
  name: string;
  domain: string;
  status: 'active' | 'inactive' | 'pending' | 'suspended';
  revenue: string;
  transactions: number;
  integration: 'api' | 'widget' | 'link' | 'all';
  createdAt: string;
  lastPayment: string;
  commission: number;
}

interface StoreManagementProps {
  loading?: boolean;
  className?: string;
}

export const StoreManagement: React.FC<StoreManagementProps> = ({
  loading = false,
  className = ''
}) => {
  const [filter, setFilter] = useState<'all' | 'active' | 'inactive' | 'pending'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'revenue' | 'name'>('date');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const mockStores: Store[] = [
    {
      id: 'STORE-001',
      name: 'TechStore Online',
      domain: 'techstore.com',
      status: 'active',
      revenue: '₽2,450,000',
      transactions: 1247,
      integration: 'all',
      createdAt: '2024-01-15',
      lastPayment: '2 мин назад',
      commission: 2.5
    },
    {
      id: 'STORE-002',
      name: 'Gaming Paradise',
      domain: 'gaming-paradise.ru',
      status: 'active',
      revenue: '₽890,300',
      transactions: 456,
      integration: 'api',
      createdAt: '2024-03-22',
      lastPayment: '15 мин назад',
      commission: 3.0
    },
    {
      id: 'STORE-003',
      name: 'Fashion Boutique',
      domain: 'fashion-boutique.shop',
      status: 'pending',
      revenue: '₽0',
      transactions: 0,
      integration: 'widget',
      createdAt: '2024-12-10',
      lastPayment: 'Нет',
      commission: 2.8
    }
  ];

  const getStatusColor = (status: Store['status']) => {
    switch (status) {
      case 'active': return 'bg-success/10 text-success border-success/20';
      case 'inactive': return 'bg-surface/80 text-secondary border-border';
      case 'pending': return 'bg-warning/10 text-warning border-warning/20';
      case 'suspended': return 'bg-error/10 text-error border-error/20';
    }
  };

  const getStatusText = (status: Store['status']) => {
    switch (status) {
      case 'active': return 'Активен';
      case 'inactive': return 'Неактивен';
      case 'pending': return 'На модерации';
      case 'suspended': return 'Заблокирован';
    }
  };

  const getIntegrationText = (integration: Store['integration']) => {
    switch (integration) {
      case 'api': return 'API';
      case 'widget': return 'Виджет';
      case 'link': return 'Ссылки';
      case 'all': return 'Все методы';
    }
  };

  const getIntegrationColor = (integration: Store['integration']) => {
    switch (integration) {
      case 'api': return 'bg-info/10 text-info';
      case 'widget': return 'bg-warning/10 text-warning';
      case 'link': return 'bg-success/10 text-success';
      case 'all': return 'bg-secondary/10 text-secondary';
    }
  };

  const filteredStores = mockStores.filter(store => 
    filter === 'all' || store.status === filter
  );

  if (loading) {
    return (
      <div className={`card-base p-6 ${className}`}>
        <div className="flex items-center justify-between mb-6">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-8 w-32" />
        </div>
        
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border border-border rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="h-6 w-20" />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-4 w-28" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`card-base p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-primary flex items-center gap-2">
            <svg className="w-6 h-6 text-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            Управление магазинами
          </h2>
          <p className="text-secondary text-sm">
            {filteredStores.length} магазинов • {filteredStores.filter(s => s.status === 'active').length} активных
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Filters */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'active' | 'inactive' | 'pending')}
            className="px-3 py-2 border border-border rounded-lg bg-surface text-primary text-sm"
          >
            <option value="all">Все магазины</option>
            <option value="active">Активные</option>
            <option value="pending">На модерации</option>
            <option value="inactive">Неактивные</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'revenue' | 'name')}
            className="px-3 py-2 border border-border rounded-lg bg-surface text-primary text-sm"
          >
            <option value="date">По дате</option>
            <option value="revenue">По доходу</option>
            <option value="name">По названию</option>
          </select>

          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-secondary text-white rounded-lg text-sm font-medium hover:bg-secondary/80 transition-colors"
          >
            + Создать магазин
          </button>
        </div>
      </div>

      {/* Stores Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredStores.length > 0 ? (
          filteredStores.map((store, index) => (
            <div
              key={store.id}
              className={`
                border border-border rounded-lg p-6 hover:shadow-lg transition-all duration-200 
                animate-fadeIn cursor-pointer hover:border-secondary/30
                ${store.status === 'active' ? 'ring-1 ring-success/20' : ''}
              `}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Store Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-secondary rounded-lg flex items-center justify-center text-white font-semibold">
                    {store.name.split(' ').map(word => word[0]).join('').substring(0, 2)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-primary">{store.name}</h3>
                    <p className="text-sm text-secondary">{store.domain}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(store.status)}`}>
                    {getStatusText(store.status)}
                  </span>
                </div>
              </div>

              {/* Store Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <span className="text-xs text-secondary">Доход</span>
                  <p className="font-semibold text-primary">{store.revenue}</p>
                </div>
                <div>
                  <span className="text-xs text-secondary">Транзакций</span>
                  <p className="font-semibold text-primary">{store.transactions.toLocaleString()}</p>
                </div>
                <div>
                  <span className="text-xs text-secondary">Комиссия</span>
                  <p className="font-semibold text-primary">{store.commission}%</p>
                </div>
                <div>
                  <span className="text-xs text-secondary">Последняя оплата</span>
                  <p className="font-semibold text-primary">{store.lastPayment}</p>
                </div>
              </div>

              {/* Integration Type */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-secondary">Интеграция:</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getIntegrationColor(store.integration)}`}>
                    {getIntegrationText(store.integration)}
                  </span>
                </div>
                <span className="text-xs text-secondary">
                  Создан: {new Date(store.createdAt).toLocaleDateString('ru-RU')}
                </span>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2">
                {store.status === 'active' && (
                  <>
                    <button className="flex-1 px-3 py-2 bg-info text-white rounded-lg text-sm font-medium hover:bg-info/80 transition-colors">
                      Настройки
                    </button>
                    <button className="flex-1 px-3 py-2 bg-surface text-secondary border border-border rounded-lg text-sm font-medium hover:bg-surface/80 transition-colors">
                      Статистика
                    </button>
                  </>
                )}
                
                {store.status === 'pending' && (
                  <button className="flex-1 px-3 py-2 bg-warning text-white rounded-lg text-sm font-medium hover:bg-yellow-600 transition-colors">
                    Дождаться модерации
                  </button>
                )}

                {store.status === 'inactive' && (
                  <button className="flex-1 px-3 py-2 bg-success text-white rounded-lg text-sm font-medium hover:bg-green-600 transition-colors">
                    Активировать
                  </button>
                )}

                <button className="px-4 py-2 bg-surface text-secondary border border-border rounded-lg text-sm font-medium hover:bg-surface/80 transition-colors">
                  ⚙️
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <svg className="w-16 h-16 text-secondary mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <p className="text-secondary">Нет магазинов для отображения</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-4 px-4 py-2 bg-secondary text-white rounded-lg text-sm font-medium hover:bg-secondary/80 transition-colors"
            >
              Создать первый магазин
            </button>
          </div>
        )}
      </div>

      {/* Create Store Modal Placeholder */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-primary mb-4">Создать новый магазин</h3>
            <p className="text-secondary mb-6">Форма создания магазина будет здесь</p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-surface text-secondary border border-border rounded-lg text-sm font-medium hover:bg-surface/80 transition-colors"
              >
                Отмена
              </button>
              <button className="flex-1 px-4 py-2 bg-secondary text-white rounded-lg text-sm font-medium hover:bg-secondary/80 transition-colors">
                Создать
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 