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
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';
import { 
  Users, 
  UserPlus, 
  Mail,
  Shield,
  Activity,
  MessageSquare,
  Clock,
  Trash2,
  MoreVertical,
  CheckCircle2,
  XCircle,
  Loader2,
  Crown,
  Edit,
  Send
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const ROLE_COLORS = {
  owner: 'bg-amber-100 text-amber-800',
  admin: 'bg-purple-100 text-purple-800',
  editor: 'bg-blue-100 text-blue-800',
  viewer: 'bg-gray-100 text-gray-800',
  guest: 'bg-slate-100 text-slate-600'
};

const ROLE_ICONS = {
  owner: Crown,
  admin: Shield,
  editor: Edit,
  viewer: Users,
  guest: Users
};

export default function TeamCollaboration() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('members');
  const [members, setMembers] = useState([]);
  const [pendingInvites, setPendingInvites] = useState([]);
  const [activities, setActivities] = useState([]);
  const [roles, setRoles] = useState({});
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('editor');
  const [inviteMessage, setInviteMessage] = useState('');
  const [inviting, setInviting] = useState(false);

  const loadData = useCallback(async () => {
    if (!currentWorkspace) return;
    
    setLoading(true);
    try {
      const [membersRes, invitesRes, activitiesRes, rolesRes] = await Promise.all([
        axios.get(`${API_URL}/team/members`, { headers: getHeaders() }),
        axios.get(`${API_URL}/team/invites/pending`, { headers: getHeaders() }),
        axios.get(`${API_URL}/team/activity?limit=30`, { headers: getHeaders() }),
        axios.get(`${API_URL}/team/roles`)
      ]);
      
      setMembers(membersRes.data || []);
      setPendingInvites(invitesRes.data || []);
      setActivities(activitiesRes.data || []);
      setRoles(rolesRes.data || {});
    } catch (error) {
      console.error('Failed to load team data:', error);
      toast.error('Failed to load team data');
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace, getHeaders]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const inviteMember = async () => {
    if (!inviteEmail.trim()) {
      toast.error('Please enter an email address');
      return;
    }
    
    setInviting(true);
    try {
      await axios.post(`${API_URL}/team/invite`, {
        email: inviteEmail,
        role: inviteRole,
        message: inviteMessage || null
      }, { headers: getHeaders() });
      
      toast.success('Invitation sent successfully!');
      setShowInviteDialog(false);
      setInviteEmail('');
      setInviteRole('editor');
      setInviteMessage('');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setInviting(false);
    }
  };

  const updateMemberRole = async (memberId, newRole) => {
    try {
      await axios.patch(`${API_URL}/team/members/${memberId}/role`, {
        role: newRole
      }, { headers: getHeaders() });
      
      toast.success('Role updated successfully');
      loadData();
    } catch (error) {
      toast.error('Failed to update role');
    }
  };

  const removeMember = async (memberId) => {
    if (!window.confirm('Are you sure you want to remove this member?')) return;
    
    try {
      await axios.delete(`${API_URL}/team/members/${memberId}`, {
        headers: getHeaders()
      });
      
      toast.success('Member removed');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to remove member');
    }
  };

  const getInitials = (name) => {
    return name?.split(' ').map(n => n[0]).join('').toUpperCase() || '?';
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric'
    });
  };

  const formatTime = (dateStr) => {
    return new Date(dateStr).toLocaleTimeString('en-US', {
      hour: '2-digit', minute: '2-digit'
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
    <div className="space-y-6 animate-slide-in" data-testid="team-collaboration-page">
      <PageHeader
        icon={Users}
        title="Team Collaboration"
        description="Manage your team members, roles, and track activity"
        actions={
          <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
            <DialogTrigger asChild>
              <Button className="gradient-primary border-0" data-testid="invite-member-btn">
                <UserPlus className="mr-2" size={16} />
                Invite Member
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Invite Team Member</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="colleague@company.com"
                    className="mt-1.5"
                    data-testid="invite-email-input"
                  />
                </div>
                <div>
                  <Label>Role</Label>
                  <Select value={inviteRole} onValueChange={setInviteRole}>
                    <SelectTrigger className="mt-1.5" data-testid="invite-role-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(roles).filter(([k]) => k !== 'owner').map(([key, role]) => (
                        <SelectItem key={key} value={key}>
                          {role.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="message">Personal Message (Optional)</Label>
                  <Textarea
                    id="message"
                    value={inviteMessage}
                    onChange={(e) => setInviteMessage(e.target.value)}
                    placeholder="Add a personal message to your invitation..."
                    className="mt-1.5"
                    rows={3}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowInviteDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={inviteMember} disabled={inviting} data-testid="send-invite-btn">
                  {inviting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2" size={16} />}
                  Send Invitation
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Users className="text-indigo-600" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{members.length}</p>
                <p className="text-sm text-gray-500">Team Members</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-100 rounded-lg">
                <Mail className="text-amber-600" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{pendingInvites.length}</p>
                <p className="text-sm text-gray-500">Pending Invites</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Activity className="text-green-600" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{activities.length}</p>
                <p className="text-sm text-gray-500">Recent Activities</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Shield className="text-purple-600" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{Object.keys(roles).length}</p>
                <p className="text-sm text-gray-500">Available Roles</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="members" className="flex items-center gap-2">
            <Users size={16} />
            Members ({members.length})
          </TabsTrigger>
          <TabsTrigger value="invites" className="flex items-center gap-2">
            <Mail size={16} />
            Invites ({pendingInvites.length})
          </TabsTrigger>
          <TabsTrigger value="activity" className="flex items-center gap-2">
            <Activity size={16} />
            Activity
          </TabsTrigger>
        </TabsList>

        <TabsContent value="members" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Team Members</CardTitle>
              <CardDescription>Manage roles and permissions for your team</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="divide-y">
                {members.map((member) => {
                  const RoleIcon = ROLE_ICONS[member.role] || Users;
                  return (
                    <div key={member.user_id} className="flex items-center justify-between py-4" data-testid={`member-${member.user_id}`}>
                      <div className="flex items-center gap-4">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback className="bg-gradient-to-br from-indigo-500 to-purple-500 text-white">
                            {getInitials(member.name)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{member.name || member.email}</p>
                          <p className="text-sm text-gray-500">{member.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge className={ROLE_COLORS[member.role]}>
                          <RoleIcon size={12} className="mr-1" />
                          {roles[member.role]?.label || member.role}
                        </Badge>
                        {member.role !== 'owner' && (
                          <div className="flex items-center gap-1">
                            <Select value={member.role} onValueChange={(v) => updateMemberRole(member.user_id, v)}>
                              <SelectTrigger className="w-[120px] h-8">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {Object.entries(roles).filter(([k]) => k !== 'owner').map(([key, role]) => (
                                  <SelectItem key={key} value={key}>{role.label}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-red-500 hover:text-red-700 hover:bg-red-50"
                              onClick={() => removeMember(member.user_id)}
                            >
                              <Trash2 size={16} />
                            </Button>
                          </div>
                        )}
                        {member.role === 'owner' && (
                          <span className="text-sm text-gray-400 italic">Workspace owner</span>
                        )}
                      </div>
                    </div>
                  );
                })}
                {members.length === 0 && (
                  <div className="py-8 text-center text-gray-500">
                    <Users className="mx-auto mb-2 text-gray-300" size={32} />
                    <p>No team members yet</p>
                    <Button className="mt-3" size="sm" onClick={() => setShowInviteDialog(true)}>
                      Invite your first team member
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="invites" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Pending Invitations</CardTitle>
              <CardDescription>Invitations waiting to be accepted</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="divide-y">
                {pendingInvites.map((invite) => (
                  <div key={invite.id} className="flex items-center justify-between py-4" data-testid={`invite-${invite.id}`}>
                    <div className="flex items-center gap-4">
                      <div className="p-2 bg-amber-100 rounded-full">
                        <Mail className="text-amber-600" size={20} />
                      </div>
                      <div>
                        <p className="font-medium">{invite.email}</p>
                        <p className="text-sm text-gray-500">
                          Invited {formatDate(invite.createdAt)} as {roles[invite.role]?.label || invite.role}
                        </p>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-amber-600 border-amber-300">
                      <Clock size={12} className="mr-1" />
                      Pending
                    </Badge>
                  </div>
                ))}
                {pendingInvites.length === 0 && (
                  <div className="py-8 text-center text-gray-500">
                    <CheckCircle2 className="mx-auto mb-2 text-gray-300" size={32} />
                    <p>No pending invitations</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Activity Feed</CardTitle>
              <CardDescription>Recent team activities and updates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {activities.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50" data-testid={`activity-${activity.id}`}>
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="bg-indigo-100 text-indigo-600 text-xs">
                        {getInitials(activity.user_name)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm">
                        <span className="font-medium">{activity.user_name}</span>
                        {' '}{activity.description}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDate(activity.createdAt)} at {formatTime(activity.createdAt)}
                      </p>
                    </div>
                    <Badge variant="outline" className="text-xs shrink-0">
                      {activity.type.replace(/_/g, ' ')}
                    </Badge>
                  </div>
                ))}
                {activities.length === 0 && (
                  <div className="py-8 text-center text-gray-500">
                    <Activity className="mx-auto mb-2 text-gray-300" size={32} />
                    <p>No activity yet</p>
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
