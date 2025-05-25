'use client';

import React from 'react';

export interface BalanceChartData {
  date: string;
  platform_balance?: number;
  merchant_balance?: number;
  trader_balance?: number;
  total_volume?: number;
  commissions?: number;
}

interface BalanceChartProps {
  data: BalanceChartData[];
  type: 'balances' | 'volume' | 'commissions';
  title?: string;
  showLegend?: boolean;
  height?: number;
  className?: string;
}

export const BalanceChart: React.FC<BalanceChartProps> = ({
  data,
  type,
  title,
  showLegend = true,
  height = 400,
  className = ''
}) => {
  // Создаем простую SVG диаграмму без внешних зависимостей
  const chartWidth = 800;
  const chartHeight = height - 80; // Место для заголовка и легенды
  const padding = 60;

  // Получаем данные для отображения в зависимости от типа
  const getChartData = () => {
    switch (type) {
      case 'balances':
        return {
          lines: [
            { key: 'platform_balance', name: 'Баланс платформы', color: 'rgb(var(--color-secondary))' },
            { key: 'merchant_balance', name: 'Баланс мерчантов', color: 'rgb(var(--color-success))' },
            { key: 'trader_balance', name: 'Баланс трейдеров', color: 'rgb(var(--color-info))' }
          ]
        };
      case 'volume':
        return {
          lines: [
            { key: 'total_volume', name: 'Общий объем', color: 'rgb(var(--color-secondary))' }
          ]
        };
      case 'commissions':
        return {
          lines: [
            { key: 'commissions', name: 'Комиссии', color: 'rgb(var(--color-warning))' }
          ]
        };
      default:
        return { lines: [] };
    }
  };

  const chartConfig = getChartData();
  const stepX = data.length > 1 ? (650 / (data.length - 1)) : 0;
  const lines = chartConfig.lines;

  // Находим максимальные и минимальные значения для масштабирования
  const getAllValues = () => {
    const allValues: number[] = [];
    data.forEach(item => {
      chartConfig.lines.forEach(line => {
        const value = item[line.key as keyof BalanceChartData];
        if (typeof value === 'number') {
          allValues.push(value);
        }
      });
    });
    return allValues;
  };

  const allValues = getAllValues();
  const maxValue = Math.max(...allValues, 0);
  const minValue = Math.min(...allValues, 0);
  const valueRange = maxValue - minValue || 1;

  // Функция для получения Y координаты точки
  const getY = (value: number) => {
    return chartHeight - padding - ((value - minValue) / valueRange) * (chartHeight - 2 * padding);
  };

  // Функция для получения X координаты точки
  const getX = (index: number) => {
    return padding + (index / (data.length - 1)) * (chartWidth - 2 * padding);
  };

  // Создаем путь для линии
  const createPath = (lineKey: string) => {
    const points = data.map((item, index) => {
      const value = item[lineKey as keyof BalanceChartData] as number || 0;
      return `${getX(index)},${getY(value)}`;
    });
    
    return `M ${points.join(' L ')}`;
  };

  // Форматирование значений для отображения
  const formatValue = (value: number) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    return value.toString();
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className={`bg-surface rounded-lg p-6 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-primary mb-4">{title}</h3>
        <div className="flex gap-2">
          {/* Переключатели типов графика */}
        </div>
      </div>
      
      <div style={{ width: '100%', height: 400 }}>
        <svg viewBox="0 0 800 400" className="w-full h-full">
          {/* Сетка */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgb(var(--color-border))" strokeWidth="1" opacity="0.3"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* Вертикальные линии сетки */}
          {Array.from({ length: 8 }, (_, i) => (
            <line 
              key={`v-line-${i}`}
              x1={100 + i * 87.5}
              y1={50}
              x2={100 + i * 87.5}
              y2={350}
              stroke="rgb(var(--color-border))"
              strokeWidth="1"
              opacity="0.3"
            />
          ))}
          
          {/* Горизонтальные линии сетки */}
          {Array.from({ length: 6 }, (_, i) => (
            <line 
              key={`h-line-${i}`}
              x1={100}
              y1={50 + i * 50}
              x2={750}
              y2={50 + i * 50}
              stroke="rgb(var(--color-border))"
              strokeWidth="1"
              opacity="0.3"
            />
          ))}
          
          {/* Подписи по Y */}
          {Array.from({ length: 6 }, (_, i) => (
            <text 
              key={`y-label-${i}`}
              x="90"
              y={55 + i * 50}
              className="text-xs fill-secondary"
              textAnchor="end"
            >
              {maxValue - (i * maxValue / 5)}
            </text>
          ))}
          
          {/* Подписи по X */}
          {data.map((item, index) => (
            <text 
              key={`x-label-${index}`}
              x={100 + index * stepX}
              y="375"
              className="text-xs fill-secondary"
              textAnchor="middle"
            >
              {new Date(item.date).toLocaleDateString()}
            </text>
          ))}
          
          {/* Линии графика */}
          {lines.map((line, lineIndex) => {
            const pathData = data.map((item, index) => {
              const x = 100 + index * stepX;
              const value = (item as any)[line.key] || 0;
              const y = 350 - (value / maxValue) * 300;
              return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
            }).join(' ');
            
            return (
              <path
                key={`line-${lineIndex}`}
                d={pathData}
                fill="none"
                stroke={line.color}
                strokeWidth="2"
              />
            );
          })}
          
          {/* Точки на линиях */}
          {lines.map((line, lineIndex) => 
            data.map((item, index) => {
              const x = 100 + index * stepX;
              const value = (item as any)[line.key] || 0;
              const y = 350 - (value / maxValue) * 300;
              
              return (
                <circle
                  key={`point-${lineIndex}-${index}`}
                  cx={x}
                  cy={y}
                  r="3"
                  fill={line.color}
                />
              );
            })
          )}
        </svg>
      </div>
      
      {/* Легенда */}
      <div className="mt-4 flex flex-wrap gap-4">
        {lines.map((line, index) => (
          <div key={index} className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded"
              style={{ backgroundColor: line.color }}
            ></div>
            <span className="text-sm text-secondary">
              {line.name}
            </span>
          </div>
        ))}
      </div>
      
      {/* Статистика */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-4 border-t border-border">
        {lines.map((line, index) => {
          const currentValue = (data[data.length - 1] as any)?.[line.key] || 0;
          const previousValue = (data[data.length - 2] as any)?.[line.key] || 0;
          const change = previousValue !== 0 ? ((currentValue - previousValue) / previousValue) * 100 : 0;
          
          return (
            <div key={index} className="text-center">
              <div className="text-sm text-secondary">{line.name}</div>
              <div className="text-lg font-semibold text-primary">
                {formatCurrency(currentValue)}
              </div>
              <div className={`text-sm ${change >= 0 ? 'text-success' : 'text-error'}`}>
                {change >= 0 ? '+' : ''}{change.toFixed(1)}%
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}; 