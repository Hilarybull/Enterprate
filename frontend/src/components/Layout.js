import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useWorkspace } from '@/context/WorkspaceContext';
import {
  LayoutDashboard,
  Lightbulb,
  FileText,
  TrendingUp,
  Globe,
  Settings,
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/genesis', icon: Lightbulb, label: 'Genesis AI' },
  { path: '/navigator', icon: FileText, label: 'Navigator' },
  { path: '/growth', icon: TrendingUp, label: 'Growth' },
  { path: '/website-builder', icon: Globe, label: 'Website Builder' },
  { path: '/settings', icon: Settings, label: 'Settings' }
];

	export default function Layout() {
	  const location = useLocation();
	  const navigate = useNavigate();
	  const { user, logout } = useAuth();
	  const { currentWorkspace, workspaces, createWorkspace, loading } = useWorkspace();
	  const [sidebarOpen, setSidebarOpen] = useState(false);
	  const [createWorkspaceOpen, setCreateWorkspaceOpen] = useState(false);
	  const [workspaceName, setWorkspaceName] = useState('');
	  const [creating, setCreating] = useState(false);

  // Auto-open workspace creation if no workspaces exist
  useEffect(() => {
    if (!loading && workspaces.length === 0 && !createWorkspaceOpen) {
      setCreateWorkspaceOpen(true);
    }
  }, [loading, workspaces, createWorkspaceOpen]);

  const handleLogout = () => {
    logout();
    navigate('/auth/login');
  };

	  const handleCreateWorkspace = async (e) => {
	    e.preventDefault();
	    if (!workspaceName.trim()) return;

	    setCreating(true);
	    try {
	      await createWorkspace({ name: workspaceName });
	      toast.success('Workspace created successfully');
	      setCreateWorkspaceOpen(false);
	      setWorkspaceName('');
	    } catch (error) {
	      const status = error?.status ?? error?.response?.status;
	      if (status === 409) {
	        toast.error('Only one workspace is allowed per user.');
	      } else {
	        toast.error('Failed to create workspace');
	      }
	    } finally {
	      setCreating(false);
	    }
	  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
              data-testid="mobile-menu-toggle"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            
            <Link to="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">E</span>
              </div>
              <span className="text-xl font-bold" style={{ fontFamily: 'Space Grotesk' }}>EnterprateAI</span>
            </Link>
	          </div>

	          <div className="flex items-center space-x-3">
	            {/* Workspace Indicator (single-workspace app) */}
	            {currentWorkspace ? (
	              <div
	                className="hidden sm:flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700"
	                data-testid="workspace-indicator"
	              >
	                <span className="text-gray-500">Workspace</span>
	                <span className="max-w-[160px] truncate font-medium">{currentWorkspace.name}</span>
	              </div>
	            ) : (
	              !loading && (
	                <Button
	                  variant="outline"
	                  onClick={() => setCreateWorkspaceOpen(true)}
	                  data-testid="create-workspace-btn"
	                >
	                  Create Workspace
	                </Button>
	              )
	            )}

	            {/* User Menu */}
	            <DropdownMenu>
	              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center space-x-2" data-testid="user-menu">
                  <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">{user?.name?.charAt(0)}</span>
                  </div>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <div className="px-2 py-1.5 text-sm">
                  <div className="font-medium">{user?.name}</div>
                  <div className="text-xs text-gray-500">{user?.email}</div>
                </div>
                <DropdownMenuItem onClick={handleLogout} data-testid="logout-btn">
                  <LogOut size={16} className="mr-2" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside
          className={`
            fixed lg:static inset-y-0 left-0 z-30 w-64 bg-white border-r border-gray-200
            transform transition-transform duration-200 ease-in-out lg:translate-x-0
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
            mt-[57px] lg:mt-0
          `}
        >
          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
                  className={`
                    flex items-center space-x-3 px-4 py-3 rounded-lg
                    transition-colors
                    ${
                      isActive
                        ? 'bg-blue-50 text-blue-600 font-medium'
                        : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>

	      {/* Create Workspace Dialog */}
	      <Dialog open={createWorkspaceOpen} onOpenChange={setCreateWorkspaceOpen}>
	        <DialogContent>
	          <DialogHeader>
	            <DialogTitle>Create Workspace</DialogTitle>
	          </DialogHeader>
	          {workspaces.length > 0 ? (
	            <div className="space-y-4">
	              <p className="text-sm text-gray-600">
	                Only one workspace is allowed per user.
	              </p>
	              <div className="flex justify-end">
	                <Button
	                  type="button"
	                  onClick={() => setCreateWorkspaceOpen(false)}
	                  data-testid="close-workspace-limit-btn"
	                >
	                  Close
	                </Button>
	              </div>
	            </div>
	          ) : (
	            <form onSubmit={handleCreateWorkspace} className="space-y-4">
	              <div>
	                <Label htmlFor="workspace-name">Workspace Name</Label>
	                <Input
	                  id="workspace-name"
	                  data-testid="workspace-name-input"
	                  value={workspaceName}
	                  onChange={(e) => setWorkspaceName(e.target.value)}
	                  placeholder="My Company"
	                  required
	                />
	              </div>
	              <div className="flex justify-end space-x-2">
	                <Button
	                  type="button"
	                  variant="outline"
	                  onClick={() => setCreateWorkspaceOpen(false)}
	                  data-testid="cancel-workspace-btn"
	                >
	                  Cancel
	                </Button>
	                <Button type="submit" disabled={creating} data-testid="submit-workspace-btn">
	                  {creating ? 'Creating...' : 'Create'}
	                </Button>
	              </div>
	            </form>
	          )}
	        </DialogContent>
	      </Dialog>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
