'use client';

import React, { useState } from 'react';
import { DataTable, StatusBadge, Modal } from '@jivapay/ui-kit';
import { usePermissions } from '@jivapay/permissions';

export interface RequisiteItem {
  id: string;
  trader_id: string;
  trader_name: string;
  bank_name: string;
  card_number: string;
  card_holder: string;
  status: 'active' | 'inactive' | 'blocked' | 'pending' | 'moderation';
  created_date: string;
  last_used?: string;
  total_orders: number;
  total_volume: string;
  success_rate: string;
  is_online: boolean;
  team_id?: string;
  moderation_comment?: string;
}

interface RequisiteManagementProps {
  requisites: RequisiteItem[];
  allowedActions?: {
    view?: boolean;
    moderate?: boolean;
    block?: boolean;
    setStatus?: boolean;
  };
  showColumns?: {
    trader?: boolean;
    team?: boolean;
    statistics?: boolean;
    onlineStatus?: boolean;
    lastUsed?: boolean;
  };
  onRequisiteAction?: (action: string, requisite: RequisiteItem, data?: any) => void;
  isLoading?: boolean;
  className?: string;
}

const RequisiteStatusBadge: React.FC<{ status: RequisiteItem['status'] }> = ({ status }) => {
  const statusConfig = {
    active: { text: 'Активен', status: 'success' as const },
    inactive: { text: 'Неактивен', status: 'inactive' as const },
    blocked: { text: 'Заблокирован', status: 'failed' as const },
    pending: { text: 'Ожидание', status: 'pending' as const },
    moderation: { text: 'На модерации', status: 'processing' as const }
  };

  const config = statusConfig[status];
  return <StatusBadge status={config.status}>{config.text}</StatusBadge>;
};

const OnlineStatusBadge: React.FC<{ isOnline: boolean }> = ({ isOnline }) => (
  <StatusBadge status={isOnline ? 'success' : 'inactive'}>
    {isOnline ? 'Онлайн' : 'Оффлайн'}
  </StatusBadge>
);

