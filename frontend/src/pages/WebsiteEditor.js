import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { useWorkspace } from '@/context/WorkspaceContext';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ArrowLeft, Plus, Trash2, GripVertical, Type, Image as ImageIcon, Layout } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const COMPONENT_TYPES = [
  { type: 'heading', icon: Type, label: 'Heading', defaultContent: 'New Heading' },
  { type: 'text', icon: Type, label: 'Text', defaultContent: 'Add your text here...' },
  { type: 'image', icon: ImageIcon, label: 'Image', defaultContent: 'https://via.placeholder.com/800x400' },
  { type: 'section', icon: Layout, label: 'Section', defaultContent: '' }
];

export default function WebsiteEditor() {
  const { websiteId } = useParams();
  const navigate = useNavigate();
  const { getHeaders } = useWorkspace();
  const [website, setWebsite] = useState(null);
  const [pages, setPages] = useState([]);
  const [selectedPage, setSelectedPage] = useState(null);
  const [sections, setSections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createPageOpen, setCreatePageOpen] = useState(false);
  const [newPageData, setNewPageData] = useState({ path: '', title: '' });

  useEffect(() => {
    loadWebsiteData();
  }, [websiteId]);

  const loadWebsiteData = async () => {
    try {
      const headers = getHeaders();
      
      const [websiteRes, pagesRes] = await Promise.all([
        axios.get(`${API_URL}/websites/${websiteId}`, { headers }),
        axios.get(`${API_URL}/websites/${websiteId}/pages`, { headers })
      ]);

      setWebsite(websiteRes.data);
      setPages(pagesRes.data);
      
      if (pagesRes.data.length > 0) {
        selectPage(pagesRes.data[0]);
      }
    } catch (error) {
      console.error('Failed to load website:', error);
      toast.error('Failed to load website');
    } finally {
      setLoading(false);
    }
  };

  const selectPage = (page) => {
    setSelectedPage(page);
    setSections(page.content?.sections || []);
  };

  const handleCreatePage = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        `${API_URL}/websites/${websiteId}/pages`,
        newPageData,
        { headers: getHeaders() }
      );
      toast.success('Page created');
      setPages([...pages, response.data]);
      setCreatePageOpen(false);
      setNewPageData({ path: '', title: '' });
      selectPage(response.data);
    } catch (error) {
      toast.error('Failed to create page');
    }
  };

  const addSection = (type) => {
    const component = COMPONENT_TYPES.find(c => c.type === type);
    const newSection = {
      id: Date.now().toString(),
      type: type,
      content: component.defaultContent
    };
    setSections([...sections, newSection]);
  };

  const updateSection = (id, content) => {
    setSections(sections.map(s => s.id === id ? { ...s, content } : s));
  };

  const deleteSection = (id) => {
    setSections(sections.filter(s => s.id !== id));
  };

  const savePage = async () => {
    if (!selectedPage) return;

    try {
      await axios.patch(
        `${API_URL}/websites/${websiteId}/pages/${selectedPage.id}`,
        {
          path: selectedPage.path,
          title: selectedPage.title,
          content: { sections }
        },
        { headers: getHeaders() }
      );
      toast.success('Page saved successfully');
    } catch (error) {
      toast.error('Failed to save page');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="website-editor">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" size="sm" onClick={() => navigate('/website-builder')} data-testid="back-btn">
            <ArrowLeft size={16} className="mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold" style={{ fontFamily: 'Space Grotesk' }}>
              {website?.name}
            </h1>
            <p className="text-sm text-gray-600">{website?.domain || 'No domain'}</p>
          </div>
        </div>
        <Button onClick={savePage} disabled={!selectedPage} data-testid="save-page-btn">
          Save Page
        </Button>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Pages Sidebar */}
        <div className="col-span-3">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Pages</h3>
                <Button size="sm" variant="outline" onClick={() => setCreatePageOpen(true)} data-testid="add-page-btn">
                  <Plus size={16} />
                </Button>
              </div>
              <div className="space-y-2">
                {pages.map((page, index) => (
                  <button
                    key={page.id}
                    onClick={() => selectPage(page)}
                    data-testid={`page-item-${index}`}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                      selectedPage?.id === page.id
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'hover:bg-gray-100'
                    }`}
                  >
                    <div className="font-medium">{page.title}</div>
                    <div className="text-xs text-gray-500">{page.path}</div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Component Library */}
          <Card className="mt-4">
            <CardContent className="p-4">
              <h3 className="font-semibold mb-4">Components</h3>
              <div className="space-y-2">
                {COMPONENT_TYPES.map((comp) => {
                  const Icon = comp.icon;
                  return (
                    <button
                      key={comp.type}
                      onClick={() => addSection(comp.type)}
                      disabled={!selectedPage}
                      data-testid={`add-${comp.type}-btn`}
                      className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Icon size={16} />
                      <span>{comp.label}</span>
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Editor Canvas */}
        <div className="col-span-9">
          <Card>
            <CardContent className="p-6">
              {!selectedPage ? (
                <div className="text-center py-16 text-gray-500">
                  Select a page to start editing
                </div>
              ) : sections.length === 0 ? (
                <div className="text-center py-16">
                  <Layout className="mx-auto text-gray-400 mb-4" size={48} />
                  <p className="text-gray-600 mb-2">No components yet</p>
                  <p className="text-sm text-gray-500">Add components from the left sidebar</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {sections.map((section, index) => (
                    <div
                      key={section.id}
                      className="group border rounded-lg p-4 hover:border-blue-500 transition-colors"
                      data-testid={`section-${index}`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className="cursor-move pt-2">
                          <GripVertical size={16} className="text-gray-400" />
                        </div>
                        <div className="flex-1">
                          {section.type === 'heading' && (
                            <Input
                              value={section.content}
                              onChange={(e) => updateSection(section.id, e.target.value)}
                              className="text-2xl font-bold border-0 p-0 focus-visible:ring-0"
                              data-testid={`heading-input-${index}`}
                            />
                          )}
                          {section.type === 'text' && (
                            <textarea
                              value={section.content}
                              onChange={(e) => updateSection(section.id, e.target.value)}
                              className="w-full border-0 p-0 focus:outline-none resize-none"
                              rows={3}
                              data-testid={`text-input-${index}`}
                            />
                          )}
                          {section.type === 'image' && (
                            <div>
                              <Input
                                value={section.content}
                                onChange={(e) => updateSection(section.id, e.target.value)}
                                placeholder="Image URL"
                                className="mb-2"
                                data-testid={`image-url-input-${index}`}
                              />
                              <img
                                src={section.content}
                                alt="Preview"
                                className="w-full h-48 object-cover rounded"
                                onError={(e) => e.target.src = 'https://via.placeholder.com/800x400?text=Image'}
                              />
                            </div>
                          )}
                          {section.type === 'section' && (
                            <div className="p-6 bg-gray-50 rounded">
                              <p className="text-sm text-gray-500">Section container</p>
                            </div>
                          )}
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => deleteSection(section.id)}
                          className="opacity-0 group-hover:opacity-100 transition-opacity"
                          data-testid={`delete-section-${index}`}
                        >
                          <Trash2 size={16} className="text-red-500" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Create Page Dialog */}
      <Dialog open={createPageOpen} onOpenChange={setCreatePageOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Page</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreatePage} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Page Title</label>
              <Input
                value={newPageData.title}
                onChange={(e) => setNewPageData({ ...newPageData, title: e.target.value })}
                placeholder="About Us"
                required
                data-testid="new-page-title-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Path</label>
              <Input
                value={newPageData.path}
                onChange={(e) => setNewPageData({ ...newPageData, path: e.target.value })}
                placeholder="/about"
                required
                data-testid="new-page-path-input"
              />
            </div>
            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => setCreatePageOpen(false)} data-testid="cancel-new-page-btn">
                Cancel
              </Button>
              <Button type="submit" data-testid="submit-new-page-btn">Create Page</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
