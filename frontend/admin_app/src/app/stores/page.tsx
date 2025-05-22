'use client';

import MainLayout from '@/layouts/MainLayout';

export default function StoresPage() {
  return (
    <MainLayout>
      <div className="max-w-full">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Магазины</h1>
          
          <button className="px-4 py-2 bg-[var(--jiva-primary)] text-white rounded-md hover:bg-[var(--jiva-primary-dark)] transition-colors">
            Добавить магазин
          </button>
        </div>
        
        {/* Фильтры */}
        <div className="flex flex-wrap gap-4 mb-6 p-4 bg-[var(--jiva-background-paper)] rounded-lg">
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="status" className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Статус
            </label>
            <select 
              id="status" 
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md"
            >
              <option value="">Все статусы</option>
              <option value="active">Активен</option>
              <option value="suspended">Приостановлен</option>
              <option value="pending">На модерации</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="merchant" className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Мерчант
            </label>
            <select 
              id="merchant" 
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md"
            >
              <option value="">Все мерчанты</option>
              <option value="1">BETBOOM</option>
              <option value="2">1XBET</option>
              <option value="3">BETCITY</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="search" className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Поиск
            </label>
            <input 
              type="text" 
              id="search" 
              placeholder="Название или ID" 
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md"
            />
          </div>
        </div>
        
        {/* Список магазинов */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((index) => (
            <div key={index} className="bg-[var(--jiva-background-paper)] rounded-lg overflow-hidden shadow-sm">
              <div className="h-40 bg-gradient-to-r from-blue-400 to-indigo-600 flex items-center justify-center">
                <span className="text-white text-2xl font-bold">Магазин {index}</span>
              </div>
              
              <div className="p-4">
                <h3 className="text-lg font-semibold mb-2">Магазин {index}</h3>
                <p className="text-sm text-[var(--jiva-text-secondary)] mb-4">ID: STORE-{1000 + index}</p>
                
                <div className="flex justify-between items-center mb-3">
                  <span className="text-sm font-medium">Мерчант:</span>
                  <span className="text-sm">{['BETBOOM', '1XBET', 'BETCITY'][index % 3]}</span>
                </div>
                
                <div className="flex justify-between items-center mb-3">
                  <span className="text-sm font-medium">Баланс:</span>
                  <span className="text-sm">₽ {(Math.random() * 10000).toFixed(2)}</span>
                </div>
                
                <div className="flex justify-between items-center mb-3">
                  <span className="text-sm font-medium">Статус:</span>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    index % 3 === 0 
                      ? 'bg-green-100 text-green-800'
                      : index % 3 === 1
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                  }`}>
                    {index % 3 === 0 ? 'Активен' : index % 3 === 1 ? 'На модерации' : 'Приостановлен'}
                  </span>
                </div>
                
                <div className="flex justify-between items-center mt-4 pt-3 border-t border-[var(--jiva-border)]">
                  <button className="text-[var(--jiva-primary)] hover:text-[var(--jiva-primary-dark)]">
                    Подробнее
                  </button>
                  
                  <button className="text-[var(--jiva-error)] hover:text-[var(--jiva-error-dark)]">
                    {index % 3 === 0 ? 'Приостановить' : 'Активировать'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {/* Пагинация */}
        <div className="mt-6 flex items-center justify-center gap-1">
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
    </MainLayout>
  );
}
 