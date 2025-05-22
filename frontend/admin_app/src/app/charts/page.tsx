'use client';

import MainLayout from '@/layouts/MainLayout';
import { AnalyticsManagement } from '@/components/Charts/AnalyticsManagement';

// Симуляция аналитических данных
const mockAnalyticsStats = {
  totalSalesVolume: 15250000,
  totalTransactions: 4520,
  averageCheck: 3370,
  totalCommission: 305000,
  salesVolumeChange: 12.5,
  transactionsChange: 8.2,
  averageCheckChange: -2.1,
  commissionChange: 15.3
};

const mockAnalyticsData = [
  { date: '01.06.2023', salesVolume: 520000, transactions: 156, averageCheck: 3330, commission: 10400, conversion: 87.5 },
  { date: '02.06.2023', salesVolume: 485000, transactions: 142, averageCheck: 3415, commission: 9700, conversion: 89.2 },
  { date: '03.06.2023', salesVolume: 610000, transactions: 178, averageCheck: 3427, commission: 12200, conversion: 85.1 },
  { date: '04.06.2023', salesVolume: 475000, transactions: 138, averageCheck: 3442, commission: 9500, conversion: 91.3 },
  { date: '05.06.2023', salesVolume: 695000, transactions: 201, averageCheck: 3458, commission: 13900, conversion: 86.7 },
  { date: '06.06.2023', salesVolume: 540000, transactions: 162, averageCheck: 3333, commission: 10800, conversion: 88.4 },
  { date: '07.06.2023', salesVolume: 580000, transactions: 170, averageCheck: 3412, commission: 11600, conversion: 90.1 },
  { date: '08.06.2023', salesVolume: 465000, transactions: 135, averageCheck: 3444, commission: 9300, conversion: 87.9 },
  { date: '09.06.2023', salesVolume: 615000, transactions: 182, averageCheck: 3379, commission: 12300, conversion: 89.6 },
  { date: '10.06.2023', salesVolume: 525000, transactions: 154, averageCheck: 3409, commission: 10500, conversion: 88.8 },
  { date: '11.06.2023', salesVolume: 705000, transactions: 208, averageCheck: 3389, commission: 14100, conversion: 85.4 },
  { date: '12.06.2023', salesVolume: 590000, transactions: 175, averageCheck: 3371, commission: 11800, conversion: 91.2 },
  { date: '13.06.2023', salesVolume: 480000, transactions: 140, averageCheck: 3429, commission: 9600, conversion: 89.7 },
  { date: '14.06.2023', salesVolume: 655000, transactions: 195, averageCheck: 3359, commission: 13100, conversion: 87.3 },
  { date: '15.06.2023', salesVolume: 510000, transactions: 151, averageCheck: 3377, commission: 10200, conversion: 90.5 }
];

export default function ChartsPage() {
  return (
    <MainLayout>
      <AnalyticsManagement 
        data={mockAnalyticsData}
        stats={mockAnalyticsStats}
        loading={false}
      />
    </MainLayout>
  );
} 