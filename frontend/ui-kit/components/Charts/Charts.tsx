import React, { useEffect, useState } from 'react';

interface DataPoint {
  label: string;
  value: number;
  date?: string;
}

interface ChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
  color?: string;
  gradient?: boolean;
  animated?: boolean;
  isLoading?: boolean;
  className?: string;
  title?: string;
  showGrid?: boolean;
  showTooltip?: boolean;
}

// Skeleton для графиков
const ChartSkeleton: React.FC<{ width: number; height: number; title?: string }> = ({ 
  width, 
  height, 
  title 
}) => (
  <div className="bg-background border border-border rounded-lg p-4">
    {title && (
      <div className="h-5 w-32 bg-muted rounded animate-pulse mb-4" />
    )}
    <div 
      className="bg-muted rounded animate-pulse"
      style={{ width, height }}
    />
  </div>
);

// Утилитарные функции
const getMinMax = (data: DataPoint[]) => {
  const values = data.map(d => d.value);
  return {
    min: Math.min(...values),
    max: Math.max(...values)
  };
};

const getPath = (data: DataPoint[], width: number, height: number) => {
  if (data.length === 0) return '';
  
  const { min, max } = getMinMax(data);
  const range = max - min || 1;
  
  const points = data.map((point, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((point.value - min) / range) * height;
    return `${x},${y}`;
  });
  
  return `M ${points.join(' L ')}`;
};

// Линейный график
export const LineChart: React.FC<ChartProps> = ({
  data,
  width = 400,
  height = 200,
  color = 'var(--color-secondary)',
  gradient = true,
  animated = true,
  isLoading = false,
  className = '',
  title,
  showGrid = true,
  showTooltip = false
}) => {
  const [mounted, setMounted] = useState(false);
  const [animatedData, setAnimatedData] = useState<DataPoint[]>([]);

  useEffect(() => {
    setMounted(true);
    if (animated) {
      // Анимация появления данных
      const timer = setTimeout(() => {
        setAnimatedData(data);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setAnimatedData(data);
    }
  }, [data, animated]);

  if (isLoading) {
    return <ChartSkeleton width={width} height={height} title={title} />;
  }

  const { min, max } = getMinMax(data);
  const path = getPath(animatedData, width, height);
  const gradientId = `gradient-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className={`bg-background border border-border rounded-lg p-4 ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-primary mb-4">{title}</h3>
      )}
      
      <div className="relative">
        <svg 
          width={width} 
          height={height} 
          className="overflow-visible"
          style={{ animation: mounted ? 'fadeIn 0.5s ease-out' : 'none' }}
        >
          {/* Градиент */}
          {gradient && (
            <defs>
              <linearGradient id={gradientId} x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style={{ stopColor: color, stopOpacity: 0.3 }} />
                <stop offset="100%" style={{ stopColor: color, stopOpacity: 0.05 }} />
              </linearGradient>
            </defs>
          )}

          {/* Сетка */}
          {showGrid && (
            <g className="opacity-20">
              {[...Array(5)].map((_, i) => (
                <line
                  key={`horizontal-${i}`}
                  x1={0}
                  y1={(height / 4) * i}
                  x2={width}
                  y2={(height / 4) * i}
                  stroke="currentColor"
                  strokeWidth={1}
                  className="text-muted"
                />
              ))}
              {[...Array(6)].map((_, i) => (
                <line
                  key={`vertical-${i}`}
                  x1={(width / 5) * i}
                  y1={0}
                  x2={(width / 5) * i}
                  y2={height}
                  stroke="currentColor"
                  strokeWidth={1}
                  className="text-muted"
                />
              ))}
            </g>
          )}

          {/* Область под линией */}
          {gradient && path && (
            <path
              d={`${path} L ${width},${height} L 0,${height} Z`}
              fill={`url(#${gradientId})`}
              style={{
                animation: animated ? 'fadeIn 1s ease-out 0.2s both' : 'none'
              }}
            />
          )}

          {/* Линия */}
          {path && (
            <path
              d={path}
              fill="none"
              stroke={color}
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{
                strokeDasharray: animated ? '1000' : 'none',
                strokeDashoffset: animated ? '1000' : '0',
                animation: animated ? 'dashOffset 2s ease-out 0.5s both' : 'none'
              }}
            />
          )}

          {/* Точки */}
          {animatedData.map((point, index) => {
            const { min: dataMin, max: dataMax } = getMinMax(data);
            const range = dataMax - dataMin || 1;
            const x = (index / (data.length - 1)) * width;
            const y = height - ((point.value - dataMin) / range) * height;
            
            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r={4}
                fill={color}
                className="opacity-80 hover:opacity-100 transition-opacity cursor-pointer"
                style={{
                  animation: animated ? `fadeIn 0.3s ease-out ${0.8 + index * 0.1}s both` : 'none'
                }}
              >
                {showTooltip && (
                  <title>{`${point.label}: ${point.value}`}</title>
                )}
              </circle>
            );
          })}
        </svg>

        {/* Подписи */}
        <div className="flex justify-between mt-2 text-xs text-muted">
          <span>{min.toLocaleString()}</span>
          <span>{max.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
};

