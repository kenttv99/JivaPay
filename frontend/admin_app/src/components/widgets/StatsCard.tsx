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
        return 'text-[var(--jiva-success)]';
      case 'down':
        return 'text-[var(--jiva-error)]';
      default:
        return 'text-[var(--jiva-text-secondary)]';
    }
  };

  const getIconBackground = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'bg-green-100';
      case 'down':
        return 'bg-red-100';
      default:
        return 'bg-blue-100';
    }
  };

  const getIconColor = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-blue-600';
    }
  };

  return (
    <div className={`bg-[var(--jiva-background-paper)] rounded-lg p-6 shadow-sm ${className}`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <p className="text-[var(--jiva-text-secondary)] text-sm mb-2">{title}</p>
          <p className="text-3xl font-bold text-[var(--jiva-text-primary)] mb-2">{value}</p>
          
          {(change || subtitle) && (
            <div className="flex items-center gap-2 text-sm">
              {change && (
                <span className={`font-medium ${getTrendColor(trend)}`}>
                  {change}
                </span>
              )}
              {subtitle && (
                <span className="text-[var(--jiva-text-secondary)]">
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