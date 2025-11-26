import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, ArrowLeft, CheckCircle, XCircle, Eye, EyeOff } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [email, setEmail] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (token) {
      verifyToken();
    } else {
      setVerifying(false);
    }
  }, [token]);

  const verifyToken = async () => {
    try {
      const response = await axios.post(`${API_URL}/auth/verify-reset-token`, { token });
      setTokenValid(response.data.valid);
      setEmail(response.data.email);
    } catch (error) {
      setTokenValid(false);
    } finally {
      setVerifying(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    
    if (password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }
    
    setLoading(true);

    try {
      await axios.post(`${API_URL}/auth/reset-password`, {
        token,
        newPassword: password
      });
      setSuccess(true);
      toast.success('Password reset successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  if (verifying) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-purple-600 mx-auto mb-4" />
          <p className="text-gray-600">Verifying reset link...</p>
        </div>
      </div>
    );
  }

  if (!token || !tokenValid) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-8 text-center">
            <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
              <XCircle className="text-red-600" size={32} />
            </div>
            <h2 className="text-xl font-semibold mb-2">Invalid Reset Link</h2>
            <p className="text-gray-600 mb-6">
              This password reset link is invalid or has expired. Please request a new one.
            </p>
            <Link to="/auth/forgot-password">
              <Button className="gradient-primary border-0">Request New Link</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-8 text-center">
            <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="text-green-600" size={32} />
            </div>
            <h2 className="text-xl font-semibold mb-2">Password Reset Complete</h2>
            <p className="text-gray-600 mb-6">
              Your password has been successfully reset. You can now login with your new password.
            </p>
            <Link to="/auth/login">
              <Button className="gradient-primary border-0">Go to Login</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <Link to="/auth/login" className="inline-block mb-4">
            <img 
              src="https://customer-assets.emergentagent.com/job_saas-dashboard-20/artifacts/aems110l_Enterprate%20Logo.png" 
              alt="Enterprate" 
              className="h-12 mx-auto"
            />
          </Link>
          <CardTitle className="text-2xl">Reset Password</CardTitle>
          <CardDescription>
            Enter your new password for <strong>{email}</strong>
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="password">New Password</Label>
              <div className="relative mt-1.5">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter new password"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>
            
            <div>
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                required
                minLength={6}
                className="mt-1.5"
              />
            </div>
            
            <Button
              type="submit"
              className="w-full gradient-primary border-0"
              disabled={loading}
            >
              {loading ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Resetting...</>
              ) : (
                'Reset Password'
              )}
            </Button>
          </form>
        </CardContent>
        
        <CardFooter className="justify-center">
          <Link 
            to="/auth/login" 
            className="flex items-center text-sm text-gray-600 hover:text-purple-600"
          >
            <ArrowLeft size={16} className="mr-2" />
            Back to login
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
