import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export default function FeatureCard({ 
  title, 
  description, 
  icon: Icon, 
  to,
  gradient = 'gradient-primary',
  stats,
  action,
  children,
  className = ''
}) {
  const CardWrapper = to ? Link : 'div';
  const cardProps = to ? { to } : {};

  return (
    <CardWrapper
      {...cardProps}
      className={`
        enterprise-card enterprise-card-interactive
        p-6 block
        ${to ? 'cursor-pointer' : ''}
        ${className}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl ${gradient} flex items-center justify-center shadow-lg`}>
          {Icon && <Icon className="text-white" size={24} />}
        </div>
        {to && (
          <ArrowRight size={18} className="text-gray-400 group-hover:text-purple-600 transition-colors" />
        )}
      </div>

      {/* Content */}
      <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-500 mb-4">{description}</p>

      {/* Stats */}
      {stats && (
        <div className="flex items-center space-x-4 mb-4">
          {stats.map((stat, i) => (
            <div key={i}>
              <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
              <div className="text-xs text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Custom Children */}
      {children}

      {/* Action */}
      {action && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          {action}
        </div>
      )}
    </CardWrapper>
  );
}
