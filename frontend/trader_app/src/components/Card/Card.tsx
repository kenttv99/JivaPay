import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'dark';
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  variant = 'default',
  ...props
}) => {
  const baseClasses = 'rounded-lg shadow-md p-8 transition-all duration-200';
  
  const variants = {
    default: 'bg-surface text-primary',
    glass: 'bg-white/15 backdrop-blur-sm border border-white/20 text-primary',
    dark: 'bg-background text-primary'
  };

  return (
    <div 
      className={`${baseClasses} ${variants[variant]} ${className}`} 
      {...props}
    >
      {children}
    </div>
  );
}; 