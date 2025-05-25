'use client';

import React, { useState } from 'react';
import { DataTable, StatusBadge, Modal } from '@jivapay/ui-kit';
import { usePermissions } from '@jivapay/permissions';

export interface StoreItem {
  id: string;
  name: string;
  merchant_id: string;
  merchant_name: string;
  status: 'active' | 'inactive' | 'blocked' | 'pending';
  created_date: string;
  last_active?: string;
  total_orders: number;
  total_revenue: string;
  commission_rate: string;
  webhook_url?: string;
  api_key_id?: string;
  description?: string;
  domain?: string;
  api_key?: boolean;
}

interface StoreManagementProps {
  stores: StoreItem[];
  allowedActions?: {
    view?: boolean;
    edit?: boolean;
    delete?: boolean;
    block?: boolean;
    create?: boolean;
  };
  showColumns?: {
    merchant?: boolean;
    revenue?: boolean;
    commission?: boolean;
    webhook?: boolean;
    lastActive?: boolean;
  };
  onStoreAction?: (action: string, store: StoreItem) => void;
  onCreateStore?: () => void;
  isLoading?: boolean;
  className?: string;
}

const StoreStatusBadge: React.FC<{ status: StoreItem['status'] }> = ({ status }) => {
  const statusConfig = {
    active: { text: 'Активен', status: 'success' as const },
    inactive: { text: 'Неактивен', status: 'inactive' as const },
    blocked: { text: 'Заблокирован', status: 'failed' as const },
    pending: { text: 'Ожидание', status: 'pending' as const }
  };

  const config = statusConfig[status];
  return <StatusBadge status={config.status}>{config.text}</StatusBadge>;
};

