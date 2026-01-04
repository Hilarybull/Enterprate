import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { 
  Globe, 
  Sparkles,
  Loader2,
  RefreshCw,
  Download,
  Rocket,
  Eye,
  Palette,
  Languages,
  FormInput,
  ExternalLink,
  Trash2,
  ChevronRight,
  Wand2,
  Code,
  Layout,
  CheckCircle2,
  Clock,
  Settings2,
  LayoutTemplate,
  Utensils,
  Briefcase,
  Scissors,
  ShoppingCart,
  LineChart,
  Dumbbell,
  Home,
  HeartPulse
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// Template icons mapping
const TEMPLATE_ICONS = {
  'code': Code,
  'utensils': Utensils,
  'briefcase': Briefcase,
  'scissors': Scissors,
  'sparkles': Sparkles,
  'shopping-cart': ShoppingCart,
  'chart-line': LineChart,
  'dumbbell': Dumbbell,
  'home': Home,
  'heart-pulse': HeartPulse
};

// Color scheme preview colors
const COLOR_PREVIEWS = {
  modern: { primary: '#6366f1', secondary: '#4f46e5', accent: '#10b981' },
  professional: { primary: '#1e40af', secondary: '#1e3a8a', accent: '#059669' },
  creative: { primary: '#ec4899', secondary: '#db2777', accent: '#8b5cf6' },
  minimal: { primary: '#18181b', secondary: '#27272a', accent: '#3f3f46' },
  warm: { primary: '#ea580c', secondary: '#c2410c', accent: '#facc15' },
  nature: { primary: '#16a34a', secondary: '#15803d', accent: '#0d9488' }
};

const LANGUAGE_OPTIONS = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'es', name: 'Spanish', flag: '🇪🇸' },
  { code: 'fr', name: 'French', flag: '🇫🇷' },
  { code: 'de', name: 'German', flag: '🇩🇪' },
  { code: 'it', name: 'Italian', flag: '🇮🇹' },
  { code: 'pt', name: 'Portuguese', flag: '🇵🇹' },
  { code: 'nl', name: 'Dutch', flag: '🇳🇱' },
  { code: 'pl', name: 'Polish', flag: '🇵🇱' },
  { code: 'ru', name: 'Russian', flag: '🇷🇺' },
  { code: 'zh', name: 'Chinese', flag: '🇨🇳' },
  { code: 'ja', name: 'Japanese', flag: '🇯🇵' },
  { code: 'ko', name: 'Korean', flag: '🇰🇷' },
  { code: 'ar', name: 'Arabic', flag: '🇸🇦' },
  { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
  { code: 'tr', name: 'Turkish', flag: '🇹🇷' }
];

const DEPLOYMENT_PLATFORMS = [
  { id: 'netlify', name: 'Netlify', icon: '⚡', description: 'Fast CDN, instant deploys' },
  { id: 'vercel', name: 'Vercel', icon: '▲', description: 'Edge network, zero config' },
  { id: 'railway', name: 'Railway', icon: '🚂', description: 'Infrastructure platform' }
];

