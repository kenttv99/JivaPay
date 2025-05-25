'use client';

import { useState } from 'react';
import MainLayout from '@/layouts/MainLayout';
import { RecentOrders } from '../components/Dashboard/RecentOrders';
import { DollarSign, CreditCard, Clock, Package, Users, Store, Headset, TrendingUp } from 'lucide-react';

export default function Dashboard() {
  const [conversionTab, setConversionTab] = useState("all");

  const handleViewAllOrders = () => {
    console.log("Переход к ордерам");
  };

  return (
    <MainLayout>
      <div className="dashboard-container space-y-8 bg-white">
        <div className="flex items-center justify-between">
        <div>
            <h1 className="text-2xl font-bold tracking-tight text-[#000000]">Дашборд JivaPay</h1>
            <p className="text-[#1D1D1D]">
              Обзор платформы, статистика и активность
            </p>
          </div>
          <button className="flex items-center gap-2 border border-[#2E2E2E] text-[#1D1D1D] hover:bg-[#F8F8F8] px-3 py-2 rounded-md text-sm">
            <TrendingUp size={16} />
            <span>Экспорт отчета</span>
          </button>
        </div>
        
        <div className="grid gap-6 grid-cols-12">
          <div className="col-span-12 md:col-span-4 p-6 border-[#E5E5E5] bg-white shadow-sm relative rounded-lg border">
            <div className="flex flex-col">
              <p className="text-sm font-medium text-[#666666]">Общий баланс USDT</p>
              <p className="mt-2 text-4xl font-bold text-[#000000]">1,234,500</p>
              <p className="mt-2 text-xs text-green-600 font-medium">+12.5% с прошлого месяца</p>
            </div>
            <div className="absolute top-5 right-5 rounded-full p-3 bg-[#000000]">
              <DollarSign className="h-6 w-6 text-white" />
            </div>
          </div>
          
          <div className="col-span-12 md:col-span-8 grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              title="Трейдеры"
              value="48"
              description="+3 за неделю"
              icon={<Users className="h-5 w-5 text-white" />}
            />
            <StatCard
              title="Мерчанты"
              value="124"
              description="+5 за неделю"
              icon={<CreditCard className="h-5 w-5 text-white" />}
            />
            <StatCard
              title="Магазины"
              value="196"
              description="+8 за неделю"
              icon={<Store className="h-5 w-5 text-white" />}
            />
            <StatCard
              title="Саппорт"
              value="12"
              description="+1 за неделю"
              icon={<Headset className="h-5 w-5 text-white" />}
            />
          </div>
        </div>
        
        <div className="grid gap-6 grid-cols-12">
          <div className="col-span-12 md:col-span-6 border-[#E5E5E5] bg-white shadow-sm rounded-lg border p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-medium text-[#000000]">Доход и активность</h3>
              <select className="rounded border border-[#E5E5E5] bg-white px-2 py-1 text-sm text-[#1D1D1D]">
                <option>За 7 дней</option>
                <option>За 30 дней</option>
                <option>За 90 дней</option>
              </select>
            </div>
            <div className="aspect-[16/9] bg-gray-100 rounded flex items-center justify-center">
              <p className="text-gray-500">График доходов</p>
            </div>
          </div>
          
          <div className="col-span-12 md:col-span-6 border-[#E5E5E5] bg-white shadow-sm rounded-lg border p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-medium text-[#000000]">Конверсия ордеров</h3>
              <div>
                <div className="bg-[#F6F6F6] h-8 rounded p-1 flex">
                  <button 
                    onClick={() => setConversionTab("all")}
                    className={`h-6 text-xs px-2 rounded ${conversionTab === "all" ? "bg-[#000000] text-white" : "text-[#1D1D1D]"}`}
                  >
                    Все
                  </button>
                  <button 
                    onClick={() => setConversionTab("merchants")}
                    className={`h-6 text-xs px-2 rounded ${conversionTab === "merchants" ? "bg-[#000000] text-white" : "text-[#1D1D1D]"}`}
                  >
                    По мерчантам
                  </button>
                  <button 
                    onClick={() => setConversionTab("stores")}
                    className={`h-6 text-xs px-2 rounded ${conversionTab === "stores" ? "bg-[#000000] text-white" : "text-[#1D1D1D]"}`}
                  >
                    По магазинам
                  </button>
                </div>
              </div>
            </div>
            <div className="aspect-[16/9] bg-gray-100 rounded flex items-center justify-center">
              <p className="text-gray-500">График конверсии</p>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatsInfoCard
            title="Ордеры в обработке"
            value="42"
            description="18 в процессе оплаты"
            icon={<Package className="h-8 w-8 text-white" />}
          />
          
          <StatsInfoCard
            title="Реквизиты онлайн"
            value="156"
            description="83% доступность"
            icon={<CreditCard className="h-8 w-8 text-white" />}
          />

          <StatsInfoCard
            title="Конверсия"
            value="89%"
            description="+4.2% за месяц"
            icon={<TrendingUp className="h-8 w-8 text-white" />}
          />

          <StatsInfoCard
            title="Среднее время"
            value="12m 30s"
            description="Обработка ордера"
            icon={<Clock className="h-8 w-8 text-white" />}
          />
        </div>

        <div className="border-[#E5E5E5] bg-white shadow-sm rounded-lg border">
          <div className="mb-4 flex items-center justify-between p-6">
            <h3 className="text-lg font-medium text-[#000000]">История ордеров</h3>
            <button 
              onClick={handleViewAllOrders}
              className="flex items-center gap-2 border border-[#2E2E2E] text-[#1D1D1D] hover:bg-[#F6F6F6] px-3 py-2 rounded-md text-sm"
            >
              <TrendingUp size={16} />
              <span>Смотреть все</span>
            </button>
          </div>
          <div className="px-6 pb-6">
            <RecentOrders />
          </div>
        </div>
            </div>
    </MainLayout>
  );
}

interface StatCardProps {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
  className?: string;
}

const StatCard = ({ title, value, description, icon, className }: StatCardProps) => {
  return (
    <div className={`p-4 border-[#E5E5E5] bg-white shadow-sm rounded-lg border ${className || ''}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-[#666666] truncate">{title}</p>
            </div>
        <div className="flex-shrink-0 ml-3 rounded-full p-2 bg-[#1D1D1D]">
          {icon}
                  </div>
                  </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold text-[#000000]">{value}</p>
        <p className="text-xs text-[#666666]">{description}</p>
                  </div>
                </div>
  );
};

interface StatsInfoCardProps {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
}

const StatsInfoCard = ({ title, value, description, icon }: StatsInfoCardProps) => {
  return (
    <div className="p-6 border-[#E5E5E5] bg-white shadow-sm rounded-lg border">
      <div className="flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-[#000000]">{title}</h3>
          <div className="flex-shrink-0 rounded-full bg-[#000000] p-3">
            {icon}
          </div>
        </div>
        <div className="flex flex-col space-y-2">
          <p className="text-3xl font-bold text-[#000000]">{value}</p>
          <p className="text-sm text-[#666666]">{description}</p>
        </div>
      </div>
    </div>
  );
};
