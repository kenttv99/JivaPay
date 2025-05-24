'use client';

import React, { useState } from 'react';
import { usePermissions } from '@jivapay/permissions';
import { BalanceChart, BalanceChartData } from '../../components/BalanceChart/BalanceChart';
import { PlatformMetrics, PlatformMetricsData } from '../../components/PlatformMetrics/PlatformMetrics';
import { TabGroup } from '@jivapay/ui-kit';
import { FINANCE_CONFIGS, UserRole } from '../../configs/roleConfigs';

interface FinancePageProps {
  // Mock данные для демонстрации - в реальности будут приходить из API хуков
  balanceData?: BalanceChartData[];
  platformMetrics?: PlatformMetricsData;
  isLoading?: boolean;
}

export const FinancePage: React.FC<FinancePageProps> = ({
  balanceData = [],
  platformMetrics,
  isLoading = false
}) => {
  const { userRole } = usePermissions();
  const role = userRole as UserRole;
  
  // Получаем конфигурацию для текущей роли
  const financeConfig = FINANCE_CONFIGS[role];

  if (!financeConfig) {
    return (
      <div className="p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-[var(--jiva-text)]">Доступ запрещен</h1>
          <p className="text-[var(--jiva-text-secondary)] mt-2">У вас нет прав для просмотра финансовой информации</p>
        </div>
      </div>
    );
  }

  // Создание контента для вкладок
  const getOverviewContent = () => (
    <div className="space-y-6">
      {platformMetrics && (
        <PlatformMetrics
          data={platformMetrics}
          showFinancials={financeConfig.config.showPlatformRevenue}
          showBalances={financeConfig.config.showSensitiveData}
        />
      )}
    </div>
  );

  const getBalancesContent = () => (
    <div className="space-y-6">
      <BalanceChart
        data={balanceData}
        type="balances"
        title="Динамика балансов"
        height={400}
      />
      
      {financeConfig.config.showSensitiveData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
            <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
              Баланс платформы
            </h3>
            <div className="text-3xl font-bold text-[var(--jiva-primary)]">
              {platformMetrics?.platform_balance || '₽ 0'}
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)] mt-2">
              Средства платформы
            </div>
          </div>

          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
            <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
              Баланс мерчантов
            </h3>
            <div className="text-3xl font-bold text-[var(--jiva-success)]">
              {platformMetrics?.merchant_balance || '₽ 0'}
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)] mt-2">
              Общий баланс всех мерчантов
            </div>
          </div>

          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
            <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
              Баланс трейдеров
            </h3>
            <div className="text-3xl font-bold text-[var(--jiva-info)]">
              {platformMetrics?.trader_balance || '₽ 0'}
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)] mt-2">
              Общий баланс всех трейдеров
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const getVolumeContent = () => (
    <div className="space-y-6">
      <BalanceChart
        data={balanceData}
        type="volume"
        title="Объемы транзакций"
        height={400}
      />
      
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Статистика объемов
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-[var(--jiva-primary)]">
              {platformMetrics?.total_volume_today || '₽ 0'}
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)]">Сегодня</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-[var(--jiva-success)]">
              ₽ 2.5M
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)]">На неделе</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-[var(--jiva-info)]">
              ₽ 8.7M
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)]">В месяце</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-[var(--jiva-warning)]">
              ₽ 45.2M
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)]">За год</div>
          </div>
        </div>
      </div>
    </div>
  );

  const getCommissionsContent = () => (
    <div className="space-y-6">
      <BalanceChart
        data={balanceData}
        type="commissions"
        title="Комиссии платформы"
        height={400}
      />
      
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Настройки комиссий
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text)]">Комиссия с мерчантов:</span>
              <span className="font-medium text-[var(--jiva-primary)]">2.5%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text)]">Комиссия с трейдеров:</span>
              <span className="font-medium text-[var(--jiva-primary)]">1.5%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text)]">Минимальная комиссия:</span>
              <span className="font-medium text-[var(--jiva-primary)]">₽ 10</span>
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text)]">Комиссия за вывод:</span>
              <span className="font-medium text-[var(--jiva-warning)]">₽ 50</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text)]">Комиссия за неактивность:</span>
              <span className="font-medium text-[var(--jiva-error)]">₽ 100/мес</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text)]">Общий доход сегодня:</span>
              <span className="font-medium text-[var(--jiva-success)]">
                {platformMetrics?.platform_revenue || '₽ 0'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const getRevenueContent = () => (
    <div className="space-y-6">
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Доходы платформы
        </h3>
        <div className="text-center mb-6">
          <div className="text-4xl font-bold text-[var(--jiva-success)]">
            {platformMetrics?.platform_revenue || '₽ 0'}
          </div>
          <div className="text-sm text-[var(--jiva-text-secondary)] mt-1">
            Доход за сегодня
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-[var(--jiva-background)] rounded-lg">
            <div className="text-2xl font-bold text-[var(--jiva-primary)]">
              ₽ 45,230
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)]">За неделю</div>
          </div>
          <div className="text-center p-4 bg-[var(--jiva-background)] rounded-lg">
            <div className="text-2xl font-bold text-[var(--jiva-success)]">
              ₽ 187,450
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)]">За месяц</div>
          </div>
          <div className="text-center p-4 bg-[var(--jiva-background)] rounded-lg">
            <div className="text-2xl font-bold text-[var(--jiva-warning)]">
              ₽ 2,156,890
            </div>
            <div className="text-sm text-[var(--jiva-text-secondary)]">За год</div>
          </div>
        </div>
      </div>

      {/* Прогнозы и аналитика */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Прогнозы и аналитика
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">Прогноз на месяц:</span>
              <span className="text-[var(--jiva-success)] font-medium">₽ 195,000</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">Рост относительно прошлого месяца:</span>
              <span className="text-[var(--jiva-success)] font-medium">+12.3%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">Средний доход в день:</span>
              <span className="text-[var(--jiva-text)] font-medium">₽ 6,248</span>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">Лучший день:</span>
              <span className="text-[var(--jiva-success)] font-medium">₽ 15,670</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">Маржинальность:</span>
              <span className="text-[var(--jiva-primary)] font-medium">87.5%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--jiva-text-secondary)]">ROI платформы:</span>
              <span className="text-[var(--jiva-success)] font-medium">245%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Создание вкладок с контентом
  const getTabs = () => {
    const tabs = [
      { key: 'overview', label: 'Обзор', content: getOverviewContent() }
    ];

    if (financeConfig.config.showBalanceCharts) {
      tabs.push({ key: 'balances', label: 'Балансы', content: getBalancesContent() });
    }

    if (financeConfig.config.showVolumeAnalytics) {
      tabs.push({ key: 'volume', label: 'Объемы', content: getVolumeContent() });
    }

    if (financeConfig.config.showCommissionAnalytics) {
      tabs.push({ key: 'commissions', label: 'Комиссии', content: getCommissionsContent() });
    }

    if (financeConfig.config.showPlatformRevenue) {
      tabs.push({ key: 'revenue', label: 'Доходы', content: getRevenueContent() });
    }

    return tabs;
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <div className="text-[var(--jiva-text-secondary)]">Загрузка финансовых данных...</div>
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
            Финансы и аналитика
          </h1>
          <p className="text-[var(--jiva-text-secondary)] mt-1">
            {role === 'admin' ? 'Полная финансовая аналитика платформы' :
             role === 'teamlead' ? 'Финансовая аналитика команды' :
             'Базовая финансовая информация'}
          </p>
        </div>

        {financeConfig.config.enableExport && (
          <button className="bg-[var(--jiva-primary)] text-white px-4 py-2 rounded-lg hover:opacity-90">
            Экспорт отчета
          </button>
        )}
      </div>

      {/* Вкладки с контентом */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <TabGroup
          tabs={getTabs()}
          defaultTab="overview"
        />
      </div>
    </div>
  );
}; 