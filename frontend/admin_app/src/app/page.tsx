'use client';

import Link from 'next/link';import MainLayout from '@/layouts/MainLayout';import { RecentOrders } from '../components/Dashboard/RecentOrders';

export default function Dashboard() {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Заголовок страницы */}
        <div>
          <h1 className="text-3xl font-bold">Панель управления</h1>
          <p className="text-[var(--jiva-text-secondary)] mt-1">Добро пожаловать в административную панель JivaPay</p>
        </div>
        
        {/* Основные метрики */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <div className="flex justify-between">
              <div>
                <p className="text-[var(--jiva-text-secondary)] text-sm mb-1">Активные пользователи</p>
                <p className="text-3xl font-bold">2,847</p>
              </div>
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-success)]">+12%</span>
              <span className="text-[var(--jiva-text-secondary)]">с прошлой недели</span>
            </div>
            <Link href="/users" className="mt-4 text-sm text-[var(--jiva-primary)] hover:underline block">
              Подробнее →
            </Link>
          </div>
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <div className="flex justify-between">
              <div>
                <p className="text-[var(--jiva-text-secondary)] text-sm mb-1">Новые магазины</p>
                <p className="text-3xl font-bold">28</p>
              </div>
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-success)]">+8%</span>
              <span className="text-[var(--jiva-text-secondary)]">с прошлой недели</span>
            </div>
            <Link href="/stores" className="mt-4 text-sm text-[var(--jiva-primary)] hover:underline block">
              Подробнее →
            </Link>
          </div>
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <div className="flex justify-between">
              <div>
                <p className="text-[var(--jiva-text-secondary)] text-sm mb-1">Объем транзакций</p>
                <p className="text-3xl font-bold">₽ 4.2M</p>
              </div>
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-success)]">+17.5%</span>
              <span className="text-[var(--jiva-text-secondary)]">с прошлой недели</span>
            </div>
            <Link href="/finance" className="mt-4 text-sm text-[var(--jiva-primary)] hover:underline block">
              Подробнее →
            </Link>
          </div>
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <div className="flex justify-between">
              <div>
                <p className="text-[var(--jiva-text-secondary)] text-sm mb-1">Доход с комиссий</p>
                <p className="text-3xl font-bold">₽ 127K</p>
              </div>
              <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 8h6m-5 0a3 3 0 110 6H9l3 3m-3-6h6m6 1a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-success)]">+12.3%</span>
              <span className="text-[var(--jiva-text-secondary)]">с прошлой недели</span>
            </div>
            <Link href="/finance" className="mt-4 text-sm text-[var(--jiva-primary)] hover:underline block">
              Подробнее →
            </Link>
          </div>
        </div>
        
        {/* График транзакций */}
        <div className="mb-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Динамика транзакций</h2>
              <div className="flex bg-[var(--jiva-background)] rounded-lg overflow-hidden">
                <button className="px-3 py-1 text-sm bg-[var(--jiva-primary)] text-white">День</button>
                <button className="px-3 py-1 text-sm">Неделя</button>
                <button className="px-3 py-1 text-sm">Месяц</button>
              </div>
            </div>
            
            <div className="h-80 w-full bg-gray-100 rounded flex items-center justify-center">
              <div className="text-center">
                <p className="text-[var(--jiva-text-secondary)]">
                  График транзакций будет здесь
                </p>
                <Link href="/charts" className="text-sm text-[var(--jiva-primary)] hover:underline">
                  Смотреть подробную аналитику
                </Link>
              </div>
            </div>
          </div>
          
          {/* Статистика платежей */}
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <h2 className="text-xl font-bold mb-4">Статистика платежей</h2>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">Успешные</span>
                  <span className="text-sm text-[var(--jiva-text-secondary)]">82%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '82%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">В процессе</span>
                  <span className="text-sm text-[var(--jiva-text-secondary)]">12%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: '12%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">Неудачные</span>
                  <span className="text-sm text-[var(--jiva-text-secondary)]">6%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-red-500 h-2 rounded-full" style={{ width: '6%' }}></div>
                </div>
              </div>
            </div>
            
            <hr className="my-4 border-[var(--jiva-border)]" />
            
            <h3 className="font-semibold mb-3">Распределение по методам оплаты</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm">Банковские карты</span>
                <span className="text-sm font-medium">65%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Электронные кошельки</span>
                <span className="text-sm font-medium">24%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Криптовалюты</span>
                <span className="text-sm font-medium">8%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Другие</span>
                <span className="text-sm font-medium">3%</span>
              </div>
            </div>
            
            <div className="mt-4">
              <Link href="/charts" className="text-sm text-[var(--jiva-primary)] hover:underline">
                Подробная аналитика →
              </Link>
            </div>
          </div>
        </div>
        
        {/* Дополнительные карточки статистики */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-5 shadow-sm">
            <div className="mb-3">
              <h3 className="text-lg font-medium">Ордеры в обработке</h3>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0 rounded-full bg-[var(--jiva-background)] p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-[var(--jiva-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                  </svg>
                </div>
                <div>
                  <p className="text-3xl font-bold text-[var(--jiva-primary)]">42</p>
                  <p className="text-sm text-[var(--jiva-text-secondary)]">18 в процессе оплаты</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-5 shadow-sm">
            <div className="mb-3">
              <h3 className="text-lg font-medium">Реквизиты онлайн</h3>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0 rounded-full bg-[var(--jiva-background)] p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-[var(--jiva-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                </div>
                <div>
                  <p className="text-3xl font-bold text-[var(--jiva-primary)]">156</p>
                  <p className="text-sm text-[var(--jiva-text-secondary)]">83% доступность</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-5 shadow-sm">
            <div className="mb-3">
              <h3 className="text-lg font-medium">Конверсия</h3>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0 rounded-full bg-[var(--jiva-background)] p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-[var(--jiva-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <div>
                  <p className="text-3xl font-bold text-[var(--jiva-primary)]">89%</p>
                  <p className="text-sm text-[var(--jiva-text-secondary)]">+4.2% за месяц</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-5 shadow-sm">
            <div className="mb-3">
              <h3 className="text-lg font-medium">Среднее время</h3>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0 rounded-full bg-[var(--jiva-background)] p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-[var(--jiva-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-3xl font-bold text-[var(--jiva-primary)]">12m 30s</p>
                  <p className="text-sm text-[var(--jiva-text-secondary)]">Обработка ордера</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* История ордеров с детализацией */}
        <div className="bg-[var(--jiva-background-paper)] rounded-lg shadow-sm mb-6">
          <div className="px-6 py-4 border-b border-[var(--jiva-border)] flex justify-between items-center">
            <h2 className="text-xl font-bold">История ордеров</h2>
            <button className="px-4 py-2 bg-[var(--jiva-primary)] text-white rounded-md hover:bg-[var(--jiva-primary-dark)] transition-colors text-sm flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span>Смотреть все</span>
            </button>
          </div>
                              <div className="p-6">            <RecentOrders />          </div>
        </div>

        {/* Последние транзакции и новые пользователи */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-[var(--jiva-background-paper)] rounded-lg overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-[var(--jiva-border)] flex justify-between items-center">
              <h2 className="text-xl font-bold">Последние транзакции</h2>
              <Link href="/finance" className="text-sm text-[var(--jiva-primary)] hover:underline">
                Все транзакции
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-[var(--jiva-background)]">
                  <tr>
                    <th className="px-6 py-3 text-left">ID</th>
                    <th className="px-6 py-3 text-left">Магазин</th>
                    <th className="px-6 py-3 text-left">Сумма</th>
                    <th className="px-6 py-3 text-left">Статус</th>
                    <th className="px-6 py-3 text-left">Дата</th>
                  </tr>
                </thead>
                <tbody>
                  {[1, 2, 3, 4, 5].map((index) => (
                    <tr key={index} className="border-b border-[var(--jiva-border)] hover:bg-[var(--jiva-background)]">
                      <td className="px-6 py-4">TRX-{10000 + index}</td>
                      <td className="px-6 py-4">Магазин {index}</td>
                      <td className="px-6 py-4 font-medium">₽ {(1000 * index + 500).toFixed(2)}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          index % 3 === 0 
                            ? 'bg-green-100 text-green-800'
                            : index % 3 === 1
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                        }`}>
                          {index % 3 === 0 ? 'Успешно' : index % 3 === 1 ? 'В процессе' : 'Ошибка'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-[var(--jiva-text-secondary)]">
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
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-[var(--jiva-border)] flex justify-between items-center">
              <h2 className="text-xl font-bold">Новые пользователи</h2>
              <Link href="/users" className="text-sm text-[var(--jiva-primary)] hover:underline">
                Все пользователи
              </Link>
            </div>
            <div className="p-4 space-y-4">
              {[1, 2, 3, 4, 5].map((index) => (
                <div key={index} className="flex items-center p-2 hover:bg-[var(--jiva-background)] rounded-lg">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-400 to-indigo-500 flex items-center justify-center text-white font-medium">
                    {['АИ', 'ПС', 'МК', 'ОТ', 'ВЛ'][index-1]}
                  </div>
                  <div className="ml-4">
                    <p className="font-medium">{['Алексей Иванов', 'Павел Смирнов', 'Марина Козлова', 'Олег Трофимов', 'Вера Лебедева'][index-1]}</p>
                    <p className="text-sm text-[var(--jiva-text-secondary)]">
                      {['Мерчант', 'Администратор', 'Мерчант', 'Трейдер', 'Саппорт'][index-1]}
                    </p>
                  </div>
                  <div className="ml-auto text-xs text-[var(--jiva-text-secondary)]">
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
