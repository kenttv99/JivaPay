'use client';

import { StatsCard, DataTable, Alert, Spinner } from '@jivapay/ui-kit';
import { Button } from '@/components/Button';
import { Card } from '@/components/Card';
import { useState } from 'react';

export default function TraderDashboard() {
  const [loading] = useState(false);

  // Mock данные для демонстрации
  const mockRequisites = [
    { id: '1', bank: 'Сбербанк', number: '****1234', status: 'active', balance: '50,000' },
    { id: '2', bank: 'Тинькофф', number: '****5678', status: 'inactive', balance: '25,000' },
    { id: '3', bank: 'ВТБ', number: '****9012', status: 'processing', balance: '75,000' }
  ];

  const columns = [
    { key: 'bank', title: 'Банк' },
    { key: 'number', title: 'Номер карты' },
    { key: 'status', title: 'Статус', render: (value: string) => (
      <span className={`status-badge ${value === 'active' ? 'status-success' : value === 'processing' ? 'status-warning' : 'status-error'}`}>
        {value === 'active' ? 'Активна' : value === 'processing' ? 'Обработка' : 'Неактивна'}
      </span>
    )},
    { key: 'balance', title: 'Баланс', align: 'right' as const, render: (value: string) => `₽ ${value}` }
  ];

  return (
    <div className="min-h-screen bg-[var(--color-bg)] text-[var(--color-primary)] p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Заголовок */}
        <div>
          <h1 className="text-3xl font-bold">Панель трейдера</h1>
          <p className="text-[var(--color-secondary)] mt-1">Управление реквизитами и ордерами</p>
        </div>

        {/* Уведомления */}
        <Alert type="info" title="Информация">
          Демонстрационная страница трейдера с использованием локальных компонентов Button и Card
        </Alert>

        {/* Основные метрики */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Активные реквизиты"
            value="12"
            change="+2"
            trend="up"
            subtitle="за неделю"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            }
          />
          
          <StatsCard
            title="Ордера в работе"
            value="8"
            change="+3"
            trend="up"
            subtitle="сегодня"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
            }
          />
          
          <StatsCard
            title="Доход за день"
            value="₽ 12,500"
            change="+15.2%"
            trend="up"
            subtitle="к вчера"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />
          
          <StatsCard
            title="Средний чек"
            value="₽ 1,580"
            change="-2.1%"
            trend="down"
            subtitle="за неделю"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
          />
        </div>

        {/* Быстрые действия */}
        <Card className="p-6">
          <h2 className="text-xl font-bold mb-4">Быстрые действия</h2>
          <div className="flex gap-4">
            <Button variant="primary">
              Добавить реквизит
            </Button>
            <Button variant="secondary">
              Просмотр ордеров
            </Button>
            <Button variant="outline">
              Статистика
            </Button>
          </div>
        </Card>

        {/* Таблица реквизитов */}
        <Card className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Мои реквизиты</h2>
            {loading && <Spinner size="sm" />}
          </div>
          
          <DataTable
            columns={columns}
            data={mockRequisites}
            loading={loading}
            emptyText="Нет активных реквизитов"
          />
        </Card>
      </div>
    </div>
  );
}
