import React from 'react';
import { PageHeader, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  BookOpen, 
  Target, 
  Users, 
  DollarSign,
  BarChart3,
  Lightbulb,
  FileText,
  Sparkles,
  ArrowRight
} from 'lucide-react';

const blueprintSections = [
  {
    title: 'Executive Summary',
    description: 'High-level overview of your business concept and goals',
    icon: FileText,
    status: 'Generate'
  },
  {
    title: 'Market Analysis',
    description: 'Industry trends, target market, and competitive landscape',
    icon: BarChart3,
    status: 'Generate'
  },
  {
    title: 'Products & Services',
    description: 'Detailed description of your offerings and value proposition',
    icon: Lightbulb,
    status: 'Generate'
  },
  {
    title: 'Marketing Strategy',
    description: 'Customer acquisition and brand positioning plans',
    icon: Target,
    status: 'Generate'
  },
  {
    title: 'Operations Plan',
    description: 'Day-to-day operations, processes, and resource requirements',
    icon: Users,
    status: 'Generate'
  },
  {
    title: 'Financial Projections',
    description: 'Revenue forecasts, expense budgets, and break-even analysis',
    icon: DollarSign,
    status: 'Generate'
  }
];

export default function BusinessBlueprint() {
  return (
    <div className="space-y-8 animate-slide-in" data-testid="business-blueprint-page">
      <PageHeader
        icon={BookOpen}
        title="Business Blueprint Generation"
        description="Create comprehensive business plans and strategic roadmaps with AI assistance"
        actions={
          <Button className="gradient-primary border-0">
            <Sparkles className="mr-2" size={18} />
            Generate Full Blueprint
          </Button>
        }
      />

      {/* AI Generation Card */}
      <Card className="bg-gradient-to-r from-purple-600 to-blue-600 text-white border-0">
        <CardContent className="p-8">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold mb-2">AI-Powered Business Planning</h3>
              <p className="text-purple-100 max-w-xl">
                Our AI analyzes your business idea and generates comprehensive plans, 
                financial models, and strategic roadmaps tailored to your industry and goals.
              </p>
              <Button className="mt-4 bg-white text-purple-700 hover:bg-purple-50">
                Start with Your Idea
                <ArrowRight className="ml-2" size={18} />
              </Button>
            </div>
            <div className="hidden lg:block">
              <div className="w-32 h-32 rounded-2xl bg-white/10 flex items-center justify-center">
                <BookOpen className="text-white" size={64} />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Blueprint Sections */}
      <Card>
        <CardHeader>
          <CardTitle>Blueprint Sections</CardTitle>
          <CardDescription>
            Generate individual sections or create a complete business plan
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {blueprintSections.map((section, index) => {
              const Icon = section.icon;
              return (
                <div
                  key={index}
                  className="flex items-center p-4 border border-gray-200 rounded-xl hover:border-purple-300 hover:bg-purple-50/50 transition-all group"
                >
                  <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center mr-4 group-hover:bg-purple-200 transition-colors">
                    <Icon size={24} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-900">{section.title}</h4>
                    <p className="text-sm text-gray-500 truncate">{section.description}</p>
                  </div>
                  <Button variant="outline" size="sm" className="ml-4">
                    {section.status}
                  </Button>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <FeatureCard
          title="Industry Templates"
          description="Pre-built templates for 50+ industries and business models"
          icon={FileText}
          gradient="gradient-primary"
        />
        <FeatureCard
          title="Financial Modeling"
          description="Automated projections based on industry benchmarks"
          icon={BarChart3}
          gradient="gradient-success"
        />
        <FeatureCard
          title="Export & Share"
          description="Download as PDF or share with investors and partners"
          icon={Target}
          gradient="gradient-warning"
        />
      </div>
    </div>
  );
}
