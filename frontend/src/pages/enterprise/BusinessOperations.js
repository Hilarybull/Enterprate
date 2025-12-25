import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader, StatsCard } from '@/components/enterprise';
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
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { 
  Briefcase, 
  CheckSquare,
  Clock,
  Plus,
  Loader2,
  Mail,
  FileText,
  Send,
  Trash2,
  AlertCircle,
  CheckCircle,
  Circle,
  Sparkles,
  Copy,
  Eye,
  ThumbsUp,
  ThumbsDown,
  FileSignature,
  ScrollText,
  Shield,
  Users,
  MessageSquare
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const taskPriorities = [
  { value: 'low', label: 'Low', color: 'bg-gray-100 text-gray-700' },
  { value: 'medium', label: 'Medium', color: 'bg-blue-100 text-blue-700' },
  { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-700' },
  { value: 'urgent', label: 'Urgent', color: 'bg-red-100 text-red-700' },
];

const taskStatuses = [
  { value: 'todo', label: 'To Do', icon: Circle },
  { value: 'in_progress', label: 'In Progress', icon: Clock },
  { value: 'review', label: 'In Review', icon: AlertCircle },
  { value: 'completed', label: 'Completed', icon: CheckCircle },
];

// Document types for AI drafting
const documentCategories = [
  {
    category: 'Business Documents',
    icon: FileSignature,
    types: [
      { id: 'quote', name: 'Quote / Estimate', description: 'Professional quotation template' },
      { id: 'simple_contract', name: 'Simple Contract', description: 'Basic service agreement' },
      { id: 'proposal', name: 'Business Proposal', description: 'Proposal for potential clients' },
      { id: 'invoice_template', name: 'Invoice Template', description: 'Professional invoice layout' },
    ]
  },
  {
    category: 'Compliance Documents',
    icon: Shield,
    types: [
      { id: 'privacy_policy', name: 'Privacy Policy', description: 'GDPR-compliant privacy notice' },
      { id: 'cookie_notice', name: 'Cookie Notice', description: 'Website cookie consent' },
      { id: 'terms_conditions', name: 'Terms & Conditions', description: 'Service terms' },
      { id: 'refund_policy', name: 'Refund Policy', description: 'Return and refund policy' },
    ]
  },
  {
    category: 'HR & Internal Policies',
    icon: Users,
    types: [
      { id: 'employee_handbook', name: 'Employee Handbook', description: 'Basic employee guide' },
      { id: 'remote_work_policy', name: 'Remote Work Policy', description: 'Work from home guidelines' },
      { id: 'leave_policy', name: 'Leave Policy', description: 'Holiday and sick leave' },
      { id: 'code_of_conduct', name: 'Code of Conduct', description: 'Expected behavior guidelines' },
    ]
  },
  {
    category: 'CRM & Sales Documents',
    icon: MessageSquare,
    types: [
      { id: 'welcome_email', name: 'Welcome Email', description: 'New client welcome message' },
      { id: 'follow_up_email', name: 'Follow-up Email', description: 'Sales follow-up template' },
      { id: 'thank_you_note', name: 'Thank You Note', description: 'Client appreciation message' },
      { id: 'meeting_agenda', name: 'Meeting Agenda', description: 'Professional agenda template' },
    ]
  }
];

export default function BusinessOperations() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [activeTab, setActiveTab] = useState('tasks');
  
  // Tasks
  const [tasks, setTasks] = useState([]);
  const [taskStats, setTaskStats] = useState(null);
  const [tasksLoading, setTasksLoading] = useState(true);
  const [showTaskDialog, setShowTaskDialog] = useState(false);
  const [creatingTask, setCreatingTask] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '', description: '', priority: 'medium', dueDate: '', assignee: '', tags: ''
  });

  // Email Templates & Agentic Email
  const [emailTemplates, setEmailTemplates] = useState([]);
  const [emailLogs, setEmailLogs] = useState([]);
  const [pendingEmails, setPendingEmails] = useState([]);
  const [showEmailTemplateDialog, setShowEmailTemplateDialog] = useState(false);
  const [showAgenticEmailDialog, setShowAgenticEmailDialog] = useState(false);
  const [showApprovalDialog, setShowApprovalDialog] = useState(false);
  const [creatingTemplate, setCreatingTemplate] = useState(false);
  const [generatingEmail, setGeneratingEmail] = useState(false);
  const [approvingEmail, setApprovingEmail] = useState(false);
  const [selectedPendingEmail, setSelectedPendingEmail] = useState(null);
  const [newTemplate, setNewTemplate] = useState({
    name: '', subject: '', bodyHtml: '', category: 'general'
  });
  const [agenticEmailRequest, setAgenticEmailRequest] = useState({
    purpose: '',
    recipientName: '',
    recipientEmail: '',
    recipientTitle: '',
    tone: 'professional',
    includeCallToAction: true
  });
  const [generatedEmail, setGeneratedEmail] = useState(null);
  const [editableEmail, setEditableEmail] = useState({ subject: '', body: '' });

  // AI Document Drafting
  const [showDocumentDraftDialog, setShowDocumentDraftDialog] = useState(false);
  const [generatingDocument, setGeneratingDocument] = useState(false);
  const [selectedDocType, setSelectedDocType] = useState(null);
  const [generatedDocument, setGeneratedDocument] = useState(null);
  const [companyProfile, setCompanyProfile] = useState(null);

  useEffect(() => {
    if (currentWorkspace) {
      loadTasks();
      loadEmailTemplates();
      loadEmailLogs();
      loadPendingEmails();
      loadCompanyProfile();
    } else {
      setTasksLoading(false);
    }
  }, [currentWorkspace]);

  // === TASK FUNCTIONS ===
  const loadTasks = async () => {
    try {
      const [tasksRes, statsRes] = await Promise.all([
        axios.get(`${API_URL}/operations/tasks`, { headers: getHeaders() }),
        axios.get(`${API_URL}/operations/tasks/stats`, { headers: getHeaders() })
      ]);
      setTasks(tasksRes.data || []);
      setTaskStats(statsRes.data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
      toast.error('Failed to load tasks');
    } finally {
      setTasksLoading(false);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!newTask.title.trim()) {
      toast.error('Task title is required');
      return;
    }
    setCreatingTask(true);
    try {
      const taskPayload = {
        title: newTask.title.trim(),
        description: newTask.description?.trim() || null,
        priority: newTask.priority || 'medium',
        tags: newTask.tags ? newTask.tags.split(',').map(t => t.trim()).filter(t => t) : []
      };
      
      if (newTask.dueDate) {
        taskPayload.dueDate = newTask.dueDate;
      }
      
      if (newTask.assignee?.trim()) {
        taskPayload.assignee = newTask.assignee.trim();
      }
      
      await axios.post(`${API_URL}/operations/tasks`, taskPayload, { headers: getHeaders() });
      toast.success('Task created!');
      setShowTaskDialog(false);
      setNewTask({ title: '', description: '', priority: 'medium', dueDate: '', assignee: '', tags: '' });
      loadTasks();
    } catch (error) {
      console.error('Task creation error:', error.response?.data || error.message);
      toast.error(error.response?.data?.detail || 'Failed to create task');
    } finally {
      setCreatingTask(false);
    }
  };

  const handleUpdateTaskStatus = async (taskId, newStatus) => {
    try {
      await axios.patch(`${API_URL}/operations/tasks/${taskId}`, { status: newStatus }, { headers: getHeaders() });
      toast.success('Task updated!');
      loadTasks();
    } catch (error) {
      toast.error('Failed to update task');
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await axios.delete(`${API_URL}/operations/tasks/${taskId}`, { headers: getHeaders() });
      toast.success('Task deleted');
      loadTasks();
    } catch (error) {
      toast.error('Failed to delete task');
    }
  };

  // === EMAIL FUNCTIONS ===
  const loadEmailTemplates = async () => {
    try {
      const response = await axios.get(`${API_URL}/operations/email-templates`, { headers: getHeaders() });
      setEmailTemplates(response.data || []);
    } catch (error) {
      console.error('Failed to load email templates:', error);
    }
  };

  const loadEmailLogs = async () => {
    try {
      const response = await axios.get(`${API_URL}/operations/email-logs`, { headers: getHeaders() });
      setEmailLogs(response.data || []);
    } catch (error) {
      console.error('Failed to load email logs:', error);
    }
  };

  const loadPendingEmails = async () => {
    try {
      const response = await axios.get(`${API_URL}/operations/pending-emails`, { headers: getHeaders() });
      setPendingEmails(response.data || []);
    } catch (error) {
      console.error('Failed to load pending emails:', error);
    }
  };

  const loadCompanyProfile = async () => {
    try {
      const response = await axios.get(`${API_URL}/company-profile`, { headers: getHeaders() });
      setCompanyProfile(response.data);
    } catch (error) {
      console.error('Failed to load company profile:', error);
    }
  };

  const handleCreateTemplate = async (e) => {
    e.preventDefault();
    setCreatingTemplate(true);
    try {
      await axios.post(`${API_URL}/operations/email-templates`, newTemplate, { headers: getHeaders() });
      toast.success('Template created!');
      setShowEmailTemplateDialog(false);
      setNewTemplate({ name: '', subject: '', bodyHtml: '', category: 'general' });
      loadEmailTemplates();
    } catch (error) {
      toast.error('Failed to create template');
    } finally {
      setCreatingTemplate(false);
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    try {
      await axios.delete(`${API_URL}/operations/email-templates/${templateId}`, { headers: getHeaders() });
      toast.success('Template deleted');
      loadEmailTemplates();
    } catch (error) {
      toast.error('Failed to delete template');
    }
  };

  // === AGENTIC EMAIL (Human-in-the-loop) ===
  const handleGenerateAgenticEmail = async (e) => {
    e.preventDefault();
    setGeneratingEmail(true);
    try {
      const response = await axios.post(`${API_URL}/operations/generate-email`, {
        ...agenticEmailRequest,
        companyName: companyProfile?.officialProfile?.companyName || companyProfile?.operatingProfile?.companyName || 'Our Company'
      }, { headers: getHeaders() });
      
      setGeneratedEmail(response.data);
      toast.success('Email draft generated! Please review before sending.');
    } catch (error) {
      toast.error('Failed to generate email');
    } finally {
      setGeneratingEmail(false);
    }
  };

  const handleApproveAndSend = async () => {
    if (!generatedEmail) return;
    setApprovingEmail(true);
    try {
      await axios.post(`${API_URL}/operations/send-approved-email`, {
        to: generatedEmail.to || agenticEmailRequest.recipientContext,
        subject: generatedEmail.subject,
        bodyHtml: generatedEmail.body
      }, { headers: getHeaders() });
      
      toast.success('Email approved and sent!');
      setShowAgenticEmailDialog(false);
      setGeneratedEmail(null);
      setAgenticEmailRequest({ purpose: '', recipientContext: '', tone: 'professional', includeCallToAction: true });
      loadEmailLogs();
    } catch (error) {
      toast.error('Failed to send email');
    } finally {
      setApprovingEmail(false);
    }
  };

  const handleRejectEmail = () => {
    setGeneratedEmail(null);
    toast.info('Email rejected. Please regenerate or modify the request.');
  };

  const handleApprovePendingEmail = async (emailId) => {
    try {
      await axios.post(`${API_URL}/operations/approve-email/${emailId}`, {}, { headers: getHeaders() });
      toast.success('Email approved and sent!');
      loadPendingEmails();
      loadEmailLogs();
    } catch (error) {
      toast.error('Failed to approve email');
    }
  };

  const handleRejectPendingEmail = async (emailId) => {
    try {
      await axios.post(`${API_URL}/operations/reject-email/${emailId}`, {}, { headers: getHeaders() });
      toast.info('Email rejected');
      loadPendingEmails();
    } catch (error) {
      toast.error('Failed to reject email');
    }
  };

  // === AI DOCUMENT DRAFTING ===
  const handleGenerateDocument = async (docType) => {
    setSelectedDocType(docType);
    setGeneratingDocument(true);
    setGeneratedDocument(null);
    
    try {
      const response = await axios.post(`${API_URL}/blueprint/generate-document`, {
        documentType: docType.id,
        companyName: companyProfile?.officialProfile?.companyName || companyProfile?.operatingProfile?.companyName || 'Company Name',
        industry: companyProfile?.operatingProfile?.industry || '',
        description: companyProfile?.operatingProfile?.description || ''
      }, { headers: getHeaders() });
      
      setGeneratedDocument(response.data.content);
      setShowDocumentDraftDialog(true);
      toast.success('Document generated!');
    } catch (error) {
      toast.error('Failed to generate document');
    } finally {
      setGeneratingDocument(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  // === STATS ===
  const getPriorityBadge = (priority) => {
    const p = taskPriorities.find(tp => tp.value === priority);
    return p?.color || 'bg-gray-100 text-gray-700';
  };

  const getStatusIcon = (status) => {
    const s = taskStatuses.find(ts => ts.value === status);
    return s?.icon || Circle;
  };

  if (tasksLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-slide-in" data-testid="business-operations-page">
      <PageHeader
        icon={Briefcase}
        title="Business Operations"
        description="Manage tasks, AI-powered email automation, and document drafting"
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard title="Total Tasks" value={taskStats?.total || 0} icon={CheckSquare} gradient="gradient-primary" />
        <StatsCard title="In Progress" value={taskStats?.inProgress || 0} icon={Clock} gradient="gradient-warning" />
        <StatsCard title="Completed" value={taskStats?.completed || 0} icon={CheckCircle} gradient="gradient-success" />
        <StatsCard title="Pending Approvals" value={pendingEmails.length} icon={Mail} gradient="gradient-secondary" />
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
          <TabsTrigger value="email">Email Automation</TabsTrigger>
          <TabsTrigger value="documents">AI Document Drafting</TabsTrigger>
        </TabsList>

        {/* TASKS TAB */}
        <TabsContent value="tasks" className="mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Task Management</CardTitle>
                <CardDescription>Create and track your tasks</CardDescription>
              </div>
              <Button onClick={() => setShowTaskDialog(true)} className="gradient-primary border-0">
                <Plus className="mr-2" size={18} /> Create Task
              </Button>
            </CardHeader>
            <CardContent>
              {tasks.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <CheckSquare className="mx-auto mb-4 text-gray-300" size={48} />
                  <p>No tasks yet. Create your first task!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {tasks.map(task => {
                    const StatusIcon = getStatusIcon(task.status);
                    return (
                      <div key={task.id} className="flex items-center justify-between p-4 rounded-lg border hover:border-purple-200 transition-colors">
                        <div className="flex items-center gap-4">
                          <StatusIcon className={`${task.status === 'completed' ? 'text-green-500' : 'text-gray-400'}`} size={20} />
                          <div>
                            <p className={`font-medium ${task.status === 'completed' ? 'line-through text-gray-400' : ''}`}>
                              {task.title}
                            </p>
                            {task.description && <p className="text-sm text-gray-500">{task.description}</p>}
                            <div className="flex items-center gap-2 mt-1">
                              <span className={`px-2 py-0.5 rounded-full text-xs ${getPriorityBadge(task.priority)}`}>
                                {task.priority}
                              </span>
                              {task.dueDate && (
                                <span className="text-xs text-gray-500">Due: {new Date(task.dueDate).toLocaleDateString()}</span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Select value={task.status} onValueChange={(val) => handleUpdateTaskStatus(task.id, val)}>
                            <SelectTrigger className="w-32">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {taskStatuses.map(s => (
                                <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteTask(task.id)}>
                            <Trash2 size={16} />
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* EMAIL AUTOMATION TAB */}
        <TabsContent value="email" className="mt-6 space-y-6">
          {/* Pending Approvals - Human in the Loop */}
          {pendingEmails.length > 0 && (
            <Card className="border-orange-200 bg-orange-50/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-orange-700">
                  <AlertCircle size={20} />
                  Pending Email Approvals ({pendingEmails.length})
                </CardTitle>
                <CardDescription>AI-generated emails awaiting your approval before sending</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {pendingEmails.map(email => (
                    <div key={email.id} className="p-4 bg-white rounded-lg border">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium">{email.subject}</p>
                          <p className="text-sm text-gray-500">To: {email.to?.join(', ')}</p>
                          <p className="text-xs text-gray-400 mt-1">Generated: {new Date(email.createdAt).toLocaleString()}</p>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => {
                              setSelectedPendingEmail(email);
                              setShowApprovalDialog(true);
                            }}
                          >
                            <Eye size={14} className="mr-1" /> Preview
                          </Button>
                          <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={() => handleApprovePendingEmail(email.id)}>
                            <ThumbsUp size={14} className="mr-1" /> Approve
                          </Button>
                          <Button size="sm" variant="destructive" onClick={() => handleRejectPendingEmail(email.id)}>
                            <ThumbsDown size={14} className="mr-1" /> Reject
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Agentic Email Generator */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="text-purple-600" size={20} />
                AI Email Generator
              </CardTitle>
              <CardDescription>
                Let AI draft your emails. You review and approve before sending (human-in-the-loop).
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => setShowAgenticEmailDialog(true)} className="gradient-primary border-0">
                <Sparkles className="mr-2" size={18} /> Generate Email with AI
              </Button>
            </CardContent>
          </Card>

          {/* Email Templates */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Email Templates</CardTitle>
                <CardDescription>Create reusable email templates</CardDescription>
              </div>
              <Button onClick={() => setShowEmailTemplateDialog(true)} className="gradient-primary border-0">
                <Plus className="mr-2" size={18} /> Create Template
              </Button>
            </CardHeader>
            <CardContent>
              {emailTemplates.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Mail className="mx-auto mb-4 text-gray-300" size={40} />
                  <p>No templates yet</p>
                </div>
              ) : (
                <div className="grid gap-3">
                  {emailTemplates.map(template => (
                    <div key={template.id} className="flex items-center justify-between p-3 rounded-lg border">
                      <div>
                        <p className="font-medium">{template.name}</p>
                        <p className="text-sm text-gray-500">{template.subject}</p>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => handleDeleteTemplate(template.id)}>
                        <Trash2 size={16} />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Email Logs */}
          <Card>
            <CardHeader>
              <CardTitle>Sent Emails</CardTitle>
              <CardDescription>History of sent emails</CardDescription>
            </CardHeader>
            <CardContent>
              {emailLogs.length === 0 ? (
                <p className="text-center py-8 text-gray-500">No emails sent yet</p>
              ) : (
                <div className="space-y-2">
                  {emailLogs.slice(0, 10).map(log => (
                    <div key={log.id} className="flex items-center justify-between p-3 rounded-lg border">
                      <div>
                        <p className="font-medium text-sm">{log.subject}</p>
                        <p className="text-xs text-gray-500">To: {log.to?.join(', ')}</p>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs ${log.status === 'sent' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                        {log.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI DOCUMENT DRAFTING TAB */}
        <TabsContent value="documents" className="mt-6">
          <div className="grid gap-6">
            {documentCategories.map(category => {
              const IconComponent = category.icon;
              return (
                <Card key={category.category}>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <IconComponent className="text-purple-600" size={20} />
                      {category.category}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      {category.types.map(docType => (
                        <div key={docType.id} className="p-4 rounded-lg border hover:border-purple-300 transition-colors">
                          <h4 className="font-medium mb-1">{docType.name}</h4>
                          <p className="text-sm text-gray-500 mb-3">{docType.description}</p>
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="w-full"
                            onClick={() => handleGenerateDocument(docType)}
                            disabled={generatingDocument && selectedDocType?.id === docType.id}
                          >
                            {generatingDocument && selectedDocType?.id === docType.id ? (
                              <><Loader2 className="mr-2 animate-spin" size={14} /> Generating...</>
                            ) : (
                              <><Sparkles className="mr-2" size={14} /> Generate</>
                            )}
                          </Button>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>
      </Tabs>

      {/* CREATE TASK DIALOG */}
      <Dialog open={showTaskDialog} onOpenChange={setShowTaskDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Create Task</DialogTitle></DialogHeader>
          <form onSubmit={handleCreateTask} className="space-y-4">
            <div>
              <Label>Title *</Label>
              <Input 
                value={newTask.title} 
                onChange={e => setNewTask({...newTask, title: e.target.value})}
                placeholder="Task title"
                required
              />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea 
                value={newTask.description} 
                onChange={e => setNewTask({...newTask, description: e.target.value})}
                placeholder="Task description"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Priority</Label>
                <Select value={newTask.priority} onValueChange={val => setNewTask({...newTask, priority: val})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {taskPriorities.map(p => (
                      <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Due Date</Label>
                <Input 
                  type="date" 
                  value={newTask.dueDate} 
                  onChange={e => setNewTask({...newTask, dueDate: e.target.value})}
                />
              </div>
            </div>
            <div>
              <Label>Assignee</Label>
              <Input 
                value={newTask.assignee} 
                onChange={e => setNewTask({...newTask, assignee: e.target.value})}
                placeholder="Assignee name"
              />
            </div>
            <div>
              <Label>Tags (comma-separated)</Label>
              <Input 
                value={newTask.tags} 
                onChange={e => setNewTask({...newTask, tags: e.target.value})}
                placeholder="e.g., urgent, client, marketing"
              />
            </div>
            <Button type="submit" className="w-full gradient-primary border-0" disabled={creatingTask}>
              {creatingTask ? <><Loader2 className="mr-2 animate-spin" size={18} /> Creating...</> : 'Create Task'}
            </Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* EMAIL TEMPLATE DIALOG */}
      <Dialog open={showEmailTemplateDialog} onOpenChange={setShowEmailTemplateDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Create Email Template</DialogTitle></DialogHeader>
          <form onSubmit={handleCreateTemplate} className="space-y-4">
            <div>
              <Label>Template Name</Label>
              <Input 
                value={newTemplate.name} 
                onChange={e => setNewTemplate({...newTemplate, name: e.target.value})}
                placeholder="e.g., Welcome Email"
                required
              />
            </div>
            <div>
              <Label>Subject Line</Label>
              <Input 
                value={newTemplate.subject} 
                onChange={e => setNewTemplate({...newTemplate, subject: e.target.value})}
                placeholder="Email subject"
                required
              />
            </div>
            <div>
              <Label>Email Body (HTML)</Label>
              <Textarea 
                value={newTemplate.bodyHtml} 
                onChange={e => setNewTemplate({...newTemplate, bodyHtml: e.target.value})}
                placeholder="<p>Your email content...</p>"
                rows={6}
                required
              />
            </div>
            <Button type="submit" className="w-full gradient-primary border-0" disabled={creatingTemplate}>
              {creatingTemplate ? <Loader2 className="mr-2 animate-spin" size={18} /> : null}
              Create Template
            </Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* AGENTIC EMAIL DIALOG */}
      <Dialog open={showAgenticEmailDialog} onOpenChange={setShowAgenticEmailDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="text-purple-600" size={20} />
              AI Email Generator
            </DialogTitle>
            <DialogDescription>
              Describe what you need and AI will draft it. You will review before sending.
            </DialogDescription>
          </DialogHeader>
          
          {!generatedEmail ? (
            <form onSubmit={handleGenerateAgenticEmail} className="space-y-4">
              <div>
                <Label>What is this email for?</Label>
                <Textarea 
                  value={agenticEmailRequest.purpose}
                  onChange={e => setAgenticEmailRequest({...agenticEmailRequest, purpose: e.target.value})}
                  placeholder="e.g., Follow up with a potential client about our web design services. They showed interest in our portfolio last week."
                  rows={3}
                  required
                />
              </div>
              <div>
                <Label>Recipient Email / Context</Label>
                <Input 
                  value={agenticEmailRequest.recipientContext}
                  onChange={e => setAgenticEmailRequest({...agenticEmailRequest, recipientContext: e.target.value})}
                  placeholder="e.g., john@company.com or 'Marketing Manager at TechCorp'"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Tone</Label>
                  <Select value={agenticEmailRequest.tone} onValueChange={val => setAgenticEmailRequest({...agenticEmailRequest, tone: val})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="friendly">Friendly</SelectItem>
                      <SelectItem value="formal">Formal</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2">
                    <input 
                      type="checkbox"
                      checked={agenticEmailRequest.includeCallToAction}
                      onChange={e => setAgenticEmailRequest({...agenticEmailRequest, includeCallToAction: e.target.checked})}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm">Include call-to-action</span>
                  </label>
                </div>
              </div>
              <Button type="submit" className="w-full gradient-primary border-0" disabled={generatingEmail}>
                {generatingEmail ? (
                  <><Loader2 className="mr-2 animate-spin" size={18} /> Generating...</>
                ) : (
                  <><Sparkles className="mr-2" size={18} /> Generate Email Draft</>
                )}
              </Button>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-medium text-gray-500 mb-1">Subject:</p>
                <p className="font-medium">{generatedEmail.subject}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg max-h-64 overflow-y-auto">
                <p className="text-sm font-medium text-gray-500 mb-2">Body:</p>
                <div className="prose prose-sm" dangerouslySetInnerHTML={{ __html: generatedEmail.body?.replace(/\n/g, '<br/>') }} />
              </div>
              <DialogFooter className="flex gap-2">
                <Button variant="outline" onClick={handleRejectEmail}>
                  <ThumbsDown className="mr-2" size={16} /> Reject & Redo
                </Button>
                <Button className="bg-green-600 hover:bg-green-700" onClick={handleApproveAndSend} disabled={approvingEmail}>
                  {approvingEmail ? (
                    <><Loader2 className="mr-2 animate-spin" size={16} /> Sending...</>
                  ) : (
                    <><ThumbsUp className="mr-2" size={16} /> Approve & Send</>
                  )}
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* APPROVAL PREVIEW DIALOG */}
      <Dialog open={showApprovalDialog} onOpenChange={setShowApprovalDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Email Preview</DialogTitle>
          </DialogHeader>
          {selectedPendingEmail && (
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-medium text-gray-500">To:</p>
                <p>{selectedPendingEmail.to?.join(', ')}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-medium text-gray-500">Subject:</p>
                <p className="font-medium">{selectedPendingEmail.subject}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg max-h-64 overflow-y-auto">
                <p className="text-sm font-medium text-gray-500 mb-2">Body:</p>
                <div className="prose prose-sm" dangerouslySetInnerHTML={{ __html: selectedPendingEmail.bodyHtml?.replace(/\n/g, '<br/>') }} />
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* DOCUMENT DRAFT DIALOG */}
      <Dialog open={showDocumentDraftDialog} onOpenChange={setShowDocumentDraftDialog}>
        <DialogContent className="max-w-3xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="text-purple-600" size={20} />
              {selectedDocType?.name}
            </DialogTitle>
            <DialogDescription>
              AI-generated document. Review and copy to use.
            </DialogDescription>
          </DialogHeader>
          <div className="bg-gray-50 p-4 rounded-lg overflow-y-auto max-h-[50vh]">
            <pre className="whitespace-pre-wrap text-sm font-mono">{generatedDocument}</pre>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDocumentDraftDialog(false)}>
              Close
            </Button>
            <Button className="gradient-primary border-0" onClick={() => copyToClipboard(generatedDocument)}>
              <Copy className="mr-2" size={16} /> Copy to Clipboard
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
