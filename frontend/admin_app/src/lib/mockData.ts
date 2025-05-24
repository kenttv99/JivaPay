import { OrderItem } from '@jivapay/shared-pages';

// Mock данные для тестирования DashboardPage
export const mockRecentOrders: OrderItem[] = [
  {
    id: 'ORD-2024-001',
    date: '2024-12-27 14:23',
    user: 'merchant123',
    amount: '₽ 15,000',
    amount_crypto: '0.0425',
    currency_crypto: 'BTC',
    type: 'payin',
    status: 'completed',
    trader: 'trader_alex',
    requisite: 'Sber *1234',
    store_commission: '₽ 150',
    trader_commission: '₽ 75',
    store_name: 'TechShop',
    external_order_id: 'EXT-12345'
  },
  {
    id: 'ORD-2024-002',
    date: '2024-12-27 14:18',
    user: 'trader_bob',
    amount: '₽ 25,000',
    amount_crypto: '0.0708',
    currency_crypto: 'BTC',
    type: 'payout',
    status: 'processing',
    trader: 'trader_bob',
    requisite: 'Tinkoff *5678',
    store_commission: '₽ 250',
    trader_commission: '₽ 125',
    store_name: undefined,
    external_order_id: undefined
  },
  {
    id: 'ORD-2024-003',
    date: '2024-12-27 14:12',
    user: 'merchant456',
    amount: '₽ 8,500',
    amount_crypto: '0.0241',
    currency_crypto: 'BTC',
    type: 'payin',
    status: 'pending',
    trader: undefined,
    requisite: undefined,
    store_commission: '₽ 85',
    trader_commission: undefined,
    store_name: 'GameStore',
    external_order_id: 'EXT-67890'
  },
  {
    id: 'ORD-2024-004',
    date: '2024-12-27 14:05',
    user: 'merchant789',
    amount: '₽ 42,000',
    amount_crypto: '0.1192',
    currency_crypto: 'BTC',
    type: 'payin',
    status: 'disputed',
    trader: 'trader_charlie',
    requisite: 'VTB *9012',
    store_commission: '₽ 420',
    trader_commission: '₽ 210',
    store_name: 'FashionStore',
    external_order_id: 'EXT-11111'
  },
  {
    id: 'ORD-2024-005',
    date: '2024-12-27 13:58',
    user: 'trader_diana',
    amount: '₽ 12,300',
    amount_crypto: '0.0349',
    currency_crypto: 'BTC',
    type: 'payout',
    status: 'failed',
    trader: 'trader_diana',
    requisite: 'Alpha *3456',
    store_commission: undefined,
    trader_commission: '₽ 62',
    store_name: undefined,
    external_order_id: undefined
  }
];

export const mockMetricsData = {
  activeUsers: 2847,
  newStores: 28, 
  transactionVolume: '₽ 4.2M',
  revenue: '₽ 127K',
  ordersInProgress: 142
}; 