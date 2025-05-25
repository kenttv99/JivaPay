'use client';

import React, { useState } from 'react';
import { Skeleton } from '../ui/Skeleton';

interface Order {
  id: string;
  type: 'input' | 'output';
  amount: string;
  currency: string;
  method: string;
  status: 'pending' | 'processing' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  createdAt: string;
  deadline?: string;
  commission: string;
  requisite?: string;
  customer: string;
}

interface OrdersWidgetProps {
  loading?: boolean;
  className?: string;
}

export const OrdersWidget: React.FC<OrdersWidgetProps> = ({
  loading = false,
  className = ''
}) => {
  const [filter, setFilter] = useState<'all' | 'pending' | 'processing' | 'completed'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'amount' | 'priority'>('date');

  const mockOrders: Order[] = [
    {
      id: 'ORD-54321',
      type: 'input',
      amount: '25,000',
      currency: 'RUB',
      method: 'Сбербанк',
      status: 'pending',
      priority: 'urgent',
      createdAt: '14:23',
      deadline: '15:00',
      commission: '375',
      requisite: 'SBER-1234',
      customer: 'client_2847'
    },
    {
      id: 'ORD-54320',
      type: 'output',
      amount: '15,750',
      currency: 'RUB', 
      method: 'Тинькофф',
      status: 'processing',
      priority: 'high',
      createdAt: '14:15',
      deadline: '14:45',
      commission: '236',
      requisite: 'TINK-5678',
      customer: 'client_1923'
    },
    {
      id: 'ORD-54319',
      type: 'input',
      amount: '8,500',
      currency: 'RUB',
      method: 'ВТБ',
      status: 'completed',
      priority: 'medium',
      createdAt: '13:42',
      commission: '128',
      requisite: 'VTB-9012',
      customer: 'client_5661'
    },
    {
      id: 'ORD-54318',
      type: 'output',
      amount: '42,300',
      currency: 'RUB',
      method: 'Альфа-Банк',
      status: 'pending',
      priority: 'high',
      createdAt: '13:15',
      deadline: '14:30',
      commission: '635',
      customer: 'client_3498'
    }
  ];

  const getStatusColor = (status: Order['status']) => {
    switch (status) {
      case 'pending': return 'bg-warning/10 text-warning border-warning/20';
      case 'processing': return 'bg-info/10 text-info border-info/20';
      case 'completed': return 'bg-success/10 text-success border-success/20';
      case 'cancelled': return 'bg-error/10 text-error border-error/20';
    }
  };

  const getPriorityColor = (priority: Order['priority']) => {
    switch (priority) {
      case 'low': return 'bg-surface/80 text-secondary';
      case 'medium': return 'bg-info/10 text-info';
      case 'high': return 'bg-warning/10 text-warning';
      case 'urgent': return 'bg-error/10 text-error animate-pulse';
    }
  };

  const getStatusText = (status: Order['status']) => {
    switch (status) {
      case 'pending': return 'Ожидает';
      case 'processing': return 'В работе';
      case 'completed': return 'Завершен';
      case 'cancelled': return 'Отменен';
    }
  };

  const getPriorityText = (priority: Order['priority']) => {
    switch (priority) {
      case 'low': return 'Низкий';
      case 'medium': return 'Средний';
      case 'high': return 'Высокий';
      case 'urgent': return 'СРОЧНО';
    }
  };

  const filteredOrders = mockOrders.filter(order => 
    filter === 'all' || order.status === filter
  );

  if (loading) {
    return (
      <div className={`card-base p-6 ${className}`}>
        <div className="flex items-center justify-between mb-6">
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-8 w-24" />
        </div>
        
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border border-border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <Skeleton className="h-5 w-24" />
                <Skeleton className="h-6 w-16" />
              </div>
              <div className="flex items-center gap-4">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-4 w-24" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`card-base p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-primary flex items-center gap-2">
            <svg className="w-6 h-6 text-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            Мои ордера
          </h2>
          <p className="text-secondary text-sm">
            {filteredOrders.length} ордеров • {filteredOrders.filter(o => o.status === 'pending').length} ожидают
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'pending' | 'processing' | 'completed')}
            className="px-3 py-2 border border-border rounded-lg bg-surface text-primary text-sm"
          >
            <option value="all">Все ордера</option>
            <option value="pending">Ожидают</option>
            <option value="processing">В работе</option>
            <option value="completed">Завершены</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'amount' | 'priority')}
            className="px-3 py-2 border border-border rounded-lg bg-surface text-primary text-sm"
          >
            <option value="date">По времени</option>
            <option value="amount">По сумме</option>
            <option value="priority">По приоритету</option>
          </select>
        </div>
      </div>

      {/* Orders List */}
      <div className="space-y-4">
        {filteredOrders.length > 0 ? (
          filteredOrders.map((order, index) => (
            <div
              key={order.id}
              className={`
                border border-border rounded-lg p-4 hover:shadow-md transition-all duration-200 
                animate-fadeIn cursor-pointer hover:border-secondary/20
                ${order.priority === 'urgent' ? 'ring-2 ring-error/20' : ''}
              `}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-secondary">#{order.id}</span>
                  
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(order.priority)}`}>
                    {getPriorityText(order.priority)}
                  </span>
                  
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(order.status)}`}>
                    {getStatusText(order.status)}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  {order.deadline && order.status === 'pending' && (
                    <span className="text-xs text-warning flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      до {order.deadline}
                    </span>
                  )}
                  
                  <div className={`
                    flex items-center gap-1 px-2 py-1 rounded text-xs font-medium
                    ${order.type === 'input' 
                      ? 'bg-success/10 text-success' 
                      : 'bg-info/10 text-info'
                    }
                  `}>
                    {order.type === 'input' ? (
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16l-4-4m0 0l4-4m-4 4h18" />
                      </svg>
                    ) : (
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                      </svg>
                    )}
                    {order.type === 'input' ? 'Ввод' : 'Вывод'}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-secondary">Сумма:</span>
                  <p className="font-semibold text-primary">₽ {order.amount}</p>
                </div>
                
                <div>
                  <span className="text-secondary">Метод:</span>
                  <p className="text-primary">{order.method}</p>
                </div>
                
                <div>
                  <span className="text-secondary">Комиссия:</span>
                  <p className="text-info">₽ {order.commission}</p>
                </div>
                
                <div>
                  <span className="text-secondary">Время:</span>
                  <p className="text-primary">{order.createdAt}</p>
                </div>
              </div>

              {order.requisite && (
                <div className="mt-2 pt-2 border-t border-border">
                  <span className="text-xs text-secondary">Реквизит: </span>
                  <span className="text-xs font-mono text-primary">{order.requisite}</span>
                </div>
              )}

              {/* Action buttons for pending orders */}
              {order.status === 'pending' && (
                <div className="mt-4 flex gap-2">
                  <button className="px-4 py-2 bg-success text-white rounded-lg text-sm font-medium hover:bg-green-600 transition-colors">
                    Принять
                  </button>
                  <button className="px-4 py-2 bg-surface text-secondary border border-border rounded-lg text-sm font-medium hover:bg-surface/80 transition-colors">
                    Детали
                  </button>
                  {order.priority === 'urgent' && (
                    <button className="px-4 py-2 bg-warning text-white rounded-lg text-sm font-medium hover:bg-yellow-600 transition-colors">
                      Срочно!
                    </button>
                  )}
                </div>
              )}

              {/* Action buttons for processing orders */}
              {order.status === 'processing' && (
                <div className="mt-4 flex gap-2">
                  <button className="px-4 py-2 bg-info text-white rounded-lg text-sm font-medium hover:bg-info/80 transition-colors">
                    Завершить
                  </button>
                  <button className="px-4 py-2 bg-surface text-secondary border border-border rounded-lg text-sm font-medium hover:bg-surface/80 transition-colors">
                    Чат с клиентом
                  </button>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-secondary mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p className="text-secondary">Нет ордеров для отображения</p>
          </div>
        )}
      </div>
    </div>
  );
}; 