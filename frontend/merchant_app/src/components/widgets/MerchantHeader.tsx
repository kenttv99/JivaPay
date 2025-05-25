'use client';

import React, { useState } from 'react';

interface MerchantHeaderProps {
  onSidebarToggle?: () => void;
  className?: string;
}

export const MerchantHeader: React.FC<MerchantHeaderProps> = ({
  onSidebarToggle,
  className = ''
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  const notifications = [
    { id: 1, text: 'Новый платеж ₽5,420 в магазине "TechStore"', time: '2 мин назад', type: 'payment', urgent: false },
    { id: 2, text: 'Заказ #12345 ожидает подтверждения доставки', time: '5 мин назад', type: 'order', urgent: true },
    { id: 3, text: 'Месячный лимит по комиссии достигнут на 85%', time: '1 час назад', type: 'warning', urgent: true },
    { id: 4, text: 'Интеграция API для нового магазина готова', time: '2 часа назад', type: 'integration', urgent: false },
    { id: 5, text: 'Вывод средств ₽250,000 обработан', time: '3 часа назад', type: 'withdrawal', urgent: false }
  ];

  const urgentCount = notifications.filter(n => n.urgent).length;

  const quickActions = [
    {
      id: 'create-payment',
      name: 'Создать платеж',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
      ),
      color: 'bg-success hover:bg-green-600'
    },
    {
      id: 'add-store',
      name: 'Новый магазин',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      ),
      color: 'bg-info hover:bg-info/80'
    },
    {
      id: 'generate-link',
      name: 'Ссылка оплаты',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
      ),
      color: 'bg-warning hover:bg-yellow-600'
    }
  ];

  const currentBalance = '₽1,234,567';
  const todayRevenue = '+₽89,340';
  const activeStores = '2 из 3';

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
              placeholder="Поиск платежей, магазинов, клиентов..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="
                pl-10 pr-4 py-2 w-96 rounded-lg border border-border 
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

          {/* Business Metrics */}
          <div className="flex items-center gap-4">
            <div className="px-3 py-1.5 bg-success/10 text-success rounded-lg">
              <div className="text-xs text-success/80">Баланс</div>
              <div className="text-sm font-semibold">{currentBalance}</div>
            </div>
            
            <div className="px-3 py-1.5 bg-info/10 text-info rounded-lg">
              <div className="text-xs text-info/80">Оборот сегодня</div>
              <div className="text-sm font-semibold">{todayRevenue}</div>
            </div>

            <div className="px-3 py-1.5 bg-warning/10 text-warning rounded-lg">
              <div className="text-xs text-warning/80">Активные магазины</div>
              <div className="text-sm font-semibold">{activeStores}</div>
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

          {/* Business Status */}
          <div className="flex items-center gap-2 px-3 py-2 bg-surface rounded-lg">
            <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
            <span className="text-sm text-primary font-medium">Работаем</span>
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
              <div className="absolute right-0 top-full mt-2 w-96 dropdown-panel">
                <div className="p-4 border-b border-border">
                  <h3 className="font-semibold text-primary">Уведомления бизнеса</h3>
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
                MR
              </div>
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium text-primary">TechCompany Ltd</p>
                <p className="text-xs text-secondary">Мерчант</p>
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
              <div className="absolute right-0 top-full mt-2 w-72 dropdown-panel">
                <div className="p-4">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 bg-secondary rounded-full flex items-center justify-center text-white text-lg font-medium">
                      MR
                    </div>
                    <div>
                      <p className="font-medium text-primary">TechCompany Ltd</p>
                      <p className="text-sm text-secondary">merchant@techcompany.com</p>
                      <p className="text-xs text-info">3 активных магазина</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Профиль компании
                    </button>
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Мои магазины
                    </button>
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      API & Интеграции
                    </button>
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Финансы и выводы
                    </button>
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Настройки бизнеса
                    </button>
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Документооборот
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