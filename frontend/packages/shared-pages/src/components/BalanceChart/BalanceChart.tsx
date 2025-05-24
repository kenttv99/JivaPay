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
            { key: 'platform_balance', name: 'Баланс платформы', color: 'var(--jiva-primary)' },
            { key: 'merchant_balance', name: 'Баланс мерчантов', color: 'var(--jiva-success)' },
            { key: 'trader_balance', name: 'Баланс трейдеров', color: 'var(--jiva-info)' }
          ]
        };
      case 'volume':
        return {
          lines: [
            { key: 'total_volume', name: 'Общий объем', color: 'var(--jiva-primary)' }
          ]
        };
      case 'commissions':
        return {
          lines: [
            { key: 'commissions', name: 'Комиссии', color: 'var(--jiva-warning)' }
          ]
        };
      default:
        return { lines: [] };
    }
  };

  const chartConfig = getChartData();

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

  return (
    <div className={`bg-[var(--jiva-background-paper)] rounded-lg p-6 ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">{title}</h3>
      )}
      
      <div className="relative">
        <svg width={chartWidth} height={height} className="w-full">
          {/* Сетка */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="var(--jiva-border-light)" strokeWidth="1" opacity="0.3"/>
            </pattern>
          </defs>
          <rect width={chartWidth} height={chartHeight} fill="url(#grid)" />
          
          {/* Y ось */}
          <line 
            x1={padding} 
            y1={padding} 
            x2={padding} 
            y2={chartHeight - padding} 
            stroke="var(--jiva-border-light)" 
            strokeWidth="2"
          />
          
          {/* X ось */}
          <line 
            x1={padding} 
            y1={chartHeight - padding} 
            x2={chartWidth - padding} 
            y2={chartHeight - padding} 
            stroke="var(--jiva-border-light)" 
            strokeWidth="2"
          />
          
          {/* Y подписи */}
          {[0, 0.25, 0.5, 0.75, 1].map(fraction => {
            const value = minValue + (maxValue - minValue) * fraction;
            const y = getY(value);
            return (
              <g key={fraction}>
                <line 
                  x1={padding - 5} 
                  y1={y} 
                  x2={padding} 
                  y2={y} 
                  stroke="var(--jiva-border-light)" 
                  strokeWidth="1"
                />
                <text 
                  x={padding - 10} 
                  y={y + 4} 
                  textAnchor="end" 
                  className="text-xs fill-[var(--jiva-text-secondary)]"
                >
                  {formatValue(value)}
                </text>
              </g>
            );
          })}
          
          {/* X подписи (даты) */}
          {data.map((item, index) => {
            if (index % Math.ceil(data.length / 6) === 0 || index === data.length - 1) {
              const x = getX(index);
              return (
                <g key={index}>
                  <line 
                    x1={x} 
                    y1={chartHeight - padding} 
                    x2={x} 
                    y2={chartHeight - padding + 5} 
                    stroke="var(--jiva-border-light)" 
                    strokeWidth="1"
                  />
                  <text 
                    x={x} 
                    y={chartHeight - padding + 20} 
                    textAnchor="middle" 
                    className="text-xs fill-[var(--jiva-text-secondary)]"
                  >
                    {new Date(item.date).toLocaleDateString('ru-RU', { 
                      month: 'short', 
                      day: 'numeric' 
                    })}
                  </text>
                </g>
              );
            }
            return null;
          })}
          
          {/* Линии данных */}
          {chartConfig.lines.map(line => (
            <g key={line.key}>
              <path
                d={createPath(line.key)}
                fill="none"
                stroke={line.color}
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              
              {/* Точки */}
              {data.map((item, index) => {
                const value = item[line.key as keyof BalanceChartData] as number;
                if (typeof value !== 'number') return null;
                
                return (
                  <circle
                    key={index}
                    cx={getX(index)}
                    cy={getY(value)}
                    r="4"
                    fill={line.color}
                    className="hover:r-6 transition-all cursor-pointer"
                  >
                    <title>{`${line.name}: ${formatValue(value)} (${item.date})`}</title>
                  </circle>
                );
              })}
            </g>
          ))}
        </svg>
      </div>
      
      {/* Легенда */}
      {showLegend && (
        <div className="flex flex-wrap gap-4 mt-4">
          {chartConfig.lines.map(line => (
            <div key={line.key} className="flex items-center gap-2">
              <div 
                className="w-4 h-4 rounded"
                style={{ backgroundColor: line.color }}
              />
              <span className="text-sm text-[var(--jiva-text-secondary)]">
                {line.name}
              </span>
            </div>
          ))}
        </div>
      )}
      
      {/* Статистика */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-4 border-t border-[var(--jiva-border-light)]">
        {chartConfig.lines.map(line => {
          const values = data.map(item => item[line.key as keyof BalanceChartData] as number || 0);
          const current = values[values.length - 1] || 0;
          const previous = values[values.length - 2] || 0;
          const change = previous !== 0 ? ((current - previous) / previous) * 100 : 0;
          
          return (
            <div key={line.key} className="text-center">
              <div className="text-sm text-[var(--jiva-text-secondary)]">{line.name}</div>
              <div className="text-lg font-semibold text-[var(--jiva-text)]">
                {formatValue(current)}
              </div>
              <div className={`text-sm ${change >= 0 ? 'text-[var(--jiva-success)]' : 'text-[var(--jiva-error)]'}`}>
                {change >= 0 ? '+' : ''}{change.toFixed(1)}%
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}; 