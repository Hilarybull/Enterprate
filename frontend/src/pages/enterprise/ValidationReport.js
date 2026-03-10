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
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
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
const JOURNEY_STORAGE_KEY = 'enterprate_journey_progress';
const IDEA_STORAGE_KEY = 'enterprate_last_validated_idea';

const MetricInfoTip = ({ text }) => (
  <Tooltip delayDuration={150}>
    <TooltipTrigger asChild>
      <button
        type="button"
        className="inline-flex items-center justify-center rounded-full text-gray-400 transition-colors hover:text-gray-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-400/60"
        aria-label="Metric info"
      >
        <Info className="w-3.5 h-3.5" />
      </button>
    </TooltipTrigger>
    <TooltipContent side="top" className="max-w-64 text-[11px] leading-relaxed">
      {text}
    </TooltipContent>
  </Tooltip>
);

// Score gauge component
const ScoreGauge = ({ value, label, subtitle, infoText, color = "purple" }) => {
  const colorClasses = {
    purple: "text-purple-600 bg-purple-100",
    green: "text-green-600 bg-green-100",
    blue: "text-blue-600 bg-blue-100",
    orange: "text-orange-600 bg-orange-100"
  };
  
  return (
    <div className={`p-4 rounded-xl border border-white/70 shadow-sm ${colorClasses[color]} relative group`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium opacity-80 inline-flex items-center gap-1.5">
          {label}
          <MetricInfoTip text={infoText || reason || `Score from ${label.toLowerCase()} factors.`} />
        </span>
      </div>
      <div className="text-2xl md:text-3xl font-bold">{value}</div>
      <div className="text-xs opacity-70 mt-1">{subtitle}</div>
    </div>
  );
};

// Business fit bar component
const BusinessFitBar = ({ label, score, maxScore = 10, description, infoText }) => (
  <div className="space-y-2">
    <div className="flex justify-between items-center">
      <span className="text-sm font-medium text-gray-700 inline-flex items-center gap-1.5">
        {label}
        <MetricInfoTip text={infoText || description} />
      </span>
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
      <span className="font-medium text-sm inline-flex items-center gap-1.5">
        {platform}
        <MetricInfoTip text="Community signal score reflects live relevance and activity strength on this platform for your context." />
      </span>
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
      <p className="text-sm font-medium truncate inline-flex items-center gap-1.5">
        {keyword}
        <MetricInfoTip text="Keyword used for search-demand signal in your selected market." />
      </p>
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
      <span className="font-bold text-purple-600 inline-flex items-center gap-1.5">
        {volume}
        <MetricInfoTip text="Estimated monthly search volume for this keyword." />
      </span>
      {growth && <p className="text-xs text-green-600">{growth}</p>}
    </div>
  </div>
);

// Framework card component
const FrameworkCard = ({ name, scores, overallScore, description }) => (
  <Card className="h-full">
    <CardContent className="p-4">
      <h4 className="font-semibold text-sm mb-3 inline-flex items-center gap-1.5">
        {name}
        <MetricInfoTip text="Framework-based view of how strongly this idea fits practical launch principles." />
      </h4>
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
  const [proofLevel, setProofLevel] = useState('none');
  const [proofCount, setProofCount] = useState(0);
  const [showAllDimensions, setShowAllDimensions] = useState(false);
  const [showAllOffer, setShowAllOffer] = useState(false);

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

      if (status === 'accepted') {
        const acceptedAt = new Date().toISOString();

        // Persist accepted idea input so it can be reused in dashboard/onboarding.
        localStorage.setItem(IDEA_STORAGE_KEY, JSON.stringify({
          reportId,
          acceptedAt,
          ideaInput: report?.ideaInput || null
        }));

        // Move business journey forward after validation acceptance.
        localStorage.setItem(JOURNEY_STORAGE_KEY, JSON.stringify({
          wizardStep: 5,
          updatedAt: acceptedAt
        }));
      }

      toast.success(`Idea ${status === 'accepted' ? 'accepted' : 'rejected'}!`);

      if (status === 'accepted') {
        navigate('/dashboard');
      }
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
  const deterministic = r.deterministicSummary;
  const overallScore = scores.opportunity?.value || 5;
  const verdict = overallScore >= 7 ? 'PASS' : overallScore >= 5 ? 'PIVOT' : 'KILL';
  const getCurrencyFromLocation = (location) => {
    const loc = (location || '').toLowerCase();
    if (loc.includes('uk') || loc.includes('united kingdom') || loc.includes('england') || loc.includes('scotland') || loc.includes('wales')) {
      return { code: 'GBP', locale: 'en-GB' };
    }
    if (loc.includes('us') || loc.includes('usa') || loc.includes('united states') || loc.includes('america')) {
      return { code: 'USD', locale: 'en-US' };
    }
    if (loc.includes('euro') || loc.includes('germany') || loc.includes('france') || loc.includes('italy') || loc.includes('spain') || loc.includes('netherlands')) {
      return { code: 'EUR', locale: 'de-DE' };
    }
    return { code: 'USD', locale: 'en-US' };
  };
  const reportCurrency = getCurrencyFromLocation(ideaInput?.targetLocation);
  const formatCurrency = (value) => {
    if (value === null || value === undefined) return `${reportCurrency.code} 0.00`;
    return new Intl.NumberFormat(reportCurrency.locale, { style: 'currency', currency: reportCurrency.code }).format(value);
  };
  const getBreakEvenDisplay = () => {
    const val = deterministic?.metrics?.breakEvenRevenue;
    if (val !== null && val !== undefined) return formatCurrency(val);
    return 'Set price above variable cost';
  };
  const getRunwayDisplay = () => {
    const val = deterministic?.metrics?.runwayMonths;
    if (val !== null && val !== undefined) return `${val}`;
    if ((deterministic?.metrics?.monthlyNet ?? 0) >= 0) return 'Not needed yet';
    return 'Add cash buffer value';
  };
  const getCapacityDisplay = () => {
    const v = deterministic?.metrics?.capacityFeasible;
    if (v === true) return 'Yes';
    if (v === false) return 'No';
    return 'Add staffing inputs';
  };
  const dimensionLabels = {
    D1_marginStrength: 'Margin Strength',
    D2_demandRealism: 'Demand Realism',
    D3_capacityFeasibility: 'Capacity Feasibility',
    D4_fixedCostImpact: 'Fixed Cost Impact',
    D5_paymentTermsImpact: 'Payment Terms Impact',
    D6_diversificationBenefit: 'Diversification Benefit',
    D7_proofStrength: 'Proof Strength'
  };
  const dimensionScores = deterministic?.scoreBreakdown?.dimensionScores || {};
  const baselineMetricInfo = {
    monthlyRevenue: 'Expected top-line monthly income. Calculated as expected units multiplied by unit price.',
    monthlyNet: 'Monthly profit or loss. Calculated as revenue minus variable costs and fixed costs.',
    contributionMarginPct: 'Share of revenue left after variable delivery costs. Formula: (revenue - variable costs) / revenue.',
    breakEvenRevenue: 'Minimum monthly revenue needed to stop losing money, using fixed costs and unit contribution.',
    capacityFeasible: 'Checks whether expected monthly demand fits current delivery capacity.',
    runwayMonths: 'How long current cash can sustain losses when monthly net is negative.'
  };
  const dimensionReason = {
    D1_marginStrength: 'Based on contribution margin percentage from your revenue and variable cost assumptions.',
    D2_demandRealism: 'Based on expected units/customers adjusted by current demand signal in your market context.',
    D3_capacityFeasibility: 'Based on utilisation versus available monthly delivery capacity.',
    D4_fixedCostImpact: 'Based on the fixed-cost-to-revenue ratio and cost rigidity risk.',
    D5_paymentTermsImpact: 'Based on payment terms and sales cycle effects on cashflow timing.',
    D6_diversificationBenefit: 'Based on channel spread and customer concentration resilience.',
    D7_proofStrength: 'Based on how much real proof/evidence exists in the structured input.',
  };
  const dimensionValueReason = (key, value) => {
    const n = Number(value || 0);
    const band = n >= 75 ? 'strong' : n >= 55 ? 'moderate' : 'weak';
    const map = {
      D1_marginStrength: {
        strong: 'Strong margin headroom from your current price and cost assumptions.',
        moderate: 'Margin is usable but leaves limited room for growth or shocks.',
        weak: 'Margin is thin; pricing or variable cost needs immediate adjustment.'
      },
      D2_demandRealism: {
        strong: 'Demand assumptions align well with available market signal strength.',
        moderate: 'Demand is plausible but still needs tighter early validation.',
        weak: 'Demand assumptions look optimistic versus current demand signals.'
      },
      D3_capacityFeasibility: {
        strong: 'Current team capacity can support expected monthly delivery volume.',
        moderate: 'Capacity is close to the limit and may constrain consistent delivery.',
        weak: 'Expected demand exceeds delivery capacity with current staffing.'
      },
      D4_fixedCostImpact: {
        strong: 'Fixed cost load is healthy relative to projected monthly revenue.',
        moderate: 'Fixed costs are manageable but could pressure net performance.',
        weak: 'Fixed costs are too heavy for current revenue assumptions.'
      },
      D5_paymentTermsImpact: {
        strong: 'Payment timing supports stable cashflow and lower financing pressure.',
        moderate: 'Payment timing is acceptable but can still create cashflow lag.',
        weak: 'Payment terms and cycle length create high cashflow pressure.'
      },
      D6_diversificationBenefit: {
        strong: 'Revenue risk is better spread across channels and customer sources.',
        moderate: 'Some diversification exists, but concentration risk remains.',
        weak: 'Revenue depends too heavily on narrow channels or few customers.'
      },
      D7_proofStrength: {
        strong: 'There is strong external proof supporting demand and buyer intent.',
        moderate: 'Some proof exists, but more evidence is needed before scaling.',
        weak: 'Evidence is limited; stronger proof is needed before confident rollout.'
      }
    };
    return map[key]?.[band] || 'Based on deterministic rubric inputs.';
  };
  const classification = deterministic?.classification;
  const reasonCodes = Array.isArray(deterministic?.reasonCodes) ? deterministic.reasonCodes : [];
  const reasonCodeDetails = {
    CAPACITY_MISMATCH: {
      title: 'Capacity Mismatch',
      why: 'Demand is higher than current delivery capacity.',
      action: 'Increase delivery capacity or reduce demand assumptions before launch.'
    },
    LOW_MARGIN: {
      title: 'Low Margin',
      why: 'Contribution margin is too low for safe scaling.',
      action: 'Increase price or reduce variable costs.'
    },
    NEGATIVE_MONTHLY_NET: {
      title: 'Negative Monthly Net',
      why: 'The current model loses money monthly.',
      action: 'Reduce fixed costs or increase revenue per customer.'
    },
    LONG_PAYMENT_TERMS: {
      title: 'Long Payment Terms',
      why: 'Cash takes too long to come back into the business.',
      action: 'Use shorter payment terms or partial upfront payment.'
    },
    LONG_SALES_CYCLE: {
      title: 'Long Sales Cycle',
      why: 'Customer acquisition takes too long.',
      action: 'Simplify offer and use faster-converting channels.'
    },
    CUSTOMER_CONCENTRATION_RISK: {
      title: 'Customer Concentration Risk',
      why: 'Too much revenue depends on too few customers.',
      action: 'Diversify customer base and reduce single-client dependence.'
    },
    LOW_PROOF_STRENGTH: {
      title: 'Low Proof Strength',
      why: 'Not enough real-world proof yet.',
      action: 'Add customer interviews, pilots, and early conversion evidence.'
    },
    WEAK_EXTERNAL_CONTEXT: {
      title: 'Weak External Context',
      why: 'Market/macro conditions are currently less supportive.',
      action: 'Tighten unit economics and focus on narrower segments.'
    }
  };
  const reasonItems = reasonCodes.map((code) => ({
    code,
    ...(reasonCodeDetails[code] || {
      title: String(code).replaceAll('_', ' '),
      why: 'Risk detected by scoring policy.',
      action: 'Review assumptions and tighten execution plan.'
    })
  }));
  const topImprovements = [
    ...(Array.isArray(deterministic?.recommendations) ? deterministic.recommendations : []),
    ...reasonItems.map((r) => r.action)
  ].filter(Boolean).slice(0, 3);
  const blendWeights = deterministic?.scoreBreakdown?.blendWeights || {};
  const externalCapPct = Math.round((blendWeights.externalContext || 0) * 100);
  const coreModelPct = Math.round((blendWeights.coreModel || 0) * 100);
  const externalMarketPct = Math.round(((blendWeights.externalSplit?.market || 0) * (blendWeights.externalContext || 0)) * 100);
  const externalMacroPct = Math.round(((blendWeights.externalSplit?.macro || 0) * (blendWeights.externalContext || 0)) * 100);
  const classView = (() => {
    const cls = classification || verdict;
    if (cls === 'Highly Robust' || cls === 'Strong' || cls === 'PASS') {
      return { tone: 'green', headline: cls, note: 'Proceed with controlled execution.' };
    }
    if (cls === 'Moderate' || cls === 'PIVOT') {
      return { tone: 'yellow', headline: cls, note: 'Viable with adjustments before scaling.' };
    }
    return { tone: 'red', headline: cls, note: 'Address major risks before launch.' };
  })();
  const scenarioResults = (() => {
    const m = deterministic?.metrics || {};
    const revenue = Number(m.monthlyRevenue || 0);
    const variable = Number(m.monthlyVariableCost || 0);
    const fixed = Number(m.monthlyFixedCost || 0);
    const capacityTotal = Number(m.capacityTotalUnits || 0);
    const units = Number(ideaInput?.expectedUnitsPerMonth || 0);
    const salesCycleDays = Number(ideaInput?.salesCycleDays || 0);

    const run = (id, label, r, v, f, capacityDelta = 0, extraPenalty = 0) => {
      const net = r - v - f;
      const newCapacity = capacityTotal > 0 ? capacityTotal + capacityDelta : 0;
      const capOk = newCapacity > 0 ? units <= newCapacity : null;
      const adjustedNet = net - (extraPenalty > 0 ? (fixed * extraPenalty) / 100 : 0);
      return { id, label, net: adjustedNet, capOk };
    };

    return [
      run('hire', 'Hire or contract (+15% fixed, +20% capacity)', revenue, variable, fixed * 1.15, Math.round(capacityTotal * 0.2)),
      run('revDown', 'Revenue -20%', revenue * 0.8, variable * 0.8, fixed),
      run('costUp', 'Costs +10%', revenue, variable * 1.1, fixed),
      run('delay14', 'Payment delay +14 days', revenue, variable, fixed, 0, salesCycleDays > 30 ? 6 : 4),
      run('priceUp', 'Price +10%', revenue * 1.1, variable, fixed),
      run('loseTop', 'Lose top client (approx -35% revenue)', revenue * 0.65, variable * 0.65, fixed),
    ];
  })();
  const d7Current = Number(dimensionScores.D7_proofStrength || 0);
  const visibleOffer = showAllOffer ? (r.offer || []) : (r.offer || []).slice(0, 2);
  const proofLevelPoints = proofLevel === 'basic' ? 8 : proofLevel === 'moderate' ? 15 : proofLevel === 'strong' ? 25 : 0;
  const proofCountPoints = Math.min(20, Number(proofCount || 0) * 2);
  const d7Projected = Math.min(100, d7Current + proofLevelPoints + proofCountPoints);
  const d7Delta = d7Projected - d7Current;
  const scoreImpactEstimate = Math.round(d7Delta * 0.09);
  const proofSimulationActive = proofLevel !== 'none' || Number(proofCount || 0) > 0;
  const simulatedDimensionScores = {
    ...dimensionScores,
    D7_proofStrength: proofSimulationActive ? d7Projected : d7Current,
  };
  const dimensionRows = Object.entries(simulatedDimensionScores);
  const visibleDimensionRows = showAllDimensions ? dimensionRows : dimensionRows.slice(0, 4);
  const simulatedValidationScore = Math.max(
    0,
    Math.min(100, Number(deterministic?.validationScore || 0) + (proofSimulationActive ? scoreImpactEstimate : 0))
  );
  const askInstantQuestion = (question) => {
    const contextPayload = {
      ideaInput: report?.ideaInput || {},
      report: report?.report || {}
    };
    window.dispatchEvent(new CustomEvent('enterprate:ask-ai', {
      detail: { message: question, autoSend: true, context: contextPayload }
    }));
  };

  return (
    <TooltipProvider>
    <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-6 py-3 space-y-4 animate-slide-in" data-testid="validation-report">
      {/* Header */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex items-start space-x-3 sm:space-x-4 min-w-0">
          <Button variant="ghost" size="icon" onClick={() => navigate('/idea-discovery')}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
              <h1 className="text-xl sm:text-2xl font-bold truncate">{r.title || ideaInput?.ideaName}</h1>
              <Badge variant={
                status === 'accepted' ? 'default' : 
                status === 'rejected' ? 'destructive' : 'secondary'
              }>
                {status?.toUpperCase()}
              </Badge>
            </div>
            <p className="text-gray-500 text-xs sm:text-sm mt-1">
              {ideaInput?.ideaType?.toUpperCase()} • Created {new Date(createdAt).toLocaleDateString()}
            </p>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="grid grid-cols-3 gap-2 sm:flex sm:flex-wrap sm:justify-end">
          <Button 
            variant="outline" 
            onClick={handleModify}
            disabled={updating}
            className="w-full sm:w-auto"
          >
            <Edit3 className="w-4 h-4 mr-2" />
            Modify
          </Button>
          <Button 
            variant={status === 'rejected' ? 'secondary' : 'destructive'}
            onClick={() => updateStatus('rejected')}
            disabled={updating || status === 'rejected'}
            className="w-full sm:w-auto"
          >
            <ThumbsDown className="w-4 h-4 mr-2" />
            Reject
          </Button>
          <Button 
            className={`w-full sm:w-auto ${status === 'accepted' ? '' : 'gradient-primary border-0'}`}
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
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-3 xl:gap-4">
        {/* Left Column - Main Content */}
        <div className="xl:col-span-8 space-y-3 xl:space-y-4">
          {/* Deterministic Baseline */}
	          {deterministic?.metrics && (
	            <Card className="border-purple-200 bg-purple-50/40 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center justify-between text-lg">
                  <span>Deterministic Baseline Model</span>
                  <Badge className="gradient-primary border-0">
                    Score {proofSimulationActive ? simulatedValidationScore : (deterministic.validationScore ?? 0)}/100
                  </Badge>
                </CardTitle>
                <CardDescription>Unit economics and feasibility from your structured assumptions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3 text-sm">
                  <div className="p-3 bg-white rounded-lg border">
                    <p className="text-gray-500 inline-flex items-center gap-1.5">Monthly Revenue <MetricInfoTip text={baselineMetricInfo.monthlyRevenue} /></p>
                    <p className="font-semibold">{formatCurrency(deterministic.metrics.monthlyRevenue)}</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg border">
                    <p className="text-gray-500 inline-flex items-center gap-1.5">Monthly Net <MetricInfoTip text={baselineMetricInfo.monthlyNet} /></p>
                    <p className={`font-semibold ${deterministic.metrics.monthlyNet >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                      {formatCurrency(deterministic.metrics.monthlyNet)}
                    </p>
                  </div>
                  <div className="p-3 bg-white rounded-lg border">
                    <p className="text-gray-500 inline-flex items-center gap-1.5">Contribution Margin <MetricInfoTip text={baselineMetricInfo.contributionMarginPct} /></p>
                    <p className="font-semibold">{deterministic.metrics.contributionMarginPct ?? 0}%</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg border">
                    <p className="text-gray-500 inline-flex items-center gap-1.5">Break-even Revenue <MetricInfoTip text={baselineMetricInfo.breakEvenRevenue} /></p>
                    <p className="font-semibold">{getBreakEvenDisplay()}</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg border">
                    <p className="text-gray-500 inline-flex items-center gap-1.5">Capacity Feasible <MetricInfoTip text={baselineMetricInfo.capacityFeasible} /></p>
                    <p className="font-semibold">{getCapacityDisplay()}</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg border">
                    <p className="text-gray-500 inline-flex items-center gap-1.5">Runway (months) <MetricInfoTip text={baselineMetricInfo.runwayMonths} /></p>
                    <p className="font-semibold">{getRunwayDisplay()}</p>
                  </div>
                </div>
                {dimensionRows.length > 0 && (
                  <div className="p-4 bg-white rounded-lg border">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                      <h4 className="font-semibold text-sm inline-flex items-center gap-1.5">
                        Dimension Breakdown
                        <MetricInfoTip text="Seven deterministic dimensions scored 0-100. Higher values indicate stronger business readiness for that dimension." />
                      </h4>
                      {classification && (
                        <Badge variant="outline" className="text-xs">{classification}</Badge>
                      )}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {visibleDimensionRows.map(([key, value]) => (
                        <div key={key} className="p-3 border rounded-md bg-gray-50/70 h-full">
                          <div className="grid grid-cols-[1fr_auto] gap-3 items-start">
                            <span className="text-sm text-gray-700 inline-flex items-center gap-1.5">
                              {dimensionLabels[key] || key}
                              <MetricInfoTip text={dimensionReason[key] || 'Based on deterministic rubric inputs.'} />
                            </span>
                            <span className="text-sm font-semibold text-purple-700">{value}/100</span>
                          </div>
                          <p className="text-[11px] text-gray-600 mt-2 leading-relaxed">Why this value: {dimensionValueReason(key, value)}</p>
                        </div>
                      ))}
                    </div>
                    {dimensionRows.length > 4 && (
                      <div className="mt-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-7 px-2 text-xs"
                          onClick={() => setShowAllDimensions((v) => !v)}
                        >
                          {showAllDimensions ? 'Show less' : `Show all (${dimensionRows.length})`}
                        </Button>
                      </div>
                    )}
                  </div>
                )}
                {Array.isArray(deterministic.flags) && deterministic.flags.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-sm mb-2">Flags</h4>
                    <ul className="space-y-1 text-sm text-gray-700">
                      {deterministic.flags.map((flag, idx) => (
                        <li key={idx}>• {flag}</li>
                      ))}
                    </ul>
                  </div>
                )}
	                {Array.isArray(deterministic.recommendations) && deterministic.recommendations.length > 0 && (
	                  <div>
	                    <h4 className="font-semibold text-sm mb-2">What To Change</h4>
                    <ul className="space-y-1 text-sm text-gray-700">
                      {deterministic.recommendations.map((rec, idx) => (
                        <li key={idx}>• {rec}</li>
                      ))}
                    </ul>
	                  </div>
	                )}
                  {reasonItems.length > 0 && (
                    <div className="p-4 bg-white rounded-lg border">
                      <h4 className="font-semibold text-sm mb-2 inline-flex items-center gap-1.5">
                        Reasons
                        <MetricInfoTip text="Triggered risk reasons from deterministic scoring, with what each one means in plain language." />
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                        {reasonItems.map((item, idx) => (
                          <div key={`${item.code}-${idx}`} className="text-sm p-2.5 rounded-md bg-gray-50 border">
                            <p className="font-medium text-gray-800 inline-flex items-center gap-1.5">
                              {item.title}
                              <Badge variant="outline" className="text-[10px]">
                                {String(item.code).replaceAll('_', ' ')}
                              </Badge>
                            </p>
                            <p className="text-gray-600">{item.why}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {topImprovements.length > 0 && (
                    <div className="p-4 bg-white rounded-lg border">
                      <h4 className="font-semibold text-sm mb-2 inline-flex items-center gap-1.5">
                        Top 3 Improvements
                        <MetricInfoTip text="Highest-priority changes that most improve model quality and launch readiness." />
                      </h4>
                      <ol className="space-y-2 text-sm text-gray-700 list-decimal pl-5">
                        {topImprovements.map((item, idx) => (
                          <li key={`improve-${idx}`}>{item}</li>
                        ))}
                      </ol>
                    </div>
                  )}
	              </CardContent>
	            </Card>
	          )}

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
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:items-center bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-xl">
                  <div>
                    <p className="text-sm text-gray-600 inline-flex items-center gap-1.5">Keyword <MetricInfoTip text="Primary search query used to estimate demand trend for this idea context." /></p>
                    <p className="font-semibold">{r.trendKeyword}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-purple-600">{r.trendVolume}</p>
                    <p className="text-xs text-gray-500 inline-flex items-center gap-1.5">Monthly Volume <MetricInfoTip text="Estimated monthly searches for the selected keyword in the selected market." /></p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-green-600">{r.trendGrowth}</p>
                    <p className="text-xs text-gray-500 inline-flex items-center gap-1.5">Growth <MetricInfoTip text="Relative trend direction for the keyword compared with its recent baseline." /></p>
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
                  <span className="ml-1"><MetricInfoTip text="Suggested offer tiers from entry to premium, aligned with your pricing model and demand assumptions." /></span>
                </CardTitle>
                <CardDescription>Recommended pricing structure</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {visibleOffer.map((tier, i) => (
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
                {r.offer.length > 2 && (
                  <div className="mt-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-7 px-2 text-xs"
                      onClick={() => setShowAllOffer((v) => !v)}
                    >
                      {showAllOffer ? 'Show fewer tiers' : `Show all tiers (${r.offer.length})`}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {(r.whyNow || r.proofSignals || r.marketGap || r.executionPlan) && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Strategic Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue={r.whyNow ? 'whyNow' : r.proofSignals ? 'proof' : r.marketGap ? 'gap' : 'plan'}>
                  <TabsList className="grid w-full grid-cols-2 md:grid-cols-4 h-auto">
                    {r.whyNow && <TabsTrigger value="whyNow">Why Now</TabsTrigger>}
                    {r.proofSignals && <TabsTrigger value="proof">Proof</TabsTrigger>}
                    {r.marketGap && <TabsTrigger value="gap">Market Gap</TabsTrigger>}
                    {r.executionPlan && <TabsTrigger value="plan">Execution</TabsTrigger>}
                  </TabsList>
                  {r.whyNow && (
                    <TabsContent value="whyNow" className="mt-3">
                      <p className="text-sm text-gray-600">{r.whyNow}</p>
                    </TabsContent>
                  )}
                  {r.proofSignals && (
                    <TabsContent value="proof" className="mt-3">
                      <p className="text-sm text-gray-600">{r.proofSignals}</p>
                    </TabsContent>
                  )}
                  {r.marketGap && (
                    <TabsContent value="gap" className="mt-3">
                      <p className="text-sm text-gray-600">{r.marketGap}</p>
                    </TabsContent>
                  )}
                  {r.executionPlan && (
                    <TabsContent value="plan" className="mt-3">
                      <p className="text-sm text-gray-600">{r.executionPlan}</p>
                    </TabsContent>
                  )}
                </Tabs>
              </CardContent>
            </Card>
          )}

            {/* Scenario Simulation */}
            {scenarioResults.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg inline-flex items-center gap-1.5">
                    Decision Simulation (v0.1)
                    <MetricInfoTip text="Scenario stress test on monthly model values. Each scenario adjusts assumptions, then recalculates monthly net and capacity fit." />
                  </CardTitle>
                  <CardDescription>Test key monthly scenarios before launch using monthly revenue, cost, and capacity assumptions.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {scenarioResults.map((s) => (
                      <div key={s.id} className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-2 md:gap-3 items-start md:items-center p-2 rounded border">
                        <span className="text-sm text-gray-700">{s.label}</span>
                        <span className={`text-sm font-semibold inline-flex items-center gap-1.5 ${s.net >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                          Monthly Net {formatCurrency(s.net)}
                          <MetricInfoTip text="Formula: Monthly Net = Monthly Revenue - Monthly Variable Costs - Monthly Fixed Costs after scenario adjustment." />
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Proof Strength Panel */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg inline-flex items-center gap-1.5">
                  Proof Strength
                  <MetricInfoTip text="Evidence quality score driver: stronger proof means higher confidence in demand assumptions and lower launch risk." />
                </CardTitle>
                <CardDescription>Add evidence to improve confidence in demand realism.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm font-medium text-gray-700 inline-flex items-center gap-1.5">Proof Level <MetricInfoTip text="Quality of evidence available: interviews, pilot signals, or paid validation." /></label>
                    <select
                      className="mt-1 w-full border rounded-md p-2 text-sm"
                      value={proofLevel}
                      onChange={(e) => setProofLevel(e.target.value)}
                    >
                      <option value="none">None</option>
                      <option value="basic">Basic (interviews)</option>
                      <option value="moderate">Moderate (pilot interest)</option>
                      <option value="strong">Strong (paid validation)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700 inline-flex items-center gap-1.5">Proof Count <MetricInfoTip text="Number of credible proof artifacts available, used to project confidence improvement." /></label>
                    <input
                      type="number"
                      min="0"
                      className="mt-1 w-full border rounded-md p-2 text-sm"
                      value={proofCount}
                      onChange={(e) => setProofCount(Math.max(0, Number(e.target.value || 0)))}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                  <div className="p-2 border rounded">
                    <p className="text-gray-500 inline-flex items-center gap-1.5">Current Proof Score <MetricInfoTip text="Current evidence strength score from the deterministic model." /></p>
                    <p className="font-semibold">{d7Current}/100</p>
                  </div>
                  <div className="p-2 border rounded">
                    <p className="text-gray-500 inline-flex items-center gap-1.5">Projected Proof Score <MetricInfoTip text="Estimated proof score after adding the selected level and count of evidence." /></p>
                    <p className="font-semibold">{d7Projected}/100</p>
                  </div>
                  <div className="p-2 border rounded">
                    <p className="text-gray-500 inline-flex items-center gap-1.5">Estimated Score Impact <MetricInfoTip text="Estimated uplift on total validation score from proof improvement only." /></p>
                    <p className="font-semibold">{scoreImpactEstimate >= 0 ? '+' : ''}{scoreImpactEstimate} pts</p>
                  </div>
                </div>
              </CardContent>
            </Card>
	
	          {/* Framework Fit */}
	          {r.frameworkFit && r.frameworkFit.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <BarChart3 className="w-5 h-5 mr-2 text-purple-600" />
                  Framework Fit
                  <span className="ml-1"><MetricInfoTip text="How this idea maps to launch frameworks using structured inputs and deterministic scoring." /></span>
                </CardTitle>
                <CardDescription>How this idea fits popular frameworks</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
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
        <div className="xl:col-span-4 space-y-3 xl:space-y-4 xl:sticky xl:top-20 self-start">
	          {/* Classification Card */}
	          <Card className={`border-2 ${
	            classView.tone === 'green' ? 'border-green-200 bg-green-50' :
	            classView.tone === 'yellow' ? 'border-yellow-200 bg-yellow-50' :
	            'border-red-200 bg-red-50'
	          }`}>
	            <CardContent className="p-6 text-center">
	              <div className="flex items-center justify-center mb-2">
	                {classView.tone === 'green' ? (
	                  <CheckCircle className="w-8 h-8 text-green-600" />
	                ) : classView.tone === 'yellow' ? (
	                  <TrendingUp className="w-8 h-8 text-yellow-600" />
	                ) : (
	                  <XCircle className="w-8 h-8 text-red-600" />
	                )}
	              </div>
	              <h2 className={`text-3xl font-bold ${
	                classView.tone === 'green' ? 'text-green-700' :
	                classView.tone === 'yellow' ? 'text-yellow-700' :
	                'text-red-700'
	              }`}>{classView.headline}</h2>
	              <p className="text-sm opacity-70 mt-1">
	                {classView.note}
	              </p>
                <p className="text-xs text-gray-600 mt-2 inline-flex items-center gap-1.5">
                  Validation Score {proofSimulationActive ? simulatedValidationScore : (deterministic?.validationScore ?? 0)}/100
                  <MetricInfoTip text="Overall deterministic score from weighted dimensions D1-D7 with capped external context influence." />
                </p>
                {proofSimulationActive && (
                  <p className="text-[11px] text-purple-700 mt-1">Preview includes proof simulation.</p>
                )}
	            </CardContent>
	          </Card>

            {/* External Context Influence */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">External Context Influence</CardTitle>
                <CardDescription>Market and macro impact is capped by policy.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-gray-600 inline-flex items-center gap-1.5">Core model weight <MetricInfoTip text="Percent of total score driven by your business inputs and unit economics." /></span><span className="font-semibold">{coreModelPct || 90}%</span></div>
                <div className="flex justify-between"><span className="text-gray-600 inline-flex items-center gap-1.5">External cap <MetricInfoTip text="Maximum percent of score allowed from external market and macro context." /></span><span className="font-semibold">{externalCapPct || 10}%</span></div>
                <div className="flex justify-between"><span className="text-gray-600 inline-flex items-center gap-1.5">Market share of total <MetricInfoTip text="Actual portion of total score assigned to market signal data." /></span><span className="font-semibold">{externalMarketPct || 6}%</span></div>
                <div className="flex justify-between"><span className="text-gray-600 inline-flex items-center gap-1.5">Macro share of total <MetricInfoTip text="Actual portion of total score assigned to macroeconomic context data." /></span><span className="font-semibold">{externalMacroPct || 4}%</span></div>
              </CardContent>
            </Card>

          {/* Validation Scores */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base inline-flex items-center gap-1.5">Validation Scores <MetricInfoTip text="Core outcome scores (0-10) summarizing opportunity, problem clarity, feasibility, and timing." /></CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <ScoreGauge 
                  value={scores.opportunity?.value || 5}
                  label="Opportunity"
                  subtitle={scores.opportunity?.label || "Assessment"}
                  infoText="Opportunity score estimates overall business upside based on economics quality, demand realism, and external context."
                  color="purple"
                />
                <ScoreGauge 
                  value={scores.problem?.value || 5}
                  label="Problem"
                  subtitle={scores.problem?.label || "Assessment"}
                  infoText="Problem score reflects clarity of pain, urgency, and how frequently the issue occurs for the target audience."
                  color="blue"
                />
                <ScoreGauge 
                  value={scores.feasibility?.value || 5}
                  label="Feasibility"
                  subtitle={scores.feasibility?.label || "Assessment"}
                  infoText="Feasibility score reflects execution practicality using capacity, delivery complexity, and operating assumptions."
                  color="green"
                />
                <ScoreGauge 
                  value={scores.whyNow?.value || 5}
                  label="Why Now"
                  subtitle={scores.whyNow?.label || "Assessment"}
                  infoText="Why Now score reflects timing strength based on urgency, market pressure, and current commercial conditions."
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
                      <p className="text-sm font-medium inline-flex items-center gap-1.5">Revenue Potential <MetricInfoTip text="Band estimate of earning potential from projected revenue level and net position." /></p>
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
                    infoText="Execution difficulty is scored from complexity, capacity fit, and operational risk in delivery."
                  />
                )}
                
                {r.businessFit.goToMarket?.score && (
                  <BusinessFitBar 
                    label="Go-To-Market"
                    score={r.businessFit.goToMarket.score}
                    description={r.businessFit.goToMarket.description}
                    infoText="Go-to-market score reflects channel readiness, acquisition pressure, and expected conversion friction."
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
                  <span className="ml-1"><MetricInfoTip text="Classification of this idea by type, market model, and target segment inferred from your structured inputs." /></span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500 inline-flex items-center gap-1.5">Type <MetricInfoTip text="Delivery archetype such as SaaS, marketplace, service, or hybrid." /></span>
                    <span className="font-medium">{r.categorization.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 inline-flex items-center gap-1.5">Market <MetricInfoTip text="Commercial model context such as B2C, B2B, or mixed audience profile." /></span>
                    <span className="font-medium">{r.categorization.market}</span>
                  </div>
                  {r.categorization.target && (
                    <div className="flex justify-between">
                      <span className="text-gray-500 inline-flex items-center gap-1.5">Target <MetricInfoTip text="Primary audience group inferred from your target audience and market context." /></span>
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
        <Card className="bg-gray-50 border border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <MessageCircle className="w-5 h-5 mr-2 text-purple-600" />
              Get Instant Answers
            </CardTitle>
            <CardDescription>Ask anything about this business idea</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                  {r.suggestedQuestions.map((q, i) => (
                    <Button 
                      key={i} 
                      variant="outline" 
                      className="justify-start text-left h-auto py-2 text-sm"
                      size="sm"
                      onClick={() => askInstantQuestion(q)}
                    >
                      {q}
                    </Button>
                  ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Feedback Section */}
      <Card className="border border-gray-200">
        <CardContent className="p-6">
          <div className="text-center">
            <h3 className="font-semibold mb-4">What do you think of this idea?</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-4">
              <Button variant="outline" className="px-4 sm:px-6">
                Excellent
              </Button>
              <Button variant="outline" className="px-4 sm:px-6">
                Interesting
              </Button>
              <Button variant="outline" className="px-4 sm:px-6">
                Needs Work
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
    </TooltipProvider>
  );
}






