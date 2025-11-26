import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader, StatsCard, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  TrendingUp, 
  Plus, 
  Users, 
  Target, 
  BarChart3,
  Mail,
  Phone,
  Loader2,
  ArrowUpRight,
  Filter
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function Growth() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newLead, setNewLead] = useState({
    name: '',
    email: '',
    phone: '',
    source: 'WEBSITE',
    status: 'NEW'
  });

  useEffect(() => {
    if (currentWorkspace) {
      loadLeads();
    } else {
      setLoading(false);
    }
  }, [currentWorkspace]);

  const loadLeads = async () => {
    try {
      const response = await axios.get(`${API_URL}/growth/leads`, {
        headers: getHeaders()
      });
      setLeads(response.data || []);
    } catch (error) {
      console.error('Failed to load leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLead = async (e) => {
    e.preventDefault();
    if (!currentWorkspace) {
      toast.error('Please select a workspace first');
      return;
    }
    setCreating(true);

    try {
      await axios.post(
        `${API_URL}/growth/leads`,
        newLead,
        { headers: getHeaders() }
      );
      toast.success('Lead added successfully!');
      setShowCreateDialog(false);
      setNewLead({ name: '', email: '', phone: '', source: 'WEBSITE', status: 'NEW' });
      loadLeads();
    } catch (error) {
      toast.error('Failed to add lead');
      console.error(error);
    } finally {
      setCreating(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      NEW: 'bg-blue-100 text-blue-700',
      CONTACTED: 'bg-yellow-100 text-yellow-700',
      QUALIFIED: 'bg-purple-100 text-purple-700',
      CONVERTED: 'bg-green-100 text-green-700',
      LOST: 'bg-gray-100 text-gray-500'
    };
    return colors[status] || colors.NEW;
  };

  const stats = {
    total: leads.length,
    new: leads.filter(l => l.status === 'NEW').length,
    converted: leads.filter(l => l.status === 'CONVERTED').length,
    conversionRate: leads.length > 0 
      ? Math.round((leads.filter(l => l.status === 'CONVERTED').length / leads.length) * 100)
      : 0
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-slide-in" data-testid="growth-page">
      <PageHeader
        icon={TrendingUp}
        title="Growth"
        description="Track leads, manage campaigns, and accelerate your business growth"
        actions={
          <Button 
            onClick={() => setShowCreateDialog(true)}
            className="gradient-primary border-0"
          >
            <Plus className="mr-2" size={18} />
            Add Lead
          </Button>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Leads"
          value={stats.total}
          icon={Users}
          gradient="gradient-primary"
        />
        <StatsCard
          title="New Leads"
          value={stats.new}
          icon={Target}
          gradient="gradient-warning"
          change="This week"
          changeType="neutral"
        />
        <StatsCard
          title="Converted"
          value={stats.converted}
          icon={ArrowUpRight}
          gradient="gradient-success"
        />
        <StatsCard
          title="Conversion Rate"
          value={`${stats.conversionRate}%`}
          icon={BarChart3}
          gradient="gradient-primary"
        />
      </div>

      {/* Features */}
      {leads.length === 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            title="Lead Tracking"
            description="Capture and organize leads from multiple sources"
            icon={Users}
            gradient="gradient-primary"
          />
          <FeatureCard
            title="Pipeline Management"
            description="Move leads through your sales pipeline"
            icon={Target}
            gradient="gradient-success"
          />
          <FeatureCard
            title="Growth Analytics"
            description="Measure and optimize your conversion rates"
            icon={BarChart3}
            gradient="gradient-warning"
          />
        </div>
      )}

      {/* Leads List */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Leads</CardTitle>
            <CardDescription>Manage your sales pipeline</CardDescription>
          </div>
          <Button variant="outline" size="sm">
            <Filter size={14} className="mr-2" />
            Filter
          </Button>
        </CardHeader>
        <CardContent>
          {leads.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center mx-auto mb-4">
                <Users className="text-white" size={28} />
              </div>
              <h3 className="font-semibold text-lg mb-2">No Leads Yet</h3>
              <p className="text-gray-500 mb-4">Start tracking your potential customers</p>
              <Button onClick={() => setShowCreateDialog(true)} className="gradient-primary border-0">
                <Plus className="mr-2" size={18} />
                Add Your First Lead
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {leads.map((lead) => (
                <div 
                  key={lead.id} 
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-xl hover:border-purple-300 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center">
                      <span className="text-white font-semibold">
                        {lead.name?.charAt(0)?.toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <h4 className="font-medium">{lead.name}</h4>
                      <div className="flex items-center space-x-3 text-sm text-gray-500">
                        {lead.email && (
                          <span className="flex items-center">
                            <Mail size={12} className="mr-1" />
                            {lead.email}
                          </span>
                        )}
                        {lead.phone && (
                          <span className="flex items-center">
                            <Phone size={12} className="mr-1" />
                            {lead.phone}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-xs text-gray-500">{lead.source}</span>
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(lead.status)}`}>
                      {lead.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Lead Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add New Lead</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreateLead} className="space-y-4">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={newLead.name}
                onChange={(e) => setNewLead({ ...newLead, name: e.target.value })}
                placeholder="John Doe"
                required
              />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={newLead.email}
                onChange={(e) => setNewLead({ ...newLead, email: e.target.value })}
                placeholder="john@example.com"
              />
            </div>
            <div>
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                value={newLead.phone}
                onChange={(e) => setNewLead({ ...newLead, phone: e.target.value })}
                placeholder="+1 (555) 123-4567"
              />
            </div>
            <div>
              <Label htmlFor="source">Source</Label>
              <Select
                value={newLead.source}
                onValueChange={(value) => setNewLead({ ...newLead, source: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="WEBSITE">Website</SelectItem>
                  <SelectItem value="REFERRAL">Referral</SelectItem>
                  <SelectItem value="SOCIAL">Social Media</SelectItem>
                  <SelectItem value="ADS">Advertising</SelectItem>
                  <SelectItem value="OTHER">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={creating} className="gradient-primary border-0">
                {creating ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Adding...</>
                ) : (
                  'Add Lead'
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
