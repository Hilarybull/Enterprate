import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Globe, Plus, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function WebsiteBuilder() {
  const navigate = useNavigate();
  const { getHeaders } = useWorkspace();
  const [websites, setWebsites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    domain: ''
  });

  useEffect(() => {
    loadWebsites();
  }, []);

  const loadWebsites = async () => {
    try {
      const response = await axios.get(`${API_URL}/websites`, {
        headers: getHeaders()
      });
      setWebsites(response.data);
    } catch (error) {
      console.error('Failed to load websites:', error);
      toast.error('Failed to load websites');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWebsite = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        `${API_URL}/websites`,
        formData,
        { headers: getHeaders() }
      );
      toast.success('Website created successfully');
      setCreateDialogOpen(false);
      setFormData({ name: '', domain: '' });
      navigate(`/website-builder/${response.data.id}`);
    } catch (error) {
      toast.error('Failed to create website');
      console.error(error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-slide-in" data-testid="website-builder-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2 flex items-center" style={{ fontFamily: 'Space Grotesk' }}>
            <Globe className="mr-3 text-purple-500" size={32} />
            Website Builder
          </h1>
          <p className="text-gray-600">Build and manage your websites with drag-and-drop simplicity</p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)} data-testid="create-website-btn">
          <Plus className="mr-2" size={18} />
          New Website
        </Button>
      </div>

      {websites.length === 0 ? (
        <Card>
          <CardContent className="py-16">
            <div className="text-center">
              <Globe className="mx-auto text-gray-400 mb-4" size={64} />
              <h3 className="text-xl font-semibold mb-2">No websites yet</h3>
              <p className="text-gray-600 mb-6">Create your first website and start building</p>
              <Button onClick={() => setCreateDialogOpen(true)} size="lg" data-testid="empty-create-website-btn">
                <Plus className="mr-2" size={18} />
                Create Your First Website
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {websites.map((website, index) => (
            <Card
              key={website.id}
              className="card-hover cursor-pointer"
              onClick={() => navigate(`/website-builder/${website.id}`)}
              data-testid={`website-card-${index}`}
            >
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="truncate">{website.name}</span>
                  {website.published && (
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      Published
                    </span>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center text-sm text-gray-600">
                    <Globe size={16} className="mr-2" />
                    {website.domain || 'No domain set'}
                  </div>
                  <div className="text-xs text-gray-500">
                    Created {new Date(website.createdAt).toLocaleDateString()}
                  </div>
                  <div className="pt-3 border-t flex items-center justify-between">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/website-builder/${website.id}`);
                      }}
                      data-testid={`edit-website-${index}`}
                    >
                      Edit Website
                    </Button>
                    {website.domain && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={(e) => {
                          e.stopPropagation();
                          window.open(`https://${website.domain}`, '_blank');
                        }}
                        data-testid={`view-website-${index}`}
                      >
                        <ExternalLink size={16} />
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Website Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Website</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreateWebsite} className="space-y-4">
            <div>
              <Label htmlFor="website-name">Website Name</Label>
              <Input
                id="website-name"
                data-testid="website-name-input"
                placeholder="My Awesome Website"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            <div>
              <Label htmlFor="domain">Domain (Optional)</Label>
              <Input
                id="domain"
                data-testid="website-domain-input"
                placeholder="example.com"
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setCreateDialogOpen(false)}
                data-testid="cancel-website-btn"
              >
                Cancel
              </Button>
              <Button type="submit" data-testid="submit-website-btn">
                Create Website
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
