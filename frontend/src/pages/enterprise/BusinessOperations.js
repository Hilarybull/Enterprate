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
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { 
  Briefcase, 
  Users, 
  Calendar, 
  CheckSquare,
  Clock,
  BarChart3,
  Workflow,
  Settings2,
  Plus,
  Loader2,
  Mail,
  FileText,
  Send,
  Trash2,
  AlertCircle,
  CheckCircle,
  Circle,
  FolderOpen
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

const documentTypes = [
  { value: 'pdf', label: 'PDF Document' },
  { value: 'doc', label: 'Word Document' },
  { value: 'spreadsheet', label: 'Spreadsheet' },
  { value: 'presentation', label: 'Presentation' },
  { value: 'other', label: 'Other' },
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

  // Email Templates
  const [emailTemplates, setEmailTemplates] = useState([]);
  const [emailLogs, setEmailLogs] = useState([]);
  const [showEmailTemplateDialog, setShowEmailTemplateDialog] = useState(false);
  const [showSendEmailDialog, setShowSendEmailDialog] = useState(false);
  const [creatingTemplate, setCreatingTemplate] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);
  const [newTemplate, setNewTemplate] = useState({
    name: '', subject: '', bodyHtml: '', category: 'general'
  });
  const [emailToSend, setEmailToSend] = useState({
    to: '', subject: '', bodyHtml: '', templateId: ''
  });

  // Documents
  const [documents, setDocuments] = useState([]);
  const [showDocumentDialog, setShowDocumentDialog] = useState(false);
  const [creatingDocument, setCreatingDocument] = useState(false);
  const [newDocument, setNewDocument] = useState({
    name: '', type: 'pdf', description: '', category: 'general', tags: ''
  });

  // Workflows
  const [workflows, setWorkflows] = useState([]);
  const [defaultWorkflows, setDefaultWorkflows] = useState([]);

  useEffect(() => {
    if (currentWorkspace) {
      loadTasks();
      loadEmailTemplates();
      loadEmailLogs();
      loadDocuments();
      loadWorkflows();
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
    } finally {
      setTasksLoading(false);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    setCreatingTask(true);
    try {
      // Build task payload with only non-empty values
      const taskPayload = {
        title: newTask.title.trim(),
        description: newTask.description?.trim() || null,
        priority: newTask.priority || 'medium',
        tags: newTask.tags ? newTask.tags.split(',').map(t => t.trim()).filter(t => t) : []
      };
      
      // Only add dueDate if it has a value
      if (newTask.dueDate) {
        taskPayload.dueDate = newTask.dueDate;
      }
      
      // Only add assignee if it has a value
      if (newTask.assignee?.trim()) {
        taskPayload.assignee = newTask.assignee.trim();
      }
      
      const response = await axios.post(`${API_URL}/operations/tasks`, taskPayload, { headers: getHeaders() });
      
      if (response.data) {
        toast.success('Task created!');
        setShowTaskDialog(false);
        setNewTask({ title: '', description: '', priority: 'medium', dueDate: '', assignee: '', tags: '' });
        loadTasks();
      }
    } catch (error) {
      console.error('Task creation error:', error.response?.data || error.message);
      const errorMessage = error.response?.data?.detail || 'Failed to create task';
      toast.error(errorMessage);
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

  const handleSendEmail = async (e) => {
    e.preventDefault();
    setSendingEmail(true);
    try {
      const response = await axios.post(`${API_URL}/operations/send-email`, {
        to: emailToSend.to.split(',').map(e => e.trim()),
        subject: emailToSend.subject,
        bodyHtml: emailToSend.bodyHtml,
        templateId: emailToSend.templateId || null
      }, { headers: getHeaders() });
      
      toast.success(response.data.message);
      setShowSendEmailDialog(false);
      setEmailToSend({ to: '', subject: '', bodyHtml: '', templateId: '' });
      loadEmailLogs();
    } catch (error) {
      toast.error('Failed to send email');
    } finally {
      setSendingEmail(false);
    }
  };

  const handleSelectTemplate = (templateId) => {
    const template = emailTemplates.find(t => t.id === templateId);
    if (template) {
      setEmailToSend(prev => ({
        ...prev,
        templateId: templateId,
        subject: template.subject,
        bodyHtml: template.bodyHtml
      }));
    }
  };

  // === DOCUMENT FUNCTIONS ===
  const loadDocuments = async () => {
    try {
      const response = await axios.get(`${API_URL}/operations/documents`, { headers: getHeaders() });
      setDocuments(response.data || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const handleCreateDocument = async (e) => {
    e.preventDefault();
    setCreatingDocument(true);
    try {
      await axios.post(`${API_URL}/operations/documents`, {
        ...newDocument,
        tags: newDocument.tags ? newDocument.tags.split(',').map(t => t.trim()) : []
      }, { headers: getHeaders() });
      toast.success('Document added!');
      setShowDocumentDialog(false);
      setNewDocument({ name: '', type: 'pdf', description: '', category: 'general', tags: '' });
      loadDocuments();
    } catch (error) {
      toast.error('Failed to add document');
    } finally {
      setCreatingDocument(false);
    }
  };

  const handleDeleteDocument = async (docId) => {
    try {
      await axios.delete(`${API_URL}/operations/documents/${docId}`, { headers: getHeaders() });
      toast.success('Document deleted');
      loadDocuments();
    } catch (error) {
      toast.error('Failed to delete document');
    }
  };

  // === WORKFLOW FUNCTIONS ===
  const loadWorkflows = async () => {
    try {
      const [workflowsRes, defaultsRes] = await Promise.all([
        axios.get(`${API_URL}/operations/workflows`, { headers: getHeaders() }),
        axios.get(`${API_URL}/operations/workflows/defaults`, { headers: getHeaders() })
      ]);
      setWorkflows(workflowsRes.data || []);
      setDefaultWorkflows(defaultsRes.data || []);
    } catch (error) {
      console.error('Failed to load workflows:', error);
    }
  };

  const handleAddDefaultWorkflow = async (workflow) => {
    try {
      await axios.post(`${API_URL}/operations/workflows`, {
        name: workflow.name,
        description: workflow.description,
        category: workflow.category,
        steps: workflow.steps,
        trigger: workflow.trigger
      }, { headers: getHeaders() });
      toast.success('Workflow added!');
      loadWorkflows();
    } catch (error) {
      toast.error('Failed to add workflow');
    }
  };

  const getPriorityColor = (priority) => {
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
        description="Manage tasks, automate emails, organize documents, and streamline workflows"
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard title="Total Tasks" value={taskStats?.total || 0} icon={CheckSquare} gradient="gradient-primary" />
        <StatsCard title="In Progress" value={taskStats?.byStatus?.in_progress || 0} icon={Clock} gradient="gradient-warning" />
        <StatsCard title="Completed" value={taskStats?.byStatus?.completed || 0} icon={CheckCircle} gradient="gradient-success" />
        <StatsCard title="Completion Rate" value={`${taskStats?.completionRate || 0}%`} icon={BarChart3} gradient="gradient-primary" />
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
          <TabsTrigger value="email">Email Automation</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
        </TabsList>

        {/* TASKS TAB */}
        <TabsContent value="tasks" className="mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Task Management</CardTitle>
                <CardDescription>Create and track tasks for your team</CardDescription>
              </div>
              <Button onClick={() => setShowTaskDialog(true)} className="gradient-primary border-0">
                <Plus className="mr-2" size={18} /> Add Task
              </Button>
            </CardHeader>
            <CardContent>
              {tasks.length === 0 ? (
                <div className="text-center py-12">
                  <CheckSquare className="mx-auto mb-2 text-gray-300" size={48} />
                  <p className="text-gray-500">No tasks yet. Create your first task!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {tasks.map((task) => {
                    const StatusIcon = getStatusIcon(task.status);
                    return (
                      <div key={task.id} className={`flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 ${task.status === 'completed' ? 'bg-green-50 border-green-200' : ''}`}>
                        <div className="flex items-center space-x-4">
                          <StatusIcon size={20} className={task.status === 'completed' ? 'text-green-500' : 'text-gray-400'} />
                          <div>
                            <h4 className={`font-medium ${task.status === 'completed' ? 'line-through text-gray-500' : ''}`}>{task.title}</h4>
                            {task.description && <p className="text-sm text-gray-500 line-clamp-1">{task.description}</p>}
                            <div className="flex items-center space-x-2 mt-1">
                              {task.dueDate && (
                                <span className="text-xs text-gray-500 flex items-center">
                                  <Calendar size={12} className="mr-1" />
                                  {new Date(task.dueDate).toLocaleDateString()}
                                </span>
                              )}
                              {task.tags?.length > 0 && (
                                <span className="text-xs text-purple-600">{task.tags.join(', ')}</span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(task.priority)}`}>
                            {task.priority}
                          </span>
                          <Select value={task.status} onValueChange={(v) => handleUpdateTaskStatus(task.id, v)}>
                            <SelectTrigger className="w-[130px] h-8 text-xs">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {taskStatuses.map((s) => (
                                <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteTask(task.id)}>
                            <Trash2 size={14} className="text-red-500" />
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

        {/* EMAIL TAB */}
        <TabsContent value="email" className="mt-6 space-y-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="text-yellow-600 flex-shrink-0" size={20} />
            <div>
              <p className="font-medium text-yellow-800">Email Automation is in Demo Mode</p>
              <p className="text-sm text-yellow-700">Emails are logged but not actually sent. To enable real sending, configure your SendGrid API key in the backend.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Templates */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Email Templates</CardTitle>
                  <CardDescription>Reusable email templates</CardDescription>
                </div>
                <Button onClick={() => setShowEmailTemplateDialog(true)} size="sm">
                  <Plus className="mr-1" size={14} /> Template
                </Button>
              </CardHeader>
              <CardContent>
                {emailTemplates.length === 0 ? (
                  <p className="text-center text-gray-500 py-6">No templates yet</p>
                ) : (
                  <div className="space-y-2">
                    {emailTemplates.map((template) => (
                      <div key={template.id} className="p-3 border rounded-lg hover:bg-gray-50">
                        <h4 className="font-medium">{template.name}</h4>
                        <p className="text-sm text-gray-500">{template.subject}</p>
                        <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{template.category}</span>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Send Email */}
            <Card>
              <CardHeader>
                <CardTitle>Send Email</CardTitle>
                <CardDescription>Compose and send emails</CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => setShowSendEmailDialog(true)} className="w-full gradient-primary border-0">
                  <Mail className="mr-2" size={18} /> Compose Email
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Email Logs */}
          <Card>
            <CardHeader>
              <CardTitle>Email History</CardTitle>
              <CardDescription>Recent email activity</CardDescription>
            </CardHeader>
            <CardContent>
              {emailLogs.length === 0 ? (
                <p className="text-center text-gray-500 py-6">No emails sent yet</p>
              ) : (
                <div className="space-y-2">
                  {emailLogs.map((log) => (
                    <div key={log.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <h4 className="font-medium">{log.subject}</h4>
                        <p className="text-sm text-gray-500">To: {log.to?.join(', ')}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs px-2 py-1 rounded-full ${log.status === 'sent' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {log.mock ? '[MOCK] ' : ''}{log.status}
                        </span>
                        <span className="text-xs text-gray-500">{new Date(log.sentAt).toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* DOCUMENTS TAB */}
        <TabsContent value="documents" className="mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Document Management</CardTitle>
                <CardDescription>Organize and manage your business documents</CardDescription>
              </div>
              <Button onClick={() => setShowDocumentDialog(true)} className="gradient-primary border-0">
                <Plus className="mr-2" size={18} /> Add Document
              </Button>
            </CardHeader>
            <CardContent>
              {documents.length === 0 ? (
                <div className="text-center py-12">
                  <FolderOpen className="mx-auto mb-2 text-gray-300" size={48} />
                  <p className="text-gray-500">No documents yet. Add your first document!</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {documents.map((doc) => (
                    <div key={doc.id} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                            <FileText className="text-purple-600" size={20} />
                          </div>
                          <div className="min-w-0">
                            <h4 className="font-medium truncate">{doc.name}</h4>
                            <p className="text-xs text-gray-500 uppercase">{doc.type}</p>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm" onClick={() => handleDeleteDocument(doc.id)}>
                          <Trash2 size={14} className="text-red-500" />
                        </Button>
                      </div>
                      {doc.description && <p className="text-sm text-gray-500 mt-2 line-clamp-2">{doc.description}</p>}
                      <div className="flex items-center justify-between mt-3">
                        <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{doc.category}</span>
                        <span className="text-xs text-gray-400">{new Date(doc.createdAt).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* WORKFLOWS TAB */}
        <TabsContent value="workflows" className="mt-6 space-y-6">
          {/* Active Workflows */}
          <Card>
            <CardHeader>
              <CardTitle>Active Workflows</CardTitle>
              <CardDescription>Your configured automation workflows</CardDescription>
            </CardHeader>
            <CardContent>
              {workflows.length === 0 ? (
                <p className="text-center text-gray-500 py-6">No workflows configured yet. Add one from the templates below.</p>
              ) : (
                <div className="space-y-3">
                  {workflows.map((workflow) => (
                    <div key={workflow.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{workflow.name}</h4>
                          <p className="text-sm text-gray-500">{workflow.description}</p>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded-full ${workflow.isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                          {workflow.isActive ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2 mt-3">
                        {workflow.steps?.map((step, i) => (
                          <React.Fragment key={step.id}>
                            <div className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">{step.title}</div>
                            {i < workflow.steps.length - 1 && <span className="text-gray-300">→</span>}
                          </React.Fragment>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Workflow Templates */}
          <Card>
            <CardHeader>
              <CardTitle>Workflow Templates</CardTitle>
              <CardDescription>Pre-built workflows you can add to your operations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {defaultWorkflows.map((workflow, i) => (
                  <div key={i} className="p-4 border rounded-lg hover:border-purple-300 transition-colors">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                        <Workflow className="text-purple-600" size={20} />
                      </div>
                      <div>
                        <h4 className="font-medium">{workflow.name}</h4>
                        <span className="text-xs text-gray-500 capitalize">{workflow.trigger} trigger</span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-500 mb-3">{workflow.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-400">{workflow.steps?.length} steps</span>
                      <Button size="sm" variant="outline" onClick={() => handleAddDefaultWorkflow(workflow)}>
                        <Plus size={14} className="mr-1" /> Add
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* CREATE TASK DIALOG */}
      <Dialog open={showTaskDialog} onOpenChange={setShowTaskDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Create Task</DialogTitle></DialogHeader>
          <form onSubmit={handleCreateTask} className="space-y-4">
            <div>
              <Label>Title</Label>
              <Input value={newTask.title} onChange={(e) => setNewTask({ ...newTask, title: e.target.value })} required />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea value={newTask.description} onChange={(e) => setNewTask({ ...newTask, description: e.target.value })} rows={2} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Priority</Label>
                <Select value={newTask.priority} onValueChange={(v) => setNewTask({ ...newTask, priority: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {taskPriorities.map((p) => (
                      <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Due Date</Label>
                <Input type="date" value={newTask.dueDate} onChange={(e) => setNewTask({ ...newTask, dueDate: e.target.value })} />
              </div>
            </div>
            <div>
              <Label>Tags (comma-separated)</Label>
              <Input value={newTask.tags} onChange={(e) => setNewTask({ ...newTask, tags: e.target.value })} placeholder="urgent, client-a" />
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowTaskDialog(false)}>Cancel</Button>
              <Button type="submit" disabled={creatingTask} className="gradient-primary border-0">
                {creatingTask ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Create
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* CREATE EMAIL TEMPLATE DIALOG */}
      <Dialog open={showEmailTemplateDialog} onOpenChange={setShowEmailTemplateDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Create Email Template</DialogTitle></DialogHeader>
          <form onSubmit={handleCreateTemplate} className="space-y-4">
            <div>
              <Label>Template Name</Label>
              <Input value={newTemplate.name} onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })} required />
            </div>
            <div>
              <Label>Subject</Label>
              <Input value={newTemplate.subject} onChange={(e) => setNewTemplate({ ...newTemplate, subject: e.target.value })} required />
            </div>
            <div>
              <Label>Category</Label>
              <Select value={newTemplate.category} onValueChange={(v) => setNewTemplate({ ...newTemplate, category: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="general">General</SelectItem>
                  <SelectItem value="marketing">Marketing</SelectItem>
                  <SelectItem value="transactional">Transactional</SelectItem>
                  <SelectItem value="notification">Notification</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Body (HTML)</Label>
              <Textarea value={newTemplate.bodyHtml} onChange={(e) => setNewTemplate({ ...newTemplate, bodyHtml: e.target.value })} rows={5} required />
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowEmailTemplateDialog(false)}>Cancel</Button>
              <Button type="submit" disabled={creatingTemplate} className="gradient-primary border-0">
                {creatingTemplate ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Create
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* SEND EMAIL DIALOG */}
      <Dialog open={showSendEmailDialog} onOpenChange={setShowSendEmailDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>Compose Email</DialogTitle></DialogHeader>
          <form onSubmit={handleSendEmail} className="space-y-4">
            {emailTemplates.length > 0 && (
              <div>
                <Label>Use Template</Label>
                <Select value={emailToSend.templateId} onValueChange={handleSelectTemplate}>
                  <SelectTrigger><SelectValue placeholder="Select a template (optional)" /></SelectTrigger>
                  <SelectContent>
                    {emailTemplates.map((t) => (
                      <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
            <div>
              <Label>To (comma-separated emails)</Label>
              <Input value={emailToSend.to} onChange={(e) => setEmailToSend({ ...emailToSend, to: e.target.value })} placeholder="user@example.com" required />
            </div>
            <div>
              <Label>Subject</Label>
              <Input value={emailToSend.subject} onChange={(e) => setEmailToSend({ ...emailToSend, subject: e.target.value })} required />
            </div>
            <div>
              <Label>Body (HTML)</Label>
              <Textarea value={emailToSend.bodyHtml} onChange={(e) => setEmailToSend({ ...emailToSend, bodyHtml: e.target.value })} rows={6} required />
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowSendEmailDialog(false)}>Cancel</Button>
              <Button type="submit" disabled={sendingEmail} className="gradient-primary border-0">
                {sendingEmail ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2" size={16} />} Send
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* CREATE DOCUMENT DIALOG */}
      <Dialog open={showDocumentDialog} onOpenChange={setShowDocumentDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Add Document</DialogTitle></DialogHeader>
          <form onSubmit={handleCreateDocument} className="space-y-4">
            <div>
              <Label>Document Name</Label>
              <Input value={newDocument.name} onChange={(e) => setNewDocument({ ...newDocument, name: e.target.value })} required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Type</Label>
                <Select value={newDocument.type} onValueChange={(v) => setNewDocument({ ...newDocument, type: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {documentTypes.map((t) => (
                      <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Category</Label>
                <Input value={newDocument.category} onChange={(e) => setNewDocument({ ...newDocument, category: e.target.value })} placeholder="contracts" />
              </div>
            </div>
            <div>
              <Label>Description</Label>
              <Textarea value={newDocument.description} onChange={(e) => setNewDocument({ ...newDocument, description: e.target.value })} rows={2} />
            </div>
            <div>
              <Label>Tags (comma-separated)</Label>
              <Input value={newDocument.tags} onChange={(e) => setNewDocument({ ...newDocument, tags: e.target.value })} placeholder="important, 2024" />
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowDocumentDialog(false)}>Cancel</Button>
              <Button type="submit" disabled={creatingDocument} className="gradient-primary border-0">
                {creatingDocument ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Add
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
