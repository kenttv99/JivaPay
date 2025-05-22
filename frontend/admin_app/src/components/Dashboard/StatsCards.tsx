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
    <div className={`bg-[var(--jiva-background-paper)] rounded-lg p-4 shadow-sm relative ${className || ''}`}>
      <div className="space-y-1">
        <p className="text-sm font-medium text-[var(--jiva-text-secondary)]">{title}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
      <div className="absolute top-4 right-4 rounded-full p-2 bg-[var(--jiva-background)]">
        {icon}
      </div>
      <p className="mt-2 text-xs text-[var(--jiva-text-secondary)]">{description}</p>
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
    <div className="bg-[var(--jiva-background-paper)] rounded-lg p-5 shadow-sm">
      <div className="mb-3">
        <h3 className="text-lg font-medium">{title}</h3>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex-shrink-0 rounded-full bg-[var(--jiva-background)] p-3">
            {icon}
          </div>
          <div>
            <p className="text-3xl font-bold text-[var(--jiva-primary)]">{value}</p>
            <p className="text-sm text-[var(--jiva-text-secondary)]">{description}</p>
          </div>
        </div>
      </div>
    </div>
  );
}; 