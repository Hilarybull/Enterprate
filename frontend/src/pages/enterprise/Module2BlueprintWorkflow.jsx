import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Check, Download, Loader2, RefreshCw, Save } from 'lucide-react';

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

  const selectedReadiness = useMemo(() => {
    if (!eligibility) return null;
    const all = [...(eligibility.available || []), ...(eligibility.partial || []), ...(eligibility.missing || [])];
    return all.find((item) => item.documentType === selectedType) || null;
  }, [eligibility, selectedType]);

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
    } catch (error) {
      toast.error('Could not save inputs');
      console.error(error);
    } finally {
      setSavingInputs(false);
    }
  };

  const onGenerate = async () => {
    setGenerating(true);
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
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Blueprint Output Builder</CardTitle>
          <CardDescription>
            Generate your core business documents from your saved business data. Numbers come from your inputs; AI only improves wording and structure.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
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
                {!selectedReadiness.ready && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {(selectedReadiness.missingFields || []).map((field) => (
                      <Badge key={field.key} variant="outline">{field.label}</Badge>
                    ))}
                  </div>
                )}
              </div>

              {!selectedReadiness.ready && (
                <Card className="border-dashed">
                  <CardHeader>
                    <CardTitle className="text-base">Missing Inputs</CardTitle>
                    <CardDescription>Fill the fields below to unlock generation for this output.</CardDescription>
                  </CardHeader>
                  <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {(selectedReadiness.missingFields || []).map((field) => (
                      <div key={field.key} className={MULTILINE_KEYS.has(field.key) ? 'md:col-span-2' : ''}>
                        <Label htmlFor={field.key}>{labels[field.key] || field.label}</Label>
                        {MULTILINE_KEYS.has(field.key) ? (
                          <Textarea
                            id={field.key}
                            value={formInputs[field.key] || ''}
                            onChange={(e) => setFormInputs((prev) => ({ ...prev, [field.key]: e.target.value }))}
                            rows={3}
                          />
                        ) : (
                          <Input
                            id={field.key}
                            type={numberKeys.has(field.key) ? 'number' : 'text'}
                            value={formInputs[field.key] || ''}
                            onChange={(e) => setFormInputs((prev) => ({ ...prev, [field.key]: e.target.value }))}
                          />
                        )}
                      </div>
                    ))}
                    <div className="md:col-span-2">
                      <Button onClick={onSaveInputs} disabled={savingInputs}>
                        {savingInputs ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</> : <><Save className="mr-2" size={14} />Save Inputs</>}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              <div className="flex flex-wrap gap-2">
                <Button onClick={onGenerate} disabled={generating}>
                  {generating ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Generating...</> : 'Generate Draft'}
                </Button>
                <Button variant="outline" onClick={loadEligibility}>
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
  );
}
