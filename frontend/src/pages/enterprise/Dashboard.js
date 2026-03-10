import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useWorkspace } from '@/context/WorkspaceContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  LayoutDashboard,
  FileText,
  Users,
  TrendingUp,
  Globe,
  DollarSign,
  ArrowRight,
  CheckCircle,
  Send,
  Receipt,
  HelpCircle,
  MessageCircle,
  Bell,
  Brain,
  Settings
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';
const JOURNEY_STORAGE_KEY = 'enterprate_journey_progress';
const IDEA_STORAGE_KEY = 'enterprate_last_validated_idea';

// Action Card Component matching Bolt design
const ActionCard = ({
  icon: Icon,
  title,
  description,
  to,
  ctaLabel = "Get Started",
  iconBg = "bg-purple-100",
  iconColor = "text-purple-600"
}) => {
  const navigate = useNavigate();
  return (
    <Card className="group h-full hover:shadow-lg transition-all duration-200 cursor-pointer border border-gray-100" onClick={() => navigate(to)}>
      <CardContent className="p-5 h-full flex flex-col">
        <div className={`w-12 h-12 rounded-xl ${iconBg} flex items-center justify-center mb-4`}>
          <Icon className={iconColor} size={24} />
        </div>
        <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-500 min-h-[52px]">{description}</p>
        <span className="mt-auto pt-4 text-purple-600 text-sm font-medium group-hover:underline inline-flex items-center">
          {ctaLabel} <ArrowRight size={14} className="ml-1" />
        </span>
      </CardContent>
    </Card>
  );
};

