'use client';

import React, { useState } from 'react';
import { DataTable, StatusBadge } from '@jivapay/ui-kit';

export type UserRole = 'admin' | 'support' | 'teamlead' | 'merchant' | 'trader';
export type UserStatus = 'active' | 'inactive' | 'blocked' | 'pending';

export interface UserItem {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  created_date: string;
  last_active?: string;
  team_id?: string;
  merchant_store_count?: number;
  trader_requisite_count?: number;
  total_orders?: number;
  balance_fiat?: string;
  balance_crypto?: string;
}

interface UserManagementProps {
  users: UserItem[];
  allowedActions?: {
    view?: boolean;
    edit?: boolean;
    delete?: boolean;
    block?: boolean;
    changeRole?: boolean;
  };
  showColumns?: {
    team?: boolean;
    balances?: boolean;
    statistics?: boolean;
    lastActive?: boolean;
  };
  onUserAction?: (action: string, user: UserItem) => void;
  isLoading?: boolean;
  className?: string;
}

const UserRoleBadge: React.FC<{ role: UserRole }> = ({ role }) => {
  const roleConfig = {
    admin: { text: 'Админ', status: 'success' as const },
    teamlead: { text: 'Тимлид', status: 'processing' as const },
    support: { text: 'Поддержка', status: 'pending' as const },
    merchant: { text: 'Мерчант', status: 'success' as const },
    trader: { text: 'Трейдер', status: 'processing' as const }
  };

  const config = roleConfig[role];
  return <StatusBadge status={config.status}>{config.text}</StatusBadge>;
};

const UserStatusBadge: React.FC<{ status: UserStatus }> = ({ status }) => {
  const statusConfig = {
    active: { text: 'Активен', status: 'success' as const },
    inactive: { text: 'Неактивен', status: 'inactive' as const },
    blocked: { text: 'Заблокирован', status: 'failed' as const },
    pending: { text: 'Ожидание', status: 'pending' as const }
  };

  const config = statusConfig[status];
  return <StatusBadge status={config.status}>{config.text}</StatusBadge>;
};

