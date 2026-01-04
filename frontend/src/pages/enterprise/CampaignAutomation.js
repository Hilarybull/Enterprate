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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { 
  Zap,
  Plus,
  Play,
  Pause,
  Settings,
  Clock,
  Trash2,
  Loader2,
  ChevronRight,
  ArrowRight,
  CheckCircle2,
  XCircle,
  Mail,
  Bell,
  Tag,
  Share2,
  DollarSign,
  Activity,
  ListChecks
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const TRIGGER_ICONS = {
  lead_created: Mail,
  lead_status_changed: Activity,
  lead_score_threshold: Activity,
  invoice_paid: DollarSign,
  invoice_overdue: Clock,
  campaign_started: Play,
  campaign_ended: CheckCircle2,
  website_lead_captured: Mail,
  ab_test_winner: CheckCircle2,
  time_based: Clock
};

const ACTION_ICONS = {
  send_email: Mail,
  create_task: ListChecks,
  update_lead_status: Activity,
  add_lead_tag: Tag,
  schedule_post: Share2,
  send_notification: Bell,
  webhook: Zap
};

export default function CampaignAutomation() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [loading, setLoading] = useState(true);
  const [rules, setRules] = useState([]);
  const [triggers, setTriggers] = useState({});
  const [actions, setActions] = useState({});
  const [operators, setOperators] = useState({});
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('rules');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [creating, setCreating] = useState(false);
  
  // Create form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    trigger: { type: 'lead_created', config: {} },
    conditions: [],
    actions: [{ type: 'send_notification', config: { message: '' } }],
    isActive: true,
    priority: 0
  });

  const loadData = useCallback(async () => {
    if (!currentWorkspace) return;
    
    setLoading(true);
    try {
      const [rulesRes, triggersRes, actionsRes, operatorsRes, logsRes] = await Promise.all([
        axios.get(`${API_URL}/automation/rules`, { headers: getHeaders() }),
        axios.get(`${API_URL}/automation/triggers`),
        axios.get(`${API_URL}/automation/actions`),
        axios.get(`${API_URL}/automation/operators`),
        axios.get(`${API_URL}/automation/logs?limit=20`, { headers: getHeaders() })
      ]);
      
      setRules(rulesRes.data || []);
      setTriggers(triggersRes.data || {});
      setActions(actionsRes.data || {});
      setOperators(operatorsRes.data || {});
      setLogs(logsRes.data || []);
    } catch (error) {
      console.error('Failed to load automation data:', error);
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace, getHeaders]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const createRule = async () => {
    if (!formData.name.trim()) {
      toast.error('Please enter a rule name');
      return;
    }
    
    setCreating(true);
    try {
      await axios.post(`${API_URL}/automation/rules`, {
        name: formData.name,
        description: formData.description,
        trigger: formData.trigger,
        conditions: formData.conditions,
        actions: formData.actions,
        isActive: formData.isActive,
        priority: formData.priority
      }, { headers: getHeaders() });
      
      toast.success('Automation rule created!');
      setShowCreateDialog(false);
      resetForm();
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create rule');
    } finally {
      setCreating(false);
    }
  };

  const toggleRule = async (ruleId, isActive) => {
    try {
      await axios.patch(`${API_URL}/automation/rules/${ruleId}`, {
        isActive: isActive
      }, { headers: getHeaders() });
      
      toast.success(isActive ? 'Rule activated' : 'Rule deactivated');
      loadData();
    } catch (error) {
      toast.error('Failed to update rule');
    }
  };

  const deleteRule = async (ruleId) => {
    if (!window.confirm('Are you sure you want to delete this automation rule?')) return;
    
    try {
      await axios.delete(`${API_URL}/automation/rules/${ruleId}`, { headers: getHeaders() });
      toast.success('Rule deleted');
      loadData();
    } catch (error) {
      toast.error('Failed to delete rule');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      trigger: { type: 'lead_created', config: {} },
      conditions: [],
      actions: [{ type: 'send_notification', config: { message: '' } }],
      isActive: true,
      priority: 0
    });
  };

  const addCondition = () => {
    setFormData({
      ...formData,
      conditions: [
        ...formData.conditions,
        { field: '', operator: 'equals', value: '' }
      ]
    });
  };

  const updateCondition = (index, field, value) => {
    const newConditions = [...formData.conditions];
    newConditions[index][field] = value;
    setFormData({ ...formData, conditions: newConditions });
  };

  const removeCondition = (index) => {
    setFormData({
      ...formData,
      conditions: formData.conditions.filter((_, i) => i !== index)
    });
  };

  const addAction = () => {
    setFormData({
      ...formData,
      actions: [
        ...formData.actions,
        { type: 'send_notification', config: { message: '' } }
      ]
    });
  };

  const updateAction = (index, field, value) => {
    const newActions = [...formData.actions];
    if (field === 'type') {
      newActions[index] = { type: value, config: {} };
    } else {
      newActions[index].config[field] = value;
    }
    setFormData({ ...formData, actions: newActions });
  };

  const removeAction = (index) => {
    if (formData.actions.length <= 1) {
      toast.error('At least one action is required');
      return;
    }
    setFormData({
      ...formData,
      actions: formData.actions.filter((_, i) => i !== index)
    });
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="loading-spinner">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-slide-in" data-testid="campaign-automation-page">
      <PageHeader
        icon={Zap}
        title="Campaign Automation"
        description="Create automated workflows with triggers, conditions, and actions"
        actions={
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button className="gradient-primary border-0" data-testid="create-rule-btn">
                <Plus className="mr-2" size={16} />
                Create Rule
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create Automation Rule</DialogTitle>
              </DialogHeader>
              <div className="space-y-5 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Rule Name</Label>
                    <Input
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="e.g., Welcome New Leads"
                      className="mt-1.5"
                      data-testid="rule-name-input"
                    />
                  </div>
                  <div>
                    <Label>Priority</Label>
                    <Input
                      type="number"
                      value={formData.priority}
                      onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 0 })}
                      className="mt-1.5"
                    />
                  </div>
                </div>
                
                <div>
                  <Label>Description</Label>
                  <Textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="What does this automation do?"
                    className="mt-1.5"
                    rows={2}
                  />
                </div>
                
                {/* Trigger */}
                <div className="p-4 bg-indigo-50 rounded-lg">
                  <Label className="text-indigo-700 mb-2 block">When this happens (Trigger)</Label>
                  <Select
                    value={formData.trigger.type}
                    onValueChange={(v) => setFormData({ ...formData, trigger: { type: v, config: {} } })}
                  >
                    <SelectTrigger data-testid="trigger-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(triggers).map(([key, trigger]) => (
                        <SelectItem key={key} value={key}>{trigger.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                {/* Conditions */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <Label className="text-gray-700">If these conditions are met (Optional)</Label>
                    <Button size="sm" variant="outline" onClick={addCondition}>
                      <Plus size={14} className="mr-1" /> Add
                    </Button>
                  </div>
                  {formData.conditions.length === 0 ? (
                    <p className="text-sm text-gray-500 italic">No conditions - rule will trigger for all events</p>
                  ) : (
                    <div className="space-y-2">
                      {formData.conditions.map((condition, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <Input
                            placeholder="Field (e.g., source)"
                            value={condition.field}
                            onChange={(e) => updateCondition(index, 'field', e.target.value)}
                            className="flex-1"
                          />
                          <Select
                            value={condition.operator}
                            onValueChange={(v) => updateCondition(index, 'operator', v)}
                          >
                            <SelectTrigger className="w-[140px]">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {Object.entries(operators).map(([key, label]) => (
                                <SelectItem key={key} value={key}>{label}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <Input
                            placeholder="Value"
                            value={condition.value}
                            onChange={(e) => updateCondition(index, 'value', e.target.value)}
                            className="flex-1"
                          />
                          <Button size="sm" variant="ghost" onClick={() => removeCondition(index)}>
                            <XCircle size={16} className="text-red-500" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                
                {/* Actions */}
                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <Label className="text-green-700">Then do this (Actions)</Label>
                    <Button size="sm" variant="outline" onClick={addAction}>
                      <Plus size={14} className="mr-1" /> Add
                    </Button>
                  </div>
                  <div className="space-y-3">
                    {formData.actions.map((action, index) => (
                      <Card key={index} className="p-3">
                        <div className="flex items-center justify-between mb-2">
                          <Select
                            value={action.type}
                            onValueChange={(v) => updateAction(index, 'type', v)}
                          >
                            <SelectTrigger className="w-[200px]">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {Object.entries(actions).map(([key, act]) => (
                                <SelectItem key={key} value={key}>{act.label}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <Button size="sm" variant="ghost" onClick={() => removeAction(index)}>
                            <Trash2 size={14} className="text-red-500" />
                          </Button>
                        </div>
                        {action.type === 'send_notification' && (
                          <Input
                            placeholder="Notification message"
                            value={action.config.message || ''}
                            onChange={(e) => updateAction(index, 'message', e.target.value)}
                          />
                        )}
                        {action.type === 'send_email' && (
                          <div className="grid grid-cols-2 gap-2">
                            <Input
                              placeholder="Email template"
                              value={action.config.template || ''}
                              onChange={(e) => updateAction(index, 'template', e.target.value)}
                            />
                            <Input
                              placeholder="Recipient (or leave for event email)"
                              value={action.config.recipient || ''}
                              onChange={(e) => updateAction(index, 'recipient', e.target.value)}
                            />
                          </div>
                        )}
                        {action.type === 'create_task' && (
                          <Input
                            placeholder="Task title"
                            value={action.config.title || ''}
                            onChange={(e) => updateAction(index, 'title', e.target.value)}
                          />
                        )}
                        {action.type === 'add_lead_tag' && (
                          <Input
                            placeholder="Tag name"
                            value={action.config.tag || ''}
                            onChange={(e) => updateAction(index, 'tag', e.target.value)}
                          />
                        )}
                        {action.type === 'update_lead_status' && (
                          <Select
                            value={action.config.status || ''}
                            onValueChange={(v) => updateAction(index, 'status', v)}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select status" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="new">New</SelectItem>
                              <SelectItem value="contacted">Contacted</SelectItem>
                              <SelectItem value="qualified">Qualified</SelectItem>
                              <SelectItem value="converted">Converted</SelectItem>
                            </SelectContent>
                          </Select>
                        )}
                      </Card>
                    ))}
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <Switch
                    checked={formData.isActive}
                    onCheckedChange={(c) => setFormData({ ...formData, isActive: c })}
                  />
                  <Label>Activate rule immediately</Label>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => { setShowCreateDialog(false); resetForm(); }}>Cancel</Button>
                <Button onClick={createRule} disabled={creating} data-testid="submit-rule-btn">
                  {creating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Zap className="mr-2" size={16} />}
                  Create Rule
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Zap className="text-green-600" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{rules.filter(r => r.isActive).length}</p>
                <p className="text-sm text-gray-500">Active Rules</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-100 rounded-lg">
                <Pause className="text-gray-600" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{rules.filter(r => !r.isActive).length}</p>
                <p className="text-sm text-gray-500">Inactive Rules</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Activity className="text-indigo-600" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{rules.reduce((sum, r) => sum + (r.executionCount || 0), 0)}</p>
                <p className="text-sm text-gray-500">Total Executions</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="rules" className="flex items-center gap-2">
            <Zap size={16} />
            Rules ({rules.length})
          </TabsTrigger>
          <TabsTrigger value="logs" className="flex items-center gap-2">
            <Activity size={16} />
            Activity Logs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="rules" className="mt-6">
          <div className="space-y-4">
            {rules.map((rule) => {
              const TriggerIcon = TRIGGER_ICONS[rule.trigger?.type] || Zap;
              return (
                <Card key={rule.id} className={`${!rule.isActive ? 'opacity-60' : ''}`} data-testid={`rule-card-${rule.id}`}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className={`p-2 rounded-lg ${rule.isActive ? 'bg-green-100' : 'bg-gray-100'}`}>
                          <TriggerIcon className={rule.isActive ? 'text-green-600' : 'text-gray-400'} size={20} />
                        </div>
                        <div>
                          <h3 className="font-medium">{rule.name}</h3>
                          <p className="text-sm text-gray-500 mt-0.5">{rule.description}</p>
                          
                          <div className="flex items-center gap-2 mt-3 text-sm">
                            <Badge variant="outline" className="text-indigo-600 border-indigo-200">
                              {triggers[rule.trigger?.type]?.label || rule.trigger?.type}
                            </Badge>
                            <ArrowRight size={14} className="text-gray-400" />
                            <div className="flex gap-1">
                              {rule.actions?.map((action, i) => {
                                const ActionIcon = ACTION_ICONS[action.type] || Zap;
                                return (
                                  <Badge key={i} variant="outline" className="text-green-600 border-green-200">
                                    <ActionIcon size={12} className="mr-1" />
                                    {actions[action.type]?.label || action.type}
                                  </Badge>
                                );
                              })}
                            </div>
                          </div>
                          
                          {rule.conditions?.length > 0 && (
                            <p className="text-xs text-gray-400 mt-2">
                              {rule.conditions.length} condition{rule.conditions.length > 1 ? 's' : ''}
                            </p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <div className="text-right text-sm">
                          <p className="text-gray-500">{rule.executionCount || 0} executions</p>
                          {rule.lastExecuted && (
                            <p className="text-xs text-gray-400">Last: {formatDate(rule.lastExecuted)}</p>
                          )}
                        </div>
                        <Switch
                          checked={rule.isActive}
                          onCheckedChange={(c) => toggleRule(rule.id, c)}
                        />
                        <Button size="sm" variant="ghost" className="text-red-500" onClick={() => deleteRule(rule.id)}>
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
            
            {rules.length === 0 && (
              <Card className="p-12 text-center">
                <Zap className="mx-auto text-gray-300 mb-4" size={48} />
                <h3 className="text-lg font-medium text-gray-700">No Automation Rules</h3>
                <p className="text-gray-500 mt-1">Create your first rule to automate workflows</p>
                <Button className="mt-4" onClick={() => setShowCreateDialog(true)}>
                  <Plus className="mr-2" size={16} /> Create Your First Rule
                </Button>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="logs" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Execution Logs</CardTitle>
              <CardDescription>Recent automation executions and results</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {logs.map((log, index) => {
                  const ActionIcon = ACTION_ICONS[log.actionType] || Zap;
                  return (
                    <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className={`p-1.5 rounded ${log.result?.success ? 'bg-green-100' : 'bg-red-100'}`}>
                        {log.result?.success ? (
                          <CheckCircle2 className="text-green-600" size={16} />
                        ) : (
                          <XCircle className="text-red-600" size={16} />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <ActionIcon size={14} className="text-gray-400" />
                          <span className="font-medium text-sm">{actions[log.actionType]?.label || log.actionType}</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">{formatDate(log.executedAt)}</p>
                      </div>
                      <Badge variant="outline" className={log.result?.success ? 'text-green-600' : 'text-red-600'}>
                        {log.result?.success ? 'Success' : 'Failed'}
                      </Badge>
                    </div>
                  );
                })}
                
                {logs.length === 0 && (
                  <div className="py-8 text-center text-gray-500">
                    <Activity className="mx-auto mb-2 text-gray-300" size={32} />
                    <p>No execution logs yet</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
