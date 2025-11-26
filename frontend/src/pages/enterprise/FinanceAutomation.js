import React, { useState, useEffect } from 'react';
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
  TrendingUp
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function FinanceAutomation() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newInvoice, setNewInvoice] = useState({
    clientName: '',
    clientEmail: '',
    amount: '',
    description: '',
    dueDate: ''
  });

  useEffect(() => {
    if (currentWorkspace) {
      loadInvoices();
    } else {
      setLoading(false);
    }
  }, [currentWorkspace]);

  const loadInvoices = async () => {
    try {
      const response = await axios.get(`${API_URL}/navigator/invoices`, {
        headers: getHeaders()
      });
      setInvoices(response.data || []);
    } catch (error) {
      console.error('Failed to load invoices:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInvoice = async (e) => {
    e.preventDefault();
    if (!currentWorkspace) {
      toast.error('Please select a workspace first');
      return;
    }
    setCreating(true);

    try {
      await axios.post(
        `${API_URL}/navigator/invoices`,
        {
          ...newInvoice,
          amount: parseFloat(newInvoice.amount)
        },
        { headers: getHeaders() }
      );
      toast.success('Invoice created successfully!');
      setShowCreateDialog(false);
      setNewInvoice({ clientName: '', clientEmail: '', amount: '', description: '', dueDate: '' });
      loadInvoices();
    } catch (error) {
      toast.error('Failed to create invoice');
      console.error(error);
    } finally {
      setCreating(false);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      DRAFT: 'bg-gray-100 text-gray-700',
      SENT: 'bg-blue-100 text-blue-700',
      PAID: 'bg-green-100 text-green-700',
      OVERDUE: 'bg-red-100 text-red-700',
      CANCELLED: 'bg-gray-100 text-gray-500'
    };
    return styles[status] || styles.DRAFT;
  };

  const stats = {
    total: invoices.length,
    paid: invoices.filter(i => i.status === 'PAID').length,
    pending: invoices.filter(i => i.status !== 'PAID' && i.status !== 'CANCELLED').length,
    totalAmount: invoices.reduce((sum, i) => sum + (i.amount || 0), 0)
  };

  if (loading) {
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
        title="Finance Automation"
        description="Manage invoices, track payments, and automate financial workflows"
        actions={
          <Button 
            onClick={() => setShowCreateDialog(true)}
            className="gradient-primary border-0"
          >
            <Plus className="mr-2" size={18} />
            Create Invoice
          </Button>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Invoices"
          value={stats.total}
          icon={FileText}
          gradient="gradient-primary"
        />
        <StatsCard
          title="Paid"
          value={stats.paid}
          icon={CheckCircle}
          gradient="gradient-success"
        />
        <StatsCard
          title="Pending"
          value={stats.pending}
          icon={Clock}
          gradient="gradient-warning"
        />
        <StatsCard
          title="Total Revenue"
          value={`$${stats.totalAmount.toLocaleString()}`}
          icon={TrendingUp}
          gradient="gradient-primary"
        />
      </div>

      {/* Features */}
      {invoices.length === 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            title="Professional Invoices"
            description="Create and send branded invoices in minutes"
            icon={Receipt}
            gradient="gradient-primary"
          />
          <FeatureCard
            title="Payment Tracking"
            description="Monitor payment status and send reminders"
            icon={CreditCard}
            gradient="gradient-success"
          />
          <FeatureCard
            title="Financial Reports"
            description="Generate revenue reports and insights"
            icon={TrendingUp}
            gradient="gradient-warning"
          />
        </div>
      )}

      {/* Invoices List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Invoices</CardTitle>
          <CardDescription>Manage and track your invoices</CardDescription>
        </CardHeader>
        <CardContent>
          {invoices.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center mx-auto mb-4">
                <FileText className="text-white" size={28} />
              </div>
              <h3 className="font-semibold text-lg mb-2">No Invoices Yet</h3>
              <p className="text-gray-500 mb-4">Create your first invoice to start tracking payments</p>
              <Button onClick={() => setShowCreateDialog(true)} className="gradient-primary border-0">
                <Plus className="mr-2" size={18} />
                Create Invoice
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Invoice #</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Client</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Amount</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Due Date</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Status</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-600">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.map((invoice) => (
                    <tr key={invoice.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <span className="font-mono text-sm">#{invoice.invoiceNumber || invoice.id.slice(0, 8)}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div>
                          <div className="font-medium">{invoice.clientName}</div>
                          <div className="text-sm text-gray-500">{invoice.clientEmail}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4 font-semibold">
                        ${invoice.amount?.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        {invoice.dueDate ? new Date(invoice.dueDate).toLocaleDateString() : '-'}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusBadge(invoice.status)}`}>
                          {invoice.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Button variant="ghost" size="sm">
                          <Send size={14} className="mr-1" />
                          Send
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Invoice Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Create New Invoice</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreateInvoice} className="space-y-4">
            <div>
              <Label htmlFor="clientName">Client Name</Label>
              <Input
                id="clientName"
                value={newInvoice.clientName}
                onChange={(e) => setNewInvoice({ ...newInvoice, clientName: e.target.value })}
                placeholder="John Doe"
                required
              />
            </div>
            <div>
              <Label htmlFor="clientEmail">Client Email</Label>
              <Input
                id="clientEmail"
                type="email"
                value={newInvoice.clientEmail}
                onChange={(e) => setNewInvoice({ ...newInvoice, clientEmail: e.target.value })}
                placeholder="john@example.com"
                required
              />
            </div>
            <div>
              <Label htmlFor="amount">Amount ($)</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                value={newInvoice.amount}
                onChange={(e) => setNewInvoice({ ...newInvoice, amount: e.target.value })}
                placeholder="1000.00"
                required
              />
            </div>
            <div>
              <Label htmlFor="dueDate">Due Date</Label>
              <Input
                id="dueDate"
                type="date"
                value={newInvoice.dueDate}
                onChange={(e) => setNewInvoice({ ...newInvoice, dueDate: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={newInvoice.description}
                onChange={(e) => setNewInvoice({ ...newInvoice, description: e.target.value })}
                placeholder="Services provided..."
                rows={3}
              />
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={creating} className="gradient-primary border-0">
                {creating ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating...</>
                ) : (
                  'Create Invoice'
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
