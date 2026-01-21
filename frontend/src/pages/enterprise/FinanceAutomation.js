import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader, StatsCard, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { 
  DollarSign, 
  Plus, 
  FileText, 
  Send,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  Receipt,
  CreditCard,
  TrendingUp,
  Calculator,
  Shield,
  Camera,
  Trash2,
  Upload,
  Check,
  Edit,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const expenseCategories = [
  { value: 'office', label: 'Office Supplies' },
  { value: 'travel', label: 'Travel' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'software', label: 'Software' },
  { value: 'utilities', label: 'Utilities' },
  { value: 'payroll', label: 'Payroll' },
  { value: 'equipment', label: 'Equipment' },
  { value: 'professional_services', label: 'Professional Services' },
  { value: 'other', label: 'Other' },
];

const complianceCategories = [
  { value: 'tax', label: 'Tax' },
  { value: 'company', label: 'Company Filing' },
  { value: 'accounts', label: 'Accounts' },
  { value: 'payroll', label: 'Payroll' },
  { value: 'insurance', label: 'Insurance' },
  { value: 'legal', label: 'Legal' },
];

export default function FinanceAutomation() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [activeTab, setActiveTab] = useState('invoices');
  
  // Invoices
  const [invoices, setInvoices] = useState([]);
  const [invoicesLoading, setInvoicesLoading] = useState(true);
  const [showInvoiceDialog, setShowInvoiceDialog] = useState(false);
  const [creatingInvoice, setCreatingInvoice] = useState(false);
  const [newInvoice, setNewInvoice] = useState({
    clientName: '', clientEmail: '', amount: '', description: '', dueDate: ''
  });

  // Expenses
  const [expenses, setExpenses] = useState([]);
  const [expenseSummary, setExpenseSummary] = useState(null);
  const [showExpenseDialog, setShowExpenseDialog] = useState(false);
  const [creatingExpense, setCreatingExpense] = useState(false);
  const [newExpense, setNewExpense] = useState({
    description: '', amount: '', category: 'other', date: '', vendor: '', notes: ''
  });

  // Receipt Scanning
  const [scanningReceipt, setScanningReceipt] = useState(false);
  const [scannedData, setScannedData] = useState(null);
  const fileInputRef = useRef(null);

  // Tax Estimation
  const [taxEstimate, setTaxEstimate] = useState(null);
  const [estimatingTax, setEstimatingTax] = useState(false);
  const [taxInput, setTaxInput] = useState({
    annualRevenue: '', annualExpenses: '', businessType: 'sole_proprietor', country: 'UK'
  });

  // Compliance
  const [complianceItems, setComplianceItems] = useState([]);
  const [showComplianceDialog, setShowComplianceDialog] = useState(false);
  const [showEditComplianceDialog, setShowEditComplianceDialog] = useState(false);
  const [creatingCompliance, setCreatingCompliance] = useState(false);
  const [editingCompliance, setEditingCompliance] = useState(null);
  const [newCompliance, setNewCompliance] = useState({
    title: '', description: '', category: 'tax', dueDate: '', priority: 'medium'
  });

  useEffect(() => {
    if (currentWorkspace) {
      loadInvoices();
      loadExpenses();
      loadComplianceItems();
    } else {
      setInvoicesLoading(false);
    }
  }, [currentWorkspace]);

  // === INVOICE FUNCTIONS ===
  const loadInvoices = async () => {
    try {
      const response = await axios.get(`${API_URL}/navigator/invoices`, {
        headers: getHeaders()
      });
      setInvoices(response.data || []);
    } catch (error) {
      console.error('Failed to load invoices:', error);
    } finally {
      setInvoicesLoading(false);
    }
  };

  const handleCreateInvoice = async (e) => {
    e.preventDefault();
    setCreatingInvoice(true);
    try {
      await axios.post(`${API_URL}/navigator/invoices`, {
        ...newInvoice,
        amount: parseFloat(newInvoice.amount)
      }, { headers: getHeaders() });
      toast.success('Invoice created!');
      setShowInvoiceDialog(false);
      setNewInvoice({ clientName: '', clientEmail: '', amount: '', description: '', dueDate: '' });
      loadInvoices();
    } catch (error) {
      toast.error('Failed to create invoice');
    } finally {
      setCreatingInvoice(false);
    }
  };

  // === EXPENSE FUNCTIONS ===
  const loadExpenses = async () => {
    try {
      const [expensesRes, summaryRes] = await Promise.all([
        axios.get(`${API_URL}/finance/expenses`, { headers: getHeaders() }),
        axios.get(`${API_URL}/finance/expenses/summary`, { headers: getHeaders() })
      ]);
      setExpenses(expensesRes.data || []);
      setExpenseSummary(summaryRes.data);
    } catch (error) {
      console.error('Failed to load expenses:', error);
    }
  };

  const handleCreateExpense = async (e) => {
    e.preventDefault();
    setCreatingExpense(true);
    try {
      await axios.post(`${API_URL}/finance/expenses`, {
        ...newExpense,
        amount: parseFloat(newExpense.amount)
      }, { headers: getHeaders() });
      toast.success('Expense added!');
      setShowExpenseDialog(false);
      setNewExpense({ description: '', amount: '', category: 'other', date: '', vendor: '', notes: '' });
      setScannedData(null);
      loadExpenses();
    } catch (error) {
      toast.error('Failed to add expense');
    } finally {
      setCreatingExpense(false);
    }
  };

  const handleDeleteExpense = async (expenseId) => {
    try {
      await axios.delete(`${API_URL}/finance/expenses/${expenseId}`, { headers: getHeaders() });
      toast.success('Expense deleted');
      loadExpenses();
    } catch (error) {
      toast.error('Failed to delete expense');
    }
  };

  // === RECEIPT SCANNING ===
  const handleReceiptUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setScanningReceipt(true);
    setScannedData(null);

    try {
      // Convert to base64
      const reader = new FileReader();
      reader.onload = async () => {
        const base64 = reader.result.split(',')[1];
        
        try {
          const response = await axios.post(`${API_URL}/finance/scan-receipt`, {
            imageBase64: base64,
            filename: file.name
          }, { headers: getHeaders() });

          setScannedData(response.data);
          
          // Pre-fill expense form with scanned data
          if (response.data) {
            setNewExpense(prev => ({
              ...prev,
              vendor: response.data.vendor || '',
              amount: response.data.amount?.toString() || '',
              date: response.data.date || '',
              category: response.data.category || 'other',
              description: response.data.vendor ? `Purchase from ${response.data.vendor}` : ''
            }));
            setShowExpenseDialog(true);
          }
          
          if (response.data.confidence > 0) {
            toast.success('Receipt scanned successfully!');
          } else {
            toast.info('Could not extract data - please enter manually');
          }
        } catch (error) {
          toast.error('Failed to scan receipt');
        } finally {
          setScanningReceipt(false);
        }
      };
      reader.readAsDataURL(file);
    } catch (error) {
      setScanningReceipt(false);
      toast.error('Failed to process receipt');
    }
  };

  // === TAX ESTIMATION ===
  const handleEstimateTax = async (e) => {
    e.preventDefault();
    setEstimatingTax(true);
    try {
      const response = await axios.post(`${API_URL}/finance/estimate-tax`, {
        annualRevenue: parseFloat(taxInput.annualRevenue),
        annualExpenses: parseFloat(taxInput.annualExpenses),
        businessType: taxInput.businessType,
        country: taxInput.country
      }, { headers: getHeaders() });
      setTaxEstimate(response.data);
      toast.success('Tax estimate calculated!');
    } catch (error) {
      toast.error('Failed to estimate tax');
    } finally {
      setEstimatingTax(false);
    }
  };

  // === COMPLIANCE ===
  const loadComplianceItems = async () => {
    try {
      const response = await axios.get(`${API_URL}/finance/compliance`, { headers: getHeaders() });
      setComplianceItems(response.data || []);
    } catch (error) {
      console.error('Failed to load compliance items:', error);
    }
  };

  const handleCreateCompliance = async (e) => {
    e.preventDefault();
    setCreatingCompliance(true);
    try {
      await axios.post(`${API_URL}/finance/compliance`, newCompliance, { headers: getHeaders() });
      toast.success('Compliance item added!');
      setShowComplianceDialog(false);
      setNewCompliance({ title: '', description: '', category: 'tax', dueDate: '', priority: 'medium' });
      loadComplianceItems();
    } catch (error) {
      toast.error('Failed to add compliance item');
    } finally {
      setCreatingCompliance(false);
    }
  };

  const handleToggleCompliance = async (itemId, completed) => {
    try {
      await axios.patch(`${API_URL}/finance/compliance/${itemId}`, { completed: !completed }, { headers: getHeaders() });
      loadComplianceItems();
    } catch (error) {
      toast.error('Failed to update item');
    }
  };

  const handleLoadDefaultCompliance = async () => {
    try {
      const response = await axios.get(`${API_URL}/finance/compliance/defaults`, { headers: getHeaders() });
      const defaults = response.data;
      
      if (!defaults || defaults.length === 0) {
        toast.info('No default checklist items available');
        return;
      }
      
      // Get existing titles to prevent duplicates
      const existingTitles = new Set(complianceItems.map(item => item.title.toLowerCase().trim()));
      
      let successCount = 0;
      let skippedCount = 0;
      let errorCount = 0;
      
      // Create each default item with proper error handling
      for (const item of defaults) {
        const itemTitle = (item.title || 'Untitled Item').toLowerCase().trim();
        
        // Skip if already exists
        if (existingTitles.has(itemTitle)) {
          skippedCount++;
          continue;
        }
        
        try {
          const complianceItem = {
            title: item.title || 'Untitled Item',
            description: item.description || 'No description',
            category: item.category || 'legal',
            priority: item.priority || 'medium',
            dueDate: item.dueDate || null
          };
          
          await axios.post(`${API_URL}/finance/compliance`, complianceItem, { headers: getHeaders() });
          successCount++;
          existingTitles.add(itemTitle);
        } catch (itemError) {
          console.error('Failed to create compliance item:', item.title, itemError);
          errorCount++;
        }
      }
      
      if (successCount > 0) {
        toast.success(`Loaded ${successCount} new compliance items!`);
        loadComplianceItems();
      }
      if (skippedCount > 0) {
        toast.info(`${skippedCount} items already exist`);
      }
      if (errorCount > 0) {
        toast.warning(`${errorCount} items failed to load`);
      }
      if (successCount === 0 && skippedCount > 0) {
        toast.info('All default items are already loaded');
      }
    } catch (error) {
      console.error('Failed to load defaults:', error);
      toast.error('Failed to load default checklist');
    }
  };

  // Edit compliance item
  const handleEditCompliance = (item) => {
    setEditingCompliance({
      id: item.id,
      title: item.title || '',
      description: item.description || '',
      category: item.category || 'tax',
      dueDate: item.dueDate || '',
      priority: item.priority || 'medium'
    });
    setShowEditComplianceDialog(true);
  };

  const handleSaveEditCompliance = async (e) => {
    e.preventDefault();
    if (!editingCompliance) return;
    
    try {
      await axios.patch(`${API_URL}/finance/compliance/${editingCompliance.id}`, {
        title: editingCompliance.title,
        description: editingCompliance.description,
        category: editingCompliance.category,
        dueDate: editingCompliance.dueDate || null,
        priority: editingCompliance.priority
      }, { headers: getHeaders() });
      toast.success('Item updated!');
      setShowEditComplianceDialog(false);
      setEditingCompliance(null);
      loadComplianceItems();
    } catch (error) {
      toast.error('Failed to update item');
    }
  };

  // Delete compliance item
  const handleDeleteCompliance = async (itemId) => {
    if (!window.confirm('Are you sure you want to delete this compliance item?')) return;
    
    try {
      await axios.delete(`${API_URL}/finance/compliance/${itemId}`, { headers: getHeaders() });
      toast.success('Item deleted');
      loadComplianceItems();
    } catch (error) {
      toast.error('Failed to delete item');
    }
  };

  // Auto-populate tax from invoices and expenses using API
  const handleAutoPopulateTax = async () => {
    try {
      const response = await axios.get(`${API_URL}/finance/tax-autofill`, {
        headers: getHeaders()
      });
      
      const data = response.data;
      
      // Determine business type based on revenue
      let businessType = 'sole_proprietor';
      if (data.annualRevenue > 150000) {
        businessType = 'limited_company';
      } else if (data.annualRevenue > 50000) {
        businessType = 'partnership';
      }
      
      setTaxInput({
        ...taxInput,
        annualRevenue: data.annualRevenue?.toFixed(2) || '0.00',
        annualExpenses: data.annualExpenses?.toFixed(2) || '0.00',
        businessType: businessType
      });
      
      // Show details about what was calculated
      const revenueInfo = data.sources?.revenue?.description || '';
      const expenseInfo = data.sources?.expenses?.description || '';
      toast.success(`Tax fields populated for ${data.taxYear}`, {
        description: `${revenueInfo}. ${expenseInfo}`
      });
    } catch (error) {
      console.error('Auto-fill failed:', error);
      toast.error('Failed to auto-fill tax data');
    }
  };

  // === STATS ===
  const invoiceStats = {
    total: invoices.length,
    paid: invoices.filter(i => i.status === 'PAID').length,
    pending: invoices.filter(i => i.status !== 'PAID' && i.status !== 'CANCELLED').length,
    totalAmount: invoices.reduce((sum, i) => sum + (i.amount || 0), 0)
  };

  const getStatusBadge = (status) => {
    const styles = {
      DRAFT: 'bg-gray-100 text-gray-700',
      SENT: 'bg-blue-100 text-blue-700',
      PAID: 'bg-green-100 text-green-700',
      OVERDUE: 'bg-red-100 text-red-700',
      pending: 'bg-yellow-100 text-yellow-700',
      approved: 'bg-green-100 text-green-700',
      rejected: 'bg-red-100 text-red-700'
    };
    return styles[status] || styles.DRAFT;
  };

  if (invoicesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-slide-in" data-testid="finance-automation-page">
      <PageHeader
        icon={DollarSign}
        title="Finance & Compliance"
        description="Manage expenses, invoices, tax estimates, and compliance requirements"
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard title="Total Invoices" value={invoiceStats.total} icon={FileText} gradient="gradient-primary" />
        <StatsCard title="Total Revenue" value={`£${invoiceStats.totalAmount.toLocaleString()}`} icon={TrendingUp} gradient="gradient-success" />
        <StatsCard title="Total Expenses" value={`£${expenseSummary?.totalAmount?.toLocaleString() || 0}`} icon={Receipt} gradient="gradient-warning" />
        <StatsCard title="Compliance Items" value={complianceItems.length} icon={Shield} gradient="gradient-primary" />
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
          <TabsTrigger value="expenses">Expenses</TabsTrigger>
          <TabsTrigger value="tax">Tax Estimator</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
        </TabsList>

        {/* INVOICES TAB */}
        <TabsContent value="invoices" className="mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Invoices</CardTitle>
                <CardDescription>Create and manage your invoices</CardDescription>
              </div>
              <Button onClick={() => setShowInvoiceDialog(true)} className="gradient-primary border-0">
                <Plus className="mr-2" size={18} /> Create Invoice
              </Button>
            </CardHeader>
            <CardContent>
              {invoices.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="mx-auto mb-2 text-gray-300" size={48} />
                  <p className="text-gray-500">No invoices yet. Create your first invoice!</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-medium">Invoice #</th>
                        <th className="text-left py-3 px-4 font-medium">Client</th>
                        <th className="text-right py-3 px-4 font-medium">Amount</th>
                        <th className="text-left py-3 px-4 font-medium">Due Date</th>
                        <th className="text-left py-3 px-4 font-medium">Status</th>
                        <th className="text-right py-3 px-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {invoices.map((invoice) => (
                        <tr key={invoice.id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 font-mono text-sm">#{invoice.invoiceNumber || invoice.id.slice(0, 8)}</td>
                          <td className="py-3 px-4">
                            <div className="font-medium">{invoice.clientName}</div>
                            <div className="text-sm text-gray-500">{invoice.clientEmail}</div>
                          </td>
                          <td className="py-3 px-4 text-right font-semibold">£{invoice.amount?.toLocaleString()}</td>
                          <td className="py-3 px-4 text-gray-600">
                            {invoice.dueDate ? new Date(invoice.dueDate).toLocaleDateString() : '-'}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusBadge(invoice.status)}`}>
                              {invoice.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <Button variant="ghost" size="sm"><Send size={14} className="mr-1" /> Send</Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* EXPENSES TAB */}
        <TabsContent value="expenses" className="mt-6 space-y-6">
          <div className="flex justify-between items-center">
            <div className="flex gap-2">
              <Button onClick={() => setShowExpenseDialog(true)} className="gradient-primary border-0">
                <Plus className="mr-2" size={18} /> Add Expense
              </Button>
              <Button 
                variant="outline" 
                onClick={() => fileInputRef.current?.click()}
                disabled={scanningReceipt}
              >
                {scanningReceipt ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Scanning...</>
                ) : (
                  <><Camera className="mr-2" size={18} /> Scan Receipt</>
                )}
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleReceiptUpload}
              />
            </div>
          </div>

          {/* Expense Summary Cards */}
          {expenseSummary && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(expenseSummary.byCategory || {}).slice(0, 4).map(([cat, amount]) => (
                <Card key={cat}>
                  <CardContent className="p-4">
                    <p className="text-sm text-gray-500 capitalize">{cat.replace('_', ' ')}</p>
                    <p className="text-xl font-bold">£{amount.toLocaleString()}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Expenses</CardTitle>
              <CardDescription>Track and manage your business expenses</CardDescription>
            </CardHeader>
            <CardContent>
              {expenses.length === 0 ? (
                <div className="text-center py-12">
                  <Receipt className="mx-auto mb-2 text-gray-300" size={48} />
                  <p className="text-gray-500">No expenses recorded yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {expenses.map((expense) => (
                    <div key={expense.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                          <Receipt className="text-purple-600" size={20} />
                        </div>
                        <div>
                          <h4 className="font-medium">{expense.description}</h4>
                          <div className="flex items-center space-x-2 text-sm text-gray-500">
                            <span className="capitalize">{expense.category?.replace('_', ' ')}</span>
                            {expense.vendor && <span>• {expense.vendor}</span>}
                            <span>• {expense.date}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className="font-semibold">£{expense.amount?.toLocaleString()}</span>
                        <span className={`text-xs px-2 py-1 rounded-full ${getStatusBadge(expense.status)}`}>
                          {expense.status}
                        </span>
                        <Button variant="ghost" size="sm" onClick={() => handleDeleteExpense(expense.id)}>
                          <Trash2 size={14} className="text-red-500" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAX ESTIMATOR TAB */}
        <TabsContent value="tax" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Tax Calculator</CardTitle>
                <CardDescription>Estimate your UK tax liability</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleEstimateTax} className="space-y-4">
                  {/* Auto-populate button */}
                  <div className="mb-4">
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={handleAutoPopulateTax}
                      className="w-full border-dashed"
                    >
                      <Sparkles className="mr-2" size={16} />
                      Auto-Fill from Invoices & Expenses
                    </Button>
                  </div>
                  <div>
                    <Label>Annual Revenue (£)</Label>
                    <Input
                      type="number"
                      value={taxInput.annualRevenue}
                      onChange={(e) => setTaxInput({ ...taxInput, annualRevenue: e.target.value })}
                      placeholder="100000"
                      required
                    />
                  </div>
                  <div>
                    <Label>Annual Expenses (£)</Label>
                    <Input
                      type="number"
                      value={taxInput.annualExpenses}
                      onChange={(e) => setTaxInput({ ...taxInput, annualExpenses: e.target.value })}
                      placeholder="50000"
                      required
                    />
                  </div>
                  <div>
                    <Label>Business Type</Label>
                    <Select value={taxInput.businessType} onValueChange={(v) => setTaxInput({ ...taxInput, businessType: v })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sole_proprietor">Sole Proprietor</SelectItem>
                        <SelectItem value="partnership">Partnership</SelectItem>
                        <SelectItem value="limited_company">Limited Company</SelectItem>
                        <SelectItem value="corporation">Corporation</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button type="submit" disabled={estimatingTax} className="w-full gradient-primary border-0">
                    {estimatingTax ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Calculator className="mr-2" size={18} />}
                    Calculate Tax
                  </Button>
                </form>
              </CardContent>
            </Card>

            {taxEstimate && (
              <Card>
                <CardHeader>
                  <CardTitle>Tax Estimate</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-purple-50 rounded-lg p-4">
                      <p className="text-sm text-purple-600">Taxable Income</p>
                      <p className="text-2xl font-bold">£{taxEstimate.taxableIncome?.toLocaleString()}</p>
                    </div>
                    <div className="bg-red-50 rounded-lg p-4">
                      <p className="text-sm text-red-600">Estimated Tax</p>
                      <p className="text-2xl font-bold">£{taxEstimate.estimatedTax?.toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Effective Tax Rate</p>
                    <p className="text-xl font-bold">{taxEstimate.effectiveRate}%</p>
                  </div>
                  
                  {taxEstimate.breakdown?.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Tax Breakdown</h4>
                      <div className="space-y-2">
                        {taxEstimate.breakdown.map((b, i) => (
                          <div key={i} className="flex justify-between text-sm">
                            <span>{b.bracket} @ {b.rate}</span>
                            <span>£{b.amount?.toLocaleString()}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {taxEstimate.recommendations?.length > 0 && (
                    <div className="border-t pt-4">
                      <h4 className="font-medium mb-2">Recommendations</h4>
                      <ul className="space-y-1">
                        {taxEstimate.recommendations.map((rec, i) => (
                          <li key={i} className="text-sm text-gray-600 flex items-start">
                            <Check size={14} className="mr-2 mt-0.5 text-green-500" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* COMPLIANCE TAB */}
        <TabsContent value="compliance" className="mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Compliance Checklist</CardTitle>
                <CardDescription>Track your regulatory and filing requirements</CardDescription>
              </div>
              <div className="flex gap-2">
                {complianceItems.length === 0 && (
                  <Button variant="outline" onClick={handleLoadDefaultCompliance}>
                    Load UK Defaults
                  </Button>
                )}
                <Button onClick={() => setShowComplianceDialog(true)} className="gradient-primary border-0">
                  <Plus className="mr-2" size={18} /> Add Item
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {complianceItems.length === 0 ? (
                <div className="text-center py-12">
                  <Shield className="mx-auto mb-2 text-gray-300" size={48} />
                  <p className="text-gray-500 mb-4">No compliance items yet</p>
                  <Button onClick={handleLoadDefaultCompliance}>Load Default UK Checklist</Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {complianceItems.map((item) => (
                    <div key={item.id} className={`flex items-center justify-between p-4 border rounded-lg ${item.completed ? 'bg-green-50 border-green-200' : 'hover:bg-gray-50'}`}>
                      <div className="flex items-center space-x-4">
                        <button
                          onClick={() => handleToggleCompliance(item.id, item.completed)}
                          className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                            item.completed ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300'
                          }`}
                        >
                          {item.completed && <Check size={14} />}
                        </button>
                        <div>
                          <h4 className={`font-medium ${item.completed ? 'line-through text-gray-500' : ''}`}>{item.title}</h4>
                          <p className="text-sm text-gray-500">{item.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          item.priority === 'high' ? 'bg-red-100 text-red-700' :
                          item.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {item.priority}
                        </span>
                        <span className="text-xs text-gray-500 capitalize">{item.category}</span>
                        {item.dueDate && (
                          <span className="text-xs text-gray-500">{new Date(item.dueDate).toLocaleDateString()}</span>
                        )}
                        <Button variant="ghost" size="sm" onClick={() => handleEditCompliance(item)}>
                          <Edit size={14} />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDeleteCompliance(item.id)} className="text-red-500 hover:text-red-700">
                          <Trash2 size={14} />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* CREATE INVOICE DIALOG */}
      <Dialog open={showInvoiceDialog} onOpenChange={setShowInvoiceDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Create Invoice</DialogTitle></DialogHeader>
          <form onSubmit={handleCreateInvoice} className="space-y-4">
            <div>
              <Label>Client Name</Label>
              <Input value={newInvoice.clientName} onChange={(e) => setNewInvoice({ ...newInvoice, clientName: e.target.value })} required />
            </div>
            <div>
              <Label>Client Email</Label>
              <Input type="email" value={newInvoice.clientEmail} onChange={(e) => setNewInvoice({ ...newInvoice, clientEmail: e.target.value })} required />
            </div>
            <div>
              <Label>Amount (£)</Label>
              <Input type="number" step="0.01" value={newInvoice.amount} onChange={(e) => setNewInvoice({ ...newInvoice, amount: e.target.value })} required />
            </div>
            <div>
              <Label>Due Date</Label>
              <Input type="date" value={newInvoice.dueDate} onChange={(e) => setNewInvoice({ ...newInvoice, dueDate: e.target.value })} />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea value={newInvoice.description} onChange={(e) => setNewInvoice({ ...newInvoice, description: e.target.value })} rows={2} />
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowInvoiceDialog(false)}>Cancel</Button>
              <Button type="submit" disabled={creatingInvoice} className="gradient-primary border-0">
                {creatingInvoice ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Create
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* CREATE EXPENSE DIALOG */}
      <Dialog open={showExpenseDialog} onOpenChange={setShowExpenseDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Add Expense</DialogTitle></DialogHeader>
          <form onSubmit={handleCreateExpense} className="space-y-4">
            {scannedData && scannedData.confidence > 0 && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-700">
                <Check size={14} className="inline mr-1" /> Receipt scanned! Review and adjust if needed.
              </div>
            )}
            <div>
              <Label>Description</Label>
              <Input value={newExpense.description} onChange={(e) => setNewExpense({ ...newExpense, description: e.target.value })} required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Amount (£)</Label>
                <Input type="number" step="0.01" value={newExpense.amount} onChange={(e) => setNewExpense({ ...newExpense, amount: e.target.value })} required />
              </div>
              <div>
                <Label>Category</Label>
                <Select value={newExpense.category} onValueChange={(v) => setNewExpense({ ...newExpense, category: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {expenseCategories.map((cat) => (
                      <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Date</Label>
                <Input type="date" value={newExpense.date} onChange={(e) => setNewExpense({ ...newExpense, date: e.target.value })} required />
              </div>
              <div>
                <Label>Vendor</Label>
                <Input value={newExpense.vendor} onChange={(e) => setNewExpense({ ...newExpense, vendor: e.target.value })} />
              </div>
            </div>
            <div>
              <Label>Notes</Label>
              <Textarea value={newExpense.notes} onChange={(e) => setNewExpense({ ...newExpense, notes: e.target.value })} rows={2} />
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => { setShowExpenseDialog(false); setScannedData(null); }}>Cancel</Button>
              <Button type="submit" disabled={creatingExpense} className="gradient-primary border-0">
                {creatingExpense ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Add Expense
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* CREATE COMPLIANCE DIALOG */}
      <Dialog open={showComplianceDialog} onOpenChange={setShowComplianceDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Add Compliance Item</DialogTitle></DialogHeader>
          <form onSubmit={handleCreateCompliance} className="space-y-4">
            <div>
              <Label>Title</Label>
              <Input value={newCompliance.title} onChange={(e) => setNewCompliance({ ...newCompliance, title: e.target.value })} required />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea value={newCompliance.description} onChange={(e) => setNewCompliance({ ...newCompliance, description: e.target.value })} rows={2} required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Category</Label>
                <Select value={newCompliance.category} onValueChange={(v) => setNewCompliance({ ...newCompliance, category: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {complianceCategories.map((cat) => (
                      <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Priority</Label>
                <Select value={newCompliance.priority} onValueChange={(v) => setNewCompliance({ ...newCompliance, priority: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Due Date</Label>
              <Input type="date" value={newCompliance.dueDate} onChange={(e) => setNewCompliance({ ...newCompliance, dueDate: e.target.value })} />
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowComplianceDialog(false)}>Cancel</Button>
              <Button type="submit" disabled={creatingCompliance} className="gradient-primary border-0">
                {creatingCompliance ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Add Item
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* EDIT COMPLIANCE DIALOG */}
      <Dialog open={showEditComplianceDialog} onOpenChange={setShowEditComplianceDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Edit Compliance Item</DialogTitle></DialogHeader>
          {editingCompliance && (
            <form onSubmit={handleSaveEditCompliance} className="space-y-4">
              <div>
                <Label>Title</Label>
                <Input 
                  value={editingCompliance.title} 
                  onChange={(e) => setEditingCompliance({ ...editingCompliance, title: e.target.value })} 
                  required 
                />
              </div>
              <div>
                <Label>Description</Label>
                <Textarea 
                  value={editingCompliance.description} 
                  onChange={(e) => setEditingCompliance({ ...editingCompliance, description: e.target.value })} 
                  rows={2} 
                  required 
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Category</Label>
                  <Select 
                    value={editingCompliance.category} 
                    onValueChange={(v) => setEditingCompliance({ ...editingCompliance, category: v })}
                  >
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {complianceCategories.map((cat) => (
                        <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Priority</Label>
                  <Select 
                    value={editingCompliance.priority} 
                    onValueChange={(v) => setEditingCompliance({ ...editingCompliance, priority: v })}
                  >
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label>Due Date</Label>
                <Input 
                  type="date" 
                  value={editingCompliance.dueDate || ''} 
                  onChange={(e) => setEditingCompliance({ ...editingCompliance, dueDate: e.target.value })} 
                />
              </div>
              <div className="flex justify-end space-x-2 pt-4">
                <Button type="button" variant="outline" onClick={() => setShowEditComplianceDialog(false)}>Cancel</Button>
                <Button type="submit" className="gradient-primary border-0">
                  Save Changes
                </Button>
              </div>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
