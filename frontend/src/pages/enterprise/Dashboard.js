import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader, StatsCard, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  LayoutDashboard, 
  Lightbulb, 
  FileText, 
  Users, 
  TrendingUp, 
  Activity,
  Globe,
  DollarSign,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { Link } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function Dashboard() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [stats, setStats] = useState({
    genesisProjects: 0,
    invoices: 0,
    unpaidInvoices: 0,
    leads: 0,
    websites: 0
  });
  const [recentEvents, setRecentEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (currentWorkspace) {
      loadDashboardData();
    } else {
      setLoading(false);
    }
  }, [currentWorkspace]);

  const loadDashboardData = async () => {
    try {
      const headers = getHeaders();

      // Load projects
      const projectsRes = await axios.get(
        `${API_URL}/workspaces/${currentWorkspace.id}/projects`,
        { headers }
      );
      const genesisProjects = projectsRes.data.filter(p => p.type === 'GENESIS');

      // Load invoices
      const invoicesRes = await axios.get(`${API_URL}/navigator/invoices`, { headers });
      const unpaid = invoicesRes.data.filter(inv => inv.status !== 'PAID' && inv.status !== 'CANCELLED');

      // Load leads
      const leadsRes = await axios.get(`${API_URL}/growth/leads`, { headers });

      // Load websites
      const websitesRes = await axios.get(`${API_URL}/websites`, { headers });

      // Load recent events
      const eventsRes = await axios.get(`${API_URL}/intel/events?limit=10`, { headers });

      setStats({
        genesisProjects: genesisProjects.length,
        invoices: invoicesRes.data.length,
        unpaidInvoices: unpaid.length,
        leads: leadsRes.data.length,
        websites: websitesRes.data?.length || 0
      });

      setRecentEvents(eventsRes.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (!currentWorkspace) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="no-workspace">
        <Card className="max-w-md">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center mx-auto mb-4">
              <LayoutDashboard className="text-white" size={28} />
            </div>
            <h2 className="text-2xl font-bold mb-2">No Workspace Selected</h2>
            <p className="text-gray-600 mb-4">
              Please create a workspace to get started using Enterprate OS.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-slide-in" data-testid="dashboard">
      <PageHeader
        icon={LayoutDashboard}
        title={`Welcome back!`}
        description={`Here's what's happening with ${currentWorkspace?.name}`}
      />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Business Ideas"
          value={stats.genesisProjects}
          icon={Lightbulb}
          gradient="gradient-warning"
          to="/idea-discovery"
          change="+2 this week"
          changeType="positive"
        />
        <StatsCard
          title="Total Invoices"
          value={stats.invoices}
          subtitle={`${stats.unpaidInvoices} unpaid`}
          icon={DollarSign}
          gradient="gradient-success"
          to="/finance-automation"
        />
        <StatsCard
          title="Active Leads"
          value={stats.leads}
          icon={Users}
          gradient="gradient-primary"
          to="/growth"
          change="+5 new"
          changeType="positive"
        />
        <StatsCard
          title="Websites"
          value={stats.websites}
          icon={Globe}
          to="/website-setup"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <FeatureCard
          title="Validate a New Idea"
          description="Use AI to analyze and score your next business concept"
          icon={Sparkles}
          to="/idea-discovery"
          gradient="gradient-primary"
        />
        <FeatureCard
          title="Create Invoice"
          description="Generate professional invoices for your clients"
          icon={FileText}
          to="/finance-automation"
          gradient="gradient-success"
        />
        <FeatureCard
          title="Track Growth"
          description="Monitor leads and marketing performance"
          icon={TrendingUp}
          to="/growth"
          gradient="gradient-warning"
        />
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center">
            <Activity className="mr-2 text-purple-600" size={20} />
            Recent Activity
          </CardTitle>
          <Link to="/intelligence-graph">
            <Button variant="ghost" size="sm">
              View All <ArrowRight size={16} className="ml-1" />
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          {recentEvents.length === 0 ? (
            <div className="text-center py-8">
              <Activity className="mx-auto text-gray-300 mb-3" size={40} />
              <p className="text-gray-500">No recent activity</p>
              <p className="text-sm text-gray-400">Your activity will appear here as you use the platform</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentEvents.map((event, index) => (
                <div
                  key={event.id || index}
                  className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                  data-testid={`event-${index}`}
                >
                  <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="font-medium text-sm text-gray-900">
                      {formatEventType(event.type)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(event.occurredAt).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function formatEventType(type) {
  const formatted = type.replace(/_/g, ' ').replace(/\./g, ' - ');
  return formatted.charAt(0).toUpperCase() + formatted.slice(1);
}
