import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';
const WorkspaceContext = createContext();

export const useWorkspace = () => {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace must be used within WorkspaceProvider');
  }
  return context;
};

export default function WorkspaceProvider({ children }) {
  const { token } = useAuth();
  const [workspaces, setWorkspaces] = useState([]);
  const [currentWorkspace, setCurrentWorkspace] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      loadWorkspaces();
    }
  }, [token]);

  const loadWorkspaces = async () => {
    try {
      const response = await axios.get(`${API_URL}/workspaces`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setWorkspaces(response.data);
      
      // Set current workspace from localStorage or first workspace
      const savedWorkspaceId = localStorage.getItem('currentWorkspaceId');
      const workspace = savedWorkspaceId
        ? response.data.find(w => w.id === savedWorkspaceId)
        : response.data[0];
      
      if (workspace) {
        setCurrentWorkspace(workspace);
        localStorage.setItem('currentWorkspaceId', workspace.id);
      }
    } catch (error) {
      console.error('Failed to load workspaces:', error);
    } finally {
      setLoading(false);
    }
  };

  const createWorkspace = async (data) => {
    const response = await axios.post(`${API_URL}/workspaces`, data, {
      headers: { Authorization: `Bearer ${token}` }
    });
    await loadWorkspaces();
    return response.data;
  };

  const switchWorkspace = (workspaceId) => {
    const workspace = workspaces.find(w => w.id === workspaceId);
    if (workspace) {
      setCurrentWorkspace(workspace);
      localStorage.setItem('currentWorkspaceId', workspaceId);
    }
  };

  const getHeaders = () => ({
    Authorization: `Bearer ${token}`,
    'X-Workspace-Id': currentWorkspace?.id
  });

  return (
    <WorkspaceContext.Provider
      value={{
        workspaces,
        currentWorkspace,
        loading,
        createWorkspace,
        switchWorkspace,
        loadWorkspaces,
        getHeaders
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}
