import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Globe, 
  Plus, 
  ExternalLink, 
  Edit3, 
  Trash2,
  Loader2,
  Layout,
  Palette,
  Rocket
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function WebsiteSetup() {
  const navigate = useNavigate();
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [websites, setWebsites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWebsite, setNewWebsite] = useState({
    name: '',
    domain: ''
  });

  useEffect(() => {
    if (currentWorkspace) {
      loadWebsites();
    } else {
      setLoading(false);
    }
  }, [currentWorkspace]);

  const loadWebsites = async () => {
    try {
      const response = await axios.get(`${API_URL}/websites`, {
        headers: getHeaders()
      });
      setWebsites(response.data || []);
    } catch (error) {
      console.error('Failed to load websites:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWebsite = async (e) => {
    e.preventDefault();
    if (!currentWorkspace) {
      toast.error('Please select a workspace first');
      return;
    }
    setCreating(true);

    try {
      const response = await axios.post(
        `${API_URL}/websites`,
        newWebsite,
        { headers: getHeaders() }
      );
      toast.success('Website created successfully!');
      setShowCreateForm(false);
      setNewWebsite({ name: '', domain: '' });
      loadWebsites();
    } catch (error) {
      toast.error('Failed to create website');
      console.error(error);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteWebsite = async (websiteId) => {
    if (!confirm('Are you sure you want to delete this website?')) return;

    try {
      await axios.delete(`${API_URL}/websites/${websiteId}`, {
        headers: getHeaders()
      });
      toast.success('Website deleted');
      loadWebsites();
    } catch (error) {
      toast.error('Failed to delete website');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-slide-in" data-testid="website-setup-page">
      <PageHeader
        icon={Globe}
        title="Website & Business Setup"
        description="Build and manage your online presence with our website builder"
        actions={
          <Button 
            onClick={() => setShowCreateForm(true)}
            className="gradient-primary border-0"
          >
            <Plus className="mr-2" size={18} />
            Create Website
          </Button>
        }
      />

      {/* Features Overview */}
      {websites.length === 0 && !showCreateForm && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            title="Drag & Drop Builder"
            description="Create stunning pages without any coding knowledge"
            icon={Layout}
            gradient="gradient-primary"
          />
          <FeatureCard
            title="Professional Templates"
            description="Start with beautiful, conversion-optimized templates"
            icon={Palette}
            gradient="gradient-success"
          />
          <FeatureCard
            title="One-Click Publish"
            description="Go live instantly with built-in hosting"
            icon={Rocket}
            gradient="gradient-warning"
          />
        </div>
      )}

      {/* Create Website Form */}
      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Website</CardTitle>
            <CardDescription>Set up a new website for your business</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateWebsite} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Website Name</Label>
                  <Input
                    id="name"
                    value={newWebsite.name}
                    onChange={(e) => setNewWebsite({ ...newWebsite, name: e.target.value })}
                    placeholder="My Business Website"
                    className="mt-1.5"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="domain">Custom Domain (optional)</Label>
                  <Input
                    id="domain"
                    value={newWebsite.domain}
                    onChange={(e) => setNewWebsite({ ...newWebsite, domain: e.target.value })}
                    placeholder="www.mybusiness.com"
                    className="mt-1.5"
                  />
                </div>
              </div>
              <div className="flex space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCreateForm(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={creating} className="gradient-primary border-0">
                  {creating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create Website'
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Websites List */}
      {websites.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {websites.map((website) => (
            <Card key={website.id} className="enterprise-card enterprise-card-interactive">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center">
                    <Globe className="text-white" size={24} />
                  </div>
                  <div className="flex space-x-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => navigate(`/website-builder/${website.id}`)}
                    >
                      <Edit3 size={16} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-red-500 hover:text-red-600"
                      onClick={() => handleDeleteWebsite(website.id)}
                    >
                      <Trash2 size={16} />
                    </Button>
                  </div>
                </div>
                <h3 className="font-semibold text-lg mb-1">{website.name}</h3>
                <p className="text-sm text-gray-500 mb-4">
                  {website.domain || 'No custom domain'}
                </p>
                <div className="flex items-center justify-between">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    website.status === 'PUBLISHED' 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {website.status || 'Draft'}
                  </span>
                  {website.status === 'PUBLISHED' && (
                    <Button variant="ghost" size="sm" className="text-purple-600">
                      <ExternalLink size={14} className="mr-1" />
                      Visit
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}

          {/* Add New Card */}
          <Card 
            className="enterprise-card border-dashed border-2 cursor-pointer hover:border-purple-400 transition-colors"
            onClick={() => setShowCreateForm(true)}
          >
            <CardContent className="p-6 flex flex-col items-center justify-center h-full min-h-[200px]">
              <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center mb-3">
                <Plus className="text-gray-400" size={24} />
              </div>
              <p className="font-medium text-gray-600">Add New Website</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Empty State */}
      {websites.length === 0 && !showCreateForm && (
        <Card className="text-center py-16">
          <CardContent>
            <div className="w-20 h-20 rounded-2xl gradient-primary flex items-center justify-center mx-auto mb-6">
              <Globe className="text-white" size={36} />
            </div>
            <h3 className="text-xl font-semibold mb-2">No Websites Yet</h3>
            <p className="text-gray-500 mb-6 max-w-md mx-auto">
              Create your first website to establish your online presence and reach more customers.
            </p>
            <Button 
              onClick={() => setShowCreateForm(true)}
              className="gradient-primary border-0"
            >
              <Plus className="mr-2" size={18} />
              Create Your First Website
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
