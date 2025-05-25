'use client';

import React, { useState } from 'react';

interface TeamleadHeaderProps {
  onSidebarToggle?: () => void;
  className?: string;
}

export const TeamleadHeader: React.FC<TeamleadHeaderProps> = ({
  onSidebarToggle,
  className = ''
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  const notifications = [
    { id: 1, text: 'Трейдер trader_05 превысил лимиты', time: '3 мин назад', type: 'warning', urgent: true },
    { id: 2, text: 'Новое назначение: ордер #ORD-78901', time: '5 мин назад', type: 'assignment', urgent: true },
    { id: 3, text: 'Команда выполнила дневной план', time: '1 час назад', type: 'success', urgent: false },
    { id: 4, text: 'Трейдер trader_02 запросил отпуск', time: '2 часа назад', type: 'request', urgent: false }
  ];

  const urgentCount = notifications.filter(n => n.urgent).length;

  const quickActions = [
    {
      id: 'bulk-assign',
      name: 'Массовое назначение',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      ),
      color: 'bg-success hover:bg-green-600'
    },
    {
      id: 'redistribute',
      name: 'Перераспределить',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
        </svg>
      ),
      color: 'bg-info hover:bg-info/80'
    },
    {
      id: 'team-meeting',
      name: 'Совещание',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      color: 'bg-warning hover:bg-yellow-600'
    }
  ];

  const teamMetrics = [
    { label: 'Онлайн', value: '8/12', status: 'success' },
    { label: 'Активность', value: '94%', status: 'info' },
    { label: 'Задачи', value: '5', status: 'warning' }
  ];

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
              placeholder="Поиск трейдеров, ордеров, задач..."
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

          {/* Team Metrics */}
          <div className="flex items-center gap-3">
            {teamMetrics.map((metric) => (
              <div 
                key={metric.label}
                className={`
                  flex items-center gap-2 px-3 py-1.5 rounded-full
                  ${metric.status === 'success' ? 'bg-success/10 text-success' :
                    metric.status === 'warning' ? 'bg-warning/10 text-warning' :
                    'bg-info/10 text-info'}
                `}
              >
                <span className="text-sm font-medium">{metric.label}: {metric.value}</span>
              </div>
            ))}
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

          {/* Team Status */}
          <div className="flex items-center gap-2 px-3 py-2 bg-surface rounded-lg">
            <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
            <span className="text-sm text-primary font-medium">Команда активна</span>
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
                  <h3 className="font-semibold text-primary">Уведомления команды</h3>
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
                    Все уведомления команды
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
                TL
              </div>
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium text-primary">Team Lead</p>
                <p className="text-xs text-secondary">Команда #007</p>
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
                      TL
                    </div>
                    <div>
                      <p className="font-medium text-primary">Team Lead #007</p>
                      <p className="text-sm text-secondary">teamlead@jivapay.com</p>
                      <p className="text-xs text-info">12 трейдеров в команде</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Моя команда
                    </button>
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Производительность
                    </button>
                    <button className="w-full text-left px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface rounded transition-colors">
                      Настройки
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