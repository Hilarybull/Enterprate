import React from 'react';

export default function PageHeader({ 
  title, 
  description, 
  icon: Icon,
  actions,
  breadcrumbs
}) {
  return (
    <div className="mb-8">
      {/* Breadcrumbs */}
      {breadcrumbs && (
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          {breadcrumbs.map((crumb, i) => (
            <React.Fragment key={i}>
              {i > 0 && <span>/</span>}
              <span className={i === breadcrumbs.length - 1 ? 'text-gray-900' : ''}>
                {crumb}
              </span>
            </React.Fragment>
          ))}
        </div>
      )}

      {/* Main Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-4">
          {Icon && (
            <div className="w-14 h-14 rounded-2xl gradient-primary flex items-center justify-center shadow-lg shadow-purple-500/25">
              <Icon className="text-white" size={28} />
            </div>
          )}
          <div>
            <h1 
              className="text-2xl lg:text-3xl font-bold text-gray-900" 
              style={{ fontFamily: 'Space Grotesk' }}
            >
              {title}
            </h1>
            {description && (
              <p className="text-gray-500 mt-1">{description}</p>
            )}
          </div>
        </div>

        {/* Actions */}
        {actions && (
          <div className="flex items-center space-x-3">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
