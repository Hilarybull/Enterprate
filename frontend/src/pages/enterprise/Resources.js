import React from 'react';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  FolderOpen, 
  FileText, 
  Download,
  ExternalLink,
  BookOpen,
  Video,
  FileSpreadsheet,
  Presentation
} from 'lucide-react';

const resources = [
  {
    category: 'Templates',
    items: [
      { name: 'Business Plan Template', type: 'PDF', icon: FileText, badge: 'Popular' },
      { name: 'Financial Projections', type: 'Excel', icon: FileSpreadsheet },
      { name: 'Pitch Deck Template', type: 'PPT', icon: Presentation, badge: 'New' },
      { name: 'Marketing Plan', type: 'PDF', icon: FileText }
    ]
  },
  {
    category: 'Guides',
    items: [
      { name: 'Starting Your LLC', type: 'Guide', icon: BookOpen },
      { name: 'Tax Planning Basics', type: 'Guide', icon: BookOpen },
      { name: 'Hiring Your First Employee', type: 'Guide', icon: BookOpen, badge: 'New' }
    ]
  },
  {
    category: 'Video Tutorials',
    items: [
      { name: 'Platform Walkthrough', type: 'Video', icon: Video, duration: '12 min' },
      { name: 'Idea Validation Deep Dive', type: 'Video', icon: Video, duration: '8 min' },
      { name: 'Financial Setup Guide', type: 'Video', icon: Video, duration: '15 min' }
    ]
  }
];

export default function Resources() {
  return (
    <div className="space-y-6 animate-slide-in" data-testid="resources-page">
      <PageHeader
        icon={FolderOpen}
        title="Business Resources Hub"
        description="Templates, guides, and tools to help grow your business"
      />

      {resources.map((section) => (
        <Card key={section.category}>
          <CardHeader>
            <CardTitle>{section.category}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {section.items.map((item, index) => {
                const Icon = item.icon;
                return (
                  <div 
                    key={index}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                        <Icon className="text-purple-600" size={20} />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium text-sm">{item.name}</h4>
                          {item.badge && (
                            <Badge variant="secondary" className="text-xs">{item.badge}</Badge>
                          )}
                        </div>
                        <p className="text-xs text-gray-500">
                          {item.type}{item.duration && ` • ${item.duration}`}
                        </p>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      {item.type === 'Video' ? (
                        <ExternalLink size={16} />
                      ) : (
                        <Download size={16} />
                      )}
                    </Button>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
