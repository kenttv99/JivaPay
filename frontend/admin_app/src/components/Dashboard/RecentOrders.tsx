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
  const getStatusClass = (status: OrderStatus) => {
    switch (status) {
      case 'completed':
        return 'px-2 py-1 rounded-full text-xs font-medium bg-success/10 text-success';
      case 'processing':
        return 'px-2 py-1 rounded-full text-xs font-medium bg-info/10 text-info';
      case 'pending':
        return 'px-2 py-1 rounded-full text-xs font-medium bg-warning/10 text-warning';
      case 'canceled':
        return 'px-2 py-1 rounded-full text-xs font-medium bg-neutral/10 text-neutral';
      case 'disputed':
        return 'px-2 py-1 rounded-full text-xs font-medium bg-warning/10 text-warning';
      case 'failed':
        return 'px-2 py-1 rounded-full text-xs font-medium bg-error/10 text-error';
      default:
        return 'px-2 py-1 rounded-full text-xs font-medium bg-neutral/10 text-neutral';
    }
  };

  const getStatusText = (status: OrderStatus) => {
    switch (status) {
      case 'completed': return 'Выполнен';
      case 'processing': return 'В обработке';
      case 'pending': return 'Ожидание';
      case 'canceled': return 'Отменён';
      case 'disputed': return 'Спор';
      case 'failed': return 'Ошибка';
      default: return status;
    }
  };
  
  return (
    <span className={getStatusClass(status)}>
      {getStatusText(status)}
    </span>
  );
};

const OrderTypeBadge = ({ type }: { type: OrderType }) => {
  const getTypeClass = (type: OrderType) => {
    switch (type) {
      case 'payin': return 'px-2 py-1 rounded-full text-xs font-medium bg-success/10 text-success';
      case 'payout': return 'px-2 py-1 rounded-full text-xs font-medium bg-info/10 text-info';
      default: return 'px-2 py-1 rounded-full text-xs font-medium bg-neutral/10 text-neutral';
    }
  };

  const getTypeText = (type: OrderType) => {
    switch (type) {
      case 'payin': return 'Ввод';
      case 'payout': return 'Вывод';
      default: return type;
    }
  };
  
  return (
    <span className={getTypeClass(type)}>
      {getTypeText(type)}
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
    <div className="bg-surface rounded-lg border border-border overflow-hidden shadow-sm">
      <table className="w-full">
        <thead>
          <tr className="bg-neutral-light">
            <th className="px-6 py-4 text-left text-sm font-semibold text-secondary">ID</th>
            <th className="px-6 py-4 text-left text-sm font-semibold text-secondary">Дата</th>
            <th className="px-6 py-4 text-left text-sm font-semibold text-secondary">Пользователь</th>
            <th className="px-6 py-4 text-right text-sm font-semibold text-secondary">Сумма Фиат</th>
            <th className="px-6 py-4 text-right text-sm font-semibold text-secondary">Сумма Крипто</th>
            <th className="px-6 py-4 text-center text-sm font-semibold text-secondary">Тип</th>
            <th className="px-6 py-4 text-center text-sm font-semibold text-secondary">Статус</th>
            <th className="px-6 py-4 text-center text-sm font-semibold text-secondary">Трейдер</th>
          </tr>
        </thead>
        <tbody className="bg-surface">
          {recentOrders.map((order) => (
            <React.Fragment key={order.id}>
              <tr 
                className="border-b border-border hover:bg-neutral-light/50 transition-colors cursor-pointer"
                onClick={() => toggleOrderDetails(order.id)}
              >
                <td className="px-6 py-4 font-medium text-sm text-primary">{order.id}</td>
                <td className="px-6 py-4 text-secondary text-sm">{order.date}</td>
                <td className="px-6 py-4 text-primary font-medium">{order.user}</td>
                <td className="px-6 py-4 text-right font-semibold text-primary">{order.amount}</td>
                <td className="px-6 py-4 text-right text-secondary">{order.amount_crypto} {order.currency_crypto}</td>
                <td className="px-6 py-4 text-center">
                  <OrderTypeBadge type={order.type} />
                </td>
                <td className="px-6 py-4 text-center">
                  <OrderStatusBadge status={order.status} />
                </td>
                <td className="px-6 py-4 text-center text-sm text-secondary">
                  {order.trader || "Не назначен"}
                </td>
              </tr>
              {expandedOrder === order.id && (
                <tr>
                  <td colSpan={8} className="px-6 py-6 bg-neutral-light border-t border-border">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-semibold text-primary mb-4">Детали ордера</h4>
                        <div className="grid grid-cols-2 gap-6">
                          <div className="space-y-2">
                            <p className="text-sm">
                              <span className="font-medium text-primary">Трейдер:</span>
                              <span className="ml-2 text-secondary">{order.trader || "Не назначен"}</span>
                            </p>
                            <p className="text-sm">
                              <span className="font-medium text-primary">Реквизит:</span>
                              <span className="ml-2 text-secondary">{order.requisite || "Не указан"}</span>
                            </p>
                          </div>
                          <div className="space-y-2">
                            <p className="text-sm">
                              <span className="font-medium text-primary">Комиссия магазина:</span>
                              <span className="ml-2 text-secondary">{order.store_commission}</span>
                            </p>
                            <p className="text-sm">
                              <span className="font-medium text-primary">Комиссия трейдера:</span>
                              <span className="ml-2 text-secondary">{order.trader_commission}</span>
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2 ml-4">
                        <button className="bg-primary text-white px-3 py-1 rounded-lg hover:bg-primary/90 transition-colors text-xs">
                          Редактировать
                        </button>
                        <button className="bg-surface text-primary border border-border px-3 py-1 rounded-lg hover:bg-neutral-light transition-colors text-xs">
                          Детали
                        </button>
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