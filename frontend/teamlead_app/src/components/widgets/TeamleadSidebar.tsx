'use client';

import React, { useState } from 'react';

interface TeamleadSidebarProps {
  isOpen?: boolean;
  onToggle?: () => void;
  className?: string;
}

export const TeamleadSidebar: React.FC<TeamleadSidebarProps> = ({
  isOpen = true,
  onToggle,
  className = ''
}) => {
  const [activeSection, setActiveSection] = useState('dashboard');

  const navigationItems = [
    {
      id: 'dashboard',
      name: 'Дашборд команды',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      href: '/dashboard',
      badge: null
    },
    {
      id: 'team',
      name: 'Моя команда',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      href: '/team',
      badge: '12'
    },
    {
      id: 'assignments',
      name: 'Назначения',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
      ),
      href: '/assignments',
      badge: '5'
    },
    {
      id: 'monitoring',
      name: 'Мониторинг',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      href: '/monitoring',
      badge: '8'
    },
    {
      id: 'performance',
      name: 'Производительность',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      href: '/performance',
      badge: null
    },
    {
      id: 'training',
      name: 'Обучение',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      href: '/training',
      badge: null
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
      id: 'schedule',
      name: 'Расписание',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
      href: '/schedule',
      badge: '3'
    }
  ];

  const quickActions = [
    {
      id: 'assign-trader',
      name: 'Назначить трейдера',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      ),
      color: 'text-success'
    },
    {
      id: 'send-message',
      name: 'Сообщение команде',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      color: 'text-info'
    },
    {
      id: 'emergency-mode',
      name: 'Экстренное перераспределение',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      ),
      color: 'text-error'
    }
  ];

  const teamStats = [
    { label: 'Онлайн', value: '8/12', color: 'text-success' },
    { label: 'Загружены', value: '10/12', color: 'text-warning' },
    { label: 'Эффективность', value: '94%', color: 'text-info' }
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
            <h2 className="text-lg font-semibold text-primary">Team Lead</h2>
            <p className="text-sm text-secondary">Управление командой</p>
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

      {/* Team Stats */}
      {isOpen && (
        <div className="px-4 py-3 border-b border-border animate-fadeIn">
          <h3 className="text-xs font-semibold text-secondary uppercase tracking-wider mb-2">
            Статус команды
          </h3>
          <div className="space-y-2">
            {teamStats.map((stat) => (
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

      {/* Team Performance Indicator */}
      <div className="px-4 py-3 border-t border-border">
        {isOpen ? (
          <div className="animate-fadeIn">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-secondary">Команда работает</span>
              <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
            </div>
            <div className="w-full bg-surface rounded-full h-2">
              <div className="bg-success h-2 rounded-full animate-pulse" style={{ width: '94%' }} />
            </div>
            <span className="text-xs text-secondary">94% эффективность</span>
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