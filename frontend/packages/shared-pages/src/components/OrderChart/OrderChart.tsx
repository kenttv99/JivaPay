'use client';

import React from 'react';

export interface OrderChartData {
  date: string;
  total_orders?: number;
  payin_orders?: number;
  payout_orders?: number;
  completed_orders?: number;
  failed_orders?: number;
  success_rate?: number;
}

interface ChartLine {
  key: string;
  name: string;
  color: string;
  isPercentage?: boolean;
}

interface OrderChartProps {
  data: OrderChartData[];
  type: 'orders' | 'success_rate' | 'order_types';
  title?: string;
  showLegend?: boolean;
  height?: number;
  className?: string;
}

export const OrderChart: React.FC<OrderChartProps> = ({
  data,
  type,
  title,
  showLegend = true,
  height = 400,
  className = ''
}) => {
  const chartWidth = 800;
  const chartHeight = height - 80;
  const padding = 60;

  // Получаем конфигурацию линий в зависимости от типа графика
  const getChartData = (): { lines: ChartLine[] } => {
    switch (type) {
      case 'orders':
        return {
          lines: [
            { key: 'total_orders', name: 'Всего ордеров', color: 'var(--jiva-primary)' },
            { key: 'completed_orders', name: 'Выполненные', color: 'var(--jiva-success)' },
            { key: 'failed_orders', name: 'Неудачные', color: 'var(--jiva-error)' }
          ]
        };
      case 'order_types':
        return {
          lines: [
            { key: 'payin_orders', name: 'Пополнения', color: 'var(--jiva-success)' },
            { key: 'payout_orders', name: 'Выводы', color: 'var(--jiva-info)' }
          ]
        };
      case 'success_rate':
        return {
          lines: [
            { key: 'success_rate', name: 'Успешность (%)', color: 'var(--jiva-warning)', isPercentage: true }
          ]
        };
      default:
        return { lines: [] };
    }
  };

  const chartConfig = getChartData();

  // Получаем все значения для масштабирования
  const getAllValues = () => {
    const allValues: number[] = [];
    data.forEach(item => {
      chartConfig.lines.forEach(line => {
        const value = item[line.key as keyof OrderChartData];
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

  // Для процентов используем диапазон 0-100
  const getScaledMinMax = () => {
    if (type === 'success_rate') {
      return { min: 0, max: 100, range: 100 };
    }
    return { min: minValue, max: maxValue, range: maxValue - minValue || 1 };
  };

  const { min: scaledMin, max: scaledMax, range: scaledRange } = getScaledMinMax();

  // Функции для координат
  const getY = (value: number) => {
    return chartHeight - padding - ((value - scaledMin) / scaledRange) * (chartHeight - 2 * padding);
  };

  const getX = (index: number) => {
    return padding + (index / (data.length - 1)) * (chartWidth - 2 * padding);
  };

  // Создание пути для линии
  const createPath = (lineKey: string) => {
    const points = data.map((item, index) => {
      const value = item[lineKey as keyof OrderChartData] as number || 0;
      return `${getX(index)},${getY(value)}`;
    });
    
    return `M ${points.join(' L ')}`;
  };

  // Форматирование значений
  const formatValue = (value: number, isPercentage?: boolean) => {
    if (isPercentage) {
      return `${value.toFixed(1)}%`;
    }
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    return value.toString();
  };

  // Создание области под графиком (для заливки)
  const createArea = (lineKey: string) => {
    const points = data.map((item, index) => {
      const value = item[lineKey as keyof OrderChartData] as number || 0;
      return `${getX(index)},${getY(value)}`;
    });
    
    const firstX = getX(0);
    const lastX = getX(data.length - 1);
    const bottomY = getY(scaledMin);
    
    return `M ${firstX},${bottomY} L ${points.join(' L ')} L ${lastX},${bottomY} Z`;
  };

  return (
    <div className={`bg-[var(--jiva-background-paper)] rounded-lg p-6 ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-[var(--jiva-text)] mb-4">{title}</h3>
      )}
      
      <div className="relative">
        <svg width={chartWidth} height={height} className="w-full">
          {/* Градиенты для заливки */}
          <defs>
            {chartConfig.lines.map((line, index) => (
              <linearGradient key={line.key} id={`gradient-${index}`} x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor={line.color} stopOpacity="0.3" />
                <stop offset="100%" stopColor={line.color} stopOpacity="0.1" />
              </linearGradient>
            ))}
            
            {/* Сетка */}
            <pattern id="orderGrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="var(--jiva-border-light)" strokeWidth="1" opacity="0.3"/>
            </pattern>
          </defs>
          
          <rect width={chartWidth} height={chartHeight} fill="url(#orderGrid)" />
          
          {/* Оси */}
          <line 
            x1={padding} y1={padding} 
            x2={padding} y2={chartHeight - padding} 
            stroke="var(--jiva-border-light)" strokeWidth="2"
          />
          <line 
            x1={padding} y1={chartHeight - padding} 
            x2={chartWidth - padding} y2={chartHeight - padding} 
            stroke="var(--jiva-border-light)" strokeWidth="2"
          />
          
          {/* Y подписи */}
          {[0, 0.25, 0.5, 0.75, 1].map(fraction => {
            const value = scaledMin + (scaledMax - scaledMin) * fraction;
            const y = getY(value);
            const isPercentage = type === 'success_rate';
            
            return (
              <g key={fraction}>
                <line 
                  x1={padding - 5} y1={y} 
                  x2={padding} y2={y} 
                  stroke="var(--jiva-border-light)" strokeWidth="1"
                />
                <text 
                  x={padding - 10} y={y + 4} 
                  textAnchor="end" 
                  className="text-xs fill-[var(--jiva-text-secondary)]"
                >
                  {formatValue(value, isPercentage)}
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
                    x1={x} y1={chartHeight - padding} 
                    x2={x} y2={chartHeight - padding + 5} 
                    stroke="var(--jiva-border-light)" strokeWidth="1"
                  />
                  <text 
                    x={x} y={chartHeight - padding + 20} 
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
          
          {/* Области под графиками */}
          {chartConfig.lines.map((line, index) => (
            <path
              key={`area-${line.key}`}
              d={createArea(line.key)}
              fill={`url(#gradient-${index})`}
            />
          ))}
          
          {/* Линии данных */}
          {chartConfig.lines.map(line => (
            <g key={line.key}>
              <path
                d={createPath(line.key)}
                fill="none"
                stroke={line.color}
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              
              {/* Точки */}
              {data.map((item, index) => {
                const value = item[line.key as keyof OrderChartData] as number;
                if (typeof value !== 'number') return null;
                
                return (
                  <circle
                    key={index}
                    cx={getX(index)}
                    cy={getY(value)}
                    r="5"
                    fill="white"
                    stroke={line.color}
                    strokeWidth="3"
                    className="hover:r-7 transition-all cursor-pointer"
                  >
                    <title>
                      {`${line.name}: ${formatValue(value, line.isPercentage)} (${item.date})`}
                    </title>
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
          const values = data.map(item => item[line.key as keyof OrderChartData] as number || 0);
          const current = values[values.length - 1] || 0;
          const previous = values[values.length - 2] || 0;
          const change = previous !== 0 ? ((current - previous) / previous) * 100 : 0;
          
          return (
            <div key={line.key} className="text-center">
              <div className="text-sm text-[var(--jiva-text-secondary)]">{line.name}</div>
              <div className="text-lg font-semibold text-[var(--jiva-text)]">
                {formatValue(current, line.isPercentage)}
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