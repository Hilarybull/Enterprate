import React from 'react';
import { Link } from 'react-router-dom';
import { Menu, ChevronDown, Plus, LogOut, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useWorkspace } from '@/context/WorkspaceContext';
import NotificationCenter from './NotificationCenter';

export default function EnterpriseHeader({ 
  user, 
  currentWorkspace, 
  onMenuClick, 
  onLogout,
  onCreateWorkspace 
}) {
  const { workspaces, switchWorkspace } = useWorkspace();

  return (
    <header className="sticky top-0 z-30 h-16 bg-white border-b border-gray-200">
      <div className="h-full px-4 lg:px-6 flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center space-x-4">
          {/* Mobile Menu Button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 text-gray-500"
            data-testid="mobile-menu-toggle"
          >
            <Menu size={20} />
          </button>

          {/* Search Bar */}
          <div className="hidden md:flex items-center">
            <div className="relative">
              <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search modules, features..."
                className="w-64 lg:w-80 pl-10 pr-4 py-2 bg-gray-100 border-0 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition-all"
              />
            </div>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-3">
          {/* Workspace Selector */}
          {currentWorkspace && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="outline" 
                  className="hidden sm:flex items-center space-x-2 h-9 px-3 border-gray-200 hover:border-gray-300"
                  data-testid="workspace-selector"
                >
                  <div className="w-6 h-6 rounded-md gradient-primary flex items-center justify-center">
                    <span className="text-white text-xs font-bold">
                      {currentWorkspace.name?.charAt(0)?.toUpperCase()}
                    </span>
                  </div>
                  <span className="max-w-[120px] truncate text-sm font-medium">
                    {currentWorkspace.name}
                  </span>
                  <ChevronDown size={14} className="text-gray-400" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-64">
                <div className="px-2 py-1.5 text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Workspaces
                </div>
                {workspaces.map((ws) => (
                  <DropdownMenuItem
                    key={ws.id}
                    onClick={() => switchWorkspace(ws.id)}
                    className={`cursor-pointer ${currentWorkspace.id === ws.id ? 'bg-purple-50' : ''}`}
                    data-testid={`workspace-option-${ws.slug || ws.id}`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        currentWorkspace.id === ws.id ? 'gradient-primary' : 'bg-gray-200'
                      }`}>
                        <span className={`text-sm font-bold ${
                          currentWorkspace.id === ws.id ? 'text-white' : 'text-gray-600'
                        }`}>
                          {ws.name?.charAt(0)?.toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <div className="font-medium text-sm">{ws.name}</div>
                        <div className="text-xs text-gray-500">{ws.role || 'Owner'}</div>
                      </div>
                    </div>
                  </DropdownMenuItem>
                ))}
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={onCreateWorkspace}
                  className="cursor-pointer"
                  data-testid="create-workspace-btn"
                >
                  <Plus size={16} className="mr-2 text-purple-600" />
                  <span className="text-purple-600 font-medium">Create Workspace</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}

          {/* Notifications */}
          <Button variant="ghost" size="icon" className="h-9 w-9 text-gray-500 hover:text-gray-700">
            <Bell size={18} />
          </Button>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                className="h-9 px-2 hover:bg-gray-100"
                data-testid="user-menu"
              >
                <div className="w-8 h-8 rounded-full gradient-primary flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  </span>
                </div>
                <ChevronDown size={14} className="ml-1 text-gray-400" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <div className="px-3 py-2">
                <div className="font-medium text-sm">{user?.name}</div>
                <div className="text-xs text-gray-500">{user?.email}</div>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link to="/settings" className="cursor-pointer">
                  Account Settings
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={onLogout} 
                className="text-red-600 cursor-pointer"
                data-testid="logout-btn"
              >
                <LogOut size={16} className="mr-2" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
