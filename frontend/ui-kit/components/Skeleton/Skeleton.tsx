import React from 'react';

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'rectangular' | 'circular' | 'rounded' | 'card' | 'avatar' | 'table-row';
  animation?: 'pulse' | 'wave' | 'none';
  className?: string;
  count?: number;
  lines?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height,
  variant = 'rectangular',
  animation = 'pulse',
  className = '',
  count = 1,
  lines = 1
}) => {
  const getVariantClasses = (variant: string) => {
    switch (variant) {
      case 'text':
        return 'h-4 rounded';
      case 'circular':
        return 'rounded-full';
      case 'rounded':
        return 'rounded-lg';
      case 'card':
        return 'rounded-lg h-48';
      case 'avatar':
        return 'rounded-full w-10 h-10';
      case 'table-row':
        return 'rounded h-12';
      default:
        return 'rounded';
    }
  };

  const getAnimationClasses = (animation: string) => {
    switch (animation) {
      case 'wave':
        return 'animate-pulse'; // Используем стандартную pulse анимацию
      case 'pulse':
        return 'animate-pulse';
      default:
        return '';
    }
  };

  const getDefaultDimensions = (variant: string) => {
    switch (variant) {
      case 'text':
        return { width: '100%', height: '1rem' };
      case 'avatar':
        return { width: '2.5rem', height: '2.5rem' };
      case 'card':
        return { width: '100%', height: '12rem' };
      case 'table-row':
        return { width: '100%', height: '3rem' };
      default:
        return { width: '100%', height: '1.5rem' };
    }
  };

  const defaults = getDefaultDimensions(variant);
  const finalWidth = width || defaults.width;
  const finalHeight = height || defaults.height;

  // Компонент для одного skeleton
  const SingleSkeleton = ({ index = 0 }: { index?: number }) => (
    <div
      className={`
        bg-muted ${getVariantClasses(variant)} ${getAnimationClasses(animation)}
        ${className}
      `}
      style={{
        width: finalWidth,
        height: finalHeight,
        animationDelay: `${index * 100}ms`
      }}
    />
  );

  // Компонент для текстовых строк
  const TextSkeleton = () => (
    <div className="space-y-2">
      {Array.from({ length: lines }, (_, index) => {
        const lineWidth = index === lines - 1 && lines > 1 
          ? `${Math.random() * 40 + 40}%` 
          : '100%';
        return (
          <div
            key={index}
            className={`h-4 bg-muted rounded ${getAnimationClasses(animation)}`}
            style={{
              width: lineWidth,
              animationDelay: `${index * 50}ms`
            }}
          />
        );
      })}
    </div>
  );

  // Компонент карточки
  const CardSkeleton = () => (
    <div className="bg-background border border-border rounded-lg p-4 space-y-3">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-muted rounded-full animate-pulse" />
        <div className="space-y-2 flex-1">
          <div className="h-4 bg-muted rounded animate-pulse" style={{ width: '60%' }} />
          <div className="h-3 bg-muted rounded animate-pulse" style={{ width: '40%' }} />
        </div>
      </div>
      <div className="space-y-2">
        <div className="h-4 bg-muted rounded animate-pulse" />
        <div className="h-4 bg-muted rounded animate-pulse" style={{ width: '80%' }} />
        <div className="h-4 bg-muted rounded animate-pulse" style={{ width: '60%' }} />
      </div>
    </div>
  );

  // Компонент строки таблицы
  const TableRowSkeleton = () => (
    <tr className="border-b border-border">
      {Array.from({ length: 4 }, (_, index) => (
        <td key={index} className="px-4 py-3">
          <div 
            className="h-4 bg-muted rounded animate-pulse" 
            style={{ 
              width: `${Math.random() * 40 + 40}%`,
              animationDelay: `${index * 100}ms`
            }} 
          />
        </td>
      ))}
    </tr>
  );

  // Специальные случаи
  if (variant === 'text' && lines > 1) {
    return count > 1 ? (
      <div className="space-y-4">
        {Array.from({ length: count }, (_, index) => (
          <TextSkeleton key={index} />
        ))}
      </div>
    ) : (
      <TextSkeleton />
    );
  }

  if (variant === 'card') {
    return count > 1 ? (
      <div className="grid gap-4">
        {Array.from({ length: count }, (_, index) => (
          <CardSkeleton key={index} />
        ))}
      </div>
    ) : (
      <CardSkeleton />
    );
  }

  if (variant === 'table-row') {
    return (
      <>
        {Array.from({ length: count }, (_, index) => (
          <TableRowSkeleton key={index} />
        ))}
      </>
    );
  }

  // Обычный skeleton с count
  if (count > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: count }, (_, index) => (
          <SingleSkeleton key={index} index={index} />
        ))}
      </div>
    );
  }

  return <SingleSkeleton />;
}; 