'use client';

import Link from 'next/link';
import MainLayout from '@/layouts/MainLayout';
import { RecentOrders } from '../components/Dashboard/RecentOrders';

export default function Dashboard() {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Заголовок страницы */}
        <div>
          <h1 className="text-3xl font-bold text-primary">Панель управления</h1>
          <p className="text-secondary mt-1">Добро пожаловать в административную панель JivaPay</p>
        </div>
        
        {/* Основные метрики */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-surface rounded-lg p-6 shadow-sm border border-border">
            <div className="flex justify-between">
              <div>
                <p className="text-secondary text-sm mb-1">Активные пользователи</p>
                <p className="text-3xl font-bold text-primary">2,847</p>
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
            <Link href="/users" className="mt-4 text-sm hover:underline block text-primary">
              Подробнее →
            </Link>
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
            <Link href="/stores" className="mt-4 text-sm hover:underline block text-primary">
              Подробнее →
            </Link>
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
            <Link href="/finance" className="mt-4 text-sm hover:underline block text-primary">
              Подробнее →
            </Link>
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
            <Link href="/finance" className="mt-4 text-sm hover:underline block text-primary">
              Подробнее →
            </Link>
          </div>
        </div>
        
        {/* График транзакций */}
        <div className="mb-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-surface rounded-lg p-6 shadow-sm border border-border">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-primary">Динамика транзакций</h2>
              <div className="flex bg-neutral-light rounded-lg overflow-hidden">
                <button className="px-3 py-1 text-sm bg-primary text-white">Неделя</button>
                <button className="px-3 py-1 text-sm text-secondary hover:text-primary transition-colors">Месяц</button>
              </div>
            </div>
            
            <div className="h-80 w-full bg-neutral-light rounded flex items-center justify-center border border-border">
              <div className="text-center">
                <p className="text-secondary">
                  График транзакций будет здесь
                </p>
                <Link href="/charts" className="text-sm hover:underline text-primary">
                  Смотреть подробную аналитику
                </Link>
              </div>
            </div>
          </div>
          
          {/* Статистика платежей */}
          <div className="bg-surface rounded-lg p-6 shadow-sm border border-border">
            <h2 className="text-xl font-bold mb-4 text-primary">Статистика платежей</h2>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-primary">Успешные</span>
                  <span className="text-sm font-semibold text-success">82%</span>
                </div>
                <div className="w-full bg-neutral-light rounded-full h-2">
                  <div className="bg-success rounded-full h-2" style={{ width: '82%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-primary">В процессе</span>
                  <span className="text-sm font-semibold text-warning">12%</span>
                </div>
                <div className="w-full bg-neutral-light rounded-full h-2">
                  <div className="bg-warning rounded-full h-2" style={{ width: '12%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-primary">Неудачные</span>
                  <span className="text-sm font-semibold text-error">6%</span>
                </div>
                <div className="w-full bg-neutral-light rounded-full h-2">
                  <div className="bg-error rounded-full h-2" style={{ width: '6%' }}></div>
                </div>
              </div>
            </div>
            
            <hr className="my-4 border-border" />
            
            <h3 className="font-semibold mb-3 text-primary">Распределение по методам оплаты</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-primary">Банковские карты</span>
                <span className="text-sm font-semibold text-primary">65%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-primary">Электронные кошельки</span>
                <span className="text-sm font-semibold text-accent">24%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-primary">Криптовалюты</span>
                <span className="text-sm font-semibold text-info">8%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-primary">Другие</span>
                <span className="text-sm font-medium text-secondary">3%</span>
              </div>
            </div>
            
            <div className="mt-4">
              <Link href="/charts" className="text-sm hover:underline text-primary">
                Подробная аналитика →
              </Link>
            </div>
          </div>
        </div>
        
        {/* Дополнительные карточки статистики */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-surface rounded-lg p-6 shadow-sm border border-border">
            <div className="mb-3">
              <h3 className="text-lg font-medium text-primary">Ордеры в обработке</h3>
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

          <div className="bg-surface rounded-lg p-6 shadow-sm border border-border">
            <div className="mb-3">
              <h3 className="text-lg font-medium text-primary">Реквизиты онлайн</h3>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0 rounded-full bg-neutral-light p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                </div>
                <div>
                  <p className="text-3xl font-bold text-success">156</p>
                  <p className="text-sm text-secondary">83% доступность</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-surface rounded-lg p-6 shadow-sm border border-border">
            <div className="mb-3">
              <h3 className="text-lg font-medium text-primary">Конверсия</h3>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0 rounded-full bg-neutral-light p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <div>
                  <p className="text-3xl font-bold text-info">89%</p>
                  <p className="text-sm text-secondary">+4.2% за месяц</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-surface rounded-lg p-6 shadow-sm border border-border">
            <div className="mb-3">
              <h3 className="text-lg font-medium text-primary">Среднее время</h3>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0 rounded-full bg-neutral-light p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-3xl font-bold text-warning">12m 30s</p>
                  <p className="text-sm text-secondary">Обработка ордера</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* История ордеров с детализацией */}
        <div className="bg-surface rounded-lg shadow-sm border border-border mb-6">
          <div className="px-6 py-4 border-b border-border flex justify-between items-center">
            <h2 className="text-xl font-bold text-primary">История ордеров</h2>
            <button className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors text-sm flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span>Смотреть все</span>
            </button>
          </div>
          <div className="p-6">
            <RecentOrders />
          </div>
        </div>

        {/* Последние транзакции и новые пользователи */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-surface rounded-lg overflow-hidden shadow-sm border border-border">
            <div className="px-6 py-4 border-b border-border flex justify-between items-center">
              <h2 className="text-xl font-bold text-primary">Последние транзакции</h2>
              <Link href="/finance" className="text-sm hover:underline text-primary">
                Все транзакции
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-neutral-light">
                  <tr>
                    <th className="px-6 py-3 text-left text-secondary font-medium">ID</th>
                    <th className="px-6 py-3 text-left text-secondary font-medium">Магазин</th>
                    <th className="px-6 py-3 text-left text-secondary font-medium">Сумма</th>
                    <th className="px-6 py-3 text-left text-secondary font-medium">Статус</th>
                    <th className="px-6 py-3 text-left text-secondary font-medium">Дата</th>
                  </tr>
                </thead>
                <tbody>
                  {[1, 2, 3, 4, 5].map((index) => (
                    <tr key={index} className="border-b border-border hover:bg-neutral-light/50 transition-colors">
                      <td className="px-6 py-4 font-medium text-primary">TRX-{10000 + index}</td>
                      <td className="px-6 py-4 text-primary">Магазин {index}</td>
                      <td className="px-6 py-4 font-medium text-primary">₽ {(1000 * index + 500).toFixed(2)}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          index % 3 === 0 
                            ? 'bg-success/10 text-success'
                            : index % 3 === 1
                              ? 'bg-warning/10 text-warning'
                              : 'bg-error/10 text-error'
                        }`}>
                          {index % 3 === 0 ? 'Успешно' : index % 3 === 1 ? 'В процессе' : 'Ошибка'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-secondary">
                        {new Date(Date.now() - index * 3600000).toLocaleString('ru-RU', {
                          hour: '2-digit',
                          minute: '2-digit',
                          day: '2-digit',
                          month: '2-digit'
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          <div className="bg-surface rounded-lg overflow-hidden shadow-sm border border-border">
            <div className="px-6 py-4 border-b border-border flex justify-between items-center">
              <h2 className="text-xl font-bold text-primary">Новые пользователи</h2>
              <Link href="/users" className="text-sm hover:underline text-primary">
                Все пользователи
              </Link>
            </div>
            <div className="p-4 space-y-4">
              {[1, 2, 3, 4, 5].map((index) => (
                <div key={index} className="flex items-center p-2 hover:bg-neutral-light/50 rounded-lg transition-colors">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-medium bg-primary">
                    {['АИ', 'ПС', 'МК', 'ОТ', 'ВЛ'][index-1]}
                  </div>
                  <div className="ml-4">
                    <p className="font-medium text-primary">{['Алексей Иванов', 'Павел Смирнов', 'Марина Козлова', 'Олег Трофимов', 'Вера Лебедева'][index-1]}</p>
                    <p className="text-sm text-secondary">
                      {['Мерчант', 'Администратор', 'Мерчант', 'Трейдер', 'Саппорт'][index-1]}
                    </p>
                  </div>
                  <div className="ml-auto text-xs text-secondary">
                    {['5 мин', '12 мин', '24 мин', '2 ч', '4 ч'][index-1]}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
