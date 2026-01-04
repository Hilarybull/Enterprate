import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import AuthProvider, { useAuth } from '@/context/AuthContext';
import WorkspaceProvider from '@/context/WorkspaceContext';
import WebSocketProvider from '@/context/WebSocketContext';

// Auth Pages
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import ForgotPassword from '@/pages/ForgotPassword';
import ResetPassword from '@/pages/ResetPassword';
import AuthCallback from '@/pages/AuthCallback';

// Enterprise Layout
import { EnterpriseLayout } from '@/components/enterprise';

// Enterprise Pages
import {
  Dashboard,
  IdeaDiscovery,
  WebsiteSetup,
  AIWebsiteBuilder,
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
  Help,
  TeamCollaboration,
  ABTesting,
  CampaignAutomation,
  WebsiteAnalytics,
  CustomDomains
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
  const location = useLocation();
  
  // Skip auth check if user data was passed from AuthCallback
  if (location.state?.user) {
    return children;
  }
  
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

/**
 * AppRouter Component
 * CRITICAL: Check for session_id in URL hash BEFORE rendering normal routes
 * This prevents race conditions with Google OAuth callback
 */
function AppRouter() {
  const location = useLocation();
  
  // Check URL hash for session_id (Google OAuth callback)
  // This must be synchronous during render to prevent race conditions
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  
  return (
    <Routes>
      {/* Auth Routes */}
      <Route path="/auth/login" element={<Login />} />
      <Route path="/auth/register" element={<Register />} />
      <Route path="/auth/forgot-password" element={<ForgotPassword />} />
      <Route path="/auth/reset-password" element={<ResetPassword />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      
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
        <Route path="ai-website-builder" element={<AIWebsiteBuilder />} />
        <Route path="website-builder/:websiteId" element={<WebsiteEditor />} />
        <Route path="website-analytics" element={<WebsiteAnalytics />} />
        <Route path="business-blueprint" element={<BusinessBlueprint />} />
        <Route path="finance-automation" element={<FinanceAutomation />} />
        <Route path="business-operations" element={<BusinessOperations />} />
        <Route path="growth" element={<Growth />} />
        <Route path="team" element={<TeamCollaboration />} />
        <Route path="ab-testing" element={<ABTesting />} />
        <Route path="automation" element={<CampaignAutomation />} />
        <Route path="resources" element={<Resources />} />
        <Route path="intelligence-graph" element={<IntelligenceGraph />} />
        <Route path="settings" element={<Settings />} />
        <Route path="help" element={<Help />} />
        
        {/* Legacy redirects */}
        <Route path="genesis" element={<Navigate to="/idea-discovery" />} />
        <Route path="navigator" element={<Navigate to="/finance-automation" />} />
        <Route path="website-builder" element={<Navigate to="/ai-website-builder" />} />
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
          <AppRouter />
          <Toaster position="top-right" richColors />
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;
