import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  FileText, 
  CheckCircle, 
  Building2,
  Scale,
  Shield,
  FileCheck,
  ArrowRight,
  ArrowLeft,
  Users,
  MapPin,
  Loader2,
  AlertCircle,
  Lightbulb,
  Search,
  User,
  Briefcase,
  CreditCard,
  Upload,
  Home,
  Building,
  HelpCircle,
  Sparkles,
  Check,
  X
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// Step configuration
const STEPS = [
  { id: 1, title: 'Business Type', icon: Building2, description: 'Choose your business structure' },
  { id: 2, title: 'Company Name', icon: FileText, description: 'Select a unique company name' },
  { id: 3, title: 'Business Activity', icon: Briefcase, description: 'Describe what your company does' },
  { id: 4, title: 'People Involved', icon: Users, description: 'Directors, shareholders & PSC' },
  { id: 5, title: 'Registered Address', icon: MapPin, description: 'Official company address' },
  { id: 6, title: 'Company Documents', icon: FileCheck, description: 'Articles of Association' },
  { id: 7, title: 'Identity Verification', icon: Shield, description: 'KYC & AML compliance' },
  { id: 8, title: 'Submit Registration', icon: CreditCard, description: 'Review and submit' }
];

// Business type options
const BUSINESS_TYPES = [
  {
    id: 'ltd',
    title: 'Private Limited Company (Ltd)',
    description: 'Separate legal entity with limited liability. Best for credibility and growth.',
    recommended: true,
    benefits: ['Limited liability protection', 'Professional credibility', 'Tax advantages', 'Easier to raise investment']
  },
  {
    id: 'sole_trader',
    title: 'Sole Trader',
    description: 'Simplest structure. You and the business are legally the same.',
    benefits: ['Easy to set up', 'Minimal paperwork', 'Full control', 'Simple taxes']
  },
  {
    id: 'partnership',
    title: 'Partnership / LLP',
    description: 'Business owned by two or more people with shared profits.',
    benefits: ['Shared responsibility', 'Combined expertise', 'Flexible structure']
  },
  {
    id: 'charity',
    title: 'Charity / CIC',
    description: 'Community Interest Company or charitable organization.',
    benefits: ['Tax exemptions', 'Grant eligibility', 'Community focus']
  }
];

// SIC code suggestions (sample)
const SIC_CODES = [
  { code: '62020', name: 'Information technology consultancy activities' },
  { code: '62090', name: 'Other information technology service activities' },
  { code: '63110', name: 'Data processing, hosting and related activities' },
  { code: '70229', name: 'Management consultancy activities' },
  { code: '73110', name: 'Advertising agencies' },
  { code: '74909', name: 'Other professional activities' },
  { code: '82990', name: 'Other business support service activities' },
  { code: '47910', name: 'Retail sale via mail order houses or via Internet' }
];

// Tip component
const Tip = ({ children }) => (
  <div className="flex items-start space-x-2 p-3 bg-purple-50 rounded-lg border border-purple-100 text-sm">
    <Lightbulb className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
    <span className="text-purple-800">{children}</span>
  </div>
);