export const UserManagement: React.FC<UserManagementProps> = ({
  users,
  allowedActions = {
    view: true,
    edit: false,
    delete: false,
    block: false,
    changeRole: false
  },
  showColumns = {
    team: false,
    balances: false,
    statistics: true,
    lastActive: true
  },
  onUserAction,
  isLoading = false,
  className = ''
}) => {
  const [selectedUser, setSelectedUser] = useState<UserItem | null>(null);

  const handleUserAction = (action: string, user: UserItem) => {
    if (onUserAction) {
      onUserAction(action, user);
    }
    console.log(`${action} action for user:`, user);
  };

  const columns = [
    {
      key: 'username',
      title: 'Пользователь',
      render: (value: any, user: UserItem) => (
        <div>
          <div className="font-medium text-[var(--jiva-text)]">{user.username}</div>
          <div className="text-sm text-[var(--jiva-text-secondary)]">{user.email}</div>
        </div>
      )
    },
    {
      key: 'role',
      title: 'Роль',
      render: (value: any, user: UserItem) => <UserRoleBadge role={user.role} />
    },
    {
      key: 'status',
      title: 'Статус',
      render: (value: any, user: UserItem) => <UserStatusBadge status={user.status} />
    },
    {
      key: 'created_date',
      title: 'Дата регистрации',
      render: (value: any, user: UserItem) => (
        <span className="text-sm text-[var(--jiva-text-secondary)]">
          {user.created_date}
        </span>
      )
    },
    ...(showColumns.lastActive ? [{
      key: 'last_active',
      title: 'Последняя активность',
      render: (value: any, user: UserItem) => (
        <span className="text-sm text-[var(--jiva-text-secondary)]">
          {user.last_active || 'Неизвестно'}
        </span>
      )
    }] : []),
    ...(showColumns.team ? [{
      key: 'team_id',
      title: 'Команда',
      render: (value: any, user: UserItem) => (
        <span className="text-sm text-[var(--jiva-text-secondary)]">
          {user.team_id || '—'}
        </span>
      )
    }] : []),
    ...(showColumns.statistics ? [{
      key: 'statistics',
      title: 'Статистика',
      render: (value: any, user: UserItem) => (
        <div className="text-sm">
          {user.role === 'merchant' && (
            <div>Магазинов: {user.merchant_store_count || 0}</div>
          )}
          {user.role === 'trader' && (
            <div>Реквизитов: {user.trader_requisite_count || 0}</div>
          )}
          <div className="text-[var(--jiva-text-secondary)]">
            Ордеров: {user.total_orders || 0}
          </div>
        </div>
      )
    }] : []),
    ...(showColumns.balances ? [{
      key: 'balances',
      title: 'Балансы',
      render: (value: any, user: UserItem) => (
        <div className="text-sm">
          {user.balance_fiat && (
            <div>Фиат: {user.balance_fiat}</div>
          )}
          {user.balance_crypto && (
            <div className="text-[var(--jiva-text-secondary)]">
              Крипто: {user.balance_crypto}
            </div>
          )}
        </div>
      )
    }] : []),
    {
      key: 'actions',
      title: 'Действия',
      render: (value: any, user: UserItem) => (
        <div className="flex gap-2">
          {allowedActions.view && (
            <button
              onClick={() => handleUserAction('view', user)}
              className="text-[var(--jiva-primary)] hover:underline text-sm"
            >
              Просмотр
            </button>
          )}
          {allowedActions.edit && (
            <button
              onClick={() => handleUserAction('edit', user)}
              className="text-[var(--jiva-info)] hover:underline text-sm"
            >
              Изменить
            </button>
          )}
          {allowedActions.block && user.status === 'active' && (
            <button
              onClick={() => handleUserAction('block', user)}
              className="text-[var(--jiva-warning)] hover:underline text-sm"
            >
              Заблокировать
            </button>
          )}
          {allowedActions.delete && (
            <button
              onClick={() => handleUserAction('delete', user)}
              className="text-[var(--jiva-error)] hover:underline text-sm"
            >
              Удалить
            </button>
          )}
        </div>
      )
    }
  ];

  return (
    <div className={className}>
      <DataTable
        columns={columns}
        data={users}
        loading={isLoading}
      />
      
      {/* Детали выбранного пользователя */}
      {selectedUser && (
        <div className="mt-6 bg-[var(--jiva-background-paper)] border border-[var(--jiva-border-light)] rounded-lg p-6">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-lg font-semibold text-[var(--jiva-text)]">
              Детали пользователя {selectedUser.username}
            </h3>
            <button
              onClick={() => setSelectedUser(null)}
              className="text-[var(--jiva-text-secondary)] hover:text-[var(--jiva-text)]"
            >
              ✕
            </button>
          </div>
          
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-3">
              <div>
                <span className="font-medium text-[var(--jiva-text)]">ID:</span>
                <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedUser.id}</span>
              </div>
              <div>
                <span className="font-medium text-[var(--jiva-text)]">Email:</span>
                <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedUser.email}</span>
              </div>
              <div>
                <span className="font-medium text-[var(--jiva-text)]">Роль:</span>
                <span className="ml-2"><UserRoleBadge role={selectedUser.role} /></span>
              </div>
              <div>
                <span className="font-medium text-[var(--jiva-text)]">Статус:</span>
                <span className="ml-2"><UserStatusBadge status={selectedUser.status} /></span>
              </div>
            </div>
            
            <div className="space-y-3">
              <div>
                <span className="font-medium text-[var(--jiva-text)]">Дата регистрации:</span>
                <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedUser.created_date}</span>
              </div>
              {selectedUser.last_active && (
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Последняя активность:</span>
                  <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedUser.last_active}</span>
                </div>
              )}
              {selectedUser.team_id && (
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Команда:</span>
                  <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedUser.team_id}</span>
                </div>
              )}
              {(selectedUser.balance_fiat || selectedUser.balance_crypto) && (
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Балансы:</span>
                  <div className="text-[var(--jiva-text-secondary)] ml-2 mt-1">
                    {selectedUser.balance_fiat && <div>Фиат: {selectedUser.balance_fiat}</div>}
                    {selectedUser.balance_crypto && <div>Крипто: {selectedUser.balance_crypto}</div>}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 