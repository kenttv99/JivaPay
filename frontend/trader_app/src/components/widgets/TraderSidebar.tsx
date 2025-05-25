'use client';

import React, { useState } from 'react';

interface TraderSidebarProps {
  isOpen?: boolean;
  onToggle?: () => void;
  className?: string;
}

export const TraderSidebar: React.FC<TraderSidebarProps> = ({
  isOpen = true,
  onToggle,
  className = ''
}) => {
  const [activeSection, setActiveSection] = useState('dashboard');

  const navigationItems = [
    {
      id: 'dashboard',
      name: 'Дашборд',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2v4zm0 0h16m-7 4h.01M8 16h.01" />
        </svg>
      ),
      href: '/dashboard',
      badge: null
    },
    {
      id: 'orders',
      name: 'Мои ордера',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      ),
      href: '/orders',
      badge: '3'
    },
    {
      id: 'requisites',
      name: 'Реквизиты',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      ),
      href: '/requisites',
      badge: '8'
    },
    {
      id: 'balance',
      name: 'Баланс',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      href: '/balance',
      badge: null
    },
    {
      id: 'transactions',
      name: 'Транзакции',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
        </svg>
      ),
      href: '/transactions',
      badge: null
    },
    {
      id: 'settings',
      name: 'Настройки',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      href: '/settings',
      badge: null
    }
  ];

  const quickActions = [
    {
      id: 'add-requisite',
      name: 'Добавить реквизит',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      ),
      color: 'text-success'
    },
    {
      id: 'quick-order',
      name: 'Быстрый ордер',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      color: 'text-info'
    },
    {
      id: 'withdraw',
      name: 'Вывод средств',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
      ),
      color: 'text-warning'
    }
  ];

  const traderStats = [
    { label: 'Активных', value: '8', color: 'text-success' },
    { label: 'В обработке', value: '3', color: 'text-warning' },
    { label: 'Доход сегодня', value: '₽12.5K', color: 'text-info' }
  ];

  return (
    <div className={`
      relative flex flex-col h-full bg-background border-r border-border 
      transition-all duration-300 ease-in-out animate-fadeIn
      ${isOpen ? 'w-72' : 'w-16'}
      ${className}
    `}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        {isOpen && (
          <div className="animate-fadeIn">
            <h2 className="text-lg font-semibold text-primary">Trader</h2>
            <p className="text-sm text-secondary">Кабинет трейдера</p>
          </div>
        )}
        
        {onToggle && (
          <button
            onClick={onToggle}
            className="p-2 rounded-lg hover:bg-surface transition-colors animated-transition"
            aria-label={isOpen ? 'Свернуть' : 'Развернуть'}
          >
            <svg 
              className={`w-4 h-4 text-secondary transition-transform duration-200 ${!isOpen ? 'rotate-180' : ''}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}
      </div>

      {/* Trader Stats */}
      {isOpen && (
        <div className="px-4 py-3 border-b border-border animate-fadeIn">
          <h3 className="text-xs font-semibold text-secondary uppercase tracking-wider mb-2">
            Статистика
          </h3>
          <div className="space-y-2">
            {traderStats.map((stat) => (
              <div key={stat.label} className="flex justify-between items-center">
                <span className="text-sm text-secondary">{stat.label}:</span>
                <span className={`text-sm font-medium ${stat.color}`}>
                  {stat.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-2 overflow-y-auto">
        {navigationItems.map((item, index) => (
          <a
            key={item.id}
            href={item.href}
            className={`
              flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 animated-transition
              ${activeSection === item.id 
                ? 'bg-secondary text-white shadow-sm' 
                : 'text-secondary hover:text-primary hover:bg-surface'
              }
            `}
            style={{ 
              animationDelay: `${index * 50}ms`,
              animationFillMode: 'both'
            }}
            onClick={() => setActiveSection(item.id)}
          >
            <div className="flex-shrink-0">
              {item.icon}
            </div>
            
            {isOpen && (
              <div className="flex-1 min-w-0 animate-fadeIn">
                <span className="text-sm font-medium truncate">
                  {item.name}
                </span>
              </div>
            )}
            
            {isOpen && item.badge && (
              <span className="flex-shrink-0 px-2 py-0.5 text-xs font-medium bg-info text-white rounded-full">
                {item.badge}
              </span>
            )}
          </a>
        ))}
      </nav>

      {/* Quick Actions */}
      {isOpen && (
        <div className="px-4 py-4 border-t border-border animate-fadeIn">
          <h3 className="text-xs font-semibold text-secondary uppercase tracking-wider mb-3">
            Быстрые действия
          </h3>
          
          <div className="space-y-2">
            {quickActions.map((action, index) => (
              <button
                key={action.id}
                className={`
                  w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg 
                  transition-all duration-200 animated-transition
                  hover:bg-surface ${action.color}
                `}
                style={{ 
                  animationDelay: `${(index + navigationItems.length) * 50}ms`,
                  animationFillMode: 'both'
                }}
              >
                {action.icon}
                <span className="truncate">{action.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Status Indicator */}
      <div className="px-4 py-3 border-t border-border">
        {isOpen ? (
          <div className="animate-fadeIn">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-secondary">Статус</span>
              <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
            </div>
            <div className="w-full bg-surface rounded-full h-2">
              <div className="bg-success h-2 rounded-full animate-pulse" style={{ width: '78%' }} />
            </div>
            <span className="text-xs text-secondary">78% эффективность</span>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
          </div>
        )}
      </div>
    </div>
  );
}; 