'use client';

import { useState } from 'react';
import MainLayout from '@/layouts/MainLayout';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('general');
  
  return (
    <MainLayout>
      <div className="max-w-full">
        <h1 className="text-3xl font-bold mb-6">Настройки</h1>
        
        {/* Табы */}
        <div className="mb-6 border-b border-[var(--jiva-border)]">
          <div className="flex flex-wrap -mb-px">
            {[
              { id: 'general', name: 'Общие' },
              { id: 'security', name: 'Безопасность' },
              { id: 'notifications', name: 'Уведомления' },
              { id: 'api', name: 'API' },
              { id: 'logs', name: 'Логи' }
            ].map((tab) => (
              <button
                key={tab.id}
                className={`py-3 px-4 text-sm font-medium border-b-2 mr-2 ${
                  activeTab === tab.id
                    ? 'border-[var(--jiva-primary)] text-[var(--jiva-primary)]'
                    : 'border-transparent text-[var(--jiva-text-secondary)] hover:text-[var(--jiva-text)] hover:border-[var(--jiva-border)]'
                }`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.name}
              </button>
            ))}
          </div>
        </div>
        
        {/* Контент таба */}
        {activeTab === 'general' && (
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Общие настройки</h2>
            
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2">
                  <label htmlFor="companyName" className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                    Название компании
                  </label>
                  <input 
                    type="text" 
                    id="companyName" 
                    className="w-full p-2 border border-[var(--jiva-border)] rounded-md" 
                    defaultValue="JivaPay"
                  />
                  <p className="text-sm text-[var(--jiva-text-secondary)] mt-1">
                    Отображается на странице входа и в документации.
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2">
                  <label htmlFor="supportEmail" className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                    Email поддержки
                  </label>
                  <input 
                    type="email" 
                    id="supportEmail" 
                    className="w-full p-2 border border-[var(--jiva-border)] rounded-md" 
                    defaultValue="support@jivapay.com"
                  />
                  <p className="text-sm text-[var(--jiva-text-secondary)] mt-1">
                    Будет показан пользователям для обращений в поддержку.
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                    Часовой пояс
                  </label>
                  <select className="w-full p-2 border border-[var(--jiva-border)] rounded-md">
                    <option value="UTC+0">UTC+0 - Гринвич</option>
                    <option value="UTC+3" selected>UTC+3 - Москва</option>
                    <option value="UTC+4">UTC+4 - Самара</option>
                    <option value="UTC+7">UTC+7 - Новосибирск</option>
                  </select>
                  <p className="text-sm text-[var(--jiva-text-secondary)] mt-1">
                    Применяется для отображения времени во всей системе.
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2">
                  <label className="flex items-center">
                    <input type="checkbox" className="h-4 w-4 text-[var(--jiva-primary)]" defaultChecked />
                    <span className="ml-2 text-sm text-[var(--jiva-text)]">
                      Разрешить регистрацию новых мерчантов
                    </span>
                  </label>
                  <p className="text-sm text-[var(--jiva-text-secondary)] mt-1 ml-6">
                    Если отключено, регистрация новых мерчантов будет недоступна.
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2">
                  <label className="flex items-center">
                    <input type="checkbox" className="h-4 w-4 text-[var(--jiva-primary)]" defaultChecked />
                    <span className="ml-2 text-sm text-[var(--jiva-text)]">
                      Режим обслуживания
                    </span>
                  </label>
                  <p className="text-sm text-[var(--jiva-text-secondary)] mt-1 ml-6">
                    При включении только администраторы смогут входить в систему.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="mt-8 flex justify-end">
              <button className="px-4 py-2 bg-[var(--jiva-primary)] text-white rounded-md hover:bg-[var(--jiva-primary-dark)] transition-colors">
                Сохранить настройки
              </button>
            </div>
          </div>
        )}
        
        {activeTab === 'security' && (
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Настройки безопасности</h2>
            
            <div className="space-y-6">
              <div className="border-b border-[var(--jiva-border)] pb-4">
                <h3 className="text-lg font-medium mb-2">Двухфакторная аутентификация</h3>
                <p className="text-sm text-[var(--jiva-text-secondary)] mb-4">
                  Настройте требования к двухфакторной аутентификации для пользователей.
                </p>
                
                <div className="space-y-3 ml-2">
                  <label className="flex items-center">
                    <input type="radio" name="2fa" className="h-4 w-4 text-[var(--jiva-primary)]" defaultChecked />
                    <span className="ml-2 text-sm text-[var(--jiva-text)]">
                      Опционально для всех пользователей
                    </span>
                  </label>
                  
                  <label className="flex items-center">
                    <input type="radio" name="2fa" className="h-4 w-4 text-[var(--jiva-primary)]" />
                    <span className="ml-2 text-sm text-[var(--jiva-text)]">
                      Обязательно только для администраторов
                    </span>
                  </label>
                  
                  <label className="flex items-center">
                    <input type="radio" name="2fa" className="h-4 w-4 text-[var(--jiva-primary)]" />
                    <span className="ml-2 text-sm text-[var(--jiva-text)]">
                      Обязательно для всех пользователей
                    </span>
                  </label>
                </div>
              </div>
              
              <div className="border-b border-[var(--jiva-border)] pb-4">
                <h3 className="text-lg font-medium mb-2">Политика паролей</h3>
                <p className="text-sm text-[var(--jiva-text-secondary)] mb-4">
                  Настройте требования к сложности паролей.
                </p>
                
                <div className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="minLength" className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                        Минимальная длина
                      </label>
                      <input 
                        type="number" 
                        id="minLength" 
                        className="w-full p-2 border border-[var(--jiva-border)] rounded-md" 
                        defaultValue="8"
                      />
                    </div>
                    
                    <div>
                      <label htmlFor="expiration" className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                        Срок действия (дней)
                      </label>
                      <input 
                        type="number" 
                        id="expiration" 
                        className="w-full p-2 border border-[var(--jiva-border)] rounded-md" 
                        defaultValue="90"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input type="checkbox" className="h-4 w-4 text-[var(--jiva-primary)]" defaultChecked />
                      <span className="ml-2 text-sm text-[var(--jiva-text)]">
                        Требовать заглавные и строчные буквы
                      </span>
                    </label>
                    
                    <label className="flex items-center">
                      <input type="checkbox" className="h-4 w-4 text-[var(--jiva-primary)]" defaultChecked />
                      <span className="ml-2 text-sm text-[var(--jiva-text)]">
                        Требовать цифры
                      </span>
                    </label>
                    
                    <label className="flex items-center">
                      <input type="checkbox" className="h-4 w-4 text-[var(--jiva-primary)]" defaultChecked />
                      <span className="ml-2 text-sm text-[var(--jiva-text)]">
                        Требовать специальные символы
                      </span>
                    </label>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2">Ограничение сессии</h3>
                <p className="text-sm text-[var(--jiva-text-secondary)] mb-4">
                  Настройте параметры сессии пользователей.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="sessionTimeout" className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                      Время автоматического выхода (минуты)
                    </label>
                    <input 
                      type="number" 
                      id="sessionTimeout" 
                      className="w-full p-2 border border-[var(--jiva-border)] rounded-md" 
                      defaultValue="30"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="maxSessions" className="block text-sm font-medium text-[var(--jiva-text)] mb-1">
                      Максимальное число одновременных сессий
                    </label>
                    <input 
                      type="number" 
                      id="maxSessions" 
                      className="w-full p-2 border border-[var(--jiva-border)] rounded-md" 
                      defaultValue="3"
                    />
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-8 flex justify-end">
              <button className="px-4 py-2 bg-[var(--jiva-primary)] text-white rounded-md hover:bg-[var(--jiva-primary-dark)] transition-colors">
                Сохранить настройки
              </button>
            </div>
          </div>
        )}
        
        {/* Остальные табы с заглушками */}
        {activeTab !== 'general' && activeTab !== 'security' && (
          <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 h-96 flex items-center justify-center">
            <p className="text-[var(--jiva-text-secondary)]">Содержимое для вкладки «{
              activeTab === 'notifications' ? 'Уведомления' : 
              activeTab === 'api' ? 'API' : 
              'Логи'
            }» находится в разработке</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
} 