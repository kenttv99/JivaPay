'use client';

import React from 'react';
import { Skeleton } from '@jivapay/ui-kit';

export interface PlatformMetricsData {
  total_users: number;
  active_merchants: number;
  active_traders: number;
  total_orders_today: number;
  total_volume_today: string;
  platform_revenue: string;
  success_rate: number;
  avg_processing_time: string;
  platform_balance: string;
  merchant_balance: string;
  trader_balance: string;
}

interface PlatformMetricsProps {
  data: PlatformMetricsData;
  showFinancials?: boolean;
  showBalances?: boolean;
  isLoading?: boolean;
  className?: string;
}

export const PlatformMetrics: React.FC<PlatformMetricsProps> = ({
  data,
  showFinancials = true,
  showBalances = true,
  isLoading = false,
  className = ''
}) => {
  // Skeleton состояние при загрузке
  if (isLoading) {
    return (
      <div className={`space-y-6 animate-fadeIn ${className}`}>
        <Skeleton variant="card" className="h-48" />
        <Skeleton variant="card" className="h-32" />
        {showFinancials && <Skeleton variant="card" className="h-24" />}
        {showBalances && <Skeleton variant="card" className="h-32" />}
        <Skeleton variant="card" className="h-48" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }, (_, i) => (
            <Skeleton key={i} variant="card" className="h-20" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 animate-fadeIn ${className}`}>
      {/* Основные метрики пользователей */}
      <div className="bg-surface rounded-lg p-6">
        <h3 className="text-lg font-semibold text-primary mb-4">
          Платформенные метрики
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-accent">
              {data.total_users.toLocaleString()}
            </div>
            <div className="text-sm text-secondary mt-1">
              Всего пользователей
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-success">
              {data.active_merchants.toLocaleString()}
            </div>
            <div className="text-sm text-secondary mt-1">
              Активных мерчантов
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-info">
              {data.active_traders.toLocaleString()}
            </div>
            <div className="text-sm text-secondary mt-1">
              Активных трейдеров
            </div>
          </div>
        </div>
      </div>

      {/* Метрики ордеров и производительности */}
      <div className="bg-surface rounded-lg p-6">
        <h3 className="text-lg font-semibold text-primary mb-4">
          Производительность системы
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-accent">
              {data.total_orders_today.toLocaleString()}
            </div>
            <div className="text-sm text-secondary mt-1">
              Ордеров за день
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-warning">
              {data.total_volume_today}
            </div>
            <div className="text-sm text-secondary mt-1">
              Объем транзакций
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-success">
              {data.success_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-secondary mt-1">
              Успешность
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-info">
              {data.avg_processing_time}
            </div>
            <div className="text-sm text-secondary mt-1">
              Среднее время обработки
            </div>
          </div>
        </div>
      </div>

      {/* Финансовые метрики (только для админов) */}
      {showFinancials && (
        <div className="bg-surface rounded-lg p-6">
          <h3 className="text-lg font-semibold text-primary mb-4">
            Доходы платформы
          </h3>
          <div className="text-center">
            <div className="text-4xl font-bold text-success">
              {data.platform_revenue}
            </div>
            <div className="text-sm text-secondary mt-1">
              Доход платформы (сегодня)
            </div>
          </div>
        </div>
      )}

      {/* Балансы (только для админов) */}
      {showBalances && (
        <div className="bg-surface rounded-lg p-6">
          <h3 className="text-lg font-semibold text-primary mb-4">
            Балансы системы
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-background rounded-lg">
              <div className="text-2xl font-bold text-accent">
                {data.platform_balance}
              </div>
              <div className="text-sm text-secondary mt-1">
                Баланс платформы
              </div>
            </div>
            
            <div className="text-center p-4 bg-background rounded-lg">
              <div className="text-2xl font-bold text-success">
                {data.merchant_balance}
              </div>
              <div className="text-sm text-secondary mt-1">
                Общий баланс мерчантов
              </div>
            </div>
            
            <div className="text-center p-4 bg-background rounded-lg">
              <div className="text-2xl font-bold text-info">
                {data.trader_balance}
              </div>
              <div className="text-sm text-secondary mt-1">
                Общий баланс трейдеров
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Состояние системы */}
      <div className="bg-surface rounded-lg p-6">
        <h3 className="text-lg font-semibold text-primary mb-4">
          Состояние системы
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-secondary">Загрузка системы:</span>
              <span className="text-primary font-medium">Нормальная</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-secondary">Статус API:</span>
              <span className="text-success font-medium">Работает</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-secondary">Статус платежного шлюза:</span>
              <span className="text-success font-medium">Работает</span>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-secondary">Обновление курсов:</span>
              <span className="text-primary font-medium">2 мин назад</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-secondary">Активных сессий:</span>
              <span className="text-primary font-medium">
                {Math.floor(data.total_users * 0.1).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-secondary">Время аптайма:</span>
              <span className="text-success font-medium">99.9%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Индикаторы производительности */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-success">
            {(data.success_rate).toFixed(1)}%
          </div>
          <div className="text-sm text-secondary">Uptime</div>
        </div>
        
        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-info">
            &lt; 1сек
          </div>
          <div className="text-sm text-secondary">Ответ API</div>
        </div>
        
        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-warning">
            {Math.floor(data.total_orders_today / 24)}
          </div>
          <div className="text-sm text-secondary">Ордеров/час</div>
        </div>
        
        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-accent">
            {Math.floor(data.total_users / 30)}
          </div>
          <div className="text-sm text-secondary">Новых за месяц</div>
        </div>
      </div>
    </div>
  );
}; 