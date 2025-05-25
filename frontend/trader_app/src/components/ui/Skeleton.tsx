interface SkeletonProps {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '' }) => {
  return (
    <div 
      className={`animate-pulse bg-surface rounded ${className}`}
      style={{ backgroundColor: 'hsl(var(--muted))' }}
    />
  );
}; 