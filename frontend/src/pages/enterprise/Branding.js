import React from 'react';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Palette, 
  Image, 
  Type, 
  Shapes, 
  Download,
  Sparkles,
  ArrowRight
} from 'lucide-react';

export default function Branding() {
  return (
    <div className="space-y-6 animate-slide-in" data-testid="branding-page">
      <PageHeader
        icon={Palette}
        title="Branding"
        description="Create and manage your visual identity and brand assets"
      />

      {/* Brand Kit Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6 text-center">
            <div className="w-14 h-14 rounded-xl bg-purple-100 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="text-purple-600" size={28} />
            </div>
            <h3 className="font-semibold text-lg mb-2">AI Logo Generator</h3>
            <p className="text-sm text-gray-500 mb-4">Create unique logos with AI assistance</p>
            <Button className="gradient-primary border-0">
              Generate Logo <ArrowRight size={16} className="ml-2" />
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6 text-center">
            <div className="w-14 h-14 rounded-xl bg-blue-100 flex items-center justify-center mx-auto mb-4">
              <Palette className="text-blue-600" size={28} />
            </div>
            <h3 className="font-semibold text-lg mb-2">Color Palette</h3>
            <p className="text-sm text-gray-500 mb-4">Define your brand colors</p>
            <Button variant="outline">
              Customize Colors
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="p-6 text-center">
            <div className="w-14 h-14 rounded-xl bg-green-100 flex items-center justify-center mx-auto mb-4">
              <Type className="text-green-600" size={28} />
            </div>
            <h3 className="font-semibold text-lg mb-2">Typography</h3>
            <p className="text-sm text-gray-500 mb-4">Choose your brand fonts</p>
            <Button variant="outline">
              Select Fonts
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Brand Assets */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Image className="mr-2 text-purple-600" size={20} />
            Brand Assets
          </CardTitle>
          <CardDescription>Your logo variations and brand materials</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
            <Shapes className="mx-auto text-gray-300 mb-4" size={48} />
            <h3 className="font-semibold text-gray-600 mb-2">No brand assets yet</h3>
            <p className="text-sm text-gray-400 mb-4">Generate your first logo to get started</p>
            <Button className="gradient-primary border-0">
              <Sparkles size={16} className="mr-2" />
              Create Brand Kit
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Download Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Download className="mr-2 text-purple-600" size={20} />
            Export Brand Kit
          </CardTitle>
          <CardDescription>Download your complete brand package</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
            <div>
              <h4 className="font-semibold">Complete Brand Kit</h4>
              <p className="text-sm text-gray-500">Logos, colors, fonts, and guidelines</p>
            </div>
            <Button variant="outline" disabled>
              <Download size={16} className="mr-2" />
              Download ZIP
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
