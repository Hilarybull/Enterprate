import React, { useState, useEffect, lazy, Suspense } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
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
  BookOpen, 
  Target, 
  Users, 
  DollarSign,
  BarChart3,
  Lightbulb,
  FileText,
  Sparkles,
  ArrowRight,
  Plus,
  Loader2,
  Check,
  ChevronDown,
  ChevronUp,
  Download,
  Trash2,
  RefreshCw,
  TrendingUp,
  Building2,
  FileSignature,
  Mail,
  Share2,
  Shield,
  ScrollText,
  Copy,
  Briefcase
} from 'lucide-react';
import { toast } from 'sonner';

// Lazy load Business Documents and Operations components
const BusinessDocumentsContent = lazy(() => import('./BusinessDocuments'));
const BusinessOperationsContent = lazy(() => import('./BusinessOperations'));

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const blueprintSections = [
  { key: 'executive_summary', title: 'Executive Summary', icon: FileText, description: 'High-level overview of your business concept and goals' },
  { key: 'market_analysis', title: 'Market Analysis', icon: BarChart3, description: 'Industry trends, target market, and competitive landscape' },
  { key: 'products_services', title: 'Products & Services', icon: Lightbulb, description: 'Detailed description of your offerings and value proposition' },
  { key: 'marketing_strategy', title: 'Marketing Strategy', icon: Target, description: 'Customer acquisition and brand positioning plans' },
  { key: 'operations_plan', title: 'Operations Plan', icon: Users, description: 'Day-to-day operations, processes, and resource requirements' },
  { key: 'financial_projections', title: 'Financial Projections', icon: DollarSign, description: 'Revenue forecasts, expense budgets, and break-even analysis' },
  { key: 'competitive_analysis', title: 'Competitive Analysis', icon: TrendingUp, description: 'Competitor analysis and differentiation strategy' },
];

// Document types for generation
const DOCUMENT_TYPES = [
  { 
    category: 'Business Documents',
    icon: FileSignature,
    items: [
      { id: 'quote', name: 'Quote/Estimate', description: 'Professional quote for products or services' },
      { id: 'simple_contract', name: 'Simple Contract', description: 'Basic service agreement template' },
      { id: 'proposal', name: 'Business Proposal', description: 'Professional proposal for clients' },
      { id: 'invoice_template', name: 'Invoice Template', description: 'Branded invoice layout' }
    ]
  },
  {
    category: 'Compliance Documents',
    icon: Shield,
    items: [
      { id: 'privacy_policy', name: 'Privacy Policy', description: 'GDPR-compliant privacy policy' },
      { id: 'cookie_notice', name: 'Cookie Notice', description: 'Website cookie consent notice' },
      { id: 'terms_conditions', name: 'Terms & Conditions', description: 'Service terms and conditions' },
      { id: 'refund_policy', name: 'Refund Policy', description: 'Returns and refunds policy' }
    ]
  },
  {
    category: 'HR & Internal Policies',
    icon: Users,
    items: [
      { id: 'employee_handbook', name: 'Employee Handbook', description: 'Basic employee policies' },
      { id: 'remote_work_policy', name: 'Remote Work Policy', description: 'Guidelines for remote work' },
      { id: 'leave_policy', name: 'Leave Policy', description: 'Holiday and sick leave policy' },
      { id: 'code_of_conduct', name: 'Code of Conduct', description: 'Workplace behavior guidelines' }
    ]
  },
  {
    category: 'CRM & Sales Documents',
    icon: ScrollText,
    items: [
      { id: 'welcome_email', name: 'Welcome Email', description: 'New client welcome template' },
      { id: 'follow_up_email', name: 'Follow-up Email', description: 'Sales follow-up template' },
      { id: 'thank_you_note', name: 'Thank You Note', description: 'Client appreciation message' },
      { id: 'meeting_agenda', name: 'Meeting Agenda', description: 'Professional meeting template' }
    ]
  }
];

const industries = [
  'Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing',
  'Education', 'Real Estate', 'Food & Beverage', 'Professional Services',
  'Entertainment', 'Transportation', 'Energy', 'Agriculture', 'Other'
];

const businessModels = [
  'SaaS', 'Marketplace', 'E-commerce', 'Subscription', 'Freemium',
  'Service-based', 'Product-based', 'Franchise', 'Agency', 'Consulting', 'Other'
];

