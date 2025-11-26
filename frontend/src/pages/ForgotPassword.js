import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, ArrowLeft, Mail, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [resetToken, setResetToken] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/auth/forgot-password`, { email });
      setSent(true);
      // For demo purposes only - in production, don't show the token
      if (response.data.resetToken) {
        setResetToken(response.data.resetToken);
      }
      toast.success('Password reset instructions sent!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to process request');
    } finally {
      setLoading(false);
    }
  };

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
          <CardTitle className="text-2xl">Forgot Password</CardTitle>
          <CardDescription>
            {sent 
              ? "We've sent you password reset instructions"
              : "Enter your email address and we'll send you a link to reset your password"
            }
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          {sent ? (
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto">
                <CheckCircle className="text-green-600" size={32} />
              </div>
              <p className="text-gray-600">
                Check your email for a link to reset your password. If it doesn't appear within a few minutes, check your spam folder.
              </p>
              
              {/* Demo only - shows reset link */}
              {resetToken && (
                <Alert className="mt-4 bg-purple-50 border-purple-200">
                  <AlertDescription className="text-sm">
                    <strong>Demo Mode:</strong> In production, this would be sent via email.
                    <br />
                    <Link 
                      to={`/auth/reset-password?token=${resetToken}`}
                      className="text-purple-600 underline hover:text-purple-800"
                    >
                      Click here to reset your password
                    </Link>
                  </AlertDescription>
                </Alert>
              )}
              
              <Button
                variant="outline"
                className="mt-4"
                onClick={() => { setSent(false); setResetToken(null); }}
              >
                <Mail className="mr-2" size={16} />
                Try another email
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="mt-1.5"
                />
              </div>
              
              <Button
                type="submit"
                className="w-full gradient-primary border-0"
                disabled={loading}
              >
                {loading ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Sending...</>
                ) : (
                  'Send Reset Link'
                )}
              </Button>
            </form>
          )}
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
