import React, { useEffect, useMemo, useRef, useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;
const GOOGLE_SCRIPT_SRC = 'https://accounts.google.com/gsi/client';

function loadGoogleScript() {
  return new Promise((resolve, reject) => {
    if (window.google?.accounts?.id) {
      resolve();
      return;
    }
    const existing = document.querySelector(`script[src="${GOOGLE_SCRIPT_SRC}"]`);
    if (existing) {
      if (window.google?.accounts?.id) {
        resolve();
        return;
      }
      // If script exists but already finished loading without Google namespace,
      // fail fast instead of leaving the UI in an infinite loading state.
      if (existing.dataset.gsiFailed === '1') {
        reject(new Error('Google script was blocked by browser policy/shields.'));
        return;
      }

      const onLoad = () => {
        if (window.google?.accounts?.id) {
          resolve();
        } else {
          reject(new Error('Google script loaded but was blocked from initializing.'));
        }
      };
      const onError = () => {
        existing.dataset.gsiFailed = '1';
        reject(new Error('Failed to load Google script'));
      };
      existing.addEventListener('load', onLoad, { once: true });
      existing.addEventListener('error', onError, { once: true });

      // If the existing script is already complete and events have passed, do a short fallback check.
      setTimeout(() => {
        if (window.google?.accounts?.id) {
          resolve();
        } else {
          reject(new Error('Google script is present but blocked. Disable shields/adblock for localhost.'));
        }
      }, 1500);
      return;
    }
    const script = document.createElement('script');
    script.src = GOOGLE_SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      if (window.google?.accounts?.id) {
        resolve();
      } else {
        script.dataset.gsiFailed = '1';
        reject(new Error('Google script loaded but failed to initialize (likely blocked by browser policy).'));
      }
    };
    script.onerror = () => {
      script.dataset.gsiFailed = '1';
      reject(new Error('Failed to load Google script'));
    };
    document.head.appendChild(script);
  });
}

export default function GoogleAuthButton({ onSuccess, mode = 'login' }) {
  const [ready, setReady] = useState(false);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState('');
  const containerRef = useRef(null);
  const onSuccessRef = useRef(onSuccess);
  const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
  const buttonLabel = mode === 'register' ? 'Sign up with Google' : 'Sign in with Google';

  const buttonId = useMemo(
    () => `google-auth-${mode}-${Math.random().toString(36).slice(2, 9)}`,
    [mode],
  );

  useEffect(() => {
    onSuccessRef.current = onSuccess;
  }, [onSuccess]);

  useEffect(() => {
    let mounted = true;
    const initialize = async () => {
      if (!clientId) return;
      try {
        await Promise.race([
          loadGoogleScript(),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Google script load timed out. Check browser shields/adblock and allowed origins.')), 12000),
          ),
        ]);
        if (!mounted || !window.google?.accounts?.id || !containerRef.current) return;

        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: async (googleResponse) => {
            const idToken = googleResponse?.credential;
            if (!idToken) {
              toast.error('Google did not return a token');
              return;
            }
            try {
              setWorking(true);
              const response = await axios.post(
                `${API_URL}/auth/google/callback`,
                { id_token: idToken },
                { withCredentials: true },
              );
              const { user, token } = response.data || {};
              if (!token) {
                toast.error('Google auth failed: token missing');
                return;
              }
              localStorage.setItem('token', token);
              if (onSuccessRef.current) onSuccessRef.current(user, token);
            } catch (error) {
              toast.error(error?.response?.data?.detail || 'Google login failed');
            } finally {
              setWorking(false);
            }
          },
        });

        window.google.accounts.id.renderButton(containerRef.current, {
          type: 'standard',
          theme: 'outline',
          size: 'large',
          text: mode === 'register' ? 'signup_with' : 'signin_with',
          width: 360,
          shape: 'rectangular',
          logo_alignment: 'left',
        });
        setReady(true);
      } catch (error) {
        console.error(error);
        if (!mounted) return;
        setError(error?.message || 'Google Sign-In failed to initialize');
        setReady(false);
      }
    };
    initialize();
    return () => {
      mounted = false;
      if (window.google?.accounts?.id) {
        window.google.accounts.id.cancel();
      }
    };
  }, [clientId, mode]);

  if (!clientId) {
    return (
      <Button variant="outline" className="w-full bg-white hover:bg-gray-50" disabled>
        Google is unavailable (set REACT_APP_GOOGLE_CLIENT_ID)
      </Button>
    );
  }

  if (!ready) {
    return (
      <div className="space-y-2">
        <Button variant="outline" className="w-full bg-white hover:bg-gray-50" disabled>
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          Loading Google...
        </Button>
        {error ? (
          <p className="text-xs text-red-600 text-center">{error}</p>
        ) : null}
        <p className="text-[11px] text-gray-500 text-center">
          If this keeps loading, allow Google scripts in browser shields/adblock.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div id={buttonId} ref={containerRef} className="w-full flex justify-center" />
      {working && (
        <div className="text-xs text-gray-600 text-center">Completing {buttonLabel.toLowerCase()}...</div>
      )}
    </div>
  );
}
