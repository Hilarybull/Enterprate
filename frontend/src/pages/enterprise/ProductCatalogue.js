import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Package, 
  Plus, 
  Upload, 
  Search,
  Edit,
  Trash2,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  FileSpreadsheet,
  FileText,
  Loader2,
  Download,
  Eye,
  X
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function ProductCatalogue() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [activeTab, setActiveTab] = useState('catalogue');
  const [loading, setLoading] = useState(true);
  const [items, setItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  
  // Upload state
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [validationResults, setValidationResults] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    unitPrice: '',
    currency: 'GBP',
    taxRate: '',
    sku: '',
    category: ''
  });

  const loadCatalogue = useCallback(async () => {
    if (!currentWorkspace) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/catalogue`, {
        headers: getHeaders()
      });
      setItems(response.data || []);
    } catch (error) {
      console.error('Failed to load catalogue:', error);
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace, getHeaders]);

  useEffect(() => {
    loadCatalogue();
  }, [loadCatalogue]);

  const handleAddItem = async () => {
    if (!formData.name || !formData.unitPrice) {
      toast.error('Name and price are required');
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/catalogue`, {
        ...formData,
        unitPrice: parseFloat(formData.unitPrice),
        taxRate: formData.taxRate ? parseFloat(formData.taxRate) : null
      }, { headers: getHeaders() });

      if (response.data) {
        toast.success('Item added to catalogue');
        setShowAddDialog(false);
        resetForm();
        loadCatalogue();
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add item');
    }
  };

  const handleUpdateItem = async () => {
    if (!editingItem || !formData.name || !formData.unitPrice) {
      toast.error('Name and price are required');
      return;
    }

    try {
      await axios.put(`${API_URL}/catalogue/${editingItem.id}`, {
        ...formData,
        unitPrice: parseFloat(formData.unitPrice),
        taxRate: formData.taxRate ? parseFloat(formData.taxRate) : null
      }, { headers: getHeaders() });

      toast.success('Item updated');
      setEditingItem(null);
      resetForm();
      loadCatalogue();
    } catch (error) {
      toast.error('Failed to update item');
    }
  };

  const handleDeleteItem = async (itemId) => {
    if (!window.confirm('Delete this item from catalogue?')) return;

    try {
      await axios.delete(`${API_URL}/catalogue/${itemId}`, { headers: getHeaders() });
      toast.success('Item deleted');
      loadCatalogue();
    } catch (error) {
      toast.error('Failed to delete item');
    }
  };

  const handleFileUpload = async () => {
    if (!uploadFile) {
      toast.error('Please select a file');
      return;
    }

    setUploading(true);
    const formDataUpload = new FormData();
    formDataUpload.append('file', uploadFile);

    try {
      const response = await axios.post(`${API_URL}/catalogue/upload`, formDataUpload, {
        headers: {
          ...getHeaders(),
          'Content-Type': 'multipart/form-data'
        }
      });

      setValidationResults(response.data);
      setActiveTab('validation');
      toast.success('File processed! Review the validation results.');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to process file');
    } finally {
      setUploading(false);
      setShowUploadDialog(false);
      setUploadFile(null);
    }
  };

  const handleAddValidatedItems = async (itemsToAdd) => {
    try {
      const response = await axios.post(`${API_URL}/catalogue/bulk`, {
        items: itemsToAdd
      }, { headers: getHeaders() });

      toast.success(`Added ${response.data.addedCount} items to catalogue`);
      setValidationResults(null);
      setActiveTab('catalogue');
      loadCatalogue();
    } catch (error) {
      toast.error('Failed to add items');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      unitPrice: '',
      currency: 'GBP',
      taxRate: '',
      sku: '',
      category: ''
    });
  };

  const startEdit = (item) => {
    setEditingItem(item);
    setFormData({
      name: item.name || '',
      description: item.description || '',
      unitPrice: item.unitPrice?.toString() || '',
      currency: item.currency || 'GBP',
      taxRate: item.taxRate?.toString() || '',
      sku: item.sku || '',
      category: item.category || ''
    });
  };

  const filteredItems = items.filter(item =>
    item.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.sku?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.category?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-slide-in" data-testid="product-catalogue-page">
      <PageHeader
        icon={Package}
        title="Catalogue"
        description="Manage product and user data for use across invoices, quotes, and website"
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setShowUploadDialog(true)}>
              <Upload className="mr-2" size={16} />
              Upload Catalogue
            </Button>
            <Button className="gradient-primary border-0" onClick={() => setShowAddDialog(true)}>
              <Plus className="mr-2" size={16} />
              Add Item
            </Button>
          </div>
        }
      />

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="catalogue">
            <Package size={16} className="mr-2" />
            Catalogue ({items.length})
          </TabsTrigger>
          {validationResults && (
            <TabsTrigger value="validation">
              <AlertCircle size={16} className="mr-2" />
              Validation Results
            </TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="catalogue" className="space-y-4 mt-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search by name, SKU, or category..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Catalogue Items */}
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
            </div>
          ) : filteredItems.length > 0 ? (
            <div className="grid gap-4">
              {filteredItems.map((item) => (
                <Card key={item.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold">{item.name}</h3>
                          {item.sku && (
                            <Badge variant="outline" className="text-xs">SKU: {item.sku}</Badge>
                          )}
                          {item.category && (
                            <Badge className="bg-purple-100 text-purple-700">{item.category}</Badge>
                          )}
                        </div>
                        {item.description && (
                          <p className="text-sm text-gray-500 mt-1">{item.description}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-lg font-bold">
                            {item.currency === 'GBP' ? '£' : item.currency === 'USD' ? '$' : '€'}
                            {item.unitPrice?.toFixed(2)}
                          </p>
                          {item.taxRate && (
                            <p className="text-xs text-gray-500">+{item.taxRate}% VAT</p>
                          )}
                        </div>
                        <div className="flex gap-1">
                          <Button variant="ghost" size="sm" onClick={() => startEdit(item)}>
                            <Edit size={16} />
                          </Button>
                          <Button variant="ghost" size="sm" className="text-red-500" onClick={() => handleDeleteItem(item.id)}>
                            <Trash2 size={16} />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-12 text-center">
              <Package className="mx-auto text-gray-300 mb-4" size={48} />
              <h3 className="text-lg font-medium text-gray-700">No Items in Catalogue</h3>
              <p className="text-gray-500 mt-1">Add products or services to use them across your business</p>
              <div className="flex justify-center gap-3 mt-4">
                <Button variant="outline" onClick={() => setShowUploadDialog(true)}>
                  <Upload className="mr-2" size={16} /> Upload File
                </Button>
                <Button onClick={() => setShowAddDialog(true)}>
                  <Plus className="mr-2" size={16} /> Add Manually
                </Button>
              </div>
            </Card>
          )}
        </TabsContent>

        {validationResults && (
          <TabsContent value="validation" className="space-y-4 mt-4">
            <ValidationResultsView 
              results={validationResults} 
              onAddItems={handleAddValidatedItems}
              onDismiss={() => setValidationResults(null)}
            />
          </TabsContent>
        )}
      </Tabs>

      {/* Add/Edit Item Dialog */}
      <Dialog open={showAddDialog || !!editingItem} onOpenChange={(open) => {
        if (!open) {
          setShowAddDialog(false);
          setEditingItem(null);
          resetForm();
        }
      }}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingItem ? 'Edit Item' : 'Add New Item'}</DialogTitle>
            <DialogDescription>
              {editingItem ? 'Update the item details' : 'Add a product or service to your catalogue'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Name *</Label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Product or service name"
              />
            </div>
            <div>
              <Label>Description</Label>
              <Input
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Brief description"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Unit Price *</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.unitPrice}
                  onChange={(e) => setFormData({ ...formData, unitPrice: e.target.value })}
                  placeholder="0.00"
                />
              </div>
              <div>
                <Label>Currency</Label>
                <Select value={formData.currency} onValueChange={(v) => setFormData({ ...formData, currency: v })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="GBP">GBP (£)</SelectItem>
                    <SelectItem value="USD">USD ($)</SelectItem>
                    <SelectItem value="EUR">EUR (€)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Tax/VAT Rate (%)</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={formData.taxRate}
                  onChange={(e) => setFormData({ ...formData, taxRate: e.target.value })}
                  placeholder="20"
                />
              </div>
              <div>
                <Label>SKU</Label>
                <Input
                  value={formData.sku}
                  onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                  placeholder="PROD-001"
                />
              </div>
            </div>
            <div>
              <Label>Category</Label>
              <Input
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="e.g., Services, Products, Consulting"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setShowAddDialog(false); setEditingItem(null); resetForm(); }}>
              Cancel
            </Button>
            <Button onClick={editingItem ? handleUpdateItem : handleAddItem}>
              {editingItem ? 'Update Item' : 'Add Item'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Upload Dialog */}
      <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Catalogue</DialogTitle>
            <DialogDescription>
              Upload a CSV, Excel, PDF, or Word file with your products/services
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <input
                type="file"
                accept=".csv,.xlsx,.xls,.pdf,.doc,.docx"
                onChange={(e) => setUploadFile(e.target.files[0])}
                className="hidden"
                id="catalogue-upload"
              />
              <label htmlFor="catalogue-upload" className="cursor-pointer">
                {uploadFile ? (
                  <div className="flex items-center justify-center gap-2">
                    <FileSpreadsheet className="text-green-600" size={24} />
                    <span className="font-medium">{uploadFile.name}</span>
                    <Button variant="ghost" size="sm" onClick={(e) => { e.preventDefault(); setUploadFile(null); }}>
                      <X size={16} />
                    </Button>
                  </div>
                ) : (
                  <>
                    <Upload className="mx-auto text-gray-400 mb-2" size={32} />
                    <p className="text-gray-600">Click to select a file</p>
                    <p className="text-xs text-gray-400 mt-1">CSV, Excel, PDF, or Word</p>
                  </>
                )}
              </label>
            </div>
            <Alert>
              <FileText className="h-4 w-4" />
              <AlertDescription>
                Your file should contain columns: <strong>Name</strong>, <strong>Description</strong>, <strong>Unit Price</strong>, Currency, Tax Rate, SKU
              </AlertDescription>
            </Alert>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowUploadDialog(false)}>Cancel</Button>
            <Button onClick={handleFileUpload} disabled={!uploadFile || uploading}>
              {uploading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Upload className="mr-2" size={16} />}
              Process File
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Validation Results Component
function ValidationResultsView({ results, onAddItems, onDismiss }) {
  const accepted = results?.accepted || [];
  const needsReview = results?.needsReview || [];
  const rejected = results?.rejected || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Validation Results</h3>
        <Button variant="outline" onClick={onDismiss}>
          <X className="mr-2" size={16} /> Dismiss
        </Button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-4 flex items-center gap-3">
            <CheckCircle2 className="text-green-600" size={24} />
            <div>
              <p className="text-2xl font-bold text-green-700">{accepted.length}</p>
              <p className="text-sm text-green-600">Accepted</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-amber-50 border-amber-200">
          <CardContent className="p-4 flex items-center gap-3">
            <AlertTriangle className="text-amber-600" size={24} />
            <div>
              <p className="text-2xl font-bold text-amber-700">{needsReview.length}</p>
              <p className="text-sm text-amber-600">Needs Review</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-red-50 border-red-200">
          <CardContent className="p-4 flex items-center gap-3">
            <AlertCircle className="text-red-600" size={24} />
            <div>
              <p className="text-2xl font-bold text-red-700">{rejected.length}</p>
              <p className="text-sm text-red-600">Rejected</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Accepted Items */}
      {accepted.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-green-700">Accepted Items</CardTitle>
              <CardDescription>Ready to add to catalogue</CardDescription>
            </div>
            <Button onClick={() => onAddItems(accepted)}>
              <Plus className="mr-2" size={16} /> Add All Accepted ({accepted.length})
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {accepted.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium">{item.name}</p>
                    {item.sku && <p className="text-xs text-gray-500">SKU: {item.sku}</p>}
                  </div>
                  <p className="font-semibold">£{item.unitPrice?.toFixed(2)}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Needs Review */}
      {needsReview.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-amber-700">Needs Review</CardTitle>
            <CardDescription>These items have missing or ambiguous fields</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {needsReview.map((item, idx) => (
                <div key={idx} className="p-3 bg-amber-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <p className="font-medium">{item.name || 'Unknown'}</p>
                    <Badge variant="outline" className="text-amber-600">{item.issue}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Rejected */}
      {rejected.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-red-700">Rejected Items</CardTitle>
            <CardDescription>These items could not be processed</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {rejected.map((item, idx) => (
                <div key={idx} className="p-3 bg-red-50 rounded-lg">
                  <p className="text-sm text-red-600">{item.reason}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
