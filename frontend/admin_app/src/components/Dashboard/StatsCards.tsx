'use client';

interface StatCardProps {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
  className?: string;
}

export const StatCard = ({ title, value, description, icon, className }: StatCardProps) => {
  return (
    <div className={`bg-surface rounded-lg p-4 shadow-sm relative ${className || ''}`}>
      <div className="space-y-1">
        <p className="text-sm font-medium text-secondary">{title}</p>
        <p className="text-2xl font-bold text-primary">{value}</p>
      </div>
      <div className="absolute top-4 right-4 rounded-full p-2 bg-background">
        {icon}
      </div>
      <p className="mt-2 text-xs text-secondary">{description}</p>
    </div>
  );
};

interface StatsInfoCardProps {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
}

export const StatsInfoCard = ({ title, value, description, icon }: StatsInfoCardProps) => {
  return (
    <div className="bg-surface rounded-lg p-5 shadow-sm">
      <div className="mb-3">
        <h3 className="text-lg font-medium text-primary">{title}</h3>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex-shrink-0 rounded-full bg-background p-3">
            {icon}
          </div>
          <div>
            <p className="text-3xl font-bold text-primary">{value}</p>
            <p className="text-sm text-secondary">{description}</p>
          </div>
        </div>
      </div>
    </div>
  );
}; 