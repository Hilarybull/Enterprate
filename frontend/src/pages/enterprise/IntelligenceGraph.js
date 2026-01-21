import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Activity, 
  TrendingUp,
  Calendar,
  FileText,
  Package,
  Receipt,
  Users,
  Globe,
  Palette,
  DollarSign,
  ChevronRight,
  Loader2,
  BarChart3,
  Clock,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// Entity type configurations
const ENTITY_CONFIG = {
  catalogue: { icon: Package, color: 'bg-blue-100 text-blue-700', label: 'Catalogue' },
  invoice: { icon: Receipt, color: 'bg-green-100 text-green-700', label: 'Invoice' },
  document: { icon: FileText, color: 'bg-purple-100 text-purple-700', label: 'Document' },
  expense: { icon: DollarSign, color: 'bg-amber-100 text-amber-700', label: 'Expense' },
  customer: { icon: Users, color: 'bg-pink-100 text-pink-700', label: 'Customer' },
  website: { icon: Globe, color: 'bg-indigo-100 text-indigo-700', label: 'Website' },
  brand: { icon: Palette, color: 'bg-cyan-100 text-cyan-700', label: 'Brand' },
  finance: { icon: TrendingUp, color: 'bg-emerald-100 text-emerald-700', label: 'Finance' }
};

