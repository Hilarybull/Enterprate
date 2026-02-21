import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  FileText, 
  Plus, 
  Search,
  Edit,
  Send,
  Download,
  Eye,
  Package,
  Loader2,
  Upload,
  Image as ImageIcon,
  CheckCircle,
  Clock,
  AlertCircle,
  X,
  DollarSign,
  Bell,
  TrendingUp
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function Invoicing() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [activeTab, setActiveTab] = useState('invoices');
  const [loading, setLoading] = useState(true);
  const [invoices, setInvoices] = useState([]);
  const [catalogueItems, setCatalogueItems] = useState([]);
  const [brandLogo, setBrandLogo] = useState(null);
  const [paymentSummary, setPaymentSummary] = useState(null);
  const [pendingReminders, setPendingReminders] = useState([]);
  
  // Dialog states
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showPreviewDialog, setShowPreviewDialog] = useState(false);
  const [showLogoDialog, setShowLogoDialog] = useState(false);
  const [showMarkPaidDialog, setShowMarkPaidDialog] = useState(false);
  const [previewInvoice, setPreviewInvoice] = useState(null);
  const [selectedInvoiceForPayment, setSelectedInvoiceForPayment] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    clientName: '',
    clientEmail: '',
    clientAddress: '',
    currency: 'GBP',
    dueDate: '',
    notes: '',
    termsAndConditions: '',
    lineItems: []
  });
  const [searchCatalogue, setSearchCatalogue] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [sendingInvoice, setSendingInvoice] = useState(null);
  const [downloadingPdf, setDownloadingPdf] = useState(null);
  const [markingPaid, setMarkingPaid] = useState(false);
  const [paymentDate, setPaymentDate] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');

  // Load data
  const loadData = useCallback(async () => {
    if (!currentWorkspace) return;
    
    setLoading(true);
    try {
      const [invoicesRes, catalogueRes, brandRes, summaryRes, remindersRes] = await Promise.all([
        axios.get(`${API_URL}/invoices`, { headers: getHeaders() }),
        axios.get(`${API_URL}/catalogue`, { headers: getHeaders() }),
        axios.get(`${API_URL}/invoices/brand/assets/logo`, { headers: getHeaders() }).catch(() => ({ data: null })),
        axios.get(`${API_URL}/invoices/reminders/summary`, { headers: getHeaders() }).catch(() => ({ data: null })),
        axios.get(`${API_URL}/invoices/reminders/pending`, { headers: getHeaders() }).catch(() => ({ data: [] }))
      ]);
      
      setInvoices(invoicesRes.data || []);
      setCatalogueItems(catalogueRes.data || []);
      setBrandLogo(brandRes.data?.imageData ? brandRes.data : null);
      setPaymentSummary(summaryRes.data);
      setPendingReminders(remindersRes.data || []);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace, getHeaders]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Mark invoice as paid
  const handleMarkPaid = async () => {
    if (!selectedInvoiceForPayment) return;
    
    setMarkingPaid(true);
    try {
      await axios.post(
        `${API_URL}/invoices/reminders/${selectedInvoiceForPayment.id}/mark-paid`,
        { paymentDate, paymentMethod },
        { headers: getHeaders() }
      );
      toast.success('Invoice marked as paid');
      setShowMarkPaidDialog(false);
      setSelectedInvoiceForPayment(null);
      setPaymentDate('');
      setPaymentMethod('');
      loadData();
    } catch (error) {
      toast.error('Failed to mark as paid');
    } finally {
      setMarkingPaid(false);
    }
  };

  // Send payment reminder
  const handleSendReminder = async (invoiceId, reminderType = 'first_overdue') => {
    try {
      await axios.post(
        `${API_URL}/invoices/reminders/${invoiceId}/send?reminder_type=${reminderType}`,
        {},
        { headers: getHeaders() }
      );
      toast.success('Payment reminder sent');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send reminder');
    }
  };

  // Add item from catalogue
  const handleAddCatalogueItem = (item) => {
    setFormData(prev => ({
      ...prev,
      lineItems: [...prev.lineItems, {
        catalogueItemId: item.id,
        name: item.name,
        description: item.description || '',
        quantity: 1,
        unitPrice: item.unitPrice,
        taxRate: item.taxRate || 0
      }]
    }));
    setSearchCatalogue('');
    toast.success(`Added "${item.name}" to invoice`);
  };

  // Add manual line item
  const handleAddManualItem = () => {
    setFormData(prev => ({
      ...prev,
      lineItems: [...prev.lineItems, {
        catalogueItemId: null,
        name: '',
        description: '',
        quantity: 1,
        unitPrice: 0,
        taxRate: 0
      }]
    }));
  };

  // Update line item
  const handleUpdateLineItem = (index, field, value) => {
    setFormData(prev => {
      const updated = [...prev.lineItems];
      updated[index] = { ...updated[index], [field]: value };
      return { ...prev, lineItems: updated };
    });
  };

  // Remove line item
  const handleRemoveLineItem = (index) => {
    setFormData(prev => ({
      ...prev,
      lineItems: prev.lineItems.filter((_, i) => i !== index)
    }));
  };

  // Calculate totals
  const calculateTotals = () => {
    let subtotal = 0;
    let taxTotal = 0;
    
    formData.lineItems.forEach(item => {
      const itemSubtotal = (parseFloat(item.quantity) || 0) * (parseFloat(item.unitPrice) || 0);
      const itemTax = itemSubtotal * ((parseFloat(item.taxRate) || 0) / 100);
      subtotal += itemSubtotal;
      taxTotal += itemTax;
    });
    
    return {
      subtotal: subtotal.toFixed(2),
      taxTotal: taxTotal.toFixed(2),
      total: (subtotal + taxTotal).toFixed(2)
    };
  };

  // Create invoice
  const handleCreateInvoice = async (status = 'draft') => {
    if (!formData.clientName || !formData.clientEmail || formData.lineItems.length === 0) {
      toast.error('Please fill in client details and add at least one item');
      return;
    }

    setSubmitting(true);
    try {
      const response = await axios.post(`${API_URL}/invoices`, {
        ...formData,
        status,
        lineItems: formData.lineItems.map(item => ({
          ...item,
          quantity: parseFloat(item.quantity) || 1,
          unitPrice: parseFloat(item.unitPrice) || 0,
          taxRate: parseFloat(item.taxRate) || 0
        }))
      }, { headers: getHeaders() });

      if (response.data) {
        toast.success(`Invoice created as ${status === 'draft' ? 'draft' : 'ready for review'}`);
        setShowCreateDialog(false);
        resetForm();
        loadData();
        
        // If status is pending_review, show preview
        if (status === 'pending_review') {
          setPreviewInvoice(response.data);
          setShowPreviewDialog(true);
        }
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create invoice');
    } finally {
      setSubmitting(false);
    }
  };

  // Download PDF
  const handleDownloadPdf = async (invoiceId) => {
    setDownloadingPdf(invoiceId);
    try {
      const response = await axios.get(`${API_URL}/invoices/${invoiceId}/pdf`, {
        headers: getHeaders(),
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice-${invoiceId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('PDF downloaded');
    } catch (error) {
      toast.error('Failed to download PDF');
    } finally {
      setDownloadingPdf(null);
    }
  };

  // Send invoice email
  const handleSendInvoice = async (invoiceId) => {
    setSendingInvoice(invoiceId);
    try {
      await axios.post(`${API_URL}/invoices/${invoiceId}/send`, {}, { headers: getHeaders() });
      toast.success('Invoice sent successfully');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send invoice');
    } finally {
      setSendingInvoice(null);
    }
  };

  // Upload logo
  const handleLogoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async () => {
      const base64 = reader.result.split(',')[1];
      
      try {
        await axios.post(`${API_URL}/invoices/brand/assets`, {
          assetType: 'logo',
          imageBase64: base64,
          filename: file.name
        }, { headers: getHeaders() });
        
        toast.success('Logo uploaded successfully');
        setShowLogoDialog(false);
        loadData();
      } catch (error) {
        toast.error('Failed to upload logo');
      }
    };
    reader.readAsDataURL(file);
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      clientName: '',
      clientEmail: '',
      clientAddress: '',
      currency: 'GBP',
      dueDate: '',
      notes: '',
      termsAndConditions: '',
      lineItems: []
    });
  };

  // Filter catalogue items
  const filteredCatalogue = searchCatalogue 
    ? catalogueItems.filter(item => 
        item.name?.toLowerCase().includes(searchCatalogue.toLowerCase()) ||
        item.sku?.toLowerCase().includes(searchCatalogue.toLowerCase())
      )
    : [];

  const currencySymbol = formData.currency === 'GBP' ? '£' : formData.currency === 'USD' ? '$' : '€';

  const getStatusBadge = (status) => {
    const styles = {
      draft: { bg: 'bg-gray-100', text: 'text-gray-700', icon: Edit },
      pending_review: { bg: 'bg-amber-100', text: 'text-amber-700', icon: Eye },
      sent: { bg: 'bg-blue-100', text: 'text-blue-700', icon: Send },
      paid: { bg: 'bg-green-100', text: 'text-green-700', icon: CheckCircle },
      overdue: { bg: 'bg-red-100', text: 'text-red-700', icon: AlertCircle }
    };
    const style = styles[status] || styles.draft;
    const Icon = style.icon;
    return (
      <Badge className={`${style.bg} ${style.text}`}>
        <Icon size={12} className="mr-1" />
        {status?.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  const totals = calculateTotals();

  return (
    <div className="space-y-6 animate-slide-in" data-testid="invoicing-page">
      <PageHeader
        icon={FileText}
        title="Invoicing"
        description="Create professional invoices with catalogue integration, download PDFs, and send via email"
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setShowLogoDialog(true)}>
              <ImageIcon className="mr-2" size={16} />
              {brandLogo ? 'Update Logo' : 'Upload Logo'}
            </Button>
            <Button className="gradient-primary border-0" onClick={() => setShowCreateDialog(true)}>
              <Plus className="mr-2" size={16} />
              Create Invoice
            </Button>
          </div>
        }
      />

      {/* Payment Summary Cards */}
      {paymentSummary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Outstanding</p>
                  <p className="text-2xl font-bold text-amber-600">
                    £{paymentSummary.totalOutstanding?.toFixed(2) || '0.00'}
                  </p>
                </div>
                <Clock className="text-amber-500" size={24} />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Collected</p>
                  <p className="text-2xl font-bold text-green-600">
                    £{paymentSummary.totalCollected?.toFixed(2) || '0.00'}
                  </p>
                </div>
                <CheckCircle className="text-green-500" size={24} />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Overdue</p>
                  <p className="text-2xl font-bold text-red-600">
                    {paymentSummary.overdueCount || 0}
                  </p>
                </div>
                <AlertCircle className="text-red-500" size={24} />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Pending Reminders</p>
                  <p className="text-2xl font-bold text-indigo-600">
                    {pendingReminders.length}
                  </p>
                </div>
                <Bell className="text-indigo-500" size={24} />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="invoices">
            <FileText size={16} className="mr-2" />
            All Invoices ({invoices.length})
          </TabsTrigger>
          <TabsTrigger value="drafts">
            <Edit size={16} className="mr-2" />
            Drafts ({invoices.filter(i => i.status === 'draft').length})
          </TabsTrigger>
          <TabsTrigger value="sent">
            <Send size={16} className="mr-2" />
            Sent ({invoices.filter(i => ['sent', 'paid'].includes(i.status)).length})
          </TabsTrigger>
          <TabsTrigger value="overdue">
            <AlertCircle size={16} className="mr-2" />
            Overdue ({invoices.filter(i => i.status === 'overdue').length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="invoices" className="space-y-4 mt-4">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
            </div>
          ) : invoices.length > 0 ? (
            <div className="space-y-3">
              {invoices.map((invoice) => (
                <Card key={invoice.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold">{invoice.invoiceNumber}</h3>
                          {getStatusBadge(invoice.status)}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {invoice.clientName} • {invoice.clientEmail}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          Created: {new Date(invoice.createdAt).toLocaleDateString()}
                          {invoice.dueDate && ` • Due: ${new Date(invoice.dueDate).toLocaleDateString()}`}
                        </p>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-lg font-bold">
                            {invoice.currency === 'GBP' ? '£' : invoice.currency === 'USD' ? '$' : '€'}
                            {invoice.total?.toFixed(2)}
                          </p>
                          <p className="text-xs text-gray-500">{invoice.lineItems?.length || 0} items</p>
                        </div>
                        <div className="flex gap-1">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleDownloadPdf(invoice.id)}
                            disabled={downloadingPdf === invoice.id}
                          >
                            {downloadingPdf === invoice.id ? (
                              <Loader2 size={16} className="animate-spin" />
                            ) : (
                              <Download size={16} />
                            )}
                          </Button>
                          {['draft', 'pending_review'].includes(invoice.status) && (
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => handleSendInvoice(invoice.id)}
                              disabled={sendingInvoice === invoice.id}
                            >
                              {sendingInvoice === invoice.id ? (
                                <Loader2 size={16} className="animate-spin" />
                              ) : (
                                <Send size={16} />
                              )}
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-12 text-center">
              <FileText className="mx-auto text-gray-300 mb-4" size={48} />
              <h3 className="text-lg font-medium text-gray-700">No Invoices Yet</h3>
              <p className="text-gray-500 mt-1">Create your first invoice to get started</p>
              <Button className="mt-4" onClick={() => setShowCreateDialog(true)}>
                <Plus className="mr-2" size={16} /> Create Invoice
              </Button>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="drafts" className="space-y-4 mt-4">
          {invoices.filter(i => i.status === 'draft').length > 0 ? (
            <div className="space-y-3">
              {invoices.filter(i => i.status === 'draft').map((invoice) => (
                <Card key={invoice.id} className="hover:shadow-md transition-shadow border-l-4 border-l-gray-400">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">{invoice.invoiceNumber}</h3>
                        <p className="text-sm text-gray-600">{invoice.clientName}</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <p className="font-bold">£{invoice.total?.toFixed(2)}</p>
                        <Button variant="outline" size="sm" onClick={() => handleSendInvoice(invoice.id)}>
                          <Send size={14} className="mr-1" /> Finalize & Send
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-8 text-center">
              <p className="text-gray-500">No draft invoices</p>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="sent" className="space-y-4 mt-4">
          {invoices.filter(i => ['sent', 'paid'].includes(i.status)).length > 0 ? (
            <div className="space-y-3">
              {invoices.filter(i => ['sent', 'paid'].includes(i.status)).map((invoice) => (
                <Card key={invoice.id} className={`hover:shadow-md transition-shadow border-l-4 ${invoice.status === 'paid' ? 'border-l-green-500' : 'border-l-blue-500'}`}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold">{invoice.invoiceNumber}</h3>
                          {getStatusBadge(invoice.status)}
                        </div>
                        <p className="text-sm text-gray-600">{invoice.clientName}</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <p className="font-bold">£{invoice.total?.toFixed(2)}</p>
                        <div className="flex gap-1">
                          <Button variant="outline" size="sm" onClick={() => handleDownloadPdf(invoice.id)}>
                            <Download size={14} className="mr-1" /> PDF
                          </Button>
                          {invoice.status === 'sent' && (
                            <Button 
                              variant="outline" 
                              size="sm"
                              className="text-green-600 border-green-200 hover:bg-green-50"
                              onClick={() => {
                                setSelectedInvoiceForPayment(invoice);
                                setShowMarkPaidDialog(true);
                              }}
                            >
                              <DollarSign size={14} className="mr-1" /> Mark Paid
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-8 text-center">
              <p className="text-gray-500">No sent invoices</p>
            </Card>
          )}
        </TabsContent>

        {/* Overdue Tab */}
        <TabsContent value="overdue" className="space-y-4 mt-4">
          {invoices.filter(i => i.status === 'overdue').length > 0 ? (
            <div className="space-y-3">
              {invoices.filter(i => i.status === 'overdue').map((invoice) => (
                <Card key={invoice.id} className="hover:shadow-md transition-shadow border-l-4 border-l-red-500">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold">{invoice.invoiceNumber}</h3>
                          {getStatusBadge(invoice.status)}
                        </div>
                        <p className="text-sm text-gray-600">{invoice.clientName} • {invoice.clientEmail}</p>
                        <p className="text-xs text-red-500 mt-1">
                          Due: {invoice.dueDate} • Last reminder: {invoice.lastReminderType || 'None sent'}
                        </p>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="font-bold text-red-600">£{invoice.total?.toFixed(2)}</p>
                        </div>
                        <div className="flex gap-1">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleSendReminder(invoice.id, 'first_overdue')}
                          >
                            <Bell size={14} className="mr-1" /> Send Reminder
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            className="text-green-600 border-green-200 hover:bg-green-50"
                            onClick={() => {
                              setSelectedInvoiceForPayment(invoice);
                              setShowMarkPaidDialog(true);
                            }}
                          >
                            <DollarSign size={14} className="mr-1" /> Mark Paid
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-8 text-center">
              <CheckCircle className="mx-auto text-green-300 mb-4" size={48} />
              <p className="text-gray-500">No overdue invoices - Great job!</p>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Create Invoice Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Invoice</DialogTitle>
            <DialogDescription>
              Add items from your catalogue or create custom line items
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Client Details */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Client Name *</Label>
                <Input
                  value={formData.clientName}
                  onChange={(e) => setFormData({ ...formData, clientName: e.target.value })}
                  placeholder="Client or Company Name"
                />
              </div>
              <div>
                <Label>Client Email *</Label>
                <Input
                  type="email"
                  value={formData.clientEmail}
                  onChange={(e) => setFormData({ ...formData, clientEmail: e.target.value })}
                  placeholder="client@example.com"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label>Client Address</Label>
                <Input
                  value={formData.clientAddress}
                  onChange={(e) => setFormData({ ...formData, clientAddress: e.target.value })}
                  placeholder="Street, City, Postcode"
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
              <div>
                <Label>Due Date</Label>
                <Input
                  type="date"
                  value={formData.dueDate}
                  onChange={(e) => setFormData({ ...formData, dueDate: e.target.value })}
                />
              </div>
            </div>

            {/* Add from Catalogue */}
            <Card className="bg-slate-50">
              <CardHeader className="py-3">
                <CardTitle className="text-sm flex items-center">
                  <Package size={16} className="mr-2" />
                  Add from Catalogue
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search catalogue items..."
                    value={searchCatalogue}
                    onChange={(e) => setSearchCatalogue(e.target.value)}
                    className="pl-10"
                  />
                </div>
                {filteredCatalogue.length > 0 && (
                  <div className="mt-2 border rounded-lg max-h-40 overflow-y-auto bg-white">
                    {filteredCatalogue.map((item) => (
                      <div 
                        key={item.id}
                        className="p-2 hover:bg-gray-50 cursor-pointer flex justify-between items-center border-b last:border-b-0"
                        onClick={() => handleAddCatalogueItem(item)}
                      >
                        <div>
                          <p className="font-medium text-sm">{item.name}</p>
                          <p className="text-xs text-gray-500">{item.sku || 'No SKU'}</p>
                        </div>
                        <p className="font-semibold">{currencySymbol}{item.unitPrice?.toFixed(2)}</p>
                      </div>
                    ))}
                  </div>
                )}
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="mt-2"
                  onClick={handleAddManualItem}
                >
                  <Plus size={14} className="mr-1" /> Add Custom Item
                </Button>
              </CardContent>
            </Card>

            {/* Line Items */}
            {formData.lineItems.length > 0 && (
              <div className="space-y-3">
                <Label>Line Items</Label>
                {formData.lineItems.map((item, index) => (
                  <div key={index} className="flex items-start gap-2 p-3 border rounded-lg bg-white">
                    <div className="flex-1 grid grid-cols-5 gap-2">
                      <div className="col-span-2">
                        <Input
                          placeholder="Item name"
                          value={item.name}
                          onChange={(e) => handleUpdateLineItem(index, 'name', e.target.value)}
                        />
                      </div>
                      <Input
                        type="number"
                        placeholder="Qty"
                        value={item.quantity}
                        onChange={(e) => handleUpdateLineItem(index, 'quantity', e.target.value)}
                        className="w-20"
                      />
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="Price"
                        value={item.unitPrice}
                        onChange={(e) => handleUpdateLineItem(index, 'unitPrice', e.target.value)}
                      />
                      <Input
                        type="number"
                        placeholder="Tax %"
                        value={item.taxRate}
                        onChange={(e) => handleUpdateLineItem(index, 'taxRate', e.target.value)}
                        className="w-20"
                      />
                    </div>
                    <div className="text-right min-w-[80px]">
                      <p className="font-semibold">
                        {currencySymbol}{((parseFloat(item.quantity) || 0) * (parseFloat(item.unitPrice) || 0) * (1 + (parseFloat(item.taxRate) || 0) / 100)).toFixed(2)}
                      </p>
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => handleRemoveLineItem(index)}>
                      <X size={16} className="text-red-500" />
                    </Button>
                  </div>
                ))}
              </div>
            )}

            {/* Totals */}
            {formData.lineItems.length > 0 && (
              <div className="flex justify-end">
                <div className="w-64 space-y-2 text-right">
                  <div className="flex justify-between text-sm">
                    <span>Subtotal:</span>
                    <span>{currencySymbol}{totals.subtotal}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Tax:</span>
                    <span>{currencySymbol}{totals.taxTotal}</span>
                  </div>
                  <div className="flex justify-between font-bold text-lg border-t pt-2">
                    <span>Total:</span>
                    <span>{currencySymbol}{totals.total}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Notes */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Notes</Label>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Payment instructions, thank you message..."
                  rows={3}
                />
              </div>
              <div>
                <Label>Terms & Conditions</Label>
                <Textarea
                  value={formData.termsAndConditions}
                  onChange={(e) => setFormData({ ...formData, termsAndConditions: e.target.value })}
                  placeholder="Payment terms, late fees..."
                  rows={3}
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => { setShowCreateDialog(false); resetForm(); }}>
              Cancel
            </Button>
            <Button 
              variant="outline"
              onClick={() => handleCreateInvoice('draft')} 
              disabled={submitting}
            >
              {submitting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Save as Draft
            </Button>
            <Button 
              className="gradient-primary border-0"
              onClick={() => handleCreateInvoice('pending_review')} 
              disabled={submitting}
            >
              {submitting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Review & Send
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Logo Upload Dialog */}
      <Dialog open={showLogoDialog} onOpenChange={setShowLogoDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Brand Logo</DialogTitle>
            <DialogDescription>
              Your logo will appear on all invoices
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            {brandLogo && (
              <div className="mb-4 p-4 border rounded-lg text-center">
                <img 
                  src={`data:image/png;base64,${brandLogo.imageData}`} 
                  alt="Current logo" 
                  className="max-h-20 mx-auto"
                />
                <p className="text-sm text-gray-500 mt-2">Current logo: {brandLogo.filename}</p>
              </div>
            )}
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <input
                type="file"
                accept="image/*"
                onChange={handleLogoUpload}
                className="hidden"
                id="logo-upload"
              />
              <label htmlFor="logo-upload" className="cursor-pointer">
                <Upload className="mx-auto text-gray-400 mb-2" size={32} />
                <p className="text-gray-600">Click to upload a new logo</p>
                <p className="text-xs text-gray-400 mt-1">PNG, JPG, or SVG recommended</p>
              </label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLogoDialog(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog open={showPreviewDialog} onOpenChange={setShowPreviewDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Invoice Created</DialogTitle>
            <DialogDescription>
              Review your invoice before sending
            </DialogDescription>
          </DialogHeader>
          {previewInvoice && (
            <div className="py-4 space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-bold">{previewInvoice.invoiceNumber}</h3>
                    <p className="text-gray-600">{previewInvoice.clientName}</p>
                    <p className="text-sm text-gray-500">{previewInvoice.clientEmail}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-indigo-600">
                      £{previewInvoice.total?.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-500">
                      Due: {previewInvoice.dueDate || 'Upon receipt'}
                    </p>
                  </div>
                </div>
              </div>
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Invoice is ready to send. Click &quot;Send Invoice&quot; to email it to the client.
                </AlertDescription>
              </Alert>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPreviewDialog(false)}>Close</Button>
            <Button 
              variant="outline"
              onClick={() => {
                handleDownloadPdf(previewInvoice?.id);
              }}
            >
              <Download size={16} className="mr-2" /> Download PDF
            </Button>
            <Button 
              className="gradient-primary border-0"
              onClick={() => {
                handleSendInvoice(previewInvoice?.id);
                setShowPreviewDialog(false);
              }}
            >
              <Send size={16} className="mr-2" /> Send Invoice
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
