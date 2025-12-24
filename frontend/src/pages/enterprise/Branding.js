import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Palette, 
  Image, 
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Download,
  Loader2,
  Check,
  RefreshCw,
  Edit3,
  Shapes,
  Building2
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// Branding Wizard Steps
const WIZARD_STEPS = [
  { id: 1, title: 'Company Details', description: 'Confirm your company information' },
  { id: 2, title: 'Brand Style', description: 'Choose your brand personality' },
  { id: 3, title: 'Logo Generation', description: 'AI generates logo options' },
  { id: 4, title: 'Brand Kit', description: 'Your complete brand package' }
];

// Brand style options
const BRAND_STYLES = [
  { id: 'modern', name: 'Modern & Minimal', description: 'Clean, simple, contemporary', colors: ['#6366f1', '#f1f5f9', '#0f172a'] },
  { id: 'professional', name: 'Professional & Corporate', description: 'Traditional, trustworthy, established', colors: ['#1e40af', '#f8fafc', '#1e293b'] },
  { id: 'playful', name: 'Playful & Creative', description: 'Fun, energetic, innovative', colors: ['#ec4899', '#fef3c7', '#7c3aed'] },
  { id: 'luxury', name: 'Luxury & Premium', description: 'Elegant, sophisticated, exclusive', colors: ['#ca8a04', '#1c1917', '#fafaf9'] },
  { id: 'eco', name: 'Natural & Eco', description: 'Sustainable, organic, earthy', colors: ['#16a34a', '#fefce8', '#365314'] },
  { id: 'tech', name: 'Tech & Digital', description: 'Innovative, cutting-edge, futuristic', colors: ['#06b6d4', '#0f172a', '#22d3ee'] }
];

// Font pairings
const FONT_PAIRINGS = [
  { id: 'classic', heading: 'Playfair Display', body: 'Inter', style: 'Elegant & Readable' },
  { id: 'modern', heading: 'Poppins', body: 'Open Sans', style: 'Modern & Clean' },
  { id: 'bold', heading: 'Montserrat', body: 'Lato', style: 'Bold & Professional' },
  { id: 'minimal', heading: 'DM Sans', body: 'Source Sans Pro', style: 'Minimal & Contemporary' }
];

