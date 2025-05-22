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
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-8 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--jiva-primary)]"></div>
        <p className="mt-2 text-[var(--jiva-text-secondary)]">Загрузка...</p>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-[var(--jiva-background-paper)] rounded-lg p-8 text-center">
        <p className="text-[var(--jiva-text-secondary)]">{emptyText}</p>
      </div>
    );
  }

  return (
    <div className="bg-[var(--jiva-background-paper)] rounded-lg overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-[var(--jiva-background)] border-b border-[var(--jiva-border)]">
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`px-4 py-3 text-sm font-medium text-[var(--jiva-text-secondary)] ${
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
                className="border-b border-[var(--jiva-border)] hover:bg-[var(--jiva-background)] transition-colors"
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className={`px-4 py-3 text-sm ${
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