export const StoreManagement: React.FC<StoreManagementProps> = ({
  stores,
  allowedActions = {
    view: true,
    edit: false,
    delete: false,
    block: false,
    create: false
  },
  showColumns = {
    merchant: true,
    revenue: true,
    commission: true,
    webhook: false,
    lastActive: true
  },
  onStoreAction,
  onCreateStore,
  isLoading = false,
  className = ''
}) => {
  const { hasPermission } = usePermissions();
  const [selectedStore, setSelectedStore] = useState<StoreItem | null>(null);

  const handleStoreAction = (action: string, store: StoreItem) => {
    if (action === 'view') {
      setSelectedStore(store);
    }
    if (onStoreAction) {
      onStoreAction(action, store);
    }
    console.log(`${action} action for store:`, store);
  };

  const canViewDetails = hasPermission('stores:view:*') || hasPermission('stores:view:own');
  const canEdit = hasPermission('stores:edit:*') || hasPermission('stores:edit:own');

  const columns = [
    {
      key: 'name',
      title: 'Магазин',
      render: (value: any, store: StoreItem) => (
        <div>
          <div className="font-medium text-primary">{store.name}</div>
          <div className="text-sm text-secondary">ID: {store.id}</div>
          {store.domain && (
            <div className="text-sm text-secondary mt-1">
              {store.domain}
            </div>
          )}
        </div>
      )
    },
    ...(showColumns.merchant ? [{
      key: 'merchant',
      title: 'Мерчант',
      render: (value: any, store: StoreItem) => (
        <div>
          <div className="font-medium text-primary">{store.merchant_name}</div>
          <div className="text-sm text-secondary">ID: {store.merchant_id}</div>
        </div>
      )
    }] : []),
    {
      key: 'status',
      title: 'Статус',
      render: (value: any, store: StoreItem) => <StoreStatusBadge status={store.status} />
    },
    {
      key: 'orders_stats',
      title: 'Статистика',
      render: (value: any, store: StoreItem) => (
        <div className="text-sm">
          <div className="font-medium text-primary">
            ₽ {store.total_revenue}
          </div>
          <div className="text-secondary">
            {store.total_orders} ордеров
          </div>
        </div>
      )
    },
    ...(showColumns.commission ? [{
      key: 'commission_rate',
      title: 'Комиссия',
      render: (value: any, store: StoreItem) => (
        <span className="text-primary">{store.commission_rate}</span>
      )
    }] : []),
    {
      key: 'created_date',
      title: 'Дата создания',
      render: (value: any, store: StoreItem) => (
        <span className="text-sm text-secondary">
          {store.created_date}
        </span>
      )
    },
    ...(showColumns.lastActive ? [{
      key: 'last_active',
      title: 'Последняя активность',
      render: (value: any, store: StoreItem) => (
        <div className="text-secondary">
          Последняя активность: {store.last_active}
        </div>
      )
    }] : []),
    ...(showColumns.webhook ? [{
      key: 'webhook_url',
      title: 'Webhook',
      render: (value: any, store: StoreItem) => (
        <div className="text-sm">
          {store.webhook_url ? (
            <div className="text-success">Настроен</div>
          ) : (
            <div className="text-secondary">Не настроен</div>
          )}
          {store.api_key_id && (
            <div className="text-secondary">
              API ключ: {store.api_key_id}
            </div>
          )}
        </div>
      )
    }] : []),
    {
      key: 'actions',
      title: 'Действия',
      render: (value: any, store: StoreItem) => (
        <div className="flex gap-2">
          {allowedActions.view && (
            <button
              onClick={() => handleStoreAction('view', store)}
              className="text-accent hover:underline text-sm"
            >
              Просмотр
            </button>
          )}
          {allowedActions.edit && (
            <button
              onClick={() => handleStoreAction('edit', store)}
              className="text-info hover:underline text-sm"
            >
              Изменить
            </button>
          )}
          {allowedActions.block && store.status === 'active' && (
            <button
              onClick={() => handleStoreAction('block', store)}
              className="text-warning hover:underline text-sm"
            >
              Заблокировать
            </button>
          )}
          {allowedActions.delete && (
            <button
              onClick={() => handleStoreAction('delete', store)}
              className="text-error hover:underline text-sm"
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
      {/* Кнопка создания магазина */}
      {allowedActions.create && onCreateStore && (
        <div className="mb-4 flex justify-end">
          <button
            onClick={onCreateStore}
            className="bg-accent text-white px-4 py-2 rounded-lg hover:opacity-90"
          >
            Создать магазин
          </button>
        </div>
      )}

      <DataTable
        columns={columns}
        data={stores}
        loading={isLoading}
      />
      
      {/* Детали выбранного магазина */}
      {selectedStore && (
        <Modal
          isOpen={!!selectedStore}
          onClose={() => setSelectedStore(null)}
          title={`Магазин ${selectedStore.name}`}
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-3">
                <div>
                  <span className="font-medium text-primary">ID магазина:</span>
                  <span className="text-secondary ml-2">{selectedStore.id}</span>
                </div>
                <div>
                  <span className="font-medium text-primary">Название:</span>
                  <span className="text-secondary ml-2">{selectedStore.name}</span>
                </div>
                <div>
                  <span className="font-medium text-primary">Мерчант:</span>
                  <span className="text-secondary ml-2">
                    {selectedStore.merchant_name}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-primary">Статус:</span>
                  <span className="ml-2"><StoreStatusBadge status={selectedStore.status} /></span>
                </div>
                <div>
                  <span className="font-medium text-primary">Комиссия:</span>
                  <span className="text-secondary ml-2">{selectedStore.commission_rate}</span>
                </div>
              </div>
              
              <div className="space-y-3">
                <div>
                  <span className="font-medium text-primary">Дата создания:</span>
                  <span className="text-secondary ml-2">{selectedStore.created_date}</span>
                </div>
                {selectedStore.last_active && (
                  <div>
                    <span className="font-medium text-primary">Последняя активность:</span>
                    <span className="text-secondary ml-2">{selectedStore.last_active}</span>
                  </div>
                )}
                <div>
                  <span className="font-medium text-primary">Всего ордеров:</span>
                  <span className="text-secondary ml-2">{selectedStore.total_orders}</span>
                </div>
                <div>
                  <span className="font-medium text-primary">Общий оборот:</span>
                  <span className="text-secondary ml-2">{selectedStore.total_revenue}</span>
                </div>
              </div>
            </div>

            {selectedStore.description && (
              <div>
                <span className="font-medium text-primary">Описание:</span>
                <div className="text-secondary mt-1">{selectedStore.description}</div>
              </div>
            )}

            {/* Интеграционная информация */}
            <div className="border-t border-border pt-4">
              <h3 className="text-lg font-semibold text-primary mb-3">
                Настройки API
              </h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium text-primary">Webhook URL:</span>
                  <span className="text-secondary ml-2">
                    {selectedStore.webhook_url || 'Не настроен'}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-primary">API ключ:</span>
                  <span className="text-secondary ml-2">
                    {selectedStore.api_key ? '••••••••••••••••' : 'Не настроен'}
                  </span>
                </div>
              </div>
            </div>

            {canEdit && (
              <div className="border-t border-border pt-4">
                <div className="flex gap-3">
                  <button
                    onClick={() => handleStoreAction('edit', selectedStore)}
                    className="bg-accent text-white px-4 py-2 rounded-lg hover:opacity-90"
                  >
                    Редактировать
                  </button>
                  {selectedStore.status === 'active' && (
                    <button
                      onClick={() => handleStoreAction('block', selectedStore)}
                      className="bg-warning text-white px-4 py-2 rounded-lg hover:opacity-90"
                    >
                      Заблокировать
                    </button>
                  )}
                  {selectedStore.status === 'blocked' && (
                    <button
                      onClick={() => handleStoreAction('unblock', selectedStore)}
                      className="bg-success text-white px-4 py-2 rounded-lg hover:opacity-90"
                    >
                      Разблокировать
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