export default function Branding() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [wizardStep, setWizardStep] = useState(0); // 0 = overview, 1-4 = wizard steps
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [companyProfile, setCompanyProfile] = useState(null);
  const [brandAssets, setBrandAssets] = useState(null);
  
  // Wizard state
  const [brandConfig, setBrandConfig] = useState({
    companyName: '',
    tagline: '',
    industry: '',
    brandStyle: '',
    fontPairing: '',
    primaryColor: '#6366f1',
    secondaryColor: '#f1f5f9',
    accentColor: '#0f172a'
  });
  
  const [generatedLogos, setGeneratedLogos] = useState([]);
  const [selectedLogo, setSelectedLogo] = useState(null);

  useEffect(() => {
    if (currentWorkspace) {
      loadCompanyProfile();
      loadBrandAssets();
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
        // Pre-fill brand config with company details
        setBrandConfig(prev => ({
          ...prev,
          companyName: response.data.legalName || response.data.proposedName || '',
          industry: response.data.officialProfile?.companyType || '',
          tagline: response.data.derivedProfile?.tagline || ''
        }));
      }
    } catch (error) {
      console.error('Failed to load company profile:', error);
    }
  };

  const loadBrandAssets = async () => {
    try {
      // Check if brand assets exist in company profile
      const response = await axios.get(`${API_URL}/company-profile`, {
        headers: getHeaders()
      });
      if (response.data?.derivedProfile?.brandAssets) {
        setBrandAssets(response.data.derivedProfile.brandAssets);
      }
    } catch (error) {
      console.error('Failed to load brand assets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectStyle = (styleId) => {
    const style = BRAND_STYLES.find(s => s.id === styleId);
    if (style) {
      setBrandConfig(prev => ({
        ...prev,
        brandStyle: styleId,
        primaryColor: style.colors[0],
        secondaryColor: style.colors[1],
        accentColor: style.colors[2]
      }));
    }
  };

  const generateLogos = async () => {
    setGenerating(true);
    try {
      const response = await axios.post(
        `${API_URL}/company-profile/generate-branding`,
        {
          companyName: brandConfig.companyName,
          tagline: brandConfig.tagline,
          industry: brandConfig.industry,
          brandStyle: brandConfig.brandStyle,
          primaryColor: brandConfig.primaryColor,
          secondaryColor: brandConfig.secondaryColor,
          accentColor: brandConfig.accentColor
        },
        { headers: getHeaders() }
      );
      
      if (response.data?.logos) {
        setGeneratedLogos(response.data.logos);
        toast.success('Logos generated successfully!');
      } else {
        // Generate placeholder logos if API doesn&apos;t return them
        setGeneratedLogos([
          { id: 1, type: 'icon', description: 'Modern icon-based logo with initials' },
          { id: 2, type: 'wordmark', description: 'Clean wordmark with custom typography' },
          { id: 3, type: 'combination', description: 'Icon + wordmark combination' }
        ]);
        toast.success('Logo concepts generated!');
      }
    } catch (error) {
      console.error('Failed to generate logos:', error);
      // Generate fallback placeholders
      setGeneratedLogos([
        { id: 1, type: 'icon', description: 'Modern icon-based logo with initials' },
        { id: 2, type: 'wordmark', description: 'Clean wordmark with custom typography' },
        { id: 3, type: 'combination', description: 'Icon + wordmark combination' }
      ]);
      toast.info('Logo concepts ready for review');
    } finally {
      setGenerating(false);
    }
  };

  const saveBrandKit = async () => {
    setGenerating(true);
    try {
      await axios.patch(
        `${API_URL}/company-profile`,
        {
          derivedProfile: {
            brandStyle: brandConfig.brandStyle,
            brandColors: [brandConfig.primaryColor, brandConfig.secondaryColor, brandConfig.accentColor],
            fontPairings: [FONT_PAIRINGS.find(f => f.id === brandConfig.fontPairing)],
            tagline: brandConfig.tagline,
            selectedLogo: selectedLogo,
            brandAssets: {
              logos: generatedLogos,
              selectedLogoId: selectedLogo,
              colors: {
                primary: brandConfig.primaryColor,
                secondary: brandConfig.secondaryColor,
                accent: brandConfig.accentColor
              },
              fonts: FONT_PAIRINGS.find(f => f.id === brandConfig.fontPairing),
              generatedAt: new Date().toISOString()
            }
          }
        },
        { headers: getHeaders() }
      );
      toast.success('Brand kit saved successfully!');
      setBrandAssets({
        logos: generatedLogos,
        selectedLogoId: selectedLogo,
        colors: {
          primary: brandConfig.primaryColor,
          secondary: brandConfig.secondaryColor,
          accent: brandConfig.accentColor
        },
        fonts: FONT_PAIRINGS.find(f => f.id === brandConfig.fontPairing)
      });
      setWizardStep(0);
    } catch (error) {
      console.error('Failed to save brand kit:', error);
      toast.error('Failed to save brand kit');
    } finally {
      setGenerating(false);
    }
  };

  const progress = (wizardStep / 4) * 100;

  const renderWizardContent = () => {
    switch (wizardStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <Building2 className="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold">Confirm Your Company Details</h3>
              <p className="text-gray-500">These details will be used to generate your brand identity</p>
            </div>
            
            {companyProfile?.isRegistrationConfirmed && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <div className="flex items-center">
                  <Check className="w-5 h-5 text-green-600 mr-2" />
                  <span className="text-green-800 font-medium">Company verified with Companies House</span>
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Company Name</Label>
                <Input 
                  value={brandConfig.companyName}
                  onChange={(e) => setBrandConfig({...brandConfig, companyName: e.target.value})}
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Industry/Sector</Label>
                <Input 
                  value={brandConfig.industry}
                  onChange={(e) => setBrandConfig({...brandConfig, industry: e.target.value})}
                  placeholder="e.g., Technology, Consulting"
                  className="mt-1"
                />
              </div>
            </div>
            
            <div>
              <Label>Tagline/Slogan (optional)</Label>
              <Input 
                value={brandConfig.tagline}
                onChange={(e) => setBrandConfig({...brandConfig, tagline: e.target.value})}
                placeholder="e.g., Innovation meets excellence"
                className="mt-1"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <Palette className="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold">Choose Your Brand Style</h3>
              <p className="text-gray-500">Select a style that represents your brand personality</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {BRAND_STYLES.map((style) => (
                <Card 
                  key={style.id}
                  className={`cursor-pointer transition-all ${
                    brandConfig.brandStyle === style.id 
                      ? 'ring-2 ring-purple-500 border-purple-500' 
                      : 'hover:border-purple-300'
                  }`}
                  onClick={() => handleSelectStyle(style.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex space-x-1 mb-3">
                      {style.colors.map((color, i) => (
                        <div 
                          key={i}
                          className="w-8 h-8 rounded-full border border-gray-200"
                          style={{ backgroundColor: color }}
                        />
                      ))}
                    </div>
                    <h4 className="font-semibold">{style.name}</h4>
                    <p className="text-sm text-gray-500">{style.description}</p>
                    {brandConfig.brandStyle === style.id && (
                      <Badge className="mt-2 bg-purple-100 text-purple-700">Selected</Badge>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
            
            <div className="mt-6">
              <Label className="mb-2 block">Font Pairing</Label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {FONT_PAIRINGS.map((font) => (
                  <Card 
                    key={font.id}
                    className={`cursor-pointer transition-all ${
                      brandConfig.fontPairing === font.id 
                        ? 'ring-2 ring-purple-500 border-purple-500' 
                        : 'hover:border-purple-300'
                    }`}
                    onClick={() => setBrandConfig({...brandConfig, fontPairing: font.id})}
                  >
                    <CardContent className="p-3 text-center">
                      <p className="font-semibold text-sm" style={{ fontFamily: font.heading }}>{font.heading}</p>
                      <p className="text-xs text-gray-500" style={{ fontFamily: font.body }}>{font.body}</p>
                      <p className="text-xs text-purple-600 mt-1">{font.style}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
            
            <div className="mt-6">
              <Label className="mb-2 block">Customize Colors</Label>
              <div className="flex space-x-4">
                <div>
                  <Label className="text-xs">Primary</Label>
                  <input 
                    type="color" 
                    value={brandConfig.primaryColor}
                    onChange={(e) => setBrandConfig({...brandConfig, primaryColor: e.target.value})}
                    className="w-12 h-12 rounded cursor-pointer"
                  />
                </div>
                <div>
                  <Label className="text-xs">Secondary</Label>
                  <input 
                    type="color" 
                    value={brandConfig.secondaryColor}
                    onChange={(e) => setBrandConfig({...brandConfig, secondaryColor: e.target.value})}
                    className="w-12 h-12 rounded cursor-pointer"
                  />
                </div>
                <div>
                  <Label className="text-xs">Accent</Label>
                  <input 
                    type="color" 
                    value={brandConfig.accentColor}
                    onChange={(e) => setBrandConfig({...brandConfig, accentColor: e.target.value})}
                    className="w-12 h-12 rounded cursor-pointer"
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <Sparkles className="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold">AI Logo Generation</h3>
              <p className="text-gray-500">Select your preferred logo concept</p>
            </div>
            
            {generatedLogos.length === 0 ? (
              <div className="text-center py-12">
                <Button 
                  onClick={generateLogos}
                  disabled={generating}
                  className="gradient-primary border-0"
                  size="lg"
                >
                  {generating ? (
                    <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Generating Logos...</>
                  ) : (
                    <><Sparkles className="mr-2" size={20} /> Generate 3 Logo Options</>
                  )}
                </Button>
                <p className="text-sm text-gray-500 mt-4">
                  AI will create 3 unique logo concepts based on your brand style
                </p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {generatedLogos.map((logo) => (
                    <Card 
                      key={logo.id}
                      className={`cursor-pointer transition-all ${
                        selectedLogo === logo.id 
                          ? 'ring-2 ring-purple-500 border-purple-500' 
                          : 'hover:border-purple-300'
                      }`}
                      onClick={() => setSelectedLogo(logo.id)}
                    >
                      <CardContent className="p-6">
                        <div 
                          className="w-full h-32 rounded-lg flex items-center justify-center mb-4"
                          style={{ backgroundColor: brandConfig.secondaryColor }}
                        >
                          {logo.type === 'icon' ? (
                            <div 
                              className="w-16 h-16 rounded-xl flex items-center justify-center text-2xl font-bold"
                              style={{ backgroundColor: brandConfig.primaryColor, color: brandConfig.secondaryColor }}
                            >
                              {brandConfig.companyName?.substring(0, 2).toUpperCase() || 'CO'}
                            </div>
                          ) : logo.type === 'wordmark' ? (
                            <span 
                              className="text-2xl font-bold"
                              style={{ color: brandConfig.primaryColor }}
                            >
                              {brandConfig.companyName || 'Company'}
                            </span>
                          ) : (
                            <div className="flex items-center space-x-2">
                              <div 
                                className="w-10 h-10 rounded-lg flex items-center justify-center text-lg font-bold"
                                style={{ backgroundColor: brandConfig.primaryColor, color: brandConfig.secondaryColor }}
                              >
                                {brandConfig.companyName?.substring(0, 1).toUpperCase() || 'C'}
                              </div>
                              <span 
                                className="text-xl font-semibold"
                                style={{ color: brandConfig.accentColor }}
                              >
                                {brandConfig.companyName || 'Company'}
                              </span>
                            </div>
                          )}
                        </div>
                        <h4 className="font-semibold capitalize">{logo.type} Logo</h4>
                        <p className="text-sm text-gray-500">{logo.description}</p>
                        {selectedLogo === logo.id && (
                          <Badge className="mt-2 bg-purple-100 text-purple-700">
                            <Check size={12} className="mr-1" /> Selected
                          </Badge>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
                
                <div className="flex justify-center">
                  <Button variant="outline" onClick={generateLogos} disabled={generating}>
                    <RefreshCw className={`mr-2 ${generating ? 'animate-spin' : ''}`} size={16} />
                    Regenerate Logos
                  </Button>
                </div>
              </>
            )}
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <Download className="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold">Your Brand Kit is Ready!</h3>
              <p className="text-gray-500">Review and save your complete brand package</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Logo Preview */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Logo</CardTitle>
                </CardHeader>
                <CardContent>
                  <div 
                    className="w-full h-32 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: brandConfig.secondaryColor }}
                  >
                    {selectedLogo && generatedLogos.find(l => l.id === selectedLogo)?.type === 'icon' ? (
                      <div 
                        className="w-16 h-16 rounded-xl flex items-center justify-center text-2xl font-bold"
                        style={{ backgroundColor: brandConfig.primaryColor, color: brandConfig.secondaryColor }}
                      >
                        {brandConfig.companyName?.substring(0, 2).toUpperCase() || 'CO'}
                      </div>
                    ) : selectedLogo && generatedLogos.find(l => l.id === selectedLogo)?.type === 'wordmark' ? (
                      <span 
                        className="text-2xl font-bold"
                        style={{ color: brandConfig.primaryColor }}
                      >
                        {brandConfig.companyName || 'Company'}
                      </span>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-10 h-10 rounded-lg flex items-center justify-center text-lg font-bold"
                          style={{ backgroundColor: brandConfig.primaryColor, color: brandConfig.secondaryColor }}
                        >
                          {brandConfig.companyName?.substring(0, 1).toUpperCase() || 'C'}
                        </div>
                        <span 
                          className="text-xl font-semibold"
                          style={{ color: brandConfig.accentColor }}
                        >
                          {brandConfig.companyName || 'Company'}
                        </span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
              
              {/* Colors */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Color Palette</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex space-x-4">
                    <div className="text-center">
                      <div 
                        className="w-16 h-16 rounded-lg border"
                        style={{ backgroundColor: brandConfig.primaryColor }}
                      />
                      <p className="text-xs mt-1">Primary</p>
                      <p className="text-xs text-gray-500">{brandConfig.primaryColor}</p>
                    </div>
                    <div className="text-center">
                      <div 
                        className="w-16 h-16 rounded-lg border"
                        style={{ backgroundColor: brandConfig.secondaryColor }}
                      />
                      <p className="text-xs mt-1">Secondary</p>
                      <p className="text-xs text-gray-500">{brandConfig.secondaryColor}</p>
                    </div>
                    <div className="text-center">
                      <div 
                        className="w-16 h-16 rounded-lg border"
                        style={{ backgroundColor: brandConfig.accentColor }}
                      />
                      <p className="text-xs mt-1">Accent</p>
                      <p className="text-xs text-gray-500">{brandConfig.accentColor}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              {/* Typography */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Typography</CardTitle>
                </CardHeader>
                <CardContent>
                  {brandConfig.fontPairing && (
                    <div>
                      <p className="text-lg font-semibold" style={{ fontFamily: FONT_PAIRINGS.find(f => f.id === brandConfig.fontPairing)?.heading }}>
                        {FONT_PAIRINGS.find(f => f.id === brandConfig.fontPairing)?.heading}
                      </p>
                      <p className="text-sm text-gray-600" style={{ fontFamily: FONT_PAIRINGS.find(f => f.id === brandConfig.fontPairing)?.body }}>
                        {FONT_PAIRINGS.find(f => f.id === brandConfig.fontPairing)?.body}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
              
              {/* Brand Style */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Brand Style</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="font-semibold">{BRAND_STYLES.find(s => s.id === brandConfig.brandStyle)?.name}</p>
                  <p className="text-sm text-gray-500">{BRAND_STYLES.find(s => s.id === brandConfig.brandStyle)?.description}</p>
                  {brandConfig.tagline && (
                    <p className="mt-2 italic text-purple-600">&ldquo;{brandConfig.tagline}&rdquo;</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  // Overview mode (not in wizard)
  if (wizardStep === 0) {
    return (
      <div className="space-y-6 animate-slide-in" data-testid="branding-page">
        <PageHeader
          icon={Palette}
          title="Branding"
          description="Create and manage your visual identity and brand assets"
          actions={
            <Button onClick={() => setWizardStep(1)} className="gradient-primary border-0">
              <Sparkles className="mr-2" size={18} />
              {brandAssets ? 'Edit Brand Kit' : 'Create Brand Kit'}
            </Button>
          }
        />

        {brandAssets ? (
          // Show existing brand assets
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Logo Card */}
              <Card>
                <CardContent className="p-6 text-center">
                  <div 
                    className="w-full h-24 rounded-lg flex items-center justify-center mb-4"
                    style={{ backgroundColor: brandAssets.colors?.secondary || '#f1f5f9' }}
                  >
                    <div 
                      className="w-12 h-12 rounded-xl flex items-center justify-center text-xl font-bold"
                      style={{ 
                        backgroundColor: brandAssets.colors?.primary || '#6366f1', 
                        color: brandAssets.colors?.secondary || '#fff' 
                      }}
                    >
                      {brandConfig.companyName?.substring(0, 2).toUpperCase() || 'CO'}
                    </div>
                  </div>
                  <h3 className="font-semibold text-lg mb-2">Your Logo</h3>
                  <Button variant="outline" size="sm" onClick={() => setWizardStep(3)}>
                    <Edit3 size={14} className="mr-1" /> Edit
                  </Button>
                </CardContent>
              </Card>

              {/* Colors Card */}
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="flex justify-center space-x-2 mb-4">
                    <div 
                      className="w-12 h-12 rounded-full border"
                      style={{ backgroundColor: brandAssets.colors?.primary }}
                    />
                    <div 
                      className="w-12 h-12 rounded-full border"
                      style={{ backgroundColor: brandAssets.colors?.secondary }}
                    />
                    <div 
                      className="w-12 h-12 rounded-full border"
                      style={{ backgroundColor: brandAssets.colors?.accent }}
                    />
                  </div>
                  <h3 className="font-semibold text-lg mb-2">Color Palette</h3>
                  <Button variant="outline" size="sm" onClick={() => setWizardStep(2)}>
                    <Edit3 size={14} className="mr-1" /> Edit
                  </Button>
                </CardContent>
              </Card>

              {/* Typography Card */}
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="mb-4">
                    <p className="text-xl font-semibold">{brandAssets.fonts?.heading || 'Poppins'}</p>
                    <p className="text-sm text-gray-500">{brandAssets.fonts?.body || 'Inter'}</p>
                  </div>
                  <h3 className="font-semibold text-lg mb-2">Typography</h3>
                  <Button variant="outline" size="sm" onClick={() => setWizardStep(2)}>
                    <Edit3 size={14} className="mr-1" /> Edit
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Export Section */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Download className="mr-2 text-purple-600" size={20} />
                  Export Brand Kit
                </CardTitle>
                <CardDescription>Download your complete brand package</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
                  <div>
                    <h4 className="font-semibold">Complete Brand Kit</h4>
                    <p className="text-sm text-gray-500">Logos, colors, fonts, and guidelines</p>
                  </div>
                  <Button variant="outline">
                    <Download size={16} className="mr-2" />
                    Download ZIP
                  </Button>
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          // Empty state
          <Card className="text-center py-16">
            <CardContent>
              <Shapes className="mx-auto text-gray-300 mb-4" size={64} />
              <h3 className="text-xl font-semibold mb-2">No Brand Kit Yet</h3>
              <p className="text-gray-500 mb-6 max-w-md mx-auto">
                Create your brand identity with our AI-powered branding wizard. 
                We&apos;ll use your confirmed company details to generate a perfect brand kit.
              </p>
              <Button onClick={() => setWizardStep(1)} className="gradient-primary border-0" size="lg">
                <Sparkles className="mr-2" size={18} />
                Start Branding Wizard
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    );
  }

  // Wizard mode
  return (
    <div className="space-y-6 animate-slide-in" data-testid="branding-wizard">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Branding Wizard</h1>
          <p className="text-gray-500">Step {wizardStep} of 4: {WIZARD_STEPS[wizardStep - 1]?.title}</p>
        </div>
        <Button variant="outline" onClick={() => setWizardStep(0)}>
          Exit Wizard
        </Button>
      </div>
      
      <Progress value={progress} className="h-2" />
      
      {/* Step indicators */}
      <div className="flex justify-between">
        {WIZARD_STEPS.map((step) => (
          <div 
            key={step.id}
            className={`flex items-center ${step.id < wizardStep ? 'text-purple-600' : step.id === wizardStep ? 'text-purple-600' : 'text-gray-400'}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step.id < wizardStep ? 'bg-purple-600 text-white' : 
              step.id === wizardStep ? 'bg-purple-100 text-purple-600 border-2 border-purple-600' : 
              'bg-gray-100'
            }`}>
              {step.id < wizardStep ? <Check size={16} /> : step.id}
            </div>
            <span className="ml-2 text-sm hidden md:inline">{step.title}</span>
          </div>
        ))}
      </div>
      
      {/* Wizard Content */}
      <Card>
        <CardContent className="p-8">
          {renderWizardContent()}
        </CardContent>
      </Card>
      
      {/* Navigation */}
      <div className="flex justify-between">
        <Button 
          variant="outline" 
          onClick={() => setWizardStep(wizardStep - 1)}
          disabled={wizardStep === 1}
        >
          <ArrowLeft className="mr-2" size={16} /> Previous
        </Button>
        
        {wizardStep < 4 ? (
          <Button 
            onClick={() => {
              if (wizardStep === 2 && !brandConfig.brandStyle) {
                toast.error('Please select a brand style');
                return;
              }
              if (wizardStep === 3 && generatedLogos.length === 0) {
                toast.error('Please generate logos first');
                return;
              }
              setWizardStep(wizardStep + 1);
            }}
            className="gradient-primary border-0"
          >
            Next <ArrowRight className="ml-2" size={16} />
          </Button>
        ) : (
          <Button 
            onClick={saveBrandKit}
            disabled={generating || !selectedLogo}
            className="gradient-primary border-0"
          >
            {generating ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</>
            ) : (
              <>Save Brand Kit <Check className="ml-2" size={16} /></>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
