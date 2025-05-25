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
          <h1 className="text-2xl font-bold text-primary">Доступ запрещен</h1>
          <p className="text-secondary mt-2">У вас нет прав для просмотра финансовой информации</p>
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
          <div className="bg-surface rounded-lg p-6">
            <h3 className="text-lg font-semibold text-primary mb-4">
              Общий баланс
            </h3>
            <div className="text-3xl font-bold text-accent">
              ₽ {Math.round(Number(platformMetrics?.platform_balance) || 0).toLocaleString()}
            </div>
            <div className="text-sm text-secondary mt-2">
              В работе: ₽ {Math.round((Number(platformMetrics?.platform_balance) || 0) * 0.7).toLocaleString()}
            </div>
          </div>

          <div className="bg-surface rounded-lg p-6">
            <h3 className="text-lg font-semibold text-primary mb-4">
              Доходы платформы
            </h3>
            <div className="text-3xl font-bold text-success">
              ₽ {Math.round(Number(platformMetrics?.platform_revenue) || 0).toLocaleString()}
            </div>
            <div className="text-sm text-secondary mt-2">
              За текущий месяц
            </div>
          </div>

          <div className="bg-surface rounded-lg p-6">
            <h3 className="text-lg font-semibold text-primary mb-4">
              Комиссионные
            </h3>
            <div className="text-3xl font-bold text-info">
              ₽ {Math.round(Number(platformMetrics?.platform_revenue) || 0).toLocaleString()}
            </div>
            <div className="text-sm text-secondary mt-2">
              Средняя комиссия: 2.5%
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
      
      <div className="bg-surface rounded-lg p-6">
        <h3 className="text-lg font-semibold text-primary mb-4">
          Разбивка по периодам
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <div className="text-2xl font-bold text-accent">
              ₽ {Math.round(Number(platformMetrics?.total_volume_today) || 0).toLocaleString()}
            </div>
            <div className="text-sm text-secondary">Сегодня</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-success">
              ₽ {Math.round((Number(platformMetrics?.total_volume_today) || 0) * 0.7).toLocaleString()}
            </div>
            <div className="text-sm text-secondary">На неделе</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-info">
              ₽ {Math.round((Number(platformMetrics?.total_volume_today) || 0) * 0.3).toLocaleString()}
            </div>
            <div className="text-sm text-secondary">В месяце</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-warning">
              ₽ {Math.round((Number(platformMetrics?.total_volume_today) || 0) * 0.1).toLocaleString()}
            </div>
            <div className="text-sm text-secondary">За год</div>
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
      
      <div className="bg-surface rounded-lg p-6">
        <h3 className="text-lg font-semibold text-primary mb-4">
          Настройки комиссий
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <span className="text-primary">Комиссия с мерчантов:</span>
            <span className="font-medium text-accent">2.5%</span>
          </div>
          <div className="space-y-2">
            <span className="text-primary">Комиссия с трейдеров:</span>
            <span className="font-medium text-accent">1.5%</span>
          </div>
          <div className="space-y-2">
            <span className="text-primary">Минимальная комиссия:</span>
            <span className="font-medium text-accent">₽ 10</span>
          </div>
          <div className="space-y-2">
            <span className="text-primary">Комиссия за вывод:</span>
            <span className="font-medium text-warning">₽ 50</span>
          </div>
          <div className="space-y-2">
            <span className="text-primary">Комиссия за неактивность:</span>
            <span className="font-medium text-error">₽ 100/мес</span>
          </div>
          <div className="space-y-2">
            <span className="text-primary">Общий доход сегодня:</span>
            <span className="font-medium text-success">
              ₽ {Math.round(Number(platformMetrics?.platform_revenue) || 0).toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  const getRevenueContent = () => (
    <div className="space-y-6">
      <div className="bg-surface rounded-lg p-6">
        <h3 className="text-lg font-semibold text-primary mb-4">
          Доходы платформы
        </h3>
        <div className="text-center mb-6">
          <div className="text-4xl font-bold text-success">
            ₽ {Math.round(Number(platformMetrics?.platform_revenue) || 0).toLocaleString()}
          </div>
          <div className="text-sm text-secondary mt-1">
            За текущий месяц
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-background rounded-lg">
            <div className="text-2xl font-bold text-accent">
              ₽ {Math.round((Number(platformMetrics?.platform_revenue) || 0) * 0.3).toLocaleString()}
            </div>
            <div className="text-sm text-secondary">За неделю</div>
          </div>
          <div className="text-center p-4 bg-background rounded-lg">
            <div className="text-2xl font-bold text-success">
              ₽ {Math.round((Number(platformMetrics?.platform_revenue) || 0) * 0.6).toLocaleString()}
            </div>
            <div className="text-sm text-secondary">За месяц</div>
          </div>
          <div className="text-center p-4 bg-background rounded-lg">
            <div className="text-2xl font-bold text-warning">
              ₽ {Math.round((Number(platformMetrics?.platform_revenue) || 0) * 0.1).toLocaleString()}
            </div>
            <div className="text-sm text-secondary">За год</div>
          </div>
        </div>
      </div>

      {/* Прогнозы и аналитика */}
      <div className="bg-surface rounded-lg p-6">
        <h3 className="text-lg font-semibold text-primary mb-4">
          Прогнозы и аналитика
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6 text-sm">
          <div>
            <span className="text-secondary">Прогноз на месяц:</span>
            <span className="text-success font-medium">₽ 195,000</span>
          </div>
          <div>
            <span className="text-secondary">Рост относительно прошлого месяца:</span>
            <span className="text-success font-medium">+12.3%</span>
          </div>
          <div>
            <span className="text-secondary">Средний доход в день:</span>
            <span className="text-primary font-medium">₽ 6,248</span>
          </div>
          <div>
            <span className="text-secondary">Лучший день:</span>
            <span className="text-success font-medium">₽ 15,670</span>
          </div>
          <div>
            <span className="text-secondary">Маржинальность:</span>
            <span className="text-accent font-medium">87.5%</span>
          </div>
          <div>
            <span className="text-secondary">ROI платформы:</span>
            <span className="text-success font-medium">245%</span>
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
          <div className="text-secondary">Загрузка финансовых данных...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Заголовок страницы */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-primary">
            Финансы JivaPay
          </h1>
          <p className="text-secondary mt-1">
            {role === 'admin' ? 'Полный доступ к финансовой отчетности' :
             'Доходы команды и аналитика'}
          </p>
        </div>

        {financeConfig.config.enableExport && (
          <button className="bg-accent text-white px-4 py-2 rounded-lg hover:opacity-90">
            Экспорт отчета
          </button>
        )}
      </div>

      {/* Вкладки с контентом */}
      <div className="bg-surface rounded-lg p-6">
        <TabGroup
          tabs={getTabs()}
          defaultTab="overview"
        />
      </div>
    </div>
  );
}; 