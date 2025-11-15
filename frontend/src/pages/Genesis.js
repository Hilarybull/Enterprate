import React, { useState } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Lightbulb, Target, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function Genesis() {
  const { getHeaders } = useWorkspace();
  const [idea, setIdea] = useState('');
  const [targetCustomer, setTargetCustomer] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleScoreIdea = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_URL}/genesis/idea-score`,
        { idea, targetCustomer },
        { headers: getHeaders() }
      );
      setResult(response.data);
      toast.success('Idea scored successfully!');
    } catch (error) {
      toast.error('Failed to score idea');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-slide-in" data-testid="genesis-page">
      <div>
        <h1 className="text-3xl font-bold mb-2 flex items-center" style={{ fontFamily: 'Space Grotesk' }}>
          <Lightbulb className="mr-3 text-yellow-500" size={32} />
          Genesis AI
        </h1>
        <p className="text-gray-600">Transform your ideas into validated business concepts</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Form */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Idea Validation</CardTitle>
              <CardDescription>
                Describe your business idea and we'll provide AI-powered analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleScoreIdea} className="space-y-4">
                <div>
                  <Label htmlFor="idea">Your Business Idea</Label>
                  <Textarea
                    id="idea"
                    data-testid="idea-input"
                    placeholder="Describe your business idea in detail..."
                    value={idea}
                    onChange={(e) => setIdea(e.target.value)}
                    rows={6}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="target">Target Customer (Optional)</Label>
                  <Input
                    id="target"
                    data-testid="target-customer-input"
                    placeholder="e.g., Small business owners, Tech startups"
                    value={targetCustomer}
                    onChange={(e) => setTargetCustomer(e.target.value)}
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  disabled={loading}
                  data-testid="score-idea-btn"
                >
                  {loading ? 'Analyzing...' : 'Score My Idea'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Info Cards */}
        <div className="space-y-4">
          <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-none">
            <CardContent className="p-6">
              <Target className="text-blue-600 mb-3" size={24} />
              <h3 className="font-semibold mb-2">AI-Powered Analysis</h3>
              <p className="text-sm text-gray-600">
                Our Genesis AI evaluates market viability, competition, and revenue potential
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-none">
            <CardContent className="p-6">
              <TrendingUp className="text-green-600 mb-3" size={24} />
              <h3 className="font-semibold mb-2">Actionable Insights</h3>
              <p className="text-sm text-gray-600">
                Get concrete next steps and strategic recommendations
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Results */}
      {result && (
        <Card className="border-2 border-blue-200" data-testid="idea-results">
          <CardHeader>
            <CardTitle className="flex items-center">
              Idea Score: {result.score}/100
              <div className="ml-auto">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <span className="text-white text-xl font-bold">{result.score}</span>
                </div>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Analysis Breakdown */}
            <div>
              <h3 className="font-semibold mb-4 text-lg">Analysis Breakdown</h3>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(result.analysis).map(([key, value]) => (
                  <div key={key} className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">
                      {key.replace(/([A-Z])/g, ' $1').trim()}
                    </p>
                    <div className="flex items-center">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${value}%` }}
                        ></div>
                      </div>
                      <span className="font-semibold">{value}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Insights */}
            <div>
              <h3 className="font-semibold mb-3 text-lg flex items-center">
                <CheckCircle className="mr-2 text-green-500" size={20} />
                Key Insights
              </h3>
              <ul className="space-y-2">
                {result.insights.map((insight, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Next Steps */}
            <div>
              <h3 className="font-semibold mb-3 text-lg flex items-center">
                <AlertCircle className="mr-2 text-orange-500" size={20} />
                Recommended Next Steps
              </h3>
              <ol className="space-y-2">
                {result.nextSteps.map((step, index) => (
                  <li key={index} className="flex items-start">
                    <span className="font-semibold text-blue-600 mr-3">{index + 1}.</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
