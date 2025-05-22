'use client';

import MainLayout from '@/layouts/MainLayout';
import { StoreManagement } from '@/components/Stores/StoreManagement';

// Симуляция данных магазинов
const mockStoreStats = {
  totalStores: 156,
  activeStores: 142,
  monthlyVolume: 45820000,
  averageCommission: 2.8,
  storesChange: 8.5,
  activeChange: 5.2,
  volumeChange: 12.3,
  commissionChange: -0.2
};

const mockStores = [
  { id: 'STR-1001', name: 'TechShop Pro', merchantName: 'ООО "Технологии"', domain: 'techshop.ru', status: 'active' as const, monthlyVolume: 2500000, commission: 2.5, category: 'Электроника', createdDate: '2023-01-15', lastActivity: 'Сегодня, 14:30' },
  { id: 'STR-1002', name: 'Fashion Store', merchantName: 'ИП Петрова', domain: 'fashion-store.net', status: 'active' as const, monthlyVolume: 1800000, commission: 3.0, category: 'Мода', createdDate: '2023-02-20', lastActivity: 'Сегодня, 12:15' },
  { id: 'STR-1003', name: 'Book Paradise', merchantName: 'ООО "Знание"', domain: 'books.paradise.com', status: 'active' as const, monthlyVolume: 1200000, commission: 2.8, category: 'Книги', createdDate: '2023-03-10', lastActivity: 'Вчера, 18:45' },
  { id: 'STR-1004', name: 'Sport World', merchantName: 'ИП Спортов', domain: 'sportworld.shop', status: 'blocked' as const, monthlyVolume: 950000, commission: 3.2, category: 'Спорт', createdDate: '2023-01-05', lastActivity: 'Неделю назад' },
  { id: 'STR-1005', name: 'Home & Garden', merchantName: 'ООО "Дом"', domain: 'home-garden.store', status: 'active' as const, monthlyVolume: 1500000, commission: 2.7, category: 'Дом и сад', createdDate: '2023-04-01', lastActivity: 'Сегодня, 10:20' },
  { id: 'STR-1006', name: 'Beauty Shop', merchantName: 'ИП Красотина', domain: 'beauty.shop', status: 'active' as const, monthlyVolume: 800000, commission: 3.5, category: 'Красота', createdDate: '2023-05-15', lastActivity: 'Сегодня, 09:30' },
  { id: 'STR-1007', name: 'Auto Parts', merchantName: 'ООО "Авто"', domain: 'autoparts.pro', status: 'pending' as const, monthlyVolume: 0, commission: 2.9, category: 'Автозапчасти', createdDate: '2023-06-10', lastActivity: 'Вчера, 16:00' },
  { id: 'STR-1008', name: 'Kids Store', merchantName: 'ИП Детский', domain: 'kids-store.ru', status: 'active' as const, monthlyVolume: 650000, commission: 3.1, category: 'Детские товары', createdDate: '2023-03-25', lastActivity: 'Сегодня, 13:45' },
  { id: 'STR-1009', name: 'Electronics Hub', merchantName: 'ООО "Гаджеты"', domain: 'electronics.hub', status: 'active' as const, monthlyVolume: 3200000, commission: 2.3, category: 'Электроника', createdDate: '2022-12-01', lastActivity: 'Сегодня, 15:10' },
  { id: 'STR-1010', name: 'Food Market', merchantName: 'ИП Вкусный', domain: 'foodmarket.online', status: 'inactive' as const, monthlyVolume: 450000, commission: 4.0, category: 'Продукты', createdDate: '2023-02-14', lastActivity: '3 дня назад' },
  { id: 'STR-1011', name: 'Music Store', merchantName: 'ООО "Мелодия"', domain: 'music-store.net', status: 'active' as const, monthlyVolume: 380000, commission: 3.3, category: 'Музыка', createdDate: '2023-04-20', lastActivity: 'Вчера, 20:30' },
  { id: 'STR-1012', name: 'Tool Shop', merchantName: 'ИП Мастер', domain: 'tools.shop', status: 'active' as const, monthlyVolume: 1100000, commission: 2.6, category: 'Инструменты', createdDate: '2023-01-30', lastActivity: 'Сегодня, 11:00' }
];

export default function StoresPage() {
  return (
    <MainLayout>
      <StoreManagement 
        stores={mockStores}
        stats={mockStoreStats}
        loading={false}
      />
    </MainLayout>
  );
}
 