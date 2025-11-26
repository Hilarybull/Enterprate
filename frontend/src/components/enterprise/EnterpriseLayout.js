import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useWorkspace } from '@/context/WorkspaceContext';
import EnterpriseSidebar from './EnterpriseSidebar';
import EnterpriseHeader from './EnterpriseHeader';
import AIChatbot from './AIChatbot';
import CreateWorkspaceModal from './CreateWorkspaceModal';

export default function EnterpriseLayout() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { currentWorkspace, workspaces, loading } = useWorkspace();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [createWorkspaceOpen, setCreateWorkspaceOpen] = useState(false);

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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Fixed Sidebar */}
      <EnterpriseSidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)} 
      />

      {/* Main Content Area */}
      <div className="lg:pl-[280px]">
        {/* Header */}
        <EnterpriseHeader
          user={user}
          currentWorkspace={currentWorkspace}
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          onLogout={handleLogout}
          onCreateWorkspace={() => setCreateWorkspaceOpen(true)}
        />

        {/* Page Content */}
        <main className="p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* AI Chatbot */}
      <AIChatbot />

      {/* Create Workspace Modal */}
      <CreateWorkspaceModal
        open={createWorkspaceOpen}
        onOpenChange={setCreateWorkspaceOpen}
      />
    </div>
  );
}
