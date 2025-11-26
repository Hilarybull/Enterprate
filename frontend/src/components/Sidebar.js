import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Lightbulb,
  Globe,
  FileText,
  BookOpen,
  DollarSign,
  Briefcase,
  TrendingUp,
  Network
} from 'lucide-react';

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/idea-discovery', icon: Lightbulb, label: 'Idea Discovery & Validation' },
  { path: '/website-setup', icon: Globe, label: 'Website & Business Setup' },
  { path: '/business-registration', icon: FileText, label: 'Business Registration Companion' },
  { path: '/business-blueprint', icon: BookOpen, label: 'Business Blueprint Generation' },
  { path: '/finance-automation', icon: DollarSign, label: 'Finance Automation' },
  { path: '/business-operations', icon: Briefcase, label: 'Business Operations' },
  { path: '/growth', icon: TrendingUp, label: 'Growth' },
  { path: '/intelligence-graph', icon: Network, label: 'Intelligence Graph' }
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-0 h-screen w-[280px] bg-white border-r border-gray-200 overflow-y-auto">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">E</span>
          </div>
          <span className="text-xl font-bold text-gray-900">EnterprateAI</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200
                ${
                  isActive
                    ? 'bg-purple-100 text-purple-600 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                }
              `}
            >
              <Icon size={20} className="flex-shrink-0" />
              <span className="text-sm leading-tight">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
