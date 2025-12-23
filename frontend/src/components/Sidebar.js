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
  HelpCircle
} from 'lucide-react';

const navItems = [
  { 
    path: '/dashboard', 
    icon: LayoutDashboard, 
    label: 'Dashboard',
    subtitle: 'Overview & analytics'
  },
  { 
    path: '/idea-discovery', 
    icon: Lightbulb, 
    label: 'Idea Discovery',
    subtitle: 'Validate business ideas'
  },
  { 
    path: '/business-registration', 
    icon: FileText, 
    label: 'Business Registration Companion',
    subtitle: 'Legal & compliance'
  },
  { 
    path: '/branding', 
    icon: Palette, 
    label: 'Branding',
    subtitle: 'Visual identity & assets'
  },
  { 
    path: '/website-setup', 
    icon: Globe, 
    label: 'Website',
    subtitle: 'Build your online presence'
  },
  { 
    path: '/business-blueprint', 
    icon: BookOpen, 
    label: 'Business Blueprint Generator',
    subtitle: 'Strategic planning'
  },
  { 
    path: '/finance-automation', 
    icon: DollarSign, 
    label: 'Finance',
    subtitle: 'Invoicing & accounting'
  },
  { 
    path: '/business-operations', 
    icon: Briefcase, 
    label: 'Operations',
    subtitle: 'Process management'
  },
  { 
    path: '/growth', 
    icon: TrendingUp, 
    label: 'Growth',
    subtitle: 'Marketing & sales'
  },
  { 
    path: '/resources', 
    icon: FolderOpen, 
    label: 'Business Resources Hub',
    subtitle: 'Tools & templates'
  }
];

const bottomItems = [
  { 
    path: '/settings', 
    icon: Settings, 
    label: 'Settings'
  },
  { 
    path: '/help', 
    icon: HelpCircle, 
    label: 'Help & Support'
  }
];

export default function Sidebar() {
  const location = useLocation();

  const NavItem = ({ item }) => {
    const Icon = item.icon;
    const isActive = location.pathname === item.path;
    
    return (
      <Link
        to={item.path}
        className={`
          relative flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200
          ${
            isActive
              ? 'bg-purple-50 text-purple-600'
              : 'text-gray-600 hover:bg-gray-50'
          }
        `}
      >
        {/* Active indicator bar */}
        {isActive && (
          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-purple-600 rounded-r-full" />
        )}
        
        <div className={`
          w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0
          ${isActive ? 'bg-purple-100' : 'bg-gray-100'}
        `}>
          <Icon size={20} className={isActive ? 'text-purple-600' : 'text-gray-500'} />
        </div>
        
        <div className="flex-1 min-w-0">
          <span className={`block text-sm font-medium leading-tight truncate ${isActive ? 'text-purple-600' : 'text-gray-900'}`}>
            {item.label}
          </span>
          {item.subtitle && (
            <span className="block text-xs text-gray-400 truncate mt-0.5">
              {item.subtitle}
            </span>
          )}
        </div>
      </Link>
    );
  };

  return (
    <aside className="fixed left-0 top-0 h-screen w-[280px] bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full border-2 border-purple-600 flex items-center justify-center">
            <span className="text-purple-600 font-bold text-lg italic">e</span>
          </div>
          <span className="text-xl font-bold">
            <span className="text-purple-600">Enterprate</span>
            <span className="text-red-500">AI</span>
          </span>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavItem key={item.path} item={item} />
        ))}
      </nav>

      {/* Bottom Navigation */}
      <div className="p-4 border-t border-gray-200 space-y-1">
        {bottomItems.map((item) => (
          <NavItem key={item.path} item={item} />
        ))}
      </div>
    </aside>
  );
}
