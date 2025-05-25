import React, { useState, useEffect } from 'react';

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  subtitle?: string;
  icon?: React.ReactNode;
  isLoading?: boolean;
  animateValue?: boolean;
  onClick?: () => void;
  className?: string;
}

// Хук для анимации чисел
const useCountUp = (end: number, duration: number = 2000, shouldAnimate: boolean = true) => {
  const [count, setCount] = useState(shouldAnimate ? 0 : end);

  useEffect(() => {
    if (!shouldAnimate) {
      setCount(end);
      return;
    }

    let startTime: number;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      // Easing function for smooth animation
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(end * easeOutQuart));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration, shouldAnimate]);

  return count;
};

// Skeleton компонент для StatsCard
const StatsCardSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`bg-background rounded-lg p-6 shadow-sm border border-border ${className}`}>
    <div className="flex justify-between items-start">
      <div className="flex-1 space-y-3">
        <div className="h-4 w-24 bg-muted rounded animate-pulse" />
        <div className="h-8 w-32 bg-muted rounded animate-pulse" />
        <div className="h-3 w-20 bg-muted rounded animate-pulse" />
      </div>
      <div className="w-12 h-12 bg-muted rounded-lg animate-pulse" />
    </div>
  </div>
);

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  trend = 'neutral',
  subtitle,
  icon,
  isLoading = false,
  animateValue = true,
  onClick,
  className = ''
}) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Парсим числовое значение для анимации
  const numericValue = typeof value === 'number' ? value : parseFloat(String(value).replace(/[^0-9.-]/g, ''));
  const isNumeric = !isNaN(numericValue);
  const animatedValue = useCountUp(numericValue, 2000, mounted && animateValue && isNumeric);

  // Форматируем значение обратно
  const displayValue = isNumeric && animateValue ? 
    String(value).replace(String(numericValue), String(animatedValue)) : 
    value;

  const trendColors = {
    up: 'text-success',
    down: 'text-error', 
    neutral: 'text-neutral'
  };
  
  const iconBackgrounds = {
    up: 'bg-gradient-to-br from-success-light to-success/10',
    down: 'bg-gradient-to-br from-error-light to-error/10',
    neutral: 'bg-gradient-to-br from-info-light to-info/10'
  };

  const iconTextColors = {
    up: 'text-success',
    down: 'text-error',
    neutral: 'text-info'
  };

  const trendIcons = {
    up: (
      <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
      </svg>
    ),
    down: (
      <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M14.707 12.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
      </svg>
    ),
    neutral: null
  };

  // Показываем skeleton при загрузке
  if (isLoading) {
    return <StatsCardSkeleton className={className} />;
  }

  const cardClasses = `
    bg-background border border-border rounded-lg p-6 shadow-sm 
    transition-all duration-200 animated-transition
    hover:shadow-md hover:border-primary/20 hover:-translate-y-0.5
    ${onClick ? 'cursor-pointer hover:bg-surface/50' : ''}
    ${className}
  `;

  return (
    <div 
      className={cardClasses}
      onClick={onClick}
      style={{ animation: mounted ? 'fadeIn 0.5s ease-out' : 'none' }}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <p className="text-muted text-sm mb-2 font-medium">{title}</p>
          <div 
            className="text-3xl font-bold text-primary mb-2"
            style={{ animation: mounted && animateValue ? 'countUp 0.5s ease-out' : 'none' }}
          >
            {displayValue}
          </div>
          
          {(change || subtitle) && (
            <div className="flex items-center gap-2 text-sm">
              {change && (
                <span className={`flex items-center gap-1 font-medium px-2 py-1 rounded-full ${
                  trend === 'up' ? 'bg-success-light text-success' :
                  trend === 'down' ? 'bg-error-light text-error' :
                  'bg-neutral-light text-neutral'
                }`}>
                  {trendIcons[trend]}
                  {change}
                </span>
              )}
              {subtitle && (
                <span className="text-muted">
                  {subtitle}
                </span>
              )}
            </div>
          )}
        </div>
        
        {icon && (
          <div className={`
            w-12 h-12 rounded-lg flex items-center justify-center 
            ${iconBackgrounds[trend]}
            transition-all duration-200 animated-transition
            hover:scale-110
          `}>
            <div className={`${iconTextColors[trend]} transition-colors duration-200`}>
              {icon}
            </div>
          </div>
        )}
      </div>

      {/* Декоративный градиент снизу */}
      {trend !== 'neutral' && (
        <div className={`
          absolute bottom-0 left-0 right-0 h-1 rounded-b-lg 
          ${trend === 'up' ? 'bg-gradient-to-r from-success/20 via-success to-success/20' :
            'bg-gradient-to-r from-error/20 via-error to-error/20'}
        `} />
      )}
    </div>
  );
}; 