import React from 'react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'accent';
  className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className = ''
}) => {
  const getSizeClasses = (size: string) => {
    switch (size) {
      case 'sm':
        return 'w-4 h-4 border-2';
      case 'lg':
        return 'w-8 h-8 border-4';
      default:
        return 'w-6 h-6 border-2';
    }
  };

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'secondary':
        return 'border-[var(--color-secondary)] border-t-transparent';
      case 'accent':
        return 'border-[var(--color-accent)] border-t-transparent';
      default:
        return 'border-[var(--color-primary)] border-t-transparent';
    }
  };

  return (
    <div
      className={`animate-spin rounded-full ${getSizeClasses(size)} ${getColorClasses(color)} ${className}`}
      role="status"
      aria-label="Загрузка"
    >
      <span className="sr-only">Загрузка...</span>
    </div>
  );
}; 