import React from 'react';

export default function SectionGrid({ title, subtitle, children, columns = 3 }) {
  const gridCols = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  };

  return (
    <div className="mb-12">
      {(title || subtitle) && (
        <div className="mb-6">
          {title && (
            <h2 className="text-xl font-bold text-gray-900 mb-2">{title}</h2>
          )}
          {subtitle && (
            <p className="text-sm text-gray-600">{subtitle}</p>
          )}
        </div>
      )}
      
      <div className={`grid ${gridCols[columns]} gap-6`}>
        {children}
      </div>
    </div>
  );
}
