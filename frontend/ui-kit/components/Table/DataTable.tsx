/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';

interface Column<T = any> {
  key: string;
  title: string;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: T) => React.ReactNode;
}

interface DataTableProps<T = any> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyText?: string;
}

export const DataTable = <T extends Record<string, any>>({ 
  columns, 
  data, 
  loading = false, 
  emptyText = 'Нет данных для отображения' 
}: DataTableProps<T>) => {
  if (loading) {
    return (
      <div className="bg-[var(--color-surface)] rounded-lg p-8 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-accent)]"></div>
        <p className="mt-2 text-[var(--color-secondary)]">Загрузка...</p>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-[var(--color-surface)] rounded-lg p-8 text-center">
        <p className="text-[var(--color-secondary)]">{emptyText}</p>
      </div>
    );
  }

  return (
    <div className="bg-[var(--color-surface)] rounded-lg overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-[var(--color-bg)] border-b border-[var(--color-border)]">
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`px-4 py-3 text-sm font-medium text-[var(--color-secondary)] ${
                    column.align === 'center' ? 'text-center' : 
                    column.align === 'right' ? 'text-right' : 'text-left'
                  }`}
                >
                  {column.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr
                key={index}
                className="border-b border-[var(--color-border)] hover:bg-[var(--color-bg)] transition-colors"
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className={`px-4 py-3 text-sm text-[var(--color-primary)] ${
                      column.align === 'center' ? 'text-center' : 
                      column.align === 'right' ? 'text-right' : 'text-left'
                    }`}
                  >
                    {column.render ? column.render(row[column.key], row) : row[column.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}; 