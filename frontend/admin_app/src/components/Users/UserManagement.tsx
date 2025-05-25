import React from 'react';
import { DataTable, StatusBadge, TabGroup } from '@jivapay/ui-kit';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'merchant' | 'trader' | 'support' | 'teamlead';
  status: 'active' | 'inactive' | 'blocked' | 'pending';
  lastActive: string;
  registrationDate: string;
  stores?: number;
  teamSize?: number;
  permissions?: string[];
  roleDescription?: string;
  teamlead?: string;
  trafficEnabled?: boolean;
}

interface UserManagementProps {
  users: User[];
  loading?: boolean;
}

const ROLE_NAMES = {
  admin: 'Администраторы',
  merchant: 'Мерчанты',
  trader: 'Трейдеры',
  support: 'Саппорт',
  teamlead: 'Тимлиды'
};

const ROLE_DISPLAY_NAMES = {
  admin: 'Администратор',
  merchant: 'Мерчант',
  trader: 'Трейдер',
  support: 'Саппорт',
  teamlead: 'Тимлид'
};

export const UserManagement: React.FC<UserManagementProps> = ({ users, loading }) => {
  const usersByRole = users.reduce((acc, user) => {
    if (!acc[user.role]) acc[user.role] = [];
    acc[user.role].push(user);
    return acc;
  }, {} as Record<string, User[]>);

  const getBaseColumns = () => [
    {
      key: 'name',
      title: 'Имя',
      render: (value: string) => <span className="font-medium">{value}</span>
    },
    {
      key: 'email',
      title: 'Email',
      render: (value: string) => <span className="text-secondary">{value}</span>
    },
    {
      key: 'role',
      title: 'Роль',
      render: (value: string) => (
        <span className="px-2 py-1 bg-background text-primary rounded text-xs font-medium">
          {ROLE_DISPLAY_NAMES[value as keyof typeof ROLE_DISPLAY_NAMES]}
        </span>
      )
    }
  ];

  const getColumnsForRole = (role: string) => {
    const baseColumns = getBaseColumns();
    const extraColumns = [];

    if (role === 'merchant') {
      extraColumns.push({
        key: 'stores',
        title: 'Магазины',
        render: (value: number) => `${value || 0} шт.`
      });
    }

    if (role === 'teamlead') {
      extraColumns.push({
        key: 'teamSize',
        title: 'Команда',
        render: (value: number) => `${value || 0} чел.`
      });
    }

    if (role === 'trader') {
      extraColumns.push({
        key: 'trafficEnabled',
        title: 'Трафик',
        render: (value: boolean, row: User) => (
          <div className="space-y-1">
            <div className="flex items-center">
              <span className={`w-2 h-2 rounded-full mr-2 ${value ? 'bg-success' : 'bg-error'}`}></span>
              <span className="text-xs">{value ? 'Включен' : 'Отключен'}</span>
            </div>
            {row.teamlead && (
              <div className="text-xs text-secondary">
                Тимлид: {row.teamlead}
              </div>
            )}
          </div>
        )
      });
    }

    if (role === 'admin') {
      extraColumns.push({
        key: 'permissions',
        title: 'Права',
        render: (value: string[]) => (
          <span className="text-xs">
            {value?.includes('*:*:*') ? 'Полные права' : `${value?.length || 0} прав`}
          </span>
        )
      });
    }

    if (role === 'support') {
      extraColumns.push({
        key: 'roleDescription',
        title: 'Описание',
        render: (value: string) => (
          <span className="text-xs text-secondary">{value}</span>
        )
      });
    }

    return [
      ...baseColumns,
      ...extraColumns,
      {
        key: 'status',
        title: 'Статус',
        render: (value: 'active' | 'inactive' | 'blocked' | 'pending') => (
          <StatusBadge status={value} />
        )
      },
      {
        key: 'lastActive',
        title: 'Активность',
        render: (value: string) => (
          <div className="text-xs text-secondary">{value}</div>
        )
      },
      {
        key: 'actions',
        title: 'Действия',
        align: 'right' as const,
        render: () => (
          <div className="flex gap-2 justify-end">
            <button className="text-accent hover:opacity-90 text-xs">
              Редактировать
            </button>
            <button className="text-error hover:opacity-90 text-xs">
              Заблокировать
            </button>
          </div>
        )
      }
    ];
  };

  const tabs = Object.entries(ROLE_NAMES).map(([role, label]) => ({
    key: role,
    label,
    count: usersByRole[role]?.length || 0,
    content: (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="Найти пользователя..."
              className="px-3 py-2 border border-border rounded-md text-sm"
            />
            <select className="px-3 py-2 border border-border rounded-md text-sm">
              <option value="">Все роли</option>
              <option value="admin">Администратор</option>
              <option value="merchant">Мерчант</option>
              <option value="trader">Трейдер</option>
            </select>
          </div>
          <button className="px-4 py-2 bg-accent text-white rounded-md hover:opacity-90 transition-colors text-sm">
            Добавить пользователя
          </button>
        </div>
        
        <DataTable
          columns={getColumnsForRole(role)}
          data={usersByRole[role] || []}
          loading={loading}
          emptyText={`Нет пользователей с ролью "${label}"`}
        />
      </div>
    )
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Пользователи</h1>
        <p className="text-secondary mt-1">
          Управление пользователями системы
        </p>
      </div>

      <TabGroup tabs={tabs} defaultTab="admin" />
    </div>
  );
}; 