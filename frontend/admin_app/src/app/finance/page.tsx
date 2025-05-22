'use client';

import MainLayout from '@/layouts/MainLayout';
import { FinanceManagement } from '@/components/Finance/FinanceManagement';

// Симуляция финансовых данных
const mockStats = {
  totalBalance: 12458320,
  monthlyCommissions: 245320,
  dailyTransactions: 1248,
  averageCheck: 4320,
  balanceChange: 2.5,
  commissionsChange: 5.2,
  transactionsChange: -1.3,
  checkChange: 0.8
};

const mockTransactions = [
  { id: 'TRX-10001', date: '2023-06-15 11:30:00', store: 'TechShop', amount: 1500, commission: 30, status: 'success' as const, method: 'Банковская карта', currency: 'RUB' },
  { id: 'TRX-10002', date: '2023-06-15 10:45:00', store: 'BookStore', amount: 2500, commission: 50, status: 'processing' as const, method: 'Электронный кошелек', currency: 'RUB' },
  { id: 'TRX-10003', date: '2023-06-15 09:20:00', store: 'FashionHub', amount: 3500, commission: 70, status: 'failed' as const, method: 'Криптовалюта', currency: 'RUB' },
  { id: 'TRX-10004', date: '2023-06-15 08:15:00', store: 'SportWorld', amount: 4500, commission: 90, status: 'refund' as const, method: 'Банковская карта', currency: 'RUB' },
  { id: 'TRX-10005', date: '2023-06-15 07:30:00', store: 'ElectroMarket', amount: 5500, commission: 110, status: 'success' as const, method: 'Банковская карта', currency: 'RUB' },
  { id: 'TRX-10006', date: '2023-06-14 18:45:00', store: 'GadgetStore', amount: 2800, commission: 56, status: 'success' as const, method: 'Apple Pay', currency: 'RUB' },
  { id: 'TRX-10007', date: '2023-06-14 17:20:00', store: 'HomeDecor', amount: 1200, commission: 24, status: 'processing' as const, method: 'Google Pay', currency: 'RUB' },
  { id: 'TRX-10008', date: '2023-06-14 16:10:00', store: 'AutoParts', amount: 7500, commission: 150, status: 'success' as const, method: 'Банковская карта', currency: 'RUB' }
];

export default function FinancePage() {
  return (
    <MainLayout>
      <FinanceManagement 
        transactions={mockTransactions} 
        stats={mockStats} 
        loading={false} 
      />
    </MainLayout>
  );
} 