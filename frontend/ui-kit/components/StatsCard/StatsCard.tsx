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
  const trendColors = {
    up: 'text-success',
    down: 'text-error', 
    neutral: 'text-secondary'
  };
  
  const iconBackgrounds = {
    up: 'bg-success-light',
    down: 'bg-error-light',
    neutral: 'bg-info-light'
  };

  const iconTextColors = {
    up: 'text-success-text',
    down: 'text-error-text',
    neutral: 'text-info-text'
  };

  return (
    <div className={`bg-surface rounded-lg p-6 shadow-sm border border-border ${className}`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <p className="text-secondary text-sm mb-2">{title}</p>
          <p className="text-3xl font-bold text-primary mb-2">{value}</p>
          
          {(change || subtitle) && (
            <div className="flex items-center gap-2 text-sm">
              {change && (
                <span className={`font-medium ${trendColors[trend]}`}>
                  {change}
                </span>
              )}
              {subtitle && (
                <span className="text-secondary">
                  {subtitle}
                </span>
              )}
            </div>
          )}
        </div>
        
        {icon && (
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${iconBackgrounds[trend]}`}>
            <div className={iconTextColors[trend]}>
              {icon}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}; 