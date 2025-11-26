import React from 'react';
import { PageHeader, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  HelpCircle, 
  MessageCircle, 
  Book, 
  Video,
  Mail,
  ExternalLink
} from 'lucide-react';

const resources = [
  {
    title: 'Documentation',
    description: 'Comprehensive guides and API references',
    icon: Book,
    action: 'View Docs'
  },
  {
    title: 'Video Tutorials',
    description: 'Step-by-step video walkthroughs',
    icon: Video,
    action: 'Watch Now'
  },
  {
    title: 'Community',
    description: 'Connect with other Enterprate users',
    icon: MessageCircle,
    action: 'Join Community'
  },
  {
    title: 'Contact Support',
    description: 'Get help from our support team',
    icon: Mail,
    action: 'Send Email'
  }
];

const faqs = [
  {
    question: 'How do I create a new workspace?',
    answer: 'Click on the workspace selector in the header and select "Create Workspace". Fill in your workspace name and click Create.'
  },
  {
    question: 'How does the AI idea validation work?',
    answer: 'Our Genesis AI analyzes your business idea using market data and AI models to provide a viability score, key insights, and recommended next steps.'
  },
  {
    question: 'Can I invite team members to my workspace?',
    answer: 'Team collaboration features are coming soon! You will be able to invite members and assign roles.'
  },
  {
    question: 'How do I create and send an invoice?',
    answer: 'Navigate to Finance Automation, click "Create Invoice", fill in client details and amount, then send directly from the platform.'
  }
];

export default function Help() {
  return (
    <div className="space-y-8 animate-slide-in" data-testid="help-page">
      <PageHeader
        icon={HelpCircle}
        title="Help & Support"
        description="Get the help you need to make the most of Enterprate OS"
      />

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {resources.map((resource, index) => {
          const Icon = resource.icon;
          return (
            <Card key={index} className="enterprise-card enterprise-card-interactive">
              <CardContent className="p-6">
                <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center mb-4">
                  <Icon className="text-white" size={24} />
                </div>
                <h3 className="font-semibold mb-1">{resource.title}</h3>
                <p className="text-sm text-gray-500 mb-4">{resource.description}</p>
                <Button variant="outline" size="sm" className="w-full">
                  {resource.action}
                  <ExternalLink size={14} className="ml-2" />
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* FAQ Section */}
      <Card>
        <CardHeader>
          <CardTitle>Frequently Asked Questions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-xl">
                <h4 className="font-medium text-gray-900 mb-2">{faq.question}</h4>
                <p className="text-sm text-gray-600">{faq.answer}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Contact Card */}
      <Card className="bg-gradient-to-r from-purple-600 to-blue-600 text-white border-0">
        <CardContent className="p-8 text-center">
          <h3 className="text-2xl font-bold mb-2">Still Need Help?</h3>
          <p className="text-purple-100 mb-6 max-w-xl mx-auto">
            Our support team is available to help you with any questions or issues you may have.
          </p>
          <div className="flex items-center justify-center space-x-4">
            <Button className="bg-white text-purple-700 hover:bg-purple-50">
              <MessageCircle className="mr-2" size={18} />
              Start Live Chat
            </Button>
            <Button variant="outline" className="border-white text-white hover:bg-white/10">
              <Mail className="mr-2" size={18} />
              Email Support
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
