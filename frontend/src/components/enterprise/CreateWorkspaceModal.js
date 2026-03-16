import React, { useState } from 'react';
import { useWorkspace } from '@/context/WorkspaceContext';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Building2, Loader2 } from 'lucide-react';

export default function CreateWorkspaceModal({ open, onOpenChange }) {
  const { createWorkspace, workspaces } = useWorkspace();
  const [workspaceName, setWorkspaceName] = useState('');
  const [creating, setCreating] = useState(false);

  const handleCreateWorkspace = async (e) => {
    e.preventDefault();
    if (!workspaceName.trim()) return;

    setCreating(true);
	    try {
	      await createWorkspace({ name: workspaceName });
	      toast.success('Workspace created successfully!');
	      onOpenChange(false);
	      setWorkspaceName('');
	    } catch (error) {
	      const status = error?.status ?? error?.response?.status;
	      if (status === 409) {
	        toast.error('Only one workspace is allowed per account.');
	      } else {
	        toast.error('Failed to create workspace');
	      }
	    } finally {
	      setCreating(false);
	    }
	  };

  const isFirstWorkspace = workspaces.length === 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="mx-auto w-12 h-12 rounded-xl gradient-primary flex items-center justify-center mb-4">
            <Building2 className="text-white" size={24} />
          </div>
          <DialogTitle className="text-center">
            {isFirstWorkspace ? 'Create Your Workspace' : 'Workspace Limit'}
          </DialogTitle>
          <DialogDescription className="text-center">
            {isFirstWorkspace
              ? 'Get started by creating your workspace. You can only have one workspace per account.'
              : 'Only one workspace is allowed per account.'
            }
          </DialogDescription>
        </DialogHeader>
        
        {isFirstWorkspace ? (
          <form onSubmit={handleCreateWorkspace} className="space-y-4 mt-4">
            <div>
              <Label htmlFor="workspace-name" className="text-sm font-medium">
                Workspace Name
              </Label>
              <Input
                id="workspace-name"
                data-testid="workspace-name-input"
                value={workspaceName}
                onChange={(e) => setWorkspaceName(e.target.value)}
                placeholder="e.g., My Startup, Acme Corp"
                className="mt-1.5"
                required
                autoFocus
              />
            </div>
            
            <div className="flex justify-end space-x-2 pt-2">
              <Button 
                type="submit" 
                disabled={creating || !workspaceName.trim()}
                className="gradient-primary border-0"
                data-testid="submit-workspace-btn"
              >
                {creating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Workspace'
                )}
              </Button>
            </div>
          </form>
        ) : (
          <div className="mt-4 flex justify-end">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
