'use client';

import MainLayout from '@/layouts/MainLayout';
import { UserManagement } from '@/components/Users/UserManagement';

// Симуляция данных пользователей
const mockUsers = [
  // Администраторы
  { id: 'USR-1001', name: 'Сергей Иванов', email: 's.ivanov@jivapay.com', role: 'admin' as const, status: 'active' as const, lastActive: 'Сегодня, 12:40', registrationDate: '2023-01-15', permissions: ['*:*:*'] },
  { id: 'USR-1002', name: 'Елена Петрова', email: 'e.petrova@jivapay.com', role: 'admin' as const, status: 'active' as const, lastActive: 'Сегодня, 10:15', registrationDate: '2023-02-03', permissions: ['platform:*:*', 'users:*:*'] },
  { id: 'USR-1003', name: 'Дмитрий Сидоров', email: 'd.sidorov@jivapay.com', role: 'admin' as const, status: 'inactive' as const, lastActive: 'Вчера, 18:20', registrationDate: '2023-03-12', permissions: ['platform:read:*'] },
  
  // Мерчанты
  { id: 'USR-2001', name: 'Виктор Лебедев', email: 'v.lebedev@business.com', role: 'merchant' as const, status: 'active' as const, lastActive: 'Сегодня, 14:20', registrationDate: '2023-06-01', stores: 2 },
  { id: 'USR-2002', name: 'Анна Кузнецова', email: 'a.kuznetsova@shop.ru', role: 'merchant' as const, status: 'active' as const, lastActive: 'Вчера, 11:05', registrationDate: '2023-06-15', stores: 1 },
  { id: 'USR-2003', name: 'Михаил Орлов', email: 'm.orlov@store.net', role: 'merchant' as const, status: 'active' as const, lastActive: 'Сегодня, 10:30', registrationDate: '2023-05-20', stores: 3 },
  { id: 'USR-2004', name: 'Екатерина Белова', email: 'e.belova@market.com', role: 'merchant' as const, status: 'blocked' as const, lastActive: 'Неделю назад', registrationDate: '2023-04-10', stores: 1 },
  
  // Трейдеры
  { id: 'USR-3001', name: 'Виктория Зайцева', email: 'v.zaitseva@jivapay.com', role: 'trader' as const, status: 'active' as const, lastActive: 'Сегодня, 14:10', registrationDate: '2023-03-01', trafficEnabled: true, teamlead: 'Андрей Соколов' },
  { id: 'USR-3002', name: 'Артем Федоров', email: 'a.fedorov@jivapay.com', role: 'trader' as const, status: 'active' as const, lastActive: 'Сегодня, 13:45', registrationDate: '2023-03-05', trafficEnabled: true, teamlead: 'Андрей Соколов' },
  { id: 'USR-3003', name: 'Юлия Медведева', email: 'y.medvedeva@jivapay.com', role: 'trader' as const, status: 'active' as const, lastActive: 'Вчера, 17:30', registrationDate: '2023-04-01', trafficEnabled: false, teamlead: 'Ирина Новикова' },
  { id: 'USR-3004', name: 'Денис Васильев', email: 'd.vasiliev@jivapay.com', role: 'trader' as const, status: 'inactive' as const, lastActive: '4 дня назад', registrationDate: '2023-02-15', trafficEnabled: false, teamlead: 'Ирина Новикова' },
  
  // Саппорт
  { id: 'USR-4001', name: 'Ольга Смирнова', email: 'o.smirnova@jivapay.com', role: 'support' as const, status: 'active' as const, lastActive: 'Сегодня, 11:30', registrationDate: '2023-01-20', roleDescription: 'Старший специалист поддержки' },
  { id: 'USR-4002', name: 'Алексей Козлов', email: 'a.kozlov@jivapay.com', role: 'support' as const, status: 'active' as const, lastActive: 'Сегодня, 09:45', registrationDate: '2023-02-10', roleDescription: 'Специалист поддержки' },
  { id: 'USR-4003', name: 'Наталья Морозова', email: 'n.morozova@jivapay.com', role: 'support' as const, status: 'active' as const, lastActive: 'Вчера, 16:10', registrationDate: '2023-03-01', roleDescription: 'Специалист поддержки по работе с мерчантами' },
  { id: 'USR-4004', name: 'Максим Волков', email: 'm.volkov@jivapay.com', role: 'support' as const, status: 'pending' as const, lastActive: '3 дня назад', registrationDate: '2023-06-20', roleDescription: 'Стажер' },
  
  // Тимлиды
  { id: 'USR-5001', name: 'Андрей Соколов', email: 'a.sokolov@jivapay.com', role: 'teamlead' as const, status: 'active' as const, lastActive: 'Сегодня, 13:15', registrationDate: '2022-12-01', teamSize: 5 },
  { id: 'USR-5002', name: 'Ирина Новикова', email: 'i.novikova@jivapay.com', role: 'teamlead' as const, status: 'active' as const, lastActive: 'Сегодня, 12:00', registrationDate: '2022-11-15', teamSize: 3 },
  { id: 'USR-5003', name: 'Павел Ковалев', email: 'p.kovalev@jivapay.com', role: 'teamlead' as const, status: 'inactive' as const, lastActive: '2 дня назад', registrationDate: '2023-01-10', teamSize: 4 }
];

export default function UsersPage() {
  return (
    <MainLayout>
      <UserManagement users={mockUsers} loading={false} />
    </MainLayout>
  );
} 