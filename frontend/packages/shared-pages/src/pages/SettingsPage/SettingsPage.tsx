'use client';

import React, { useState } from 'react';
import { usePermissions } from '@jivapay/permissions';
import { TabGroup } from '@jivapay/ui-kit';
import { DASHBOARD_CONFIGS, UserRole } from '../../configs/roleConfigs';

interface SettingsPageProps {
  isLoading?: boolean;
}

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
  sessionMaxDuration: number;
  maxLoginAttempts: number;
  ipWhitelistEnabled: boolean;
  auditLogRetention: number;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  isLoading = false
}) => {
  const { userRole } = usePermissions();
  const role = userRole as UserRole;
  
  // Получаем конфигурацию для текущей роли
  const dashboardConfig = DASHBOARD_CONFIGS[role];

  // Только админы имеют доступ к настройкам
  if (role !== 'admin') {
    return (
      <div className="p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-[var(--jiva-text)]">Доступ запрещен</h1>
          <p className="text-[var(--jiva-text-secondary)] mt-2">У вас нет прав для управления настройками системы</p>
        </div>
      </div>
    );
  }

  // Mock данные настроек
  const [systemSettings, setSystemSettings] = useState<SystemSettings>({
    maintenance: false,
    registrationEnabled: true,
    maxTransactionLimit: 1000000,
    minTransactionAmount: 100,
    defaultCommission: 2.5,
    sessionTimeout: 30,
    apiRateLimit: 1000,
    notificationsEnabled: true
  });

  const [securitySettings, setSecuritySettings] = useState<SecuritySettings>({
    twoFactorRequired: true,
    passwordMinLength: 8,
    sessionMaxDuration: 24,
    maxLoginAttempts: 5,
    ipWhitelistEnabled: false,
    auditLogRetention: 90
  });

  const handleSystemSettingChange = (key: keyof SystemSettings, value: any) => {
    setSystemSettings(prev => ({ ...prev, [key]: value }));
    console.log(`Изменение системной настройки: ${key} = ${value}`);
  };

  const handleSecuritySettingChange = (key: keyof SecuritySettings, value: any) => {
    setSecuritySettings(prev => ({ ...prev, [key]: value }));
    console.log(`Изменение настройки безопасности: ${key} = ${value}`);
  };

  const handleSaveSettings = () => {
    console.log('Сохранение настроек', { systemSettings, securitySettings });
    // Здесь будет вызов API
  };

  // Контент вкладки "Система"
  const getSystemContent = () => (
    <div className="space-y-6">
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Основные настройки
        </h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <span className="font-medium text-[var(--jiva-text)]">Режим обслуживания</span>
              <div className="text-sm text-[var(--jiva-text-secondary)]">
                Временно отключить доступ к платформе
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={systemSettings.maintenance}
                onChange={(e) => handleSystemSettingChange('maintenance', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[var(--jiva-primary)]"></div>
            </label>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <span className="font-medium text-[var(--jiva-text)]">Регистрация новых пользователей</span>
              <div className="text-sm text-[var(--jiva-text-secondary)]">
                Разрешить создание новых аккаунтов
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={systemSettings.registrationEnabled}
                onChange={(e) => handleSystemSettingChange('registrationEnabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[var(--jiva-primary)]"></div>
            </label>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <span className="font-medium text-[var(--jiva-text)]">Уведомления</span>
              <div className="text-sm text-[var(--jiva-text-secondary)]">
                Email и push уведомления
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={systemSettings.notificationsEnabled}
                onChange={(e) => handleSystemSettingChange('notificationsEnabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[var(--jiva-primary)]"></div>
            </label>
          </div>
        </div>
      </div>

      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Лимиты транзакций
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-[var(--jiva-text)] mb-2">
              Максимальная сумма транзакции (₽)
            </label>
            <input
              type="number"
              value={systemSettings.maxTransactionLimit}
              onChange={(e) => handleSystemSettingChange('maxTransactionLimit', parseInt(e.target.value))}
              className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-[var(--jiva-text)] mb-2">
              Минимальная сумма транзакции (₽)
            </label>
            <input
              type="number"
              value={systemSettings.minTransactionAmount}
              onChange={(e) => handleSystemSettingChange('minTransactionAmount', parseInt(e.target.value))}
              className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-[var(--jiva-text)] mb-2">
              Комиссия по умолчанию (%)
            </label>
            <input
              type="number"
              step="0.1"
              value={systemSettings.defaultCommission}
              onChange={(e) => handleSystemSettingChange('defaultCommission', parseFloat(e.target.value))}
              className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-[var(--jiva-text)] mb-2">
              Лимит API запросов/мин
            </label>
            <input
              type="number"
              value={systemSettings.apiRateLimit}
              onChange={(e) => handleSystemSettingChange('apiRateLimit', parseInt(e.target.value))}
              className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
            />
          </div>
        </div>
      </div>
    </div>
  );

  // Контент вкладки "Безопасность"
  const getSecurityContent = () => (
    <div className="space-y-6">
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Аутентификация
        </h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <span className="font-medium text-[var(--jiva-text)]">Обязательная двухфакторная аутентификация</span>
              <div className="text-sm text-[var(--jiva-text-secondary)]">
                Требовать 2FA для всех пользователей
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={securitySettings.twoFactorRequired}
                onChange={(e) => handleSecuritySettingChange('twoFactorRequired', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[var(--jiva-primary)]"></div>
            </label>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <span className="font-medium text-[var(--jiva-text)]">Белый список IP адресов</span>
              <div className="text-sm text-[var(--jiva-text-secondary)]">
                Ограничить доступ только разрешенными IP
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={securitySettings.ipWhitelistEnabled}
                onChange={(e) => handleSecuritySettingChange('ipWhitelistEnabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[var(--jiva-primary)]"></div>
            </label>
          </div>
        </div>
      </div>

      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Политики безопасности
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-[var(--jiva-text)] mb-2">
              Минимальная длина пароля
            </label>
            <input
              type="number"
              value={securitySettings.passwordMinLength}
              onChange={(e) => handleSecuritySettingChange('passwordMinLength', parseInt(e.target.value))}
              className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-[var(--jiva-text)] mb-2">
              Максимальная длительность сессии (часы)
            </label>
            <input
              type="number"
              value={securitySettings.sessionMaxDuration}
              onChange={(e) => handleSecuritySettingChange('sessionMaxDuration', parseInt(e.target.value))}
              className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-[var(--jiva-text)] mb-2">
              Максимальное количество попыток входа
            </label>
            <input
              type="number"
              value={securitySettings.maxLoginAttempts}
              onChange={(e) => handleSecuritySettingChange('maxLoginAttempts', parseInt(e.target.value))}
              className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-[var(--jiva-text)] mb-2">
              Хранение аудит логов (дни)
            </label>
            <input
              type="number"
              value={securitySettings.auditLogRetention}
              onChange={(e) => handleSecuritySettingChange('auditLogRetention', parseInt(e.target.value))}
              className="w-full border border-[var(--jiva-border-light)] rounded-lg px-3 py-2 text-[var(--jiva-text)] bg-[var(--jiva-background)]"
            />
          </div>
        </div>
      </div>
    </div>
  );

  // Контент вкладки "Интеграции"
  const getIntegrationsContent = () => (
    <div className="space-y-6">
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Платежные системы
        </h3>
        <div className="space-y-4">
          {[
            { name: 'Сбербанк', status: 'active', updated: '2024-12-27' },
            { name: 'Тинькофф', status: 'active', updated: '2024-12-26' },
            { name: 'ВТБ', status: 'inactive', updated: '2024-12-20' },
            { name: 'Альфа-Банк', status: 'active', updated: '2024-12-27' },
          ].map((system, index) => (
            <div key={index} className="flex justify-between items-center p-4 bg-[var(--jiva-background)] rounded-lg">
              <div>
                <div className="font-medium text-[var(--jiva-text)]">{system.name}</div>
                <div className="text-sm text-[var(--jiva-text-secondary)]">
                  Обновлено: {system.updated}
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  system.status === 'active' 
                    ? 'bg-[var(--jiva-success-light)] text-[var(--jiva-success)]'
                    : 'bg-[var(--jiva-error-light)] text-[var(--jiva-error)]'
                }`}>
                  {system.status === 'active' ? 'Активна' : 'Отключена'}
                </span>
                <button className="text-[var(--jiva-primary)] hover:underline text-sm">
                  Настроить
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">
          Внешние сервисы
        </h3>
        <div className="space-y-4">
          {[
            { name: 'Email сервис (SMTP)', status: 'active', description: 'Отправка уведомлений' },
            { name: 'SMS сервис', status: 'active', description: 'Двухфакторная аутентификация' },
            { name: 'Курсы валют API', status: 'active', description: 'Обновление курсов' },
            { name: 'Аудит логирование', status: 'active', description: 'Системные логи' },
          ].map((service, index) => (
            <div key={index} className="flex justify-between items-center p-4 bg-[var(--jiva-background)] rounded-lg">
              <div>
                <div className="font-medium text-[var(--jiva-text)]">{service.name}</div>
                <div className="text-sm text-[var(--jiva-text-secondary)]">
                  {service.description}
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  service.status === 'active' 
                    ? 'bg-[var(--jiva-success-light)] text-[var(--jiva-success)]'
                    : 'bg-[var(--jiva-error-light)] text-[var(--jiva-error)]'
                }`}>
                  {service.status === 'active' ? 'Работает' : 'Отключен'}
                </span>
                <button className="text-[var(--jiva-primary)] hover:underline text-sm">
                  Проверить
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Создание вкладок
  const getTabs = () => [
    { key: 'system', label: 'Система', content: getSystemContent() },
    { key: 'security', label: 'Безопасность', content: getSecurityContent() },
    { key: 'integrations', label: 'Интеграции', content: getIntegrationsContent() }
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <div className="text-[var(--jiva-text-secondary)]">Загрузка настроек...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Заголовок страницы */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-[var(--jiva-text)]">
            Настройки системы
          </h1>
          <p className="text-[var(--jiva-text-secondary)] mt-1">
            Управление конфигурацией платформы JivaPay
          </p>
        </div>

        <button 
          onClick={handleSaveSettings}
          className="bg-[var(--jiva-primary)] text-white px-6 py-2 rounded-lg hover:opacity-90 font-medium"
        >
          Сохранить изменения
        </button>
      </div>

      {/* Предупреждение */}
      <div className="bg-[var(--jiva-warning-light)] border border-[var(--jiva-warning)] rounded-lg p-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-[var(--jiva-warning)] rounded-full"></div>
          <span className="font-medium text-[var(--jiva-text)]">
            Внимание: Изменения в настройках системы влияют на всех пользователей платформы
          </span>
        </div>
      </div>

      {/* Вкладки с настройками */}
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-6">
        <TabGroup
          tabs={getTabs()}
          defaultTab="system"
        />
      </div>
    </div>
  );
}; 