export default function BusinessBlueprint() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [blueprints, setBlueprints] = useState([]);
  const [selectedBlueprint, setSelectedBlueprint] = useState(null);
  const [companyProfile, setCompanyProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showDocumentDialog, setShowDocumentDialog] = useState(false);
  const [creating, setCreating] = useState(false);
  const [generating, setGenerating] = useState({});
  const [expandedSections, setExpandedSections] = useState({});
  const [generatedDocuments, setGeneratedDocuments] = useState({});
  const [activeTab, setActiveTab] = useState('sections');
  
  const [newBlueprint, setNewBlueprint] = useState({
    businessName: '',
    industry: '',
    description: '',
    targetMarket: '',
    businessModel: '',
    fundingGoal: ''
  });

  const [selectedDocument, setSelectedDocument] = useState(null);

  useEffect(() => {
    if (currentWorkspace) {
      loadCompanyProfile();
      loadBlueprints();
    } else {
      setLoading(false);
    }
  }, [currentWorkspace]);

  const loadCompanyProfile = async () => {
    try {
      const response = await axios.get(`${API_URL}/company-profile`, {
        headers: getHeaders()
      });
      if (response.data) {
        setCompanyProfile(response.data);
        // Pre-fill new blueprint with company details
        setNewBlueprint(prev => ({
          ...prev,
          businessName: response.data.legalName || response.data.proposedName || '',
          industry: response.data.officialProfile?.companyType || '',
          description: response.data.businessDescription || ''
        }));
      }
    } catch (error) {
      console.error('Failed to load company profile:', error);
    }
  };

  const loadBlueprints = async () => {
    try {
      const response = await axios.get(`${API_URL}/blueprint`, {
        headers: getHeaders()
      });
      setBlueprints(response.data || []);
      if (response.data?.length > 0 && !selectedBlueprint) {
        setSelectedBlueprint(response.data[0]);
      }
    } catch (error) {
      console.error('Failed to load blueprints:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBlueprint = async (e) => {
    e.preventDefault();
    if (!currentWorkspace) {
      toast.error('Please select a workspace first');
      return;
    }
    setCreating(true);

    try {
      const response = await axios.post(
        `${API_URL}/blueprint`,
        {
          ...newBlueprint,
          fundingGoal: newBlueprint.fundingGoal ? parseFloat(newBlueprint.fundingGoal) : null
        },
        { headers: getHeaders() }
      );
      toast.success('Blueprint created successfully!');
      setShowCreateDialog(false);
      setNewBlueprint({ businessName: '', industry: '', description: '', targetMarket: '', businessModel: '', fundingGoal: '' });
      await loadBlueprints();
      setSelectedBlueprint(response.data);
    } catch (error) {
      toast.error('Failed to create blueprint');
      console.error(error);
    } finally {
      setCreating(false);
    }
  };

  const handleGenerateSection = async (sectionType) => {
    if (!selectedBlueprint) return;
    
    setGenerating(prev => ({ ...prev, [sectionType]: true }));
    
    try {
      await axios.post(
        `${API_URL}/blueprint/${selectedBlueprint.id}/generate-section/${sectionType}`,
        {},
        { headers: getHeaders() }
      );
      toast.success(`${sectionType.replace('_', ' ')} generated!`);
      
      const response = await axios.get(`${API_URL}/blueprint/${selectedBlueprint.id}`, {
        headers: getHeaders()
      });
      setSelectedBlueprint(response.data);
      setExpandedSections(prev => ({ ...prev, [sectionType]: true }));
    } catch (error) {
      toast.error('Failed to generate section');
      console.error(error);
    } finally {
      setGenerating(prev => ({ ...prev, [sectionType]: false }));
    }
  };

  const handleGenerateSWOT = async () => {
    if (!selectedBlueprint) return;
    
    setGenerating(prev => ({ ...prev, swot: true }));
    
    try {
      await axios.post(
        `${API_URL}/blueprint/${selectedBlueprint.id}/generate-swot`,
        {},
        { headers: getHeaders() }
      );
      toast.success('SWOT Analysis generated!');
      
      const response = await axios.get(`${API_URL}/blueprint/${selectedBlueprint.id}`, {
        headers: getHeaders()
      });
      setSelectedBlueprint(response.data);
    } catch (error) {
      toast.error('Failed to generate SWOT');
      console.error(error);
    } finally {
      setGenerating(prev => ({ ...prev, swot: false }));
    }
  };

  const handleGenerateFinancials = async () => {
    if (!selectedBlueprint) return;
    
    setGenerating(prev => ({ ...prev, financials: true }));
    
    try {
      await axios.post(
        `${API_URL}/blueprint/${selectedBlueprint.id}/generate-financials`,
        {},
        { headers: getHeaders() }
      );
      toast.success('Financial projections generated!');
      
      const response = await axios.get(`${API_URL}/blueprint/${selectedBlueprint.id}`, {
        headers: getHeaders()
      });
      setSelectedBlueprint(response.data);
    } catch (error) {
      toast.error('Failed to generate financials');
      console.error(error);
    } finally {
      setGenerating(prev => ({ ...prev, financials: false }));
    }
  };

  const handleGenerateFullBlueprint = async () => {
    if (!selectedBlueprint) return;
    
    setGenerating(prev => ({ ...prev, full: true }));
    
    try {
      const response = await axios.post(
        `${API_URL}/blueprint/${selectedBlueprint.id}/generate-full`,
        {},
        { headers: getHeaders() }
      );
      toast.success('Complete blueprint generated!');
      setSelectedBlueprint(response.data);
    } catch (error) {
      toast.error('Failed to generate full blueprint');
      console.error(error);
    } finally {
      setGenerating(prev => ({ ...prev, full: false }));
    }
  };

  const handleDeleteBlueprint = async (blueprintId) => {
    if (!window.confirm('Are you sure you want to delete this blueprint?')) return;
    
    try {
      await axios.delete(`${API_URL}/blueprint/${blueprintId}`, {
        headers: getHeaders()
      });
      toast.success('Blueprint deleted');
      if (selectedBlueprint?.id === blueprintId) {
        setSelectedBlueprint(null);
      }
      await loadBlueprints();
    } catch (error) {
      toast.error('Failed to delete blueprint');
    }
  };

  const handleGenerateDocument = async (docId) => {
    setGenerating(prev => ({ ...prev, [docId]: true }));
    
    try {
      const response = await axios.post(
        `${API_URL}/blueprint/generate-document`,
        {
          documentType: docId,
          companyName: companyProfile?.legalName || selectedBlueprint?.businessName || 'Company',
          industry: selectedBlueprint?.industry || companyProfile?.officialProfile?.companyType || '',
          description: selectedBlueprint?.description || companyProfile?.businessDescription || ''
        },
        { headers: getHeaders() }
      );
      
      if (response.data?.content) {
        setGeneratedDocuments(prev => ({ ...prev, [docId]: response.data.content }));
        toast.success('Document generated!');
      }
    } catch (error) {
      // Generate fallback document
      const fallbackDoc = generateFallbackDocument(docId);
      setGeneratedDocuments(prev => ({ ...prev, [docId]: fallbackDoc }));
      toast.info('Document template generated');
    } finally {
      setGenerating(prev => ({ ...prev, [docId]: false }));
    }
  };

  const generateFallbackDocument = (docId) => {
    const companyName = companyProfile?.legalName || selectedBlueprint?.businessName || '[Company Name]';
    
    const templates = {
      privacy_policy: `PRIVACY POLICY\n\nLast Updated: ${new Date().toLocaleDateString()}\n\n${companyName} ("we", "us", or "our") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information.\n\n1. INFORMATION WE COLLECT\nWe collect information you provide directly to us, such as when you create an account, make a purchase, or contact us for support.\n\n2. HOW WE USE YOUR INFORMATION\nWe use the information we collect to provide, maintain, and improve our services.\n\n3. INFORMATION SHARING\nWe do not sell, trade, or rent your personal information to third parties.\n\n4. DATA SECURITY\nWe implement appropriate security measures to protect your personal information.\n\n5. YOUR RIGHTS\nYou have the right to access, correct, or delete your personal data.\n\n6. CONTACT US\nIf you have questions about this Privacy Policy, please contact us.`,
      
      cookie_notice: `COOKIE NOTICE\n\n${companyName} uses cookies and similar technologies to improve your experience on our website.\n\nWHAT ARE COOKIES?\nCookies are small text files stored on your device when you visit our website.\n\nTYPES OF COOKIES WE USE:\n• Essential Cookies: Required for basic website functionality\n• Analytics Cookies: Help us understand how visitors use our site\n• Marketing Cookies: Used to deliver relevant advertisements\n\nMANAGING COOKIES\nYou can control cookies through your browser settings. Note that disabling certain cookies may affect website functionality.\n\nBy continuing to use our website, you consent to our use of cookies.`,
      
      terms_conditions: `TERMS AND CONDITIONS\n\nEffective Date: ${new Date().toLocaleDateString()}\n\nWelcome to ${companyName}. By using our services, you agree to these terms.\n\n1. ACCEPTANCE OF TERMS\nBy accessing our services, you agree to be bound by these Terms and Conditions.\n\n2. USE OF SERVICES\nYou agree to use our services only for lawful purposes.\n\n3. INTELLECTUAL PROPERTY\nAll content and materials are the property of ${companyName}.\n\n4. LIMITATION OF LIABILITY\nWe shall not be liable for any indirect, incidental, or consequential damages.\n\n5. TERMINATION\nWe reserve the right to terminate services at our discretion.\n\n6. GOVERNING LAW\nThese terms are governed by the laws of England and Wales.`,
      
      proposal: `BUSINESS PROPOSAL\n\n${companyName}\n\nPrepared for: [Client Name]\nDate: ${new Date().toLocaleDateString()}\n\nEXECUTIVE SUMMARY\n[Brief overview of the proposal]\n\nPROJECT SCOPE\n[Detailed description of deliverables]\n\nTIMELINE\n[Project milestones and deadlines]\n\nINVESTMENT\n[Pricing and payment terms]\n\nWHY CHOOSE US\n[Your unique value proposition]\n\nNEXT STEPS\n[Call to action]`,
      
      quote: `QUOTATION\n\n${companyName}\nDate: ${new Date().toLocaleDateString()}\nQuote #: [Number]\nValid Until: [Date]\n\nTO:\n[Client Name]\n[Client Address]\n\nDESCRIPTION OF SERVICES:\n\n| Item | Description | Quantity | Unit Price | Total |\n|------|-------------|----------|------------|-------|\n| 1    | [Service]   | 1        | £0.00      | £0.00 |\n\nSubtotal: £0.00\nVAT (20%): £0.00\nTOTAL: £0.00\n\nTerms: Payment due within 30 days\n\nAccepted by: _______________ Date: ___________`,
      
      welcome_email: `Subject: Welcome to ${companyName}!\n\nDear [Client Name],\n\nWelcome to ${companyName}! We're thrilled to have you as a customer.\n\nHere's what you can expect from us:\n• [Key benefit 1]\n• [Key benefit 2]\n• [Key benefit 3]\n\nIf you have any questions, don't hesitate to reach out. We're here to help!\n\nBest regards,\nThe ${companyName} Team`,
      
      simple_contract: `SERVICE AGREEMENT\n\nThis Agreement is entered into as of [Date] between:\n\n${companyName} ("Provider")\nand\n[Client Name] ("Client")\n\n1. SERVICES\nProvider agrees to provide the following services: [Description]\n\n2. COMPENSATION\nClient agrees to pay £[Amount] for the services described above.\n\n3. TERM\nThis agreement begins on [Date] and continues until [Date].\n\n4. TERMINATION\nEither party may terminate with 30 days written notice.\n\nSignatures:\n\nProvider: _______________ Date: ___________\nClient: _______________ Date: ___________`
    };
    
    return templates[docId] || `[${docId.replace(/_/g, ' ').toUpperCase()}]\n\nDocument template for ${companyName}.\n\n[Content to be customized]`;
  };

  const copyDocument = (content, name) => {
    navigator.clipboard.writeText(content);
    toast.success(`${name} copied to clipboard!`);
  };

  const getSectionContent = (sectionType) => {
    if (!selectedBlueprint?.sections) return null;
    return selectedBlueprint.sections.find(s => s.sectionType === sectionType);
  };

  const toggleSection = (sectionType) => {
    setExpandedSections(prev => ({ ...prev, [sectionType]: !prev[sectionType] }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-slide-in" data-testid="business-blueprint-page">
      <PageHeader
        icon={BookOpen}
        title="Business Blueprint Generator"
        description="Create comprehensive business plans, documents, and strategic roadmaps with AI assistance"
        actions={
          <div className="flex space-x-2">
            <Button variant="outline" onClick={() => setShowDocumentDialog(true)}>
              <FileSignature className="mr-2" size={16} />
              Generate Documents
            </Button>
            <Button onClick={() => setShowCreateDialog(true)} className="gradient-primary border-0">
              <Plus className="mr-2" size={18} />
              New Blueprint
            </Button>
          </div>
        }
      />

      {/* Company Profile Banner */}
      {companyProfile?.isRegistrationConfirmed && (
        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Building2 className="w-5 h-5 text-green-600 mr-3" />
                <div>
                  <p className="font-medium text-green-800">
                    Using confirmed company: {companyProfile.legalName}
                  </p>
                  <p className="text-sm text-green-700">
                    Your blueprints and documents will be pre-filled with verified company details
                  </p>
                </div>
              </div>
              <Badge className="bg-green-100 text-green-700">Verified</Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {blueprints.length === 0 ? (
        <Card className="bg-gradient-to-r from-purple-600 to-blue-600 text-white border-0">
          <CardContent className="p-8">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold mb-2">AI-Powered Business Planning</h3>
                <p className="text-purple-100 max-w-xl mb-4">
                  Our AI analyzes your business idea and generates comprehensive plans, 
                  financial models, and strategic roadmaps tailored to your industry and goals.
                </p>
                <Button onClick={() => setShowCreateDialog(true)} className="bg-white text-purple-700 hover:bg-purple-50">
                  Create Your First Blueprint
                  <ArrowRight className="ml-2" size={18} />
                </Button>
              </div>
              <div className="hidden lg:block">
                <div className="w-32 h-32 rounded-2xl bg-white/10 flex items-center justify-center">
                  <BookOpen className="text-white" size={64} />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Blueprint List */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">My Blueprints</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {blueprints.map((bp) => (
                  <div
                    key={bp.id}
                    onClick={() => setSelectedBlueprint(bp)}
                    className={`p-3 rounded-lg cursor-pointer transition-all ${
                      selectedBlueprint?.id === bp.id
                        ? 'bg-purple-100 border-purple-300 border'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="min-w-0 flex-1">
                        <h4 className="font-medium text-sm truncate">{bp.businessName}</h4>
                        <p className="text-xs text-gray-500">{bp.industry}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 text-gray-400 hover:text-red-500"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteBlueprint(bp.id);
                        }}
                      >
                        <Trash2 size={14} />
                      </Button>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      bp.status === 'complete' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {bp.status}
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Blueprint Details */}
          <div className="lg:col-span-3 space-y-6">
            {selectedBlueprint && (
              <>
                <Card>
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start">
                      <div>
                        <h2 className="text-2xl font-bold">{selectedBlueprint.businessName}</h2>
                        <p className="text-gray-500">{selectedBlueprint.industry} • {selectedBlueprint.businessModel || 'Business Model TBD'}</p>
                        <p className="text-sm text-gray-600 mt-2 max-w-2xl">{selectedBlueprint.description}</p>
                      </div>
                      <Button
                        onClick={handleGenerateFullBlueprint}
                        disabled={generating.full}
                        className="gradient-primary border-0"
                      >
                        {generating.full ? (
                          <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating...</>
                        ) : (
                          <><Sparkles className="mr-2" size={18} /> Generate Full Blueprint</>
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList>
                    <TabsTrigger value="sections">Sections</TabsTrigger>
                    <TabsTrigger value="swot">SWOT Analysis</TabsTrigger>
                    <TabsTrigger value="financials">Financial Projections</TabsTrigger>
                    <TabsTrigger value="documents">Documents</TabsTrigger>
                  </TabsList>

                  <TabsContent value="sections" className="space-y-4 mt-4">
                    {blueprintSections.map((section) => {
                      const Icon = section.icon;
                      const content = getSectionContent(section.key);
                      const isExpanded = expandedSections[section.key];
                      const isGenerating = generating[section.key];

                      return (
                        <Card key={section.key}>
                          <CardHeader className="pb-2">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center">
                                  <Icon size={20} />
                                </div>
                                <div>
                                  <CardTitle className="text-base">{section.title}</CardTitle>
                                  <CardDescription className="text-xs">{section.description}</CardDescription>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                {content ? (
                                  <>
                                    <span className="text-xs text-green-600 flex items-center">
                                      <Check size={14} className="mr-1" /> Generated
                                    </span>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => handleGenerateSection(section.key)}
                                      disabled={isGenerating}
                                    >
                                      <RefreshCw size={14} className={isGenerating ? 'animate-spin' : ''} />
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => toggleSection(section.key)}
                                    >
                                      {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                    </Button>
                                  </>
                                ) : (
                                  <Button
                                    size="sm"
                                    onClick={() => handleGenerateSection(section.key)}
                                    disabled={isGenerating}
                                    className="gradient-primary border-0"
                                  >
                                    {isGenerating ? (
                                      <><Loader2 className="mr-2 h-3 w-3 animate-spin" /> Generating</>
                                    ) : (
                                      <><Sparkles className="mr-1" size={14} /> Generate</>
                                    )}
                                  </Button>
                                )}
                              </div>
                            </div>
                          </CardHeader>
                          {content && isExpanded && (
                            <CardContent className="pt-2">
                              <div className="bg-gray-50 rounded-lg p-4 prose prose-sm max-w-none">
                                <div className="whitespace-pre-wrap text-sm text-gray-700">
                                  {content.content}
                                </div>
                              </div>
                            </CardContent>
                          )}
                        </Card>
                      );
                    })}
                  </TabsContent>

                  <TabsContent value="swot" className="mt-4">
                    <Card>
                      <CardHeader>
                        <div className="flex justify-between items-center">
                          <CardTitle>SWOT Analysis</CardTitle>
                          <Button
                            onClick={handleGenerateSWOT}
                            disabled={generating.swot}
                            variant={selectedBlueprint.swotAnalysis ? 'outline' : 'default'}
                            className={!selectedBlueprint.swotAnalysis ? 'gradient-primary border-0' : ''}
                          >
                            {generating.swot ? (
                              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating</>
                            ) : selectedBlueprint.swotAnalysis ? (
                              <><RefreshCw className="mr-2" size={16} /> Regenerate</>
                            ) : (
                              <><Sparkles className="mr-2" size={16} /> Generate SWOT</>
                            )}
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent>
                        {selectedBlueprint.swotAnalysis ? (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-green-50 rounded-lg p-4">
                              <h4 className="font-semibold text-green-700 mb-2">Strengths</h4>
                              <ul className="space-y-1">
                                {selectedBlueprint.swotAnalysis.strengths?.map((item, i) => (
                                  <li key={i} className="text-sm text-green-800 flex items-start">
                                    <Check size={14} className="mr-2 mt-0.5 flex-shrink-0" />
                                    {item}
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div className="bg-red-50 rounded-lg p-4">
                              <h4 className="font-semibold text-red-700 mb-2">Weaknesses</h4>
                              <ul className="space-y-1">
                                {selectedBlueprint.swotAnalysis.weaknesses?.map((item, i) => (
                                  <li key={i} className="text-sm text-red-800">• {item}</li>
                                ))}
                              </ul>
                            </div>
                            <div className="bg-blue-50 rounded-lg p-4">
                              <h4 className="font-semibold text-blue-700 mb-2">Opportunities</h4>
                              <ul className="space-y-1">
                                {selectedBlueprint.swotAnalysis.opportunities?.map((item, i) => (
                                  <li key={i} className="text-sm text-blue-800">• {item}</li>
                                ))}
                              </ul>
                            </div>
                            <div className="bg-yellow-50 rounded-lg p-4">
                              <h4 className="font-semibold text-yellow-700 mb-2">Threats</h4>
                              <ul className="space-y-1">
                                {selectedBlueprint.swotAnalysis.threats?.map((item, i) => (
                                  <li key={i} className="text-sm text-yellow-800">• {item}</li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-8 text-gray-500">
                            <Target className="mx-auto mb-2 text-gray-300" size={48} />
                            <p>Generate a SWOT analysis for your business</p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="financials" className="mt-4">
                    <Card>
                      <CardHeader>
                        <div className="flex justify-between items-center">
                          <CardTitle>Financial Projections (3-Year)</CardTitle>
                          <Button
                            onClick={handleGenerateFinancials}
                            disabled={generating.financials}
                            variant={selectedBlueprint.financialProjections?.length ? 'outline' : 'default'}
                            className={!selectedBlueprint.financialProjections?.length ? 'gradient-primary border-0' : ''}
                          >
                            {generating.financials ? (
                              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating</>
                            ) : selectedBlueprint.financialProjections?.length ? (
                              <><RefreshCw className="mr-2" size={16} /> Regenerate</>
                            ) : (
                              <><Sparkles className="mr-2" size={16} /> Generate Projections</>
                            )}
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent>
                        {selectedBlueprint.financialProjections?.length > 0 ? (
                          <div className="overflow-x-auto">
                            <table className="w-full">
                              <thead>
                                <tr className="border-b">
                                  <th className="text-left py-2 px-4">Year</th>
                                  <th className="text-right py-2 px-4">Revenue</th>
                                  <th className="text-right py-2 px-4">Expenses</th>
                                  <th className="text-right py-2 px-4">Net Income</th>
                                  <th className="text-right py-2 px-4">Growth</th>
                                </tr>
                              </thead>
                              <tbody>
                                {selectedBlueprint.financialProjections.map((proj) => (
                                  <tr key={proj.year} className="border-b">
                                    <td className="py-3 px-4 font-medium">Year {proj.year}</td>
                                    <td className="py-3 px-4 text-right text-green-600">
                                      £{proj.revenue?.toLocaleString()}
                                    </td>
                                    <td className="py-3 px-4 text-right text-red-600">
                                      £{proj.expenses?.toLocaleString()}
                                    </td>
                                    <td className={`py-3 px-4 text-right font-semibold ${
                                      proj.netIncome >= 0 ? 'text-green-600' : 'text-red-600'
                                    }`}>
                                      £{proj.netIncome?.toLocaleString()}
                                    </td>
                                    <td className="py-3 px-4 text-right">
                                      <span className="text-purple-600">+{proj.growthRate}%</span>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <div className="text-center py-8 text-gray-500">
                            <DollarSign className="mx-auto mb-2 text-gray-300" size={48} />
                            <p>Generate financial projections for your business</p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="documents" className="mt-4 space-y-4">
                    {DOCUMENT_TYPES.map((category) => {
                      const Icon = category.icon;
                      return (
                        <Card key={category.category}>
                          <CardHeader>
                            <CardTitle className="text-lg flex items-center">
                              <Icon className="mr-2 text-purple-600" size={20} />
                              {category.category}
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              {category.items.map((doc) => {
                                const content = generatedDocuments[doc.id];
                                const isGenerating = generating[doc.id];
                                
                                return (
                                  <div key={doc.id} className="border rounded-lg p-3">
                                    <div className="flex justify-between items-start mb-2">
                                      <div>
                                        <h4 className="font-medium text-sm">{doc.name}</h4>
                                        <p className="text-xs text-gray-500">{doc.description}</p>
                                      </div>
                                    </div>
                                    <div className="flex space-x-2">
                                      <Button
                                        size="sm"
                                        onClick={() => handleGenerateDocument(doc.id)}
                                        disabled={isGenerating}
                                        variant={content ? 'outline' : 'default'}
                                        className={!content ? 'gradient-primary border-0' : ''}
                                      >
                                        {isGenerating ? (
                                          <Loader2 className="h-3 w-3 animate-spin" />
                                        ) : content ? (
                                          <><RefreshCw size={12} className="mr-1" /> Regenerate</>
                                        ) : (
                                          <><Sparkles size={12} className="mr-1" /> Generate</>
                                        )}
                                      </Button>
                                      {content && (
                                        <Button
                                          size="sm"
                                          variant="ghost"
                                          onClick={() => copyDocument(content, doc.name)}
                                        >
                                          <Copy size={12} className="mr-1" /> Copy
                                        </Button>
                                      )}
                                    </div>
                                    {content && (
                                      <div className="mt-2 p-2 bg-gray-50 rounded text-xs max-h-32 overflow-y-auto">
                                        <pre className="whitespace-pre-wrap font-sans">{content.substring(0, 200)}...</pre>
                                      </div>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </TabsContent>
                </Tabs>
              </>
            )}
          </div>
        </div>
      )}

      {/* Create Blueprint Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Create New Blueprint</DialogTitle>
          </DialogHeader>
          
          {companyProfile?.isRegistrationConfirmed && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-green-800">
                <Check size={14} className="inline mr-1" />
                Pre-filled with your confirmed company details
              </p>
            </div>
          )}
          
          <form onSubmit={handleCreateBlueprint} className="space-y-4">
            <div>
              <Label htmlFor="businessName">Business Name *</Label>
              <Input
                id="businessName"
                value={newBlueprint.businessName}
                onChange={(e) => setNewBlueprint({ ...newBlueprint, businessName: e.target.value })}
                placeholder="My Awesome Startup"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="industry">Industry *</Label>
                <Select
                  value={newBlueprint.industry}
                  onValueChange={(value) => setNewBlueprint({ ...newBlueprint, industry: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select industry" />
                  </SelectTrigger>
                  <SelectContent>
                    {industries.map((ind) => (
                      <SelectItem key={ind} value={ind}>{ind}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="businessModel">Business Model</Label>
                <Select
                  value={newBlueprint.businessModel}
                  onValueChange={(value) => setNewBlueprint({ ...newBlueprint, businessModel: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent>
                    {businessModels.map((model) => (
                      <SelectItem key={model} value={model}>{model}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="description">Business Description *</Label>
              <Textarea
                id="description"
                value={newBlueprint.description}
                onChange={(e) => setNewBlueprint({ ...newBlueprint, description: e.target.value })}
                placeholder="Describe your business idea..."
                rows={3}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="targetMarket">Target Market</Label>
                <Input
                  id="targetMarket"
                  value={newBlueprint.targetMarket}
                  onChange={(e) => setNewBlueprint({ ...newBlueprint, targetMarket: e.target.value })}
                  placeholder="e.g., B2B SaaS, SMBs in UK"
                />
              </div>
              <div>
                <Label htmlFor="fundingGoal">Funding Goal (£)</Label>
                <Input
                  id="fundingGoal"
                  type="number"
                  value={newBlueprint.fundingGoal}
                  onChange={(e) => setNewBlueprint({ ...newBlueprint, fundingGoal: e.target.value })}
                  placeholder="100000"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={creating || !newBlueprint.businessName || !newBlueprint.industry || !newBlueprint.description} className="gradient-primary border-0">
                {creating ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating...</>
                ) : (
                  'Create Blueprint'
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Document Generation Dialog */}
      <Dialog open={showDocumentDialog} onOpenChange={setShowDocumentDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Generate Business Documents</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6">
            {DOCUMENT_TYPES.map((category) => {
              const Icon = category.icon;
              return (
                <div key={category.category}>
                  <h3 className="font-semibold flex items-center mb-3">
                    <Icon className="mr-2 text-purple-600" size={18} />
                    {category.category}
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    {category.items.map((doc) => {
                      const content = generatedDocuments[doc.id];
                      const isGenerating = generating[doc.id];
                      
                      return (
                        <Card key={doc.id} className="cursor-pointer hover:border-purple-300">
                          <CardContent className="p-3">
                            <h4 className="font-medium text-sm">{doc.name}</h4>
                            <p className="text-xs text-gray-500 mb-2">{doc.description}</p>
                            <div className="flex space-x-2">
                              <Button
                                size="sm"
                                onClick={() => handleGenerateDocument(doc.id)}
                                disabled={isGenerating}
                                className={!content ? 'gradient-primary border-0' : ''}
                                variant={content ? 'outline' : 'default'}
                              >
                                {isGenerating ? (
                                  <Loader2 className="h-3 w-3 animate-spin" />
                                ) : (
                                  <><Sparkles size={12} className="mr-1" /> {content ? 'Regenerate' : 'Generate'}</>
                                )}
                              </Button>
                              {content && (
                                <Button size="sm" variant="ghost" onClick={() => copyDocument(content, doc.name)}>
                                  <Copy size={12} />
                                </Button>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
