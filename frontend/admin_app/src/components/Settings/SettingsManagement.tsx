import React from 'react';
import { TabGroup } from '../ui/TabGroup';
import { StatusBadge } from '../ui/StatusBadge';

interface SystemSettings {
  maintenance: boolean;
  registrationEnabled: boolean;
  maxTransactionLimit: number;
  minTransactionAmount: number;
  defaultCommission: number;
  sessionTimeout: number;
  apiRateLimit: number;
  notificationsEnabled: boolean;
}

interface SecuritySettings {
  twoFactorRequired: boolean;
  passwordMinLength: number;
  sessionExpiry: number;
  maxLoginAttempts: number;
  ipWhitelistEnabled: boolean;
  auditLogRetention: number;
}

interface SettingsManagementProps {
  systemSettings: SystemSettings;
  securitySettings: SecuritySettings;
  loading?: boolean;
}

export const SettingsManagement: React.FC<SettingsManagementProps> = ({ 
  systemSettings, 
  securitySettings, 
  loading 
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  // Системные настройки
  const SystemSettingsTab = () => (
    <div className="space-y-6">
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-bold mb-4">Общие настройки</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Режим обслуживания</label>
              <p className="text-xs text-[var(--jiva-text-secondary)]">Временно отключить платформу для обслуживания</p>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status={systemSettings.maintenance ? 'pending' : 'success'}>
                {systemSettings.maintenance ? 'Включен' : 'Отключен'}
              </StatusBadge>
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Регистрация новых пользователей</label>
              <p className="text-xs text-[var(--jiva-text-secondary)]">Разрешить регистрацию новых аккаунтов</p>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status={systemSettings.registrationEnabled ? 'success' : 'failed'}>
                {systemSettings.registrationEnabled ? 'Разрешена' : 'Запрещена'}
              </StatusBadge>
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Уведомления</label>
              <p className="text-xs text-[var(--jiva-text-secondary)]">Email и SMS уведомления</p>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status={systemSettings.notificationsEnabled ? 'success' : 'failed'}>
                {systemSettings.notificationsEnabled ? 'Включены' : 'Отключены'}
              </StatusBadge>
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-bold mb-4">Лимиты транзакций</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Максимальный лимит транзакции</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={systemSettings.maxTransactionLimit}
                className="flex-1 p-2 border border-[var(--jiva-border)] rounded text-sm"
                readOnly
              />
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
            <p className="text-xs text-[var(--jiva-text-secondary)] mt-1">
              Текущий: {formatCurrency(systemSettings.maxTransactionLimit)}
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Минимальная сумма транзакции</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={systemSettings.minTransactionAmount}
                className="flex-1 p-2 border border-[var(--jiva-border)] rounded text-sm"
                readOnly
              />
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
            <p className="text-xs text-[var(--jiva-text-secondary)] mt-1">
              Текущий: {formatCurrency(systemSettings.minTransactionAmount)}
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Комиссия по умолчанию (%)</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={systemSettings.defaultCommission}
                step="0.1"
                className="flex-1 p-2 border border-[var(--jiva-border)] rounded text-sm"
                readOnly
              />
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Лимит API запросов в минуту</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={systemSettings.apiRateLimit}
                className="flex-1 p-2 border border-[var(--jiva-border)] rounded text-sm"
                readOnly
              />
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Настройки безопасности
  const SecuritySettingsTab = () => (
    <div className="space-y-6">
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-bold mb-4">Аутентификация</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Двухфакторная аутентификация</label>
              <p className="text-xs text-[var(--jiva-text-secondary)]">Обязательная 2FA для всех пользователей</p>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status={securitySettings.twoFactorRequired ? 'success' : 'pending'}>
                {securitySettings.twoFactorRequired ? 'Обязательна' : 'Опционально'}
              </StatusBadge>
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Whitelist IP адресов</label>
              <p className="text-xs text-[var(--jiva-text-secondary)]">Ограничить доступ к определенным IP</p>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status={securitySettings.ipWhitelistEnabled ? 'success' : 'failed'}>
                {securitySettings.ipWhitelistEnabled ? 'Включен' : 'Отключен'}
              </StatusBadge>
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Настроить
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-bold mb-4">Параметры безопасности</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Минимальная длина пароля</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={securitySettings.passwordMinLength}
                className="flex-1 p-2 border border-[var(--jiva-border)] rounded text-sm"
                readOnly
              />
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Время сессии (минуты)</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={securitySettings.sessionExpiry}
                className="flex-1 p-2 border border-[var(--jiva-border)] rounded text-sm"
                readOnly
              />
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Максимум попыток входа</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={securitySettings.maxLoginAttempts}
                className="flex-1 p-2 border border-[var(--jiva-border)] rounded text-sm"
                readOnly
              />
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Хранение логов аудита (дни)</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={securitySettings.auditLogRetention}
                className="flex-1 p-2 border border-[var(--jiva-border)] rounded text-sm"
                readOnly
              />
              <button className="px-3 py-1 text-xs border border-[var(--jiva-border)] rounded">
                Изменить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Системная информация
  const SystemInfoTab = () => (
    <div className="space-y-6">
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-bold mb-4">Информация о системе</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Версия платформы:</span>
              <span className="text-sm">v2.1.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium">Последнее обновление:</span>
              <span className="text-sm">15.06.2023</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium">Статус сервера:</span>
              <StatusBadge status="success">Работает</StatusBadge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium">База данных:</span>
              <StatusBadge status="success">Подключена</StatusBadge>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Активных пользователей:</span>
              <span className="text-sm">1,247</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium">Загрузка CPU:</span>
              <span className="text-sm">23%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium">Использование памяти:</span>
              <span className="text-sm">45%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm font-medium">Свободное место:</span>
              <span className="text-sm">2.1 TB</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-bold mb-4">Журнал системных событий</h3>
        
        <div className="space-y-2">
          {[
            { time: '15:30:45', event: 'Резервное копирование завершено', status: 'success' },
            { time: '14:22:10', event: 'Обновление конфигурации API', status: 'success' },
            { time: '13:45:33', event: 'Превышен лимит попыток входа для IP 192.168.1.100', status: 'failed' },
            { time: '12:15:22', event: 'Начато плановое обслуживание', status: 'pending' },
            { time: '11:30:15', event: 'Подключение нового мерчанта', status: 'success' }
          ].map((log, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-[var(--jiva-background)] rounded">
              <div className="flex items-center gap-3">
                <span className="text-xs text-[var(--jiva-text-secondary)] font-mono">{log.time}</span>
                <span className="text-sm">{log.event}</span>
              </div>
              <StatusBadge status={log.status as 'success' | 'failed' | 'pending'} />
            </div>
          ))}
        </div>
        
        <div className="mt-4 text-center">
          <button className="px-4 py-2 text-sm border border-[var(--jiva-border)] rounded hover:bg-[var(--jiva-background)]">
            Показать все события
          </button>
        </div>
      </div>
    </div>
  );

  const tabs = [
    {
      key: 'system',
      label: 'Система',
      content: <SystemSettingsTab />
    },
    {
      key: 'security',
      label: 'Безопасность',
      content: <SecuritySettingsTab />
    },
    {
      key: 'info',
      label: 'Информация',
      content: <SystemInfoTab />
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--jiva-primary)]"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Настройки</h1>
        <p className="text-[var(--jiva-text-secondary)] mt-1">
          Управление системными настройками и конфигурацией
        </p>
      </div>

      <TabGroup tabs={tabs} defaultTab="system" />
    </div>
  );
}; 