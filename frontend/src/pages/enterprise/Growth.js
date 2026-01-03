import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader, StatsCard, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
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
  Filter,
  Megaphone,
  Share2,
  Calendar,
  Sparkles,
  Trash2,
  Eye,
  DollarSign,
  Percent,
  Brain,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Activity,
  Zap,
  TrendingDown,
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const campaignTypes = [
  { value: 'email', label: 'Email Campaign' },
  { value: 'social', label: 'Social Media' },
  { value: 'content', label: 'Content Marketing' },
  { value: 'ppc', label: 'PPC/Ads' },
  { value: 'event', label: 'Event' },
  { value: 'other', label: 'Other' },
];

const socialPlatforms = [
  { value: 'twitter', label: 'Twitter/X' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'instagram', label: 'Instagram' },
];

const toneOptions = [
  { value: 'professional', label: 'Professional' },
  { value: 'casual', label: 'Casual' },
  { value: 'humorous', label: 'Humorous' },
  { value: 'inspiring', label: 'Inspiring' },
];

export default function Growth() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [activeTab, setActiveTab] = useState('agent');
  
  // Leads
  const [leads, setLeads] = useState([]);
  const [leadsLoading, setLeadsLoading] = useState(true);
  const [showLeadDialog, setShowLeadDialog] = useState(false);
  const [creatingLead, setCreatingLead] = useState(false);
  const [newLead, setNewLead] = useState({
    name: '', email: '', phone: '', source: 'WEBSITE', status: 'NEW'
  });

  // Campaigns
  const [campaigns, setCampaigns] = useState([]);
  const [showCampaignDialog, setShowCampaignDialog] = useState(false);
  const [creatingCampaign, setCreatingCampaign] = useState(false);
  const [newCampaign, setNewCampaign] = useState({
    name: '', description: '', type: 'other', budget: '', startDate: '', endDate: '', targetAudience: '', goals: '', channels: ''
  });

  // Social Posts
  const [socialPosts, setSocialPosts] = useState([]);
  const [showSocialPostDialog, setShowSocialPostDialog] = useState(false);
  const [showGenerateDialog, setShowGenerateDialog] = useState(false);
  const [creatingSocialPost, setCreatingSocialPost] = useState(false);
  const [generatingPost, setGeneratingPost] = useState(false);
  const [newSocialPost, setNewSocialPost] = useState({
    platform: 'twitter', content: '', scheduledFor: '', hashtags: ''
  });
  const [generateRequest, setGenerateRequest] = useState({
    platform: 'twitter', topic: '', tone: 'professional', includeEmojis: true, includeHashtags: true
  });
  const [generatedPost, setGeneratedPost] = useState(null);

  // Analytics
  const [analytics, setAnalytics] = useState(null);

  // Proactive Growth Agent
  const [performanceData, setPerformanceData] = useState(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [generatingRec, setGeneratingRec] = useState(null);
  const [processingRec, setProcessingRec] = useState(null);

  useEffect(() => {
    if (currentWorkspace) {
      loadLeads();
      loadCampaigns();
      loadSocialPosts();
      loadAnalytics();
      loadPerformanceAnalysis();
      loadRecommendations();
    } else {
      setLeadsLoading(false);
    }
  }, [currentWorkspace]);

  // === LEAD FUNCTIONS ===
  const loadLeads = async () => {
    try {
      const response = await axios.get(`${API_URL}/growth/leads`, { headers: getHeaders() });
      setLeads(response.data || []);
    } catch (error) {
      console.error('Failed to load leads:', error);
    } finally {
      setLeadsLoading(false);
    }
  };

  const handleCreateLead = async (e) => {
    e.preventDefault();
    setCreatingLead(true);
    try {
      await axios.post(`${API_URL}/growth/leads`, newLead, { headers: getHeaders() });
      toast.success('Lead added!');
      setShowLeadDialog(false);
      setNewLead({ name: '', email: '', phone: '', source: 'WEBSITE', status: 'NEW' });
      loadLeads();
      loadAnalytics();
    } catch (error) {
      toast.error('Failed to add lead');
    } finally {
      setCreatingLead(false);
    }
  };

  const handleUpdateLeadStatus = async (leadId, newStatus) => {
    try {
      await axios.patch(`${API_URL}/growth/leads/${leadId}`, { status: newStatus }, { headers: getHeaders() });
      toast.success('Lead updated!');
      loadLeads();
      loadAnalytics();
    } catch (error) {
      toast.error('Failed to update lead');
    }
  };

  // === CAMPAIGN FUNCTIONS ===
  const loadCampaigns = async () => {
    try {
      const response = await axios.get(`${API_URL}/marketing/campaigns`, { headers: getHeaders() });
      setCampaigns(response.data || []);
    } catch (error) {
      console.error('Failed to load campaigns:', error);
    }
  };

  const handleCreateCampaign = async (e) => {
    e.preventDefault();
    setCreatingCampaign(true);
    try {
      await axios.post(`${API_URL}/marketing/campaigns`, {
        ...newCampaign,
        budget: newCampaign.budget ? parseFloat(newCampaign.budget) : null,
        goals: newCampaign.goals ? newCampaign.goals.split(',').map(g => g.trim()) : [],
        channels: newCampaign.channels ? newCampaign.channels.split(',').map(c => c.trim()) : []
      }, { headers: getHeaders() });
      toast.success('Campaign created!');
      setShowCampaignDialog(false);
      setNewCampaign({ name: '', description: '', type: 'other', budget: '', startDate: '', endDate: '', targetAudience: '', goals: '', channels: '' });
      loadCampaigns();
      loadAnalytics();
    } catch (error) {
      toast.error('Failed to create campaign');
    } finally {
      setCreatingCampaign(false);
    }
  };

  const handleUpdateCampaignStatus = async (campaignId, newStatus) => {
    try {
      await axios.patch(`${API_URL}/marketing/campaigns/${campaignId}`, { status: newStatus }, { headers: getHeaders() });
      toast.success('Campaign updated!');
      loadCampaigns();
    } catch (error) {
      toast.error('Failed to update campaign');
    }
  };

  const handleDeleteCampaign = async (campaignId) => {
    try {
      await axios.delete(`${API_URL}/marketing/campaigns/${campaignId}`, { headers: getHeaders() });
      toast.success('Campaign deleted');
      loadCampaigns();
      loadAnalytics();
    } catch (error) {
      toast.error('Failed to delete campaign');
    }
  };

  // === SOCIAL POST FUNCTIONS ===
  const loadSocialPosts = async () => {
    try {
      const response = await axios.get(`${API_URL}/marketing/social-posts`, { headers: getHeaders() });
      setSocialPosts(response.data || []);
    } catch (error) {
      console.error('Failed to load social posts:', error);
    }
  };

  const handleCreateSocialPost = async (e) => {
    e.preventDefault();
    setCreatingSocialPost(true);
    try {
      await axios.post(`${API_URL}/marketing/social-posts`, {
        ...newSocialPost,
        hashtags: newSocialPost.hashtags ? newSocialPost.hashtags.split(',').map(h => h.trim().replace('#', '')) : []
      }, { headers: getHeaders() });
      toast.success('Post created!');
      setShowSocialPostDialog(false);
      setNewSocialPost({ platform: 'twitter', content: '', scheduledFor: '', hashtags: '' });
      loadSocialPosts();
    } catch (error) {
      toast.error('Failed to create post');
    } finally {
      setCreatingSocialPost(false);
    }
  };

  const handleGeneratePost = async (e) => {
    e.preventDefault();
    setGeneratingPost(true);
    setGeneratedPost(null);
    try {
      const response = await axios.post(`${API_URL}/marketing/social-posts/generate`, generateRequest, { headers: getHeaders() });
      
      if (response.data && response.data.content) {
        setGeneratedPost(response.data);
        if (response.data.generated) {
          toast.success('AI post generated successfully!');
        } else {
          toast.info('Generated a fallback post. Try again for AI-generated content.');
        }
      } else {
        toast.warning('Generated post is empty. Please try again.');
      }
    } catch (error) {
      console.error('Post generation error:', error.response?.data || error.message);
      const errorMessage = error.response?.data?.detail || 'Failed to generate post';
      toast.error(errorMessage);
    } finally {
      setGeneratingPost(false);
    }
  };

  const handleUseGeneratedPost = () => {
    if (generatedPost) {
      setNewSocialPost({
        platform: generatedPost.platform,
        content: generatedPost.content,
        hashtags: generatedPost.hashtags?.join(', ') || '',
        scheduledFor: ''
      });
      setShowGenerateDialog(false);
      setShowSocialPostDialog(true);
    }
  };

  const handleDeleteSocialPost = async (postId) => {
    try {
      await axios.delete(`${API_URL}/marketing/social-posts/${postId}`, { headers: getHeaders() });
      toast.success('Post deleted');
      loadSocialPosts();
    } catch (error) {
      toast.error('Failed to delete post');
    }
  };

  // === ANALYTICS ===
  const loadAnalytics = async () => {
    try {
      const response = await axios.get(`${API_URL}/marketing/analytics`, { headers: getHeaders() });
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    }
  };

  // === PROACTIVE GROWTH AGENT ===
  const loadPerformanceAnalysis = async () => {
    setLoadingAnalysis(true);
    try {
      const response = await axios.get(`${API_URL}/growth/agent/analyze`, { headers: getHeaders() });
      setPerformanceData(response.data);
    } catch (error) {
      console.error('Failed to load performance analysis:', error);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const loadRecommendations = async () => {
    try {
      const response = await axios.get(`${API_URL}/growth/agent/recommendations`, { headers: getHeaders() });
      setRecommendations(response.data || []);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    }
  };

  const handleGenerateRecommendation = async (alertType, alertId) => {
    setGeneratingRec(alertId || alertType);
    try {
      const response = await axios.post(`${API_URL}/growth/agent/recommend`, 
        { alertType, alertId },
        { headers: getHeaders() }
      );
      toast.success('Growth recommendation generated!');
      loadRecommendations();
      return response.data;
    } catch (error) {
      toast.error('Failed to generate recommendation');
    } finally {
      setGeneratingRec(null);
    }
  };

  const handleApproveRecommendation = async (recommendationId) => {
    setProcessingRec(recommendationId);
    try {
      await axios.post(`${API_URL}/growth/agent/approve`,
        { recommendationId },
        { headers: getHeaders() }
      );
      toast.success('Recommendation approved and executed!');
      loadRecommendations();
      loadSocialPosts(); // Refresh social posts in case new ones were created
      loadCampaigns();
    } catch (error) {
      toast.error('Failed to approve recommendation');
    } finally {
      setProcessingRec(null);
    }
  };

  const handleRejectRecommendation = async (recommendationId, reason) => {
    setProcessingRec(recommendationId);
    try {
      await axios.post(`${API_URL}/growth/agent/reject`,
        { recommendationId, reason },
        { headers: getHeaders() }
      );
      toast.success('Recommendation rejected');
      loadRecommendations();
    } catch (error) {
      toast.error('Failed to reject recommendation');
    } finally {
      setProcessingRec(null);
    }
  };

  const getHealthScoreColor = (score) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getHealthScoreBg = (score) => {
    if (score >= 70) return 'bg-green-100';
    if (score >= 40) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'bg-red-100 text-red-700 border-red-200',
      warning: 'bg-yellow-100 text-yellow-700 border-yellow-200',
      info: 'bg-blue-100 text-blue-700 border-blue-200'
    };
    return colors[severity] || colors.info;
  };

  const getSeverityIcon = (severity) => {
    if (severity === 'critical') return <AlertTriangle className="text-red-500" size={18} />;
    if (severity === 'warning') return <AlertTriangle className="text-yellow-500" size={18} />;
    return <Activity className="text-blue-500" size={18} />;
  };

  const getStatusColor = (status) => {
    const colors = {
      NEW: 'bg-blue-100 text-blue-700',
      CONTACTED: 'bg-yellow-100 text-yellow-700',
      QUALIFIED: 'bg-purple-100 text-purple-700',
      CONVERTED: 'bg-green-100 text-green-700',
      LOST: 'bg-gray-100 text-gray-500',
      draft: 'bg-gray-100 text-gray-700',
      scheduled: 'bg-blue-100 text-blue-700',
      active: 'bg-green-100 text-green-700',
      paused: 'bg-yellow-100 text-yellow-700',
      completed: 'bg-purple-100 text-purple-700'
    };
    return colors[status] || colors.draft;
  };

  const getPlatformIcon = (platform) => {
    return Share2; // Simplified - could use specific icons
  };

  if (leadsLoading) {
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
        description="Manage leads, run campaigns, and accelerate your business growth"
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard title="Total Leads" value={analytics?.leads?.totalLeads || 0} icon={Users} gradient="gradient-primary" />
        <StatsCard title="Conversion Rate" value={`${analytics?.leads?.conversionRate || 0}%`} icon={Percent} gradient="gradient-success" />
        <StatsCard title="Active Campaigns" value={analytics?.campaigns?.activeCampaigns || 0} icon={Megaphone} gradient="gradient-warning" />
        <StatsCard title="Total Budget" value={`£${analytics?.campaigns?.totalBudget?.toLocaleString() || 0}`} icon={DollarSign} gradient="gradient-primary" />
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="agent" data-testid="growth-agent-tab">
            <Brain className="mr-2" size={16} /> Growth Agent
          </TabsTrigger>
          <TabsTrigger value="leads">Leads</TabsTrigger>
          <TabsTrigger value="campaigns">Campaigns</TabsTrigger>
          <TabsTrigger value="social">Social Media</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* GROWTH AGENT TAB */}
        <TabsContent value="agent" className="mt-6 space-y-6">
          {/* Performance Overview */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="flex items-center">
                  <Brain className="mr-2 text-purple-600" size={24} />
                  Proactive Growth Agent
                </CardTitle>
                <CardDescription>AI-powered monitoring and growth recommendations</CardDescription>
              </div>
              <Button 
                variant="outline" 
                onClick={loadPerformanceAnalysis}
                disabled={loadingAnalysis}
              >
                {loadingAnalysis ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="mr-2" size={16} />
                )}
                Refresh Analysis
              </Button>
            </CardHeader>
            <CardContent>
              {loadingAnalysis ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
                  <span className="ml-3 text-gray-500">Analyzing business performance...</span>
                </div>
              ) : performanceData ? (
                <div className="space-y-6">
                  {/* Health Score */}
                  <div className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-r from-purple-50 to-blue-50">
                    <div>
                      <p className="text-sm text-gray-600">Business Health Score</p>
                      <div className="flex items-center mt-1">
                        <span className={`text-4xl font-bold ${getHealthScoreColor(performanceData.healthScore)}`}>
                          {performanceData.healthScore}
                        </span>
                        <span className="text-gray-400 text-lg ml-1">/100</span>
                        <span className={`ml-4 px-3 py-1 rounded-full text-sm ${getHealthScoreBg(performanceData.healthScore)} ${getHealthScoreColor(performanceData.healthScore)}`}>
                          {performanceData.status === 'healthy' ? 'Healthy' : performanceData.status === 'warning' ? 'Needs Attention' : 'Critical'}
                        </span>
                      </div>
                    </div>
                    <Activity className={`${getHealthScoreColor(performanceData.healthScore)}`} size={48} />
                  </div>

                  {/* Metrics Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Leads Metric */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600">Lead Generation</span>
                        {performanceData.leads?.trend === 'up' ? (
                          <TrendingUp className="text-green-500" size={16} />
                        ) : performanceData.leads?.trend === 'down' ? (
                          <TrendingDown className="text-red-500" size={16} />
                        ) : (
                          <ArrowRight className="text-gray-400" size={16} />
                        )}
                      </div>
                      <p className="text-2xl font-bold">{performanceData.leads?.currentPeriod || 0}</p>
                      <p className={`text-sm ${performanceData.leads?.percentChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {performanceData.leads?.percentChange >= 0 ? '+' : ''}{performanceData.leads?.percentChange}% vs last month
                      </p>
                    </div>

                    {/* Revenue Metric */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600">Revenue</span>
                        {performanceData.revenue?.trend === 'up' ? (
                          <TrendingUp className="text-green-500" size={16} />
                        ) : performanceData.revenue?.trend === 'down' ? (
                          <TrendingDown className="text-red-500" size={16} />
                        ) : (
                          <ArrowRight className="text-gray-400" size={16} />
                        )}
                      </div>
                      <p className="text-2xl font-bold">£{(performanceData.revenue?.currentRevenue || 0).toLocaleString()}</p>
                      <p className={`text-sm ${performanceData.revenue?.percentChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {performanceData.revenue?.percentChange >= 0 ? '+' : ''}{performanceData.revenue?.percentChange}% vs last month
                      </p>
                    </div>

                    {/* Campaigns Metric */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600">Active Campaigns</span>
                        <Megaphone className="text-purple-500" size={16} />
                      </div>
                      <p className="text-2xl font-bold">{performanceData.campaigns?.activeCampaigns || 0}</p>
                      <p className="text-sm text-gray-500">
                        {performanceData.campaigns?.totalConversions || 0} total conversions
                      </p>
                    </div>
                  </div>

                  {/* Alerts */}
                  {performanceData.alerts?.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="font-semibold flex items-center">
                        <AlertTriangle className="mr-2 text-yellow-500" size={18} />
                        Alerts & Opportunities
                      </h4>
                      {performanceData.alerts.map((alert) => (
                        <div 
                          key={alert.id} 
                          className={`p-4 rounded-lg border ${getSeverityColor(alert.severity)}`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex items-start space-x-3">
                              {getSeverityIcon(alert.severity)}
                              <div>
                                <h5 className="font-medium">{alert.title}</h5>
                                <p className="text-sm mt-1 opacity-80">{alert.message}</p>
                              </div>
                            </div>
                            <Button
                              size="sm"
                              onClick={() => handleGenerateRecommendation(alert.suggestedAction, alert.id)}
                              disabled={generatingRec === alert.id}
                              className="gradient-primary border-0"
                            >
                              {generatingRec === alert.id ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <>
                                  <Zap className="mr-1" size={14} />
                                  {alert.actionLabel || 'Get Recommendation'}
                                </>
                              )}
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {performanceData.alerts?.length === 0 && (
                    <div className="text-center py-8 bg-green-50 rounded-lg">
                      <CheckCircle2 className="mx-auto mb-2 text-green-500" size={48} />
                      <p className="text-green-700 font-medium">All systems healthy!</p>
                      <p className="text-sm text-green-600">No immediate actions required</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Brain className="mx-auto mb-2 text-gray-300" size={48} />
                  <p className="text-gray-500">Click "Refresh Analysis" to analyze your business performance</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Pending Recommendations */}
          {recommendations.filter(r => r.status === 'pending').length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Pending Recommendations</CardTitle>
                <CardDescription>Review and approve AI-generated growth actions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {recommendations.filter(r => r.status === 'pending').map((rec) => (
                  <div key={rec.id} className="p-4 border rounded-lg bg-purple-50 border-purple-200">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-semibold text-purple-800">{rec.recommendation?.title || rec.title}</h4>
                        <p className="text-sm text-purple-700 mt-1">{rec.recommendation?.description || rec.description}</p>
                        <div className="flex items-center space-x-4 mt-3 text-xs text-purple-600">
                          <span>Expected: {rec.recommendation?.expectedOutcome || rec.expectedOutcome}</span>
                          <span>Duration: {rec.recommendation?.duration || rec.duration}</span>
                        </div>
                        {(rec.recommendation?.actions || rec.actions)?.length > 0 && (
                          <div className="mt-3 p-2 bg-white rounded">
                            <p className="text-xs font-medium text-gray-600 mb-1">Proposed Actions:</p>
                            <ul className="text-xs text-gray-500 space-y-1">
                              {(rec.recommendation?.actions || rec.actions).map((action, i) => (
                                <li key={i}>• {action.type}: {action.platform || action.target || action.content_type || 'Execute'}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleRejectRecommendation(rec.id)}
                          disabled={processingRec === rec.id}
                          className="text-red-600 border-red-200 hover:bg-red-50"
                        >
                          <XCircle size={14} className="mr-1" />
                          Reject
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleApproveRecommendation(rec.id)}
                          disabled={processingRec === rec.id}
                          className="gradient-primary border-0"
                        >
                          {processingRec === rec.id ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <>
                              <CheckCircle2 size={14} className="mr-1" />
                              Approve & Execute
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Recommendation History */}
          {recommendations.filter(r => r.status !== 'pending').length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recommendation History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {recommendations.filter(r => r.status !== 'pending').slice(0, 5).map((rec) => (
                    <div key={rec.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        {rec.status === 'approved' ? (
                          <CheckCircle2 className="text-green-500" size={18} />
                        ) : (
                          <XCircle className="text-red-500" size={18} />
                        )}
                        <span className="text-sm">{rec.recommendation?.title || rec.title || 'Recommendation'}</span>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded ${rec.status === 'approved' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {rec.status}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* LEADS TAB */}
        <TabsContent value="leads" className="mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Lead Management</CardTitle>
                <CardDescription>Track and manage your sales pipeline</CardDescription>
              </div>
              <Button onClick={() => setShowLeadDialog(true)} className="gradient-primary border-0">
                <Plus className="mr-2" size={18} /> Add Lead
              </Button>
            </CardHeader>
            <CardContent>
              {leads.length === 0 ? (
                <div className="text-center py-12">
                  <Users className="mx-auto mb-2 text-gray-300" size={48} />
                  <p className="text-gray-500">No leads yet. Add your first lead!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {leads.map((lead) => (
                    <div key={lead.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center">
                          <span className="text-white font-semibold">{lead.name?.charAt(0)?.toUpperCase()}</span>
                        </div>
                        <div>
                          <h4 className="font-medium">{lead.name}</h4>
                          <div className="flex items-center space-x-3 text-sm text-gray-500">
                            {lead.email && <span className="flex items-center"><Mail size={12} className="mr-1" />{lead.email}</span>}
                            {lead.phone && <span className="flex items-center"><Phone size={12} className="mr-1" />{lead.phone}</span>}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className="text-xs text-gray-500">{lead.source}</span>
                        <Select value={lead.status} onValueChange={(v) => handleUpdateLeadStatus(lead.id, v)}>
                          <SelectTrigger className={`w-[120px] h-8 text-xs ${getStatusColor(lead.status)}`}>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="NEW">New</SelectItem>
                            <SelectItem value="CONTACTED">Contacted</SelectItem>
                            <SelectItem value="QUALIFIED">Qualified</SelectItem>
                            <SelectItem value="CONVERTED">Converted</SelectItem>
                            <SelectItem value="LOST">Lost</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* CAMPAIGNS TAB */}
        <TabsContent value="campaigns" className="mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Marketing Campaigns</CardTitle>
                <CardDescription>Plan and track your marketing efforts</CardDescription>
              </div>
              <Button onClick={() => setShowCampaignDialog(true)} className="gradient-primary border-0">
                <Plus className="mr-2" size={18} /> New Campaign
              </Button>
            </CardHeader>
            <CardContent>
              {campaigns.length === 0 ? (
                <div className="text-center py-12">
                  <Megaphone className="mx-auto mb-2 text-gray-300" size={48} />
                  <p className="text-gray-500">No campaigns yet. Create your first campaign!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {campaigns.map((campaign) => (
                    <div key={campaign.id} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center space-x-2">
                            <h4 className="font-semibold">{campaign.name}</h4>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(campaign.status)}`}>
                              {campaign.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mt-1">{campaign.description}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Select value={campaign.status} onValueChange={(v) => handleUpdateCampaignStatus(campaign.id, v)}>
                            <SelectTrigger className="w-[100px] h-8 text-xs">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="draft">Draft</SelectItem>
                              <SelectItem value="scheduled">Scheduled</SelectItem>
                              <SelectItem value="active">Active</SelectItem>
                              <SelectItem value="paused">Paused</SelectItem>
                              <SelectItem value="completed">Completed</SelectItem>
                            </SelectContent>
                          </Select>
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteCampaign(campaign.id)}>
                            <Trash2 size={14} className="text-red-500" />
                          </Button>
                        </div>
                      </div>
                      <div className="flex items-center space-x-6 mt-3 text-sm">
                        <span className="flex items-center text-gray-500">
                          <Target size={14} className="mr-1" />
                          {campaign.type}
                        </span>
                        {campaign.budget && (
                          <span className="flex items-center text-gray-500">
                            <DollarSign size={14} className="mr-1" />
                            £{campaign.budget.toLocaleString()}
                          </span>
                        )}
                        {campaign.startDate && (
                          <span className="flex items-center text-gray-500">
                            <Calendar size={14} className="mr-1" />
                            {new Date(campaign.startDate).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                      {campaign.metrics && (
                        <div className="flex items-center space-x-4 mt-3 pt-3 border-t">
                          <span className="text-xs text-gray-500">Impressions: {campaign.metrics.impressions}</span>
                          <span className="text-xs text-gray-500">Clicks: {campaign.metrics.clicks}</span>
                          <span className="text-xs text-gray-500">CTR: {campaign.metrics.ctr}%</span>
                          <span className="text-xs text-gray-500">Conversions: {campaign.metrics.conversions}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* SOCIAL MEDIA TAB */}
        <TabsContent value="social" className="mt-6 space-y-6">
          <div className="flex justify-between items-center">
            <div className="flex gap-2">
              <Button onClick={() => setShowSocialPostDialog(true)} className="gradient-primary border-0">
                <Plus className="mr-2" size={18} /> Create Post
              </Button>
              <Button variant="outline" onClick={() => setShowGenerateDialog(true)}>
                <Sparkles className="mr-2" size={18} /> AI Generate
              </Button>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Social Media Posts</CardTitle>
              <CardDescription>Schedule and manage your social content</CardDescription>
            </CardHeader>
            <CardContent>
              {socialPosts.length === 0 ? (
                <div className="text-center py-12">
                  <Share2 className="mx-auto mb-2 text-gray-300" size={48} />
                  <p className="text-gray-500">No posts yet. Create or generate your first post!</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {socialPosts.map((post) => (
                    <div key={post.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <Share2 size={16} className="text-purple-600" />
                          <span className="font-medium capitalize">{post.platform}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(post.status)}`}>
                            {post.status}
                          </span>
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteSocialPost(post.id)}>
                            <Trash2 size={14} className="text-red-500" />
                          </Button>
                        </div>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{post.content}</p>
                      {post.hashtags?.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {post.hashtags.map((tag, i) => (
                            <span key={i} className="text-xs text-purple-600">#{tag}</span>
                          ))}
                        </div>
                      )}
                      {post.scheduledFor && (
                        <p className="text-xs text-gray-500 mt-2">
                          <Calendar size={12} className="inline mr-1" />
                          Scheduled: {new Date(post.scheduledFor).toLocaleString()}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ANALYTICS TAB */}
        <TabsContent value="analytics" className="mt-6 space-y-6">
          {analytics ? (
            <>
              {/* Lead Analytics */}
              <Card>
                <CardHeader>
                  <CardTitle>Lead Analytics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <p className="text-sm text-blue-600">Total Leads</p>
                      <p className="text-2xl font-bold">{analytics.leads?.totalLeads || 0}</p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4">
                      <p className="text-sm text-green-600">Converted</p>
                      <p className="text-2xl font-bold">{analytics.leads?.convertedLeads || 0}</p>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-4">
                      <p className="text-sm text-purple-600">Conversion Rate</p>
                      <p className="text-2xl font-bold">{analytics.leads?.conversionRate || 0}%</p>
                    </div>
                    <div className="bg-yellow-50 rounded-lg p-4">
                      <p className="text-sm text-yellow-600">New Leads</p>
                      <p className="text-2xl font-bold">{analytics.leads?.newLeads || 0}</p>
                    </div>
                  </div>
                  
                  {analytics.leads?.leadsBySource && Object.keys(analytics.leads.leadsBySource).length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Leads by Source</h4>
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                        {Object.entries(analytics.leads.leadsBySource).map(([source, count]) => (
                          <div key={source} className="bg-gray-50 rounded-lg p-3 text-center">
                            <p className="text-xs text-gray-500">{source}</p>
                            <p className="text-lg font-semibold">{count}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Campaign Analytics */}
              <Card>
                <CardHeader>
                  <CardTitle>Campaign Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-purple-50 rounded-lg p-4">
                      <p className="text-sm text-purple-600">Total Campaigns</p>
                      <p className="text-2xl font-bold">{analytics.campaigns?.totalCampaigns || 0}</p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4">
                      <p className="text-sm text-green-600">Active</p>
                      <p className="text-2xl font-bold">{analytics.campaigns?.activeCampaigns || 0}</p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-4">
                      <p className="text-sm text-blue-600">Total Budget</p>
                      <p className="text-2xl font-bold">£{analytics.campaigns?.totalBudget?.toLocaleString() || 0}</p>
                    </div>
                    <div className="bg-yellow-50 rounded-lg p-4">
                      <p className="text-sm text-yellow-600">Avg ROI</p>
                      <p className="text-2xl font-bold">{analytics.campaigns?.avgROI || 0}%</p>
                    </div>
                  </div>

                  {analytics.campaigns?.topPerforming?.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Top Performing Campaigns</h4>
                      <div className="space-y-2">
                        {analytics.campaigns.topPerforming.map((campaign, i) => (
                          <div key={campaign.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="font-medium">{campaign.name}</span>
                            <span className="text-sm text-green-600">{campaign.conversions} conversions</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          ) : (
            <div className="text-center py-12">
              <BarChart3 className="mx-auto mb-2 text-gray-300" size={48} />
              <p className="text-gray-500">Loading analytics...</p>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* CREATE LEAD DIALOG */}
      <Dialog open={showLeadDialog} onOpenChange={setShowLeadDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Add Lead</DialogTitle></DialogHeader>
          <form onSubmit={handleCreateLead} className="space-y-4">
            <div>
              <Label>Name</Label>
              <Input value={newLead.name} onChange={(e) => setNewLead({ ...newLead, name: e.target.value })} required />
            </div>
            <div>
              <Label>Email</Label>
              <Input type="email" value={newLead.email} onChange={(e) => setNewLead({ ...newLead, email: e.target.value })} />
            </div>
            <div>
              <Label>Phone</Label>
              <Input value={newLead.phone} onChange={(e) => setNewLead({ ...newLead, phone: e.target.value })} />
            </div>
            <div>
              <Label>Source</Label>
              <Select value={newLead.source} onValueChange={(v) => setNewLead({ ...newLead, source: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
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
              <Button type="button" variant="outline" onClick={() => setShowLeadDialog(false)}>Cancel</Button>
              <Button type="submit" disabled={creatingLead} className="gradient-primary border-0">
                {creatingLead ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Add Lead
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* CREATE CAMPAIGN DIALOG */}
      <Dialog open={showCampaignDialog} onOpenChange={setShowCampaignDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>Create Campaign</DialogTitle></DialogHeader>
          <form onSubmit={handleCreateCampaign} className="space-y-4">
            <div>
              <Label>Campaign Name</Label>
              <Input value={newCampaign.name} onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })} required />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea value={newCampaign.description} onChange={(e) => setNewCampaign({ ...newCampaign, description: e.target.value })} rows={2} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Type</Label>
                <Select value={newCampaign.type} onValueChange={(v) => setNewCampaign({ ...newCampaign, type: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {campaignTypes.map((t) => (
                      <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Budget (£)</Label>
                <Input type="number" value={newCampaign.budget} onChange={(e) => setNewCampaign({ ...newCampaign, budget: e.target.value })} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Start Date</Label>
                <Input type="date" value={newCampaign.startDate} onChange={(e) => setNewCampaign({ ...newCampaign, startDate: e.target.value })} />
              </div>
              <div>
                <Label>End Date</Label>
                <Input type="date" value={newCampaign.endDate} onChange={(e) => setNewCampaign({ ...newCampaign, endDate: e.target.value })} />
              </div>
            </div>
            <div>
              <Label>Target Audience</Label>
              <Input value={newCampaign.targetAudience} onChange={(e) => setNewCampaign({ ...newCampaign, targetAudience: e.target.value })} placeholder="e.g., Small business owners in UK" />
            </div>
            <div>
              <Label>Goals (comma-separated)</Label>
              <Input value={newCampaign.goals} onChange={(e) => setNewCampaign({ ...newCampaign, goals: e.target.value })} placeholder="increase awareness, generate leads" />
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowCampaignDialog(false)}>Cancel</Button>
              <Button type="submit" disabled={creatingCampaign} className="gradient-primary border-0">
                {creatingCampaign ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Create
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* CREATE SOCIAL POST DIALOG */}
      <Dialog open={showSocialPostDialog} onOpenChange={setShowSocialPostDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Create Social Post</DialogTitle></DialogHeader>
          <form onSubmit={handleCreateSocialPost} className="space-y-4">
            <div>
              <Label>Platform</Label>
              <Select value={newSocialPost.platform} onValueChange={(v) => setNewSocialPost({ ...newSocialPost, platform: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {socialPlatforms.map((p) => (
                    <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Content</Label>
              <Textarea value={newSocialPost.content} onChange={(e) => setNewSocialPost({ ...newSocialPost, content: e.target.value })} rows={4} required />
            </div>
            <div>
              <Label>Hashtags (comma-separated)</Label>
              <Input value={newSocialPost.hashtags} onChange={(e) => setNewSocialPost({ ...newSocialPost, hashtags: e.target.value })} placeholder="business, growth, tips" />
            </div>
            <div>
              <Label>Schedule For</Label>
              <Input type="datetime-local" value={newSocialPost.scheduledFor} onChange={(e) => setNewSocialPost({ ...newSocialPost, scheduledFor: e.target.value })} />
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowSocialPostDialog(false)}>Cancel</Button>
              <Button type="submit" disabled={creatingSocialPost} className="gradient-primary border-0">
                {creatingSocialPost ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Create
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* AI GENERATE POST DIALOG */}
      <Dialog open={showGenerateDialog} onOpenChange={setShowGenerateDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>AI Post Generator</DialogTitle></DialogHeader>
          <form onSubmit={handleGeneratePost} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Platform</Label>
                <Select value={generateRequest.platform} onValueChange={(v) => setGenerateRequest({ ...generateRequest, platform: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {socialPlatforms.map((p) => (
                      <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Tone</Label>
                <Select value={generateRequest.tone} onValueChange={(v) => setGenerateRequest({ ...generateRequest, tone: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {toneOptions.map((t) => (
                      <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Topic</Label>
              <Input value={generateRequest.topic} onChange={(e) => setGenerateRequest({ ...generateRequest, topic: e.target.value })} placeholder="e.g., new product launch, business tips" required />
            </div>
            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={generateRequest.includeEmojis}
                  onChange={(e) => setGenerateRequest({ ...generateRequest, includeEmojis: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm">Include Emojis</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={generateRequest.includeHashtags}
                  onChange={(e) => setGenerateRequest({ ...generateRequest, includeHashtags: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm">Include Hashtags</span>
              </label>
            </div>
            <Button type="submit" disabled={generatingPost} className="w-full gradient-primary border-0">
              {generatingPost ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2" size={16} />}
              Generate Post
            </Button>
          </form>

          {generatedPost && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-2">Generated Post:</h4>
              <p className="text-sm mb-2">{generatedPost.content}</p>
              {generatedPost.hashtags?.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {generatedPost.hashtags.map((tag, i) => (
                    <span key={i} className="text-xs text-purple-600">#{tag}</span>
                  ))}
                </div>
              )}
              <Button onClick={handleUseGeneratedPost} size="sm">
                Use This Post
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
