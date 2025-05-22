'use client';

import MainLayout from '@/layouts/MainLayout';

export default function UsersPage() {
  return (
    <MainLayout>
      <div className="max-w-full">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Пользователи</h1>
          
          <button className="px-4 py-2 bg-[var(--jiva-primary)] text-white rounded-md hover:bg-[var(--jiva-primary-dark)] transition-colors">
            Добавить пользователя
          </button>
        </div>
        
        {/* Фильтры */}
        <div className="flex flex-wrap gap-4 mb-6 p-4 bg-[var(--jiva-background-paper)] rounded-lg">
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="role" className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Роль
            </label>
            <select 
              id="role" 
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md"
            >
              <option value="">Все роли</option>
              <option value="admin">Администратор</option>
              <option value="merchant">Мерчант</option>
              <option value="trader">Трейдер</option>
              <option value="support">Саппорт</option>
              <option value="teamlead">Тимлид</option>
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
              <option value="active">Активен</option>
              <option value="blocked">Заблокирован</option>
              <option value="pending">Ожидает подтверждения</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="search" className="block text-sm font-medium text-[var(--jiva-text-secondary)] mb-1">
              Поиск
            </label>
            <input 
              type="text" 
              id="search" 
              placeholder="Email, имя или ID" 
              className="w-full p-2 border border-[var(--jiva-border)] rounded-md"
            />
          </div>
        </div>
        
        {/* Таблица пользователей */}
        <div className="bg-[var(--jiva-background-paper)] rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-[var(--jiva-background)] border-b border-[var(--jiva-border)]">
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Имя</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Роль</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3">Дата регистрации</th>
                  <th className="px-4 py-3">Действия</th>
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3, 4, 5].map((index) => (
                  <tr key={index} className="border-b border-[var(--jiva-border)] hover:bg-[var(--jiva-background)]">
                    <td className="px-4 py-3">USR-{1000 + index}</td>
                    <td className="px-4 py-3">Пользователь {index}</td>
                    <td className="px-4 py-3">user{index}@example.com</td>
                    <td className="px-4 py-3">
                      {['Администратор', 'Мерчант', 'Трейдер', 'Саппорт', 'Тимлид'][index % 5]}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        index % 3 === 0 
                          ? 'bg-green-100 text-green-800'
                          : index % 3 === 1
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {index % 3 === 0 ? 'Активен' : index % 3 === 1 ? 'Заблокирован' : 'Ожидает подтверждения'}
                      </span>
                    </td>
                    <td className="px-4 py-3">2023-06-{10 + index}</td>
                    <td className="px-4 py-3">
                      <button className="text-[var(--jiva-primary)] hover:text-[var(--jiva-primary-dark)] mr-2">
                        Редактировать
                      </button>
                      <button className="text-[var(--jiva-error)] hover:text-[var(--jiva-error-dark)]">
                        Заблокировать
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
                Показано 1-5 из 100 записей
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