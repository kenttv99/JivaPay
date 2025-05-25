'use client';

import React, { useState } from 'react';
import { usePermissions } from '@jivapay/permissions';
import { RequisiteManagement, RequisiteItem } from '../../components/RequisiteManagement/RequisiteManagement';
import { DASHBOARD_CONFIGS, UserRole } from '../../configs/roleConfigs';

interface RequisitesPageProps {
  // Mock данные для демонстрации - в реальности будут приходить из API хуков
  requisitesData?: RequisiteItem[];
  isLoading?: boolean;
}

export const RequisitesPage: React.FC<RequisitesPageProps> = ({
  requisitesData = [],
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
          <h1 className="text-2xl font-bold text-primary">Доступ запрещен</h1>
          <p className="text-secondary mt-2">У вас нет прав для управления реквизитами</p>
        </div>
      </div>
    );
  }

  // Конфигурация действий в зависимости от роли
  const getActionConfig = () => {
    switch (role) {
      case 'admin':
        return {
          view: true,
          moderate: true,
          block: true,
          setStatus: true
        };
      case 'teamlead':
        return {
          view: true,
          moderate: true,
          block: true,
          setStatus: true
        };
      case 'support':
        return {
          view: true,
          moderate: false,
          block: false,
          setStatus: false
        };
      default:
        return {
          view: true,
          moderate: false,
          block: false,
          setStatus: false
        };
    }
  };

  // Конфигурация отображаемых колонок
  const getColumnConfig = () => {
    switch (role) {
      case 'admin':
        return {
          trader: true,
          team: true,
          statistics: true,
          onlineStatus: true,
          lastUsed: true
        };
      case 'teamlead':
        return {
          trader: true,
          team: true,
          statistics: true,
          onlineStatus: true,
          lastUsed: true
        };
      case 'support':
        return {
          trader: true,
          team: false,
          statistics: false,
          onlineStatus: true,
          lastUsed: true
        };
      default:
        return {
          trader: true,
          team: false,
          statistics: true,
          onlineStatus: true,
          lastUsed: true
        };
    }
  };

  const handleRequisiteAction = (action: string, requisite: RequisiteItem, data?: any) => {
    console.log(`Action: ${action}`, requisite, data);
    // Здесь будет вызов API в реальном приложении
    switch (action) {
      case 'moderate':
        console.log(`Модерация реквизита ${requisite.id}: ${data.action} - ${data.comment}`);
        break;
      case 'block':
        console.log(`Блокировка реквизита ${requisite.id}`);
        break;
      case 'unblock':
        console.log(`Разблокировка реквизита ${requisite.id}`);
        break;
      case 'activate':
        console.log(`Активация реквизита ${requisite.id}`);
        break;
    }
  };

  // Фильтрация реквизитов в зависимости от роли
  const getFilteredRequisites = () => {
    if (role === 'support') {
      // Для саппорта только проблемные реквизиты
      return requisitesData.filter(req => 
        req.status === 'moderation' || req.status === 'blocked'
      );
    }
    return requisitesData;
  };

  // Статистика реквизитов
  const getRequisiteStats = () => {
    const filtered = getFilteredRequisites();
    const totalCount = filtered.length;
    const activeCount = filtered.filter(req => req.status === 'active').length;
    const moderationCount = filtered.filter(req => req.status === 'moderation').length;
    const blockedCount = filtered.filter(req => req.status === 'blocked').length;
    const onlineCount = filtered.filter(req => req.is_online).length;

    return {
      totalCount,
      activeCount,
      moderationCount,
      blockedCount,
      onlineCount
    };
  };

  const stats = getRequisiteStats();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <div className="text-secondary">Загрузка реквизитов...</div>
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
            Управление реквизитами
          </h1>
          <p className="text-secondary mt-1">
            {role === 'admin' ? 'Полное управление всеми реквизитами' :
             role === 'teamlead' ? 'Управление реквизитами команды' :
             'Модерация реквизитов'}
          </p>
        </div>

        {dashboardConfig.config.enableExport && (
          <button className="bg-accent text-white px-4 py-2 rounded-lg hover:opacity-90">
            Экспорт списка
          </button>
        )}
      </div>

      {/* Статистика реквизитов */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-accent">
            {stats.totalCount}
          </div>
          <div className="text-sm text-secondary">
            Всего реквизитов
          </div>
        </div>

        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-success">
            {stats.activeCount}
          </div>
          <div className="text-sm text-secondary">
            Активных
          </div>
        </div>

        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-warning">
            {stats.moderationCount}
          </div>
          <div className="text-sm text-secondary">
            На модерации
          </div>
        </div>

        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-error">
            {stats.blockedCount}
          </div>
          <div className="text-sm text-secondary">
            Заблокированных
          </div>
        </div>

        <div className="bg-surface rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-info">
            {stats.onlineCount}
          </div>
          <div className="text-sm text-secondary">
            Онлайн
          </div>
        </div>
      </div>

      {/* Управление реквизитами */}
      <RequisiteManagement
        requisites={getFilteredRequisites()}
        allowedActions={getActionConfig()}
        showColumns={getColumnConfig()}
        onRequisiteAction={handleRequisiteAction}
        isLoading={isLoading}
      />

      {/* Дополнительная информация для разных ролей */}
      {role === 'admin' && (
        <div className="bg-surface rounded-lg p-6">
          <h3 className="text-lg font-semibold text-primary mb-4">
            Аналитика реквизитов
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm">
            <div>
              <span className="text-secondary">Среднее время модерации:</span>
              <span className="text-primary font-medium">2.3 часа</span>
            </div>
            <div>
              <span className="text-secondary">Процент одобрения:</span>
              <span className="text-success font-medium">87.5%</span>
            </div>
            <div>
              <span className="text-secondary">Новых реквизитов за день:</span>
              <span className="text-primary font-medium">12</span>
            </div>
            <div>
              <span className="text-secondary">Самый активный банк:</span>
              <span className="text-primary font-medium">Сбербанк</span>
            </div>
            <div>
              <span className="text-secondary">Средняя загрузка:</span>
              <span className="text-primary font-medium">78%</span>
            </div>
            <div>
              <span className="text-secondary">Требуют внимания:</span>
              <span className="text-warning font-medium">{stats.moderationCount + stats.blockedCount}</span>
            </div>
          </div>
        </div>
      )}

      {role === 'teamlead' && (
        <div className="bg-surface rounded-lg p-6">
          <h3 className="text-lg font-semibold text-primary mb-4">
            Управление командой
          </h3>
          <div className="grid grid-cols-3 gap-6">
            <div className="text-center p-4 bg-background rounded-lg">
              <div className="text-2xl font-bold text-accent">
                {Math.floor(stats.activeCount / 3)}
              </div>
              <div className="text-sm text-secondary">Трейдеров в команде</div>
            </div>
            <div className="text-center p-4 bg-background rounded-lg">
              <div className="text-2xl font-bold text-success">
                {((stats.activeCount / stats.totalCount) * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-secondary">Эффективность команды</div>
            </div>
            <div className="text-center p-4 bg-background rounded-lg">
              <div className="text-2xl font-bold text-info">
                ₽ 2.3M
              </div>
              <div className="text-sm text-secondary">Оборот за месяц</div>
            </div>
          </div>
        </div>
      )}

      {role === 'support' && stats.moderationCount > 0 && (
        <div className="bg-warning-light border border-warning rounded-lg p-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-warning rounded-full"></div>
            <span className="font-medium text-primary">
              Внимание: {stats.moderationCount} реквизитов требуют модерации
            </span>
          </div>
        </div>
      )}
    </div>
  );
}; 