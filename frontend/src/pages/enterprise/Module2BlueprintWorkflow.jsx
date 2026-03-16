import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { toast } from 'sonner';
import { Check, Download, Info, Loader2, RefreshCw, Save } from 'lucide-react';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

const OUTPUTS = [
  { id: 'business_plan', label: 'Business Plan', helper: 'Strategy + deterministic financial sections' },
  { id: 'client_proposal', label: 'Client Proposal', helper: 'Client-specific scope and commercial terms' },
  { id: 'sales_letter', label: 'Sales Letter', helper: 'Structured outreach copy from offer data' },
  { id: 'sales_quotation', label: 'Sales Quotation', helper: 'Price-consistent quote with terms' },
  { id: 'cashflow_analysis', label: 'Cashflow Analysis', helper: 'Monthly inflow, outflow, and liquidity signal' },
  { id: 'financial_projection', label: 'Financial Projection', helper: 'Year-by-year deterministic projection' },
];

const MULTILINE_KEYS = new Set(['deliverables']);

const labels = {
  businessName: 'Business name',
  problemSolved: 'Problem statement',
  customerSegment: 'Customer segment',
  serviceType: 'Service offer',
  priceAmount: 'Pricing amount',
  expectedUnitsPerMonth: 'Units per month',
  fixedMonthlyCosts: 'Fixed monthly costs',
  projectionYears: 'Projection years (1,2,3,5)',
  growthRateAnnualPct: 'Annual growth assumption (%)',
  costInflationAnnualPct: 'Annual cost inflation (%)',
  analysisMonths: 'Analysis horizon (months)',
  prospectName: 'Prospect name',
  deliverables: 'Deliverables',
  deliveryTimelineDays: 'Timeline (days)',
  paymentTermsDays: 'Payment terms (days)',
  targetRecipientType: 'Recipient type',
  tonePreference: 'Tone preference',
  clientName: 'Client name',
  servicePackage: 'Service package',
  validityDays: 'Validity period (days)',
  paymentSchedule: 'Payment schedule',
};

const helpText = {
  businessName: 'The name that will appear on the generated documents (your trading/business name).',
  problemSolved: 'In 1–2 sentences: what pain point are you solving and for whom?',
  customerSegment: 'Who you sell to (e.g., “UK SMEs in retail”, “homeowners in Manchester”).',
  serviceType: 'What you offer (product or service) in plain language.',
  priceAmount: 'Your price per unit/package (use numbers only; currency is inferred from your location).',
  expectedUnitsPerMonth: 'Estimated monthly volume (units sold, projects delivered, subscriptions, etc.).',
  fixedMonthlyCosts: 'Monthly fixed costs (e.g., rent, tools, insurance, subscriptions).',
  projectionYears: 'How many years to include in the financial forecast. Allowed: 1, 2, 3, or 5.',
  growthRateAnnualPct: 'Assumed annual revenue growth used for projections (percentage).',
  costInflationAnnualPct: 'Assumed annual cost inflation used for projections (percentage).',
  analysisMonths: 'Number of months to generate the cashflow table for (up to 60).',
  prospectName: 'The client/prospect name this proposal is addressed to.',
  deliverables: 'List the concrete outputs you will deliver (bullet points work well).',
  deliveryTimelineDays: 'Estimated delivery time in days.',
  paymentTermsDays: 'How many days the client has to pay after invoicing (e.g., 7, 14, 30).',
  targetRecipientType: 'Who the document is written for (e.g., “investor”, “customer”, “partner”).',
  tonePreference: 'Tone guidance (e.g., “formal”, “friendly”, “premium”, “direct”).',
  clientName: 'Client name for quotation/invoice-style outputs.',
  servicePackage: 'The package/tier being purchased (if applicable).',
  validityDays: 'How long the quote is valid for, in days (e.g., 14 or 30).',
  paymentSchedule: 'If staged payments apply, describe milestones and percentages.',
};

const numberKeys = new Set([
  'projectionYears',
  'growthRateAnnualPct',
  'costInflationAnnualPct',
  'analysisMonths',
  'deliveryTimelineDays',
  'paymentTermsDays',
  'validityDays',
]);

