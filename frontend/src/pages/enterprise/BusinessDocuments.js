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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { 
  FileSignature, 
  ChevronRight,
  ChevronLeft,
  FileText,
  Scale,
  Shield,
  Handshake,
  ScrollText,
  Loader2,
  Download,
  Eye,
  Edit,
  CheckCircle2,
  Sparkles,
  Building,
  User,
  Calendar,
  Globe
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// Document types with their required fields
const DOCUMENT_TYPES = [
  {
    id: 'terms_conditions',
    name: 'Terms & Conditions',
    icon: ScrollText,
    description: 'Standard terms for your products/services',
    fields: [
      { id: 'companyName', label: 'Company Name', type: 'text', required: true },
      { id: 'businessType', label: 'Business Type', type: 'select', options: ['E-commerce', 'SaaS', 'Consulting', 'Agency', 'Marketplace', 'Other'], required: true },
      { id: 'jurisdiction', label: 'Jurisdiction', type: 'select', options: ['England & Wales', 'Scotland', 'United States', 'European Union'], required: true },
      { id: 'refundPolicy', label: 'Refund Policy', type: 'textarea', placeholder: 'Describe your refund/cancellation policy' },
      { id: 'liabilityLimit', label: 'Liability Limit', type: 'text', placeholder: 'e.g., £1,000 or "contract value"' }
    ]
  },
  {
    id: 'privacy_policy',
    name: 'Privacy Policy',
    icon: Shield,
    description: 'GDPR-compliant privacy policy',
    fields: [
      { id: 'companyName', label: 'Company Name', type: 'text', required: true },
      { id: 'companyAddress', label: 'Company Address', type: 'textarea', required: true },
      { id: 'contactEmail', label: 'Data Protection Contact Email', type: 'email', required: true },
      { id: 'dataCollected', label: 'Types of Data Collected', type: 'textarea', placeholder: 'e.g., Name, email, payment info, usage data' },
      { id: 'thirdParties', label: 'Third Party Services Used', type: 'textarea', placeholder: 'e.g., Stripe, Google Analytics, Mailchimp' },
      { id: 'dataRetention', label: 'Data Retention Period', type: 'text', placeholder: 'e.g., 7 years' }
    ]
  },
  {
    id: 'service_agreement',
    name: 'Service Agreement',
    icon: Handshake,
    description: 'Contract for service delivery',
    fields: [
      { id: 'providerName', label: 'Service Provider Name', type: 'text', required: true },
      { id: 'clientName', label: 'Client Name', type: 'text', required: true },
      { id: 'serviceDescription', label: 'Service Description', type: 'textarea', required: true },
      { id: 'deliverables', label: 'Key Deliverables', type: 'textarea', placeholder: 'List main deliverables' },
      { id: 'timeline', label: 'Project Timeline', type: 'text', placeholder: 'e.g., 4 weeks from start date' },
      { id: 'paymentTerms', label: 'Payment Terms', type: 'textarea', placeholder: 'e.g., 50% upfront, 50% on completion' },
      { id: 'totalValue', label: 'Contract Value', type: 'text', placeholder: 'e.g., £5,000' }
    ]
  },
  {
    id: 'proposal',
    name: 'Business Proposal',
    icon: FileText,
    description: 'Professional project proposal',
    fields: [
      { id: 'companyName', label: 'Your Company Name', type: 'text', required: true },
      { id: 'clientName', label: 'Client/Prospect Name', type: 'text', required: true },
      { id: 'projectTitle', label: 'Project Title', type: 'text', required: true },
      { id: 'problemStatement', label: 'Problem/Opportunity', type: 'textarea', placeholder: 'What problem are you solving?' },
      { id: 'proposedSolution', label: 'Proposed Solution', type: 'textarea', required: true },
      { id: 'scope', label: 'Scope of Work', type: 'textarea', placeholder: 'List what is included' },
      { id: 'pricing', label: 'Pricing', type: 'textarea', placeholder: 'Break down your pricing' },
      { id: 'timeline', label: 'Timeline', type: 'text', placeholder: 'Estimated delivery time' }
    ]
  },
  {
    id: 'nda',
    name: 'Non-Disclosure Agreement',
    icon: Scale,
    description: 'Confidentiality agreement',
    fields: [
      { id: 'disclosingParty', label: 'Disclosing Party', type: 'text', required: true },
      { id: 'receivingParty', label: 'Receiving Party', type: 'text', required: true },
      { id: 'purpose', label: 'Purpose of Disclosure', type: 'textarea', required: true, placeholder: 'Why is confidential information being shared?' },
      { id: 'duration', label: 'NDA Duration', type: 'select', options: ['1 year', '2 years', '3 years', '5 years', 'Perpetual'], required: true },
      { id: 'jurisdiction', label: 'Governing Law', type: 'select', options: ['England & Wales', 'Scotland', 'United States', 'European Union'] }
    ]
  }
];

export default function BusinessDocuments() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [step, setStep] = useState(1); // 1: Select Type, 2: Fill Details, 3: Review, 4: Export
  const [selectedType, setSelectedType] = useState(null);
  const [formData, setFormData] = useState({});
  const [generating, setGenerating] = useState(false);
  const [generatedDocument, setGeneratedDocument] = useState(null);
  const [savedDocuments, setSavedDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState('');

  const loadDocuments = useCallback(async () => {
    if (!currentWorkspace) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/documents`, { headers: getHeaders() });
      setSavedDocuments(response.data || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace, getHeaders]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleSelectType = (type) => {
    setSelectedType(type);
    setFormData({});
    setStep(2);
  };

  const handleFieldChange = (fieldId, value) => {
    setFormData(prev => ({ ...prev, [fieldId]: value }));
  };

  const validateForm = () => {
    if (!selectedType) return false;
    const requiredFields = selectedType.fields.filter(f => f.required);
    return requiredFields.every(f => formData[f.id]?.trim());
  };

  const handleGenerate = async () => {
    if (!validateForm()) {
      toast.error('Please fill in all required fields');
      return;
    }

    setGenerating(true);
    try {
      const response = await axios.post(`${API_URL}/documents/generate`, {
        documentType: selectedType.id,
        inputs: formData
      }, { headers: getHeaders() });

      setGeneratedDocument(response.data);
      setEditedContent(response.data.content);
      setStep(3);
      toast.success('Document generated successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate document');
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async () => {
    try {
      const response = await axios.post(`${API_URL}/documents/save`, {
        documentType: selectedType.id,
        title: generatedDocument.title,
        content: editMode ? editedContent : generatedDocument.content,
        inputs: formData
      }, { headers: getHeaders() });

      toast.success('Document saved!');
      loadDocuments();
      setStep(4);
    } catch (error) {
      toast.error('Failed to save document');
    }
  };

  const handleDownload = async (format = 'pdf') => {
    try {
      const response = await axios.post(`${API_URL}/documents/export`, {
        content: editMode ? editedContent : generatedDocument.content,
        title: generatedDocument.title,
        format
      }, { 
        headers: getHeaders(),
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${generatedDocument.title}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success(`Downloaded as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Failed to download document');
    }
  };

  const resetWizard = () => {
    setStep(1);
    setSelectedType(null);
    setFormData({});
    setGeneratedDocument(null);
    setEditMode(false);
    setEditedContent('');
  };

  const progress = (step / 4) * 100;

  return (
    <div className="space-y-6 animate-slide-in" data-testid="business-documents-page">
      <PageHeader
        icon={FileSignature}
        title="Business Documents"
        description="Generate professional legal and business documents with AI assistance"
      />

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-500">
          <span>Step {step} of 4</span>
          <span>{['Select Type', 'Fill Details', 'Review & Edit', 'Export'][step - 1]}</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Step 1: Select Document Type */}
      {step === 1 && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {DOCUMENT_TYPES.map((type) => {
            const Icon = type.icon;
            return (
              <Card 
                key={type.id}
                className="cursor-pointer hover:shadow-lg hover:border-indigo-300 transition-all"
                onClick={() => handleSelectType(type)}
              >
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-indigo-100 rounded-xl">
                      <Icon className="text-indigo-600" size={24} />
                    </div>
                    <div>
                      <h3 className="font-semibold">{type.name}</h3>
                      <p className="text-sm text-gray-500 mt-1">{type.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Step 2: Fill Details */}
      {step === 2 && selectedType && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              {React.createElement(selectedType.icon, { className: "text-indigo-600", size: 24 })}
              <div>
                <CardTitle>{selectedType.name}</CardTitle>
                <CardDescription>Fill in the details below</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {selectedType.fields.map((field) => (
              <div key={field.id}>
                <Label className="flex items-center gap-1">
                  {field.label}
                  {field.required && <span className="text-red-500">*</span>}
                </Label>
                {field.type === 'select' ? (
                  <Select 
                    value={formData[field.id] || ''} 
                    onValueChange={(v) => handleFieldChange(field.id, v)}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder={`Select ${field.label.toLowerCase()}`} />
                    </SelectTrigger>
                    <SelectContent>
                      {field.options.map((opt) => (
                        <SelectItem key={opt} value={opt}>{opt}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : field.type === 'textarea' ? (
                  <Textarea
                    value={formData[field.id] || ''}
                    onChange={(e) => handleFieldChange(field.id, e.target.value)}
                    placeholder={field.placeholder}
                    className="mt-1.5"
                    rows={3}
                  />
                ) : (
                  <Input
                    type={field.type}
                    value={formData[field.id] || ''}
                    onChange={(e) => handleFieldChange(field.id, e.target.value)}
                    placeholder={field.placeholder}
                    className="mt-1.5"
                  />
                )}
              </div>
            ))}

            <div className="flex justify-between pt-4">
              <Button variant="outline" onClick={() => setStep(1)}>
                <ChevronLeft className="mr-2" size={16} /> Back
              </Button>
              <Button onClick={handleGenerate} disabled={generating || !validateForm()}>
                {generating ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating...</>
                ) : (
                  <><Sparkles className="mr-2" size={16} /> Generate Document</>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Review & Edit */}
      {step === 3 && generatedDocument && (
        <div className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>{generatedDocument.title}</CardTitle>
                <CardDescription>Review and edit if needed</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button 
                  variant={editMode ? "default" : "outline"} 
                  size="sm"
                  onClick={() => setEditMode(!editMode)}
                >
                  <Edit className="mr-2" size={16} />
                  {editMode ? 'Preview' : 'Edit'}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {editMode ? (
                <Textarea
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  className="min-h-[500px] font-mono text-sm"
                />
              ) : (
                <div 
                  className="prose max-w-none p-6 bg-gray-50 rounded-lg min-h-[500px] overflow-auto"
                  dangerouslySetInnerHTML={{ __html: editedContent.replace(/\n/g, '<br/>') }}
                />
              )}
            </CardContent>
          </Card>

          <div className="flex justify-between">
            <Button variant="outline" onClick={() => setStep(2)}>
              <ChevronLeft className="mr-2" size={16} /> Back to Edit Details
            </Button>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => handleDownload('pdf')}>
                <Download className="mr-2" size={16} /> Download PDF
              </Button>
              <Button onClick={handleSave}>
                <CheckCircle2 className="mr-2" size={16} /> Save Document
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Step 4: Success */}
      {step === 4 && (
        <Card className="p-12 text-center">
          <CheckCircle2 className="mx-auto text-green-500 mb-4" size={64} />
          <h2 className="text-2xl font-bold text-gray-800">Document Saved!</h2>
          <p className="text-gray-500 mt-2">Your document has been saved to your documents library</p>
          <div className="flex justify-center gap-3 mt-6">
            <Button variant="outline" onClick={resetWizard}>
              Create Another Document
            </Button>
            <Button onClick={() => handleDownload('pdf')}>
              <Download className="mr-2" size={16} /> Download PDF
            </Button>
          </div>
        </Card>
      )}

      {/* Saved Documents */}
      {step === 1 && savedDocuments.length > 0 && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Recent Documents</CardTitle>
            <CardDescription>Previously generated documents</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {savedDocuments.slice(0, 5).map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <FileText className="text-gray-400" size={20} />
                    <div>
                      <p className="font-medium">{doc.title}</p>
                      <p className="text-xs text-gray-500">
                        Created {new Date(doc.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{doc.documentType?.replace(/_/g, ' ')}</Badge>
                    <Button variant="ghost" size="sm">
                      <Eye size={16} />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Download size={16} />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