export default function IntelligenceGraph() {
  const { currentWorkspace, getHeaders, loading: workspaceLoading } = useWorkspace();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState(null);
  const [events, setEvents] = useState([]);
  const [activitySummary, setActivitySummary] = useState([]);
  const [selectedEntityType, setSelectedEntityType] = useState('all');
  const [periodType, setPeriodType] = useState('daily');
  const [error, setError] = useState(null);

  // Load insights
  const loadInsights = useCallback(async () => {
    if (!currentWorkspace) return;
    
    setLoading(true);
    setError(null);
    try {
      const headers = getHeaders();
      const [insightsRes, eventsRes, summaryRes] = await Promise.all([
        axios.get(`${API_URL}/intelligence/insights`, { headers }),
        axios.get(`${API_URL}/intelligence/events?limit=50`, { headers }),
        axios.get(`${API_URL}/intelligence/summary?period_type=${periodType}&periods=7`, { headers })
      ]);
      
      setInsights(insightsRes.data);
      setEvents(eventsRes.data || []);
      setActivitySummary(summaryRes.data || []);
    } catch (err) {
      console.error('Failed to load intelligence data:', err);
      setError(err.message || 'Failed to load analytics');
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace, getHeaders, periodType]);

  useEffect(() => {
    if (currentWorkspace) {
      loadInsights();
    }
  }, [currentWorkspace, loadInsights]);

  // Show loading while workspace is loading
  if (workspaceLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  // Show error state
  if (error && !loading) {
    return (
      <div className="space-y-6 animate-slide-in" data-testid="intelligence-graph-page">
        <PageHeader
          icon={Activity}
          title="Intelligence Graph"
          description="Track activities, analyze patterns, and gain insights across your business"
        />
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-red-500 mb-4">Failed to load data: {error}</p>
            <Button onClick={loadInsights}>Try Again</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Filter events by entity type
  const filteredEvents = selectedEntityType === 'all' 
    ? events 
    : events.filter(e => e.entityType === selectedEntityType);

  // Format event description
  const formatEventDescription = (event) => {
    const { eventType, entityType, data } = event;
    
    switch (`${entityType}_${eventType}`) {
      case 'invoice_created':
        return `Created invoice ${data?.invoiceNumber || ''} for ${data?.clientName || 'client'} (${data?.currency || '£'}${data?.total?.toFixed(2) || '0'})`;
      case 'invoice_sent':
        return `Sent invoice ${data?.invoiceNumber || ''} to ${data?.recipient || 'client'}`;
      case 'invoice_paid':
        return `Invoice ${data?.invoiceNumber || ''} marked as paid`;
      case 'document_generated':
        return `Generated ${data?.documentType?.replace(/_/g, ' ') || 'document'}: ${data?.title || ''}`;
      case 'document_saved':
        return `Saved document: ${data?.title || ''}`;
      case 'catalogue_bulk_added':
        return `Added ${data?.count || 0} items to catalogue`;
      case 'catalogue_item_added':
        return `Added item: ${data?.name || ''}`;
      case 'brand_logo_uploaded':
        return `Uploaded brand logo: ${data?.filename || ''}`;
      case 'finance_autofill_used':
        return `Used tax auto-fill for ${data?.taxYear || 'tax year'}`;
      case 'website_generated':
        return `Generated website: ${data?.title || ''}`;
      case 'website_published':
        return `Published website to ${data?.provider || 'hosting'}`;
      default:
        return `${eventType.replace(/_/g, ' ')} - ${entityType}`;
    }
  };

  // Format time ago
  const formatTimeAgo = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getEntityIcon = (entityType) => {
    const config = ENTITY_CONFIG[entityType] || { icon: Activity };
    const Icon = config.icon;
    return <Icon size={16} />;
  };

  const getEntityBadge = (entityType) => {
    const config = ENTITY_CONFIG[entityType] || { color: 'bg-gray-100 text-gray-700', label: entityType };
    return (
      <Badge className={config.color}>
        {config.label}
      </Badge>
    );
  };

  return (
    <div className="space-y-6 animate-slide-in" data-testid="intelligence-graph-page">
      <PageHeader
        icon={Activity}
        title="Intelligence Graph"
        description="Track activities, analyze patterns, and gain insights across your business"
        actions={
          <Button variant="outline" onClick={loadInsights} disabled={loading}>
            <RefreshCw className={`mr-2 ${loading ? 'animate-spin' : ''}`} size={16} />
            Refresh
          </Button>
        }
      />

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">
            <BarChart3 size={16} className="mr-2" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="activity">
            <Clock size={16} className="mr-2" />
            Activity Feed
          </TabsTrigger>
          <TabsTrigger value="analytics">
            <TrendingUp size={16} className="mr-2" />
            Analytics
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6 mt-4">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
            </div>
          ) : (
            <>
              {/* Stats Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-500">Today&apos;s Activity</p>
                        <p className="text-2xl font-bold">{insights?.today?.total || 0}</p>
                      </div>
                      <div className="p-3 bg-indigo-100 rounded-lg">
                        <Activity className="text-indigo-600" size={24} />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-500">This Month</p>
                        <p className="text-2xl font-bold">{insights?.month?.total || 0}</p>
                      </div>
                      <div className="p-3 bg-green-100 rounded-lg">
                        <Calendar className="text-green-600" size={24} />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-500">Invoices</p>
                        <p className="text-2xl font-bold">{insights?.entityCounts?.invoice || 0}</p>
                      </div>
                      <div className="p-3 bg-blue-100 rounded-lg">
                        <Receipt className="text-blue-600" size={24} />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-500">Catalogue Items</p>
                        <p className="text-2xl font-bold">{insights?.entityCounts?.catalogue || 0}</p>
                      </div>
                      <div className="p-3 bg-purple-100 rounded-lg">
                        <Package className="text-purple-600" size={24} />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Entity Counts */}
              <Card>
                <CardHeader>
                  <CardTitle>Entity Overview</CardTitle>
                  <CardDescription>Total counts across all entity types</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(insights?.entityCounts || {}).map(([type, count]) => {
                      const config = ENTITY_CONFIG[type] || { icon: Activity, label: type, color: 'bg-gray-100 text-gray-700' };
                      const Icon = config.icon;
                      return (
                        <div key={type} className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
                          <div className={`p-2 rounded-lg ${config.color.split(' ')[0]}`}>
                            <Icon className={config.color.split(' ')[1]} size={20} />
                          </div>
                          <div>
                            <p className="text-sm text-gray-500 capitalize">{config.label}</p>
                            <p className="text-lg font-semibold">{count}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>Latest events across your workspace</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {insights?.recentActivity?.slice(0, 10).map((event, index) => (
                      <div key={event.id || index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-lg ${(ENTITY_CONFIG[event.entityType]?.color || 'bg-gray-100 text-gray-700').split(' ')[0]}`}>
                            {getEntityIcon(event.entityType)}
                          </div>
                          <div>
                            <p className="text-sm font-medium">{formatEventDescription(event)}</p>
                            <p className="text-xs text-gray-500">{formatTimeAgo(event.occurredAt)}</p>
                          </div>
                        </div>
                        {getEntityBadge(event.entityType)}
                      </div>
                    ))}
                    {(!insights?.recentActivity || insights.recentActivity.length === 0) && (
                      <p className="text-center text-gray-500 py-8">No recent activity</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* Activity Feed Tab */}
        <TabsContent value="activity" className="space-y-4 mt-4">
          <div className="flex items-center gap-4">
            <Select value={selectedEntityType} onValueChange={setSelectedEntityType}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Activities</SelectItem>
                <SelectItem value="invoice">Invoices</SelectItem>
                <SelectItem value="document">Documents</SelectItem>
                <SelectItem value="catalogue">Catalogue</SelectItem>
                <SelectItem value="brand">Brand</SelectItem>
                <SelectItem value="expense">Expenses</SelectItem>
                <SelectItem value="website">Websites</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-gray-500">{filteredEvents.length} events</p>
          </div>

          <Card>
            <CardContent className="p-0">
              <div className="divide-y">
                {filteredEvents.map((event, index) => (
                  <div key={event.id || index} className="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-lg ${(ENTITY_CONFIG[event.entityType]?.color || 'bg-gray-100 text-gray-700').split(' ')[0]}`}>
                        {getEntityIcon(event.entityType)}
                      </div>
                      <div>
                        <p className="font-medium">{formatEventDescription(event)}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <p className="text-xs text-gray-500">{formatTimeAgo(event.occurredAt)}</p>
                          <span className="text-xs text-gray-300">•</span>
                          <p className="text-xs text-gray-500 capitalize">{event.eventType.replace(/_/g, ' ')}</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getEntityBadge(event.entityType)}
                      <ChevronRight size={16} className="text-gray-400" />
                    </div>
                  </div>
                ))}
                {filteredEvents.length === 0 && (
                  <div className="p-12 text-center">
                    <Activity className="mx-auto text-gray-300 mb-4" size={48} />
                    <p className="text-gray-500">No activities found</p>
                    <p className="text-sm text-gray-400 mt-1">Start using the platform to see your activity here</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6 mt-4">
          <div className="flex items-center gap-4">
            <Select value={periodType} onValueChange={setPeriodType}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Activity Trend</CardTitle>
              <CardDescription>
                {periodType === 'daily' ? 'Last 7 days' : 'Last 7 months'} of activity
              </CardDescription>
            </CardHeader>
            <CardContent>
              {activitySummary.length > 0 ? (
                <div className="space-y-4">
                  {[...activitySummary].reverse().map((summary, index) => (
                    <div key={summary.period || index} className="flex items-center gap-4">
                      <div className="w-24 text-sm text-gray-500">{summary.period}</div>
                      <div className="flex-1 h-8 bg-gray-100 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min((summary.counts?.total || 0) * 10, 100)}%` }}
                        />
                      </div>
                      <div className="w-12 text-right font-medium">{summary.counts?.total || 0}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No activity data available yet</p>
              )}
            </CardContent>
          </Card>

          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Top Activities</CardTitle>
                <CardDescription>Most common actions this month</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(insights?.month?.breakdown || {})
                    .filter(([key]) => key !== 'total')
                    .slice(0, 5)
                    .map(([entityType, data]) => {
                      const config = ENTITY_CONFIG[entityType] || { label: entityType };
                      const total = typeof data === 'object' ? data.total || 0 : data;
                      return (
                        <div key={entityType} className="flex items-center justify-between">
                          <span className="capitalize">{config.label}</span>
                          <Badge variant="outline">{total}</Badge>
                        </div>
                      );
                    })}
                  {Object.keys(insights?.month?.breakdown || {}).length <= 1 && (
                    <p className="text-sm text-gray-500">No activity breakdown available</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Stats</CardTitle>
                <CardDescription>Key metrics at a glance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Total Documents</span>
                    <span className="font-semibold">{insights?.entityCounts?.document || 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Total Invoices</span>
                    <span className="font-semibold">{insights?.entityCounts?.invoice || 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Catalogue Items</span>
                    <span className="font-semibold">{insights?.entityCounts?.catalogue || 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Customers</span>
                    <span className="font-semibold">{insights?.entityCounts?.customer || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
