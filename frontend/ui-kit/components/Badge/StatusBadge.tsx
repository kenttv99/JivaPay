import React from 'react';

interface StatusBadgeProps {
  status: 'active' | 'inactive' | 'blocked' | 'pending' | 'success' | 'processing' | 'failed';
  children?: React.ReactNode;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, children }) => {
  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'active':
      case 'success':
        return 'bg-[var(--color-success-light)] text-[var(--color-success-text)]';
      case 'inactive':
      case 'blocked':
      case 'failed':
        return 'bg-[var(--color-error-light)] text-[var(--color-error-text)]';
      case 'pending':
      case 'processing':
        return 'bg-[var(--color-warning-light)] text-[var(--color-warning-text)]';
      default:
        return 'bg-[var(--color-neutral-light)] text-[var(--color-neutral-text)]';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'Активен';
      case 'inactive':
        return 'Неактивен';
      case 'blocked':
        return 'Заблокирован';
      case 'pending':
        return 'Ожидает';
      case 'success':
        return 'Успешно';
      case 'processing':
        return 'В процессе';
      case 'failed':
        return 'Ошибка';
      default:
        return status;
    }
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusStyle(status)}`}>
      {children || getStatusText(status)}
    </span>
  );
}; 