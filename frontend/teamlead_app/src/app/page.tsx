'use client';

import React from 'react';
import { TeamleadLayout } from '../layouts/TeamleadLayout';
import { TeamStats, type TeamStatsData, type TraderStats } from '../components/TeamStats/TeamStats';

// Мок данные для демонстрации
const mockTeamData: TeamStatsData = {
  totalTraders: 12,
  onlineTraders: 8,
  totalOrdersToday: 247,
  avgSuccessRate: 94.5,
  avgResponseTime: '3.2 мин',
  topPerformer: 'trader_007',
  teamEfficiency: 94,
  pendingAssignments: 5
};

const mockTraders: TraderStats[] = [
  {
    id: 'trader_001',
    name: 'trader_001',
    status: 'online',
    ordersToday: 28,
    successRate: 97.2,
    avgTime: '2.8 мин',
    rating: 4.9,
    balance: '₽ 125,000'
  },
  {
    id: 'trader_002',
    name: 'trader_002',
    status: 'busy',
    ordersToday: 22,
    successRate: 94.5,
    avgTime: '3.1 мин',
    rating: 4.7,
    balance: '₽ 89,500'
  },
  {
    id: 'trader_003',
    name: 'trader_003',
    status: 'online',
    ordersToday: 31,
    successRate: 98.5,
    avgTime: '2.4 мин',
    rating: 4.8,
    balance: '₽ 156,800'
  },
  {
    id: 'trader_004',
    name: 'trader_004',
    status: 'offline',
    ordersToday: 0,
    successRate: 92.1,
    avgTime: '3.5 мин',
    rating: 4.5,
    balance: '₽ 67,200'
  },
  {
    id: 'trader_005',
    name: 'trader_005',
    status: 'online',
    ordersToday: 25,
    successRate: 95.8,
    avgTime: '2.9 мин',
    rating: 4.6,
    balance: '₽ 98,400'
  },
  {
    id: 'trader_006',
    name: 'trader_006',
    status: 'busy',
    ordersToday: 19,
    successRate: 93.2,
    avgTime: '3.8 мин',
    rating: 4.4,
    balance: '₽ 78,900'
  }
];

const pendingAssignments = [
  {
    id: 'ORD-78901',
    type: 'payin',
    amount: '₽ 25,000',
    currency: 'BTC',
    priority: 'high',
    waitTime: '12 мин'
  },
  {
    id: 'ORD-78902',
    type: 'payout',
    amount: '₽ 15,500',
    currency: 'ETH',
    priority: 'medium',
    waitTime: '8 мин'
  },
  {
    id: 'ORD-78903',
    type: 'payin',
    amount: '₽ 45,000',
    currency: 'BTC',
    priority: 'urgent',
    waitTime: '5 мин'
  }
];

const recentActivities = [
  'trader_003 завершил ордер #ORD-78845 (98% успех)',
  'trader_001 превысил дневной план на 120%',
  'Команда достигла 95% эффективности',
  'trader_005 запросил помощь по сложному ордеру',
  'Обновлены лимиты для trader_002'
];

export default function TeamleadDashboard() {
  return (
    <TeamleadLayout>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-primary">
              Дашборд команды
            </h1>
            <p className="text-secondary mt-1">
              Управление командой из {mockTeamData.totalTraders} трейдеров • {mockTeamData.onlineTraders} онлайн
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <button className="px-4 py-2 bg-success text-white rounded-lg hover:bg-green-600 transition-colors animated-transition">
              Массовое назначение
            </button>
            <button className="px-4 py-2 bg-info text-white rounded-lg hover:bg-info/80 transition-colors animated-transition">
              Совещание команды
            </button>
            <button className="px-4 py-2 bg-warning text-white rounded-lg hover:bg-yellow-600 transition-colors animated-transition">
              Перераспределить
            </button>
          </div>
        </div>

        {/* Team Statistics */}
        <div>
          <h2 className="text-xl font-semibold text-primary mb-4">
            Статистика команды
          </h2>
          <TeamStats 
            data={mockTeamData}
            tradersList={mockTraders}
          />
        </div>

        {/* Pending Assignments */}
        <div>
          <h2 className="text-xl font-semibold text-primary mb-4">
            Ожидают назначения ({pendingAssignments.length})
          </h2>
          <div className="card-base p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {pendingAssignments.map((assignment) => (
                <div 
                  key={assignment.id}
                  className={`
                    p-4 rounded-lg border transition-all duration-200 animated-transition hover:shadow-sm
                    ${assignment.priority === 'urgent' ? 'border-error bg-error/5' :
                      assignment.priority === 'high' ? 'border-warning bg-warning/5' :
                      'border-border bg-surface'}
                  `}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-primary">{assignment.id}</span>
                    <span className={`
                      px-2 py-1 text-xs rounded-full
                      ${assignment.priority === 'urgent' ? 'bg-error text-white' :
                        assignment.priority === 'high' ? 'bg-warning text-white' :
                        'bg-info text-white'}
                    `}>
                      {assignment.priority === 'urgent' ? 'Срочно' :
                       assignment.priority === 'high' ? 'Высокий' : 'Средний'}
                    </span>
                  </div>
                  
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-secondary">Тип:</span>
                      <span className="text-primary">
                        {assignment.type === 'payin' ? 'Пополнение' : 'Вывод'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-secondary">Сумма:</span>
                      <span className="text-primary font-medium">{assignment.amount}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-secondary">Валюта:</span>
                      <span className="text-accent">{assignment.currency}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-secondary">Ожидает:</span>
                      <span className="text-warning font-medium">{assignment.waitTime}</span>
                    </div>
                  </div>
                  
                  <button className="w-full mt-3 px-3 py-2 bg-secondary text-white rounded-lg hover:bg-secondary/80 transition-colors text-sm">
                    Назначить трейдера
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Management Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card-base p-6">
            <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
              <svg className="w-5 h-5 text-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              Быстрые действия
            </h3>
            <div className="space-y-3">
              <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                Создать групповое задание
              </button>
              <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                Перераспределить нагрузку
              </button>
              <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                Экспорт отчета команды
              </button>
              <button className="w-full text-left p-3 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-sm">
                Настройки автоназначения
              </button>
            </div>
          </div>

          <div className="card-base p-6">
            <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
              <svg className="w-5 h-5 text-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Недавняя активность
            </h3>
            <div className="space-y-2 text-sm">
              {recentActivities.map((activity, index) => (
                <div key={index} className="p-2 bg-surface rounded text-secondary">
                  {activity}
                </div>
              ))}
            </div>
          </div>

          <div className="card-base p-6">
            <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
              <svg className="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Цели команды
            </h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-secondary">Дневной план:</span>
                  <span className="text-success font-medium">112%</span>
                </div>
                <div className="w-full bg-surface rounded-full h-2">
                  <div className="bg-success h-2 rounded-full" style={{ width: '100%' }} />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-secondary">Качество:</span>
                  <span className="text-info font-medium">94.5%</span>
                </div>
                <div className="w-full bg-surface rounded-full h-2">
                  <div className="bg-info h-2 rounded-full" style={{ width: '94.5%' }} />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-secondary">Активность:</span>
                  <span className="text-warning font-medium">67%</span>
                </div>
                <div className="w-full bg-surface rounded-full h-2">
                  <div className="bg-warning h-2 rounded-full" style={{ width: '67%' }} />
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>
    </TeamleadLayout>
  );
}
