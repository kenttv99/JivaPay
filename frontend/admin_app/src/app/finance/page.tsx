'use client';

import MainLayout from '@/layouts/MainLayout';

export default function FinancePage() {
  return (
    <MainLayout>
      <div className="max-w-full">
        <h1 className="text-3xl font-bold mb-6">Финансы</h1>
        
        {/* Баланс системы */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <p className="text-[var(--jiva-text-secondary)] text-sm mb-2">Общий баланс</p>
            <p className="text-3xl font-bold">₽ 12,458,320.00</p>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-success)]">+2.5%</span>
              <span className="text-[var(--jiva-text-secondary)]">за неделю</span>
            </div>
          </div>
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <p className="text-[var(--jiva-text-secondary)] text-sm mb-2">Комиссии за месяц</p>
            <p className="text-3xl font-bold">₽ 245,320.00</p>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-success)]">+5.2%</span>
              <span className="text-[var(--jiva-text-secondary)]">от прошлого месяца</span>
            </div>
          </div>
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <p className="text-[var(--jiva-text-secondary)] text-sm mb-2">Транзакций за день</p>
            <p className="text-3xl font-bold">1,248</p>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-error)]">-1.3%</span>
              <span className="text-[var(--jiva-text-secondary)]">от вчера</span>
            </div>
          </div>
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <p className="text-[var(--jiva-text-secondary)] text-sm mb-2">Средний чек</p>
            <p className="text-3xl font-bold">₽ 4,320.00</p>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-success)]">+0.8%</span>
              <span className="text-[var(--jiva-text-secondary)]">за неделю</span>
            </div>
          </div>
        </div>
        
        {/* График */}
        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Динамика транзакций</h2>
            <div className="flex gap-2">
              <button className="px-3 py-1 border border-[var(--jiva-border)] rounded-md text-sm bg-[var(--jiva-primary)] text-white">День</button>
              <button className="px-3 py-1 border border-[var(--jiva-border)] rounded-md text-sm">Неделя</button>
              <button className="px-3 py-1 border border-[var(--jiva-border)] rounded-md text-sm">Месяц</button>
            </div>
          </div>
          <div className="h-80 w-full bg-gray-100 flex items-center justify-center">
            Здесь будет график финансовых показателей
          </div>
        </div>
        
        {/* Фильтры транзакций */}
        <div className="flex flex-wrap gap-4 mb-6 p-4 bg-[var(--jiva-background-paper)] rounded-lg">
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="dateRange" className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Период
            </label>
            <select 
              id="dateRange" 
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md"
            >
              <option value="today">Сегодня</option>
              <option value="yesterday">Вчера</option>
              <option value="week">Неделя</option>
              <option value="month">Месяц</option>
              <option value="custom">Выбрать период</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="status" className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Статус
            </label>
            <select 
              id="status" 
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md"
            >
              <option value="">Все статусы</option>
              <option value="success">Успешно</option>
              <option value="pending">В процессе</option>
              <option value="failed">Ошибка</option>
              <option value="refund">Возврат</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="search" className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Поиск
            </label>
            <input 
              type="text" 
              id="search" 
              placeholder="ID транзакции или магазин" 
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md"
            />
          </div>
        </div>
        
        {/* Таблица транзакций */}
        <div className="bg-[var(--jiva-background-paper)] rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-[var(--jiva-border)]">
                  <th className="px-4 py-3">ID транзакции</th>
                  <th className="px-4 py-3">Дата и время</th>
                  <th className="px-4 py-3">Магазин</th>
                  <th className="px-4 py-3">Сумма</th>
                  <th className="px-4 py-3">Комиссия</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3">Действия</th>
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3, 4, 5].map((index) => (
                  <tr key={index} className="border-b border-[var(--jiva-border)] hover:bg-[var(--jiva-background)]">
                    <td className="px-4 py-3">TRX-{10000 + index}</td>
                    <td className="px-4 py-3">2023-06-{15 - index} {10 + index}:30:00</td>
                    <td className="px-4 py-3">Магазин {index}</td>
                    <td className="px-4 py-3">₽ {(1000 * index + 500).toFixed(2)}</td>
                    <td className="px-4 py-3">₽ {((1000 * index + 500) * 0.02).toFixed(2)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        index % 4 === 0 
                          ? 'bg-green-100 text-green-800'
                          : index % 4 === 1
                            ? 'bg-yellow-100 text-yellow-800'
                            : index % 4 === 2
                              ? 'bg-red-100 text-red-800'
                              : 'bg-blue-100 text-blue-800'
                      }`}>
                        {index % 4 === 0 ? 'Успешно' : index % 4 === 1 ? 'В процессе' : index % 4 === 2 ? 'Ошибка' : 'Возврат'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button className="text-[var(--jiva-primary)] hover:text-[var(--jiva-primary-dark)]">
                        Подробнее
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Пагинация */}
          <div className="px-4 py-3 flex items-center justify-between">
            <div>
              <p className="text-sm text-[var(--jiva-text-secondary)]">
                Показано 1-5 из 243 транзакций
              </p>
            </div>
            <div className="flex gap-1">
              <button className="px-3 py-1 border border-[var(--jiva-border)] rounded-md disabled:opacity-50">
                Назад
              </button>
              <button className="px-3 py-1 bg-[var(--jiva-primary)] text-white rounded-md">
                1
              </button>
              <button className="px-3 py-1 border border-[var(--jiva-border)] rounded-md">
                2
              </button>
              <button className="px-3 py-1 border border-[var(--jiva-border)] rounded-md">
                3
              </button>
              <button className="px-3 py-1 border border-[var(--jiva-border)] rounded-md">
                Далее
              </button>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
} 