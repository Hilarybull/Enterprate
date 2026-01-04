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
  Palette,
  FolderOpen,
  Settings,
  HelpCircle,
  Users,
  FlaskConical,
  Zap,
  BarChart3
} from 'lucide-react';

const navItems = [
  { 
    path: '/dashboard', 
    icon: LayoutDashboard, 
    label: 'Dashboard',
    description: 'Overview & analytics'
  },
  { 
    path: '/idea-discovery', 
    icon: Lightbulb, 
    label: 'Idea Discovery',
    description: 'Validate business ideas'
  },
  { 
    path: '/business-registration', 
    icon: FileText, 
    label: 'Business Registration Companion',
    description: 'Legal & compliance'
  },
  { 
    path: '/branding', 
    icon: Palette, 
    label: 'Branding',
    description: 'Visual identity & assets'
  },
  { 
    path: '/ai-website-builder', 
    icon: Globe, 
    label: 'AI Website Builder',
    description: 'Generate landing pages with AI'
  },
  { 
    path: '/website-analytics', 
    icon: BarChart3, 
    label: 'Website Analytics',
    description: 'Track visits & conversions'
  },
  { 
    path: '/business-blueprint', 
    icon: BookOpen, 
    label: 'Business Blueprint Generator',
    description: 'Strategic planning'
  },
  { 
    path: '/finance-automation', 
    icon: DollarSign, 
    label: 'Finance',
    description: 'Invoicing & accounting'
  },
  { 
    path: '/business-operations', 
    icon: Briefcase, 
    label: 'Operations',
    description: 'Process management'
  },
  { 
    path: '/growth', 
    icon: TrendingUp, 
    label: 'Growth',
    description: 'Marketing & sales'
  },
  { 
    path: '/team', 
    icon: Users, 
    label: 'Team',
    description: 'Collaboration & roles'
  },
  { 
    path: '/ab-testing', 
    icon: FlaskConical, 
    label: 'A/B Testing',
    description: 'Optimize campaigns'
  },
  { 
    path: '/automation', 
    icon: Zap, 
    label: 'Automation',
    description: 'Campaign automation rules'
  },
  { 
    path: '/resources', 
    icon: FolderOpen, 
    label: 'Business Resources Hub',
    description: 'Tools & templates'
  }
];

const bottomItems = [
  { path: '/settings', icon: Settings, label: 'Settings' },
  { path: '/help', icon: HelpCircle, label: 'Help & Support' }
];

export default function EnterpriseSidebar({ isOpen, onClose }) {
  const location = useLocation();

  return (
    <aside
      className={`
        fixed top-0 left-0 z-40 h-screen w-[280px] 
        bg-white border-r border-gray-200
        transform transition-transform duration-300 ease-in-out
        lg:translate-x-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        flex flex-col
      `}
    >
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-gray-200">
        <Link to="/dashboard" className="flex items-center" onClick={onClose}>
          <img 
            src="https://customer-assets.emergentagent.com/job_saas-dashboard-20/artifacts/aems110l_Enterprate%20Logo.png" 
            alt="Enterprate" 
            className="h-9"
          />
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3">
        <div className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={onClose}
                data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                className={`
                  flex items-center px-3 py-2.5 rounded-lg transition-all duration-200
                  group relative
                  ${isActive
                    ? 'bg-purple-50 text-purple-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
              >
                <div className={`
                  w-9 h-9 rounded-lg flex items-center justify-center mr-3
                  transition-all duration-200
                  ${isActive 
                    ? 'bg-purple-100' 
                    : 'bg-gray-100 group-hover:bg-gray-200'
                  }
                `}>
                  <Icon 
                    size={18} 
                    className={isActive ? 'text-purple-600' : 'text-gray-500 group-hover:text-gray-700'} 
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <span className={`text-sm font-medium block truncate ${isActive ? 'text-purple-700' : ''}`}>
                    {item.label}
                  </span>
                  <span className="text-xs text-gray-400 truncate block">
                    {item.description}
                  </span>
                </div>
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-purple-600 rounded-r-full" />
                )}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Bottom Items */}
      <div className="p-3 border-t border-gray-200">
        {bottomItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={`
                flex items-center px-3 py-2 rounded-lg transition-colors
                ${isActive
                  ? 'bg-gray-100 text-gray-900'
                  : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                }
              `}
            >
              <Icon size={18} className="mr-3" />
              <span className="text-sm">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </aside>
  );
}
