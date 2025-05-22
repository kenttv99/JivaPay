'use client';

import MainLayout from '@/layouts/MainLayout';

export default function ChartsPage() {
  return (
    <MainLayout>
      <div className="max-w-full">
        <h1 className="text-3xl font-bold mb-6">Аналитика</h1>
        
        {/* Фильтры */}
        <div className="flex flex-wrap gap-4 mb-6 p-4 bg-[var(--jiva-background-paper)] rounded-lg">
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="dateRange" className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Период
            </label>
            <select 
              id="dateRange" 
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md"
            >
              <option value="week">Неделя</option>
              <option value="month" selected>Месяц</option>
              <option value="quarter">Квартал</option>
              <option value="year">Год</option>
              <option value="custom">Выбрать период</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="merchants" className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Мерчант
            </label>
            <select 
              id="merchants" 
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md"
            >
              <option value="">Все мерчанты</option>
              <option value="1">ООО "Первый"</option>
              <option value="2">ИП Петров</option>
              <option value="3">ООО "Технологии"</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="metrics" className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Метрики
            </label>
            <select 
              id="metrics" 
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md"
            >
              <option value="transactions">Транзакции</option>
              <option value="volume" selected>Объем продаж</option>
              <option value="commission">Комиссии</option>
            </select>
          </div>
        </div>
        
        {/* Основной график */}
        <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Объем продаж по дням</h2>
          <div className="h-96 w-full bg-gray-100 rounded flex items-center justify-center">
            Здесь будет основной график
          </div>
        </div>
        
        {/* Карточки с ключевыми метриками */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <p className="text-[var(--jiva-text-secondary)] text-sm mb-2">Общий объем продаж</p>
            <p className="text-3xl font-bold">₽ 12,458,320</p>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-success)]">+12.5%</span>
              <span className="text-[var(--jiva-text-secondary)]">к прошлому месяцу</span>
            </div>
          </div>
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <p className="text-[var(--jiva-text-secondary)] text-sm mb-2">Кол-во транзакций</p>
            <p className="text-3xl font-bold">32,451</p>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-success)]">+8.3%</span>
              <span className="text-[var(--jiva-text-secondary)]">к прошлому месяцу</span>
            </div>
          </div>
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <p className="text-[var(--jiva-text-secondary)] text-sm mb-2">Средний чек</p>
            <p className="text-3xl font-bold">₽ 4,320</p>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-success)]">+3.8%</span>
              <span className="text-[var(--jiva-text-secondary)]">к прошлому месяцу</span>
            </div>
          </div>
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
            <p className="text-[var(--jiva-text-secondary)] text-sm mb-2">Доход с комиссий</p>
            <p className="text-3xl font-bold">₽ 249,166</p>
            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="text-[var(--jiva-success)]">+12.5%</span>
              <span className="text-[var(--jiva-text-secondary)]">к прошлому месяцу</span>
            </div>
          </div>
        </div>
        
        {/* Дополнительные графики - сетка из двух */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">Распределение по способам оплаты</h2>
            <div className="h-80 w-full bg-gray-100 rounded flex items-center justify-center">
              Здесь будет круговая диаграмма
            </div>
          </div>
          
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">Топ-5 мерчантов</h2>
            <div className="h-80 w-full bg-gray-100 rounded flex items-center justify-center">
              Здесь будет горизонтальная гистограмма
            </div>
          </div>
        </div>
        
        {/* Таблица с детальными данными */}
        <div className="bg-[var(--jiva-background-paper)] rounded-lg overflow-hidden">
          <div className="flex justify-between items-center p-6 border-b border-[var(--jiva-border)]">
            <h2 className="text-xl font-bold">Детальная статистика</h2>
            <button className="px-4 py-2 bg-[var(--jiva-primary)] text-white rounded-md hover:bg-[var(--jiva-primary-dark)] transition-colors">
              Экспорт в CSV
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-[var(--jiva-border)]">
                  <th className="px-4 py-3">Дата</th>
                  <th className="px-4 py-3">Объем продаж</th>
                  <th className="px-4 py-3">Транзакций</th>
                  <th className="px-4 py-3">Средний чек</th>
                  <th className="px-4 py-3">Комиссия</th>
                  <th className="px-4 py-3">Конверсия</th>
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3, 4, 5, 6, 7].map((index) => (
                  <tr key={index} className="border-b border-[var(--jiva-border)] hover:bg-[var(--jiva-background)]">
                    <td className="px-4 py-3">2023-06-{(15 - index).toString().padStart(2, '0')}</td>
                    <td className="px-4 py-3">₽ {(400000 + index * 10000 + Math.floor(Math.random() * 5000)).toLocaleString()}</td>
                    <td className="px-4 py-3">{(1000 + index * 50 + Math.floor(Math.random() * 30)).toLocaleString()}</td>
                    <td className="px-4 py-3">₽ {(3800 + Math.floor(Math.random() * 800)).toLocaleString()}</td>
                    <td className="px-4 py-3">₽ {(8000 + index * 200 + Math.floor(Math.random() * 300)).toLocaleString()}</td>
                    <td className="px-4 py-3">{(89 + Math.floor(Math.random() * 10))}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Пагинация */}
          <div className="px-4 py-3 flex items-center justify-between">
            <div>
              <p className="text-sm text-[var(--jiva-text-secondary)]">
                Показано 7 дней из 30
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