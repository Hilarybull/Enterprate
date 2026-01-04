import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { 
  FlaskConical,
  Plus,
  Play,
  Pause,
  Trophy,
  BarChart3,
  Eye,
  Trash2,
  Loader2,
  CheckCircle2,
  Clock,
  Target,
  TrendingUp,
  Users,
  MousePointerClick,
  DollarSign,
  Activity
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const STATUS_COLORS = {
  draft: 'bg-gray-100 text-gray-700',
  running: 'bg-green-100 text-green-700',
  paused: 'bg-amber-100 text-amber-700',
  completed: 'bg-blue-100 text-blue-700'
};

const TEST_TYPES = [
  { value: 'campaign', label: 'Marketing Campaign' },
  { value: 'landing_page', label: 'Landing Page' },
  { value: 'email', label: 'Email Campaign' },
  { value: 'social_post', label: 'Social Post' },
  { value: 'cta', label: 'Call to Action' }
];

const GOAL_METRICS = [
  { value: 'conversion_rate', label: 'Conversion Rate', icon: Target },
  { value: 'click_rate', label: 'Click Rate', icon: MousePointerClick },
  { value: 'engagement', label: 'Engagement Rate', icon: Activity },
  { value: 'revenue', label: 'Revenue per Visitor', icon: DollarSign }
];

export default function ABTesting() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [loading, setLoading] = useState(true);
  const [tests, setTests] = useState([]);
  const [selectedTest, setSelectedTest] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [activeTab, setActiveTab] = useState('tests');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [creating, setCreating] = useState(false);
  
  // Create form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    testType: 'campaign',
    goalMetric: 'conversion_rate',
    durationDays: 14,
    variants: [
      { name: 'Control (A)', content: { headline: '', description: '' } },
      { name: 'Variant B', content: { headline: '', description: '' } }
    ]
  });

  const loadTests = useCallback(async () => {
    if (!currentWorkspace) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/ab-tests`, {
        headers: getHeaders()
      });
      setTests(response.data || []);
    } catch (error) {
      console.error('Failed to load A/B tests:', error);
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace, getHeaders]);

  useEffect(() => {
    loadTests();
  }, [loadTests]);

  const createTest = async () => {
    if (!formData.name.trim()) {
      toast.error('Please enter a test name');
      return;
    }
    
    setCreating(true);
    try {
      await axios.post(`${API_URL}/ab-tests`, {
        name: formData.name,
        description: formData.description,
        testType: formData.testType,
        variants: formData.variants,
        durationDays: formData.durationDays,
        goalMetric: formData.goalMetric
      }, { headers: getHeaders() });
      
      toast.success('A/B test created successfully!');
      setShowCreateDialog(false);
      setFormData({
        name: '',
        description: '',
        testType: 'campaign',
        goalMetric: 'conversion_rate',
        durationDays: 14,
        variants: [
          { name: 'Control (A)', content: { headline: '', description: '' } },
          { name: 'Variant B', content: { headline: '', description: '' } }
        ]
      });
      loadTests();
    } catch (error) {
      toast.error('Failed to create test');
    } finally {
      setCreating(false);
    }
  };

  const startTest = async (testId) => {
    try {
      await axios.post(`${API_URL}/ab-tests/${testId}/start`, {}, { headers: getHeaders() });
      toast.success('Test started!');
      loadTests();
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to start test');
    }
  };

  const pauseTest = async (testId) => {
    try {
      await axios.post(`${API_URL}/ab-tests/${testId}/pause`, {}, { headers: getHeaders() });
      toast.success('Test paused');
      loadTests();
    } catch (error) {
      toast.error('Failed to pause test');
    }
  };

  const resumeTest = async (testId) => {
    try {
      await axios.post(`${API_URL}/ab-tests/${testId}/resume`, {}, { headers: getHeaders() });
      toast.success('Test resumed');
      loadTests();
    } catch (error) {
      toast.error('Failed to resume test');
    }
  };

  const analyzeTest = async (test) => {
    setSelectedTest(test);
    setActiveTab('analysis');
    
    try {
      const response = await axios.get(`${API_URL}/ab-tests/${test.id}/analyze`, {
        headers: getHeaders()
      });
      setAnalysis(response.data);
    } catch (error) {
      toast.error('Failed to analyze test');
    }
  };

  const completeTest = async (testId, winnerId = null) => {
    try {
      await axios.post(`${API_URL}/ab-tests/${testId}/complete`, {}, {
        headers: getHeaders(),
        params: winnerId ? { winner_id: winnerId } : {}
      });
      toast.success('Test completed!');
      loadTests();
      if (selectedTest?.id === testId) {
        setSelectedTest(null);
        setAnalysis(null);
        setActiveTab('tests');
      }
    } catch (error) {
      toast.error('Failed to complete test');
    }
  };

  const deleteTest = async (testId) => {
    if (!window.confirm('Are you sure you want to delete this test?')) return;
    
    try {
      await axios.delete(`${API_URL}/ab-tests/${testId}`, { headers: getHeaders() });
      toast.success('Test deleted');
      loadTests();
      if (selectedTest?.id === testId) {
        setSelectedTest(null);
        setAnalysis(null);
        setActiveTab('tests');
      }
    } catch (error) {
      toast.error('Failed to delete test');
    }
  };

  const addVariant = () => {
    const letter = String.fromCharCode(65 + formData.variants.length);
    setFormData({
      ...formData,
      variants: [
        ...formData.variants,
        { name: `Variant ${letter}`, content: { headline: '', description: '' } }
      ]
    });
  };

  const updateVariant = (index, field, value) => {
    const newVariants = [...formData.variants];
    if (field === 'name') {
      newVariants[index].name = value;
    } else {
      newVariants[index].content[field] = value;
    }
    setFormData({ ...formData, variants: newVariants });
  };

  const removeVariant = (index) => {
    if (formData.variants.length <= 2) {
      toast.error('Minimum 2 variants required');
      return;
    }
    const newVariants = formData.variants.filter((_, i) => i !== index);
    setFormData({ ...formData, variants: newVariants });
  };

  const getStatusStats = () => {
    const stats = { draft: 0, running: 0, paused: 0, completed: 0 };
    tests.forEach(t => { stats[t.status] = (stats[t.status] || 0) + 1; });
    return stats;
  };

  const stats = getStatusStats();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="loading-spinner">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-slide-in" data-testid="ab-testing-page">
      <PageHeader
        icon={FlaskConical}
        title="A/B Testing"
        description="Create and analyze split tests to optimize your campaigns"
        actions={
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button className="gradient-primary border-0" data-testid="create-test-btn">
                <Plus className="mr-2" size={16} />
                Create Test
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create A/B Test</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Test Name</Label>
                    <Input
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="e.g., Homepage CTA Test"
                      className="mt-1.5"
                      data-testid="test-name-input"
                    />
                  </div>
                  <div>
                    <Label>Test Type</Label>
                    <Select value={formData.testType} onValueChange={(v) => setFormData({ ...formData, testType: v })}>
                      <SelectTrigger className="mt-1.5">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {TEST_TYPES.map(t => (
                          <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div>
                  <Label>Description</Label>
                  <Textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe what you're testing..."
                    className="mt-1.5"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Goal Metric</Label>
                    <Select value={formData.goalMetric} onValueChange={(v) => setFormData({ ...formData, goalMetric: v })}>
                      <SelectTrigger className="mt-1.5">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {GOAL_METRICS.map(m => (
                          <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Duration (Days)</Label>
                    <Input
                      type="number"
                      value={formData.durationDays}
                      onChange={(e) => setFormData({ ...formData, durationDays: parseInt(e.target.value) || 14 })}
                      min={1}
                      max={90}
                      className="mt-1.5"
                    />
                  </div>
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Label>Variants</Label>
                    <Button size="sm" variant="outline" onClick={addVariant}>
                      <Plus size={14} className="mr-1" /> Add Variant
                    </Button>
                  </div>
                  <div className="space-y-3">
                    {formData.variants.map((variant, index) => (
                      <Card key={index} className="p-3">
                        <div className="flex items-center justify-between mb-2">
                          <Input
                            value={variant.name}
                            onChange={(e) => updateVariant(index, 'name', e.target.value)}
                            className="w-40 h-8"
                          />
                          {index > 0 && (
                            <Button
                              size="sm"
                              variant="ghost"
                              className="text-red-500"
                              onClick={() => removeVariant(index)}
                            >
                              <Trash2 size={14} />
                            </Button>
                          )}
                          {index === 0 && <Badge variant="outline">Control</Badge>}
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <Input
                            placeholder="Headline"
                            value={variant.content.headline}
                            onChange={(e) => updateVariant(index, 'headline', e.target.value)}
                            className="text-sm"
                          />
                          <Input
                            placeholder="Description"
                            value={variant.content.description}
                            onChange={(e) => updateVariant(index, 'description', e.target.value)}
                            className="text-sm"
                          />
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>Cancel</Button>
                <Button onClick={createTest} disabled={creating} data-testid="submit-test-btn">
                  {creating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FlaskConical className="mr-2" size={16} />}
                  Create Test
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-100 rounded-lg">
                <FlaskConical className="text-gray-600" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.draft}</p>
                <p className="text-sm text-gray-500">Draft Tests</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Play className="text-green-600" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.running}</p>
                <p className="text-sm text-gray-500">Running</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-100 rounded-lg">
                <Pause className="text-amber-600" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.paused}</p>
                <p className="text-sm text-gray-500">Paused</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Trophy className="text-blue-600" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.completed}</p>
                <p className="text-sm text-gray-500">Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="tests" className="flex items-center gap-2">
            <FlaskConical size={16} />
            All Tests
          </TabsTrigger>
          <TabsTrigger value="analysis" className="flex items-center gap-2" disabled={!selectedTest}>
            <BarChart3 size={16} />
            Analysis
          </TabsTrigger>
        </TabsList>

        <TabsContent value="tests" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tests.map((test) => (
              <Card key={test.id} className="hover:shadow-md transition-shadow" data-testid={`test-card-${test.id}`}>
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-base">{test.name}</CardTitle>
                      <CardDescription className="text-xs mt-1">
                        {TEST_TYPES.find(t => t.value === test.testType)?.label || test.testType}
                      </CardDescription>
                    </div>
                    <Badge className={STATUS_COLORS[test.status]}>
                      {test.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 line-clamp-2 mb-3">{test.description}</p>
                  
                  <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
                    <span className="flex items-center gap-1">
                      <Users size={12} />
                      {test.variants?.length || 0} variants
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock size={12} />
                      {test.durationDays} days
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {test.status === 'draft' && (
                      <Button size="sm" onClick={() => startTest(test.id)} className="flex-1">
                        <Play size={14} className="mr-1" /> Start
                      </Button>
                    )}
                    {test.status === 'running' && (
                      <Button size="sm" variant="outline" onClick={() => pauseTest(test.id)} className="flex-1">
                        <Pause size={14} className="mr-1" /> Pause
                      </Button>
                    )}
                    {test.status === 'paused' && (
                      <Button size="sm" onClick={() => resumeTest(test.id)} className="flex-1">
                        <Play size={14} className="mr-1" /> Resume
                      </Button>
                    )}
                    <Button size="sm" variant="outline" onClick={() => analyzeTest(test)}>
                      <BarChart3 size={14} />
                    </Button>
                    <Button size="sm" variant="ghost" className="text-red-500" onClick={() => deleteTest(test.id)}>
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {tests.length === 0 && (
              <Card className="col-span-full p-12 text-center">
                <FlaskConical className="mx-auto text-gray-300 mb-4" size={48} />
                <h3 className="text-lg font-medium text-gray-700">No A/B Tests Yet</h3>
                <p className="text-gray-500 mt-1">Create your first A/B test to start optimizing</p>
                <Button className="mt-4" onClick={() => setShowCreateDialog(true)}>
                  <Plus className="mr-2" size={16} /> Create Your First Test
                </Button>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="analysis" className="mt-6">
          {selectedTest && analysis ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>{analysis.testName}</CardTitle>
                      <CardDescription>
                        Goal: {GOAL_METRICS.find(m => m.value === analysis.goalMetric)?.label}
                        {' • '}Total Impressions: {analysis.totalImpressions?.toLocaleString()}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={STATUS_COLORS[selectedTest.status]}>
                        {selectedTest.status}
                      </Badge>
                      {selectedTest.status !== 'completed' && (
                        <Button size="sm" onClick={() => completeTest(selectedTest.id, analysis.winner?.variantId)}>
                          <CheckCircle2 size={14} className="mr-1" /> End Test
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {analysis.results?.map((result, index) => {
                      const isWinner = analysis.winner?.variantId === result.variantId;
                      return (
                        <Card key={result.variantId} className={`${isWinner ? 'ring-2 ring-green-500 bg-green-50' : ''}`}>
                          <CardHeader className="pb-2">
                            <div className="flex items-center justify-between">
                              <CardTitle className="text-base">{result.variantName}</CardTitle>
                              <div className="flex gap-1">
                                {result.isControl && <Badge variant="outline">Control</Badge>}
                                {isWinner && (
                                  <Badge className="bg-green-100 text-green-700">
                                    <Trophy size={12} className="mr-1" /> Winner
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </CardHeader>
                          <CardContent className="space-y-3">
                            <div className="grid grid-cols-2 gap-3 text-sm">
                              <div>
                                <p className="text-gray-500">Impressions</p>
                                <p className="font-semibold">{result.metrics.impressions.toLocaleString()}</p>
                              </div>
                              <div>
                                <p className="text-gray-500">Clicks</p>
                                <p className="font-semibold">{result.metrics.clicks.toLocaleString()}</p>
                              </div>
                              <div>
                                <p className="text-gray-500">Conversions</p>
                                <p className="font-semibold">{result.metrics.conversions.toLocaleString()}</p>
                              </div>
                              <div>
                                <p className="text-gray-500">Revenue</p>
                                <p className="font-semibold">${result.metrics.revenue.toLocaleString()}</p>
                              </div>
                            </div>
                            
                            <div className="pt-2 border-t">
                              <div className="flex justify-between text-sm mb-1">
                                <span>Conversion Rate</span>
                                <span className="font-semibold">{result.rates.conversionRate}%</span>
                              </div>
                              <Progress value={result.rates.conversionRate} className="h-2" />
                            </div>
                            
                            <div>
                              <div className="flex justify-between text-sm mb-1">
                                <span>Click Rate</span>
                                <span className="font-semibold">{result.rates.clickRate}%</span>
                              </div>
                              <Progress value={result.rates.clickRate} className="h-2" />
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                  
                  {analysis.hasStatisticalSignificance ? (
                    <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="text-green-600" size={20} />
                        <span className="font-medium text-green-800">Statistical significance reached</span>
                      </div>
                      <p className="text-sm text-green-700 mt-1">
                        Results are statistically significant at 95% confidence level.
                      </p>
                    </div>
                  ) : (
                    <div className="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
                      <div className="flex items-center gap-2">
                        <Clock className="text-amber-600" size={20} />
                        <span className="font-medium text-amber-800">More data needed</span>
                      </div>
                      <p className="text-sm text-amber-700 mt-1">
                        Continue running the test to reach statistical significance (min. 100 impressions per variant).
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card className="p-12 text-center">
              <BarChart3 className="mx-auto text-gray-300 mb-4" size={48} />
              <h3 className="text-lg font-medium text-gray-700">No Test Selected</h3>
              <p className="text-gray-500 mt-1">Select a test from the list to view its analysis</p>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
