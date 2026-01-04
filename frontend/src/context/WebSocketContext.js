import React, { createContext, useContext, useEffect, useState, useRef, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { useWorkspace } from './WorkspaceContext';
import { toast } from 'sonner';

const WebSocketContext = createContext(null);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const { isAuthenticated, token } = useAuth();
  const { currentWorkspace } = useWorkspace();
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const wsRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000;
  const pingIntervalRef = useRef(null);
  const connectRef = useRef(null);

  const getWebSocketUrl = useCallback(() => {
    if (!token || !currentWorkspace?.id) return null;
    
    const baseUrl = process.env.REACT_APP_BACKEND_URL || '';
    const wsProtocol = baseUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = baseUrl.replace(/^https?:\/\//, '');
    
    return `${wsProtocol}://${wsHost}/api/ws/notifications?token=${token}&workspace_id=${currentWorkspace.id}`;
  }, [token, currentWorkspace?.id]);

  const handleMessage = useCallback((event) => {
    try {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'connected':
          console.log('WebSocket connected:', data.message);
          break;
          
        case 'pong':
          // Heartbeat response
          break;
          
        case 'notification':
          // Add notification to state
          const notification = {
            id: Date.now().toString(),
            ...data,
            read: false,
            receivedAt: new Date().toISOString()
          };
          
          setNotifications(prev => [notification, ...prev].slice(0, 50));
          setUnreadCount(prev => prev + 1);
          
          // Show toast based on category
          const toastOptions = { duration: 5000 };
          
          switch (data.category) {
            case 'lead':
              toast.success(data.message, { ...toastOptions, icon: '🎯' });
              break;
            case 'website':
              toast.success(data.message, { ...toastOptions, icon: '🚀' });
              break;
            case 'ab_test':
              toast.info(data.message, { ...toastOptions, icon: '🧪' });
              break;
            case 'automation':
              toast(data.message, { 
                ...toastOptions, 
                icon: data.data?.success ? '⚡' : '⚠️'
              });
              break;
            case 'team':
              toast.info(data.message, { ...toastOptions, icon: '👥' });
              break;
            case 'scheduling':
              toast.success(data.message, { ...toastOptions, icon: '📅' });
              break;
            default:
              toast(data.message, toastOptions);
          }
          break;
          
        default:
          console.log('Unknown message type:', data.type);
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }, []);

  // Store connect function in ref to avoid circular dependency
  useEffect(() => {
    connectRef.current = () => {
      const wsUrl = getWebSocketUrl();
      if (!wsUrl) return;
      
      // Close existing connection
      if (wsRef.current) {
        wsRef.current.close();
      }
      
      try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          console.log('WebSocket connection established');
          setIsConnected(true);
          reconnectAttemptsRef.current = 0;
          
          // Start ping interval
          pingIntervalRef.current = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ type: 'ping' }));
            }
          }, 30000);
        };
        
        ws.onmessage = handleMessage;
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
        
        ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          setIsConnected(false);
          
          // Clear ping interval
          if (pingIntervalRef.current) {
            clearInterval(pingIntervalRef.current);
            pingIntervalRef.current = null;
          }
          
          // Attempt reconnection if not a clean close
          if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current += 1;
            console.log(`Reconnecting... Attempt ${reconnectAttemptsRef.current}`);
            setTimeout(() => {
              if (connectRef.current) connectRef.current();
            }, reconnectDelay * reconnectAttemptsRef.current);
          }
        };
        
        wsRef.current = ws;
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
      }
    };
  }, [getWebSocketUrl, handleMessage]);

  const disconnect = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnect');
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  const markAsRead = useCallback((notificationId) => {
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
    
    // Send mark_read to server
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'mark_read',
        notification_id: notificationId
      }));
    }
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
    setUnreadCount(0);
  }, []);

  const reconnect = useCallback(() => {
    if (connectRef.current) {
      connectRef.current();
    }
  }, []);

  // Connect when authenticated and workspace is available
  useEffect(() => {
    if (isAuthenticated && currentWorkspace?.id && token) {
      // Small delay to ensure connectRef is set
      const timer = setTimeout(() => {
        if (connectRef.current) connectRef.current();
      }, 100);
      return () => {
        clearTimeout(timer);
        disconnect();
      };
    } else {
      disconnect();
    }
  }, [isAuthenticated, currentWorkspace?.id, token, disconnect]);

  const value = {
    isConnected,
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    clearNotifications,
    reconnect
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export default WebSocketProvider;
