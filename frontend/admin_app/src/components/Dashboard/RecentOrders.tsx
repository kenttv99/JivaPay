'use client';

import { useState } from "react";
import React from "react";

type OrderStatus = "completed" | "processing" | "pending" | "canceled" | "disputed" | "failed";
type OrderType = "payin" | "payout";

interface Order {
  id: string;
  date: string;
  user: string;
  amount: string;
  amount_crypto: string;
  currency_crypto: string;
  type: OrderType;
  status: OrderStatus;
  trader: string | null;
  requisite: string | null;
  store_commission: string;
  trader_commission: string;
}

const OrderStatusBadge = ({ status }: { status: OrderStatus }) => {
  const getStatusConfig = (status: OrderStatus) => {
    switch (status) {
      case 'completed':
        return { text: 'Выполнен', className: 'status-success' };
      case 'processing':
        return { text: 'В обработке', className: 'status-info' };
      case 'pending':
        return { text: 'Ожидание', className: 'status-warning' };
      case 'canceled':
        return { text: 'Отменён', className: 'bg-gray-100 text-gray-700' };
      case 'disputed':
        return { text: 'Спор', className: 'status-warning' };
      case 'failed':
        return { text: 'Ошибка', className: 'status-error' };
      default:
        return { text: status, className: 'bg-gray-100 text-gray-700' };
    }
  };

  const config = getStatusConfig(status);
  
  return (
    <span className={`status-badge ${config.className}`}>
      {config.text}
    </span>
  );
};

const OrderTypeBadge = ({ type }: { type: OrderType }) => {
  const getTypeConfig = (type: OrderType) => {
    switch (type) {
      case 'payin':
        return { text: 'Ввод', className: 'status-success' };
      case 'payout':
        return { text: 'Вывод', className: 'bg-blue-100 text-blue-700' };
      default:
        return { text: type, className: 'bg-gray-100 text-gray-700' };
    }
  };

  const config = getTypeConfig(type);
  
  return (
    <span className={`status-badge ${config.className}`}>
      {config.text}
    </span>
  );
};

const recentOrders: Order[] = [
  {
    id: "ORD-2305001",
    date: "15.05.2023 12:30",
    user: "Иван Петров",
    amount: "₽12,500",
    amount_crypto: "250",
    currency_crypto: "USDT",
    type: "payin",
    status: "completed",
    trader: "Максим Иванов",
    requisite: "Сбербанк ****1234",
    store_commission: "₽625",
    trader_commission: "₽250"
  },
  {
    id: "ORD-2305002",
    date: "15.05.2023 13:45",
    user: "Елена Сидорова",
    amount: "₽8,300",
    amount_crypto: "166",
    currency_crypto: "USDT",
    type: "payin",
    status: "processing",
    trader: null,
    requisite: null,
    store_commission: "₽415",
    trader_commission: "₽166"
  },
  {
    id: "ORD-2305003",
    date: "15.05.2023 14:22",
    user: "Алексей Иванов",
    amount: "₽15,750",
    amount_crypto: "315",
    currency_crypto: "USDT",
    type: "payout",
    status: "completed",
    trader: "Анна Смирнова",
    requisite: "Тинькофф ****5678",
    store_commission: "₽788",
    trader_commission: "₽315"
  },
  {
    id: "ORD-2305004",
    date: "15.05.2023 15:10",
    user: "Мария Кузнецова",
    amount: "₽5,200",
    amount_crypto: "104",
    currency_crypto: "USDT",
    type: "payin",
    status: "canceled",
    trader: null,
    requisite: null,
    store_commission: "₽0",
    trader_commission: "₽0"
  },
  {
    id: "ORD-2305005",
    date: "15.05.2023 16:05",
    user: "Дмитрий Смирнов",
    amount: "₽21,000",
    amount_crypto: "420",
    currency_crypto: "USDT",
    type: "payout",
    status: "processing",
    trader: null,
    requisite: null,
    store_commission: "₽1,050",
    trader_commission: "₽420"
  }
];

