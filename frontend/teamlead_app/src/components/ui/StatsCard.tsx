interface StatsCardProps {
  title: string;
  value: string;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  subtitle?: string;
  icon?: React.ReactNode;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  trend = 'neutral',
  subtitle,
  icon
}) => {
  const getTrendColor = () => {
    switch (trend) {
      case 'up': return 'text-success';
      case 'down': return 'text-error';
      default: return 'text-secondary';
    }
  };

  const getTrendIcon = () => {
    if (!change || trend === 'neutral') return null;
    
    return trend === 'up' ? (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 14l9-9 9 9" />
      </svg>
    ) : (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 10l-9 9-9-9" />
      </svg>
    );
  };

  return (
    <div className="card-base p-6 animate-fadeIn">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-secondary">{title}</h3>
        {icon && (
          <div className="p-2 bg-surface rounded-lg text-primary">
            {icon}
          </div>
        )}
      </div>
      
      <div className="space-y-2">
        <div className="text-2xl font-bold text-primary">{value}</div>
        
        {(change || subtitle) && (
          <div className="flex items-center justify-between">
            {change && (
              <div className={`flex items-center gap-1 text-sm ${getTrendColor()}`}>
                {getTrendIcon()}
                <span>{change}</span>
              </div>
            )}
            {subtitle && (
              <div className="text-xs text-secondary">{subtitle}</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}; 