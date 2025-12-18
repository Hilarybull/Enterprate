import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Lightbulb, 
  ArrowLeft, 
  ArrowRight, 
  CheckCircle,
  AlertTriangle,
  XCircle,
  Loader2,
  BarChart3,
  Target,
  TrendingUp,
  Users,
  FileText,
  RefreshCw,
  History
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const INDUSTRIES = [
  'Technology', 'Education', 'Health', 'Finance', 'Retail', 
  'Logistics', 'Food', 'Real Estate', 'Manufacturing', 
  'Construction', 'Media', 'Professional Services', 'Nonprofit', 'Other'
];

const BUSINESS_DELIVERY_MODELS = [
  { value: 'service', label: 'Service' },
  { value: 'marketplace', label: 'Marketplace' },
  { value: 'subscription', label: 'Subscription' },
  { value: 'agency', label: 'Agency' },
  { value: 'other', label: 'Other' }
];

const PRODUCT_DELIVERY_MODELS = [
  { value: 'physical', label: 'Physical Product' },
  { value: 'digital', label: 'Digital Product' },
  { value: 'saas', label: 'SaaS' },
  { value: 'mobile app', label: 'Mobile App' },
  { value: 'other', label: 'Other' }
];

const GTM_CHANNELS = [
  'SEO', 'Ads', 'Social', 'Partnerships', 'Direct Sales', 'Marketplaces', 'Other'
];

const TOTAL_STEPS = 6;