export const RecentOrders = () => {
  const [expandedOrder, setExpandedOrder] = useState<string | null>(null);

  const toggleOrderDetails = (orderId: string) => {
    setExpandedOrder(expandedOrder === orderId ? null : orderId);
  };

  return (
    <div className="bg-white rounded-lg border border-[var(--jiva-border)] overflow-hidden shadow-sm">
      <table className="w-full">
        <thead>
          <tr className="border-b border-[var(--jiva-border)] bg-[var(--jiva-background)]">
            <th className="px-6 py-4 text-left text-sm font-semibold text-[var(--jiva-text)]">ID</th>
            <th className="px-6 py-4 text-left text-sm font-semibold text-[var(--jiva-text)]">Дата</th>
            <th className="px-6 py-4 text-left text-sm font-semibold text-[var(--jiva-text)]">Пользователь</th>
            <th className="px-6 py-4 text-right text-sm font-semibold text-[var(--jiva-text)]">Сумма Фиат</th>
            <th className="px-6 py-4 text-right text-sm font-semibold text-[var(--jiva-text)]">Сумма Крипто</th>
            <th className="px-6 py-4 text-center text-sm font-semibold text-[var(--jiva-text)]">Тип</th>
            <th className="px-6 py-4 text-center text-sm font-semibold text-[var(--jiva-text)]">Статус</th>
            <th className="px-6 py-4 text-center text-sm font-semibold text-[var(--jiva-text)]">Трейдер</th>
          </tr>
        </thead>
        <tbody className="bg-white">
          {recentOrders.map((order) => (
            <React.Fragment key={order.id}>
              <tr 
                className="border-b border-[var(--jiva-border-light)] hover:bg-[var(--jiva-background)] cursor-pointer transition-colors"
                onClick={() => toggleOrderDetails(order.id)}
              >
                <td className="px-6 py-4 text-[var(--jiva-primary)] font-medium text-sm">{order.id}</td>
                <td className="px-6 py-4 text-[var(--jiva-text-secondary)] text-sm">{order.date}</td>
                <td className="px-6 py-4 text-[var(--jiva-text)] font-medium">{order.user}</td>
                <td className="px-6 py-4 text-right font-semibold text-[var(--jiva-text)]">{order.amount}</td>
                <td className="px-6 py-4 text-right text-[var(--jiva-text-secondary)]">{order.amount_crypto} {order.currency_crypto}</td>
                <td className="px-6 py-4 text-center">
                  <OrderTypeBadge type={order.type} />
                </td>
                <td className="px-6 py-4 text-center">
                  <OrderStatusBadge status={order.status} />
                </td>
                <td className="px-6 py-4 text-center text-sm text-[var(--jiva-text-secondary)]">
                  {order.trader || "Не назначен"}
                </td>
              </tr>
              {expandedOrder === order.id && (
                <tr>
                  <td colSpan={8} className="px-6 py-6 bg-[var(--jiva-background)] border-t border-[var(--jiva-border-light)]">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-semibold text-[var(--jiva-text)] mb-4">Детали ордера</h4>
                        <div className="grid grid-cols-2 gap-6">
                          <div className="space-y-2">
                            <p className="text-sm">
                              <span className="font-medium text-[var(--jiva-text)]">Трейдер:</span> 
                              <span className="text-[var(--jiva-text-secondary)] ml-2">{order.trader || "Не назначен"}</span>
                            </p>
                            <p className="text-sm">
                              <span className="font-medium text-[var(--jiva-text)]">Реквизит:</span> 
                              <span className="text-[var(--jiva-text-secondary)] ml-2">{order.requisite || "Не назначен"}</span>
                            </p>
                          </div>
                          <div className="space-y-2">
                            <p className="text-sm">
                              <span className="font-medium text-[var(--jiva-text)]">Комиссия магазина:</span> 
                              <span className="text-[var(--jiva-text-secondary)] ml-2">{order.store_commission}</span>
                            </p>
                            <p className="text-sm">
                              <span className="font-medium text-[var(--jiva-text)]">Комиссия трейдера:</span> 
                              <span className="text-[var(--jiva-text-secondary)] ml-2">{order.trader_commission}</span>
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-3 ml-6">
                        <button className="px-4 py-2 bg-white hover:bg-[var(--jiva-background)] text-[var(--jiva-text)] border border-[var(--jiva-border)] rounded-md transition-colors flex items-center gap-2">
                          <span>👁</span>
                          <span className="text-sm font-medium">Детали</span>
                        </button>
                        {order.status === "processing" && (
                          <button className="px-4 py-2 bg-[var(--jiva-primary)] hover:bg-[var(--jiva-primary-dark)] text-white rounded-md transition-colors flex items-center gap-2">
                            <span>✓</span>
                            <span className="text-sm font-medium">Принять</span>
                          </button>
                        )}
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}; 