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
  BarChart3, 
  Eye,
  Users,
  Target,
  TrendingUp,
  Globe,
  ExternalLink,
  Loader2,
  ArrowUpRight,
  ArrowDownRight,
  Monitor,
  Smartphone,
  Tablet,
  Clock,
  Mail,
  MapPin
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const DEVICE_ICONS = {
  desktop: Monitor,
  mobile: Smartphone,
  tablet: Tablet
};

// Moved outside of component to avoid re-creation on each render
const StatCard = ({ title, value, icon: Icon, trend, subtitle }) => (
  <Card>
    <CardContent className="pt-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-2 rounded-lg ${trend > 0 ? 'bg-green-100' : trend < 0 ? 'bg-red-100' : 'bg-gray-100'}`}>
          <Icon className={trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-600'} size={20} />
        </div>
      </div>
      {trend !== undefined && (
        <div className={`flex items-center gap-1 mt-2 text-sm ${trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-500'}`}>
          {trend > 0 ? <ArrowUpRight size={14} /> : trend < 0 ? <ArrowDownRight size={14} /> : null}
          <span>{Math.abs(trend)}% vs previous period</span>
        </div>
      )}
    </CardContent>
  </Card>
);

const SimpleBarChart = ({ data, valueKey, labelKey, maxValue }) => {
  const max = maxValue || Math.max(...data.map(d => d[valueKey]), 1);
  return (
    <div className="space-y-2">
      {data.map((item, index) => (
        <div key={index} className="flex items-center gap-3">
          <div className="w-24 text-sm text-gray-600 truncate">{item[labelKey]}</div>
          <div className="flex-1 h-6 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all"
              style={{ width: `${(item[valueKey] / max) * 100}%` }}
            />
          </div>
          <div className="w-16 text-sm font-medium text-right">{item[valueKey].toLocaleString()}</div>
        </div>
      ))}
    </div>
  );
};

export default function WebsiteAnalytics() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [selectedWebsite, setSelectedWebsite] = useState(null);
  const [websiteAnalytics, setWebsiteAnalytics] = useState(null);
  const [period, setPeriod] = useState('30');
  const [activeTab, setActiveTab] = useState('overview');

  const loadOverview = useCallback(async () => {
    if (!currentWorkspace) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/website-analytics/overview`, {
        headers: getHeaders(),
        params: { days: parseInt(period) }
      });
      setOverview(response.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace, getHeaders, period]);

  const loadWebsiteAnalytics = useCallback(async (websiteId) => {
    try {
      const response = await axios.get(`${API_URL}/website-analytics/website/${websiteId}`, {
        headers: getHeaders(),
        params: { days: parseInt(period) }
      });
      setWebsiteAnalytics(response.data);
    } catch (error) {
      console.error('Failed to load website analytics:', error);
      toast.error('Failed to load analytics');
    }
  }, [getHeaders, period]);

  useEffect(() => {
    loadOverview();
  }, [loadOverview]);

  useEffect(() => {
    if (selectedWebsite) {
      loadWebsiteAnalytics(selectedWebsite.websiteId);
    }
  }, [selectedWebsite, loadWebsiteAnalytics]);

  const selectWebsite = (website) => {
    setSelectedWebsite(website);
    setActiveTab('details');
  };

  if (loading) {
            <div className="w-16 text-sm font-medium text-right">{item[valueKey].toLocaleString()}</div>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="loading-spinner">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-slide-in" data-testid="website-analytics-page">
      <PageHeader
        icon={BarChart3}
        title="Website Analytics"
        description="Track visits, leads, and conversions across your landing pages"
        actions={
          <Select value={period} onValueChange={setPeriod}>
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
              <SelectItem value="365">Last year</SelectItem>
            </SelectContent>
          </Select>
        }
      />

      {overview && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <StatCard 
              title="Total Websites" 
              value={overview.summary.totalWebsites} 
              icon={Globe}
              subtitle={`${overview.summary.deployedWebsites} deployed`}
            />
            <StatCard 
              title="Page Views" 
              value={overview.summary.totalPageViews.toLocaleString()} 
              icon={Eye}
            />
            <StatCard 
              title="Unique Visitors" 
              value={overview.summary.totalVisitors.toLocaleString()} 
              icon={Users}
            />
            <StatCard 
              title="Conversions" 
              value={overview.summary.totalConversions.toLocaleString()} 
              icon={Target}
            />
            <StatCard 
              title="Conversion Rate" 
              value={`${overview.summary.averageConversionRate}%`} 
              icon={TrendingUp}
            />
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="overview" className="flex items-center gap-2">
                <BarChart3 size={16} />
                Overview
              </TabsTrigger>
              <TabsTrigger value="details" className="flex items-center gap-2" disabled={!selectedWebsite}>
                <Eye size={16} />
                Website Details
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Website Performance</CardTitle>
                  <CardDescription>Click on a website to see detailed analytics</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-3 px-4 font-medium text-gray-600">Website</th>
                          <th className="text-right py-3 px-4 font-medium text-gray-600">Status</th>
                          <th className="text-right py-3 px-4 font-medium text-gray-600">Page Views</th>
                          <th className="text-right py-3 px-4 font-medium text-gray-600">Visitors</th>
                          <th className="text-right py-3 px-4 font-medium text-gray-600">Leads</th>
                          <th className="text-right py-3 px-4 font-medium text-gray-600">Conv. Rate</th>
                          <th className="text-right py-3 px-4 font-medium text-gray-600">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {overview.websites.map((website) => (
                          <tr 
                            key={website.websiteId} 
                            className="border-b hover:bg-gray-50 cursor-pointer transition-colors"
                            onClick={() => selectWebsite(website)}
                            data-testid={`website-row-${website.websiteId}`}
                          >
                            <td className="py-3 px-4">
                              <div>
                                <p className="font-medium">{website.name}</p>
                                {website.deploymentUrl && (
                                  <p className="text-xs text-gray-400 truncate max-w-[200px]">{website.deploymentUrl}</p>
                                )}
                              </div>
                            </td>
                            <td className="py-3 px-4 text-right">
                              <Badge className={
                                website.status === 'deployed' 
                                  ? 'bg-green-100 text-green-700' 
                                  : 'bg-gray-100 text-gray-700'
                              }>
                                {website.status}
                              </Badge>
                            </td>
                            <td className="py-3 px-4 text-right font-medium">{website.pageViews.toLocaleString()}</td>
                            <td className="py-3 px-4 text-right">{website.visitors.toLocaleString()}</td>
                            <td className="py-3 px-4 text-right">{website.leads}</td>
                            <td className="py-3 px-4 text-right">
                              <span className={website.conversionRate > 0 ? 'text-green-600 font-medium' : ''}>
                                {website.conversionRate}%
                              </span>
                            </td>
                            <td className="py-3 px-4 text-right">
                              {website.deploymentUrl && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    window.open(website.deploymentUrl, '_blank');
                                  }}
                                >
                                  <ExternalLink size={14} />
                                </Button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    
                    {overview.websites.length === 0 && (
                      <div className="py-12 text-center text-gray-500">
                        <Globe className="mx-auto mb-3 text-gray-300" size={40} />
                        <p>No websites found</p>
                        <Button className="mt-3" onClick={() => window.location.href = '/ai-website-builder'}>
                          Create Your First Website
                        </Button>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="details" className="mt-6">
              {selectedWebsite && websiteAnalytics ? (
                <div className="space-y-6">
                  <Card className="bg-gradient-to-r from-indigo-50 to-purple-50">
                    <CardContent className="py-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h2 className="text-xl font-bold text-indigo-900">{selectedWebsite.name}</h2>
                          {selectedWebsite.deploymentUrl && (
                            <a 
                              href={selectedWebsite.deploymentUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-indigo-600 hover:underline flex items-center gap-1"
                            >
                              {selectedWebsite.deploymentUrl} <ExternalLink size={12} />
                            </a>
                          )}
                        </div>
                        <Button variant="outline" onClick={() => { setSelectedWebsite(null); setActiveTab('overview'); }}>
                          Back to Overview
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <StatCard title="Page Views" value={websiteAnalytics.summary.pageViews.toLocaleString()} icon={Eye} />
                    <StatCard title="Unique Visitors" value={websiteAnalytics.summary.uniqueVisitors.toLocaleString()} icon={Users} />
                    <StatCard title="Conversions" value={websiteAnalytics.summary.conversions.toLocaleString()} icon={Target} />
                    <StatCard title="Conversion Rate" value={`${websiteAnalytics.summary.conversionRate}%`} icon={TrendingUp} />
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Daily Trend */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Daily Page Views</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {websiteAnalytics.dailyData.length > 0 ? (
                          <div className="h-48 flex items-end gap-1">
                            {websiteAnalytics.dailyData.slice(-14).map((day, index) => {
                              const max = Math.max(...websiteAnalytics.dailyData.map(d => d.pageViews), 1);
                              const height = (day.pageViews / max) * 100;
                              return (
                                <div key={index} className="flex-1 flex flex-col items-center gap-1">
                                  <div 
                                    className="w-full bg-indigo-500 rounded-t hover:bg-indigo-600 transition-colors"
                                    style={{ height: `${height}%`, minHeight: day.pageViews > 0 ? '4px' : '0' }}
                                    title={`${day.date}: ${day.pageViews} views`}
                                  />
                                  <span className="text-[10px] text-gray-400 transform -rotate-45 origin-top-left">
                                    {new Date(day.date).getDate()}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <div className="h-48 flex items-center justify-center text-gray-400">
                            No data available
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    {/* Devices */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Devices</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {Object.entries(websiteAnalytics.devices).map(([device, count]) => {
                            const DeviceIcon = DEVICE_ICONS[device] || Monitor;
                            const total = Object.values(websiteAnalytics.devices).reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                            return (
                              <div key={device} className="flex items-center gap-4">
                                <div className="p-2 bg-gray-100 rounded-lg">
                                  <DeviceIcon size={20} className="text-gray-600" />
                                </div>
                                <div className="flex-1">
                                  <div className="flex justify-between mb-1">
                                    <span className="capitalize font-medium">{device}</span>
                                    <span className="text-gray-500">{percentage}%</span>
                                  </div>
                                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                                    <div 
                                      className="h-full bg-indigo-500 rounded-full"
                                      style={{ width: `${percentage}%` }}
                                    />
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                          {Object.keys(websiteAnalytics.devices).length === 0 && (
                            <p className="text-gray-400 text-center py-4">No device data</p>
                          )}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Top Referrers */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Top Referrers</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {websiteAnalytics.referrers.length > 0 ? (
                          <SimpleBarChart 
                            data={websiteAnalytics.referrers} 
                            valueKey="count" 
                            labelKey="source"
                          />
                        ) : (
                          <p className="text-gray-400 text-center py-4">No referrer data</p>
                        )}
                      </CardContent>
                    </Card>

                    {/* Top Countries */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base flex items-center gap-2">
                          <MapPin size={16} />
                          Top Countries
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        {websiteAnalytics.countries.length > 0 ? (
                          <SimpleBarChart 
                            data={websiteAnalytics.countries} 
                            valueKey="count" 
                            labelKey="country"
                          />
                        ) : (
                          <p className="text-gray-400 text-center py-4">No country data</p>
                        )}
                      </CardContent>
                    </Card>
                  </div>

                  {/* Recent Leads */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <Mail size={16} />
                        Recent Leads
                      </CardTitle>
                      <CardDescription>Leads captured from your landing page</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {websiteAnalytics.recentLeads.length > 0 ? (
                        <div className="divide-y">
                          {websiteAnalytics.recentLeads.map((lead) => (
                            <div key={lead.id} className="py-3 flex items-center justify-between">
                              <div>
                                <p className="font-medium">{lead.name}</p>
                                <p className="text-sm text-gray-500">{lead.email}</p>
                              </div>
                              <div className="text-sm text-gray-400 flex items-center gap-1">
                                <Clock size={14} />
                                {new Date(lead.createdAt).toLocaleDateString()}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-400 text-center py-8">No leads captured yet</p>
                      )}
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <Card className="p-12 text-center">
                  <BarChart3 className="mx-auto text-gray-300 mb-4" size={48} />
                  <h3 className="text-lg font-medium text-gray-700">No Website Selected</h3>
                  <p className="text-gray-500 mt-1">Select a website from the overview to see detailed analytics</p>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
}
