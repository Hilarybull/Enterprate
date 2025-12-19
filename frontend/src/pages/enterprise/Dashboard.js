import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { useWorkspace } from '@/context/WorkspaceContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  LayoutDashboard, 
  Lightbulb, 
  FileText, 
  Users, 
  TrendingUp, 
  Globe,
  DollarSign,
  ArrowRight,
  Sparkles,
  CheckCircle,
  Building,
  Send,
  Mail,
  Share2,
  Receipt,
  ChevronUp,
  ChevronDown,
  List,
  HelpCircle,
  MessageCircle,
  Clock,
  Bell,
  Brain,
  Briefcase,
  Settings
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// Action Card Component matching Bolt design
const ActionCard = ({ icon: Icon, title, description, to, iconBg = "bg-purple-100", iconColor = "text-purple-600" }) => {
  const navigate = useNavigate();
  return (
    <Card className="group hover:shadow-lg transition-all duration-200 cursor-pointer border border-gray-100" onClick={() => navigate(to)}>
      <CardContent className="p-5">
        <div className={`w-12 h-12 rounded-xl ${iconBg} flex items-center justify-center mb-4`}>
          <Icon className={iconColor} size={24} />
        </div>
        <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
        <p className="text-sm text-gray-500 mb-3">{description}</p>
        <span className="text-purple-600 text-sm font-medium group-hover:underline inline-flex items-center">
          Get Started <ArrowRight size={14} className="ml-1" />
        </span>
      </CardContent>
    </Card>
  );
};

// Circular Progress Component
const CircularProgress = ({ percentage, stepsComplete, totalSteps }) => {
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-28 h-28">
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="56"
            cy="56"
            r={radius}
            stroke="#E5E7EB"
            strokeWidth="8"
            fill="none"
          />
          <circle
            cx="56"
            cy="56"
            r={radius}
            stroke="url(#progressGradient)"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-500"
          />
          <defs>
            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#8B5CF6" />
              <stop offset="100%" stopColor="#6366F1" />
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-gray-900">{percentage}%</span>
        </div>
      </div>
      <p className="text-sm text-gray-500 mt-2">{stepsComplete} of {totalSteps} steps complete</p>
    </div>
  );
};

