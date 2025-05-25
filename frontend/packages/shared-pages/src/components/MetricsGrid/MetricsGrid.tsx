'use client';

import React from 'react';
import { StatsCard, Skeleton } from '@jivapay/ui-kit';

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
  isLoading?: boolean;
  skeletonCount?: number;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ 
  metrics, 
  columns = 4, 
  className = '',
  isLoading = false,
  skeletonCount = 4
}) => {
  const gridClass = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  }[columns];

  // Skeleton состояние при загрузке
  if (isLoading) {
    return (
      <div className={`grid ${gridClass} gap-6 animate-fadeIn ${className}`}>
        {Array.from({ length: skeletonCount }, (_, index) => (
          <Skeleton 
            key={`skeleton-${index}`}
            variant="card" 
            className="h-32"
            animation="pulse"
          />
        ))}
      </div>
    );
  }

  return (
    <div className={`grid ${gridClass} gap-6 animate-fadeIn ${className}`}>
      {metrics.map((metric, index) => {
        const cardContent = (
          <div
            key={metric.id}
            className="animate-fadeIn"
            style={{ 
              animationDelay: `${index * 100}ms`,
              animationFillMode: 'both'
            }}
          >
            <StatsCard
              title={metric.title}
              value={metric.value}
              change={metric.change}
              trend={metric.trend}
              subtitle={metric.subtitle}
              icon={metric.icon}
              animateValue={true}
            />
          </div>
        );

        // Если есть ссылка, оборачиваем в Link или a
        if (metric.link) {
          return (
            <a 
              key={metric.id} 
              href={metric.link} 
              className="block hover:scale-[1.02] transition-all duration-200 animated-transition hover:shadow-lg"
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