'use client';

import React from 'react';
import { StatsCard } from '@jivapay/ui-kit';

export interface MetricItem {
  id: string;
  title: string;
  value: string;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  subtitle?: string;
  icon?: React.ReactNode;
  link?: string;
  permission?: string;
}

interface MetricsGridProps {
  metrics: MetricItem[];
  columns?: 2 | 3 | 4;
  className?: string;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ 
  metrics, 
  columns = 4, 
  className = '' 
}) => {
  const gridClass = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  }[columns];

  return (
    <div className={`grid ${gridClass} gap-6 ${className}`}>
      {metrics.map((metric) => {
        const cardContent = (
          <StatsCard
            key={metric.id}
            title={metric.title}
            value={metric.value}
            change={metric.change}
            trend={metric.trend}
            subtitle={metric.subtitle}
            icon={metric.icon}
          />
        );

        // Если есть ссылка, оборачиваем в Link или a
        if (metric.link) {
          return (
            <a 
              key={metric.id} 
              href={metric.link} 
              className="block hover:scale-105 transition-transform"
            >
              {cardContent}
            </a>
          );
        }

        return cardContent;
      })}
    </div>
  );
}; 