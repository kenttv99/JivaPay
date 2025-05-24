'use client';

import React, { useState } from 'react';
import { DataTable, StatusBadge } from '@jivapay/ui-kit';

// Типы ордеров согласно бэкенду
export type OrderStatus = 'completed' | 'processing' | 'pending' | 'canceled' | 'disputed' | 'failed';
export type OrderType = 'payin' | 'payout';

export interface OrderItem {
  id: string;
  date: string;
  user: string;
  amount: string;
  amount_crypto?: string;
  currency_crypto?: string;
  type: OrderType;
  status: OrderStatus;
  trader?: string | null;
  requisite?: string | null;
  store_commission?: string;
  trader_commission?: string;
  store_name?: string;
  external_order_id?: string;
}

interface OrdersTableProps {
  orders: OrderItem[];
  showColumns?: {
    trader?: boolean;
    commissions?: boolean;
    store?: boolean;
    crypto?: boolean;
    actions?: boolean;
  };
  onOrderSelect?: (order: OrderItem) => void;
  isLoading?: boolean;
  className?: string;
}

const OrderTypeBadge: React.FC<{ type: OrderType }> = ({ type }) => {
  // Маппинг на статусы, которые поддерживает StatusBadge
  const typeToStatus = {
    payin: 'success' as const,
    payout: 'processing' as const
  };

  const typeText = {
    payin: 'Ввод',
    payout: 'Вывод'
  };

  return (
    <StatusBadge status={typeToStatus[type]}>
      {typeText[type]}
    </StatusBadge>
  );
};

const OrderStatusBadge: React.FC<{ status: OrderStatus }> = ({ status }) => {
  // Маппинг на статусы, которые поддерживает StatusBadge
  const statusMapping = {
    completed: 'success' as const,
    processing: 'processing' as const,
    pending: 'pending' as const,
    canceled: 'inactive' as const,
    disputed: 'pending' as const,
    failed: 'failed' as const
  };

  const statusText = {
    completed: 'Выполнен',
    processing: 'В обработке',
    pending: 'Ожидание',
    canceled: 'Отменён',
    disputed: 'Спор',
    failed: 'Ошибка'
  };

  return (
    <StatusBadge status={statusMapping[status]}>
      {statusText[status]}
    </StatusBadge>
  );
};

export const OrdersTable: React.FC<OrdersTableProps> = ({ 
  orders, 
  showColumns = {
    trader: true,
    commissions: false,
    store: false,
    crypto: true,
    actions: false
  },
  onOrderSelect,
  isLoading = false,
  className = ''
}) => {
  const [expandedOrder, setExpandedOrder] = useState<string | null>(null);

  const toggleOrderDetails = (order: OrderItem) => {
    if (onOrderSelect) {
      onOrderSelect(order);
    }
    setExpandedOrder(expandedOrder === order.id ? null : order.id);
  };

  const columns = [
    {
      key: 'id',
      title: 'ID',
      render: (value: any, order: OrderItem) => (
        <button 
          onClick={() => toggleOrderDetails(order)}
          className="text-[var(--jiva-primary)] font-medium text-sm hover:underline"
        >
          {order.id}
        </button>
      )
    },
    {
      key: 'date',
      title: 'Дата',
      render: (value: any, order: OrderItem) => (
        <span className="text-[var(--jiva-text-secondary)] text-sm">
          {order.date}
        </span>
      )
    },
    {
      key: 'user',
      title: 'Пользователь',
      render: (value: any, order: OrderItem) => (
        <span className="text-[var(--jiva-text)] font-medium">
          {order.user}
        </span>
      )
    },
    {
      key: 'amount',
      title: 'Сумма Фиат',
      render: (value: any, order: OrderItem) => (
        <span className="font-semibold text-[var(--jiva-text)]">
          {order.amount}
        </span>
      )
    },
    ...(showColumns.crypto ? [{
      key: 'amount_crypto',
      title: 'Сумма Крипто',
      render: (value: any, order: OrderItem) => (
        <span className="text-[var(--jiva-text-secondary)]">
          {order.amount_crypto} {order.currency_crypto}
        </span>
      )
    }] : []),
    {
      key: 'type',
      title: 'Тип',
      render: (value: any, order: OrderItem) => <OrderTypeBadge type={order.type} />
    },
    {
      key: 'status',
      title: 'Статус',
      render: (value: any, order: OrderItem) => <OrderStatusBadge status={order.status} />
    },
    ...(showColumns.trader ? [{
      key: 'trader',
      title: 'Трейдер',
      render: (value: any, order: OrderItem) => (
        <span className="text-sm text-[var(--jiva-text-secondary)]">
          {order.trader || "Не назначен"}
        </span>
      )
    }] : []),
    ...(showColumns.store ? [{
      key: 'store',
      title: 'Магазин',
      render: (value: any, order: OrderItem) => (
        <span className="text-sm text-[var(--jiva-text-secondary)]">
          {order.store_name || "—"}
        </span>
      )
    }] : [])
  ];

  return (
    <div className={className}>
      <DataTable
        columns={columns}
        data={orders}
        loading={isLoading}
      />
      
      {/* Детали развернутого ордера */}
      {expandedOrder && (
        <div className="mt-4 bg-[var(--jiva-background)] border border-[var(--jiva-border-light)] rounded-lg">
          {(() => {
            const order = orders.find(o => o.id === expandedOrder);
            if (!order) return null;

            return (
              <div className="px-6 py-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-semibold text-[var(--jiva-text)] mb-4">Детали ордера {order.id}</h4>
                    <div className="grid grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <p className="text-sm">
                          <span className="font-medium text-[var(--jiva-text)]">Трейдер:</span> 
                          <span className="text-[var(--jiva-text-secondary)]"> {order.trader || "Не назначен"}</span>
                        </p>
                        <p className="text-sm">
                          <span className="font-medium text-[var(--jiva-text)]">Реквизит:</span> 
                          <span className="text-[var(--jiva-text-secondary)]"> {order.requisite || "Не назначен"}</span>
                        </p>
                        {order.external_order_id && (
                          <p className="text-sm">
                            <span className="font-medium text-[var(--jiva-text)]">External ID:</span> 
                            <span className="text-[var(--jiva-text-secondary)]"> {order.external_order_id}</span>
                          </p>
                        )}
                      </div>
                      {showColumns.commissions && (
                        <div className="space-y-2">
                          <p className="text-sm">
                            <span className="font-medium text-[var(--jiva-text)]">Комиссия магазина:</span> 
                            <span className="text-[var(--jiva-text-secondary)]"> {order.store_commission || "—"}</span>
                          </p>
                          <p className="text-sm">
                            <span className="font-medium text-[var(--jiva-text)]">Комиссия трейдера:</span> 
                            <span className="text-[var(--jiva-text-secondary)]"> {order.trader_commission || "—"}</span>
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => setExpandedOrder(null)}
                    className="text-[var(--jiva-text-secondary)] hover:text-[var(--jiva-text)] ml-4"
                  >
                    ✕
                  </button>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}; 