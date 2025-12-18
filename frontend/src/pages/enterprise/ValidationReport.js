import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  ArrowLeft, 
  CheckCircle, 
  XCircle, 
  Edit3,
  TrendingUp,
  Target,
  Users,
  DollarSign,
  Zap,
  Clock,
  BarChart3,
  MessageCircle,
  ExternalLink,
  ThumbsUp,
  ThumbsDown,
  Loader2,
  Info,
  Sparkles,
  Building,
  Globe,
  Hash
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// Score gauge component
const ScoreGauge = ({ value, maxValue = 10, label, description, color = "purple" }) => {
  const percentage = (value / maxValue) * 100;
  const colorClasses = {
    purple: "text-purple-600 bg-purple-100",
    green: "text-green-600 bg-green-100",
    blue: "text-blue-600 bg-blue-100",
    orange: "text-orange-600 bg-orange-100"
  };
  
  return (
    <div className={`p-4 rounded-xl ${colorClasses[color]} relative group`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium opacity-80">{label}</span>
        <Info className="w-4 h-4 opacity-50 cursor-help" />
      </div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-xs opacity-70 mt-1">{description}</div>
      {/* Tooltip on hover */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
        Score: {value}/{maxValue}
      </div>
    </div>
  );
};

// Business fit bar component
const BusinessFitBar = ({ label, score, maxScore = 10, description }) => (
  <div className="space-y-2">
    <div className="flex justify-between items-center">
      <span className="text-sm font-medium text-gray-700">{label}</span>
      <span className="text-sm font-bold text-purple-600">{score}/{maxScore}</span>
    </div>
    <Progress value={(score / maxScore) * 100} className="h-2" />
    <p className="text-xs text-gray-500">{description}</p>
  </div>
);

// Community signal component
const CommunitySignal = ({ platform, details, score }) => (
  <div className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
    <div>
      <span className="font-medium text-sm">{platform}</span>
      <p className="text-xs text-gray-500">{details}</p>
    </div>
    <Badge variant={score >= 7 ? "default" : "secondary"} className="ml-2">
      {score}/10
    </Badge>
  </div>
);

// Keyword card component
const KeywordCard = ({ keyword, volume, competition, growth }) => (
  <div className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
    <div className="flex-1 min-w-0">
      <p className="text-sm font-medium truncate">{keyword}</p>
      {competition && (
        <Badge variant="outline" className={`text-xs mt-1 ${
          competition === 'LOW' ? 'text-green-600' : 
          competition === 'HIGH' ? 'text-red-600' : 'text-yellow-600'
        }`}>
          {competition} competition
        </Badge>
      )}
    </div>
    <div className="text-right ml-2">
      <span className="font-bold text-purple-600">{volume}</span>
      {growth && <p className="text-xs text-green-600">{growth}</p>}
    </div>
  </div>
);

// Framework card component
const FrameworkCard = ({ name, scores, overallScore, description }) => (
  <Card className="h-full">
    <CardContent className="p-4">
      <h4 className="font-semibold text-sm mb-3">{name}</h4>
      {overallScore !== undefined && (
        <div className="flex items-center justify-center mb-3">
          <div className="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center">
            <span className="text-2xl font-bold text-purple-600">{overallScore}</span>
          </div>
        </div>
      )}
      {scores && scores.length > 0 && (
        <div className="space-y-2">
          {scores.map((s, i) => (
            <div key={i}>
              <div className="flex justify-between text-xs mb-1">
                <span>{s.name}</span>
                <span className="font-medium">{s.score}/{s.maxScore || 10}</span>
              </div>
              <Progress value={(s.score / (s.maxScore || 10)) * 100} className="h-1.5" />
            </div>
          ))}
        </div>
      )}
      {description && <p className="text-xs text-gray-500 mt-2">{description}</p>}
    </CardContent>
  </Card>
);

export default function ValidationReport() {
  const { reportId } = useParams();
  const navigate = useNavigate();
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (currentWorkspace && reportId) {
      fetchReport();
    }
  }, [currentWorkspace, reportId]);

  const fetchReport = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/validation-reports/${reportId}`,
        { headers: getHeaders() }
      );
      setReport(response.data);
    } catch (error) {
      toast.error('Failed to load report');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (status) => {
    setUpdating(true);
    try {
      await axios.put(
        `${API_URL}/validation-reports/${reportId}/status`,
        { status },
        { headers: getHeaders() }
      );
      setReport(prev => ({ ...prev, status }));
      toast.success(`Idea ${status === 'accepted' ? 'accepted' : 'rejected'}!`);
    } catch (error) {
      toast.error('Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const handleModify = () => {
    // Navigate to modification page with report data
    navigate(`/idea-discovery/modify/${reportId}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Report not found</p>
        <Button onClick={() => navigate('/idea-discovery')} className="mt-4">
          Back to Idea Discovery
        </Button>
      </div>
    );
  }

  const { report: r, ideaInput, status, createdAt } = report;
  const scores = r.scores || {};
  const overallScore = scores.opportunity?.value || 5;
  const verdict = overallScore >= 7 ? 'PASS' : overallScore >= 5 ? 'PIVOT' : 'KILL';

  return (
    <div className="space-y-6 animate-slide-in" data-testid="validation-report">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/idea-discovery')}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold">{r.title || ideaInput?.ideaName}</h1>
              <Badge variant={
                status === 'accepted' ? 'default' : 
                status === 'rejected' ? 'destructive' : 'secondary'
              }>
                {status?.toUpperCase()}
              </Badge>
            </div>
            <p className="text-gray-500 text-sm mt-1">
              {ideaInput?.ideaType?.toUpperCase()} • Created {new Date(createdAt).toLocaleDateString()}
            </p>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            onClick={handleModify}
            disabled={updating}
          >
            <Edit3 className="w-4 h-4 mr-2" />
            Modify
          </Button>
          <Button 
            variant={status === 'rejected' ? 'secondary' : 'destructive'}
            onClick={() => updateStatus('rejected')}
            disabled={updating || status === 'rejected'}
          >
            <ThumbsDown className="w-4 h-4 mr-2" />
            Reject
          </Button>
          <Button 
            className={status === 'accepted' ? '' : 'gradient-primary border-0'}
            onClick={() => updateStatus('accepted')}
            disabled={updating || status === 'accepted'}
          >
            <ThumbsUp className="w-4 h-4 mr-2" />
            Accept
          </Button>
        </div>
      </div>

      {/* Tags */}
      {r.tags && r.tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {r.tags.map((tag, i) => (
            <Badge key={i} variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
              <Sparkles className="w-3 h-3 mr-1" />
              {tag}
            </Badge>
          ))}
        </div>
      )}

      {/* Main Content - Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <Card>
            <CardContent className="p-6">
              <p className="text-gray-700 whitespace-pre-line">{r.description}</p>
              {r.disclaimer && (
                <p className="text-xs text-gray-400 mt-4 italic">{r.disclaimer}</p>
              )}
            </CardContent>
          </Card>

          {/* Trend Section */}
          {r.trendKeyword && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <TrendingUp className="w-5 h-5 mr-2 text-purple-600" />
                  Keyword Trend
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-xl">
                  <div>
                    <p className="text-sm text-gray-600">Keyword</p>
                    <p className="font-semibold">{r.trendKeyword}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-purple-600">{r.trendVolume}</p>
                    <p className="text-xs text-gray-500">Monthly Volume</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-green-600">{r.trendGrowth}</p>
                    <p className="text-xs text-gray-500">Growth</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Offer / Value Ladder */}
          {r.offer && r.offer.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <DollarSign className="w-5 h-5 mr-2 text-purple-600" />
                  Value Ladder
                </CardTitle>
                <CardDescription>Recommended pricing structure</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {r.offer.map((tier, i) => (
                    <div key={i} className="flex items-start p-4 bg-gray-50 rounded-lg">
                      <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold text-sm mr-4 flex-shrink-0">
                        {i + 1}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <Badge variant="outline" className="mb-1">{tier.tier}</Badge>
                            <h4 className="font-semibold">{tier.name}</h4>
                          </div>
                          <span className="font-bold text-purple-600">{tier.price}</span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{tier.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Content Sections */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {r.whyNow && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center">
                    <Clock className="w-4 h-4 mr-2 text-purple-600" />
                    Why Now?
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">{r.whyNow}</p>
                </CardContent>
              </Card>
            )}

            {r.proofSignals && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center">
                    <Zap className="w-4 h-4 mr-2 text-yellow-600" />
                    Proof & Signals
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">{r.proofSignals}</p>
                </CardContent>
              </Card>
            )}

            {r.marketGap && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center">
                    <Target className="w-4 h-4 mr-2 text-green-600" />
                    Market Gap
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">{r.marketGap}</p>
                </CardContent>
              </Card>
            )}

            {r.executionPlan && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center">
                    <FileText className="w-4 h-4 mr-2 text-blue-600" />
                    Execution Plan
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">{r.executionPlan}</p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Framework Fit */}
          {r.frameworkFit && r.frameworkFit.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <BarChart3 className="w-5 h-5 mr-2 text-purple-600" />
                  Framework Fit
                </CardTitle>
                <CardDescription>How this idea fits popular frameworks</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {r.frameworkFit.map((fw, i) => (
                    <FrameworkCard 
                      key={i}
                      name={fw.name}
                      scores={fw.scores}
                      overallScore={fw.overallScore}
                      description={fw.description}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column - Scores & Metrics */}
        <div className="space-y-6">
          {/* Verdict Card */}
          <Card className={`border-2 ${
            verdict === 'PASS' ? 'border-green-200 bg-green-50' :
            verdict === 'PIVOT' ? 'border-yellow-200 bg-yellow-50' :
            'border-red-200 bg-red-50'
          }`}>
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center mb-2">
                {verdict === 'PASS' ? (
                  <CheckCircle className="w-8 h-8 text-green-600" />
                ) : verdict === 'PIVOT' ? (
                  <TrendingUp className="w-8 h-8 text-yellow-600" />
                ) : (
                  <XCircle className="w-8 h-8 text-red-600" />
                )}
              </div>
              <h2 className={`text-3xl font-bold ${
                verdict === 'PASS' ? 'text-green-700' :
                verdict === 'PIVOT' ? 'text-yellow-700' :
                'text-red-700'
              }`}>{verdict}</h2>
              <p className="text-sm opacity-70 mt-1">
                {verdict === 'PASS' ? 'Strong potential - proceed with confidence' :
                 verdict === 'PIVOT' ? 'Moderate potential - consider adjustments' :
                 'High risk - significant changes needed'}
              </p>
            </CardContent>
          </Card>

          {/* AI Scores */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">AI Scores</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                <ScoreGauge 
                  value={scores.opportunity?.value || 5}
                  label="Opportunity"
                  description={scores.opportunity?.label || "Assessment"}
                  color="purple"
                />
                <ScoreGauge 
                  value={scores.problem?.value || 5}
                  label="Problem"
                  description={scores.problem?.label || "Assessment"}
                  color="blue"
                />
                <ScoreGauge 
                  value={scores.feasibility?.value || 5}
                  label="Feasibility"
                  description={scores.feasibility?.label || "Assessment"}
                  color="green"
                />
                <ScoreGauge 
                  value={scores.whyNow?.value || 5}
                  label="Why Now"
                  description={scores.whyNow?.label || "Assessment"}
                  color="orange"
                />
              </div>
            </CardContent>
          </Card>

          {/* Business Fit */}
          {r.businessFit && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center">
                  <Building className="w-4 h-4 mr-2" />
                  Business Fit
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {r.businessFit.revenuePotential && (
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium">Revenue Potential</p>
                      <p className="text-xs text-gray-500">{r.businessFit.revenuePotential.description}</p>
                    </div>
                    <span className="text-2xl font-bold text-green-600">
                      {r.businessFit.revenuePotential.indicator}
                    </span>
                  </div>
                )}
                
                {r.businessFit.executionDifficulty?.score && (
                  <BusinessFitBar 
                    label="Execution Difficulty"
                    score={r.businessFit.executionDifficulty.score}
                    description={r.businessFit.executionDifficulty.description}
                  />
                )}
                
                {r.businessFit.goToMarket?.score && (
                  <BusinessFitBar 
                    label="Go-To-Market"
                    score={r.businessFit.goToMarket.score}
                    description={r.businessFit.goToMarket.description}
                  />
                )}
              </CardContent>
            </Card>
          )}

          {/* Categorization */}
          {r.categorization && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center">
                  <Hash className="w-4 h-4 mr-2" />
                  Categorization
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Type</span>
                    <span className="font-medium">{r.categorization.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Market</span>
                    <span className="font-medium">{r.categorization.market}</span>
                  </div>
                  {r.categorization.target && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Target</span>
                      <span className="font-medium truncate ml-2">{r.categorization.target}</span>
                    </div>
                  )}
                </div>
                {r.categorization.trendAnalysis && (
                  <p className="text-xs text-gray-500 mt-3 p-2 bg-gray-50 rounded">
                    {r.categorization.trendAnalysis}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Community Signals */}
          {r.communitySignals && r.communitySignals.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center">
                  <Users className="w-4 h-4 mr-2" />
                  Community Signals
                </CardTitle>
              </CardHeader>
              <CardContent>
                {r.communitySignals.map((signal, i) => (
                  <CommunitySignal 
                    key={i}
                    platform={signal.platform}
                    details={signal.details}
                    score={signal.score}
                  />
                ))}
              </CardContent>
            </Card>
          )}

          {/* Top Keywords */}
          {r.topKeywords && r.topKeywords.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center">
                  <Globe className="w-4 h-4 mr-2" />
                  Top Keywords
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {r.topKeywords.map((kw, i) => (
                  <KeywordCard 
                    key={i}
                    keyword={kw.keyword}
                    volume={kw.volume}
                    competition={kw.competition}
                    growth={kw.growth}
                  />
                ))}
              </CardContent>
            </Card>
          )}

          {/* Build Prompts */}
          {r.buildPrompts && r.buildPrompts.length > 0 && (
            <Card className="bg-gradient-to-br from-purple-50 to-blue-50">
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center">
                  <Sparkles className="w-4 h-4 mr-2 text-purple-600" />
                  Start Building
                </CardTitle>
                <CardDescription>Pre-built prompts to get started</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {r.buildPrompts.map((prompt, i) => (
                    <Button 
                      key={i} 
                      variant="outline" 
                      className="w-full justify-start bg-white hover:bg-purple-50"
                      size="sm"
                    >
                      <ExternalLink className="w-3 h-3 mr-2" />
                      {prompt}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Suggested Questions */}
      {r.suggestedQuestions && r.suggestedQuestions.length > 0 && (
        <Card className="bg-gray-50">
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <MessageCircle className="w-5 h-5 mr-2 text-purple-600" />
              Get Instant Answers
            </CardTitle>
            <CardDescription>Ask anything about this business idea</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {r.suggestedQuestions.map((q, i) => (
                <Button 
                  key={i} 
                  variant="outline" 
                  className="justify-start text-left h-auto py-2 text-sm"
                  size="sm"
                >
                  {q}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Feedback Section */}
      <Card>
        <CardContent className="p-6">
          <div className="text-center">
            <h3 className="font-semibold mb-4">What do you think of this idea?</h3>
            <div className="flex justify-center space-x-4">
              <Button variant="outline" className="px-6">
                💎 Amazing
              </Button>
              <Button variant="outline" className="px-6">
                🤔 Pretty interesting
              </Button>
              <Button variant="outline" className="px-6">
                🔥 Needs work
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
