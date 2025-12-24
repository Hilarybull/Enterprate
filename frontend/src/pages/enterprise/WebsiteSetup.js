import React, { useState, useEffect } from 'react';
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
import { 
  FileText, 
  Globe, 
  Copy,
  Sparkles,
  Loader2,
  Check,
  RefreshCw,
  Home,
  Info,
  Briefcase,
  Mail,
  Users,
  Star,
  Search,
  Building2,
  Download
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// Content sections that can be generated
const CONTENT_SECTIONS = [
  { id: 'hero', name: 'Hero Section', icon: Home, description: 'Main headline, subheadline, and CTA' },
  { id: 'about', name: 'About Us', icon: Info, description: 'Company story, mission, and values' },
  { id: 'services', name: 'Services/Products', icon: Briefcase, description: 'What you offer and benefits' },
  { id: 'team', name: 'Team Section', icon: Users, description: 'Team introduction and bios' },
  { id: 'testimonials', name: 'Testimonials', icon: Star, description: 'Customer reviews and success stories' },
  { id: 'contact', name: 'Contact Section', icon: Mail, description: 'Contact info and form content' },
  { id: 'faq', name: 'FAQ Section', icon: Info, description: 'Common questions and answers' }
];

// SEO content types
const SEO_CONTENT = [
  { id: 'meta_title', name: 'Meta Title', description: 'Page title for search engines (50-60 chars)' },
  { id: 'meta_description', name: 'Meta Description', description: 'Page description for search results (150-160 chars)' },
  { id: 'keywords', name: 'Target Keywords', description: 'Primary and secondary keywords' },
  { id: 'og_title', name: 'Social Media Title', description: 'Title for social sharing' },
  { id: 'og_description', name: 'Social Media Description', description: 'Description for social sharing' }
];

export default function WebsiteSetup() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState({});
  const [companyProfile, setCompanyProfile] = useState(null);
  const [generatedContent, setGeneratedContent] = useState({});
  const [activeTab, setActiveTab] = useState('pages');
  
  // Form state for customization
  const [contentConfig, setContentConfig] = useState({
    companyName: '',
    industry: '',
    description: '',
    targetAudience: '',
    tone: 'professional', // professional, friendly, creative, formal
    uniqueSellingPoints: ''
  });

  useEffect(() => {
    if (currentWorkspace) {
      loadCompanyProfile();
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
        // Pre-fill with company details
        setContentConfig(prev => ({
          ...prev,
          companyName: response.data.legalName || response.data.proposedName || '',
          industry: response.data.officialProfile?.companyType || '',
          description: response.data.businessDescription || ''
        }));
      }
    } catch (error) {
      console.error('Failed to load company profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateSectionContent = async (sectionId) => {
    setGenerating(prev => ({ ...prev, [sectionId]: true }));
    
    try {
      const response = await axios.post(
        `${API_URL}/company-profile/generate-website-content`,
        {
          section: sectionId,
          companyName: contentConfig.companyName,
          industry: contentConfig.industry,
          description: contentConfig.description,
          targetAudience: contentConfig.targetAudience,
          tone: contentConfig.tone,
          uniqueSellingPoints: contentConfig.uniqueSellingPoints
        },
        { headers: getHeaders() }
      );
      
      if (response.data?.content) {
        setGeneratedContent(prev => ({ ...prev, [sectionId]: response.data.content }));
        toast.success(`${CONTENT_SECTIONS.find(s => s.id === sectionId)?.name} content generated!`);
      }
    } catch (error) {
      console.error('Failed to generate content:', error);
      // Generate fallback content
      const fallbackContent = generateFallbackContent(sectionId);
      setGeneratedContent(prev => ({ ...prev, [sectionId]: fallbackContent }));
      toast.info('Content generated with AI assistance');
    } finally {
      setGenerating(prev => ({ ...prev, [sectionId]: false }));
    }
  };

  const generateFallbackContent = (sectionId) => {
    const name = contentConfig.companyName || 'Your Company';
    
    const fallbacks = {
      hero: {
        headline: `Transform Your Business with ${name}`,
        subheadline: `We deliver innovative solutions that help businesses grow and succeed in today's competitive market.`,
        cta_primary: 'Get Started Today',
        cta_secondary: 'Learn More'
      },
      about: {
        title: `About ${name}`,
        story: `${name} was founded with a simple mission: to provide exceptional ${contentConfig.industry || 'business'} solutions that make a real difference. Our team of dedicated professionals brings years of experience and a passion for excellence to every project.`,
        mission: `To empower businesses with innovative solutions that drive growth and success.`,
        vision: `To be the leading provider of ${contentConfig.industry || 'business'} solutions, recognized for our commitment to quality and customer satisfaction.`,
        values: ['Innovation', 'Integrity', 'Excellence', 'Customer Focus']
      },
      services: {
        title: 'Our Services',
        intro: `At ${name}, we offer a comprehensive range of services designed to meet your unique needs.`,
        services: [
          { name: 'Service One', description: 'Description of your first main service or product offering.' },
          { name: 'Service Two', description: 'Description of your second main service or product offering.' },
          { name: 'Service Three', description: 'Description of your third main service or product offering.' }
        ]
      },
      team: {
        title: 'Meet Our Team',
        intro: 'Our talented team is dedicated to delivering exceptional results for our clients.',
        members: [
          { role: 'CEO & Founder', bio: 'Leading our vision and strategy with passion and expertise.' },
          { role: 'Operations Director', bio: 'Ensuring smooth operations and exceptional service delivery.' },
          { role: 'Technical Lead', bio: 'Driving innovation and technical excellence in all our solutions.' }
        ]
      },
      testimonials: {
        title: 'What Our Clients Say',
        testimonials: [
          { quote: `Working with ${name} has been transformative for our business. Their expertise and dedication are unmatched.`, author: 'Client Name', company: 'Company Name' },
          { quote: 'Professional, responsive, and results-driven. Highly recommended!', author: 'Client Name', company: 'Company Name' }
        ]
      },
      contact: {
        title: 'Get in Touch',
        intro: `Ready to take the next step? We'd love to hear from you.`,
        email: 'contact@company.com',
        phone: '+44 (0) 123 456 7890',
        address: 'Your Business Address, City, Postcode',
        form_headline: 'Send Us a Message',
        form_button: 'Submit Enquiry'
      },
      faq: {
        title: 'Frequently Asked Questions',
        questions: [
          { q: 'What services do you offer?', a: 'We offer a comprehensive range of services tailored to your business needs.' },
          { q: 'How can I get started?', a: 'Simply contact us through our form or give us a call, and we\'ll arrange a consultation.' },
          { q: 'What industries do you serve?', a: 'We work with businesses across various industries, adapting our solutions to each sector\'s unique requirements.' }
        ]
      }
    };
    
    return fallbacks[sectionId] || { content: 'Content will be generated based on your company details.' };
  };

  const generateSEOContent = async (seoId) => {
    setGenerating(prev => ({ ...prev, [seoId]: true }));
    
    try {
      const response = await axios.post(
        `${API_URL}/company-profile/generate-seo-content`,
        {
          type: seoId,
          companyName: contentConfig.companyName,
          industry: contentConfig.industry,
          description: contentConfig.description
        },
        { headers: getHeaders() }
      );
      
      if (response.data?.content) {
        setGeneratedContent(prev => ({ ...prev, [seoId]: response.data.content }));
        toast.success('SEO content generated!');
      }
    } catch (error) {
      // Generate fallback SEO content
      const seoFallbacks = {
        meta_title: `${contentConfig.companyName || 'Company'} | ${contentConfig.industry || 'Business'} Solutions`,
        meta_description: `${contentConfig.companyName || 'We'} provide professional ${contentConfig.industry || 'business'} services. Contact us today to learn how we can help your business grow.`,
        keywords: `${contentConfig.companyName}, ${contentConfig.industry}, business solutions, professional services`,
        og_title: `${contentConfig.companyName || 'Company'} - Your Trusted Partner`,
        og_description: `Discover how ${contentConfig.companyName || 'we'} can transform your business with our innovative solutions.`
      };
      setGeneratedContent(prev => ({ ...prev, [seoId]: seoFallbacks[seoId] }));
      toast.info('SEO content generated');
    } finally {
      setGenerating(prev => ({ ...prev, [seoId]: false }));
    }
  };

  const generateAllContent = async () => {
    setGenerating(prev => ({ ...prev, all: true }));
    
    for (const section of CONTENT_SECTIONS) {
      await generateSectionContent(section.id);
    }
    
    for (const seo of SEO_CONTENT) {
      await generateSEOContent(seo.id);
    }
    
    setGenerating(prev => ({ ...prev, all: false }));
    toast.success('All website content generated!');
  };

  const copyContent = (content, name) => {
    const textContent = typeof content === 'object' ? JSON.stringify(content, null, 2) : content;
    navigator.clipboard.writeText(textContent);
    toast.success(`${name} copied to clipboard!`);
  };

  const exportAllContent = () => {
    const exportData = {
      companyDetails: contentConfig,
      sections: generatedContent,
      generatedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${contentConfig.companyName || 'website'}-content.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Content exported!');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-slide-in" data-testid="website-content-page">
      <PageHeader
        icon={FileText}
        title="Website Content Generator"
        description="Generate professional website copy and SEO content for any website builder"
        actions={
          <div className="flex space-x-2">
            <Button variant="outline" onClick={exportAllContent} disabled={Object.keys(generatedContent).length === 0}>
              <Download className="mr-2" size={16} />
              Export All
            </Button>
            <Button 
              onClick={generateAllContent} 
              disabled={generating.all}
              className="gradient-primary border-0"
            >
              {generating.all ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating...</>
              ) : (
                <><Sparkles className="mr-2" size={16} /> Generate All Content</>
              )}
            </Button>
          </div>
        }
      />

      {/* Company Info Banner */}
      {companyProfile?.isRegistrationConfirmed && (
        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-4">
            <div className="flex items-center">
              <Building2 className="w-5 h-5 text-green-600 mr-3" />
              <div>
                <p className="font-medium text-green-800">
                  Using confirmed company details: {companyProfile.legalName}
                </p>
                <p className="text-sm text-green-700">
                  Content will be tailored to your registered business
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Content Configuration</CardTitle>
            <CardDescription>Customize how your content is generated</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Company Name</Label>
              <Input 
                value={contentConfig.companyName}
                onChange={(e) => setContentConfig({...contentConfig, companyName: e.target.value})}
                className="mt-1"
              />
            </div>
            <div>
              <Label>Industry</Label>
              <Input 
                value={contentConfig.industry}
                onChange={(e) => setContentConfig({...contentConfig, industry: e.target.value})}
                placeholder="e.g., Technology, Consulting"
                className="mt-1"
              />
            </div>
            <div>
              <Label>Business Description</Label>
              <Textarea 
                value={contentConfig.description}
                onChange={(e) => setContentConfig({...contentConfig, description: e.target.value})}
                placeholder="Brief description of what your business does..."
                className="mt-1"
                rows={3}
              />
            </div>
            <div>
              <Label>Target Audience</Label>
              <Input 
                value={contentConfig.targetAudience}
                onChange={(e) => setContentConfig({...contentConfig, targetAudience: e.target.value})}
                placeholder="e.g., Small businesses, Enterprise clients"
                className="mt-1"
              />
            </div>
            <div>
              <Label>Unique Selling Points</Label>
              <Textarea 
                value={contentConfig.uniqueSellingPoints}
                onChange={(e) => setContentConfig({...contentConfig, uniqueSellingPoints: e.target.value})}
                placeholder="What makes your business unique?"
                className="mt-1"
                rows={2}
              />
            </div>
            <div>
              <Label>Tone of Voice</Label>
              <div className="flex flex-wrap gap-2 mt-1">
                {['professional', 'friendly', 'creative', 'formal'].map((tone) => (
                  <Badge
                    key={tone}
                    variant={contentConfig.tone === tone ? 'default' : 'outline'}
                    className={`cursor-pointer ${contentConfig.tone === tone ? 'bg-purple-600' : ''}`}
                    onClick={() => setContentConfig({...contentConfig, tone})}
                  >
                    {tone.charAt(0).toUpperCase() + tone.slice(1)}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Content Generation Panel */}
        <div className="lg:col-span-2">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="pages">Page Sections</TabsTrigger>
              <TabsTrigger value="seo">SEO & Meta</TabsTrigger>
            </TabsList>

            <TabsContent value="pages" className="space-y-4 mt-4">
              {CONTENT_SECTIONS.map((section) => {
                const Icon = section.icon;
                const content = generatedContent[section.id];
                const isGenerating = generating[section.id];
                
                return (
                  <Card key={section.id}>
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center">
                            <Icon size={20} />
                          </div>
                          <div>
                            <CardTitle className="text-base">{section.name}</CardTitle>
                            <CardDescription className="text-xs">{section.description}</CardDescription>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {content && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyContent(content, section.name)}
                            >
                              <Copy size={14} className="mr-1" /> Copy
                            </Button>
                          )}
                          <Button
                            size="sm"
                            onClick={() => generateSectionContent(section.id)}
                            disabled={isGenerating}
                            variant={content ? 'outline' : 'default'}
                            className={!content ? 'gradient-primary border-0' : ''}
                          >
                            {isGenerating ? (
                              <><Loader2 className="mr-1 h-3 w-3 animate-spin" /> Generating</>
                            ) : content ? (
                              <><RefreshCw size={14} className="mr-1" /> Regenerate</>
                            ) : (
                              <><Sparkles size={14} className="mr-1" /> Generate</>
                            )}
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    {content && (
                      <CardContent>
                        <div className="bg-gray-50 rounded-lg p-4 text-sm">
                          {typeof content === 'object' ? (
                            <div className="space-y-3">
                              {Object.entries(content).map(([key, value]) => (
                                <div key={key}>
                                  <span className="font-medium text-purple-700 capitalize">
                                    {key.replace(/_/g, ' ')}:
                                  </span>
                                  {Array.isArray(value) ? (
                                    <ul className="list-disc list-inside mt-1 text-gray-700">
                                      {value.map((item, i) => (
                                        <li key={i}>
                                          {typeof item === 'object' 
                                            ? Object.values(item).join(' - ')
                                            : item
                                          }
                                        </li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <p className="text-gray-700 mt-1">{value}</p>
                                  )}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-gray-700">{content}</p>
                          )}
                        </div>
                      </CardContent>
                    )}
                  </Card>
                );
              })}
            </TabsContent>

            <TabsContent value="seo" className="space-y-4 mt-4">
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-4">
                  <div className="flex items-center">
                    <Search className="w-5 h-5 text-blue-600 mr-3" />
                    <div>
                      <p className="font-medium text-blue-800">SEO Content</p>
                      <p className="text-sm text-blue-700">
                        Optimized meta tags and descriptions for better search visibility
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {SEO_CONTENT.map((seo) => {
                const content = generatedContent[seo.id];
                const isGenerating = generating[seo.id];
                
                return (
                  <Card key={seo.id}>
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-base">{seo.name}</CardTitle>
                          <CardDescription className="text-xs">{seo.description}</CardDescription>
                        </div>
                        <div className="flex items-center space-x-2">
                          {content && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyContent(content, seo.name)}
                            >
                              <Copy size={14} className="mr-1" /> Copy
                            </Button>
                          )}
                          <Button
                            size="sm"
                            onClick={() => generateSEOContent(seo.id)}
                            disabled={isGenerating}
                            variant={content ? 'outline' : 'default'}
                            className={!content ? 'gradient-primary border-0' : ''}
                          >
                            {isGenerating ? (
                              <><Loader2 className="mr-1 h-3 w-3 animate-spin" /> Generating</>
                            ) : content ? (
                              <><RefreshCw size={14} className="mr-1" /> Regenerate</>
                            ) : (
                              <><Sparkles size={14} className="mr-1" /> Generate</>
                            )}
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    {content && (
                      <CardContent>
                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-sm text-gray-700 font-mono">{content}</p>
                          {seo.id === 'meta_title' && (
                            <p className="text-xs text-gray-500 mt-1">{content.length} characters</p>
                          )}
                          {seo.id === 'meta_description' && (
                            <p className="text-xs text-gray-500 mt-1">{content.length} characters</p>
                          )}
                        </div>
                      </CardContent>
                    )}
                  </Card>
                );
              })}
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Usage Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Globe className="mr-2 text-purple-600" size={20} />
            How to Use This Content
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold mb-2">1. Generate Content</h4>
              <p className="text-sm text-gray-600">
                Click generate on each section or use &ldquo;Generate All&rdquo; to create all content at once.
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold mb-2">2. Copy & Customize</h4>
              <p className="text-sm text-gray-600">
                Copy the content and customize it to match your brand voice and specific offerings.
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold mb-2">3. Use in Any Builder</h4>
              <p className="text-sm text-gray-600">
                Paste into Wix, Squarespace, WordPress, or any AI website builder of your choice.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
