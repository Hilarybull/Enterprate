import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
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
  Loader2,
  Users,
  FileText,
  History,
  Info
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
  'Referrals', 'Ads', 'Partnerships', 'Marketplace', 'Outbound', 'SEO', 'Social'
];

const BUSINESS_TYPES = [
  { value: 'cleaning', label: 'Cleaning' },
  { value: 'it_services', label: 'IT Services' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'trades', label: 'Trades' },
  { value: 'consulting', label: 'Consulting' },
  { value: 'other', label: 'Other' }
];

const PROBLEM_TYPES = ['cost', 'time', 'compliance', 'quality', 'reliability'];
const PROBLEM_FREQUENCIES = ['daily', 'weekly', 'monthly'];
const CUSTOMER_SEGMENTS = ['Small offices', 'SMEs', 'Freelancers', 'Households', 'Other'];
const PRICING_MODELS = [
  { value: 'hourly', label: 'Hourly' },
  { value: 'fixed_job', label: 'Fixed Job' },
  { value: 'retainer', label: 'Retainer' },
  { value: 'subscription', label: 'Subscription' }
];
const DELIVERABLE_UNITS = ['hour', 'job', 'month', 'project'];
const PAYMENT_TERMS = [0, 7, 14, 30, 60];

const TOTAL_STEPS = 6;

const FieldHelp = ({ text }) => (
  <span
    className="inline-flex align-middle ml-1 text-gray-400 cursor-help"
    title={text}
    aria-label={text}
  >
    <Info size={12} />
  </span>
);

const EMPTY_FORM = {
  ideaType: 'business',
  ideaName: '',
  ideaDescription: '',
  industry: '',
  subIndustry: '',
  businessType: '',
  problemSolved: '',
  targetAudience: '',
  urgencyLevel: '',
  howItWorks: '',
  deliveryModel: '',
  targetMarket: '',
  targetLocation: '',
  customerBudget: '',
  goToMarketChannel: [],
  founderAvailabilityHoursPerWeek: '',
  stage: 'idea',
  customerSegment: '',
  problemType: [],
  problemFrequency: '',
  currentAlternatives: '',
  serviceType: '',
  pricingModel: '',
  priceAmount: '',
  deliverableUnit: '',
  packageTiers: '',
  expectedUnitsPerMonth: '',
  expectedCustomers: '',
  salesCycleDays: '',
  paymentTermsDays: '',
  variableCostPerUnit: '',
  fixedMonthlyCosts: '',
  founderDrawMonthly: '',
  contractorCostsMonthly: '',
  staffCount: '',
  capacityPerStaffPerMonth: '',
  cashBuffer: '',
  upfrontCosts: ''
};

