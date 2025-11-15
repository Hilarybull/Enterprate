import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import AuthProvider, { useAuth } from '@/context/AuthContext';
import WorkspaceProvider from '@/context/WorkspaceContext';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Dashboard from '@/pages/Dashboard';
import Genesis from '@/pages/Genesis';
import Navigator from '@/pages/Navigator';
import Growth from '@/pages/Growth';
import WebsiteBuilder from '@/pages/WebsiteBuilder';
import WebsiteEditor from '@/pages/WebsiteEditor';
import Settings from '@/pages/Settings';
import Layout from '@/components/Layout';
import '@/App.css';

function PrivateRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/auth/login" />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/auth/login" element={<Login />} />
      <Route path="/auth/register" element={<Register />} />
      
      <Route path="/" element={
        <PrivateRoute>
          <WorkspaceProvider>
            <Layout />
          </WorkspaceProvider>
        </PrivateRoute>
      }>
        <Route index element={<Navigate to="/dashboard" />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="genesis" element={<Genesis />} />
        <Route path="navigator" element={<Navigator />} />
        <Route path="growth" element={<Growth />} />
        <Route path="website-builder" element={<WebsiteBuilder />} />
        <Route path="website-builder/:websiteId" element={<WebsiteEditor />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
          <Toaster position="top-right" />
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;
