'use client';

import React from 'react';

export interface OrderChartData {
  date: string;
  total_orders: number;
  completed_orders: number;
  failed_orders: number;
  payin_orders: number;
  payout_orders: number;
  success_rate: number;
}

interface ChartLine {
  key: string;
  name: string;
  color: string;
  isPercentage?: boolean;
}

interface OrderChartProps {
  data: OrderChartData[];
  type: 'orders' | 'order_types' | 'success_rate';
  title?: string;
  height?: number;
  width?: number;
  showLegend?: boolean;
  className?: string;
}

const formatValue = (value: number, isPercentage?: boolean) => {
  if (isPercentage) {
    return `${value.toFixed(1)}%`;
  }
  return value.toLocaleString();
};

export const OrderChart: React.FC<OrderChartProps> = ({
  data,
  type,
  title,
  height = 400,
  width = 800,
  showLegend = true,
  className = ''
}) => {
  const chartWidth = width;
  const chartHeight = height - 80;
  const padding = 60;

  const statusOptions = [
    { key: 'total_orders', name: 'Всего ордеров', color: 'rgb(var(--color-primary))' },
    { key: 'completed_orders', name: 'Выполненные', color: 'rgb(var(--color-success))' },
    { key: 'failed_orders', name: 'Неудачные', color: 'rgb(var(--color-error))' }
  ];

  const typeOptions = [
    { key: 'payin_orders', name: 'Пополнения', color: 'rgb(var(--color-success))' },
    { key: 'payout_orders', name: 'Выводы', color: 'rgb(var(--color-info))' }
  ];

  const rateOptions = [
    { key: 'success_rate', name: 'Успешность (%)', color: 'rgb(var(--color-warning))', isPercentage: true }
  ];

  // Получаем конфигурацию линий в зависимости от типа графика
  const getChartConfig = () => {
    switch (type) {
      case 'orders':
        return {
          lines: statusOptions
        };
      case 'order_types':
        return {
          lines: typeOptions
        };
      case 'success_rate':
        return {
          lines: rateOptions
        };
      default:
        return { lines: statusOptions };
    }
  };

  const chartConfig = getChartConfig();
  const lines = chartConfig.lines;

  // Находим минимальные и максимальные значения для масштабирования
  const allValues = data.flatMap(item => 
    lines.map(line => item[line.key as keyof OrderChartData] as number || 0)
  );
  const maxValue = Math.max(...allValues);
  const minValue = Math.min(...allValues);
  const scaledMax = maxValue * 1.1;
  const scaledMin = Math.max(0, minValue * 0.9);

  // Функции для координат
  const getX = (index: number) => {
    return padding + (index / (data.length - 1)) * (chartWidth - 2 * padding);
  };

  const getY = (value: number) => {
    const ratio = (value - scaledMin) / (scaledMax - scaledMin);
    return chartHeight - padding - ratio * (chartHeight - 2 * padding);
  };

  // Генерация меток для Y оси
  const yLabels = [0, 0.25, 0.5, 0.75, 1].map(fraction => {
    const value = scaledMin + (scaledMax - scaledMin) * fraction;
    return {
      y: getY(value),
      value: formatValue(value, type === 'success_rate')
    };
  });

  // Простой форматтер даты
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return `${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')}`;
  };

  // Форматтер времени
  const formatTime = () => {
    const now = new Date();
    return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
  };

  // Создание пути для линии
  const createPath = (lineKey: string) => {
    const points = data.map((item, index) => {
      const value = item[lineKey as keyof OrderChartData] as number || 0;
      return `${getX(index)},${getY(value)}`;
    });
    
    return `M ${points.join(' L ')}`;
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
    <div className={`bg-surface rounded-lg p-6 ${className}`}>
      {/* Заголовок */}
      <h3 className="text-lg font-semibold text-primary mb-4">{title}</h3>

      {/* SVG График */}
      <div className="relative">
        <svg width={chartWidth} height={height} className="overflow-visible">
          {/* Фоновая сетка */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgb(var(--color-border))" strokeWidth="1" opacity="0.3"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* Оси координат */}
          <g>
            {/* Y-ось */}
            <line 
              x1={padding} y1={padding} 
              x2={padding} y2={height - padding}
              stroke="rgb(var(--color-border))" strokeWidth="2"
            />
            {/* X-ось */}
            <line 
              x1={padding} y1={height - padding} 
              x2={chartWidth - padding} y2={height - padding}
              stroke="rgb(var(--color-border))" strokeWidth="2"
            />
          </g>

          {/* Разметка оси Y */}
          <g>
            {yLabels.map((label, index) => (
              <g key={index}>
                <line
                  x1={padding - 5} y1={label.y}
                  x2={padding} y2={label.y}
                  stroke="rgb(var(--color-border))" strokeWidth="1"
                />
                <text
                  x={padding - 10} y={label.y + 4}
                  textAnchor="end"
                  className="text-xs fill-secondary"
                >
                  {label.value}
                </text>
              </g>
            ))}
          </g>

          {/* Разметка оси X */}
          <g>
            {data.map((point, index) => (
              <g key={index}>
                <line
                  x1={getX(index)} y1={height - padding}
                  x2={getX(index)} y2={height - padding + 5}
                  stroke="rgb(var(--color-border))" strokeWidth="1"
                />
                <text
                  x={getX(index)} y={height - padding + 20}
                  textAnchor="middle"
                  className="text-xs fill-secondary"
                >
                  {formatDate(point.date)}
                </text>
              </g>
            ))}
          </g>

          {/* Линии графика */}
          {lines.map((line, lineIndex) => {
            const linePoints = data.map((point, index) => {
              const value = point[line.key as keyof OrderChartData] as number;
              return `${getX(index)},${getY(value)}`;
            }).join(' ');

            return (
              <g key={line.key}>
                {/* Линия */}
                <polyline
                  points={linePoints}
                  fill="none"
                  stroke={line.color}
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                
                {/* Точки */}
                {data.map((point, index) => {
                  const value = point[line.key as keyof OrderChartData] as number;
                  return (
                    <circle
                      key={index}
                      cx={getX(index)}
                      cy={getY(value)}
                      r="4"
                      fill={line.color}
                      stroke="white"
                      strokeWidth="2"
                    />
                  );
                })}
              </g>
            );
          })}
        </svg>

        {/* Тултип (если нужен) */}
        <div className="absolute top-4 right-4 bg-surface border border-border rounded-lg p-3 shadow-lg">
          <span className="text-sm text-secondary">
            Последнее обновление: {formatTime()}
          </span>
        </div>
      </div>

      {/* Легенда */}
      {showLegend && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-4 border-t border-border">
          {lines.map((line) => {
            const latestValue = data[data.length - 1]?.[line.key as keyof OrderChartData] as number || 0;
            const previousValue = data[data.length - 2]?.[line.key as keyof OrderChartData] as number || 0;
            const change = latestValue - previousValue;
            const isPercentage = line.key === 'success_rate';
            
            return (
              <div key={line.key} className="flex items-center space-x-2">
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: line.color }}
                />
                <div>
                  <div className="text-sm text-secondary">{line.name}</div>
                  <div className="text-lg font-semibold text-primary">
                    {isPercentage ? `${latestValue}%` : latestValue.toLocaleString()}
                  </div>
                  <div className={`text-sm ${change >= 0 ? 'text-success' : 'text-error'}`}>
                    {change >= 0 ? '+' : ''}{change}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};