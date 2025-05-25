'use client';

import React, { useState } from 'react';

interface MerchantSidebarProps {
  isOpen?: boolean;
  onToggle?: () => void;
  className?: string;
}

export const MerchantSidebar: React.FC<MerchantSidebarProps> = ({
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
      id: 'stores',
      name: 'Мои магазины',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      ),
      href: '/stores',
      badge: '3'
    },
    {
      id: 'payments',
      name: 'Платежи',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      ),
      href: '/payments',
      badge: '12'
    },
    {
      id: 'gateway',
      name: 'API & Интеграция',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
      href: '/gateway',
      badge: null
    },
    {
      id: 'analytics',
      name: 'Аналитика',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      href: '/analytics',
      badge: null
    },
    {
      id: 'customers',
      name: 'Клиенты',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
        </svg>
      ),
      href: '/customers',
      badge: '247'
    },
    {
      id: 'reports',
      name: 'Отчеты',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      href: '/reports',
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
      id: 'create-store',
      name: 'Создать магазин',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      ),
      color: 'text-success'
    },
    {
      id: 'payment-link',
      name: 'Ссылка для оплаты',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
      ),
      color: 'text-info'
    },
    {
      id: 'withdraw-funds',
      name: 'Вывести средства',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
      ),
      color: 'text-warning'
    }
  ];

  const businessStats = [
    { label: 'Магазинов', value: '3', color: 'text-success' },
    { label: 'Активных', value: '2', color: 'text-info' },
    { label: 'Оборот сегодня', value: '₽89K', color: 'text-warning' }
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
            <h2 className="text-lg font-semibold text-primary">Business</h2>
            <p className="text-sm text-secondary">Кабинет мерчанта</p>
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

      {/* Business Stats */}
      {isOpen && (
        <div className="px-4 py-3 border-b border-border animate-fadeIn">
          <h3 className="text-xs font-semibold text-secondary uppercase tracking-wider mb-2">
            Статистика бизнеса
          </h3>
          <div className="space-y-2">
            {businessStats.map((stat) => (
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

      {/* Business Status Indicator */}
      <div className="px-4 py-3 border-t border-border">
        {isOpen ? (
          <div className="animate-fadeIn">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-secondary">Статус магазинов</span>
              <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
            </div>
            <div className="w-full bg-surface rounded-full h-2">
              <div className="bg-success h-2 rounded-full animate-pulse" style={{ width: '67%' }} />
            </div>
            <span className="text-xs text-secondary">2 из 3 активны</span>
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