'use client';

import { useState } from "react";

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
    <div className="overflow-hidden rounded-lg">
      <table className="w-full">
        <thead>
          <tr className="border-b border-[var(--jiva-border)]">
            <th className="px-4 py-3 text-left text-sm font-medium text-[var(--jiva-text-secondary)]">ID</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-[var(--jiva-text-secondary)]">Дата</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-[var(--jiva-text-secondary)]">Пользователь</th>
            <th className="px-4 py-3 text-right text-sm font-medium text-[var(--jiva-text-secondary)]">Сумма Фиат</th>
            <th className="px-4 py-3 text-right text-sm font-medium text-[var(--jiva-text-secondary)]">Сумма Крипто</th>
            <th className="px-4 py-3 text-center text-sm font-medium text-[var(--jiva-text-secondary)]">Тип</th>
            <th className="px-4 py-3 text-center text-sm font-medium text-[var(--jiva-text-secondary)]">Статус</th>
            <th className="px-4 py-3 text-center text-sm font-medium text-[var(--jiva-text-secondary)]">Трейдер</th>
          </tr>
        </thead>
        <tbody>
          {recentOrders.map((order) => (
            <>
              <tr 
                key={order.id} 
                className="border-b border-[var(--jiva-border)] hover:bg-[var(--jiva-background)] cursor-pointer"
                onClick={() => toggleOrderDetails(order.id)}
              >
                <td className="px-4 py-3 text-[var(--jiva-primary)] font-medium">{order.id}</td>
                <td className="px-4 py-3 text-sm">{order.date}</td>
                <td className="px-4 py-3">{order.user}</td>
                <td className="px-4 py-3 text-right font-medium">{order.amount}</td>
                <td className="px-4 py-3 text-right">{order.amount_crypto} {order.currency_crypto}</td>
                <td className="px-4 py-3 text-center">
                  <OrderTypeBadge type={order.type} />
                </td>
                <td className="px-4 py-3 text-center">
                  <OrderStatusBadge status={order.status} />
                </td>
                <td className="px-4 py-3 text-center text-sm">
                  {order.trader || "Не назначен"}
                </td>
              </tr>
              {expandedOrder === order.id && (
                <tr>
                  <td colSpan={8} className="p-4 bg-[var(--jiva-background)] border-t border-[var(--jiva-border)]">
                    <div className="flex justify-between">
                      <div>
                        <p className="font-medium text-[var(--jiva-primary)] mb-2">Детали ордера</p>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm text-[var(--jiva-text-secondary)]">Трейдер: {order.trader || "Не назначен"}</p>
                            <p className="text-sm text-[var(--jiva-text-secondary)]">Реквизит: {order.requisite || "Не назначен"}</p>
                          </div>
                          <div>
                            <p className="text-sm text-[var(--jiva-text-secondary)]">Комиссия магазина: {order.store_commission}</p>
                            <p className="text-sm text-[var(--jiva-text-secondary)]">Комиссия трейдера: {order.trader_commission}</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button className="px-3 py-1 bg-[var(--jiva-background-paper)] hover:bg-[var(--jiva-background)] text-[var(--jiva-text)] rounded flex items-center gap-1">
                          <span>👁</span>
                          <span>Детали</span>
                        </button>
                        {order.status === "processing" && (
                          <button className="px-3 py-1 bg-[var(--jiva-primary)] hover:bg-[var(--jiva-primary-dark)] text-white rounded flex items-center gap-1">
                            <span>✓</span>
                            <span>Принять</span>
                          </button>
                        )}
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const OrderStatusBadge = ({ status }: { status: OrderStatus }) => {
  const getStatusConfig = (status: OrderStatus) => {
    switch (status) {
      case 'completed':
        return { text: 'Выполнен', className: 'bg-green-100 text-green-800' };
      case 'processing':
        return { text: 'В обработке', className: 'bg-blue-100 text-blue-800' };
      case 'pending':
        return { text: 'Ожидание', className: 'bg-yellow-100 text-yellow-800' };
      case 'canceled':
        return { text: 'Отменён', className: 'bg-gray-100 text-gray-800' };
      case 'disputed':
        return { text: 'Спор', className: 'bg-orange-100 text-orange-800' };
      case 'failed':
        return { text: 'Ошибка', className: 'bg-red-100 text-red-800' };
      default:
        return { text: status, className: 'bg-gray-100 text-gray-800' };
    }
  };

  const config = getStatusConfig(status);
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
      {config.text}
    </span>
  );
};

const OrderTypeBadge = ({ type }: { type: OrderType }) => {
  const getTypeConfig = (type: OrderType) => {
    switch (type) {
      case 'payin':
        return { text: 'Ввод', className: 'bg-green-100 text-green-800' };
      case 'payout':
        return { text: 'Вывод', className: 'bg-purple-100 text-purple-800' };
      default:
        return { text: type, className: 'bg-gray-100 text-gray-800' };
    }
  };

  const config = getTypeConfig(type);
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
      {config.text}
    </span>
  );
}; 