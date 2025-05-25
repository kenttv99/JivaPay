/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState, useMemo } from 'react';

interface Column<T = any> {
  key: string;
  title: string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
  width?: string;
}

interface DataTableProps<T = any> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyText?: string;
  onRowClick?: (row: T, index: number) => void;
  selectedRows?: (string | number)[];
  rowKeyField?: string;
  className?: string;
}

// Skeleton компонент для загрузки таблицы
const TableSkeleton: React.FC<{ columns: Column[]; rowCount?: number }> = ({ 
  columns, 
  rowCount = 5 
}) => (
  <div className="bg-background rounded-lg overflow-hidden shadow-sm border border-border">
    <div className="overflow-x-auto">
      <table className="w-full text-left">
        <thead>
          <tr className="bg-surface border-b border-border">
            {columns.map((column) => (
              <th key={column.key} className="px-4 py-3">
                <div className="h-4 bg-muted rounded animate-pulse" style={{ width: '60%' }} />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {[...Array(rowCount)].map((_, index) => (
            <tr key={index} className="border-b border-border">
              {columns.map((column) => (
                <td key={column.key} className="px-4 py-3">
                  <div 
                    className="h-4 bg-muted rounded animate-pulse" 
                    style={{ 
                      width: Math.random() * 40 + 40 + '%',
                      animationDelay: `${index * 100 + Math.random() * 200}ms`
                    }} 
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export const DataTable = <T extends Record<string, any>>({ 
  columns, 
  data, 
  loading = false, 
  emptyText = 'Нет данных для отображения',
  onRowClick,
  selectedRows = [],
  rowKeyField = 'id',
  className = ''
}: DataTableProps<T>) => {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);

  // Сортировка данных
  const sortedData = useMemo(() => {
    if (!sortConfig) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [data, sortConfig]);

  // Обработка сортировки
  const handleSort = (key: string) => {
    setSortConfig(current => {
      if (current?.key === key) {
        return current.direction === 'asc' 
          ? { key, direction: 'desc' }
          : null;
      }
      return { key, direction: 'asc' };
    });
  };

  // Иконка сортировки
  const SortIcon: React.FC<{ column: Column; sortConfig: { key: string; direction: 'asc' | 'desc' } | null }> = ({ column, sortConfig }) => {
    if (!column.sortable) return null;

    const isActive = sortConfig?.key === column.key;
    const direction = sortConfig?.direction;

    return (
      <span className="ml-1 inline-flex flex-col">
        <svg 
          className={`h-3 w-3 transition-colors ${
            isActive && direction === 'asc' ? 'text-secondary' : 'text-muted'
          }`}
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fillRule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
        </svg>
        <svg 
          className={`h-3 w-3 -mt-1 transition-colors ${
            isActive && direction === 'desc' ? 'text-secondary' : 'text-muted'
          }`}
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fillRule="evenodd" d="M14.707 12.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      </span>
    );
  };

  // Проверка выбранной строки
  const isRowSelected = (row: T) => {
    const rowKey = row[rowKeyField];
    return selectedRows.includes(String(rowKey));
  };

  // Показываем skeleton при загрузке
  if (loading) {
    return <TableSkeleton columns={columns} />;
  }

  // Пустое состояние
  if (!data || data.length === 0) {
    return (
      <div className="bg-background rounded-lg p-8 text-center border border-border">
        <div className="max-w-sm mx-auto">
          <svg 
            className="h-12 w-12 text-muted mx-auto mb-4" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-muted font-medium">{emptyText}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-background rounded-lg overflow-hidden shadow-sm border border-border animate-fadeIn ${className}`}>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-surface border-b border-border">
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`px-4 py-3 text-sm font-semibold text-primary ${
                    column.align === 'center' ? 'text-center' : 
                    column.align === 'right' ? 'text-right' : 'text-left'
                  } ${column.sortable ? 'cursor-pointer hover:bg-muted/50 transition-colors select-none' : ''}`}
                  style={{ width: column.width }}
                  onClick={() => column.sortable && handleSort(column.key)}
                >
                  <div className="flex items-center justify-between">
                    <span>{column.title}</span>
                    <SortIcon column={column} sortConfig={sortConfig} />
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, index) => {
              const isSelected = isRowSelected(row);
              return (
                <tr
                  key={row[rowKeyField] || index}
                  className={`
                    border-b border-border transition-all duration-200 animated-transition
                    ${onRowClick ? 'cursor-pointer' : ''}
                    ${isSelected 
                      ? 'bg-secondary/10 border-secondary/20' 
                      : 'hover:bg-surface/80'
                    }
                    hover:shadow-sm
                  `}
                  onClick={() => onRowClick?.(row, index)}
                  style={{ 
                    animation: `fadeIn 0.3s ease-out ${index * 50}ms both`
                  }}
                >
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={`px-4 py-3 text-sm ${
                        column.align === 'center' ? 'text-center' : 
                        column.align === 'right' ? 'text-right' : 'text-left'
                      } ${isSelected ? 'text-primary font-medium' : 'text-primary'}`}
                    >
                      {column.render ? column.render(row[column.key], row) : row[column.key]}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Индикатор количества записей */}
      <div className="px-4 py-3 bg-surface/50 border-t border-border text-sm text-muted">
        Показано {sortedData.length} записей
        {sortConfig && (
          <span className="ml-2 text-xs">
            • Сортировка по "{columns.find(c => c.key === sortConfig.key)?.title}" 
            ({sortConfig.direction === 'asc' ? 'по возрастанию' : 'по убыванию'})
          </span>
        )}
      </div>
    </div>
  );
}; 