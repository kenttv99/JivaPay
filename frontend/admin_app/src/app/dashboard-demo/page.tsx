'use client';

import MainLayout from '@/layouts/MainLayout';
import { RecentOrders } from '@/components/Dashboard/RecentOrders';

export default function DashboardDemoPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Заголовок страницы */}
        <div>
          <h1 className="text-3xl font-bold text-primary">🚀 Демонстрация shared-pages</h1>
          <p className="text-secondary mt-1">Эта страница демонстрирует работу DashboardPage из пакета @jivapay/shared-pages. Содержимое адаптируется под роль пользователя (admin/teamlead/support).</p>
        </div>
        
        {/* Основные метрики */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-surface rounded-lg p-6 shadow-sm border border-border">
            <div className="flex justify-between">
              <div>
                <p className="text-secondary text-sm mb-1">Активные пользователи</p>
                <p className="text-3xl font-bold text-primary">2847</p>
              </div>
              <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-success font-semibold">+12%</span>
              <span className="text-secondary">с прошлой недели</span>
            </div>
            <p className="mt-4 text-sm text-primary hover:underline cursor-pointer">Подробнее →</p>
          </div>
          
          <div className="bg-surface rounded-lg p-6 shadow-sm border border-border">
            <div className="flex justify-between">
              <div>
                <p className="text-secondary text-sm mb-1">Новые магазины</p>
                <p className="text-3xl font-bold text-success">28</p>
              </div>
              <div className="w-12 h-12 bg-success rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-success font-semibold">+8%</span>
              <span className="text-secondary">с прошлой недели</span>
            </div>
            <p className="mt-4 text-sm text-primary hover:underline cursor-pointer">Подробнее →</p>
          </div>
          
          <div className="bg-surface rounded-lg p-6 shadow-sm border border-border">
            <div className="flex justify-between">
              <div>
                <p className="text-secondary text-sm mb-1">Объем транзакций</p>
                <p className="text-3xl font-bold text-accent">₽ 4.2M</p>
              </div>
              <div className="w-12 h-12 bg-accent rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-success font-semibold">+17.5%</span>
              <span className="text-secondary">с прошлой недели</span>
            </div>
            <p className="mt-4 text-sm text-primary hover:underline cursor-pointer">Подробнее →</p>
          </div>
          
          <div className="bg-surface rounded-lg p-6 shadow-sm border border-border">
            <div className="flex justify-between">
              <div>
                <p className="text-secondary text-sm mb-1">Доход с комиссий</p>
                <p className="text-3xl font-bold text-info">₽ 127K</p>
              </div>
              <div className="w-12 h-12 bg-info rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 8h6m-5 0a3 3 0 110 6H9l3 3m-3-6h6m6 1a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-success font-semibold">+12.3%</span>
              <span className="text-secondary">с прошлой недели</span>
            </div>
            <p className="mt-4 text-sm text-primary hover:underline cursor-pointer">Подробнее →</p>
          </div>
        </div>

        {/* Дополнительные карточки статистики */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-surface rounded-lg p-6 shadow-sm border border-border">
            <div className="mb-3">
              <h3 className="text-lg font-medium text-primary">Ордера в обработке</h3>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0 rounded-full bg-neutral-light p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                  </svg>
                </div>
                <div>
                  <p className="text-3xl font-bold text-primary">142</p>
                  <p className="text-sm text-secondary">требуют внимания</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Недавние ордера */}
        <div className="bg-surface rounded-lg shadow-sm border border-border mb-6">
          <div className="px-6 py-4 border-b border-border flex justify-between items-center">
            <h2 className="text-xl font-bold text-primary">Недавние ордера</h2>
            <button className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors text-sm flex items-center gap-2">
              <span>Экспорт данных</span>
            </button>
          </div>
          <div className="p-6">
            <RecentOrders />
          </div>
        </div>
      </div>
    </MainLayout>
  );
} 