import React from 'react';

interface Column<T> {
  header: string;
  render: (item: T) => React.ReactNode;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  title?: string;
  emptyMessage?: string;
}

export default function DataTable<T>({ data, columns, title, emptyMessage = "No data available" }: DataTableProps<T>) {
  return (
    <div className="glass rounded-2xl border border-slate-700/50 overflow-hidden">
      {title && (
        <div className="px-6 py-4 border-b border-slate-700/50">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-slate-900/50 border-b border-slate-800">
            <tr>
              {columns.map((col, idx) => (
                <th key={idx} className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {data.length > 0 ? (
              data.map((item, rowIdx) => (
                <tr key={rowIdx} className="hover:bg-slate-800/30 transition-colors">
                  {columns.map((col, colIdx) => (
                    <td key={colIdx} className="px-6 py-4 text-sm text-slate-300">
                      {col.render(item)}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="px-6 py-12 text-center text-slate-500 italic">
                  {emptyMessage}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
