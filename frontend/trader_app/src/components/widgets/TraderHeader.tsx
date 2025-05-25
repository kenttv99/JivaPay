'use client';

import React, { useState } from 'react';

interface TraderHeaderProps {
  onSidebarToggle?: () => void;
  className?: string;
}

export const TraderHeader: React.FC<TraderHeaderProps> = ({
  onSidebarToggle,
  className = ''
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  const notifications = [
    { id: 1, text: 'Новый ордер #ORD-54321 назначен вам', time: '1 мин назад', type: 'order', urgent: true },
    { id: 2, text: 'Пополнение реквизита SBER-1234 обработано', time: '3 мин назад', type: 'requisite', urgent: false },
    { id: 3, text: 'Лимит по ордерам достигнут на 80%', time: '10 мин назад', type: 'warning', urgent: true },
    { id: 4, text: 'Выплата ₽15,000 готова к подтверждению', time: '15 мин назад', type: 'payout', urgent: true }
  ];

  const urgentCount = notifications.filter(n => n.urgent).length;

  const quickActions = [
    {
      id: 'accept-order',
      name: 'Принять ордер',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'bg-success hover:bg-green-600'
    },
    {
      id: 'add-requisite',
      name: 'Добавить реквизит',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      ),
      color: 'bg-info hover:bg-info/80'
    },
    {
      id: 'withdraw',
      name: 'Вывести',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
      ),
      color: 'bg-warning hover:bg-yellow-600'
    }
  ];

  const currentBalance = '₽156,750';
  const todayEarnings = '+₽12,500';

  return (
    <header className={`
      bg-background border-b border-border px-6 py-4 
      animate-fadeIn ${className}
    `}>
      <div className="flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center gap-4">
          {onSidebarToggle && (
            <button
              onClick={onSidebarToggle}
              className="p-2 rounded-lg hover:bg-surface transition-colors animated-transition"
              aria-label="Переключить сайдбар"
            >
              <svg className="w-5 h-5 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          )}

          {/* Search */}
          <div className="relative">
            <svg 
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary w-4 h-4"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Поиск ордеров, реквизитов..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="
                pl-10 pr-4 py-2 w-80 rounded-lg border border-border 
                bg-surface text-primary placeholder-secondary
                focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent
                transition-all duration-200 animated-transition
              "
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary hover:text-primary"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* Balance Info */}
          <div className="flex items-center gap-4">
            <div className="px-3 py-1.5 bg-success/10 text-success rounded-lg">
              <div className="text-xs text-success/80">Баланс</div>
              <div className="text-sm font-semibold">{currentBalance}</div>
            </div>
            
            <div className="px-3 py-1.5 bg-info/10 text-info rounded-lg">
              <div className="text-xs text-info/80">Сегодня</div>
              <div className="text-sm font-semibold">{todayEarnings}</div>
            </div>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {/* Quick Actions */}
          <div className="flex items-center gap-2">
            {quickActions.map((action) => (
              <button
                key={action.id}
                className={`
                  flex items-center gap-2 px-3 py-2 text-sm font-medium text-white rounded-lg
                  transition-all duration-200 animated-transition hover:scale-105 shadow-sm
                  ${action.color}
                `}
                title={action.name}
              >
                {action.icon}
                <span className="hidden lg:inline">{action.name}</span>
              </button>
            ))}
          </div>

          {/* Status */}
          <div className="flex items-center gap-2 px-3 py-2 bg-surface rounded-lg">
            <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
            <span className="text-sm text-primary font-medium">Активен</span>
          </div>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-lg hover:bg-surface transition-colors animated-transition"
            >
              <svg className="w-5 h-5 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              {urgentCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-error text-white text-xs rounded-full flex items-center justify-center animate-pulse">
                  {urgentCount}
                </span>
              )}
            </button>

            {showNotifications && (
              <div className="absolute right-0 top-full mt-2 w-80 dropdown-panel">
                <div className="p-4 border-b border-border">
                  <h3 className="font-semibold text-primary">Уведомления</h3>
                  <p className="text-sm text-secondary">{urgentCount} требуют внимания</p>
                </div>
                
                <div className="max-h-80 overflow-y-auto">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`
                        p-4 border-b border-border last:border-b-0 hover:bg-surface 
                        transition-colors animated-transition cursor-pointer
                        ${notification.urgent ? 'border-l-4 border-l-warning' : ''}
                      `}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`
                          w-2 h-2 rounded-full mt-2 flex-shrink-0
                          ${notification.urgent ? 'bg-warning animate-pulse' : 'bg-success'}
                        `} />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-primary font-medium">
                            {notification.text}
                          </p>
                          <p className="text-xs text-secondary mt-1">
                            {notification.time}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="p-3 border-t border-border">
                  <button className="w-full text-center text-sm text-secondary hover:text-primary transition-colors">
                    Показать все уведомления
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Profile */}
          <div className="relative">
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center gap-2 p-2 rounded-lg hover:bg-surface transition-colors animated-transition"
            >
              <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center text-white text-sm font-medium">
                TR
              </div>
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium text-primary">Trader #001</p>
                <p className="text-xs text-secondary">Активен</p>
              </div>
              <svg 
                className={`w-4 h-4 text-secondary transition-transform duration-200 ${showProfile ? 'rotate-180' : ''}`}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showProfile && (
              <div className="absolute right-0 top-full mt-2 w-64 dropdown-panel">
                <div className="p-4">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 bg-secondary rounded-full flex items-center justify-center text-white text-lg font-medium">
                      TR
                    </div>
                    <div>
                      <p className="font-medium text-primary">Trader #001</p>
                      <p className="text-sm text-secondary">trader001@jivapay.com</p>
                      <p className="text-xs text-info">78% эффективность</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Профиль
                    </button>
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Мои ордера
                    </button>
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Настройки
                    </button>
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Статистика
                    </button>
                    <hr className="border-border" />
                    <button className="w-full text-left px-3 py-2 text-sm text-error hover:bg-error/10 rounded transition-colors">
                      Выйти
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}; 