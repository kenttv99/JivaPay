'use client';

import React from 'react';
import { StatsCard } from '../ui/StatsCard';
import { Skeleton } from '../ui/Skeleton';

export interface TraderStats {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'busy';
  ordersToday: number;
  successRate: number;
  avgTime: string;
  rating: number;
  balance: string;
}

export interface TeamStatsData {
  totalTraders: number;
  onlineTraders: number;
  totalOrdersToday: number;
  avgSuccessRate: number;
  avgResponseTime: string;
  topPerformer: string;
  teamEfficiency: number;
  pendingAssignments: number;
}

interface TeamStatsProps {
  data: TeamStatsData;
  tradersList?: TraderStats[];
  isLoading?: boolean;
  className?: string;
}

export const TeamStats: React.FC<TeamStatsProps> = ({
  data,
  tradersList = [],
  isLoading = false,
  className = ''
}) => {
  // Skeleton состояние при загрузке
  if (isLoading) {
    return (
      <div className={`space-y-6 animate-fadeIn ${className}`}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }, (_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-48" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  const teamMetrics = [
    {
      id: 'total-traders',
      title: 'Общая команда',
      value: data.totalTraders.toString(),
      subtitle: 'трейдеров',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      )
    },
    {
      id: 'online-traders',
      title: 'Онлайн сейчас',
      value: data.onlineTraders.toString(),
      change: `${Math.round((data.onlineTraders / data.totalTraders) * 100)}%`,
      trend: 'up' as const,
      subtitle: 'активных',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    },
    {
      id: 'orders-today',
      title: 'Ордеров за день',
      value: data.totalOrdersToday.toLocaleString(),
      change: '+12%',
      trend: 'up' as const,
      subtitle: 'командой',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      )
    },
    {
      id: 'team-efficiency',
      title: 'Эффективность',
      value: `${data.teamEfficiency}%`,
      change: '+5%',
      trend: 'up' as const,
      subtitle: 'команды',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      )
    }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'online': return 'bg-success/10 text-success';
      case 'busy': return 'bg-warning/10 text-warning';
      case 'offline': return 'bg-secondary/10 text-secondary';
      default: return 'bg-secondary/10 text-secondary';
    }
  };

  return (
    <div className={`space-y-6 animate-fadeIn ${className}`}>
      {/* Team Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {teamMetrics.map((metric, index) => (
          <div 
            key={metric.id}
            className="animate-fadeIn"
            style={{ 
              animationDelay: `${index * 100}ms`,
              animationFillMode: 'both'
            }}
          >
            <StatsCard
              title={metric.title}
              value={metric.value}
              change={metric.change}
              trend={metric.trend}
              subtitle={metric.subtitle}
              icon={metric.icon}
            />
          </div>
        ))}
      </div>

      {/* Team Performance Overview */}
      <div className="card-base p-6">
        <h3 className="text-lg font-semibold text-primary mb-4">
          Обзор производительности команды
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-success">
              {data.avgSuccessRate.toFixed(1)}%
            </div>
            <div className="text-sm text-secondary mt-1">
              Средняя успешность
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-info">
              {data.avgResponseTime}
            </div>
            <div className="text-sm text-secondary mt-1">
              Среднее время ответа
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-warning">
              {data.pendingAssignments}
            </div>
            <div className="text-sm text-secondary mt-1">
              Ожидают назначения
            </div>
          </div>
        </div>
      </div>

      {/* Top Performer */}
      <div className="card-base p-6">
        <h3 className="text-lg font-semibold text-primary mb-4">
          Лучший трейдер дня
        </h3>
        <div className="flex items-center gap-4 p-4 bg-success/5 rounded-lg border border-success/20">
          <div className="w-12 h-12 bg-success rounded-full flex items-center justify-center text-white text-lg font-bold">
            🏆
          </div>
          <div className="flex-1">
            <div className="font-semibold text-primary text-lg">
              {data.topPerformer}
            </div>
            <div className="text-sm text-secondary">
              Высокая производительность и качество обслуживания
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-success">98.5%</div>
            <div className="text-xs text-secondary">успешность</div>
          </div>
        </div>
      </div>

      {/* Traders List */}
      {tradersList.length > 0 && (
        <div className="card-base p-6">
          <h3 className="text-lg font-semibold text-primary mb-4">
            Статус трейдеров ({tradersList.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tradersList.map((trader, index) => (
              <div 
                key={trader.id}
                className="p-4 bg-surface rounded-lg border border-border hover:shadow-sm transition-all duration-200 animated-transition"
                style={{ 
                  animationDelay: `${index * 50}ms`,
                  animationFillMode: 'both'
                }}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${
                      trader.status === 'online' ? 'bg-success animate-pulse' :
                      trader.status === 'busy' ? 'bg-warning' : 'bg-secondary'
                    }`} />
                    <span className="font-medium text-primary">{trader.name}</span>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusBadge(trader.status)}`}>
                    {trader.status === 'online' ? 'Онлайн' :
                     trader.status === 'busy' ? 'Занят' : 'Оффлайн'}
                  </span>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-secondary">Ордеров:</span>
                    <span className="text-primary font-medium">{trader.ordersToday}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-secondary">Успешность:</span>
                    <span className={`font-medium ${
                      trader.successRate >= 95 ? 'text-success' :
                      trader.successRate >= 85 ? 'text-warning' : 'text-error'
                    }`}>
                      {trader.successRate.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-secondary">Время:</span>
                    <span className="text-primary font-medium">{trader.avgTime}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-secondary">Рейтинг:</span>
                    <span className="text-accent font-medium">⭐ {trader.rating.toFixed(1)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}; 