import React from 'react';
import { TabGroup } from '@jivapay/ui-kit';

export const SettingsManagement: React.FC = () => {
  // Системные настройки
  const SystemSettingsTab = () => (
    <div className="space-y-6">
      <div className="bg-surface rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-primary mb-4">Системные настройки</h2>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-primary">Режим обслуживания</h3>
              <p className="text-xs text-secondary">Временно отключить платформу для обслуживания</p>
            </div>
            <div className="flex items-center space-x-2">
              <input type="checkbox" className="form-checkbox" />
              <button className="px-3 py-1 text-xs border border-border rounded">
                Включить
              </button>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-primary">Регистрация пользователей</h3>
              <p className="text-xs text-secondary">Разрешить регистрацию новых аккаунтов</p>
            </div>
            <div className="flex items-center space-x-2">
              <input type="checkbox" className="form-checkbox" defaultChecked />
              <button className="px-3 py-1 text-xs border border-border rounded">
                Отключить
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-surface rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-primary mb-4">Лимиты и ограничения</h2>
        
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-primary mb-2">
              Максимальная сумма ордера (₽)
            </label>
            <div className="flex space-x-2">
              <input 
                type="number" 
                defaultValue="100000"
                className="flex-1 p-2 border border-border rounded text-sm"
              />
              <button className="px-3 py-1 text-xs border border-border rounded">
                Сохранить
              </button>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-primary mb-2">
              Дневной лимит трейдера (₽)
            </label>
            <div className="flex space-x-2">
              <input 
                type="number" 
                defaultValue="500000"
                className="flex-1 p-2 border border-border rounded text-sm"
              />
              <button className="px-3 py-1 text-xs border border-border rounded">
                Сохранить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const SecuritySettingsTab = () => (
    <div className="space-y-6">
      <div className="bg-surface rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-bold mb-4">Настройки безопасности</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-primary">Двухфакторная аутентификация</label>
              <p className="text-xs text-secondary">Обязательная 2FA для всех пользователей</p>
            </div>
            <div className="flex items-center space-x-2">
              <input type="checkbox" className="form-checkbox" defaultChecked />
              <button className="px-3 py-1 text-xs border border-border rounded">
                Настроить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const tabs = [
    { key: 'system', label: 'Система', content: <SystemSettingsTab /> },
    { key: 'security', label: 'Безопасность', content: <SecuritySettingsTab /> }
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-primary">Настройки системы</h1>
      
      <div className="bg-surface rounded-lg p-6">
        <TabGroup tabs={tabs} defaultTab="system" />
      </div>
    </div>
  );
}; 