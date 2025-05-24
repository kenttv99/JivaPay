'use client';

import React, { useState } from 'react';
import { usePermissions } from '@jivapay/permissions';
import { UserManagement, UserItem } from '../../components/UserManagement/UserManagement';
import { USERS_CONFIGS, UserRole } from '../../configs/roleConfigs';
import { TabGroup } from '@jivapay/ui-kit';

interface UsersPageProps {
  // Mock данные для демонстрации - в реальности будут приходить из API хуков
  usersData?: UserItem[];
  isLoading?: boolean;
}

export const UsersPage: React.FC<UsersPageProps> = ({
  usersData = [],
  isLoading = false
}) => {
  const { userRole } = usePermissions();
  const role = userRole as UserRole;
  
  // Получаем конфигурацию для текущей роли
  const usersConfig = USERS_CONFIGS[role];
  const [activeTab, setActiveTab] = useState('all');

  if (!usersConfig) {
    return (
      <div className="p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-[var(--jiva-text)]">Доступ запрещен</h1>
          <p className="text-[var(--jiva-text-secondary)] mt-2">У вас нет прав для просмотра пользователей</p>
        </div>
      </div>
    );
  }

  // Фильтрация пользователей в зависимости от роли
  const getFilteredUsers = (filter: string = 'all'): UserItem[] => {
    let filteredUsers = usersData;

    // Фильтрация по ролям в зависимости от прав доступа
    if (!usersConfig.config.showAllRoles) {
      if (role === 'teamlead') {
        // Тимлид видит только трейдеров своей команды
        filteredUsers = filteredUsers.filter(user => 
          user.role === 'trader' && user.team_id === 'current_teamlead_team'
        );
      } else if (role === 'support') {
        // Саппорт видит только назначенных пользователей
        filteredUsers = filteredUsers.filter(user => 
          user.id.includes('assigned') // Мок логика назначения
        );
      }
    }

    // Дополнительная фильтрация по вкладкам
    if (filter !== 'all') {
      if (filter === 'admins') {
        filteredUsers = filteredUsers.filter(user => 
          ['admin', 'teamlead', 'support'].includes(user.role)
        );
      } else if (filter === 'business') {
        filteredUsers = filteredUsers.filter(user => 
          ['merchant', 'trader'].includes(user.role)
        );
      } else if (filter === 'active') {
        filteredUsers = filteredUsers.filter(user => user.status === 'active');
      } else if (filter === 'blocked') {
        filteredUsers = filteredUsers.filter(user => user.status === 'blocked');
      }
    }

    return filteredUsers;
  };

  // Статистика пользователей
  const getUserStats = () => {
    const allUsers = getFilteredUsers();
    return {
      total: allUsers.length,
      active: allUsers.filter(u => u.status === 'active').length,
      blocked: allUsers.filter(u => u.status === 'blocked').length,
      admins: allUsers.filter(u => ['admin', 'teamlead', 'support'].includes(u.role)).length,
      business: allUsers.filter(u => ['merchant', 'trader'].includes(u.role)).length
    };
  };

  const handleUserAction = (action: string, user: UserItem) => {
    console.log(`Action ${action} on user:`, user);
    // Здесь будет вызов API в зависимости от действия
  };

  const stats = getUserStats();
  const filteredUsers = getFilteredUsers(activeTab);

  // Вкладки в зависимости от роли
  const getTabs = () => {
    const baseTabs = [
      { id: 'all', label: `Все (${stats.total})`, content: null }
    ];

    if (usersConfig.config.showAllRoles) {
      baseTabs.push(
        { id: 'active', label: `Активные (${stats.active})`, content: null },
        { id: 'blocked', label: `Заблокированные (${stats.blocked})`, content: null },
        { id: 'admins', label: `Админы (${stats.admins})`, content: null },
        { id: 'business', label: `Бизнес (${stats.business})`, content: null }
      );
    } else {
      // Ограниченный набор вкладок для teamlead/support
      baseTabs.push(
        { id: 'active', label: `Активные (${stats.active})`, content: null }
      );
    }

    return baseTabs;
  };

  // Определяем права доступа к действиям
  const getAllowedActions = () => {
    return {
      view: true, // Все могут просматривать
      edit: usersConfig.config.enableRoleManagement && (
        usersConfig.permissions.editAny || usersConfig.permissions.editTeam
      ),
      delete: usersConfig.config.enableRoleManagement && 
        'deleteAny' in usersConfig.permissions,
      block: usersConfig.config.enableRoleManagement && (
        usersConfig.permissions.editAny || usersConfig.permissions.editTeam
      ),
      changeRole: usersConfig.config.enablePermissionManagement
    };
  };

  // Определяем какие колонки показывать
  const getShowColumns = () => {
    return {
      team: role === 'admin' || role === 'teamlead',
      balances: usersConfig.config.showSensitiveData,
      statistics: true,
      lastActive: true
    };
  };

  return (
    <div className="space-y-6">
      {/* Заголовок страницы */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-[var(--jiva-text)]">
            Управление пользователями
          </h1>
          <p className="text-[var(--jiva-text-secondary)] mt-1">
            {role === 'admin' ? 'Управление всеми пользователями системы' :
             role === 'teamlead' ? 'Управление трейдерами команды' :
             'Поддержка назначенных пользователей'}
          </p>
        </div>

        {usersConfig.config.enableRoleManagement && (
          <button className="bg-[var(--jiva-primary)] text-white px-4 py-2 rounded-lg hover:opacity-90">
            Создать пользователя
          </button>
        )}
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[var(--jiva-background-paper)] p-4 rounded-lg">
          <div className="text-2xl font-bold text-[var(--jiva-text)]">{stats.total}</div>
          <div className="text-sm text-[var(--jiva-text-secondary)]">Всего пользователей</div>
        </div>
        <div className="bg-[var(--jiva-background-paper)] p-4 rounded-lg">
          <div className="text-2xl font-bold text-[var(--jiva-success)]">{stats.active}</div>
          <div className="text-sm text-[var(--jiva-text-secondary)]">Активных</div>
        </div>
        {usersConfig.config.showAllRoles && (
          <>
            <div className="bg-[var(--jiva-background-paper)] p-4 rounded-lg">
              <div className="text-2xl font-bold text-[var(--jiva-error)]">{stats.blocked}</div>
              <div className="text-sm text-[var(--jiva-text-secondary)]">Заблокированных</div>
            </div>
            <div className="bg-[var(--jiva-background-paper)] p-4 rounded-lg">
              <div className="text-2xl font-bold text-[var(--jiva-info)]">{stats.business}</div>
              <div className="text-sm text-[var(--jiva-text-secondary)]">Бизнес пользователей</div>
            </div>
          </>
        )}
      </div>

      {/* Фильтры/Вкладки */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <TabGroup
          tabs={getTabs()}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />

        {/* Таблица пользователей */}
        <div className="mt-6">
          <UserManagement
            users={filteredUsers}
            allowedActions={getAllowedActions()}
            showColumns={getShowColumns()}
            onUserAction={handleUserAction}
            isLoading={isLoading}
          />
        </div>

        {filteredUsers.length === 0 && !isLoading && (
          <div className="text-center py-8">
            <div className="text-[var(--jiva-text-secondary)]">
              {activeTab === 'all' ? 'Пользователи не найдены' : 
               `Нет пользователей в категории "${getTabs().find(t => t.id === activeTab)?.label}"`}
            </div>
          </div>
        )}
      </div>

      {/* Дополнительная информация для админов */}
      {role === 'admin' && usersConfig.config.enablePermissionManagement && (
        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
          <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
            Системная информация
          </h3>
          <div className="grid grid-cols-3 gap-6 text-sm">
            <div>
              <div className="font-medium text-[var(--jiva-text)]">Роли системы:</div>
              <div className="text-[var(--jiva-text-secondary)] mt-1">
                <div>• Администратор (полный доступ)</div>
                <div>• Тимлид (управление командой)</div>
                <div>• Поддержка (помощь пользователям)</div>
                <div>• Мерчант (управление магазинами)</div>
                <div>• Трейдер (обработка ордеров)</div>
              </div>
            </div>
            <div>
              <div className="font-medium text-[var(--jiva-text)]">Статусы:</div>
              <div className="text-[var(--jiva-text-secondary)] mt-1">
                <div>• Активен - полный доступ</div>
                <div>• Неактивен - временно отключен</div>
                <div>• Заблокирован - доступ запрещен</div>
                <div>• Ожидание - требует активации</div>
              </div>
            </div>
            <div>
              <div className="font-medium text-[var(--jiva-text)]">Действия:</div>
              <div className="text-[var(--jiva-text-secondary)] mt-1">
                <div>• Просмотр - детали пользователя</div>
                <div>• Изменить - редактирование данных</div>
                <div>• Заблокировать - временная блокировка</div>
                <div>• Удалить - полное удаление</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 