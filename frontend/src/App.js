import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import AuthProvider, { useAuth } from '@/context/AuthContext';
import WorkspaceProvider from '@/context/WorkspaceContext';

// Auth Pages
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import ForgotPassword from '@/pages/ForgotPassword';
import ResetPassword from '@/pages/ResetPassword';

// Enterprise Layout
import { EnterpriseLayout } from '@/components/enterprise';

// Enterprise Pages
import {
  Dashboard,
  IdeaDiscovery,
  WebsiteSetup,
  BusinessRegistration,
  BusinessBlueprint,
  FinanceAutomation,
  BusinessOperations,
  Growth,
  IntelligenceGraph,
  Settings,
  ValidationReport,
  ValidationHistory,
  Branding,
  Resources,
  Help
} from '@/pages/enterprise';

// Legacy imports for website editor
import WebsiteEditor from '@/pages/WebsiteEditor';

import '@/App.css';

// Suppress ResizeObserver loop errors (harmless in Radix UI)
if (typeof window !== 'undefined') {
  const originalError = window.onerror;
  window.onerror = function(message, source, lineno, colno, error) {
    if (message && message.includes('ResizeObserver loop')) {
      return true; // Suppress the error
    }
    if (originalError) {
      return originalError(message, source, lineno, colno, error);
    }
    return false;
  };
}

function PrivateRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_saas-dashboard-20/artifacts/aems110l_Enterprate%20Logo.png" 
            alt="Enterprate" 
            className="h-12 mx-auto mb-4 animate-pulse"
          />
          <p className="text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/auth/login" />;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route path="/auth/login" element={<Login />} />
      <Route path="/auth/register" element={<Register />} />
      <Route path="/auth/forgot-password" element={<ForgotPassword />} />
      <Route path="/auth/reset-password" element={<ResetPassword />} />
      
      {/* Protected Enterprise Routes */}
      <Route path="/" element={
        <PrivateRoute>
          <WorkspaceProvider>
            <EnterpriseLayout />
          </WorkspaceProvider>
        </PrivateRoute>
      }>
        <Route index element={<Navigate to="/dashboard" />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="idea-discovery" element={<IdeaDiscovery />} />
        <Route path="idea-discovery/modify/:modifyId" element={<IdeaDiscovery />} />
        <Route path="validation-report/:reportId" element={<ValidationReport />} />
        <Route path="validation-history" element={<ValidationHistory />} />
        <Route path="business-registration" element={<BusinessRegistration />} />
        <Route path="branding" element={<Branding />} />
        <Route path="website-setup" element={<WebsiteSetup />} />
        <Route path="website-builder/:websiteId" element={<WebsiteEditor />} />
        <Route path="business-blueprint" element={<BusinessBlueprint />} />
        <Route path="finance-automation" element={<FinanceAutomation />} />
        <Route path="business-operations" element={<BusinessOperations />} />
        <Route path="growth" element={<Growth />} />
        <Route path="resources" element={<Resources />} />
        <Route path="intelligence-graph" element={<IntelligenceGraph />} />
        <Route path="settings" element={<Settings />} />
        <Route path="help" element={<Help />} />
        
        {/* Legacy redirects */}
        <Route path="genesis" element={<Navigate to="/idea-discovery" />} />
        <Route path="navigator" element={<Navigate to="/finance-automation" />} />
        <Route path="website-builder" element={<Navigate to="/website-setup" />} />
      </Route>

      {/* Catch all - redirect to dashboard */}
      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
          <Toaster position="top-right" richColors />
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;