export default function AIWebsiteBuilder() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [deploying, setDeploying] = useState(false);
  const [refining, setRefining] = useState(false);
  const [activeTab, setActiveTab] = useState('templates');
  const [websites, setWebsites] = useState([]);
  const [templates, setTemplates] = useState({});
  const [selectedWebsite, setSelectedWebsite] = useState(null);
  const [previewHtml, setPreviewHtml] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    userDescription: '',
    colorScheme: 'modern',
    language: 'en',
    includeLeadForm: true,
    contactMethod: 'form',
    contactValue: '',
    logoUrl: ''
  });
  
  // Refinement state
  const [refinementFeedback, setRefinementFeedback] = useState('');
  
  // Deployment state
  const [deployPlatform, setDeployPlatform] = useState('netlify');
  const [deploySiteName, setDeploySiteName] = useState('');

  const loadWebsites = useCallback(async () => {
    if (!currentWorkspace) return;
    try {
      const response = await axios.get(`${API_URL}/ai-websites`, {
        headers: getHeaders()
      });
      setWebsites(response.data || []);
    } catch (error) {
      console.error('Failed to load websites:', error);
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace, getHeaders]);

  useEffect(() => {
    if (currentWorkspace) {
      loadWebsites();
    } else {
      setLoading(false);
    }
  }, [currentWorkspace, loadWebsites]);

  const generateWebsite = async () => {
    if (!formData.userDescription.trim()) {
      toast.error('Please describe your business');
      return;
    }
    
    setGenerating(true);
    try {
      const response = await axios.post(`${API_URL}/ai-websites/generate`, {
        userDescription: formData.userDescription,
        brandPreferences: { colorScheme: formData.colorScheme },
        logoUrl: formData.logoUrl || null,
        contactMethod: formData.contactMethod,
        contactValue: formData.contactValue || null,
        language: formData.language,
        includeLeadForm: formData.includeLeadForm
      }, { headers: getHeaders() });
      
      if (response.data?.id) {
        toast.success('Website generated successfully!');
        setSelectedWebsite(response.data);
        setPreviewHtml(response.data.htmlContent);
        setShowPreview(true);
        setActiveTab('preview');
        loadWebsites();
      }
    } catch (error) {
      console.error('Generation failed:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate website');
    } finally {
      setGenerating(false);
    }
  };

  const refineWebsite = async () => {
    if (!selectedWebsite || !refinementFeedback.trim()) {
      toast.error('Please provide feedback for refinement');
      return;
    }
    
    setRefining(true);
    try {
      const response = await axios.post(
        `${API_URL}/ai-websites/${selectedWebsite.id}/refine`,
        { feedback: refinementFeedback },
        { headers: getHeaders() }
      );
      
      if (response.data?.htmlContent) {
        toast.success('Website refined successfully!');
        setSelectedWebsite(response.data);
        setPreviewHtml(response.data.htmlContent);
        setRefinementFeedback('');
        loadWebsites();
      }
    } catch (error) {
      console.error('Refinement failed:', error);
      toast.error('Failed to refine website');
    } finally {
      setRefining(false);
    }
  };

  const deployWebsite = async () => {
    if (!selectedWebsite) {
      toast.error('Please select a website to deploy');
      return;
    }
    
    setDeploying(true);
    try {
      const response = await axios.post(
        `${API_URL}/ai-websites/${selectedWebsite.id}/deploy`,
        { 
          platform: deployPlatform,
          siteName: deploySiteName || null 
        },
        { headers: getHeaders() }
      );
      
      if (response.data?.success) {
        toast.success('Website deployed successfully!');
        setSelectedWebsite(prev => ({
          ...prev,
          status: 'deployed',
          deploymentUrl: response.data.siteUrl
        }));
        loadWebsites();
      }
    } catch (error) {
      console.error('Deployment failed:', error);
      toast.error(error.response?.data?.detail || 'Deployment failed');
    } finally {
      setDeploying(false);
    }
  };

  const downloadWebsite = async () => {
    if (!selectedWebsite) return;
    
    try {
      const response = await axios.get(
        `${API_URL}/ai-websites/${selectedWebsite.id}/download`,
        { 
          headers: getHeaders(),
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `website_${selectedWebsite.id}.html`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Website downloaded!');
    } catch (error) {
      toast.error('Download failed');
    }
  };

  const deleteWebsite = async (websiteId) => {
    if (!window.confirm('Are you sure you want to delete this website?')) return;
    
    try {
      await axios.delete(`${API_URL}/ai-websites/${websiteId}`, {
        headers: getHeaders()
      });
      toast.success('Website deleted');
      if (selectedWebsite?.id === websiteId) {
        setSelectedWebsite(null);
        setPreviewHtml('');
        setShowPreview(false);
      }
      loadWebsites();
    } catch (error) {
      toast.error('Failed to delete website');
    }
  };

  const selectWebsite = async (website) => {
    setSelectedWebsite(website);
    setPreviewHtml(website.htmlContent);
    setShowPreview(true);
    setActiveTab('preview');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="loading-spinner">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-slide-in" data-testid="ai-website-builder-page">
      <PageHeader
        icon={Globe}
        title="AI Website Builder"
        description="Generate high-converting landing pages using AI and the AIDA framework"
        actions={
          <div className="flex space-x-2">
            {selectedWebsite && (
              <>
                <Button 
                  variant="outline" 
                  onClick={downloadWebsite}
                  data-testid="download-website-btn"
                >
                  <Download className="mr-2" size={16} />
                  Download
                </Button>
                {selectedWebsite.deploymentUrl && (
                  <Button 
                    variant="outline"
                    onClick={() => window.open(selectedWebsite.deploymentUrl, '_blank')}
                    data-testid="visit-website-btn"
                  >
                    <ExternalLink className="mr-2" size={16} />
                    Visit Site
                  </Button>
                )}
              </>
            )}
          </div>
        }
      />

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="create" className="flex items-center gap-2">
            <Wand2 size={16} />
            Create
          </TabsTrigger>
          <TabsTrigger value="preview" className="flex items-center gap-2" disabled={!previewHtml}>
            <Eye size={16} />
            Preview
          </TabsTrigger>
          <TabsTrigger value="deploy" className="flex items-center gap-2" disabled={!selectedWebsite}>
            <Rocket size={16} />
            Deploy
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <Clock size={16} />
            History
          </TabsTrigger>
        </TabsList>

        {/* CREATE TAB */}
        <TabsContent value="create" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Form */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="text-indigo-500" size={20} />
                  Describe Your Business
                </CardTitle>
                <CardDescription>
                  Tell us about your business and we&apos;ll create a professional landing page using the AIDA framework
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label htmlFor="description">Business Description *</Label>
                  <Textarea
                    id="description"
                    value={formData.userDescription}
                    onChange={(e) => setFormData({...formData, userDescription: e.target.value})}
                    placeholder="Describe your business, products/services, target audience, and what makes you unique..."
                    className="mt-2 min-h-[150px]"
                    data-testid="business-description-input"
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    The more detail you provide, the better your website will be
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="logo">Logo URL (Optional)</Label>
                    <Input
                      id="logo"
                      value={formData.logoUrl}
                      onChange={(e) => setFormData({...formData, logoUrl: e.target.value})}
                      placeholder="https://example.com/logo.png"
                      className="mt-2"
                      data-testid="logo-url-input"
                    />
                  </div>
                  
                  <div>
                    <Label>Contact Method</Label>
                    <Select 
                      value={formData.contactMethod} 
                      onValueChange={(v) => setFormData({...formData, contactMethod: v})}
                    >
                      <SelectTrigger className="mt-2" data-testid="contact-method-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="form">Contact Form</SelectItem>
                        <SelectItem value="email">Email Link</SelectItem>
                        <SelectItem value="phone">Phone Link</SelectItem>
                        <SelectItem value="link">Custom Link</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                {formData.contactMethod !== 'form' && (
                  <div>
                    <Label>Contact Value</Label>
                    <Input
                      value={formData.contactValue}
                      onChange={(e) => setFormData({...formData, contactValue: e.target.value})}
                      placeholder={
                        formData.contactMethod === 'email' ? 'contact@example.com' :
                        formData.contactMethod === 'phone' ? '+1234567890' : 'https://calendly.com/...'
                      }
                      className="mt-2"
                      data-testid="contact-value-input"
                    />
                  </div>
                )}
                
                <Button 
                  className="w-full gradient-primary border-0 h-12 text-lg"
                  onClick={generateWebsite}
                  disabled={generating || !formData.userDescription.trim()}
                  data-testid="generate-website-btn"
                >
                  {generating ? (
                    <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Generating Your Website...</>
                  ) : (
                    <><Sparkles className="mr-2" size={20} /> Generate Website</>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Settings Panel */}
            <div className="space-y-4">
              {/* Color Scheme */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Palette size={18} />
                    Color Scheme
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(COLOR_PREVIEWS).map(([name, colors]) => (
                      <button
                        key={name}
                        onClick={() => setFormData({...formData, colorScheme: name})}
                        className={`p-3 rounded-lg border-2 transition-all ${
                          formData.colorScheme === name 
                            ? 'border-indigo-500 shadow-md' 
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        data-testid={`color-scheme-${name}`}
                      >
                        <div className="flex gap-1 mb-2">
                          <div 
                            className="w-4 h-4 rounded-full" 
                            style={{ backgroundColor: colors.primary }}
                          />
                          <div 
                            className="w-4 h-4 rounded-full" 
                            style={{ backgroundColor: colors.secondary }}
                          />
                          <div 
                            className="w-4 h-4 rounded-full" 
                            style={{ backgroundColor: colors.accent }}
                          />
                        </div>
                        <span className="text-xs capitalize font-medium">{name}</span>
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Language */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Languages size={18} />
                    Language
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Select 
                    value={formData.language} 
                    onValueChange={(v) => setFormData({...formData, language: v})}
                  >
                    <SelectTrigger data-testid="language-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {LANGUAGE_OPTIONS.map(lang => (
                        <SelectItem key={lang.code} value={lang.code}>
                          <span className="flex items-center gap-2">
                            <span>{lang.flag}</span>
                            <span>{lang.name}</span>
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>

              {/* Lead Form Toggle */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <FormInput size={18} />
                    Lead Capture
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Include Lead Form</p>
                      <p className="text-xs text-gray-500">Capture visitor information</p>
                    </div>
                    <Switch
                      checked={formData.includeLeadForm}
                      onCheckedChange={(c) => setFormData({...formData, includeLeadForm: c})}
                      data-testid="lead-form-toggle"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* AIDA Info */}
              <Card className="bg-gradient-to-br from-indigo-50 to-purple-50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">AIDA Framework</CardTitle>
                </CardHeader>
                <CardContent className="text-sm space-y-2">
                  <div className="flex items-start gap-2">
                    <Badge variant="outline" className="shrink-0">A</Badge>
                    <span><strong>Attention:</strong> Compelling hero headline</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Badge variant="outline" className="shrink-0">I</Badge>
                    <span><strong>Interest:</strong> Features & benefits</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Badge variant="outline" className="shrink-0">D</Badge>
                    <span><strong>Desire:</strong> Social proof & trust</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Badge variant="outline" className="shrink-0">A</Badge>
                    <span><strong>Action:</strong> Clear CTAs</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* PREVIEW TAB */}
        <TabsContent value="preview" className="space-y-6 mt-6">
          {previewHtml ? (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Preview iframe */}
              <Card className="lg:col-span-3 overflow-hidden">
                <CardHeader className="border-b bg-gray-50 py-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-400" />
                        <div className="w-3 h-3 rounded-full bg-yellow-400" />
                        <div className="w-3 h-3 rounded-full bg-green-400" />
                      </div>
                      <span className="text-sm text-gray-500 ml-2">Preview</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {selectedWebsite?.version && (
                        <Badge variant="outline">v{selectedWebsite.version}</Badge>
                      )}
                      <Badge className={
                        selectedWebsite?.status === 'deployed' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-yellow-100 text-yellow-700'
                      }>
                        {selectedWebsite?.status || 'draft'}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <iframe
                    srcDoc={previewHtml}
                    className="w-full h-[600px] border-0"
                    title="Website Preview"
                    sandbox="allow-scripts"
                    data-testid="website-preview-iframe"
                  />
                </CardContent>
              </Card>

              {/* Refinement Panel */}
              <Card className="h-fit">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <RefreshCw size={18} />
                    Refine Design
                  </CardTitle>
                  <CardDescription>
                    Tell us what to change
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Textarea
                    value={refinementFeedback}
                    onChange={(e) => setRefinementFeedback(e.target.value)}
                    placeholder="e.g., Make the headline bigger, change the CTA button color to red, add more testimonials..."
                    className="min-h-[120px]"
                    data-testid="refinement-feedback-input"
                  />
                  <Button 
                    className="w-full"
                    onClick={refineWebsite}
                    disabled={refining || !refinementFeedback.trim()}
                    data-testid="refine-website-btn"
                  >
                    {refining ? (
                      <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Refining...</>
                    ) : (
                      <><RefreshCw className="mr-2" size={16} /> Apply Changes</>
                    )}
                  </Button>
                  
                  <div className="border-t pt-4 mt-4">
                    <p className="text-xs text-gray-500 mb-3">Quick refinements:</p>
                    <div className="flex flex-wrap gap-2">
                      {['Bigger headline', 'More contrast', 'Different images', 'Add pricing'].map(suggestion => (
                        <Badge 
                          key={suggestion}
                          variant="outline" 
                          className="cursor-pointer hover:bg-gray-100"
                          onClick={() => setRefinementFeedback(suggestion)}
                        >
                          {suggestion}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card className="p-12 text-center">
              <Layout className="mx-auto text-gray-300 mb-4" size={48} />
              <h3 className="text-lg font-medium text-gray-700">No Preview Available</h3>
              <p className="text-gray-500 mt-1">Generate a website first to see the preview</p>
              <Button className="mt-4" onClick={() => setActiveTab('create')}>
                <ChevronRight className="mr-2" size={16} /> Go to Create
              </Button>
            </Card>
          )}
        </TabsContent>

        {/* DEPLOY TAB */}
        <TabsContent value="deploy" className="space-y-6 mt-6">
          {selectedWebsite ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Rocket className="text-indigo-500" size={20} />
                    Deploy Your Website
                  </CardTitle>
                  <CardDescription>
                    Choose a platform and deploy with one click
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Platform Selection */}
                  <div>
                    <Label className="mb-3 block">Select Platform</Label>
                    <div className="grid grid-cols-1 gap-3">
                      {DEPLOYMENT_PLATFORMS.map(platform => (
                        <button
                          key={platform.id}
                          onClick={() => setDeployPlatform(platform.id)}
                          className={`p-4 rounded-lg border-2 text-left transition-all flex items-center gap-4 ${
                            deployPlatform === platform.id
                              ? 'border-indigo-500 bg-indigo-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          data-testid={`deploy-platform-${platform.id}`}
                        >
                          <span className="text-2xl">{platform.icon}</span>
                          <div>
                            <p className="font-medium">{platform.name}</p>
                            <p className="text-sm text-gray-500">{platform.description}</p>
                          </div>
                          {deployPlatform === platform.id && (
                            <CheckCircle2 className="ml-auto text-indigo-500" size={20} />
                          )}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Site Name */}
                  <div>
                    <Label htmlFor="siteName">Site Name (Optional)</Label>
                    <Input
                      id="siteName"
                      value={deploySiteName}
                      onChange={(e) => setDeploySiteName(e.target.value)}
                      placeholder="my-awesome-site"
                      className="mt-2"
                      data-testid="deploy-site-name-input"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Leave empty for auto-generated name
                    </p>
                  </div>

                  <Button 
                    className="w-full gradient-primary border-0 h-12"
                    onClick={deployWebsite}
                    disabled={deploying}
                    data-testid="deploy-website-btn"
                  >
                    {deploying ? (
                      <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Deploying...</>
                    ) : (
                      <><Rocket className="mr-2" size={20} /> Deploy to {DEPLOYMENT_PLATFORMS.find(p => p.id === deployPlatform)?.name}</>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Deployment Status */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings2 size={20} />
                    Deployment Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Status</span>
                      <Badge className={
                        selectedWebsite.status === 'deployed'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }>
                        {selectedWebsite.status || 'draft'}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Version</span>
                      <span className="font-medium">v{selectedWebsite.version || 1}</span>
                    </div>
                    {selectedWebsite.deploymentUrl && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-500">URL</span>
                        <a 
                          href={selectedWebsite.deploymentUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-600 hover:underline text-sm flex items-center gap-1"
                        >
                          Visit <ExternalLink size={12} />
                        </a>
                      </div>
                    )}
                    {selectedWebsite.deploymentPlatform && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-500">Platform</span>
                        <span className="font-medium capitalize">{selectedWebsite.deploymentPlatform}</span>
                      </div>
                    )}
                  </div>

                  {selectedWebsite.deploymentUrl && (
                    <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                      <div className="flex items-start gap-3">
                        <CheckCircle2 className="text-green-500 shrink-0 mt-0.5" size={20} />
                        <div>
                          <p className="font-medium text-green-800">Website is Live!</p>
                          <p className="text-sm text-green-700 mt-1">
                            Your website is deployed and accessible at the URL above.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="border-t pt-4">
                    <p className="text-sm font-medium mb-2">Other Options</p>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={downloadWebsite}>
                        <Download size={14} className="mr-1" /> Download HTML
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => setActiveTab('preview')}>
                        <Code size={14} className="mr-1" /> View Preview
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card className="p-12 text-center">
              <Rocket className="mx-auto text-gray-300 mb-4" size={48} />
              <h3 className="text-lg font-medium text-gray-700">No Website Selected</h3>
              <p className="text-gray-500 mt-1">Generate or select a website to deploy</p>
              <Button className="mt-4" onClick={() => setActiveTab('create')}>
                <ChevronRight className="mr-2" size={16} /> Create Website
              </Button>
            </Card>
          )}
        </TabsContent>

        {/* HISTORY TAB */}
        <TabsContent value="history" className="space-y-6 mt-6">
          {websites.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {websites.map(website => (
                <Card 
                  key={website.id} 
                  className={`cursor-pointer transition-all hover:shadow-md ${
                    selectedWebsite?.id === website.id ? 'ring-2 ring-indigo-500' : ''
                  }`}
                  onClick={() => selectWebsite(website)}
                  data-testid={`website-card-${website.id}`}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-base truncate max-w-[200px]">
                          {website.businessContext?.companyName || 'Untitled Website'}
                        </CardTitle>
                        <CardDescription className="text-xs">
                          {new Date(website.createdAt).toLocaleDateString()}
                        </CardDescription>
                      </div>
                      <Badge className={
                        website.status === 'deployed'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }>
                        {website.status || 'draft'}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                      {website.businessContext?.description || 'No description'}
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Badge variant="outline" className="text-xs">
                          v{website.version || 1}
                        </Badge>
                        <span className="uppercase">{website.language || 'en'}</span>
                      </div>
                      <div className="flex gap-1">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            selectWebsite(website);
                          }}
                        >
                          <Eye size={14} />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          className="text-red-500 hover:text-red-700 hover:bg-red-50"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteWebsite(website.id);
                          }}
                          data-testid={`delete-website-${website.id}`}
                        >
                          <Trash2 size={14} />
                        </Button>
                      </div>
                    </div>
                    {website.deploymentUrl && (
                      <a 
                        href={website.deploymentUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-indigo-600 hover:underline mt-2 block truncate"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {website.deploymentUrl}
                      </a>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-12 text-center">
              <Clock className="mx-auto text-gray-300 mb-4" size={48} />
              <h3 className="text-lg font-medium text-gray-700">No Websites Yet</h3>
              <p className="text-gray-500 mt-1">Your generated websites will appear here</p>
              <Button className="mt-4" onClick={() => setActiveTab('create')}>
                <ChevronRight className="mr-2" size={16} /> Create Your First Website
              </Button>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
