'use client';

import React, { useState } from 'react';

interface SupportSidebarProps {
  isOpen?: boolean;
  onToggle?: () => void;
  className?: string;
}

export const SupportSidebar: React.FC<SupportSidebarProps> = ({
  isOpen = true,
  onToggle,
  className = ''
}) => {
  const [activeSection, setActiveSection] = useState('tickets');

  const navigationItems = [
    {
      id: 'dashboard',
      name: 'Дашборд',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6a2 2 0 01-2 2H10a2 2 0 01-2-2V5z" />
        </svg>
      ),
      href: '/dashboard',
      badge: null
    },
    {
      id: 'tickets',
      name: 'Тикеты поддержки',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      ),
      href: '/tickets',
      badge: '15'
    },
    {
      id: 'users',
      name: 'Пользователи',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
        </svg>
      ),
      href: '/users',
      badge: null
    },
    {
      id: 'orders',
      name: 'Проблемные ордера',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v13m0-13V6a2 2 0 112 0v6.5m0 0L16 10m-4 2.5L8 10" />
          <circle cx="12" cy="12" r="3" fill="currentColor" />
        </svg>
      ),
      href: '/orders',
      badge: '8'
    },
    {
      id: 'disputes',
      name: 'Споры',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      ),
      href: '/disputes',
      badge: '3'
    },
    {
      id: 'knowledge',
      name: 'База знаний',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      href: '/knowledge-base',
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
    }
  ];

  const quickActions = [
    {
      id: 'escalate',
      name: 'Эскалировать в админ',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      color: 'text-warning'
    },
    {
      id: 'broadcast',
      name: 'Системное уведомление',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
        </svg>
      ),
      color: 'text-info'
    },
    {
      id: 'emergency',
      name: 'Экстренная блокировка',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      ),
      color: 'text-error'
    }
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
            <h2 className="text-lg font-semibold text-primary">JivaPay Support</h2>
            <p className="text-sm text-secondary">Панель поддержки</p>
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
              <span className="flex-shrink-0 px-2 py-0.5 text-xs font-medium bg-error text-white rounded-full animate-pulse">
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

      {/* Status */}
      <div className="px-4 py-3 border-t border-border">
        {isOpen ? (
          <div className="flex items-center gap-2 animate-fadeIn">
            <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
            <span className="text-xs text-secondary">Система работает</span>
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