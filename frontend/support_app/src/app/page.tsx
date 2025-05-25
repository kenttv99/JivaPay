'use client';

import React from 'react';
import { SupportLayout } from '../layouts/SupportLayout';
import { MetricsGrid, OrdersTable, UserManagement, PlatformMetrics } from '@jivapay/shared-pages';

// Мок данные для демонстрации
const mockMetrics = [
  {
    id: 'total-tickets',
    title: 'Всего тикетов',
    value: '1,247',
    change: '+12%',
    trend: 'up' as const,
    subtitle: 'За последний месяц'
  },
  {
    id: 'pending-tickets',
    title: 'Ожидают ответа',
    value: '23',
    change: '+5',
    trend: 'up' as const,
    subtitle: 'Требуют внимания'
  },
  {
    id: 'resolved-today',
    title: 'Решено сегодня',
    value: '89',
    change: '+15%',
    trend: 'up' as const,
    subtitle: 'Выше среднего'
  },
  {
    id: 'avg-response',
    title: 'Среднее время ответа',
    value: '2.4ч',
    change: '-18%',
    trend: 'down' as const,
    subtitle: 'Улучшение'
  }
];

const mockOrders = [
  {
    id: 'ORD-12345',
    date: '2024-12-15 14:30',
    user: 'user123@example.com',
    amount: '₽ 15,000',
    amount_crypto: '0.45',
    currency_crypto: 'BTC',
    type: 'payin' as const,
    status: 'disputed' as const,
    trader: 'trader_001',
    requisite: 'SBER-4567'
  },
  {
    id: 'ORD-12346',
    date: '2024-12-15 14:15',
    user: 'merchant@shop.com',
    amount: '₽ 8,750',
    amount_crypto: '0.28',
    currency_crypto: 'BTC',
    type: 'payout' as const,
    status: 'failed' as const,
    trader: null,
    requisite: null
  }
];

const mockUsers = [
  {
    id: 'user_001',
    username: 'problem_user',
    email: 'user@example.com',
    role: 'merchant' as const,
    status: 'blocked' as const,
    created_date: '2024-01-15',
    last_active: '2024-12-14 23:45',
    total_orders: 156,
    merchant_store_count: 3
  }
];

const mockPlatformData = {
  total_users: 15643,
  active_merchants: 892,
  active_traders: 234,
  total_orders_today: 1247,
  total_volume_today: '₽ 12,450,000',
  platform_revenue: '₽ 245,600',
  success_rate: 97.8,
  avg_processing_time: '4.2 мин',
  platform_balance: '₽ 2,340,000',
  merchant_balance: '₽ 15,670,000',
  trader_balance: '₽ 8,920,000'
};

export default function SupportDashboard() {
  return (
    <SupportLayout>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-primary">
              Панель поддержки
            </h1>
            <p className="text-secondary mt-1">
              Управление тикетами, пользователями и проблемными ордерами
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <button className="px-4 py-2 bg-success text-white rounded-lg hover:bg-green-600 transition-colors">
              Создать тикет
            </button>
            <button className="px-4 py-2 bg-warning text-white rounded-lg hover:bg-yellow-600 transition-colors">
              Экстренный режим
            </button>
          </div>
        </div>

        {/* Support Metrics */}
        <div>
          <h2 className="text-xl font-semibold text-primary mb-4">
            Метрики поддержки
          </h2>
          <MetricsGrid 
            metrics={mockMetrics}
            columns={4}
          />
        </div>

        {/* Platform Overview */}
        <div>
          <h2 className="text-xl font-semibold text-primary mb-4">
            Состояние платформы
          </h2>
          <PlatformMetrics 
            data={mockPlatformData}
            showFinancials={false}
            showBalances={false}
          />
        </div>

        {/* Problem Orders */}
        <div>
          <h2 className="text-xl font-semibold text-primary mb-4">
            Проблемные ордера
          </h2>
          <OrdersTable 
            orders={mockOrders}
            showColumns={{
              trader: true,
              commissions: false,
              store: false,
              crypto: true,
              actions: true
            }}
          />
        </div>

        {/* Problem Users */}
        <div>
          <h2 className="text-xl font-semibold text-primary mb-4">
            Пользователи с проблемами
          </h2>
          <UserManagement 
            users={mockUsers}
            allowedActions={{
              view: true,
              edit: true,
              delete: false,
              block: true,
              changeRole: false
            }}
            showColumns={{
              team: false,
              balances: true,
              statistics: true,
              lastActive: true
            }}
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card-base p-6">
            <h3 className="font-semibold text-primary mb-3">
              Быстрые действия
            </h3>
            <div className="space-y-3">
              <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors">
                Массовое назначение тикетов
              </button>
              <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors">
                Экспорт отчета за день
              </button>
              <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors">
                Системное уведомление
              </button>
            </div>
          </div>

          <div className="card-base p-6">
            <h3 className="font-semibold text-primary mb-3">
              Статистика команды
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-secondary">Онлайн сейчас:</span>
                <span className="text-primary font-medium">5 агентов</span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary">Средний рейтинг:</span>
                <span className="text-primary font-medium">4.8/5</span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary">Решено сегодня:</span>
                <span className="text-primary font-medium">89 тикетов</span>
              </div>
            </div>
          </div>

          <div className="card-base p-6">
            <h3 className="font-semibold text-primary mb-3">
              Системные уведомления
            </h3>
            <div className="space-y-2 text-sm">
              <div className="p-2 bg-warning/10 text-warning rounded">
                Превышен лимит ожидания ответа
              </div>
              <div className="p-2 bg-success/10 text-success rounded">
                Все системы работают стабильно
              </div>
              <div className="p-2 bg-info/10 text-info rounded">
                Обновление в 2:00 МСК
              </div>
            </div>
          </div>
        </div>
    </div>
    </SupportLayout>
  );
}
