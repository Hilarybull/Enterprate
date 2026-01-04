import React, { useState } from 'react';
import { useWebSocket } from '@/context/WebSocketContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Bell, 
  BellOff,
  Check, 
  CheckCheck, 
  Trash2,
  Target,
  Globe,
  FlaskConical,
  Zap,
  Users,
  Calendar,
  Wifi,
  WifiOff
} from 'lucide-react';

const CATEGORY_ICONS = {
  lead: Target,
  website: Globe,
  ab_test: FlaskConical,
  automation: Zap,
  team: Users,
  scheduling: Calendar
};

const CATEGORY_COLORS = {
  lead: 'bg-green-100 text-green-600',
  website: 'bg-blue-100 text-blue-600',
  ab_test: 'bg-purple-100 text-purple-600',
  automation: 'bg-amber-100 text-amber-600',
  team: 'bg-indigo-100 text-indigo-600',
  scheduling: 'bg-pink-100 text-pink-600'
};

export default function NotificationCenter() {
  const { 
    isConnected, 
    notifications, 
    unreadCount, 
    markAsRead, 
    markAllAsRead, 
    clearNotifications 
  } = useWebSocket();
  const [open, setOpen] = useState(false);

  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button 
          variant="ghost" 
          size="sm" 
          className="relative"
          data-testid="notification-bell"
        >
          {isConnected ? (
            <Bell className="h-5 w-5" />
          ) : (
            <BellOff className="h-5 w-5 text-gray-400" />
          )}
          {unreadCount > 0 && (
            <Badge 
              className="absolute -top-1 -right-1 h-5 min-w-5 flex items-center justify-center p-0 text-xs bg-red-500 text-white"
              data-testid="notification-badge"
            >
              {unreadCount > 9 ? '9+' : unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-96 p-0" align="end">
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold">Notifications</h3>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              {isConnected ? (
                <>
                  <Wifi className="h-3 w-3 text-green-500" />
                  <span className="text-green-600">Live</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-3 w-3 text-gray-400" />
                  <span>Offline</span>
                </>
              )}
            </div>
          </div>
          <div className="flex gap-1">
            {unreadCount > 0 && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={markAllAsRead}
                className="h-8 px-2"
                title="Mark all as read"
              >
                <CheckCheck className="h-4 w-4" />
              </Button>
            )}
            {notifications.length > 0 && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={clearNotifications}
                className="h-8 px-2 text-red-500 hover:text-red-600"
                title="Clear all"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
        
        <ScrollArea className="max-h-[400px]">
          {notifications.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Bell className="h-8 w-8 mx-auto mb-2 text-gray-300" />
              <p className="text-sm">No notifications yet</p>
              <p className="text-xs mt-1">Real-time updates will appear here</p>
            </div>
          ) : (
            <div className="divide-y">
              {notifications.map((notification) => {
                const CategoryIcon = CATEGORY_ICONS[notification.category] || Bell;
                const colorClass = CATEGORY_COLORS[notification.category] || 'bg-gray-100 text-gray-600';
                
                return (
                  <div
                    key={notification.id}
                    className={`p-4 hover:bg-gray-50 cursor-pointer transition ${
                      !notification.read ? 'bg-blue-50/50' : ''
                    }`}
                    onClick={() => markAsRead(notification.id)}
                    data-testid={`notification-${notification.id}`}
                  >
                    <div className="flex gap-3">
                      <div className={`p-2 rounded-full ${colorClass}`}>
                        <CategoryIcon className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <p className={`text-sm ${!notification.read ? 'font-medium' : ''}`}>
                            {notification.message}
                          </p>
                          {!notification.read && (
                            <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                          )}
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="text-xs px-1.5 py-0">
                            {notification.category?.replace(/_/g, ' ')}
                          </Badge>
                          <span className="text-xs text-gray-400">
                            {formatTime(notification.timestamp || notification.receivedAt)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>
        
        {notifications.length > 0 && (
          <div className="p-3 border-t bg-gray-50 text-center">
            <span className="text-xs text-gray-500">
              {notifications.length} notification{notifications.length !== 1 ? 's' : ''}
            </span>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}
