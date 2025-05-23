import React from 'react';

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  subtitle?: string;
  icon?: React.ReactNode;
  className?: string;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  trend = 'neutral',
  subtitle,
  icon,
  className = ''
}) => {
  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'text-[var(--color-success)]';
      case 'down':
        return 'text-[var(--color-error)]';
      default:
        return 'text-[var(--color-secondary)]';
    }
  };

  const getIconBackground = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'bg-[var(--color-success-light)]';
      case 'down':
        return 'bg-[var(--color-error-light)]';
      default:
        return 'bg-[var(--color-info-light)]';
    }
  };

  const getIconColor = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'text-[var(--color-success-text)]';
      case 'down':
        return 'text-[var(--color-error-text)]';
      default:
        return 'text-[var(--color-info-text)]';
    }
  };

  return (
    <div className={`bg-[var(--color-surface)] rounded-lg p-6 shadow-sm ${className}`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <p className="text-[var(--color-secondary)] text-sm mb-2">{title}</p>
          <p className="text-3xl font-bold text-[var(--color-primary)] mb-2">{value}</p>
          
          {(change || subtitle) && (
            <div className="flex items-center gap-2 text-sm">
              {change && (
                <span className={`font-medium ${getTrendColor(trend)}`}>
                  {change}
                </span>
              )}
              {subtitle && (
                <span className="text-[var(--color-secondary)]">
                  {subtitle}
                </span>
              )}
            </div>
          )}
        </div>
        
        {icon && (
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getIconBackground(trend)}`}>
            <div className={getIconColor(trend)}>
              {icon}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}; 