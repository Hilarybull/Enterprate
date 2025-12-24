import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
import { Separator } from '@/components/ui/separator';
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
  User,
  Briefcase,
  Home,
  Building,
  Sparkles,
  Check,
  X,
  ExternalLink,
  Download,
  Printer,
  Copy,
  Info,
  BookOpen,
  Link2,
  ClipboardList,
  Globe,
  Search,
  RefreshCw,
  XCircle,
  CheckCircle2
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// Step configuration
const STEPS = [
  { id: 1, title: 'Business Type', icon: Building2, description: 'Choose your business structure' },
  { id: 2, title: 'Company Name', icon: FileText, description: 'Select a unique company name' },
  { id: 3, title: 'Business Activity', icon: Briefcase, description: 'Describe what your company does' },
  { id: 4, title: 'People Involved', icon: Users, description: 'Directors, shareholders & PSC' },
  { id: 5, title: 'Registered Address', icon: MapPin, description: 'Official company address' },
  { id: 6, title: 'Documents & Requirements', icon: FileCheck, description: 'What you will need' },
  { id: 7, title: 'Your Summary', icon: ClipboardList, description: 'Review and use for registration' }
];

// Business type options with updated fees from Companies House (as of 2024)
const BUSINESS_TYPES = [
  {
    id: 'ltd',
    title: 'Private Limited Company (Ltd)',
    description: 'Separate legal entity with limited liability. Best for credibility and growth.',
    recommended: true,
    registrationFee: '£50 (online) / £71 (paper)',
    benefits: ['Limited liability protection', 'Professional credibility', 'Tax advantages', 'Easier to raise investment']
  },
  {
    id: 'sole_trader',
    title: 'Sole Trader',
    description: 'Simplest structure. You and the business are legally the same.',
    registrationFee: 'Free (register with HMRC)',
    benefits: ['Easy to set up', 'Minimal paperwork', 'Full control', 'Simple taxes']
  },
  {
    id: 'partnership',
    title: 'Partnership / LLP',
    description: 'Business owned by two or more people with shared profits.',
    registrationFee: '£50 (online) / £71 (paper)',
    benefits: ['Shared responsibility', 'Combined expertise', 'Flexible structure']
  },
  {
    id: 'charity',
    title: 'Charity / CIC',
    description: 'Community Interest Company or charitable organization.',
    registrationFee: '£65 (online) / £86 (paper)',
    benefits: ['Tax exemptions', 'Grant eligibility', 'Community focus']
  }
];

// SIC code database (expanded)
const SIC_CODE_DATABASE = [
  { code: '62011', name: 'Ready-made interactive leisure and entertainment software development', keywords: ['gaming', 'games', 'entertainment', 'app'] },
  { code: '62012', name: 'Business and domestic software development', keywords: ['software', 'saas', 'app', 'development', 'tech'] },
  { code: '62020', name: 'Information technology consultancy activities', keywords: ['it', 'consulting', 'technology', 'advice', 'tech'] },
  { code: '62090', name: 'Other information technology service activities', keywords: ['it', 'tech', 'support', 'services'] },
  { code: '63110', name: 'Data processing, hosting and related activities', keywords: ['hosting', 'cloud', 'data', 'server'] },
  { code: '63120', name: 'Web portals', keywords: ['website', 'portal', 'online', 'platform'] },
  { code: '70229', name: 'Management consultancy activities (other than financial management)', keywords: ['consulting', 'business', 'management', 'advice'] },
  { code: '73110', name: 'Advertising agencies', keywords: ['advertising', 'marketing', 'agency', 'ads'] },
  { code: '73120', name: 'Media representation services', keywords: ['media', 'pr', 'public relations'] },
  { code: '74100', name: 'Specialised design activities', keywords: ['design', 'graphic', 'creative', 'branding'] },
  { code: '74209', name: 'Other photographic activities', keywords: ['photography', 'photo', 'video'] },
  { code: '74909', name: 'Other professional, scientific and technical activities', keywords: ['professional', 'technical', 'services'] },
  { code: '82110', name: 'Combined office administrative service activities', keywords: ['admin', 'office', 'virtual assistant'] },
  { code: '82990', name: 'Other business support service activities', keywords: ['business', 'support', 'services'] },
  { code: '47910', name: 'Retail sale via mail order houses or via Internet', keywords: ['ecommerce', 'online', 'retail', 'shop', 'store'] },
  { code: '56101', name: 'Restaurants and mobile food service activities', keywords: ['restaurant', 'food', 'catering', 'cafe'] },
  { code: '85600', name: 'Educational support activities', keywords: ['education', 'training', 'coaching', 'tutoring'] },
  { code: '96090', name: 'Other personal service activities', keywords: ['personal', 'services', 'freelance'] }
];

