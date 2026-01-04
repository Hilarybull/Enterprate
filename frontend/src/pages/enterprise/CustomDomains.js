import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Globe2, 
  Plus, 
  RefreshCw, 
  Trash2, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  ExternalLink,
  Copy,
  Server,
  Shield,
  Loader2,
  Info
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const STATUS_COLORS = {
  active: 'bg-green-100 text-green-700',
  pending_dns: 'bg-amber-100 text-amber-700',
  pending: 'bg-gray-100 text-gray-700',
  error: 'bg-red-100 text-red-700'
};

const SSL_STATUS_COLORS = {
  active: 'bg-green-100 text-green-700',
  pending: 'bg-amber-100 text-amber-700',
  error: 'bg-red-100 text-red-700'
};

export default function CustomDomains() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [loading, setLoading] = useState(true);
  const [websites, setWebsites] = useState([]);
  const [selectedWebsite, setSelectedWebsite] = useState(null);
  const [domains, setDomains] = useState([]);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [adding, setAdding] = useState(false);
  const [verifying, setVerifying] = useState(null);
  
  // Form state
  const [newDomain, setNewDomain] = useState('');

  const loadWebsites = useCallback(async () => {
    if (!currentWorkspace) return;
    
    try {
      const response = await axios.get(`${API_URL}/ai-websites`, {
        headers: getHeaders()
      });
      // Only show deployed websites
      const deployedWebsites = (response.data || []).filter(w => w.status === 'deployed');
      setWebsites(deployedWebsites);
      
      if (deployedWebsites.length > 0 && !selectedWebsite) {
        setSelectedWebsite(deployedWebsites[0]);
      }
    } catch (error) {
      console.error('Failed to load websites:', error);
    }
  }, [currentWorkspace, getHeaders, selectedWebsite]);

  const loadDomains = useCallback(async () => {
    if (!currentWorkspace || !selectedWebsite) {
      setDomains([]);
      setLoading(false);
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_URL}/domains/website/${selectedWebsite.id}`,
        { headers: getHeaders() }
      );
      setDomains(response.data || []);
    } catch (error) {
      console.error('Failed to load domains:', error);
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace, selectedWebsite, getHeaders]);

  useEffect(() => {
    loadWebsites();
  }, [loadWebsites]);

  useEffect(() => {
    loadDomains();
  }, [loadDomains]);

  const addDomain = async () => {
    if (!newDomain.trim()) {
      toast.error('Please enter a domain name');
      return;
    }
    
    if (!selectedWebsite) {
      toast.error('Please select a website first');
      return;
    }
    
    setAdding(true);
    try {
      const response = await axios.post(`${API_URL}/domains`, {
        websiteId: selectedWebsite.id,
        domain: newDomain
      }, { headers: getHeaders() });
      
      if (response.data?.success) {
        toast.success('Domain added! Configure DNS records to complete setup.');
        setShowAddDialog(false);
        setNewDomain('');
        loadDomains();
      } else {
        toast.error(response.data?.error || 'Failed to add domain');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add domain');
    } finally {
      setAdding(false);
    }
  };

  const verifyDomain = async (domainId) => {
    setVerifying(domainId);
    try {
      const response = await axios.post(
        `${API_URL}/domains/${domainId}/verify`,
        {},
        { headers: getHeaders() }
      );
      
      if (response.data?.dnsVerified) {
        toast.success('Domain verified successfully!');
      } else {
        toast.info(response.data?.message || 'DNS not yet propagated. Please wait and try again.');
      }
      loadDomains();
    } catch (error) {
      toast.error('Verification failed');
    } finally {
      setVerifying(null);
    }
  };

  const removeDomain = async (domainId) => {
    if (!window.confirm('Are you sure you want to remove this domain?')) return;
    
    try {
      await axios.delete(`${API_URL}/domains/${domainId}`, {
        headers: getHeaders()
      });
      toast.success('Domain removed');
      loadDomains();
    } catch (error) {
      toast.error('Failed to remove domain');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircle2 className="h-4 w-4" />;
      case 'pending_dns':
        return <Clock className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  if (loading && websites.length === 0) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="loading-spinner">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-slide-in" data-testid="custom-domains-page">
      <PageHeader
        icon={Globe2}
        title="Custom Domains"
        description="Connect your own domain to your deployed websites"
        actions={
          <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
            <DialogTrigger asChild>
              <Button 
                className="gradient-primary border-0" 
                disabled={websites.length === 0}
                data-testid="add-domain-btn"
              >
                <Plus className="mr-2" size={16} />
                Add Domain
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Custom Domain</DialogTitle>
                <DialogDescription>
                  Connect your domain to a deployed website. You&apos;ll need to configure DNS records with your domain provider.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label>Select Website</Label>
                  <Select 
                    value={selectedWebsite?.id || ''} 
                    onValueChange={(id) => setSelectedWebsite(websites.find(w => w.id === id))}
                  >
                    <SelectTrigger className="mt-1.5" data-testid="website-select">
                      <SelectValue placeholder="Choose a website" />
                    </SelectTrigger>
                    <SelectContent>
                      {websites.map((website) => (
                        <SelectItem key={website.id} value={website.id}>
                          {website.businessContext?.companyName || 'Untitled Website'}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Domain Name</Label>
                  <Input
                    value={newDomain}
                    onChange={(e) => setNewDomain(e.target.value)}
                    placeholder="example.com or subdomain.example.com"
                    className="mt-1.5"
                    data-testid="domain-input"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Enter your domain without http:// or www.
                  </p>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowAddDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={addDomain} disabled={adding} data-testid="submit-domain-btn">
                  {adding ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Plus className="mr-2" size={16} />}
                  Add Domain
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      {websites.length === 0 ? (
        <Card className="p-12 text-center">
          <Globe2 className="mx-auto text-gray-300 mb-4" size={48} />
          <h3 className="text-lg font-medium text-gray-700">No Deployed Websites</h3>
          <p className="text-gray-500 mt-1">
            Deploy a website first to connect a custom domain
          </p>
          <Button className="mt-4" variant="outline" onClick={() => window.location.href = '/ai-website-builder'}>
            Go to Website Builder
          </Button>
        </Card>
      ) : (
        <>
          {/* Website Selector */}
          <div className="flex items-center gap-4">
            <Label className="shrink-0">Website:</Label>
            <Select 
              value={selectedWebsite?.id || ''} 
              onValueChange={(id) => setSelectedWebsite(websites.find(w => w.id === id))}
            >
              <SelectTrigger className="w-[300px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {websites.map((website) => (
                  <SelectItem key={website.id} value={website.id}>
                    {website.businessContext?.companyName || 'Untitled Website'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedWebsite?.deploymentUrl && (
              <a 
                href={selectedWebsite.deploymentUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-indigo-600 hover:underline flex items-center gap-1"
              >
                View Site <ExternalLink size={14} />
              </a>
            )}
          </div>

          {/* Domains List */}
          <div className="grid gap-4">
            {domains.map((domain) => (
              <Card key={domain.id} data-testid={`domain-card-${domain.id}`}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <Globe2 className="text-indigo-600" size={20} />
                        <span className="text-lg font-medium">{domain.domain}</span>
                        <Badge className={STATUS_COLORS[domain.status]}>
                          {getStatusIcon(domain.status)}
                          <span className="ml-1">{domain.status.replace(/_/g, ' ')}</span>
                        </Badge>
                        <Badge variant="outline" className={SSL_STATUS_COLORS[domain.sslStatus]}>
                          <Shield size={12} className="mr-1" />
                          SSL: {domain.sslStatus}
                        </Badge>
                      </div>
                      
                      {domain.status === 'pending_dns' && domain.dnsRecords?.length > 0 && (
                        <Alert>
                          <Info className="h-4 w-4" />
                          <AlertDescription>
                            <div className="font-medium mb-2">Configure these DNS records with your domain provider:</div>
                            <div className="space-y-2 font-mono text-sm">
                              {domain.dnsRecords.map((record, idx) => (
                                <div key={idx} className="flex items-center gap-4 bg-gray-100 p-2 rounded">
                                  <span className="font-semibold w-16">{record.type}</span>
                                  <span className="text-gray-600">Name:</span>
                                  <span>{record.name}</span>
                                  <span className="text-gray-600">Value:</span>
                                  <span className="flex-1 truncate">{record.value}</span>
                                  <Button 
                                    variant="ghost" 
                                    size="sm" 
                                    onClick={() => copyToClipboard(record.value)}
                                  >
                                    <Copy size={14} />
                                  </Button>
                                </div>
                              ))}
                            </div>
                            <p className="text-xs text-gray-500 mt-2">
                              DNS changes can take up to 48 hours to propagate. You can verify at any time.
                            </p>
                          </AlertDescription>
                        </Alert>
                      )}
                      
                      {domain.status === 'active' && (
                        <p className="text-sm text-green-600 flex items-center gap-2">
                          <CheckCircle2 size={16} />
                          Your domain is active and serving your website
                        </p>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {domain.status !== 'active' && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => verifyDomain(domain.id)}
                          disabled={verifying === domain.id}
                        >
                          {verifying === domain.id ? (
                            <Loader2 className="h-4 w-4 animate-spin mr-1" />
                          ) : (
                            <RefreshCw size={14} className="mr-1" />
                          )}
                          Verify DNS
                        </Button>
                      )}
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                        onClick={() => removeDomain(domain.id)}
                      >
                        <Trash2 size={14} />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {domains.length === 0 && selectedWebsite && !loading && (
              <Card className="p-12 text-center">
                <Server className="mx-auto text-gray-300 mb-4" size={48} />
                <h3 className="text-lg font-medium text-gray-700">No Custom Domains</h3>
                <p className="text-gray-500 mt-1">
                  This website is available at: {selectedWebsite.deploymentUrl}
                </p>
                <Button className="mt-4" onClick={() => setShowAddDialog(true)}>
                  <Plus className="mr-2" size={16} /> Add Custom Domain
                </Button>
              </Card>
            )}
          </div>

          {/* Instructions Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">How to Set Up a Custom Domain</CardTitle>
              <CardDescription>
                Follow these steps to connect your domain
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ol className="list-decimal list-inside space-y-2 text-sm text-gray-600">
                <li>Click &quot;Add Domain&quot; and enter your domain name (e.g., example.com)</li>
                <li>Copy the DNS records shown after adding the domain</li>
                <li>Log in to your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.)</li>
                <li>Navigate to DNS settings for your domain</li>
                <li>Add the DNS records exactly as shown (CNAME or A records)</li>
                <li>Wait for DNS propagation (can take up to 48 hours, usually faster)</li>
                <li>Click &quot;Verify DNS&quot; to check if the records are properly configured</li>
                <li>Once verified, SSL will be automatically provisioned</li>
              </ol>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
