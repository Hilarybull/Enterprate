import React from 'react';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  HelpCircle, 
  MessageCircle, 
  Mail, 
  FileText,
  ExternalLink,
  Search,
  ChevronRight
} from 'lucide-react';

const faqs = [
  { q: 'How do I validate my business idea?', a: 'Navigate to Idea Discovery and complete the 6-step wizard.' },
  { q: 'How do I create an invoice?', a: 'Go to Finance and click on Create Invoice.' },
  { q: 'Can I export my data?', a: 'Yes, most sections have export options in CSV or PDF format.' },
  { q: 'How do I register my business?', a: 'Use the Business Registration Companion for step-by-step guidance.' }
];

export default function Help() {
  return (
    <div className="space-y-6 animate-slide-in" data-testid="help-page">
      <PageHeader
        icon={HelpCircle}
        title="Help & Support"
        description="Get help with EnterprateAI"
      />

      {/* Search */}
      <Card>
        <CardContent className="p-6">
          <div className="max-w-xl mx-auto">
            <h3 className="text-lg font-semibold text-center mb-4">How can we help you?</h3>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <Input 
                placeholder="Search for help..." 
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contact Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6 text-center">
            <div className="w-14 h-14 rounded-xl bg-purple-100 flex items-center justify-center mx-auto mb-4">
              <MessageCircle className="text-purple-600" size={28} />
            </div>
            <h3 className="font-semibold mb-2">Live Chat</h3>
            <p className="text-sm text-gray-500 mb-4">Chat with our support team</p>
            <Button className="gradient-primary border-0 w-full">
              Start Chat
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6 text-center">
            <div className="w-14 h-14 rounded-xl bg-blue-100 flex items-center justify-center mx-auto mb-4">
              <Mail className="text-blue-600" size={28} />
            </div>
            <h3 className="font-semibold mb-2">Email Support</h3>
            <p className="text-sm text-gray-500 mb-4">Get help via email</p>
            <Button variant="outline" className="w-full">
              support@enterprate.ai
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6 text-center">
            <div className="w-14 h-14 rounded-xl bg-green-100 flex items-center justify-center mx-auto mb-4">
              <FileText className="text-green-600" size={28} />
            </div>
            <h3 className="font-semibold mb-2">Documentation</h3>
            <p className="text-sm text-gray-500 mb-4">Browse our docs</p>
            <Button variant="outline" className="w-full">
              <ExternalLink size={16} className="mr-2" />
              View Docs
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* FAQs */}
      <Card>
        <CardHeader>
          <CardTitle>Frequently Asked Questions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {faqs.map((faq, i) => (
              <div key={i} className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">{faq.q}</h4>
                  <ChevronRight className="text-gray-400" size={20} />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