// Notification Item Component
const NotificationItem = ({ icon: Icon, iconBg, title, subtitle, timestamp }) => (
  <div className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-0">
    <div className={`w-8 h-8 rounded-full ${iconBg} flex items-center justify-center flex-shrink-0`}>
      <Icon size={14} className="text-white" />
    </div>
    <div className="flex-1 min-w-0">
      <p className="font-medium text-sm text-gray-900">{title}</p>
      {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
    </div>
    <span className="text-xs text-gray-400 shrink-0 hidden sm:block">{timestamp}</span>
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
  const [loading, setLoading] = useState(true);
  const [aiQuestion, setAiQuestion] = useState('');
  const [wizardStep, setWizardStep] = useState(4);
  const [acceptedReportId, setAcceptedReportId] = useState(null);
  const hasCompletedValidation = wizardStep >= 5;

  useEffect(() => {
    const savedJourney = localStorage.getItem(JOURNEY_STORAGE_KEY);
    if (savedJourney) {
      try {
        const parsed = JSON.parse(savedJourney);
        if (parsed?.wizardStep && Number.isFinite(parsed.wizardStep)) {
          setWizardStep(Math.max(1, Math.min(8, parsed.wizardStep)));
        }
      } catch (e) {
        console.error('Failed to load saved journey progress');
      }
    }
  }, []);

  useEffect(() => {
    const savedIdea = localStorage.getItem(IDEA_STORAGE_KEY);
    if (!savedIdea) return;
    try {
      const parsed = JSON.parse(savedIdea);
      if (parsed?.reportId) {
        setAcceptedReportId(parsed.reportId);
      }
    } catch (e) {
      console.error('Failed to load accepted idea state');
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(JOURNEY_STORAGE_KEY, JSON.stringify({
      wizardStep
    }));
  }, [wizardStep]);

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

      // Load validation engagement
      try {
        const engagementRes = await axios.get(`${API_URL}/validation-reports/engagement`, { headers });
        if ((engagementRes.data?.acceptedCount || 0) > 0) {
          setWizardStep(prev => Math.max(prev, 5));
          if (!acceptedReportId) {
            const reportsRes = await axios.get(`${API_URL}/validation-reports?limit=50`, { headers });
            const latestAccepted = (reportsRes.data || []).find((r) => r.status === 'accepted');
            if (latestAccepted?.id) {
              setAcceptedReportId(latestAccepted.id);
              localStorage.setItem(IDEA_STORAGE_KEY, JSON.stringify({
                reportId: latestAccepted.id
              }));
            }
          }
        }
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
              Please create a workspace to get started using EnterprateAI.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="animate-slide-in" data-testid="dashboard">
      {/* Main Content Grid - Two Column Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,2.1fr)_minmax(320px,1fr)] gap-6">
        
        {/* Left Column - Main Content */}
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-500">Your business launch and operations hub</p>
            </div>
          </div>

          {/* Action Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 2xl:grid-cols-3 auto-rows-fr gap-4">
            <ActionCard
              icon={CheckCircle}
              title="Validate my idea"
              description={hasCompletedValidation ? "Modify accepted idea or create a new one" : "Score ideas, get customer persona"}
              to={hasCompletedValidation && acceptedReportId ? `/idea-discovery/modify/${acceptedReportId}` : "/idea-discovery"}
              ctaLabel={hasCompletedValidation ? "Modify Accepted Idea" : "Start Validation"}
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
              icon={Settings}
              title="Run my business"
              description="Manage daily operations and keep your business moving"
              to="/business-blueprint"
              ctaLabel="Open Operations"
              iconBg="bg-amber-100"
              iconColor="text-amber-600"
            />
            <ActionCard
              icon={Receipt}
              title="Finance & Invoicing"
              description="Manage invoices, expenses & tax"
              to="/finance-automation"
              iconBg="bg-green-100"
              iconColor="text-green-600"
            />
            <ActionCard
              icon={Users}
              title="Team Collaboration"
              description="Invite teammates and manage shared workspaces"
              to="/team"
              iconBg="bg-indigo-100"
              iconColor="text-indigo-600"
            />
            <ActionCard
              icon={Globe}
              title="Resources & Help"
              description="Access business resources, guides, and support"
              to="/resources"
              iconBg="bg-cyan-100"
              iconColor="text-cyan-600"
            />
            {/* Hidden cards for now (kept for future re-enable)
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
            */}
          </div>

          {/* Market Watch Card */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-base">
                <TrendingUp className="mr-2 text-purple-600" size={18} />
                Market Watch - General Markets
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 2xl:grid-cols-3 gap-3">
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
                    hasCompletedValidation
                      ? "Choose your business entity type and begin formation"
                      : "Run comprehensive validation to get SWOT, demand metrics, risks, and UVP",
                    hasCompletedValidation
                      ? "Create your customized operating agreement"
                      : "Choose your business entity type and begin formation",
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
                <div className="flex flex-col sm:flex-row gap-2">
                  <Input
                    placeholder="Ask anything about your business..."
                    value={aiQuestion}
                    onChange={(e) => setAiQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAiQuestion()}
                    className="flex-1"
                  />
                  <Button onClick={handleAiQuestion} className="gradient-primary border-0 px-3 w-full sm:w-auto">
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
                    content={
                      hasCompletedValidation
                        ? 'Complete "Register my business" - Choose your entity and start formation.'
                        : 'Complete "Validate Idea (All-in-One)" - Run comprehensive validation to get SWOT, demand metrics, risks, and UVP.'
                    }
                    timestamp="Just now"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Quick Insights */}
        <div className="space-y-6">
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

          {/* Quick Insights */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Quick Insights</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Suggestions */}
              <div>
                <h5 className="text-xs font-semibold text-gray-500 uppercase mb-2">SUGGESTIONS</h5>
                <ul className="space-y-2 text-sm text-gray-700 list-disc pl-5">
                  <li>
                    {hasCompletedValidation ? 'Choose your legal entity type' : 'Describe your idea in one sentence'}
                  </li>
                  <li>
                    {hasCompletedValidation ? 'Prepare your formation details' : 'Identify your target customer'}
                  </li>
                  <li>
                    {hasCompletedValidation ? 'Start business registration and continue onboarding' : 'Run validation to get SWOT, demand, risks, and UVP'}
                  </li>
                </ul>
              </div>

              {/* Quick Actions */}
              <div>
                <h5 className="text-xs font-semibold text-gray-500 uppercase mb-2">QUICK ACTIONS</h5>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <Button variant="outline" size="sm" className="w-full" onClick={() => navigate('/dashboard')}>
                    Dashboard
                  </Button>
                  <Button variant="outline" size="sm" className="w-full" onClick={() => {
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

