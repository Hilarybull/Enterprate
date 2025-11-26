import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function StatsCard({ 
  title, 
  value, 
  change,
  changeType = 'neutral', // 'positive', 'negative', 'neutral'
  icon: Icon,
  gradient = 'gradient-primary',
  to,
  subtitle
}) {
  const CardWrapper = to ? Link : 'div';
  const cardProps = to ? { to } : {};

  const changeColors = {
    positive: 'text-green-600 bg-green-50',
    negative: 'text-red-600 bg-red-50',
    neutral: 'text-gray-600 bg-gray-100'
  };

  return (
    <CardWrapper
      {...cardProps}
      className={`
        enterprise-card p-6
        ${to ? 'enterprise-card-interactive cursor-pointer' : ''}
      `}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
          {change && (
            <div className={`inline-flex items-center mt-2 px-2 py-0.5 rounded-full text-xs font-medium ${changeColors[changeType]}`}>
              {changeType === 'positive' && <ArrowUpRight size={12} className="mr-1" />}
              {changeType === 'negative' && <ArrowDownRight size={12} className="mr-1" />}
              {change}
            </div>
          )}
        </div>
        {Icon && (
          <div className={`w-12 h-12 rounded-xl ${gradient} flex items-center justify-center`}>
            <Icon className="text-white" size={22} />
          </div>
        )}
      </div>
    </CardWrapper>
  );
}