// Official links
const OFFICIAL_LINKS = {
  nameCheck: 'https://find-and-update.company-information.service.gov.uk/company-name-availability',
  companiesHouse: 'https://www.gov.uk/limited-company-formation',
  registerOnline: 'https://www.gov.uk/limited-company-formation/register-your-company',
  sicCodes: 'https://www.gov.uk/government/publications/standard-industrial-classification-of-economic-activities-sic',
  modelArticles: 'https://www.gov.uk/guidance/model-articles-of-association-for-limited-companies',
  pscRegister: 'https://www.gov.uk/guidance/people-with-significant-control-pscs',
  hmrcRegister: 'https://www.gov.uk/register-for-self-assessment',
  vatRegister: 'https://www.gov.uk/vat-registration',
  companiesHouseFees: 'https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees'
};

// Complete list of countries for nationality dropdown
const COUNTRIES = [
  "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria",
  "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
  "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon",
  "Canada", "Cape Verde", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica",
  "Croatia", "Cuba", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor",
  "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland",
  "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea",
  "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq",
  "Ireland", "Israel", "Italy", "Ivory Coast", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
  "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania",
  "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius",
  "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia",
  "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway",
  "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland",
  "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino",
  "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands",
  "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland",
  "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey",
  "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu",
  "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
];

// Info Box component
const InfoBox = ({ type = 'info', title, children }) => {
  const styles = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    tip: 'bg-purple-50 border-purple-200 text-purple-800'
  };
  const icons = {
    info: Info,
    warning: AlertCircle,
    success: CheckCircle,
    tip: Lightbulb
  };
  const Icon = icons[type];
  
  return (
    <div className={`flex items-start space-x-3 p-4 rounded-lg border ${styles[type]}`}>
      <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
      <div>
        {title && <h4 className="font-semibold mb-1">{title}</h4>}
        <div className="text-sm">{children}</div>
      </div>
    </div>
  );
};

// External Link Button component
const ExternalLinkButton = ({ href, children, variant = 'default' }) => (
  <a 
    href={href} 
    target="_blank" 
    rel="noopener noreferrer"
    className={`inline-flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
      variant === 'primary' 
        ? 'bg-purple-600 text-white hover:bg-purple-700' 
        : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
    }`}
  >
    <span>{children}</span>
    <ExternalLink size={14} />
  </a>
);