// Wizard Companion Component
const WizardCompanion = ({ currentStep, totalSteps, stepTitle, stepDescription, onContinue }) => {
  const [expanded, setExpanded] = useState(true);
  
  return (
    <div className="bg-purple-50 rounded-xl p-4 border border-purple-100">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
            <Sparkles className="text-purple-600" size={20} />
          </div>
          <div>
            <h4 className="font-semibold text-gray-900">Wizard Companion</h4>
            <p className="text-xs text-gray-500">I'll guide you step-by-step</p>
          </div>
        </div>
        <button onClick={() => setExpanded(!expanded)} className="text-gray-400 hover:text-gray-600">
          {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>
      </div>
      
      {expanded && (
        <>
          <div className="mb-3">
            <span className="text-xs font-semibold text-purple-600 uppercase">
              NEXT STEP {currentStep} OF {totalSteps}
            </span>
          </div>
          <h5 className="font-semibold text-gray-900 mb-2">{stepTitle}</h5>
          <p className="text-sm text-gray-600 mb-4">{stepDescription}</p>
          <Button 
            onClick={onContinue}
            className="w-full gradient-primary border-0 text-white"
          >
            Continue <ArrowRight size={16} className="ml-2" />
          </Button>
          <button className="w-full mt-3 flex items-center justify-center text-sm text-purple-600 hover:underline">
            <List size={14} className="mr-2" />
            View all steps
          </button>
        </>
      )}
    </div>
  );
};

// Notification Item Component
const NotificationItem = ({ icon: Icon, iconBg, title, subtitle, timestamp }) => (
  <div className="flex items-start space-x-3 py-3 border-b border-gray-100 last:border-0">
    <div className={`w-8 h-8 rounded-full ${iconBg} flex items-center justify-center flex-shrink-0`}>
      <Icon size={14} className="text-white" />
    </div>
    <div className="flex-1 min-w-0">
      <p className="font-medium text-sm text-gray-900">{title}</p>
      {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
    </div>
    <span className="text-xs text-gray-400 flex-shrink-0">{timestamp}</span>
  </div>
);

// AI Coach Advice Card
const AdviceCard = ({ title, content, timestamp }) => (
  <div className="p-4 bg-white rounded-lg border border-gray-100">
    <div className="flex items-start space-x-3">
      <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
        <MessageCircle size={14} className="text-purple-600" />
      </div>
      <div className="flex-1">
        <h5 className="font-medium text-sm text-gray-900">{title}</h5>
        <p className="text-xs text-gray-500 mt-1">{content}</p>
        <span className="text-xs text-gray-400 mt-2 block">{timestamp}</span>
      </div>
    </div>
  </div>
);

export default function Dashboard() {
  const navigate = useNavigate();
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [stats, setStats] = useState({
    genesisProjects: 0,
    invoices: 0,
    unpaidInvoices: 0,
    leads: 0,
    websites: 0,
    validations: 0
  });
  const [recentEvents, setRecentEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aiQuestion, setAiQuestion] = useState('');
  const [wizardStep, setWizardStep] = useState(4);
  const totalSteps = 8;

  // Calculate progress percentage
  const progressPercentage = Math.round((wizardStep - 1) / totalSteps * 100);

  useEffect(() => {
    if (currentWorkspace) {
      loadDashboardData();
    } else {
      setLoading(false);
    }
  }, [currentWorkspace]);

  const loadDashboardData = async () => {
    try {
      const headers = getHeaders();

      // Load projects
      const projectsRes = await axios.get(
        `${API_URL}/workspaces/${currentWorkspace.id}/projects`,
        { headers }
      );
      const genesisProjects = projectsRes.data.filter(p => p.type === 'GENESIS');

      // Load invoices
      const invoicesRes = await axios.get(`${API_URL}/navigator/invoices`, { headers });
      const unpaid = invoicesRes.data.filter(inv => inv.status !== 'PAID' && inv.status !== 'CANCELLED');

      // Load leads
      const leadsRes = await axios.get(`${API_URL}/growth/leads`, { headers });

      // Load websites
      const websitesRes = await axios.get(`${API_URL}/websites`, { headers });

      // Load recent events
      const eventsRes = await axios.get(`${API_URL}/intel/events?limit=5`, { headers });

      // Load validation engagement
      try {
        const engagementRes = await axios.get(`${API_URL}/validation-reports/engagement`, { headers });
        setStats(prev => ({
          ...prev,
          validations: engagementRes.data.totalValidations
        }));
      } catch (e) {}

      setStats(prev => ({
        ...prev,
        genesisProjects: genesisProjects.length,
        invoices: invoicesRes.data.length,
        unpaidInvoices: unpaid.length,
        leads: leadsRes.data.length,
        websites: websitesRes.data?.length || 0
      }));

      setRecentEvents(eventsRes.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAiQuestion = async () => {
    if (!aiQuestion.trim()) return;
    toast.info('AI Coach feature coming soon!');
    setAiQuestion('');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (!currentWorkspace) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="no-workspace">
        <Card className="max-w-md">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center mx-auto mb-4">
              <LayoutDashboard className="text-white" size={28} />
            </div>
            <h2 className="text-2xl font-bold mb-2">No Workspace Selected</h2>
            <p className="text-gray-600 mb-4">
              Please create a workspace to get started using Enterprate OS.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="animate-slide-in" data-testid="dashboard">
      {/* Main Content Grid - Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column - Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-500">Your business launch and operations hub</p>
            </div>
            <Button 
              className="gradient-primary border-0"
              onClick={() => navigate('/idea-discovery')}
            >
              Continue Journey <ArrowRight size={16} className="ml-2" />
            </Button>
          </div>

          {/* Action Cards Grid - 2x3 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ActionCard
              icon={CheckCircle}
              title="Validate my idea"
              description="Score ideas, get customer persona"
              to="/idea-discovery"
              iconBg="bg-purple-100"
              iconColor="text-purple-600"
            />
            <ActionCard
              icon={FileText}
              title="Register my business"
              description="LLC, Corp, or nonprofit formation"
              to="/business-registration"
              iconBg="bg-blue-100"
              iconColor="text-blue-600"
            />
            <ActionCard
              icon={Briefcase}
              title="Run my company"
              description="Contracts, compliance, ops"
              to="/business-operations"
              iconBg="bg-blue-100"
              iconColor="text-blue-600"
            />
            <ActionCard
              icon={Mail}
              title="Send Email AI Agent"
              description="Auto-draft and send emails"
              to="/growth"
              iconBg="bg-purple-100"
              iconColor="text-purple-600"
            />
            <ActionCard
              icon={Share2}
              title="Social Media Post AI Agent"
              description="Generate and schedule posts"
              to="/growth"
              iconBg="bg-teal-100"
              iconColor="text-teal-600"
            />
            <ActionCard
              icon={Receipt}
              title="Invoice Agent"
              description="Create and track invoices"
              to="/finance-automation"
              iconBg="bg-purple-100"
              iconColor="text-purple-600"
            />
          </div>

          {/* Market Watch Card */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-base">
                <TrendingUp className="mr-2 text-purple-600" size={18} />
                Market watch – General Markets
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">S&P 500:</span>
                  <div className="flex items-center">
                    <span className="font-semibold">$491.68</span>
                    <TrendingUp size={14} className="ml-1 text-green-500" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Dow Jones:</span>
                  <div className="flex items-center">
                    <span className="font-semibold">$393.49</span>
                    <TrendingUp size={14} className="ml-1 text-green-500" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">NASDAQ:</span>
                  <div className="flex items-center">
                    <span className="font-semibold">$421.32</span>
                    <TrendingUp size={14} className="ml-1 text-green-500" />
                  </div>
                </div>
              </div>
              <p className="text-xs text-gray-400 mt-2">just now</p>
            </CardContent>
          </Card>

          {/* AI Business Coach */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-base">
                <Brain className="mr-2 text-purple-600" size={18} />
                AI Business Coach
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Today's Focus */}
              <div className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-semibold text-sm text-gray-900 mb-3">Today's Focus</h4>
                <div className="space-y-2">
                  {[
                    "Run comprehensive validation to get SWOT, demand metrics, risks, and UVP",
                    "Choose your business entity type and begin formation",
                    "Create your customized operating agreement"
                  ].map((item, i) => (
                    <div key={i} className="flex items-start space-x-2">
                      <CheckCircle size={16} className="text-purple-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Ask AI Coach */}
              <div>
                <h4 className="font-semibold text-sm text-gray-900 mb-2">Ask the AI Coach</h4>
                <div className="flex space-x-2">
                  <Input
                    placeholder="Ask anything about your business..."
                    value={aiQuestion}
                    onChange={(e) => setAiQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAiQuestion()}
                    className="flex-1"
                  />
                  <Button onClick={handleAiQuestion} className="gradient-primary border-0 px-3">
                    <Send size={16} />
                  </Button>
                </div>
              </div>

              {/* Recent Advice */}
              <div>
                <h4 className="font-semibold text-sm text-gray-900 mb-2">Recent Advice</h4>
                <div className="space-y-2">
                  <AdviceCard
                    title="What's next in my journey?"
                    content='Complete "Validate Idea (All-in-One)" - Run comprehensive validation to get SWOT, demand metrics, risks, and UVP'
                    timestamp="Just now"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Quick Insights */}
        <div className="space-y-6">
          {/* Business Setup Progress */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Business Setup Progress</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center py-4">
              <CircularProgress 
                percentage={progressPercentage} 
                stepsComplete={wizardStep - 1} 
                totalSteps={totalSteps} 
              />
            </CardContent>
          </Card>

          {/* Next Best Action */}
          <Card className="border-purple-200">
            <CardContent className="p-4">
              <span className="text-xs font-semibold text-purple-600 uppercase">NEXT BEST ACTION</span>
              <h4 className="font-semibold text-gray-900 mt-2 mb-1">Validate Idea (All-in-One)</h4>
              <p className="text-sm text-gray-500 mb-3">
                Run comprehensive validation to get SWOT, demand metrics, risks, and UVP
              </p>
              <Button 
                className="w-full gradient-primary border-0"
                onClick={() => navigate('/idea-discovery')}
              >
                Continue <ArrowRight size={16} className="ml-2" />
              </Button>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-base">
                <Bell className="mr-2 text-purple-600" size={16} />
                Notifications
              </CardTitle>
            </CardHeader>
            <CardContent>
              <NotificationItem
                icon={DollarSign}
                iconBg="bg-green-500"
                title="Due invoices"
                subtitle={`${stats.unpaidInvoices} pending`}
                timestamp="just now"
              />
              <NotificationItem
                icon={TrendingUp}
                iconBg="bg-gray-400"
                title="No cash flow activity last week"
                timestamp="just now"
              />
              <NotificationItem
                icon={Globe}
                iconBg="bg-blue-500"
                title="Market watch - General"
                subtitle="Markets are up today"
                timestamp="1h ago"
              />
            </CardContent>
          </Card>

          {/* Quick Insights / Wizard Companion */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Quick Insights</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <WizardCompanion
                currentStep={wizardStep}
                totalSteps={totalSteps}
                stepTitle="Validate Idea (All-in-One)"
                stepDescription="Run comprehensive validation to get SWOT, demand metrics, risks, and UVP"
                onContinue={() => navigate('/idea-discovery')}
              />

              {/* Suggestions */}
              <div>
                <h5 className="text-xs font-semibold text-gray-500 uppercase mb-2">SUGGESTIONS</h5>
                <ul className="space-y-1 text-sm text-gray-700">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    Describe your idea in one sentence
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    Identify your target customer
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    Run validation to get SWOT, demand, risks, and UVP
                  </li>
                </ul>
              </div>

              {/* Quick Actions */}
              <div>
                <h5 className="text-xs font-semibold text-gray-500 uppercase mb-2">QUICK ACTIONS</h5>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => navigate('/dashboard')}>
                    Dashboard
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => {
                    setWizardStep(1);
                    toast.success('Journey reset!');
                  }}>
                    Reset Journey
                  </Button>
                </div>
              </div>

              {/* Help Link */}
              <div className="text-center">
                <button className="text-sm text-gray-400 hover:text-gray-600 inline-flex items-center">
                  <HelpCircle size={14} className="mr-1" />
                  Need help?
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
