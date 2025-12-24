import React, { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

/**
 * AuthCallback Component
 * Handles the OAuth callback from Emergent Google Auth
 * 
 * REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
 */
export default function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Use ref to prevent double-processing in StrictMode
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      try {
        // Extract session_id from URL hash
        const hash = location.hash;
        const sessionIdMatch = hash.match(/session_id=([^&]+)/);
        
        if (!sessionIdMatch) {
          console.error('No session_id found in URL');
          navigate('/auth/login', { replace: true });
          return;
        }

        const sessionId = sessionIdMatch[1];
        console.log('Processing session_id:', sessionId.substring(0, 10) + '...');

        // Exchange session_id for user data and session_token via backend
        const response = await axios.post(
          `${API_URL}/auth/google/callback`,
          { session_id: sessionId },
          { withCredentials: true }
        );

        const { user, token } = response.data;
        
        // Store token in localStorage for JWT auth compatibility
        localStorage.setItem('token', token);
        
        console.log('Auth successful, redirecting to dashboard');
        
        // Navigate to dashboard with user data
        navigate('/dashboard', { 
          replace: true,
          state: { user } 
        });
        
      } catch (error) {
        console.error('Auth callback error:', error);
        navigate('/auth/login', { 
          replace: true,
          state: { error: 'Authentication failed. Please try again.' }
        });
      }
    };

    processAuth();
  }, [navigate, location]);

  // Show minimal loading state (no UI flicker)
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="text-center">
        <img 
          src="https://customer-assets.emergentagent.com/job_saas-dashboard-20/artifacts/aems110l_Enterprate%20Logo.png" 
          alt="Enterprate" 
          className="h-12 mx-auto mb-4 animate-pulse"
        />
        <p className="text-gray-500">Completing sign in...</p>
      </div>
    </div>
  );
}