// Name availability checker component
const NameChecker = ({ name, onAvailabilityChange }) => {
  const [status, setStatus] = useState(null); // null, 'checking', 'available', 'unavailable'
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    if (name.length < 3) {
      setStatus(null);
      return;
    }

    setStatus('checking');
    const timer = setTimeout(() => {
      // Simulate name check - in production, this would call an API
      const isAvailable = !name.toLowerCase().includes('apple') && 
                          !name.toLowerCase().includes('google') &&
                          !name.toLowerCase().includes('microsoft');
      
      setStatus(isAvailable ? 'available' : 'unavailable');
      onAvailabilityChange(isAvailable);
      
      if (!isAvailable) {
        setSuggestions([
          `${name} Solutions Ltd`,
          `${name} Group Ltd`,
          `${name} UK Ltd`
        ]);
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [name]);

  if (!name || name.length < 3) return null;

  return (
    <div className="mt-2">
      {status === 'checking' && (
        <div className="flex items-center text-gray-500 text-sm">
          <Loader2 className="w-4 h-4 animate-spin mr-2" />
          Checking availability...
        </div>
      )}
      {status === 'available' && (
        <div className="flex items-center text-green-600 text-sm">
          <Check className="w-4 h-4 mr-2" />
          This name is available!
        </div>
      )}
      {status === 'unavailable' && (
        <div className="space-y-2">
          <div className="flex items-center text-red-600 text-sm">
            <X className="w-4 h-4 mr-2" />
            This name may be too similar to an existing company
          </div>
          {suggestions.length > 0 && (
            <div className="text-sm text-gray-600">
              <p className="font-medium mb-1">Try these alternatives:</p>
              <ul className="space-y-1">
                {suggestions.map((s, i) => (
                  <li key={i} className="text-purple-600 cursor-pointer hover:underline">• {s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Director/Shareholder form component
const PersonForm = ({ person, onChange, onRemove, index, type }) => (
  <Card className="border-gray-200">
    <CardContent className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="font-semibold">{type} {index + 1}</h4>
        {index > 0 && (
          <Button variant="ghost" size="sm" onClick={onRemove} className="text-red-600">
            Remove
          </Button>
        )}
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>First Name *</Label>
          <Input 
            value={person.firstName || ''} 
            onChange={(e) => onChange({ ...person, firstName: e.target.value })}
            placeholder="John"
          />
        </div>
        <div>
          <Label>Last Name *</Label>
          <Input 
            value={person.lastName || ''} 
            onChange={(e) => onChange({ ...person, lastName: e.target.value })}
            placeholder="Smith"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Date of Birth *</Label>
          <Input 
            type="date"
            value={person.dob || ''} 
            onChange={(e) => onChange({ ...person, dob: e.target.value })}
          />
        </div>
        <div>
          <Label>Nationality *</Label>
          <Select value={person.nationality || ''} onValueChange={(v) => onChange({ ...person, nationality: v })}>
            <SelectTrigger>
              <SelectValue placeholder="Select nationality" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="british">British</SelectItem>
              <SelectItem value="american">American</SelectItem>
              <SelectItem value="indian">Indian</SelectItem>
              <SelectItem value="chinese">Chinese</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div>
        <Label>Occupation *</Label>
        <Input 
          value={person.occupation || ''} 
          onChange={(e) => onChange({ ...person, occupation: e.target.value })}
          placeholder="e.g., Software Engineer, Consultant"
        />
      </div>

      <div>
        <Label>Residential Address *</Label>
        <Textarea 
          value={person.address || ''} 
          onChange={(e) => onChange({ ...person, address: e.target.value })}
          placeholder="Full residential address"
          rows={2}
        />
      </div>

      {type === 'Director' && (
        <div className="flex items-center space-x-2">
          <Checkbox 
            id={`service-${index}`}
            checked={person.useServiceAddress || false}
            onCheckedChange={(checked) => onChange({ ...person, useServiceAddress: checked })}
          />
          <Label htmlFor={`service-${index}`} className="text-sm">
            Use a different service address (this will be public)
          </Label>
        </div>
      )}

      {type === 'Shareholder' && (
        <div>
          <Label>Number of Shares *</Label>
          <Input 
            type="number"
            value={person.shares || ''} 
            onChange={(e) => onChange({ ...person, shares: e.target.value })}
            placeholder="100"
          />
        </div>
      )}
    </CardContent>
  </Card>
);

export default function BusinessRegistration() {
  const navigate = useNavigate();
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [nameAvailable, setNameAvailable] = useState(false);
  
  // Form data state
  const [formData, setFormData] = useState({
    // Step 1: Business Type
    businessType: '',
    
    // Step 2: Company Name
    companyName: '',
    
    // Step 3: Business Activity
    businessDescription: '',
    selectedSicCodes: [],
    
    // Step 4: People
    directors: [{ firstName: '', lastName: '', dob: '', nationality: '', occupation: '', address: '', useServiceAddress: false }],
    shareholders: [{ firstName: '', lastName: '', dob: '', nationality: '', occupation: '', address: '', shares: '100' }],
    directorIsShareholder: true,
    founderIsPSC: true,
    
    // Step 5: Registered Address
    addressType: 'home', // 'home', 'office', 'virtual'
    registeredAddress: '',
    useForMail: true,
    
    // Step 6: Documents
    articlesType: 'model', // 'model', 'custom'
    
    // Step 7: Verification
    idVerificationStatus: 'pending', // 'pending', 'in_progress', 'completed', 'failed'
    
    // Step 8: Submission
    agreedToTerms: false,
    paymentMethod: ''
  });

  // Calculate progress
  const progress = Math.round((currentStep / STEPS.length) * 100);

  // Update form data helper
  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // Add director/shareholder
  const addDirector = () => {
    setFormData(prev => ({
      ...prev,
      directors: [...prev.directors, { firstName: '', lastName: '', dob: '', nationality: '', occupation: '', address: '', useServiceAddress: false }]
    }));
  };

  const addShareholder = () => {
    setFormData(prev => ({
      ...prev,
      shareholders: [...prev.shareholders, { firstName: '', lastName: '', dob: '', nationality: '', occupation: '', address: '', shares: '' }]
    }));
  };

  // Update director/shareholder
  const updateDirector = (index, data) => {
    const updated = [...formData.directors];
    updated[index] = data;
    updateFormData('directors', updated);
  };

  const updateShareholder = (index, data) => {
    const updated = [...formData.shareholders];
    updated[index] = data;
    updateFormData('shareholders', updated);
  };

  // Remove director/shareholder
  const removeDirector = (index) => {
    const updated = formData.directors.filter((_, i) => i !== index);
    updateFormData('directors', updated);
  };

  const removeShareholder = (index) => {
    const updated = formData.shareholders.filter((_, i) => i !== index);
    updateFormData('shareholders', updated);
  };

  // Toggle SIC code
  const toggleSicCode = (code) => {
    const selected = formData.selectedSicCodes;
    if (selected.includes(code)) {
      updateFormData('selectedSicCodes', selected.filter(c => c !== code));
    } else if (selected.length < 4) {
      updateFormData('selectedSicCodes', [...selected, code]);
    } else {
      toast.error('Maximum 4 SIC codes allowed');
    }
  };

  // Validate current step
  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return !!formData.businessType;
      case 2:
        return formData.companyName.length >= 3 && nameAvailable;
      case 3:
        return formData.businessDescription.length >= 20 && formData.selectedSicCodes.length > 0;
      case 4:
        return formData.directors.every(d => d.firstName && d.lastName && d.dob && d.nationality) &&
               formData.shareholders.every(s => s.firstName && s.lastName && s.shares);
      case 5:
        return !!formData.registeredAddress;
      case 6:
        return !!formData.articlesType;
      case 7:
        return formData.idVerificationStatus === 'completed' || formData.idVerificationStatus === 'pending';
      case 8:
        return formData.agreedToTerms;
      default:
        return true;
    }
  };

  // Navigation
  const nextStep = () => {
    if (currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
      window.scrollTo(0, 0);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      window.scrollTo(0, 0);
    }
  };

  // Submit registration
  const handleSubmit = async () => {
    setLoading(true);
    try {
      // In production, this would submit to the backend
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success('Registration submitted successfully!');
      // Navigate to confirmation or dashboard
    } catch (error) {
      toast.error('Failed to submit registration');
    } finally {
      setLoading(false);
    }
  };

  // Render step content
  const renderStepContent = () => {
    switch (currentStep) {
      // STEP 1: Business Type
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">What type of business are you creating?</h2>
              <p className="text-gray-500">Choose the structure that best fits your needs. Most beginners choose a Private Limited Company.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {BUSINESS_TYPES.map(type => (
                <Card 
                  key={type.id}
                  className={`cursor-pointer transition-all ${
                    formData.businessType === type.id 
                      ? 'border-purple-500 ring-2 ring-purple-200' 
                      : 'hover:border-purple-300'
                  }`}
                  onClick={() => updateFormData('businessType', type.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="font-semibold">{type.title}</h3>
                          {type.recommended && (
                            <Badge className="bg-purple-100 text-purple-700">Recommended</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 mt-1">{type.description}</p>
                        <div className="mt-3 space-y-1">
                          {type.benefits.map((b, i) => (
                            <div key={i} className="flex items-center text-xs text-gray-600">
                              <Check className="w-3 h-3 text-green-500 mr-1" />
                              {b}
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        formData.businessType === type.id ? 'border-purple-600 bg-purple-600' : 'border-gray-300'
                      }`}>
                        {formData.businessType === type.id && <Check className="w-3 h-3 text-white" />}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Tip>
              If you want credibility, liability protection, and room to grow → Private Limited Company (Ltd) is the best choice for most beginners.
            </Tip>
          </div>
        );

      // STEP 2: Company Name
      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Choose a Company Name</h2>
              <p className="text-gray-500">Your company name must be unique and end with "Limited" or "Ltd"</p>
            </div>

            <Card>
              <CardContent className="p-6 space-y-4">
                <div>
                  <Label>Company Name *</Label>
                  <div className="flex space-x-2">
                    <Input 
                      value={formData.companyName}
                      onChange={(e) => updateFormData('companyName', e.target.value)}
                      placeholder="e.g., Acme Consulting"
                      className="flex-1"
                    />
                    <span className="flex items-center text-gray-500 bg-gray-100 px-3 rounded-md">Ltd</span>
                  </div>
                  <NameChecker 
                    name={formData.companyName} 
                    onAvailabilityChange={setNameAvailable}
                  />
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <h4 className="font-medium text-amber-800 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-2" />
                    Naming Rules
                  </h4>
                  <ul className="mt-2 text-sm text-amber-700 space-y-1">
                    <li>• Must be unique (not too similar to existing companies)</li>
                    <li>• Cannot include restricted words (e.g., "Bank", "Royal") without permission</li>
                    <li>• Must end with "Limited" or "Ltd"</li>
                    <li>• Cannot be offensive or misleading</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            <Tip>
              A good company name is memorable, easy to spell, and reflects your business. Avoid names too similar to well-known brands.
            </Tip>
          </div>
        );

      // STEP 3: Business Activity
      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Describe What Your Company Will Do</h2>
              <p className="text-gray-500">Explain your main activities. This helps us select the right SIC codes.</p>
            </div>

            <Card>
              <CardContent className="p-6 space-y-4">
                <div>
                  <Label>Business Description *</Label>
                  <Textarea 
                    value={formData.businessDescription}
                    onChange={(e) => updateFormData('businessDescription', e.target.value)}
                    placeholder="e.g., I provide IT consulting services to small businesses and may sell software products online in the future."
                    rows={4}
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    {formData.businessDescription.length}/500 characters
                  </p>
                </div>

                <div>
                  <Label className="mb-3 block">Select SIC Codes (up to 4) *</Label>
                  <p className="text-sm text-gray-500 mb-3">
                    SIC codes are official business activity codes used for classification.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {SIC_CODES.map(sic => (
                      <div 
                        key={sic.code}
                        onClick={() => toggleSicCode(sic.code)}
                        className={`p-3 border rounded-lg cursor-pointer transition-all ${
                          formData.selectedSicCodes.includes(sic.code)
                            ? 'border-purple-500 bg-purple-50'
                            : 'hover:border-purple-300'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="font-mono text-sm text-purple-600">{sic.code}</span>
                            <p className="text-sm text-gray-700">{sic.name}</p>
                          </div>
                          {formData.selectedSicCodes.includes(sic.code) && (
                            <Check className="w-4 h-4 text-purple-600" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Tip>
              Select codes that cover your current activities and any you plan to do in the future. You can change these later.
            </Tip>
          </div>
        );

      // STEP 4: People Involved
      case 4:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Who Is Involved in the Company?</h2>
              <p className="text-gray-500">Add directors, shareholders, and people with significant control.</p>
            </div>

            {/* Directors Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Directors</h3>
                  <p className="text-sm text-gray-500">At least one director required. Must be 16+ years old.</p>
                </div>
                <Button variant="outline" size="sm" onClick={addDirector}>
                  + Add Director
                </Button>
              </div>
              
              {formData.directors.map((director, index) => (
                <PersonForm 
                  key={index}
                  person={director}
                  onChange={(data) => updateDirector(index, data)}
                  onRemove={() => removeDirector(index)}
                  index={index}
                  type="Director"
                />
              ))}
            </div>

            {/* Quick setup option */}
            <Card className="bg-purple-50 border-purple-200">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="director-is-shareholder"
                    checked={formData.directorIsShareholder}
                    onCheckedChange={(checked) => updateFormData('directorIsShareholder', checked)}
                  />
                  <Label htmlFor="director-is-shareholder">
                    The director above is also the sole shareholder (owns 100% of shares)
                  </Label>
                </div>
              </CardContent>
            </Card>

            {/* Shareholders Section */}
            {!formData.directorIsShareholder && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">Shareholders</h3>
                    <p className="text-sm text-gray-500">People who own shares in the company.</p>
                  </div>
                  <Button variant="outline" size="sm" onClick={addShareholder}>
                    + Add Shareholder
                  </Button>
                </div>
                
                {formData.shareholders.map((shareholder, index) => (
                  <PersonForm 
                    key={index}
                    person={shareholder}
                    onChange={(data) => updateShareholder(index, data)}
                    onRemove={() => removeShareholder(index)}
                    index={index}
                    type="Shareholder"
                  />
                ))}
              </div>
            )}

            {/* PSC Notice */}
            <Card className="border-blue-200 bg-blue-50">
              <CardContent className="p-4">
                <h4 className="font-semibold text-blue-800 flex items-center">
                  <Shield className="w-4 h-4 mr-2" />
                  People with Significant Control (PSC)
                </h4>
                <p className="text-sm text-blue-700 mt-1">
                  Anyone who owns more than 25% of shares or has significant influence must be registered as a PSC.
                </p>
                <div className="flex items-center space-x-2 mt-3">
                  <Checkbox 
                    id="founder-psc"
                    checked={formData.founderIsPSC}
                    onCheckedChange={(checked) => updateFormData('founderIsPSC', checked)}
                  />
                  <Label htmlFor="founder-psc" className="text-sm">
                    I confirm the founder/director above is a Person with Significant Control
                  </Label>
                </div>
              </CardContent>
            </Card>

            <Tip>
              Most single-founder companies have 1 director who is also the sole shareholder and PSC. We recommend 100 ordinary shares.
            </Tip>
          </div>
        );

      // STEP 5: Registered Address
      case 5:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Choose a Registered Office Address</h2>
              <p className="text-gray-500">This is the official company address (public record). Must be a UK physical address.</p>
            </div>

            <Card>
              <CardContent className="p-6 space-y-4">
                <div>
                  <Label className="mb-3 block">Address Type</Label>
                  <div className="grid grid-cols-3 gap-4">
                    {[
                      { id: 'home', icon: Home, label: 'Home Address' },
                      { id: 'office', icon: Building, label: 'Office Address' },
                      { id: 'virtual', icon: MapPin, label: 'Virtual Office' }
                    ].map(type => (
                      <div
                        key={type.id}
                        onClick={() => updateFormData('addressType', type.id)}
                        className={`p-4 border rounded-lg cursor-pointer text-center transition-all ${
                          formData.addressType === type.id
                            ? 'border-purple-500 bg-purple-50'
                            : 'hover:border-purple-300'
                        }`}
                      >
                        <type.icon className={`w-6 h-6 mx-auto mb-2 ${
                          formData.addressType === type.id ? 'text-purple-600' : 'text-gray-400'
                        }`} />
                        <span className="text-sm font-medium">{type.label}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <Label>Full Address *</Label>
                  <Textarea 
                    value={formData.registeredAddress}
                    onChange={(e) => updateFormData('registeredAddress', e.target.value)}
                    placeholder="123 Business Street&#10;London&#10;SW1A 1AA&#10;United Kingdom"
                    rows={4}
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="use-for-mail"
                    checked={formData.useForMail}
                    onCheckedChange={(checked) => updateFormData('useForMail', checked)}
                  />
                  <Label htmlFor="use-for-mail">
                    Use this address for official mail as well
                  </Label>
                </div>
              </CardContent>
            </Card>

            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <h4 className="font-medium text-amber-800 flex items-center">
                <AlertCircle className="w-4 h-4 mr-2" />
                Important Note
              </h4>
              <p className="text-sm text-amber-700 mt-1">
                Your registered address will be publicly visible on Companies House. If you use your home address, 
                it will be searchable online. Consider using a virtual office for privacy.
              </p>
            </div>
          </div>
        );

      // STEP 6: Company Documents
      case 6:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Prepare Company Documents</h2>
              <p className="text-gray-500">The Articles of Association is your company's rulebook.</p>
            </div>

            <Card>
              <CardContent className="p-6 space-y-4">
                <Label className="mb-3 block">Articles of Association *</Label>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div
                    onClick={() => updateFormData('articlesType', 'model')}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      formData.articlesType === 'model'
                        ? 'border-purple-500 bg-purple-50 ring-2 ring-purple-200'
                        : 'hover:border-purple-300'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="font-semibold">Model Articles</h3>
                          <Badge className="bg-green-100 text-green-700">Recommended</Badge>
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                          Standard articles provided by Companies House. Suitable for most businesses.
                        </p>
                        <ul className="mt-2 text-sm text-gray-600 space-y-1">
                          <li>• Pre-approved by government</li>
                          <li>• Covers standard operations</li>
                          <li>• No additional cost</li>
                        </ul>
                      </div>
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        formData.articlesType === 'model' ? 'border-purple-600 bg-purple-600' : 'border-gray-300'
                      }`}>
                        {formData.articlesType === 'model' && <Check className="w-3 h-3 text-white" />}
                      </div>
                    </div>
                  </div>

                  <div
                    onClick={() => updateFormData('articlesType', 'custom')}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      formData.articlesType === 'custom'
                        ? 'border-purple-500 bg-purple-50 ring-2 ring-purple-200'
                        : 'hover:border-purple-300'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold">Custom Articles</h3>
                        <p className="text-sm text-gray-500 mt-1">
                          Tailored articles for specific needs. Requires legal expertise.
                        </p>
                        <ul className="mt-2 text-sm text-gray-600 space-y-1">
                          <li>• Fully customizable</li>
                          <li>• Complex share structures</li>
                          <li>• May need legal review</li>
                        </ul>
                      </div>
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        formData.articlesType === 'custom' ? 'border-purple-600 bg-purple-600' : 'border-gray-300'
                      }`}>
                        {formData.articlesType === 'custom' && <Check className="w-3 h-3 text-white" />}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Tip>
              Model Articles are recommended for beginners. They cover everything you need and can be amended later if required.
            </Tip>
          </div>
        );

      // STEP 7: Identity Verification
      case 7:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Verify Identity</h2>
              <p className="text-gray-500">Legal requirement: Each director and PSC must complete ID verification.</p>
            </div>

            <Card>
              <CardContent className="p-6 space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-800 flex items-center">
                    <Shield className="w-4 h-4 mr-2" />
                    AML & KYC Compliance
                  </h4>
                  <p className="text-sm text-blue-700 mt-1">
                    Anti-Money Laundering (AML) and Know Your Customer (KYC) checks are required by law.
                  </p>
                </div>

                <div className="space-y-3">
                  <h4 className="font-semibold">Required Documents:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 border rounded-lg text-center">
                      <FileText className="w-8 h-8 mx-auto text-purple-600 mb-2" />
                      <h5 className="font-medium text-sm">Photo ID</h5>
                      <p className="text-xs text-gray-500">Passport or driving licence</p>
                    </div>
                    <div className="p-4 border rounded-lg text-center">
                      <Home className="w-8 h-8 mx-auto text-purple-600 mb-2" />
                      <h5 className="font-medium text-sm">Proof of Address</h5>
                      <p className="text-xs text-gray-500">Utility bill or bank statement</p>
                    </div>
                    <div className="p-4 border rounded-lg text-center">
                      <User className="w-8 h-8 mx-auto text-purple-600 mb-2" />
                      <h5 className="font-medium text-sm">Liveness Check</h5>
                      <p className="text-xs text-gray-500">Selfie or video verification</p>
                    </div>
                  </div>
                </div>

                {/* Verification Status */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold">Verification Status</h4>
                      <p className="text-sm text-gray-500">
                        {formData.directors[0]?.firstName} {formData.directors[0]?.lastName}
                      </p>
                    </div>
                    <Badge className={
                      formData.idVerificationStatus === 'completed' ? 'bg-green-100 text-green-700' :
                      formData.idVerificationStatus === 'in_progress' ? 'bg-yellow-100 text-yellow-700' :
                      formData.idVerificationStatus === 'failed' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }>
                      {formData.idVerificationStatus === 'completed' ? 'Verified' :
                       formData.idVerificationStatus === 'in_progress' ? 'In Progress' :
                       formData.idVerificationStatus === 'failed' ? 'Failed' : 'Pending'}
                    </Badge>
                  </div>
                  
                  <Button 
                    className="w-full mt-4 gradient-primary border-0"
                    onClick={() => {
                      updateFormData('idVerificationStatus', 'in_progress');
                      setTimeout(() => updateFormData('idVerificationStatus', 'completed'), 2000);
                      toast.info('Starting verification process...');
                    }}
                    disabled={formData.idVerificationStatus === 'completed'}
                  >
                    {formData.idVerificationStatus === 'completed' ? (
                      <>
                        <Check className="w-4 h-4 mr-2" />
                        Verification Complete
                      </>
                    ) : formData.idVerificationStatus === 'in_progress' ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Verifying...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 mr-2" />
                        Start Verification
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Tip>
              Verification typically takes a few minutes. Make sure your documents are clear and not expired.
            </Tip>
          </div>
        );

      // STEP 8: Submit Registration
      case 8:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Review & Submit Registration</h2>
              <p className="text-gray-500">Please review all details before submitting your company registration.</p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardContent className="p-4">
                  <h4 className="font-semibold text-sm text-gray-500 mb-2">COMPANY DETAILS</h4>
                  <p className="font-semibold">{formData.companyName} Ltd</p>
                  <p className="text-sm text-gray-600">
                    {BUSINESS_TYPES.find(t => t.id === formData.businessType)?.title}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <h4 className="font-semibold text-sm text-gray-500 mb-2">SIC CODES</h4>
                  <div className="flex flex-wrap gap-1">
                    {formData.selectedSicCodes.map(code => (
                      <Badge key={code} variant="secondary">{code}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <h4 className="font-semibold text-sm text-gray-500 mb-2">DIRECTOR</h4>
                  <p className="font-semibold">
                    {formData.directors[0]?.firstName} {formData.directors[0]?.lastName}
                  </p>
                  <p className="text-sm text-gray-600">{formData.directors[0]?.occupation}</p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <h4 className="font-semibold text-sm text-gray-500 mb-2">REGISTERED ADDRESS</h4>
                  <p className="text-sm text-gray-600 whitespace-pre-line">{formData.registeredAddress}</p>
                </CardContent>
              </Card>
            </div>

            {/* Payment */}
            <Card>
              <CardContent className="p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold">Registration Fee</h4>
                    <p className="text-sm text-gray-500">Companies House filing fee</p>
                  </div>
                  <span className="text-2xl font-bold text-purple-600">£12</span>
                </div>

                <div className="border-t pt-4">
                  <Label className="mb-3 block">Payment Method</Label>
                  <Select value={formData.paymentMethod} onValueChange={(v) => updateFormData('paymentMethod', v)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select payment method" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="card">Credit/Debit Card</SelectItem>
                      <SelectItem value="paypal">PayPal</SelectItem>
                      <SelectItem value="bank">Bank Transfer</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-start space-x-2 pt-4">
                  <Checkbox 
                    id="agree-terms"
                    checked={formData.agreedToTerms}
                    onCheckedChange={(checked) => updateFormData('agreedToTerms', checked)}
                  />
                  <Label htmlFor="agree-terms" className="text-sm">
                    I confirm all information is accurate and I agree to the terms of service and Companies House regulations.
                  </Label>
                </div>
              </CardContent>
            </Card>

            {/* What happens next */}
            <Card className="bg-green-50 border-green-200">
              <CardContent className="p-4">
                <h4 className="font-semibold text-green-800 flex items-center">
                  <Sparkles className="w-4 h-4 mr-2" />
                  What happens next?
                </h4>
                <ul className="mt-2 text-sm text-green-700 space-y-1">
                  <li>• Your application will be submitted to Companies House</li>
                  <li>• Processing usually takes 24 hours</li>
                  <li>• You will receive your Certificate of Incorporation</li>
                  <li>• Your company number will be issued</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6 animate-slide-in" data-testid="business-registration-page">
      <PageHeader
        icon={FileText}
        title="Business Registration Companion"
        description="Step-by-step guidance through company formation"
      />

      {/* Progress Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="font-semibold">Step {currentStep} of {STEPS.length}</h3>
              <p className="text-sm text-gray-500">{STEPS[currentStep - 1].title}</p>
            </div>
            <span className="text-lg font-bold text-purple-600">{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
          
          {/* Step indicators */}
          <div className="flex justify-between mt-4">
            {STEPS.map((step, index) => {
              const Icon = step.icon;
              const isCompleted = index + 1 < currentStep;
              const isCurrent = index + 1 === currentStep;
              
              return (
                <div 
                  key={step.id}
                  className={`flex flex-col items-center ${index < STEPS.length - 1 ? 'flex-1' : ''}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                    isCompleted ? 'bg-green-500 text-white' :
                    isCurrent ? 'bg-purple-600 text-white' :
                    'bg-gray-200 text-gray-400'
                  }`}>
                    {isCompleted ? <Check size={16} /> : <Icon size={14} />}
                  </div>
                  <span className={`text-xs mt-1 hidden md:block ${
                    isCurrent ? 'text-purple-600 font-medium' : 'text-gray-400'
                  }`}>
                    {step.title}
                  </span>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Step Content */}
      <div className="min-h-[400px]">
        {renderStepContent()}
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between pt-4 border-t">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={currentStep === 1}
        >
          <ArrowLeft size={16} className="mr-2" />
          Previous
        </Button>
        
        {currentStep < STEPS.length ? (
          <Button
            onClick={nextStep}
            disabled={!canProceed()}
            className="gradient-primary border-0"
          >
            Next Step
            <ArrowRight size={16} className="ml-2" />
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
                Submitting...
              </>
            ) : (
              <>
                Submit Registration
                <ArrowRight size={16} className="ml-2" />
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