// Person Form component
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
            <SelectContent className="max-h-[300px]">
              {COUNTRIES.map(country => (
                <SelectItem key={country} value={country.toLowerCase().replace(/\s+/g, '_')}>
                  {country}
                </SelectItem>
              ))}
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
          placeholder="Full residential address including postcode"
          rows={2}
        />
      </div>

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
  const { currentWorkspace } = useWorkspace();
  const [currentStep, setCurrentStep] = useState(1);
  const [suggestedSicCodes, setSuggestedSicCodes] = useState([]);
  const [generatingSicCodes, setGeneratingSicCodes] = useState(false);
  const [sicCodesGenerated, setSicCodesGenerated] = useState(false);
  
  // Name availability check state
  const [checkingName, setCheckingName] = useState(false);
  const [nameCheckResult, setNameCheckResult] = useState(null);
  const [nameVerified, setNameVerified] = useState(false);
  
  // Form data state
  const [formData, setFormData] = useState({
    // Step 1: Business Type
    businessType: '',
    
    // Step 2: Company Name
    companyName: '',
    alternativeNames: ['', ''],
    
    // Step 3: Business Activity
    businessDescription: '',
    selectedSicCodes: [],
    
    // Step 4: People
    directors: [{ firstName: '', lastName: '', dob: '', nationality: '', occupation: '', address: '' }],
    shareholders: [{ firstName: '', lastName: '', dob: '', nationality: '', occupation: '', address: '', shares: '100' }],
    directorIsShareholder: true,
    
    // Step 5: Registered Address
    addressType: 'home',
    registeredAddress: '',
    
    // Step 6: Acknowledgements
    understandsNotFormationAgent: false,
    understandsOfficialRegistration: false
  });

  // Get auth headers
  const getHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      Authorization: `Bearer ${token}`,
      'X-Workspace-ID': currentWorkspace?.id || ''
    };
  };

  // Check company name availability via Companies House API
  const checkNameAvailability = async () => {
    if (!formData.companyName || formData.companyName.length < 3) {
      toast.error('Please enter at least 3 characters for the company name');
      return;
    }

    setCheckingName(true);
    setNameCheckResult(null);
    setNameVerified(false);

    try {
      const response = await axios.post(
        `${API_URL}/company-profile/check-name`,
        { companyName: formData.companyName },
        { headers: getHeaders() }
      );

      setNameCheckResult(response.data);
      
      if (response.data.isAvailable) {
        setNameVerified(true);
        toast.success('Name appears to be available!');
      } else {
        toast.warning('This name may already be taken. See suggestions below.');
      }
    } catch (error) {
      console.error('Name check error:', error);
      toast.error('Failed to check name availability. Please try again.');
    } finally {
      setCheckingName(false);
    }
  };

  // Select a suggested name
  const selectSuggestedName = (name) => {
    updateFormData('companyName', name);
    setNameCheckResult(null);
    setNameVerified(false);
    toast.info(`Selected: ${name}. Click "Check Availability" to verify.`);
  };

  // Reset name check when name changes
  const handleNameChange = (newName) => {
    updateFormData('companyName', newName);
    if (nameVerified) {
      setNameVerified(false);
      setNameCheckResult(null);
    }
  };

  // Calculate progress
  const progress = Math.round((currentStep / STEPS.length) * 100);

  // Update form data helper
  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // Generate SIC codes based on business description
  const generateSicCodes = () => {
    if (formData.businessDescription.length < 20) {
      toast.error('Please enter at least 20 characters describing your business');
      return;
    }

    setGeneratingSicCodes(true);
    setSuggestedSicCodes([]);
    updateFormData('selectedSicCodes', []);

    // Simulate AI analysis (in production, this would call an API)
    setTimeout(() => {
      const description = formData.businessDescription.toLowerCase();
      
      // Score each SIC code based on keyword matches
      const scoredCodes = SIC_CODE_DATABASE.map(sic => {
        let score = 0;
        sic.keywords.forEach(keyword => {
          if (description.includes(keyword)) {
            score += 1;
          }
        });
        // Also check if code name words appear in description
        sic.name.toLowerCase().split(' ').forEach(word => {
          if (word.length > 3 && description.includes(word)) {
            score += 0.5;
          }
        });
        return { ...sic, score };
      });

      // Sort by score and get top 6
      const topCodes = scoredCodes
        .sort((a, b) => b.score - a.score)
        .slice(0, 6);

      // If not enough matches, pad with generic business codes
      if (topCodes.filter(c => c.score > 0).length < 6) {
        const genericCodes = SIC_CODE_DATABASE.filter(
          sic => !topCodes.some(t => t.code === sic.code)
        ).slice(0, 6 - topCodes.length);
        topCodes.push(...genericCodes.map(c => ({ ...c, score: 0 })));
      }

      setSuggestedSicCodes(topCodes.slice(0, 6));
      setSicCodesGenerated(true);
      setGeneratingSicCodes(false);
      toast.success('6 SIC codes generated! Please select exactly 4.');
    }, 1500);
  };

  // Toggle SIC code (must select exactly 4)
  const toggleSicCode = (code) => {
    const selected = formData.selectedSicCodes;
    if (selected.includes(code)) {
      // Allow deselection
      updateFormData('selectedSicCodes', selected.filter(c => c !== code));
    } else if (selected.length < 4) {
      // Allow selection if less than 4 selected
      updateFormData('selectedSicCodes', [...selected, code]);
      if (selected.length === 3) {
        toast.success('4 SIC codes selected! You can now proceed to the next step.');
      }
    } else {
      // Already have 4 selected
      toast.error('You must select exactly 4 SIC codes. Deselect one to choose a different code.');
    }
  };

  // Director/Shareholder management
  const addDirector = () => {
    setFormData(prev => ({
      ...prev,
      directors: [...prev.directors, { firstName: '', lastName: '', dob: '', nationality: '', occupation: '', address: '' }]
    }));
  };

  const updateDirector = (index, data) => {
    const updated = [...formData.directors];
    updated[index] = data;
    updateFormData('directors', updated);
  };

  const removeDirector = (index) => {
    const updated = formData.directors.filter((_, i) => i !== index);
    updateFormData('directors', updated);
  };

  const addShareholder = () => {
    setFormData(prev => ({
      ...prev,
      shareholders: [...prev.shareholders, { firstName: '', lastName: '', dob: '', nationality: '', occupation: '', address: '', shares: '' }]
    }));
  };

  const updateShareholder = (index, data) => {
    const updated = [...formData.shareholders];
    updated[index] = data;
    updateFormData('shareholders', updated);
  };

  const removeShareholder = (index) => {
    const updated = formData.shareholders.filter((_, i) => i !== index);
    updateFormData('shareholders', updated);
  };

  // Validate current step
  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return !!formData.businessType;
      case 2:
        // Must have company name and it must be verified as available
        return formData.companyName.length >= 3 && nameVerified;
      case 3:
        // Must have description, generated SIC codes, and selected exactly 4
        return formData.businessDescription.length >= 20 && 
               sicCodesGenerated && 
               formData.selectedSicCodes.length === 4;
      case 4:
        return formData.directors.every(d => d.firstName && d.lastName);
      case 5:
        return !!formData.registeredAddress;
      case 6:
        return formData.understandsNotFormationAgent && formData.understandsOfficialRegistration;
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

  // Copy summary to clipboard
  const copySummary = () => {
    const summary = generateTextSummary();
    navigator.clipboard.writeText(summary);
    toast.success('Summary copied to clipboard!');
  };

  // Generate text summary
  const generateTextSummary = () => {
    const businessType = BUSINESS_TYPES.find(t => t.id === formData.businessType);
    const sicCodes = formData.selectedSicCodes.map(code => {
      const sic = SIC_CODE_DATABASE.find(s => s.code === code);
      return sic ? `${sic.code} - ${sic.name}` : code;
    });

    return `
BUSINESS REGISTRATION SUMMARY
Generated by Enterprate AI
================================

COMPANY DETAILS
---------------
Company Name: ${formData.companyName} ${formData.businessType === 'ltd' ? 'Ltd' : ''}
Business Type: ${businessType?.title || 'Not specified'}
Registration Fee: ${businessType?.registrationFee || 'Varies'}

BUSINESS ACTIVITIES
-------------------
Description: ${formData.businessDescription}

SIC Codes:
${sicCodes.map(c => `  • ${c}`).join('\n')}

DIRECTORS
---------
${formData.directors.map((d, i) => `
Director ${i + 1}:
  Name: ${d.firstName} ${d.lastName}
  DOB: ${d.dob}
  Nationality: ${d.nationality}
  Occupation: ${d.occupation}
  Address: ${d.address}
`).join('')}

${!formData.directorIsShareholder ? `
SHAREHOLDERS
------------
${formData.shareholders.map((s, i) => `
Shareholder ${i + 1}:
  Name: ${s.firstName} ${s.lastName}
  Shares: ${s.shares}
`).join('')}` : 'Director is also the sole shareholder (100% ownership)'}

REGISTERED OFFICE ADDRESS
-------------------------
Type: ${formData.addressType === 'home' ? 'Home Address' : formData.addressType === 'office' ? 'Office Address' : 'Virtual Office'}
Address: ${formData.registeredAddress}

IMPORTANT LINKS
---------------
• Check Name Availability: ${OFFICIAL_LINKS.nameCheck}
• Register Company Online: ${OFFICIAL_LINKS.registerOnline}
• SIC Codes Reference: ${OFFICIAL_LINKS.sicCodes}
• Model Articles: ${OFFICIAL_LINKS.modelArticles}

NEXT STEPS
----------
1. Check your company name availability using the link above
2. Prepare your ID documents (passport/driving licence)
3. Have proof of address ready
4. Register online at Companies House
5. Pay the registration fee (£12 online)
6. Receive Certificate of Incorporation (usually within 24 hours)

This summary was generated to help you prepare for registration.
You must complete the actual registration at Companies House.
`.trim();
  };

  // Print summary
  const printSummary = () => {
    window.print();
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
              <p className="text-gray-500">Choose the structure that best fits your needs. This will determine where and how you register.</p>
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
                        <div className="flex items-center space-x-2 flex-wrap gap-1">
                          <h3 className="font-semibold">{type.title}</h3>
                          {type.recommended && (
                            <Badge className="bg-purple-100 text-purple-700">Recommended</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 mt-1">{type.description}</p>
                        <p className="text-xs text-purple-600 mt-2 font-medium">Fee: {type.registrationFee}</p>
                        <div className="mt-3 space-y-1">
                          {type.benefits.map((b, i) => (
                            <div key={i} className="flex items-center text-xs text-gray-600">
                              <Check className="w-3 h-3 text-green-500 mr-1 flex-shrink-0" />
                              {b}
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ml-2 ${
                        formData.businessType === type.id ? 'border-purple-600 bg-purple-600' : 'border-gray-300'
                      }`}>
                        {formData.businessType === type.id && <Check className="w-3 h-3 text-white" />}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <InfoBox type="tip" title="Recommendation for beginners">
              If you want credibility, liability protection, and room to grow → <strong>Private Limited Company (Ltd)</strong> is the best choice. 
              It separates your personal assets from the business.
            </InfoBox>
          </div>
        );

      // STEP 2: Company Name
      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Choose Your Company Name</h2>
              <p className="text-gray-500">Your company name must be unique and follow Companies House naming rules.</p>
            </div>

            <Card>
              <CardContent className="p-6 space-y-4">
                <div>
                  <Label>Preferred Company Name *</Label>
                  <div className="flex space-x-2">
                    <Input 
                      value={formData.companyName}
                      onChange={(e) => updateFormData('companyName', e.target.value)}
                      placeholder="e.g., Acme Consulting"
                      className="flex-1"
                    />
                    {formData.businessType === 'ltd' && (
                      <span className="flex items-center text-gray-500 bg-gray-100 px-3 rounded-md">Ltd</span>
                    )}
                  </div>
                </div>

                <div>
                  <Label>Alternative Names (in case your first choice is taken)</Label>
                  <div className="space-y-2 mt-2">
                    <Input 
                      value={formData.alternativeNames[0]}
                      onChange={(e) => {
                        const alts = [...formData.alternativeNames];
                        alts[0] = e.target.value;
                        updateFormData('alternativeNames', alts);
                      }}
                      placeholder="Alternative name 1"
                    />
                    <Input 
                      value={formData.alternativeNames[1]}
                      onChange={(e) => {
                        const alts = [...formData.alternativeNames];
                        alts[1] = e.target.value;
                        updateFormData('alternativeNames', alts);
                      }}
                      placeholder="Alternative name 2"
                    />
                  </div>
                </div>

                {/* Check Name Availability Link */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h4 className="font-semibold text-purple-800 flex items-center mb-2">
                    <Globe className="w-4 h-4 mr-2" />
                    Check Name Availability
                  </h4>
                  <p className="text-sm text-purple-700 mb-3">
                    Use the official Companies House service to check if your chosen name is available.
                  </p>
                  <ExternalLinkButton href={OFFICIAL_LINKS.nameCheck} variant="primary">
                    Check Name on Companies House
                  </ExternalLinkButton>
                </div>
              </CardContent>
            </Card>

            <InfoBox type="warning" title="Naming Rules">
              <ul className="space-y-1 mt-1">
                <li>• Must be <strong>unique</strong> (not too similar to existing companies)</li>
                <li>• Cannot include restricted words (e.g., "Bank", "Royal") without permission</li>
                <li>• Must end with "Limited" or "Ltd" for private limited companies</li>
                <li>• Cannot be offensive or misleading</li>
              </ul>
            </InfoBox>
          </div>
        );

      // STEP 3: Business Activity
      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Describe Your Business Activities</h2>
              <p className="text-gray-500">Tell us what your company will do. We will generate appropriate SIC codes based on your description.</p>
            </div>

            <Card>
              <CardContent className="p-6 space-y-4">
                <div>
                  <Label>Business Description *</Label>
                  <Textarea 
                    value={formData.businessDescription}
                    onChange={(e) => {
                      updateFormData('businessDescription', e.target.value);
                      // Reset SIC codes if description changes significantly
                      if (sicCodesGenerated && e.target.value.length < 20) {
                        setSuggestedSicCodes([]);
                        setSicCodesGenerated(false);
                        updateFormData('selectedSicCodes', []);
                      }
                    }}
                    placeholder="e.g., I provide IT consulting services to small businesses. I may also develop and sell software products online in the future."
                    rows={4}
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    {formData.businessDescription.length}/500 characters (minimum 20)
                  </p>
                </div>

                {/* Generate SIC Codes Button */}
                {!sicCodesGenerated && (
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <h4 className="font-semibold text-purple-800 flex items-center mb-2">
                      <Sparkles className="w-4 h-4 mr-2" />
                      Generate SIC Codes
                    </h4>
                    <p className="text-sm text-purple-700 mb-3">
                      Based on your business description, we will identify 6 relevant SIC codes from the official GOV.UK database. 
                      You must then select exactly 4 codes.
                    </p>
                    <Button 
                      onClick={generateSicCodes}
                      disabled={formData.businessDescription.length < 20 || generatingSicCodes}
                      className="gradient-primary border-0"
                    >
                      {generatingSicCodes ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Analyzing your business...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4 mr-2" />
                          Generate SIC Codes
                        </>
                      )}
                    </Button>
                    {formData.businessDescription.length < 20 && (
                      <p className="text-xs text-purple-600 mt-2">
                        Enter at least 20 characters to enable SIC code generation
                      </p>
                    )}
                  </div>
                )}

                {/* Generated SIC Codes - Select 4 out of 6 */}
                {sicCodesGenerated && suggestedSicCodes.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <Sparkles className="w-4 h-4 text-purple-600" />
                        <Label>Generated SIC Codes</Label>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setSicCodesGenerated(false);
                          setSuggestedSicCodes([]);
                          updateFormData('selectedSicCodes', []);
                        }}
                      >
                        Regenerate
                      </Button>
                    </div>
                    
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4">
                      <p className="text-sm text-amber-800 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                        <span>
                          <strong>Select exactly 4 codes</strong> from the 6 options below to proceed.
                        </span>
                      </p>
                    </div>

                    <div className="grid grid-cols-1 gap-2">
                      {suggestedSicCodes.map(sic => (
                        <div 
                          key={sic.code}
                          onClick={() => toggleSicCode(sic.code)}
                          className={`p-3 border rounded-lg cursor-pointer transition-all ${
                            formData.selectedSicCodes.includes(sic.code)
                              ? 'border-purple-500 bg-purple-50 ring-2 ring-purple-200'
                              : 'hover:border-purple-300 bg-white'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <span className="font-mono text-sm text-purple-600 font-semibold">{sic.code}</span>
                              <p className="text-sm text-gray-700">{sic.name}</p>
                            </div>
                            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 ml-2 ${
                              formData.selectedSicCodes.includes(sic.code) 
                                ? 'border-purple-600 bg-purple-600' 
                                : 'border-gray-300'
                            }`}>
                              {formData.selectedSicCodes.includes(sic.code) && (
                                <Check className="w-4 h-4 text-white" />
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="mt-4 flex items-center justify-between">
                      <p className={`text-sm font-medium ${
                        formData.selectedSicCodes.length === 4 
                          ? 'text-green-600' 
                          : 'text-gray-500'
                      }`}>
                        Selected: {formData.selectedSicCodes.length}/4 codes
                        {formData.selectedSicCodes.length === 4 && (
                          <CheckCircle className="w-4 h-4 inline ml-1" />
                        )}
                      </p>
                      {formData.selectedSicCodes.length !== 4 && (
                        <p className="text-xs text-gray-400">
                          {4 - formData.selectedSicCodes.length} more to select
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <InfoBox type="info" title="What are SIC codes?">
              SIC (Standard Industrial Classification) codes are 5-digit codes that describe your business activities. 
              Companies House uses these to categorize businesses. You must select exactly 4 SIC codes for your registration.
            </InfoBox>
          </div>
        );

      // STEP 4: People Involved
      case 4:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Who Is Involved in the Company?</h2>
              <p className="text-gray-500">Provide details of directors and shareholders. You will need this information when registering.</p>
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
            <InfoBox type="info" title="People with Significant Control (PSC)">
              Anyone who owns more than 25% of shares or has significant influence must be registered as a PSC. 
              For single-founder companies, the founder is automatically the PSC.
              <a 
                href={OFFICIAL_LINKS.pscRegister}
                target="_blank"
                rel="noopener noreferrer"
                className="text-purple-600 hover:underline ml-1 inline-flex items-center"
              >
                Learn more <ExternalLink size={12} className="ml-1" />
              </a>
            </InfoBox>

            <InfoBox type="tip">
              Most single-founder companies have <strong>1 director</strong> who is also the <strong>sole shareholder</strong> and <strong>PSC</strong>. 
              We recommend <strong>100 ordinary shares</strong> at £1 each.
            </InfoBox>
          </div>
        );

      // STEP 5: Registered Address
      case 5:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Registered Office Address</h2>
              <p className="text-gray-500">This will be your company&apos;s official address. It must be a UK physical address and will be public.</p>
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
              </CardContent>
            </Card>

            <InfoBox type="warning" title="Privacy Notice">
              Your registered address will be <strong>publicly visible</strong> on Companies House and searchable online. 
              If you use your home address, consider using a virtual office service for privacy.
            </InfoBox>
          </div>
        );

      // STEP 6: Documents & Requirements
      case 6:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">What You Will Need to Register</h2>
              <p className="text-gray-500">Here is everything you will need to complete your registration on Companies House.</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <FileCheck className="w-5 h-5 mr-2 text-purple-600" />
                  Required Documents
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { item: 'Photo ID for each director', desc: 'Passport or driving licence' },
                  { item: 'Proof of address for each director', desc: 'Utility bill or bank statement (dated within 3 months)' },
                  { item: 'Your chosen company name', desc: 'Verified as available on Companies House' },
                  { item: 'Registered office address', desc: 'Must be a UK physical address' },
                  { item: 'SIC code(s)', desc: 'Up to 4 codes describing your business activities' },
                  { item: 'Director/shareholder details', desc: 'Full names, DOB, nationality, occupation, addresses' },
                  { item: 'Share structure', desc: 'Number and type of shares (e.g., 100 ordinary shares at £1 each)' }
                ].map((doc, i) => (
                  <div key={i} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-sm">{doc.item}</p>
                      <p className="text-xs text-gray-500">{doc.desc}</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <Scale className="w-5 h-5 mr-2 text-purple-600" />
                  Articles of Association
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-3">
                  This is your company&apos;s rulebook. For most new companies, the standard <strong>Model Articles</strong> are recommended.
                </p>
                <a 
                  href={OFFICIAL_LINKS.modelArticles}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-purple-600 hover:underline inline-flex items-center text-sm"
                >
                  View Model Articles on GOV.UK <ExternalLink size={12} className="ml-1" />
                </a>
              </CardContent>
            </Card>

            {/* Important Acknowledgement */}
            <Card className="border-amber-200 bg-amber-50">
              <CardContent className="p-6 space-y-4">
                <h4 className="font-semibold text-amber-800 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  Important: Please Read and Acknowledge
                </h4>
                
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <Checkbox 
                      id="not-formation-agent"
                      checked={formData.understandsNotFormationAgent}
                      onCheckedChange={(checked) => updateFormData('understandsNotFormationAgent', checked)}
                    />
                    <Label htmlFor="not-formation-agent" className="text-sm text-amber-800">
                      I understand that Enterprate AI is <strong>NOT a formation agent</strong> and does not register companies. 
                      This tool helps me prepare the information I need to register myself.
                    </Label>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <Checkbox 
                      id="official-registration"
                      checked={formData.understandsOfficialRegistration}
                      onCheckedChange={(checked) => updateFormData('understandsOfficialRegistration', checked)}
                    />
                    <Label htmlFor="official-registration" className="text-sm text-amber-800">
                      I understand that I must complete the <strong>actual registration</strong> on the official Companies House website.
                    </Label>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      // STEP 7: Summary
      case 7:
        const businessType = BUSINESS_TYPES.find(t => t.id === formData.businessType);
        
        return (
          <div className="space-y-6 print:space-y-4" id="registration-summary">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold mb-2">Your Registration Summary</h2>
                <p className="text-gray-500">Use this summary to complete your registration on Companies House.</p>
              </div>
              <div className="flex space-x-2 print:hidden">
                <Button variant="outline" size="sm" onClick={copySummary}>
                  <Copy size={14} className="mr-1" /> Copy
                </Button>
                <Button variant="outline" size="sm" onClick={printSummary}>
                  <Printer size={14} className="mr-1" /> Print
                </Button>
              </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardContent className="p-4">
                  <h4 className="font-semibold text-sm text-gray-500 mb-2">COMPANY NAME</h4>
                  <p className="font-semibold text-lg">
                    {formData.companyName} {formData.businessType === 'ltd' ? 'Ltd' : ''}
                  </p>
                  {formData.alternativeNames.filter(n => n).length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs text-gray-500">Alternative names:</p>
                      {formData.alternativeNames.filter(n => n).map((n, i) => (
                        <p key={i} className="text-sm text-gray-600">• {n}</p>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <h4 className="font-semibold text-sm text-gray-500 mb-2">BUSINESS TYPE</h4>
                  <p className="font-semibold">{businessType?.title}</p>
                  <p className="text-sm text-purple-600">Fee: {businessType?.registrationFee}</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardContent className="p-4">
                <h4 className="font-semibold text-sm text-gray-500 mb-2">SIC CODES</h4>
                <div className="space-y-2">
                  {formData.selectedSicCodes.map(code => {
                    const sic = SIC_CODE_DATABASE.find(s => s.code === code);
                    return (
                      <div key={code} className="flex items-center">
                        <Badge variant="outline" className="mr-2 font-mono">{code}</Badge>
                        <span className="text-sm">{sic?.name || 'Unknown'}</span>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <h4 className="font-semibold text-sm text-gray-500 mb-2">BUSINESS DESCRIPTION</h4>
                <p className="text-sm text-gray-700">{formData.businessDescription}</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <h4 className="font-semibold text-sm text-gray-500 mb-2">DIRECTORS</h4>
                {formData.directors.map((d, i) => (
                  <div key={i} className="mb-3 last:mb-0">
                    <p className="font-semibold">{d.firstName} {d.lastName}</p>
                    <p className="text-sm text-gray-600">DOB: {d.dob} | Nationality: {d.nationality}</p>
                    <p className="text-sm text-gray-600">Occupation: {d.occupation}</p>
                    <p className="text-sm text-gray-600">Address: {d.address}</p>
                  </div>
                ))}
                {formData.directorIsShareholder && (
                  <p className="text-sm text-purple-600 mt-2">
                    ✓ Director is also the sole shareholder (100 ordinary shares)
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <h4 className="font-semibold text-sm text-gray-500 mb-2">REGISTERED ADDRESS</h4>
                <Badge variant="outline" className="mb-2">
                  {formData.addressType === 'home' ? 'Home Address' : 
                   formData.addressType === 'office' ? 'Office Address' : 'Virtual Office'}
                </Badge>
                <p className="text-sm text-gray-700 whitespace-pre-line">{formData.registeredAddress}</p>
              </CardContent>
            </Card>

            {/* Action Links */}
            <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
              <CardContent className="p-6">
                <h4 className="font-semibold text-lg mb-4 flex items-center">
                  <Link2 className="w-5 h-5 mr-2 text-purple-600" />
                  Next Steps - Complete Your Registration
                </h4>
                
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 rounded-full bg-purple-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">1</div>
                    <div>
                      <p className="font-medium">Check Name Availability</p>
                      <p className="text-sm text-gray-600 mb-2">Verify your chosen company name is available.</p>
                      <ExternalLinkButton href={OFFICIAL_LINKS.nameCheck}>
                        Check Name on Companies House
                      </ExternalLinkButton>
                    </div>
                  </div>

                  <Separator />

                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 rounded-full bg-purple-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">2</div>
                    <div>
                      <p className="font-medium">Register Your Company</p>
                      <p className="text-sm text-gray-600 mb-2">Use this summary to complete registration (approx. 24 hours for approval).</p>
                      <ExternalLinkButton href={OFFICIAL_LINKS.registerOnline} variant="primary">
                        Register on GOV.UK
                      </ExternalLinkButton>
                    </div>
                  </div>

                  <Separator />

                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 rounded-full bg-purple-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">3</div>
                    <div>
                      <p className="font-medium">After Registration</p>
                      <p className="text-sm text-gray-600">
                        Once registered, you will receive your Certificate of Incorporation and Company Number. 
                        Then register for taxes with HMRC.
                      </p>
                      <div className="flex space-x-2 mt-2">
                        <ExternalLinkButton href={OFFICIAL_LINKS.hmrcRegister}>
                          Register with HMRC
                        </ExternalLinkButton>
                        <ExternalLinkButton href={OFFICIAL_LINKS.vatRegister}>
                          VAT Registration
                        </ExternalLinkButton>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <InfoBox type="success" title="You are ready!">
              You have all the information you need to register your company. 
              Use the links above to complete the official registration process on Companies House. Good luck! 🎉
            </InfoBox>
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
        description="Prepare everything you need to register your company on Companies House"
      />

      {/* Important Notice Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start space-x-3">
        <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-sm text-blue-800">
            <strong>This is a preparation guide, not a formation agent.</strong> We help you gather all the information 
            you need to register your company yourself on the official Companies House website.
          </p>
        </div>
      </div>

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
                  <span className={`text-xs mt-1 hidden md:block text-center ${
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
      <div className="flex justify-between pt-4 border-t print:hidden">
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
            onClick={copySummary}
            className="gradient-primary border-0"
          >
            <Copy size={16} className="mr-2" />
            Copy Summary
          </Button>
        )}
      </div>
    </div>
  );
}
