'use client';

import React, { useState } from 'react';
import { StatusBadge, Modal } from '@jivapay/ui-kit';
import { usePermissions } from '@jivapay/permissions';
import { OrderItem } from '../OrdersTable/OrdersTable';

interface OrderDetailsProps {
  order: OrderItem | null;
  isOpen: boolean;
  onClose: () => void;
  onStatusChange?: (orderId: string, newStatus: string, comment?: string) => void;
  onAssignTrader?: (orderId: string, traderId: string) => void;
  availableTraders?: { id: string; name: string }[];
  isLoading?: boolean;
}

const OrderTypeBadge: React.FC<{ type: 'payin' | 'payout' }> = ({ type }) => {
  return (
    <StatusBadge status={type === 'payin' ? 'success' : 'processing'}>
      {type === 'payin' ? 'Пополнение' : 'Вывод'}
    </StatusBadge>
  );
};

const OrderStatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const statusConfig = {
    completed: { text: 'Выполнен', status: 'success' as const },
    processing: { text: 'В обработке', status: 'processing' as const },
    pending: { text: 'Ожидание', status: 'pending' as const },
    canceled: { text: 'Отменен', status: 'inactive' as const },
    disputed: { text: 'Спор', status: 'failed' as const },
    failed: { text: 'Неудача', status: 'failed' as const }
  };

  const config = statusConfig[status as keyof typeof statusConfig];
  return <StatusBadge status={config.status}>{config.text}</StatusBadge>;
};

export const OrderDetails: React.FC<OrderDetailsProps> = ({
  order,
  isOpen,
  onClose,
  onStatusChange,
  onAssignTrader,
  availableTraders = [],
  isLoading = false
}) => {
  const { hasPermission } = usePermissions();
  const [newStatus, setNewStatus] = useState('');
  const [comment, setComment] = useState('');
  const [selectedTrader, setSelectedTrader] = useState('');

  if (!order) return null;

  const canEditStatus = hasPermission('orders:edit:*') || hasPermission('orders:edit:team') || hasPermission('orders:edit:assigned');
  const canAssignTrader = hasPermission('orders:edit:*') || hasPermission('orders:edit:team');
  const canViewSensitive = hasPermission('orders:details:*') || hasPermission('finance:view:*');

  const handleStatusChange = () => {
    if (newStatus && onStatusChange) {
      onStatusChange(order.id, newStatus, comment);
      setNewStatus('');
      setComment('');
    }
  };

  const handleTraderAssign = () => {
    if (selectedTrader && onAssignTrader) {
      onAssignTrader(order.id, selectedTrader);
      setSelectedTrader('');
    }
  };

  const availableStatuses = [
    { value: 'pending', label: 'Ожидание' },
    { value: 'processing', label: 'В обработке' },
    { value: 'completed', label: 'Выполнен' },
    { value: 'disputed', label: 'Спор' },
    { value: 'failed', label: 'Неудача' },
    { value: 'canceled', label: 'Отменен' }
  ].filter(status => status.value !== order.status);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Ордер ${order.id}`}>
      <div className="space-y-6">
        {/* Основная информация */}
        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                ID ордера
              </label>
              <div className="text-[var(--jiva-text-secondary)]">{order.id}</div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                Дата создания
              </label>
              <div className="text-[var(--jiva-text-secondary)]">{order.date}</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                Пользователь
              </label>
              <div className="text-[var(--jiva-text-secondary)]">{order.user}</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                Тип операции
              </label>
              <OrderTypeBadge type={order.type} />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                Статус
              </label>
              <OrderStatusBadge status={order.status} />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                Сумма (фиат)
              </label>
              <div className="text-lg font-semibold text-[var(--jiva-text)]">{order.amount}</div>
            </div>

            {order.amount_crypto && (
              <div>
                <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                  Сумма (крипто)
                </label>
                <div className="text-[var(--jiva-text-secondary)]">
                  {order.amount_crypto} {order.currency_crypto}
                </div>
              </div>
            )}

            {order.trader && (
              <div>
                <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                  Трейдер
                </label>
                <div className="text-[var(--jiva-text-secondary)]">{order.trader}</div>
              </div>
            )}

            {order.requisite && (
              <div>
                <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                  Реквизит
                </label>
                <div className="text-[var(--jiva-text-secondary)]">{order.requisite}</div>
              </div>
            )}

            {order.store_name && (
              <div>
                <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                  Магазин
                </label>
                <div className="text-[var(--jiva-text-secondary)]">{order.store_name}</div>
              </div>
            )}
          </div>
        </div>

        {/* Финансовая информация (только для админов) */}
        {canViewSensitive && (order.store_commission || order.trader_commission) && (
          <div className="border-t border-[var(--jiva-border-light)] pt-4">
            <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-3">
              Финансовая информация
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {order.store_commission && (
                <div>
                  <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                    Комиссия магазина
                  </label>
                  <div className="text-[var(--jiva-text-secondary)]">{order.store_commission}</div>
                </div>
              )}
              {order.trader_commission && (
                <div>
                  <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                    Комиссия трейдера
                  </label>
                  <div className="text-[var(--jiva-text-secondary)]">{order.trader_commission}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Дополнительная информация */}
        {order.external_order_id && (
          <div>
            <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
              Внешний ID ордера
            </label>
            <div className="text-[var(--jiva-text-secondary)]">{order.external_order_id}</div>
          </div>
        )}

        {/* Действия для изменения статуса */}
        {canEditStatus && availableStatuses.length > 0 && (
          <div className="border-t border-[var(--jiva-border-light)] pt-4">
            <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-3">
              Изменить статус
            </h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                  Новый статус
                </label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
                >
                  <option value="">Выберите статус</option>
                  {availableStatuses.map(status => (
                    <option key={status.value} value={status.value}>
                      {status.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                  Комментарий (необязательно)
                </label>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
                  rows={3}
                  placeholder="Причина изменения статуса..."
                />
              </div>
              
              <button
                onClick={handleStatusChange}
                disabled={!newStatus || isLoading}
                className="bg-[var(--jiva-primary)] text-white px-4 py-2 rounded-lg hover:opacity-90 disabled:opacity-50"
              >
                {isLoading ? 'Обновление...' : 'Изменить статус'}
              </button>
            </div>
          </div>
        )}

        {/* Назначение трейдера */}
        {canAssignTrader && !order.trader && availableTraders.length > 0 && (
          <div className="border-t border-[var(--jiva-border-light)] pt-4">
            <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-3">
              Назначить трейдера
            </h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                  Выберите трейдера
                </label>
                <select
                  value={selectedTrader}
                  onChange={(e) => setSelectedTrader(e.target.value)}
                  className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
                >
                  <option value="">Выберите трейдера</option>
                  {availableTraders.map(trader => (
                    <option key={trader.id} value={trader.id}>
                      {trader.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <button
                onClick={handleTraderAssign}
                disabled={!selectedTrader || isLoading}
                className="bg-[var(--jiva-success)] text-white px-4 py-2 rounded-lg hover:opacity-90 disabled:opacity-50"
              >
                {isLoading ? 'Назначение...' : 'Назначить трейдера'}
              </button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}; 