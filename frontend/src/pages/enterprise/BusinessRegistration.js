import React from 'react';
import { PageHeader, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  FileText, 
  CheckCircle, 
  Clock, 
  Building2,
  Scale,
  Shield,
  FileCheck,
  ArrowRight
} from 'lucide-react';

const registrationSteps = [
  {
    id: 1,
    title: 'Choose Business Structure',
    description: 'LLC, Corporation, Sole Proprietorship, or Partnership',
    status: 'pending',
    icon: Building2
  },
  {
    id: 2,
    title: 'Register Business Name',
    description: 'Check availability and register your business name',
    status: 'pending',
    icon: FileText
  },
  {
    id: 3,
    title: 'Obtain EIN/Tax ID',
    description: 'Get your Employer Identification Number',
    status: 'pending',
    icon: FileCheck
  },
  {
    id: 4,
    title: 'Business Licenses & Permits',
    description: 'Apply for required licenses in your jurisdiction',
    status: 'pending',
    icon: Scale
  },
  {
    id: 5,
    title: 'Compliance Setup',
    description: 'Set up compliance requirements and reporting',
    status: 'pending',
    icon: Shield
  }
];

export default function BusinessRegistration() {
  return (
    <div className="space-y-8 animate-slide-in" data-testid="business-registration-page">
      <PageHeader
        icon={FileText}
        title="Business Registration Companion"
        description="Step-by-step guidance through business formation and legal compliance"
      />

      {/* Progress Overview */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-lg">Registration Progress</h3>
              <p className="text-sm text-gray-500">0 of 5 steps completed</p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-bold text-purple-600">0%</span>
              <p className="text-xs text-gray-500">Complete</p>
            </div>
          </div>
          <Progress value={0} className="h-2" />
        </CardContent>
      </Card>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <FeatureCard
          title="AI-Powered Guidance"
          description="Get personalized recommendations based on your business type and location"
          icon={Building2}
          gradient="gradient-primary"
        />
        <FeatureCard
          title="Document Templates"
          description="Access ready-to-use legal document templates for your business"
          icon={FileCheck}
          gradient="gradient-success"
        />
        <FeatureCard
          title="Compliance Tracking"
          description="Stay on top of deadlines and regulatory requirements"
          icon={Shield}
          gradient="gradient-warning"
        />
      </div>

      {/* Registration Steps */}
      <Card>
        <CardHeader>
          <CardTitle>Registration Checklist</CardTitle>
          <CardDescription>
            Complete these steps to properly register your business
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {registrationSteps.map((step, index) => {
              const Icon = step.icon;
              return (
                <div
                  key={step.id}
                  className="flex items-center p-4 border border-gray-200 rounded-xl hover:border-purple-300 transition-colors"
                >
                  <div className="flex-shrink-0 mr-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      step.status === 'completed' 
                        ? 'bg-green-100 text-green-600' 
                        : step.status === 'in_progress'
                          ? 'bg-purple-100 text-purple-600'
                          : 'bg-gray-100 text-gray-400'
                    }`}>
                      {step.status === 'completed' ? (
                        <CheckCircle size={20} />
                      ) : (
                        <span className="font-semibold">{index + 1}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-900">{step.title}</h4>
                    <p className="text-sm text-gray-500">{step.description}</p>
                  </div>
                  <div className="flex-shrink-0 ml-4">
                    <Button variant="outline" size="sm">
                      Start <ArrowRight size={14} className="ml-1" />
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Coming Soon Notice */}
      <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
        <CardContent className="p-6 text-center">
          <Clock className="mx-auto text-purple-600 mb-3" size={40} />
          <h3 className="font-semibold text-lg mb-2">Full Registration Workflow Coming Soon</h3>
          <p className="text-gray-600 max-w-xl mx-auto">
            We&apos;re building an AI-powered registration assistant that will guide you through each step, 
            generate documents, and help you stay compliant. Check back soon!
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
