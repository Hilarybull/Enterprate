import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { 
  Settings as SettingsIcon, 
  Save, 
  User, 
  Building2,
  Bell,
  Shield,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import { useTheme } from 'next-themes';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function Settings() {
  const { theme, setTheme } = useTheme();
  const { currentWorkspace, getHeaders, loadWorkspaces } = useWorkspace();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('workspace');
  const [formData, setFormData] = useState({
    name: '',
    country: '',
    industry: '',
    stage: ''
  });

  useEffect(() => {
    if (currentWorkspace) {
      loadWorkspaceDetails();
    } else {
      setLoading(false);
    }
  }, [currentWorkspace]);

  const loadWorkspaceDetails = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/workspaces/${currentWorkspace.id}`,
        { headers: getHeaders() }
      );
      
      setFormData({
        name: response.data.name || '',
        country: response.data.country || '',
        industry: response.data.industry || '',
        stage: response.data.stage || ''
      });
    } catch (error) {
      console.error('Failed to load workspace details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      await axios.patch(
        `${API_URL}/workspaces/${currentWorkspace.id}`,
        formData,
        { headers: getHeaders() }
      );
      toast.success('Settings saved successfully');
      await loadWorkspaces();
    } catch (error) {
      toast.error('Failed to save settings');
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: 'workspace', label: 'Workspace', icon: Building2 },
    { id: 'appearance', label: 'Appearance', icon: SettingsIcon },
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield }
  ];

  const themeOptions = [
    { id: 'light', label: 'Light', description: 'Bright interface for daytime use' },
    { id: 'dark', label: 'Dark', description: 'Dim interface for low-light environments' },
    { id: 'system', label: 'System', description: 'Match your device appearance settings' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-slide-in" data-testid="settings-page">
      <PageHeader
        icon={SettingsIcon}
        title="Settings"
        description="Manage your workspace and account preferences"
      />

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar Navigation */}
        <div className="w-full lg:w-64 flex-shrink-0">
          <Card>
            <CardContent className="p-2">
              <nav className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${
                        activeTab === tab.id
                          ? 'bg-purple-100 text-purple-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <Icon size={18} className="mr-3" />
                      {tab.label}
                    </button>
                  );
                })}
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          {activeTab === 'workspace' && (
            <Card>
              <CardHeader>
                <CardTitle>Workspace Settings</CardTitle>
                <CardDescription>
                  Update your workspace details and business information
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSave} className="space-y-6">
                  <div>
                    <Label htmlFor="name">Workspace Name</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="mt-1.5"
                      required
                    />
                  </div>

                  <Separator />

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="country">Country</Label>
                      <Input
                        id="country"
                        value={formData.country}
                        onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                        placeholder="United States"
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="industry">Industry</Label>
                      <Input
                        id="industry"
                        value={formData.industry}
                        onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                        placeholder="Technology"
                        className="mt-1.5"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <Label htmlFor="stage">Business Stage</Label>
                      <Input
                        id="stage"
                        value={formData.stage}
                        onChange={(e) => setFormData({ ...formData, stage: e.target.value })}
                        placeholder="Startup, Growth, Enterprise"
                        className="mt-1.5"
                      />
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <Label>Workspace ID</Label>
                    <div className="flex items-center space-x-2 mt-1.5">
                      <Input
                        value={currentWorkspace?.id || ''}
                        readOnly
                        className="font-mono text-sm bg-gray-50"
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          navigator.clipboard.writeText(currentWorkspace?.id || '');
                          toast.success('Copied to clipboard');
                        }}
                      >
                        Copy
                      </Button>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Use this ID for API integrations and webhooks
                    </p>
                  </div>

                  <div className="flex justify-end">
                    <Button type="submit" disabled={saving} className="gradient-primary border-0">
                      {saving ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="mr-2" size={18} />
                          Save Changes
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {activeTab === 'profile' && (
            <Card>
              <CardHeader>
                <CardTitle>Profile Settings</CardTitle>
                <CardDescription>Manage your personal account information</CardDescription>
              </CardHeader>
              <CardContent className="text-center py-12">
                <User className="mx-auto text-gray-300 mb-3" size={48} />
                <p className="text-gray-500">Profile settings coming soon</p>
              </CardContent>
            </Card>
          )}

          {activeTab === 'appearance' && (
            <Card>
              <CardHeader>
                <CardTitle>Theme</CardTitle>
                <CardDescription>Choose how EnterprateAI should look</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {themeOptions.map((option) => {
                  const isActive = (theme || 'system') === option.id;
                  return (
                    <button
                      key={option.id}
                      type="button"
                      onClick={() => {
                        setTheme(option.id);
                        toast.success(`Theme set to ${option.label}`);
                      }}
                      className={`w-full text-left border rounded-lg p-4 transition-colors ${
                        isActive
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <p className="font-medium text-gray-900">{option.label}</p>
                      <p className="text-sm text-gray-500 mt-1">{option.description}</p>
                    </button>
                  );
                })}
              </CardContent>
            </Card>
          )}

          {activeTab === 'notifications' && (
            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <CardDescription>Choose how you want to be notified</CardDescription>
              </CardHeader>
              <CardContent className="text-center py-12">
                <Bell className="mx-auto text-gray-300 mb-3" size={48} />
                <p className="text-gray-500">Notification settings coming soon</p>
              </CardContent>
            </Card>
          )}

          {activeTab === 'security' && (
            <Card>
              <CardHeader>
                <CardTitle>Security Settings</CardTitle>
                <CardDescription>Manage your account security</CardDescription>
              </CardHeader>
              <CardContent className="text-center py-12">
                <Shield className="mx-auto text-gray-300 mb-3" size={48} />
                <p className="text-gray-500">Security settings coming soon</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
