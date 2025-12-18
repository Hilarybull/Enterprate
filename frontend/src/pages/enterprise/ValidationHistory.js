import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  History, 
  Eye, 
  Trash2, 
  CheckCircle, 
  XCircle, 
  Clock,
  Loader2,
  FileText,
  Plus,
  TrendingUp
} from 'lucide-react';
import { toast } from 'sonner';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function ValidationHistory() {
  const navigate = useNavigate();
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [reports, setReports] = useState([]);
  const [engagement, setEngagement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    if (currentWorkspace) {
      fetchData();
    }
  }, [currentWorkspace]);

  const fetchData = async () => {
    try {
      const [reportsRes, engagementRes] = await Promise.all([
        axios.get(`${API_URL}/validation-reports`, { headers: getHeaders() }),
        axios.get(`${API_URL}/validation-reports/engagement`, { headers: getHeaders() })
      ]);
      setReports(reportsRes.data);
      setEngagement(engagementRes.data);
    } catch (error) {
      toast.error('Failed to load validation history');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const deleteReport = async (reportId) => {
    setDeleting(reportId);
    try {
      await axios.delete(`${API_URL}/validation-reports/${reportId}`, { headers: getHeaders() });
      setReports(prev => prev.filter(r => r.id !== reportId));
      toast.success('Report deleted');
    } catch (error) {
      toast.error('Failed to delete report');
    } finally {
      setDeleting(null);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'accepted':
        return <Badge className="bg-green-100 text-green-700"><CheckCircle className="w-3 h-3 mr-1" />Accepted</Badge>;
      case 'rejected':
        return <Badge className="bg-red-100 text-red-700"><XCircle className="w-3 h-3 mr-1" />Rejected</Badge>;
      default:
        return <Badge variant="secondary"><Clock className="w-3 h-3 mr-1" />Pending</Badge>;
    }
  };

  const getVerdictBadge = (verdict) => {
    switch (verdict) {
      case 'PASS':
        return <Badge className="bg-green-500 text-white">PASS</Badge>;
      case 'PIVOT':
        return <Badge className="bg-yellow-500 text-white">PIVOT</Badge>;
      case 'KILL':
        return <Badge className="bg-red-500 text-white">KILL</Badge>;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-slide-in" data-testid="validation-history">
      <PageHeader
        icon={History}
        title="Validation History"
        description="View and manage your past idea validations"
        actions={
          <Button 
            onClick={() => navigate('/idea-discovery')} 
            className="gradient-primary border-0"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Validation
          </Button>
        }
      />

      {/* Engagement Stats */}
      {engagement && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold text-purple-600">{engagement.totalValidations}</p>
              <p className="text-sm text-gray-500">Total Validations</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold text-green-600">{engagement.acceptedCount}</p>
              <p className="text-sm text-gray-500">Accepted</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold text-red-600">{engagement.rejectedCount}</p>
              <p className="text-sm text-gray-500">Rejected</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold text-gray-600">{engagement.pendingCount}</p>
              <p className="text-sm text-gray-500">Pending</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Reports List */}
      {reports.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="font-semibold text-lg mb-2">No validations yet</h3>
            <p className="text-gray-500 mb-4">Start validating your business ideas to see them here</p>
            <Button onClick={() => navigate('/idea-discovery')} className="gradient-primary border-0">
              <Plus className="w-4 h-4 mr-2" />
              Start First Validation
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => (
            <Card key={report.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 flex-1 min-w-0">
                    <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center flex-shrink-0">
                      <TrendingUp className="w-6 h-6 text-purple-600" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center space-x-2 flex-wrap">
                        <h3 className="font-semibold truncate">{report.ideaName}</h3>
                        {getStatusBadge(report.status)}
                        {getVerdictBadge(report.verdict)}
                      </div>
                      <div className="flex items-center space-x-3 text-sm text-gray-500 mt-1">
                        <span className="capitalize">{report.ideaType}</span>
                        <span>•</span>
                        <span>Score: {report.overallScore}/10</span>
                        <span>•</span>
                        <span>{new Date(report.createdAt).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => navigate(`/validation-report/${report.id}`)}
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </Button>
                    
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          disabled={deleting === report.id}
                        >
                          {deleting === report.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete Validation Report</AlertDialogTitle>
                          <AlertDialogDescription>
                            Are you sure you want to delete &quot;{report.ideaName}&quot;? This action cannot be undone.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction 
                            onClick={() => deleteReport(report.id)}
                            className="bg-red-600 hover:bg-red-700"
                          >
                            Delete
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