export default function Module2BlueprintWorkflow({ getHeaders }) {
  const [eligibility, setEligibility] = useState(null);
  const [selectedType, setSelectedType] = useState('business_plan');
  const [loadingEligibility, setLoadingEligibility] = useState(true);
  const [savingInputs, setSavingInputs] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [formInputs, setFormInputs] = useState({});
  const [documentDraft, setDocumentDraft] = useState(null);
  const [savingSection, setSavingSection] = useState('');
  const [regeneratingSection, setRegeneratingSection] = useState('');
  const [showInputsDialog, setShowInputsDialog] = useState(false);
  const [missingFieldsForDialog, setMissingFieldsForDialog] = useState([]);
  const [hasTriedGenerate, setHasTriedGenerate] = useState(false);

  const loadEligibility = async () => {
    setLoadingEligibility(true);
    try {
      const res = await axios.get(`${API_URL}/blueprint/module2/eligibility`, {
        headers: getHeaders(),
      });
      setEligibility(res.data);
    } catch (error) {
      toast.error('Failed to load Module 2 readiness');
      console.error(error);
    } finally {
      setLoadingEligibility(false);
    }
  };

  useEffect(() => {
    loadEligibility();
  }, []);

  useEffect(() => {
    setShowInputsDialog(false);
    setMissingFieldsForDialog([]);
    setHasTriedGenerate(false);
  }, [selectedType]);

  const selectedReadiness = useMemo(() => {
    if (!eligibility) return null;
    const all = [...(eligibility.available || []), ...(eligibility.partial || []), ...(eligibility.missing || [])];
    return all.find((item) => item.documentType === selectedType) || null;
  }, [eligibility, selectedType]);

  const missingFields = missingFieldsForDialog.length
    ? missingFieldsForDialog
    : (selectedReadiness?.missingFields || []);

  const onSaveInputs = async () => {
    if (!selectedReadiness) return;
    setSavingInputs(true);
    try {
      const payload = {
        businessId: eligibility?.businessId || null,
        documentType: selectedType,
        inputs: formInputs,
        provenance: { source: 'module2-ui' },
      };
      const res = await axios.post(`${API_URL}/blueprint/module2/input`, payload, {
        headers: getHeaders(),
      });
      setEligibility((prev) => {
        if (!prev) return prev;
        const next = { ...prev };
        const up = (arr) => (arr || []).map((x) => (x.documentType === selectedType ? res.data.readiness : x));
        next.available = up(next.available);
        next.partial = up(next.partial);
        next.missing = up(next.missing);
        return next;
      });
      toast.success('Inputs saved');
      setMissingFieldsForDialog([]);
      setShowInputsDialog(false);
    } catch (error) {
      toast.error('Could not save inputs');
      console.error(error);
    } finally {
      setSavingInputs(false);
    }
  };

  const onGenerate = async () => {
    setGenerating(true);
    setHasTriedGenerate(true);
    try {
      const payload = {
        businessId: eligibility?.businessId || null,
        documentType: selectedType,
        regenerate: false,
      };
      const res = await axios.post(`${API_URL}/blueprint/module2/generate`, payload, {
        headers: getHeaders(),
      });
      setDocumentDraft(res.data);
      toast.success('Draft generated');
      await loadEligibility();
    } catch (error) {
      const detail = error?.response?.data?.detail;
      if (detail?.missingFields) {
        toast.error('Missing required fields before generation');
        setMissingFieldsForDialog(detail.missingFields || []);
        if (detail?.suggestedInputs) {
          const suggested = detail.suggestedInputs || {};
          setFormInputs((prev) => {
            const next = { ...prev };
            Object.entries(suggested).forEach(([key, value]) => {
              const existing = next[key];
              if (existing === undefined || existing === null || String(existing).trim() === '') {
                next[key] = value;
              }
            });
            return next;
          });
        }
        setShowInputsDialog(true);
      } else {
        toast.error('Generation failed');
      }
      console.error(error);
    } finally {
      setGenerating(false);
    }
  };

  const onUpdateSection = async (sectionId, content) => {
    if (!documentDraft?.id) return;
    setSavingSection(sectionId);
    try {
      const res = await axios.post(
        `${API_URL}/blueprint/module2/document/${documentDraft.id}/edit`,
        { sectionId, content },
        { headers: getHeaders() },
      );
      setDocumentDraft(res.data);
      toast.success('Section saved');
    } catch (error) {
      toast.error('Could not save section');
      console.error(error);
    } finally {
      setSavingSection('');
    }
  };

  const onRegenerateSection = async (sectionId) => {
    if (!documentDraft?.id) return;
    setRegeneratingSection(sectionId);
    try {
      const res = await axios.post(
        `${API_URL}/blueprint/module2/document/${documentDraft.id}/regenerate-section`,
        { sectionId },
        { headers: getHeaders() },
      );
      setDocumentDraft(res.data);
      toast.success('Section regenerated');
    } catch (error) {
      toast.error('Section regeneration failed');
      console.error(error);
    } finally {
      setRegeneratingSection('');
    }
  };

  const onExport = async (format) => {
    if (!documentDraft?.id) return;
    try {
      const res = await axios.get(`${API_URL}/blueprint/module2/document/${documentDraft.id}/export`, {
        params: { format },
        headers: getHeaders(),
      });
      const content = res.data?.content || '';
      const blob = new Blob([content], { type: format === 'html' ? 'text/html' : 'text/plain' });
      const href = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = href;
      a.download = `${selectedType}.${format === 'html' ? 'html' : 'txt'}`;
      a.click();
      URL.revokeObjectURL(href);
    } catch (error) {
      toast.error('Export failed');
      console.error(error);
    }
  };

  return (
    <TooltipProvider>
      <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Blueprint Output Builder</CardTitle>
          <CardDescription>
            Generate your core business documents from your saved business data. Numbers come from your inputs; AI only improves wording and structure.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {OUTPUTS.map((output) => {
              const readiness = [...(eligibility?.available || []), ...(eligibility?.partial || []), ...(eligibility?.missing || [])]
                .find((x) => x.documentType === output.id);
              const active = selectedType === output.id;
              return (
                <button
                  key={output.id}
                  type="button"
                  onClick={() => setSelectedType(output.id)}
                  className={`rounded-xl border p-3 text-left transition ${
                    active ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200 hover:border-indigo-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <p className="font-semibold text-sm">{output.label}</p>
                    {readiness?.ready ? (
                      <Badge className="bg-green-100 text-green-700"><Check size={12} className="mr-1" />Ready</Badge>
                    ) : (
                      <Badge variant="outline">{readiness?.completionPercent || 0}%</Badge>
                    )}
                  </div>
                  <p className="text-xs text-gray-600 mt-2">{output.helper}</p>
                </button>
              );
            })}
          </div>

          {loadingEligibility ? (
            <div className="flex items-center text-sm text-gray-500"><Loader2 className="mr-2 h-4 w-4 animate-spin" />Checking readiness...</div>
          ) : selectedReadiness ? (
            <div className="space-y-3">
              <div className="rounded-lg border bg-white p-3">
                <p className="text-sm font-semibold">{selectedReadiness.label}</p>
                <p className="text-xs text-gray-600">Completion: {selectedReadiness.completionPercent}%</p>
                {hasTriedGenerate && !selectedReadiness.ready && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {(selectedReadiness.missingFields || []).map((field) => (
                      <Tooltip key={field.key}>
                        <TooltipTrigger asChild>
                          <button type="button" className="text-left">
                            <Badge variant="outline" className="cursor-help">
                              {labels[field.key] || field.label}
                              <Info size={12} className="ml-1 text-slate-500" />
                            </Badge>
                          </button>
                        </TooltipTrigger>
                        <TooltipContent side="top" className="max-w-xs">
                          {helpText[field.key] || field.label}
                        </TooltipContent>
                      </Tooltip>
                    ))}
                  </div>
                )}
              </div>

              <Dialog open={showInputsDialog} onOpenChange={setShowInputsDialog}>
                <DialogContent className="max-w-3xl">
                  <DialogHeader>
                    <DialogTitle>Missing inputs - {selectedReadiness.label}</DialogTitle>
                  </DialogHeader>

                  <div className="max-h-[70vh] overflow-y-auto pr-1">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {(missingFields || []).map((field) => (
                        <div key={field.key} className={MULTILINE_KEYS.has(field.key) ? 'sm:col-span-2' : ''}>
                          <Label htmlFor={`missing-${field.key}`} className="flex items-center gap-1 flex-wrap">
                            <span>{labels[field.key] || field.label}</span>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <button
                                  type="button"
                                  className="inline-flex items-center rounded-full p-0.5 text-slate-500 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                                  aria-label={`Info: ${labels[field.key] || field.label}`}
                                >
                                  <Info size={14} />
                                </button>
                              </TooltipTrigger>
                              <TooltipContent side="top" className="max-w-xs">
                                {helpText[field.key] || field.label}
                              </TooltipContent>
                            </Tooltip>
                          </Label>

                          {MULTILINE_KEYS.has(field.key) ? (
                            <Textarea
                              id={`missing-${field.key}`}
                              value={formInputs[field.key] || ''}
                              onChange={(e) => setFormInputs((prev) => ({ ...prev, [field.key]: e.target.value }))}
                              rows={4}
                            />
                          ) : (
                            <Input
                              id={`missing-${field.key}`}
                              type={numberKeys.has(field.key) ? 'number' : 'text'}
                              value={formInputs[field.key] || ''}
                              onChange={(e) => setFormInputs((prev) => ({ ...prev, [field.key]: e.target.value }))}
                            />
                          )}
                        </div>
                      ))}
                    </div>

                    <div className="sticky bottom-0 mt-4 border-t bg-white/95 backdrop-blur p-3 flex justify-end">
                      <Button onClick={onSaveInputs} disabled={savingInputs} className="w-full sm:w-auto">
                        {savingInputs ? (
                          <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</>
                        ) : (
                          <><Save className="mr-2" size={14} />Save inputs</>
                        )}
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>

              <div className="flex flex-wrap gap-2">
                <Button onClick={onGenerate} disabled={generating} className="w-full sm:w-auto">
                  {generating ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Generating...</> : 'Generate Draft'}
                </Button>
                <Button variant="outline" onClick={loadEligibility} className="w-full sm:w-auto">
                  <RefreshCw size={14} className="mr-2" />
                  Refresh Readiness
                </Button>
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>

      {documentDraft && (
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <CardTitle>{documentDraft.title}</CardTitle>
                <CardDescription>
                  Version count: {documentDraft.versions?.length || 0} | Template: {documentDraft.templateVersion}
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => onExport('html')}>
                  <Download size={14} className="mr-2" />
                  Export HTML
                </Button>
                <Button variant="outline" onClick={() => onExport('text')}>
                  <Download size={14} className="mr-2" />
                  Export Text
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {(documentDraft.sections || []).map((section) => (
              <div key={section.id} className="rounded-lg border p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <p className="font-semibold text-sm">{section.title}</p>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onRegenerateSection(section.id)}
                    disabled={regeneratingSection === section.id}
                  >
                    {regeneratingSection === section.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <RefreshCw size={12} />}
                  </Button>
                </div>
                <Textarea
                  value={section.content || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    setDocumentDraft((prev) => ({
                      ...prev,
                      sections: (prev.sections || []).map((s) => (s.id === section.id ? { ...s, content: value } : s)),
                    }));
                  }}
                  rows={4}
                />
                <Button
                  size="sm"
                  onClick={() => onUpdateSection(section.id, section.content || '')}
                  disabled={savingSection === section.id}
                >
                  {savingSection === section.id ? <><Loader2 className="mr-2 h-3 w-3 animate-spin" />Saving...</> : 'Save section'}
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
      </div>
    </TooltipProvider>
  );
}