export const RequisiteManagement: React.FC<RequisiteManagementProps> = ({
  requisites,
  allowedActions = {
    view: true,
    moderate: false,
    block: false,
    setStatus: false
  },
  showColumns = {
    trader: true,
    team: false,
    statistics: true,
    onlineStatus: true,
    lastUsed: true
  },
  onRequisiteAction,
  isLoading = false,
  className = ''
}) => {
  const { hasPermission } = usePermissions();
  const [selectedRequisite, setSelectedRequisite] = useState<RequisiteItem | null>(null);
  const [moderationComment, setModerationComment] = useState('');

  const handleRequisiteAction = (action: string, requisite: RequisiteItem, data?: any) => {
    if (action === 'view') {
      setSelectedRequisite(requisite);
    }
    if (onRequisiteAction) {
      onRequisiteAction(action, requisite, data);
    }
    console.log(`${action} action for requisite:`, requisite);
  };

  const canModerate = hasPermission('requisites:moderate:*') || hasPermission('requisites:moderate:team');
  const canEdit = hasPermission('requisites:edit:*') || hasPermission('requisites:edit:team');

  // Скрываем номер карты для безопасности
  const maskCardNumber = (cardNumber: string) => {
    if (cardNumber.length < 8) return cardNumber;
    return cardNumber.slice(0, 4) + '****' + cardNumber.slice(-4);
  };

  const handleModeration = (action: 'approve' | 'reject') => {
    if (selectedRequisite) {
      handleRequisiteAction('moderate', selectedRequisite, { 
        action, 
        comment: moderationComment 
      });
      setSelectedRequisite(null);
      setModerationComment('');
    }
  };

  const columns = [
    {
      key: 'card_info',
      title: 'Реквизит',
      render: (value: any, requisite: RequisiteItem) => (
        <div>
          <div className="font-medium text-[var(--jiva-text)]">{requisite.bank_name}</div>
          <div className="text-sm text-[var(--jiva-text-secondary)]">
            {maskCardNumber(requisite.card_number)}
          </div>
          <div className="text-sm text-[var(--jiva-text-secondary)]">
            {requisite.card_holder}
          </div>
        </div>
      )
    },
    ...(showColumns.trader ? [{
      key: 'trader',
      title: 'Трейдер',
      render: (value: any, requisite: RequisiteItem) => (
        <div>
          <div className="font-medium text-[var(--jiva-text)]">{requisite.trader_name}</div>
          <div className="text-sm text-[var(--jiva-text-secondary)]">ID: {requisite.trader_id}</div>
          {showColumns.team && requisite.team_id && (
            <div className="text-sm text-[var(--jiva-text-secondary)]">
              Команда: {requisite.team_id}
            </div>
          )}
        </div>
      )
    }] : []),
    {
      key: 'status',
      title: 'Статус',
      render: (value: any, requisite: RequisiteItem) => (
        <div className="space-y-1">
          <RequisiteStatusBadge status={requisite.status} />
          {showColumns.onlineStatus && (
            <OnlineStatusBadge isOnline={requisite.is_online} />
          )}
        </div>
      )
    },
    ...(showColumns.statistics ? [{
      key: 'statistics',
      title: 'Статистика',
      render: (value: any, requisite: RequisiteItem) => (
        <div className="text-sm">
          <div className="font-medium text-[var(--jiva-text)]">
            Ордеров: {requisite.total_orders}
          </div>
          <div className="text-[var(--jiva-text-secondary)]">
            Объем: {requisite.total_volume}
          </div>
          <div className="text-[var(--jiva-text-secondary)]">
            Успешность: {requisite.success_rate}
          </div>
        </div>
      )
    }] : []),
    {
      key: 'created_date',
      title: 'Дата создания',
      render: (value: any, requisite: RequisiteItem) => (
        <span className="text-sm text-[var(--jiva-text-secondary)]">
          {requisite.created_date}
        </span>
      )
    },
    ...(showColumns.lastUsed ? [{
      key: 'last_used',
      title: 'Последнее использование',
      render: (value: any, requisite: RequisiteItem) => (
        <span className="text-sm text-[var(--jiva-text-secondary)]">
          {requisite.last_used || 'Не использовался'}
        </span>
      )
    }] : []),
    {
      key: 'actions',
      title: 'Действия',
      render: (value: any, requisite: RequisiteItem) => (
        <div className="flex gap-2">
          {allowedActions.view && (
            <button
              onClick={() => handleRequisiteAction('view', requisite)}
              className="text-[var(--jiva-primary)] hover:underline text-sm"
            >
              Просмотр
            </button>
          )}
          {allowedActions.moderate && requisite.status === 'moderation' && (
            <button
              onClick={() => handleRequisiteAction('view', requisite)}
              className="text-[var(--jiva-info)] hover:underline text-sm"
            >
              Модерация
            </button>
          )}
          {allowedActions.block && requisite.status === 'active' && (
            <button
              onClick={() => handleRequisiteAction('block', requisite)}
              className="text-[var(--jiva-warning)] hover:underline text-sm"
            >
              Заблокировать
            </button>
          )}
          {allowedActions.setStatus && requisite.status === 'blocked' && (
            <button
              onClick={() => handleRequisiteAction('unblock', requisite)}
              className="text-[var(--jiva-success)] hover:underline text-sm"
            >
              Разблокировать
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
        data={requisites}
        loading={isLoading}
      />
      
      {/* Детали выбранного реквизита */}
      {selectedRequisite && (
        <Modal
          isOpen={!!selectedRequisite}
          onClose={() => setSelectedRequisite(null)}
          title={`Реквизит ${selectedRequisite.bank_name}`}
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-3">
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">ID реквизита:</span>
                  <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedRequisite.id}</span>
                </div>
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Банк:</span>
                  <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedRequisite.bank_name}</span>
                </div>
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Номер карты:</span>
                  <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedRequisite.card_number}</span>
                </div>
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Держатель карты:</span>
                  <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedRequisite.card_holder}</span>
                </div>
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Трейдер:</span>
                  <span className="text-[var(--jiva-text-secondary)] ml-2">
                    {selectedRequisite.trader_name} ({selectedRequisite.trader_id})
                  </span>
                </div>
              </div>
              
              <div className="space-y-3">
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Статус:</span>
                  <span className="ml-2"><RequisiteStatusBadge status={selectedRequisite.status} /></span>
                </div>
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Онлайн статус:</span>
                  <span className="ml-2"><OnlineStatusBadge isOnline={selectedRequisite.is_online} /></span>
                </div>
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Дата создания:</span>
                  <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedRequisite.created_date}</span>
                </div>
                {selectedRequisite.last_used && (
                  <div>
                    <span className="font-medium text-[var(--jiva-text)]">Последнее использование:</span>
                    <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedRequisite.last_used}</span>
                  </div>
                )}
                {selectedRequisite.team_id && (
                  <div>
                    <span className="font-medium text-[var(--jiva-text)]">Команда:</span>
                    <span className="text-[var(--jiva-text-secondary)] ml-2">{selectedRequisite.team_id}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Статистика использования */}
            <div className="border-t border-[var(--jiva-border-light)] pt-4">
              <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-3">
                Статистика использования
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Всего ордеров:</span>
                  <div className="text-[var(--jiva-text-secondary)]">{selectedRequisite.total_orders}</div>
                </div>
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Общий объем:</span>
                  <div className="text-[var(--jiva-text-secondary)]">{selectedRequisite.total_volume}</div>
                </div>
                <div>
                  <span className="font-medium text-[var(--jiva-text)]">Успешность:</span>
                  <div className="text-[var(--jiva-text-secondary)]">{selectedRequisite.success_rate}</div>
                </div>
              </div>
            </div>

            {selectedRequisite.moderation_comment && (
              <div className="border-t border-[var(--jiva-border-light)] pt-4">
                <span className="font-medium text-[var(--jiva-text)]">Комментарий модерации:</span>
                <div className="text-[var(--jiva-text-secondary)] mt-1">{selectedRequisite.moderation_comment}</div>
              </div>
            )}

            {/* Модерация (только для реквизитов на модерации) */}
            {canModerate && selectedRequisite.status === 'moderation' && (
              <div className="border-t border-[var(--jiva-border-light)] pt-4">
                <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-3">
                  Модерация реквизита
                </h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                      Комментарий модерации
                    </label>
                    <textarea
                      value={moderationComment}
                      onChange={(e) => setModerationComment(e.target.value)}
                      className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
                      rows={3}
                      placeholder="Укажите причину одобрения или отклонения..."
                    />
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleModeration('approve')}
                      className="bg-[var(--jiva-success)] text-white px-4 py-2 rounded-lg hover:opacity-90"
                    >
                      Одобрить
                    </button>
                    <button
                      onClick={() => handleModeration('reject')}
                      className="bg-[var(--jiva-error)] text-white px-4 py-2 rounded-lg hover:opacity-90"
                    >
                      Отклонить
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Управление статусом */}
            {canEdit && selectedRequisite.status !== 'moderation' && (
              <div className="border-t border-[var(--jiva-border-light)] pt-4">
                <div className="flex gap-2">
                  {selectedRequisite.status === 'active' && (
                    <button
                      onClick={() => handleRequisiteAction('block', selectedRequisite)}
                      className="bg-[var(--jiva-warning)] text-white px-4 py-2 rounded-lg hover:opacity-90"
                    >
                      Заблокировать
                    </button>
                  )}
                  {selectedRequisite.status === 'blocked' && (
                    <button
                      onClick={() => handleRequisiteAction('unblock', selectedRequisite)}
                      className="bg-[var(--jiva-success)] text-white px-4 py-2 rounded-lg hover:opacity-90"
                    >
                      Разблокировать
                    </button>
                  )}
                  {selectedRequisite.status === 'inactive' && (
                    <button
                      onClick={() => handleRequisiteAction('activate', selectedRequisite)}
                      className="bg-[var(--jiva-primary)] text-white px-4 py-2 rounded-lg hover:opacity-90"
                    >
                      Активировать
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}; 