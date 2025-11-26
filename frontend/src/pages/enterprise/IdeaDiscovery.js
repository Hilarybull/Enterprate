import React, { useState } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { 
  Lightbulb, 
  Target, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle,
  Zap,
  BarChart3,
  Users,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function IdeaDiscovery() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [idea, setIdea] = useState('');
  const [targetCustomer, setTargetCustomer] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleScoreIdea = async (e) => {
    e.preventDefault();
    if (!currentWorkspace) {
      toast.error('Please select a workspace first');
      return;
    }
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_URL}/genesis/idea-score`,
        { idea, targetCustomer },
        { headers: getHeaders() }
      );
      setResult(response.data);
      toast.success('Idea analyzed successfully!');
    } catch (error) {
      toast.error('Failed to analyze idea');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreGradient = (score) => {
    if (score >= 80) return 'gradient-success';
    if (score >= 60) return 'gradient-warning';
    return 'gradient-danger';
  };

  return (
    <div className="space-y-8 animate-slide-in" data-testid="idea-discovery-page">
      <PageHeader
        icon={Lightbulb}
        title="Idea Discovery & Validation"
        description="Transform your ideas into validated business concepts with AI-powered analysis"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Form */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Describe Your Business Idea</CardTitle>
              <CardDescription>
                Provide details about your concept and our AI will analyze market viability, competition, and potential
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleScoreIdea} className="space-y-6">
                <div>
                  <Label htmlFor="idea" className="text-sm font-medium">
                    Business Idea *
                  </Label>
                  <Textarea
                    id="idea"
                    data-testid="idea-input"
                    placeholder="Describe your business idea in detail. What problem does it solve? How does it work? What makes it unique?"
                    value={idea}
                    onChange={(e) => setIdea(e.target.value)}
                    rows={6}
                    className="mt-1.5"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="target" className="text-sm font-medium">
                    Target Customer
                  </Label>
                  <Input
                    id="target"
                    data-testid="target-customer-input"
                    placeholder="e.g., Small business owners, Tech startups, Healthcare professionals"
                    value={targetCustomer}
                    onChange={(e) => setTargetCustomer(e.target.value)}
                    className="mt-1.5"
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full gradient-primary border-0"
                  disabled={loading || !idea.trim()}
                  data-testid="score-idea-btn"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Zap className="mr-2" size={18} />
                      Analyze My Idea
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Info Cards */}
        <div className="space-y-4">
          <FeatureCard
            title="AI-Powered Analysis"
            description="Deep market research and competitive analysis in seconds"
            icon={BarChart3}
            gradient="gradient-primary"
          />
          <FeatureCard
            title="Market Validation"
            description="Understand your target audience and market size"
            icon={Target}
            gradient="gradient-success"
          />
          <FeatureCard
            title="Growth Potential"
            description="Predict revenue opportunities and scaling strategies"
            icon={TrendingUp}
            gradient="gradient-warning"
          />
        </div>
      </div>

      {/* Results */}
      {result && (
        <Card className="border-2 border-purple-200" data-testid="idea-results">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl">Analysis Results</CardTitle>
                <CardDescription>Based on market data and AI analysis</CardDescription>
              </div>
              <div className={`w-20 h-20 rounded-2xl ${getScoreGradient(result.score)} flex items-center justify-center shadow-lg`}>
                <span className="text-white text-2xl font-bold">{result.score}</span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Score Breakdown */}
            <div>
              <h3 className="font-semibold mb-4 text-lg flex items-center">
                <BarChart3 className="mr-2 text-purple-600" size={20} />
                Score Breakdown
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(result.analysis || {}).map(([key, value]) => (
                  <div key={key} className="p-4 bg-gray-50 rounded-xl">
                    <div className="flex justify-between items-center mb-2">
                      <p className="text-sm font-medium text-gray-600 capitalize">
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </p>
                      <span className={`font-bold ${getScoreColor(value)}`}>{value}/100</span>
                    </div>
                    <Progress value={value} className="h-2" />
                  </div>
                ))}
              </div>
            </div>

            {/* Insights */}
            {result.insights && result.insights.length > 0 && (
              <div>
                <h3 className="font-semibold mb-4 text-lg flex items-center">
                  <CheckCircle className="mr-2 text-green-500" size={20} />
                  Key Insights
                </h3>
                <div className="space-y-2">
                  {result.insights.map((insight, index) => (
                    <div key={index} className="flex items-start p-3 bg-green-50 rounded-lg">
                      <CheckCircle className="text-green-500 mr-3 mt-0.5 flex-shrink-0" size={16} />
                      <span className="text-sm text-gray-700">{insight}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Next Steps */}
            {result.nextSteps && result.nextSteps.length > 0 && (
              <div>
                <h3 className="font-semibold mb-4 text-lg flex items-center">
                  <AlertCircle className="mr-2 text-orange-500" size={20} />
                  Recommended Next Steps
                </h3>
                <div className="space-y-2">
                  {result.nextSteps.map((step, index) => (
                    <div key={index} className="flex items-start p-3 bg-orange-50 rounded-lg">
                      <span className="font-bold text-orange-600 mr-3">{index + 1}.</span>
                      <span className="text-sm text-gray-700">{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
