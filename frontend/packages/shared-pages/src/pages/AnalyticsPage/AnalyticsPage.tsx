'use client';

import React, { useState } from 'react';
import { usePermissions } from '@jivapay/permissions';
import { OrderChart, OrderChartData } from '../../components/OrderChart/OrderChart';
import { BalanceChart, BalanceChartData } from '../../components/BalanceChart/BalanceChart';
import { TabGroup } from '@jivapay/ui-kit';
import { DASHBOARD_CONFIGS, UserRole } from '../../configs/roleConfigs';

interface AnalyticsPageProps {
  // Mock данные для демонстрации - в реальности будут приходить из API хуков
  orderData?: OrderChartData[];
  balanceData?: BalanceChartData[];
  isLoading?: boolean;
}

export const AnalyticsPage: React.FC<AnalyticsPageProps> = ({
  orderData = [],
  balanceData = [],
  isLoading = false
}) => {
  const { userRole } = usePermissions();
  const role = userRole as UserRole;
  
  // Получаем конфигурацию для текущей роли
  const dashboardConfig = DASHBOARD_CONFIGS[role];

  if (!dashboardConfig) {
    return (
      <div className="p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-[var(--jiva-text)]">Доступ запрещен</h1>
          <p className="text-[var(--jiva-text-secondary)] mt-2">У вас нет прав для просмотра аналитики</p>
        </div>
      </div>
    );
  }

  // Контент для вкладок
  const getOrdersAnalyticsContent = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <OrderChart
          data={orderData}
          type="orders"
          title="Динамика ордеров"
          height={350}
        />
        <OrderChart
          data={orderData}
          type="success_rate"
          title="Успешность выполнения"
          height={350}
        />
      </div>
      
      <OrderChart
        data={orderData}
        type="order_types"
        title="Распределение типов ордеров"
        height={400}
      />

      {/* Статистические карточки */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 text-center">
          <div className="text-3xl font-bold text-[var(--jiva-primary)]">
            {orderData.length > 0 ? orderData[orderData.length - 1].total_orders : 0}
          </div>
          <div className="text-sm text-[var(--jiva-text-secondary)] mt-1">
            Ордеров сегодня
          </div>
        </div>
        
        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 text-center">
          <div className="text-3xl font-bold text-[var(--jiva-success)]">
            {orderData.length > 0 ? orderData[orderData.length - 1].completed_orders : 0}
          </div>
          <div className="text-sm text-[var(--jiva-text-secondary)] mt-1">
            Выполнено
          </div>
        </div>
        
        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 text-center">
          <div className="text-3xl font-bold text-[var(--jiva-error)]">
            {orderData.length > 0 ? orderData[orderData.length - 1].failed_orders : 0}
          </div>
          <div className="text-sm text-[var(--jiva-text-secondary)] mt-1">
            Неудачных
          </div>
        </div>
        
        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 text-center">
          <div className="text-3xl font-bold text-[var(--jiva-warning)]">
            {orderData.length > 0 ? `${orderData[orderData.length - 1].success_rate?.toFixed(1)}%` : '0%'}
          </div>
          <div className="text-sm text-[var(--jiva-text-secondary)] mt-1">
            Успешность
          </div>
        </div>
      </div>
    </div>
  );

  const getVolumeAnalyticsContent = () => (
    <div className="space-y-6">
      <BalanceChart
        data={balanceData}
        type="volume"
        title="Объемы транзакций"
        height={400}
      />
      
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Анализ объемов
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-[var(--jiva-background)] rounded-lg">
            <div className="text-2xl font-bold text-[var(--jiva-primary)]">
              ₽ 1.2M
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)]">Сегодня</div>
            <div className="text-xs text-[var(--jiva-success)] mt-1">+15.3%</div>
          </div>
          <div className="text-center p-4 bg-[var(--jiva-background)] rounded-lg">
            <div className="text-2xl font-bold text-[var(--jiva-success)]">
              ₽ 8.5M
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)]">За неделю</div>
            <div className="text-xs text-[var(--jiva-success)] mt-1">+8.7%</div>
          </div>
          <div className="text-center p-4 bg-[var(--jiva-background)] rounded-lg">
            <div className="text-2xl font-bold text-[var(--jiva-info)]">
              ₽ 32M
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)]">За месяц</div>
            <div className="text-xs text-[var(--jiva-success)] mt-1">+22.1%</div>
          </div>
          <div className="text-center p-4 bg-[var(--jiva-background)] rounded-lg">
            <div className="text-2xl font-bold text-[var(--jiva-warning)]">
              ₽ 145M
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)]">За год</div>
            <div className="text-xs text-[var(--jiva-success)] mt-1">+67.2%</div>
          </div>
        </div>
      </div>

      {/* Топ пользователей по объемам */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Топ пользователей по объемам
        </h3>
        <div className="space-y-3">
          {[
            { name: 'Мерчант "TechShop"', volume: '₽ 2.1M', growth: '+45%' },
            { name: 'Трейдер "AlexPay"', volume: '₽ 1.8M', growth: '+38%' },
            { name: 'Мерчант "GameStore"', volume: '₽ 1.5M', growth: '+28%' },
            { name: 'Трейдер "CryptoMax"', volume: '₽ 1.2M', growth: '+22%' },
            { name: 'Мерчант "FashionPay"', volume: '₽ 980K', growth: '+15%' }
          ].map((user, index) => (
            <div key={index} className="flex justify-between items-center p-3 bg-[var(--jiva-background)] rounded-lg">
              <div>
                <div className="font-medium text-[var(--jiva-text)]">{user.name}</div>
                <div className="text-sm text-[var(--jiva-text-secondary)]">За месяц</div>
              </div>
              <div className="text-right">
                <div className="font-bold text-[var(--jiva-primary)]">{user.volume}</div>
                <div className="text-sm text-[var(--jiva-success)]">{user.growth}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const getPerformanceContent = () => (
    <div className="space-y-6">
      {/* Основные KPI */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
          <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
            Время обработки
          </h3>
          <div className="text-center">
            <div className="text-4xl font-bold text-[var(--jiva-success)]">2.3 мин</div>
            <div className="text-sm text-[var(--jiva-text-secondary)] mt-1">
              Среднее время
            </div>
            <div className="text-xs text-[var(--jiva-success)] mt-2">
              -15% к прошлому месяцу
            </div>
          </div>
        </div>

        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
          <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
            Система доступности
          </h3>
          <div className="text-center">
            <div className="text-4xl font-bold text-[var(--jiva-success)]">99.8%</div>
            <div className="text-sm text-[var(--jiva-text-secondary)] mt-1">
              Uptime
            </div>
            <div className="text-xs text-[var(--jiva-text-secondary)] mt-2">
              Последние 30 дней
            </div>
          </div>
        </div>

        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
          <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
            Нагрузка API
          </h3>
          <div className="text-center">
            <div className="text-4xl font-bold text-[var(--jiva-warning)]">1.2K</div>
            <div className="text-sm text-[var(--jiva-text-secondary)] mt-1">
              Запросов/мин
            </div>
            <div className="text-xs text-[var(--jiva-info)] mt-2">
              Нормальная нагрузка
            </div>
          </div>
        </div>
      </div>

      {/* Мониторинг системы */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Мониторинг системы
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">Загрузка CPU:</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-2 bg-[var(--jiva-background)] rounded-full overflow-hidden">
                  <div className="w-1/4 h-full bg-[var(--jiva-success)]"></div>
                </div>
                <span className="text-[var(--jiva-text)] font-medium">25%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">Использование RAM:</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-2 bg-[var(--jiva-background)] rounded-full overflow-hidden">
                  <div className="w-3/5 h-full bg-[var(--jiva-warning)]"></div>
                </div>
                <span className="text-[var(--jiva-text)] font-medium">60%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">Дисковое пространство:</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-2 bg-[var(--jiva-background)] rounded-full overflow-hidden">
                  <div className="w-1/3 h-full bg-[var(--jiva-info)]"></div>
                </div>
                <span className="text-[var(--jiva-text)] font-medium">33%</span>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">База данных:</span>
              <span className="text-[var(--jiva-success)] font-medium">Работает</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">Redis кэш:</span>
              <span className="text-[var(--jiva-success)] font-medium">Работает</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">Очередь задач:</span>
              <span className="text-[var(--jiva-success)] font-medium">Работает</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Создание вкладок
  const getTabs = () => {
    const tabs = [
      { key: 'orders', label: 'Ордера', content: getOrdersAnalyticsContent() }
    ];

    if (dashboardConfig.config.showAdvancedMetrics) {
      tabs.push({ key: 'volume', label: 'Объемы', content: getVolumeAnalyticsContent() });
      tabs.push({ key: 'performance', label: 'Производительность', content: getPerformanceContent() });
    }

    return tabs;
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <div className="text-[var(--jiva-text-secondary)]">Загрузка аналитических данных...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Заголовок страницы */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-[var(--jiva-text)]">
            Аналитика и отчеты
          </h1>
          <p className="text-[var(--jiva-text-secondary)] mt-1">
            {role === 'admin' ? 'Полная аналитика платформы' :
             role === 'teamlead' ? 'Аналитика команды' :
             'Базовая аналитика'}
          </p>
        </div>

        {dashboardConfig.config.enableExport && (
          <button className="bg-[var(--jiva-primary)] text-white px-4 py-2 rounded-lg hover:opacity-90">
            Экспорт отчета
          </button>
        )}
      </div>

      {/* Вкладки с аналитикой */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <TabGroup
          tabs={getTabs()}
          defaultTab="orders"
        />
      </div>
    </div>
  );
}; 