export default function IdeaDiscovery() {
  const navigate = useNavigate();
  const { modifyId } = useParams(); // For modify mode
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [isModifyMode, setIsModifyMode] = useState(false);
  
  const [formData, setFormData] = useState(EMPTY_FORM);

  const normalizeFormData = (value) => ({
    ...EMPTY_FORM,
    ...(value || {}),
    problemType: Array.isArray(value?.problemType)
      ? value.problemType
      : value?.problemType ? [value.problemType] : [],
    goToMarketChannel: Array.isArray(value?.goToMarketChannel)
      ? value.goToMarketChannel
      : []
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
          setFormData(normalizeFormData(parsed.formData));
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
        setFormData(normalizeFormData(response.data.ideaInput));
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

  const toggleProblemType = (value) => {
    setFormData((prev) => ({
      ...prev,
      problemType: prev.problemType.includes(value)
        ? prev.problemType.filter((item) => item !== value)
        : [...prev.problemType, value]
    }));
  };

  const isBusinessPath = formData.ideaType === 'business';

  const canProceed = () => true;

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

    const toNumberOrNull = (value) => {
      if (value === '' || value === null || value === undefined) return null;
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : null;
    };

    const toTextOrNull = (value) => {
      if (value === null || value === undefined) return null;
      const text = String(value).trim();
      return text.length ? text : null;
    };

    const payload = {
      ...formData,
      ideaType: toTextOrNull(formData.ideaType) || 'business',
      ideaName: toTextOrNull(formData.ideaName),
      ideaDescription: toTextOrNull(formData.ideaDescription),
      industry: toTextOrNull(formData.industry) || 'General',
      subIndustry: toTextOrNull(formData.subIndustry),
      businessType: toTextOrNull(formData.businessType),
      problemSolved: toTextOrNull(formData.problemSolved),
      targetAudience: toTextOrNull(formData.targetAudience),
      urgencyLevel: toTextOrNull(formData.urgencyLevel),
      howItWorks: toTextOrNull(formData.howItWorks),
      deliveryModel: toTextOrNull(formData.deliveryModel),
      targetMarket: toTextOrNull(formData.targetMarket) || 'B2C',
      targetLocation: toTextOrNull(formData.targetLocation) || 'UK',
      customerBudget: toTextOrNull(formData.customerBudget) || 'unknown',
      customerSegment: toTextOrNull(formData.customerSegment),
      problemFrequency: toTextOrNull(formData.problemFrequency),
      currentAlternatives: toTextOrNull(formData.currentAlternatives),
      serviceType: toTextOrNull(formData.serviceType),
      pricingModel: toTextOrNull(formData.pricingModel),
      deliverableUnit: toTextOrNull(formData.deliverableUnit),
      packageTiers: toTextOrNull(formData.packageTiers),
      stage: toTextOrNull(formData.stage) || 'idea',
      goToMarketChannel: Array.isArray(formData.goToMarketChannel) ? formData.goToMarketChannel : [],
      problemType: Array.isArray(formData.problemType) ? formData.problemType : [],
      founderAvailabilityHoursPerWeek: toNumberOrNull(formData.founderAvailabilityHoursPerWeek),
      priceAmount: toNumberOrNull(formData.priceAmount),
      expectedUnitsPerMonth: toNumberOrNull(formData.expectedUnitsPerMonth),
      expectedCustomers: toNumberOrNull(formData.expectedCustomers),
      salesCycleDays: toNumberOrNull(formData.salesCycleDays),
      paymentTermsDays: toNumberOrNull(formData.paymentTermsDays),
      variableCostPerUnit: toNumberOrNull(formData.variableCostPerUnit),
      fixedMonthlyCosts: toNumberOrNull(formData.fixedMonthlyCosts),
      founderDrawMonthly: toNumberOrNull(formData.founderDrawMonthly),
      contractorCostsMonthly: toNumberOrNull(formData.contractorCostsMonthly),
      staffCount: toNumberOrNull(formData.staffCount),
      capacityPerStaffPerMonth: toNumberOrNull(formData.capacityPerStaffPerMonth),
      cashBuffer: toNumberOrNull(formData.cashBuffer),
      upfrontCosts: toNumberOrNull(formData.upfrontCosts)
    };

    setLoading(true);
    try {
      let response;
      if (isModifyMode && modifyId) {
        // Modify existing report
        response = await axios.post(
          `${API_URL}/validation-reports/${modifyId}/modify`,
          payload,
          { headers: getHeaders() }
        );
        toast.success('Report regenerated!');
      } else {
        // Create new comprehensive report
        response = await axios.post(
          `${API_URL}/validation-reports`,
          payload,
          { headers: getHeaders() }
        );
        toast.success('Validation complete!');
      }
      
      // Clear saved data
      localStorage.removeItem('enterprate_idea_validation');
      
      // Navigate to the report view
      const reportId = response.data.id;
      navigate(`/validation-report/${reportId}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to validate idea');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Render wizard steps
  return (
    <div className="space-y-6 animate-slide-in" data-testid="idea-validation-wizard">
      <PageHeader
        icon={Lightbulb}
        title={isModifyMode ? "Modify Validation" : "Business/Product Idea and Validation"}
        description={isModifyMode ? "Update your idea details and regenerate the report" : "Answer a few questions and we'll generate a comprehensive validation report"}
        actions={
          <div className="flex space-x-2">
            {isModifyMode && (
              <Button variant="outline" onClick={() => navigate(`/validation-report/${modifyId}`)}>
                <ArrowLeft className="mr-2" size={16} />
                Back to Report
              </Button>
            )}
            <Button variant="outline" onClick={() => navigate('/validation-history')}>
              <History className="mr-2" size={16} />
              View History
            </Button>
          </div>
        }
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
                <p className="text-gray-500 text-sm">Choose the one that best matches what you are validating.</p>
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

          {/* Step 2: Setup Business Context */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">Setup Business Context</h2>
                <p className="text-gray-500 text-sm">Capture your starting context before deterministic evaluation.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="ideaName">
                    {isBusinessPath ? 'Business Name' : 'Product/Service Name'}
                    <FieldHelp text="Use the name customers will recognize." />
                  </Label>
                  <Input
                    id="ideaName"
                    value={formData.ideaName}
                    onChange={(e) => updateField('ideaName', e.target.value)}
                    placeholder={isBusinessPath ? 'e.g., SparklePro Cleaning' : 'e.g., Managed IT Helpdesk'}
                    className="mt-1.5"
                  />
                </div>

                <div>
                  <Label htmlFor="targetLocation">
                    Location
                    <FieldHelp text="Enter your main launch market: city, country, or global." />
                  </Label>
                  <Input
                    id="targetLocation"
                    value={formData.targetLocation}
                    onChange={(e) => updateField('targetLocation', e.target.value)}
                    placeholder="e.g., London / Manchester / UK-wide"
                    className="mt-1.5"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="ideaDescription">
                  What are you building?
                  <FieldHelp text="Write one clear sentence on what the app or service does and who it helps." />
                </Label>
                <Textarea
                  id="ideaDescription"
                  value={formData.ideaDescription}
                  onChange={(e) => updateField('ideaDescription', e.target.value)}
                  placeholder="Short summary of your business idea and what it will deliver."
                  rows={3}
                  className="mt-1.5"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="industry">
                    Primary Industry
                    <FieldHelp text="Choose the closest industry to your core use case." />
                  </Label>
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

                {isBusinessPath && (
                  <div>
                    <Label>
                      Business Type
                      <FieldHelp text="Pick the operating model that best fits your service." />
                    </Label>
                    <Select
                      value={formData.businessType}
                      onValueChange={(value) => updateField('businessType', value)}
                    >
                      <SelectTrigger className="mt-1.5">
                        <SelectValue placeholder="Select business type" />
                      </SelectTrigger>
                      <SelectContent>
                        {BUSINESS_TYPES.map((item) => (
                          <SelectItem key={item.value} value={item.value}>{item.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="founderAvailabilityHoursPerWeek">
                    Founder hours/week (optional)
                    <FieldHelp text="How many hours per week you can commit to building and delivery." />
                  </Label>
                  <Input
                    id="founderAvailabilityHoursPerWeek"
                    type="number"
                    min="1"
                    max="80"
                    value={formData.founderAvailabilityHoursPerWeek}
                    onChange={(e) => updateField('founderAvailabilityHoursPerWeek', e.target.value)}
                    className="mt-1.5"
                  />
                </div>

                <div>
                  <Label>
                    Stage
                    <FieldHelp text="Idea means pre-launch. Running Business means already operating." />
                  </Label>
                  <Select value={formData.stage} onValueChange={(value) => updateField('stage', value)}>
                    <SelectTrigger className="mt-1.5">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="idea">Idea</SelectItem>
                      <SelectItem value="running">Running Business</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Problem & Target Customer */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">Problem & Target Customer</h2>
                <p className="text-gray-500 text-sm">Define who you serve, what hurts, and how often it happens.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>
                    Customer Segment
                    <FieldHelp text="Choose the primary group you want to serve first." />
                  </Label>
                  <Select
                    value={formData.customerSegment}
                    onValueChange={(value) => updateField('customerSegment', value)}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder="Select customer segment" />
                    </SelectTrigger>
                    <SelectContent>
                      {CUSTOMER_SEGMENTS.map((item) => (
                        <SelectItem key={item} value={item}>{item}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>
                    Problem Frequency
                    <FieldHelp text="How often this pain happens for the customer." />
                  </Label>
                  <Select value={formData.problemFrequency} onValueChange={(value) => updateField('problemFrequency', value)}>
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder="Select frequency" />
                    </SelectTrigger>
                    <SelectContent>
                      {PROBLEM_FREQUENCIES.map((item) => (
                        <SelectItem key={item} value={item}>{item}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="targetAudience">
                  Target Audience Details
                  <FieldHelp text="Specify who they are, where they are, and the concrete pain they face." />
                </Label>
                <Textarea
                  id="targetAudience"
                  value={formData.targetAudience}
                  onChange={(e) => updateField('targetAudience', e.target.value)}
                  placeholder="Describe your ideal customer profile."
                  rows={3}
                  className="mt-1.5"
                />
              </div>

              <div>
                <Label className="mb-3 block">
                  Problem Type (select all that apply)
                  <FieldHelp text="Select the pain categories this idea addresses." />
                </Label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {PROBLEM_TYPES.map((item) => (
                    <label key={item} className="flex items-center gap-2 p-3 border rounded-lg cursor-pointer">
                      <Checkbox
                        checked={formData.problemType.includes(item)}
                        onCheckedChange={() => toggleProblemType(item)}
                      />
                      <span className="text-sm capitalize">{item}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <Label htmlFor="problemSolved">
                  Problem Statement
                  <FieldHelp text="One sentence: customer pain plus measurable impact." />
                </Label>
                <Textarea
                  id="problemSolved"
                  value={formData.problemSolved}
                  onChange={(e) => updateField('problemSolved', e.target.value)}
                  placeholder="What specific problem are you solving?"
                  rows={3}
                  className="mt-1.5"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="currentAlternatives">
                    Current Alternatives (optional)
                    <FieldHelp text="What they use today: competitors, manual process, in-house, or nothing." />
                  </Label>
                  <Textarea
                    id="currentAlternatives"
                    value={formData.currentAlternatives}
                    onChange={(e) => updateField('currentAlternatives', e.target.value)}
                    placeholder="e.g., in-house, freelancer, competitor, do nothing"
                    rows={2}
                    className="mt-1.5"
                  />
                </div>
                <div>
                  <Label>
                    Urgency Level
                    <FieldHelp text="How urgent this pain is for customers right now." />
                  </Label>
                  <Select
                    value={formData.urgencyLevel}
                    onValueChange={(value) => updateField('urgencyLevel', value)}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder="Select urgency level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Offer Definition & Demand Assumptions */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">Offer Definition & Demand Assumptions</h2>
                <p className="text-gray-500 text-sm">Define what you sell, how you charge, and expected monthly demand.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="serviceType">
                    Service Type
                    <FieldHelp text="Name the exact offer customers will buy." />
                  </Label>
                  <Input
                    id="serviceType"
                    value={formData.serviceType}
                    onChange={(e) => updateField('serviceType', e.target.value)}
                    placeholder="e.g., Deep Cleaning, IT support retainer"
                    className="mt-1.5"
                  />
                </div>

                <div>
                  <Label>
                    Delivery Model
                    <FieldHelp text="How customers receive it: service, app, marketplace, or subscription." />
                  </Label>
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

              <div>
                <Label htmlFor="howItWorks">
                  How It Works
                  <FieldHelp text="Two short sentences: how users access it and how value is delivered." />
                </Label>
                <Textarea
                  id="howItWorks"
                  value={formData.howItWorks}
                  onChange={(e) => updateField('howItWorks', e.target.value)}
                  placeholder="Describe your service/package delivery process."
                  rows={3}
                  className="mt-1.5"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <Label>
                    Pricing Model
                    <FieldHelp text="How you charge: hourly, fixed job, retainer, or subscription." />
                  </Label>
                  <Select
                    value={formData.pricingModel}
                    onValueChange={(value) => updateField('pricingModel', value)}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder="Select model" />
                    </SelectTrigger>
                    <SelectContent>
                      {PRICING_MODELS.map((item) => (
                        <SelectItem key={item.value} value={item.value}>{item.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="priceAmount">
                    Price (local currency)
                    <FieldHelp text="Amount paid per deliverable unit." />
                  </Label>
                  <Input
                    id="priceAmount"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.priceAmount}
                    onChange={(e) => updateField('priceAmount', e.target.value)}
                    className="mt-1.5"
                  />
                </div>

                <div>
                  <Label>
                    Deliverable Unit
                    <FieldHelp text="Unit tied to your price, for example hour, job, month, or project." />
                  </Label>
                  <Select
                    value={formData.deliverableUnit}
                    onValueChange={(value) => updateField('deliverableUnit', value)}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder="Select unit" />
                    </SelectTrigger>
                    <SelectContent>
                      {DELIVERABLE_UNITS.map((item) => (
                        <SelectItem key={item} value={item}>{item}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="packageTiers">
                    Package Tiers (optional)
                    <FieldHelp text="Optional package ladder like Basic, Standard, Premium." />
                  </Label>
                  <Input
                    id="packageTiers"
                    value={formData.packageTiers}
                    onChange={(e) => updateField('packageTiers', e.target.value)}
                    placeholder="Basic / Standard / Premium"
                    className="mt-1.5"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <Label htmlFor="expectedUnitsPerMonth">
                    Expected Units/Month
                    <FieldHelp text="Estimated billable units you can deliver monthly." />
                  </Label>
                  <Input
                    id="expectedUnitsPerMonth"
                    type="number"
                    min="0"
                    value={formData.expectedUnitsPerMonth}
                    onChange={(e) => updateField('expectedUnitsPerMonth', e.target.value)}
                    className="mt-1.5"
                  />
                </div>

                <div>
                  <Label htmlFor="expectedCustomers">
                    Expected Customers
                    <FieldHelp text="Estimated number of paying customers per month." />
                  </Label>
                  <Input
                    id="expectedCustomers"
                    type="number"
                    min="0"
                    value={formData.expectedCustomers}
                    onChange={(e) => updateField('expectedCustomers', e.target.value)}
                    className="mt-1.5"
                  />
                </div>

                <div>
                  <Label htmlFor="salesCycleDays">
                    Sales Cycle (days)
                    <FieldHelp text="Average days from first contact to payment commitment." />
                  </Label>
                  <Input
                    id="salesCycleDays"
                    type="number"
                    min="1"
                    value={formData.salesCycleDays}
                    onChange={(e) => updateField('salesCycleDays', e.target.value)}
                    className="mt-1.5"
                  />
                </div>

                <div>
                  <Label>
                    Payment Terms
                    <FieldHelp text="How long after invoice customers pay." />
                  </Label>
                  <Select
                    value={formData.paymentTermsDays}
                    onValueChange={(value) => updateField('paymentTermsDays', value)}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder="Select terms" />
                    </SelectTrigger>
                    <SelectContent>
                      {PAYMENT_TERMS.map((item) => (
                        <SelectItem key={item} value={String(item)}>
                          {item === 0 ? 'Immediately' : `${item} days`}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          )}

          {/* Step 5: Cost Inputs, Capacity & Cash Buffer */}
          {currentStep === 5 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">Cost Inputs, Capacity & Cash Buffer</h2>
                <p className="text-gray-500 text-sm">Set unit costs, fixed costs, delivery capacity, and optional cash buffer.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="variableCostPerUnit">
                    Variable Cost per Unit (local currency)
                    <FieldHelp text="Direct cost to deliver one unit (materials, tools, transaction fees)." />
                  </Label>
                  <Input
                    id="variableCostPerUnit"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.variableCostPerUnit}
                    onChange={(e) => updateField('variableCostPerUnit', e.target.value)}
                    className="mt-1.5"
                  />
                </div>

                <div>
                  <Label htmlFor="fixedMonthlyCosts">
                    Fixed Monthly Costs (local currency)
                    <FieldHelp text="Recurring monthly overheads like rent, software, admin, and utilities." />
                  </Label>
                  <Input
                    id="fixedMonthlyCosts"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.fixedMonthlyCosts}
                    onChange={(e) => updateField('fixedMonthlyCosts', e.target.value)}
                    className="mt-1.5"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="founderDrawMonthly">
                    Founder Draw/Month (optional)
                    <FieldHelp text="Monthly amount you plan to pay yourself." />
                  </Label>
                  <Input
                    id="founderDrawMonthly"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.founderDrawMonthly}
                    onChange={(e) => updateField('founderDrawMonthly', e.target.value)}
                    className="mt-1.5"
                  />
                </div>
                <div>
                  <Label htmlFor="contractorCostsMonthly">
                    Contractor Costs/Month (optional)
                    <FieldHelp text="Monthly spend on freelancers or contractors." />
                  </Label>
                  <Input
                    id="contractorCostsMonthly"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.contractorCostsMonthly}
                    onChange={(e) => updateField('contractorCostsMonthly', e.target.value)}
                    className="mt-1.5"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="founderAvailabilityHoursPerWeekStep5">
                    Founder hours/week
                    <FieldHelp text="Available weekly founder time for delivery and operations." />
                  </Label>
                  <Input
                    id="founderAvailabilityHoursPerWeekStep5"
                    type="number"
                    min="1"
                    max="80"
                    value={formData.founderAvailabilityHoursPerWeek}
                    onChange={(e) => updateField('founderAvailabilityHoursPerWeek', e.target.value)}
                    className="mt-1.5"
                  />
                </div>
                <div>
                  <Label htmlFor="staffCount">
                    Team Count (optional)
                    <FieldHelp text="Number of active delivery staff excluding optional contractors." />
                  </Label>
                  <Input
                    id="staffCount"
                    type="number"
                    min="0"
                    value={formData.staffCount}
                    onChange={(e) => updateField('staffCount', e.target.value)}
                    className="mt-1.5"
                  />
                </div>
                <div>
                  <Label htmlFor="capacityPerStaffPerMonth">
                    Capacity per Staff/Month
                    <FieldHelp text="How many units one staff member can deliver in a month." />
                  </Label>
                  <Input
                    id="capacityPerStaffPerMonth"
                    type="number"
                    min="0"
                    value={formData.capacityPerStaffPerMonth}
                    onChange={(e) => updateField('capacityPerStaffPerMonth', e.target.value)}
                    className="mt-1.5"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="cashBuffer">
                    Cash Buffer (optional)
                    <FieldHelp text="Available cash reserve to survive slow months or delays." />
                  </Label>
                  <Input
                    id="cashBuffer"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.cashBuffer}
                    onChange={(e) => updateField('cashBuffer', e.target.value)}
                    className="mt-1.5"
                  />
                </div>
                <div>
                  <Label htmlFor="upfrontCosts">
                    Startup One-off Costs (optional)
                    <FieldHelp text="One-time launch costs like setup, hardware, branding, or legal." />
                  </Label>
                  <Input
                    id="upfrontCosts"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.upfrontCosts}
                    onChange={(e) => updateField('upfrontCosts', e.target.value)}
                    className="mt-1.5"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 6: Market Context & Go-To-Market */}
          {currentStep === 6 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">Market Context & Go-To-Market</h2>
                <p className="text-gray-500 text-sm">Final inputs before baseline metrics, score, and simulation-ready output.</p>
              </div>

              <div className="p-4 rounded-lg border border-blue-200 bg-blue-50 text-sm text-blue-900">
                Market context is auto-enriched from sector/location benchmarks and used as advisory input.
                It does not overwrite your assumptions.
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label>
                      Target Market
                      <FieldHelp text="Choose whether you sell primarily to consumers, businesses, or government." />
                    </Label>
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
                    <Label>
                      Customer Budget Level
                      <FieldHelp text="Expected customer spending ability for this offer." />
                    </Label>
                    <Select
                      value={formData.customerBudget}
                      onValueChange={(value) => updateField('customerBudget', value)}
                    >
                      <SelectTrigger className="mt-1.5">
                        <SelectValue placeholder="Select budget level" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="unknown">Unknown</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="subIndustry">
                      Sub-Industry (optional)
                      <FieldHelp text="More specific niche within your primary industry." />
                    </Label>
                    <Input
                      id="subIndustry"
                      value={formData.subIndustry}
                      onChange={(e) => updateField('subIndustry', e.target.value)}
                      placeholder="e.g., Managed IT Services"
                      className="mt-1.5"
                    />
                  </div>
                </div>

                <div>
                  <Label className="mb-3 block">
                    Go-To-Market Channels
                    <FieldHelp text="Select your first customer acquisition channels." />
                  </Label>
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
                {isModifyMode ? 'Regenerating...' : 'Validating...'}
              </>
            ) : (
              <>
                {isModifyMode ? 'Regenerate Report' : 'Generate Validation Report'}
                <ArrowRight className="ml-2" size={16} />
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