// Столбчатый график
export const BarChart: React.FC<ChartProps> = ({
  data,
  width = 400,
  height = 200,
  color = 'var(--color-secondary)',
  animated = true,
  isLoading = false,
  className = '',
  title,
  showTooltip = true
}) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (isLoading) {
    return <ChartSkeleton width={width} height={height} title={title} />;
  }

  const { min, max } = getMinMax(data);
  const range = max - min || 1;
  const barWidth = width / data.length * 0.8;
  const barSpacing = width / data.length * 0.2;

  return (
    <div className={`bg-background border border-border rounded-lg p-4 ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-primary mb-4">{title}</h3>
      )}
      
      <svg 
        width={width} 
        height={height}
        style={{ animation: mounted ? 'fadeIn 0.5s ease-out' : 'none' }}
      >
        {data.map((point, index) => {
          const barHeight = ((point.value - min) / range) * height;
          const x = index * (barWidth + barSpacing) + barSpacing / 2;
          const y = height - barHeight;
          
          return (
            <rect
              key={index}
              x={x}
              y={animated ? height : y}
              width={barWidth}
              height={animated ? 0 : barHeight}
              fill={color}
              className="opacity-80 hover:opacity-100 transition-opacity cursor-pointer"
              style={{
                animation: animated ? `slideUp 0.8s ease-out ${index * 0.1}s both` : 'none'
              }}
            >
              {showTooltip && (
                <title>{`${point.label}: ${point.value}`}</title>
              )}
            </rect>
          );
        })}
      </svg>

      {/* Подписи снизу */}
      <div className="flex justify-between mt-2 text-xs text-muted">
        {data.map((point, index) => (
          <span key={index} className="truncate" style={{ width: `${100 / data.length}%` }}>
            {point.label}
          </span>
        ))}
      </div>
    </div>
  );
};

// Area Chart (заполненный график)
export const AreaChart: React.FC<ChartProps> = ({
  data,
  width = 400,
  height = 200,
  color = 'var(--color-secondary)',
  animated = true,
  isLoading = false,
  className = '',
  title
}) => {
  if (isLoading) {
    return <ChartSkeleton width={width} height={height} title={title} />;
  }

  const path = getPath(data, width, height);
  const gradientId = `area-gradient-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className={`bg-background border border-border rounded-lg p-4 ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-primary mb-4">{title}</h3>
      )}
      
      <svg width={width} height={height}>
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style={{ stopColor: color, stopOpacity: 0.4 }} />
            <stop offset="100%" style={{ stopColor: color, stopOpacity: 0.1 }} />
          </linearGradient>
        </defs>

        {/* Заполненная область */}
        {path && (
          <path
            d={`${path} L ${width},${height} L 0,${height} Z`}
            fill={`url(#${gradientId})`}
            style={{
              animation: animated ? 'fadeIn 1s ease-out' : 'none'
            }}
          />
        )}

        {/* Линия границы */}
        {path && (
          <path
            d={path}
            fill="none"
            stroke={color}
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              strokeDasharray: animated ? '1000' : 'none',
              strokeDashoffset: animated ? '1000' : '0',
              animation: animated ? 'dashOffset 2s ease-out 0.5s both' : 'none'
            }}
          />
        )}
      </svg>
    </div>
  );
};

// Экспорт готовых компонентов для конкретных целей
export const BalanceChart = (props: Omit<ChartProps, 'color'>) => (
  <LineChart {...props} color="var(--color-success)" title="Динамика баланса" />
);

export const OrderChart = (props: Omit<ChartProps, 'color'>) => (
  <BarChart {...props} color="var(--color-secondary)" title="Заказы по дням" />
);

export const RevenueChart = (props: Omit<ChartProps, 'color'>) => (
  <AreaChart {...props} color="var(--color-tory-blue)" title="Выручка" />
); 