export default function IdeaDiscovery() {
  const navigate = useNavigate();
  const { modifyId } = useParams(); // For modify mode
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [isModifyMode, setIsModifyMode] = useState(false);
  
  // Form data
  const [formData, setFormData] = useState({
    ideaType: '',
    ideaName: '',
    ideaDescription: '',
    industry: '',
    subIndustry: '',
    problemSolved: '',
    targetAudience: '',
    urgencyLevel: '',
    howItWorks: '',
    deliveryModel: '',
    targetMarket: '',
    targetLocation: '',
    customerBudget: '',
    goToMarketChannel: []
  });

  // Load existing report data for modify mode
  useEffect(() => {
    if (modifyId && currentWorkspace) {
      loadReportForModification();
    } else {
      // Auto-save to localStorage for new validations
      const saved = localStorage.getItem('enterprate_idea_validation');
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          setFormData(parsed.formData || formData);
          setCurrentStep(parsed.currentStep || 1);
        } catch (e) {
          console.error('Failed to load saved data');
        }
      }
    }
  }, [modifyId, currentWorkspace]);

  const loadReportForModification = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/validation-reports/${modifyId}`,
        { headers: getHeaders() }
      );
      if (response.data && response.data.ideaInput) {
        setFormData(response.data.ideaInput);
        setIsModifyMode(true);
        setCurrentStep(1);
      }
    } catch (error) {
      toast.error('Failed to load report for modification');
      navigate('/idea-discovery');
    }
  };

  useEffect(() => {
    localStorage.setItem('enterprate_idea_validation', JSON.stringify({
      formData,
      currentStep
    }));
  }, [formData, currentStep]);

  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const toggleGTMChannel = (channel) => {
    setFormData(prev => ({
      ...prev,
      goToMarketChannel: prev.goToMarketChannel.includes(channel)
        ? prev.goToMarketChannel.filter(c => c !== channel)
        : [...prev.goToMarketChannel, channel]
    }));
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return formData.ideaType !== '';
      case 2:
        return formData.ideaName.trim() !== '' && formData.ideaDescription.trim() !== '';
      case 3:
        return formData.industry !== '';
      case 4:
        return formData.problemSolved.trim() !== '' && 
               formData.targetAudience.trim() !== '' && 
               formData.urgencyLevel !== '';
      case 5:
        return formData.howItWorks.trim() !== '' && formData.deliveryModel !== '';
      case 6:
        return formData.targetMarket !== '' && 
               formData.targetLocation.trim() !== '' && 
               formData.customerBudget !== '' && 
               formData.goToMarketChannel.length > 0;
      default:
        return true;
    }
  };

  const handleNext = () => {
    if (currentStep < TOTAL_STEPS) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    if (!currentWorkspace) {
      toast.error('Please select a workspace first');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_URL}/genesis/validate`,
        formData,
        { headers: getHeaders() }
      );
      setValidationResult(response.data);
      setShowResults(true);
      toast.success('Validation complete!');
      // Clear saved data
      localStorage.removeItem('enterprate_idea_validation');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to validate idea');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      ideaType: '',
      ideaName: '',
      ideaDescription: '',
      industry: '',
      subIndustry: '',
      problemSolved: '',
      targetAudience: '',
      urgencyLevel: '',
      howItWorks: '',
      deliveryModel: '',
      targetMarket: '',
      targetLocation: '',
      customerBudget: '',
      goToMarketChannel: []
    });
    setCurrentStep(1);
    setShowResults(false);
    setValidationResult(null);
    localStorage.removeItem('enterprate_idea_validation');
  };

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'PASS': return 'bg-green-100 text-green-800 border-green-200';
      case 'PIVOT': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'KILL': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getVerdictIcon = (verdict) => {
    switch (verdict) {
      case 'PASS': return <CheckCircle className="text-green-600" size={24} />;
      case 'PIVOT': return <AlertTriangle className="text-yellow-600" size={24} />;
      case 'KILL': return <XCircle className="text-red-600" size={24} />;
      default: return null;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'positive': return 'text-green-600 bg-green-50';
      case 'negative': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  // Render validation results
  if (showResults && validationResult) {
    const report = validationResult.report;
    
    return (
      <div className="space-y-6 animate-slide-in" data-testid="validation-results">
        <PageHeader
          icon={Lightbulb}
          title="Validation Results"
          description={`${validationResult.ideaName} - ${validationResult.ideaType} Idea`}
          actions={
            <div className="flex space-x-2">
              <Button variant="outline" onClick={() => setShowResults(false)}>
                <ArrowLeft className="mr-2" size={16} />
                Edit Answers
              </Button>
              <Button onClick={resetForm} className="gradient-primary border-0">
                <RefreshCw className="mr-2" size={16} />
                New Validation
              </Button>
            </div>
          }
        />

        {/* Verdict Banner */}
        <Card className={`border-2 ${getVerdictColor(report.verdict)}`}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                {getVerdictIcon(report.verdict)}
                <div>
                  <h2 className="text-2xl font-bold">{report.verdict}</h2>
                  <p className="text-sm opacity-80">{report.verdictReason}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-4xl font-bold">{report.overallScore}</div>
                <div className="text-sm opacity-60">/ 100</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Output Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {report.outputCards?.map((card, i) => (
            <Card key={i} className="enterprise-card">
              <CardContent className="p-4">
                <p className="text-sm text-gray-500 mb-1">{card.title}</p>
                <p className={`text-xl font-bold ${card.status ? getStatusColor(card.status).split(' ')[0] : ''}`}>
                  {card.value}
                </p>
                {card.description && (
                  <p className="text-xs text-gray-400 mt-1">{card.description}</p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Score Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="mr-2 text-purple-600" size={20} />
              Score Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {report.scoreBreakdown?.map((item, i) => (
                <div key={i}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium">{item.name}</span>
                    <span className="text-sm">
                      <span className="font-bold">{item.score}</span>
                      <span className="text-gray-400">/{item.maxScore}</span>
                      <Badge variant="outline" className="ml-2 text-xs">
                        {item.assessment}
                      </Badge>
                    </span>
                  </div>
                  <Progress value={(item.score / item.maxScore) * 100} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Insights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Strengths */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-green-600">
                <CheckCircle className="mr-2" size={18} />
                Strengths Identified
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {report.strengths?.map((s, i) => (
                  <li key={i} className="flex items-start text-sm">
                    <CheckCircle className="mr-2 mt-0.5 flex-shrink-0 text-green-500" size={14} />
                    {s}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Weak Areas */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-orange-600">
                <AlertTriangle className="mr-2" size={18} />
                Weak Areas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {report.weakAreas?.map((w, i) => (
                  <li key={i} className="flex items-start text-sm">
                    <AlertTriangle className="mr-2 mt-0.5 flex-shrink-0 text-orange-500" size={14} />
                    {w}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Key Risks */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-red-600">
                <XCircle className="mr-2" size={18} />
                Key Risks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {report.keyRisks?.map((r, i) => (
                  <li key={i} className="flex items-start text-sm">
                    <XCircle className="mr-2 mt-0.5 flex-shrink-0 text-red-500" size={14} />
                    {r}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-purple-600">
                <Target className="mr-2" size={18} />
                Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {report.recommendations?.map((r, i) => (
                  <li key={i} className="flex items-start text-sm">
                    <span className="mr-2 mt-0.5 flex-shrink-0 w-5 h-5 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-xs font-bold">
                      {i + 1}
                    </span>
                    {r}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Next Experiments */}
        <Card className="bg-purple-50 border-purple-200">
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="mr-2 text-purple-600" size={20} />
              Next Validation Experiments
            </CardTitle>
            <CardDescription>Suggested actions to further validate your idea</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {report.nextExperiments?.map((exp, i) => (
                <div key={i} className="flex items-start p-3 bg-white rounded-lg">
                  <span className="mr-2 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">
                    {i + 1}
                  </span>
                  <span className="text-sm">{exp}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          <Button variant="outline" size="lg" onClick={() => setShowResults(false)}>
            Edit Answers
          </Button>
          <Button size="lg" className="gradient-primary border-0">
            Continue to Next Module
            <ArrowRight className="ml-2" size={18} />
          </Button>
        </div>
      </div>
    );
  }

  // Render wizard steps
  return (
    <div className="space-y-6 animate-slide-in" data-testid="idea-validation-wizard">
      <PageHeader
        icon={Lightbulb}
        title="Business/Product Idea and Validation"
        description="Answer a few questions and we'll generate a validation report"
      />

      {/* Progress Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Step {currentStep} of {TOTAL_STEPS}</span>
            <span className="text-sm text-gray-500">{Math.round((currentStep / TOTAL_STEPS) * 100)}% complete</span>
          </div>
          <Progress value={(currentStep / TOTAL_STEPS) * 100} className="h-2" />
        </CardContent>
      </Card>

      {/* Step Content */}
      <Card>
        <CardContent className="p-6">
          {/* Step 1: Idea Type */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">What are you validating?</h2>
                <p className="text-gray-500 text-sm">Choose the one that best matches what you're validating.</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                  onClick={() => updateField('ideaType', 'business')}
                  className={`p-6 border-2 rounded-xl cursor-pointer transition-all ${
                    formData.ideaType === 'business' 
                      ? 'border-purple-500 bg-purple-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center mb-4">
                    <Users className="text-white" size={24} />
                  </div>
                  <h3 className="font-semibold text-lg mb-1">Business Idea</h3>
                  <p className="text-sm text-gray-500">
                    A service, marketplace, or company concept you want to start
                  </p>
                </div>
                
                <div
                  onClick={() => updateField('ideaType', 'product')}
                  className={`p-6 border-2 rounded-xl cursor-pointer transition-all ${
                    formData.ideaType === 'product' 
                      ? 'border-purple-500 bg-purple-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="w-12 h-12 rounded-xl gradient-success flex items-center justify-center mb-4">
                    <FileText className="text-white" size={24} />
                  </div>
                  <h3 className="font-semibold text-lg mb-1">Product Idea</h3>
                  <p className="text-sm text-gray-500">
                    A physical, digital, or software product you want to build
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Brief Description */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">Brief Description</h2>
                <p className="text-gray-500 text-sm">Briefly describe your {formData.ideaType} idea in plain language.</p>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="ideaName">Idea Name *</Label>
                  <Input
                    id="ideaName"
                    value={formData.ideaName}
                    onChange={(e) => updateField('ideaName', e.target.value)}
                    placeholder="e.g., SmartMeal - AI Meal Planning App"
                    className="mt-1.5"
                  />
                </div>
                
                <div>
                  <Label htmlFor="ideaDescription">Idea Description *</Label>
                  <Textarea
                    id="ideaDescription"
                    value={formData.ideaDescription}
                    onChange={(e) => updateField('ideaDescription', e.target.value)}
                    placeholder="Describe what your idea does, what makes it unique, and the core value it provides..."
                    rows={5}
                    className="mt-1.5"
                  />
                  <p className="text-xs text-gray-400 mt-1">Aim for 3-6 sentences</p>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Industry */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">Industry</h2>
                <p className="text-gray-500 text-sm">What industry best fits your idea?</p>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="industry">Primary Industry *</Label>
                  <Select
                    value={formData.industry}
                    onValueChange={(value) => updateField('industry', value)}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder="Select an industry" />
                    </SelectTrigger>
                    <SelectContent>
                      {INDUSTRIES.map((ind) => (
                        <SelectItem key={ind} value={ind}>{ind}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="subIndustry">Sub-Industry (Optional)</Label>
                  <Input
                    id="subIndustry"
                    value={formData.subIndustry}
                    onChange={(e) => updateField('subIndustry', e.target.value)}
                    placeholder="e.g., FinTech, EdTech, HealthTech"
                    className="mt-1.5"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Problem & Audience */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">Problem & Audience</h2>
                <p className="text-gray-500 text-sm">What problem does it solve, and who experiences that problem?</p>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="problemSolved">Problem Being Solved *</Label>
                  <Textarea
                    id="problemSolved"
                    value={formData.problemSolved}
                    onChange={(e) => updateField('problemSolved', e.target.value)}
                    placeholder="Describe the specific problem your idea solves and why it matters..."
                    rows={4}
                    className="mt-1.5"
                  />
                </div>
                
                <div>
                  <Label htmlFor="targetAudience">Target Audience *</Label>
                  <Textarea
                    id="targetAudience"
                    value={formData.targetAudience}
                    onChange={(e) => updateField('targetAudience', e.target.value)}
                    placeholder="e.g., Small business owners aged 25-45, busy professionals, parents with young children..."
                    rows={2}
                    className="mt-1.5"
                  />
                </div>
                
                <div>
                  <Label>How urgent is this problem for your target audience? *</Label>
                  <Select
                    value={formData.urgencyLevel}
                    onValueChange={(value) => updateField('urgencyLevel', value)}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder="Select urgency level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low - Nice to have</SelectItem>
                      <SelectItem value="medium">Medium - Important but not critical</SelectItem>
                      <SelectItem value="high">High - Critical pain point</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          )}

          {/* Step 5: Solution & How It Works */}
          {currentStep === 5 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">Solution & How It Works</h2>
                <p className="text-gray-500 text-sm">Explain how your {formData.ideaType} solves the problem.</p>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="howItWorks">How It Works *</Label>
                  <Textarea
                    id="howItWorks"
                    value={formData.howItWorks}
                    onChange={(e) => updateField('howItWorks', e.target.value)}
                    placeholder="Describe the core mechanism of how your solution works, the key features, and how users will interact with it..."
                    rows={5}
                    className="mt-1.5"
                  />
                </div>
                
                <div>
                  <Label>Delivery Model *</Label>
                  <Select
                    value={formData.deliveryModel}
                    onValueChange={(value) => updateField('deliveryModel', value)}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder="How will you deliver this?" />
                    </SelectTrigger>
                    <SelectContent>
                      {(formData.ideaType === 'business' ? BUSINESS_DELIVERY_MODELS : PRODUCT_DELIVERY_MODELS).map((model) => (
                        <SelectItem key={model.value} value={model.value}>{model.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          )}

          {/* Step 6: Market & Location */}
          {currentStep === 6 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">Market & Location</h2>
                <p className="text-gray-500 text-sm">Define your target market and go-to-market strategy.</p>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Target Market *</Label>
                    <Select
                      value={formData.targetMarket}
                      onValueChange={(value) => updateField('targetMarket', value)}
                    >
                      <SelectTrigger className="mt-1.5">
                        <SelectValue placeholder="Select market type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="B2C">B2C - Business to Consumer</SelectItem>
                        <SelectItem value="B2B">B2B - Business to Business</SelectItem>
                        <SelectItem value="B2G">B2G - Business to Government</SelectItem>
                        <SelectItem value="Other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="targetLocation">Target Location *</Label>
                    <Input
                      id="targetLocation"
                      value={formData.targetLocation}
                      onChange={(e) => updateField('targetLocation', e.target.value)}
                      placeholder="e.g., UK (Manchester) / Nigeria / Global"
                      className="mt-1.5"
                    />
                  </div>
                </div>
                
                <div>
                  <Label>Customer Budget Level *</Label>
                  <Select
                    value={formData.customerBudget}
                    onValueChange={(value) => updateField('customerBudget', value)}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder="What can your target customers afford?" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low - Price-sensitive customers</SelectItem>
                      <SelectItem value="medium">Medium - Moderate spending power</SelectItem>
                      <SelectItem value="high">High - Premium customers</SelectItem>
                      <SelectItem value="unknown">Unknown - Need to research</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label className="mb-3 block">Go-To-Market Channels *</Label>
                  <p className="text-xs text-gray-500 mb-3">Select all channels you plan to use to reach customers</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {GTM_CHANNELS.map((channel) => (
                      <div
                        key={channel}
                        onClick={() => toggleGTMChannel(channel)}
                        className={`p-3 border rounded-lg cursor-pointer text-center transition-all ${
                          formData.goToMarketChannel.includes(channel)
                            ? 'border-purple-500 bg-purple-50 text-purple-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <span className="text-sm font-medium">{channel}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={handleBack}
          disabled={currentStep === 1}
        >
          <ArrowLeft className="mr-2" size={16} />
          Back
        </Button>
        
        {currentStep < TOTAL_STEPS ? (
          <Button
            onClick={handleNext}
            disabled={!canProceed()}
            className="gradient-primary border-0"
          >
            Next
            <ArrowRight className="ml-2" size={16} />
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            disabled={!canProceed() || loading}
            className="gradient-primary border-0"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Validating...
              </>
            ) : (
              <>
                Generate Validation Report
                <ArrowRight className="ml-2" size={16} />
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
