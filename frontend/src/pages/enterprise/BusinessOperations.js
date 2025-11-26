import React from 'react';
import { PageHeader, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Briefcase, 
  Users, 
  Calendar, 
  CheckSquare,
  Clock,
  BarChart3,
  Workflow,
  Settings2,
  ArrowRight
} from 'lucide-react';

const operationsModules = [
  {
    title: 'Task Management',
    description: 'Create, assign, and track tasks across your team',
    icon: CheckSquare,
    status: 'Coming Soon'
  },
  {
    title: 'Team Collaboration',
    description: 'Real-time collaboration tools for your team',
    icon: Users,
    status: 'Coming Soon'
  },
  {
    title: 'Process Automation',
    description: 'Automate repetitive workflows and tasks',
    icon: Workflow,
    status: 'Coming Soon'
  },
  {
    title: 'Resource Planning',
    description: 'Allocate resources and manage capacity',
    icon: Calendar,
    status: 'Coming Soon'
  },
  {
    title: 'Performance Metrics',
    description: 'Track KPIs and operational efficiency',
    icon: BarChart3,
    status: 'Coming Soon'
  },
  {
    title: 'System Integrations',
    description: 'Connect with your existing tools and services',
    icon: Settings2,
    status: 'Coming Soon'
  }
];

export default function BusinessOperations() {
  return (
    <div className="space-y-8 animate-slide-in" data-testid="business-operations-page">
      <PageHeader
        icon={Briefcase}
        title="Business Operations"
        description="Streamline your daily operations with intelligent process management"
      />

      {/* Hero Card */}
      <Card className="bg-gradient-to-r from-purple-600 to-blue-600 text-white border-0">
        <CardContent className="p-8">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold mb-2">Operations Command Center</h3>
              <p className="text-purple-100 max-w-xl">
                Manage all aspects of your business operations from a single dashboard. 
                Track tasks, coordinate teams, and optimize workflows.
              </p>
              <Button className="mt-4 bg-white text-purple-700 hover:bg-purple-50">
                Explore Features
                <ArrowRight className="ml-2" size={18} />
              </Button>
            </div>
            <div className="hidden lg:block">
              <div className="w-32 h-32 rounded-2xl bg-white/10 flex items-center justify-center">
                <Briefcase className="text-white" size={64} />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Operations Modules */}
      <Card>
        <CardHeader>
          <CardTitle>Operations Modules</CardTitle>
          <CardDescription>
            Comprehensive tools to manage every aspect of your business operations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {operationsModules.map((module, index) => {
              const Icon = module.icon;
              return (
                <div
                  key={index}
                  className="p-5 border border-gray-200 rounded-xl hover:border-purple-300 hover:bg-purple-50/50 transition-all group"
                >
                  <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center mb-4 group-hover:bg-purple-200 transition-colors">
                    <Icon size={24} />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-1">{module.title}</h4>
                  <p className="text-sm text-gray-500 mb-3">{module.description}</p>
                  <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full">
                    {module.status}
                  </span>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Quick Stats Placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Active Projects', value: '0', icon: Briefcase },
          { label: 'Team Members', value: '1', icon: Users },
          { label: 'Open Tasks', value: '0', icon: CheckSquare },
          { label: 'Hours Saved', value: '0h', icon: Clock }
        ].map((stat, i) => {
          const Icon = stat.icon;
          return (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{stat.label}</p>
                    <p className="text-2xl font-bold">{stat.value}</p>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
                    <Icon className="text-gray-500" size={20} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
