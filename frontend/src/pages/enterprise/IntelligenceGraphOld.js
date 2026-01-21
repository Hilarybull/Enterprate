import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkspace } from '@/context/WorkspaceContext';
import { PageHeader, FeatureCard } from '@/components/enterprise';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Network, 
  Activity, 
  Search, 
  Filter,
  Lightbulb,
  FileText,
  TrendingUp,
  Users,
  Globe,
  DollarSign,
  Clock
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const eventIcons = {
  'genesis': Lightbulb,
  'invoice': DollarSign,
  'lead': Users,
  'website': Globe,
  'project': FileText,
  'default': Activity
};

export default function IntelligenceGraph() {
  const { currentWorkspace, getHeaders } = useWorkspace();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (currentWorkspace) {
      loadEvents();
    } else {
      setLoading(false);
    }
  }, [currentWorkspace]);

  const loadEvents = async () => {
    try {
      const response = await axios.get(`${API_URL}/intel/events?limit=50`, {
        headers: getHeaders()
      });
      setEvents(response.data || []);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (type) => {
    const lowerType = type?.toLowerCase() || '';
    for (const key of Object.keys(eventIcons)) {
      if (lowerType.includes(key)) {
        return eventIcons[key];
      }
    }
    return eventIcons.default;
  };

  const formatEventType = (type) => {
    if (!type) return 'Activity';
    return type.replace(/_/g, ' ').replace(/\./g, ' - ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const filteredEvents = events.filter(event => 
    event.type?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    JSON.stringify(event.data)?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-slide-in" data-testid="intelligence-graph-page">
      <PageHeader
        icon={Network}
        title="Intelligence Graph"
        description="Visualize and analyze your business events and data relationships"
      />

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <FeatureCard
          title="Event Timeline"
          description="Track all business activities in chronological order"
          icon={Activity}
          gradient="gradient-primary"
        />
        <FeatureCard
          title="Data Insights"
          description="Discover patterns and trends in your business data"
          icon={TrendingUp}
          gradient="gradient-success"
        />
        <FeatureCard
          title="Smart Search"
          description="Find and filter events across your entire history"
          icon={Search}
          gradient="gradient-warning"
        />
      </div>

      {/* Events Timeline */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Business Events</CardTitle>
              <CardDescription>All activities across your workspace</CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="Search events..."
                  className="pl-9 w-64"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Button variant="outline" size="icon">
                <Filter size={16} />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredEvents.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center mx-auto mb-4">
                <Network className="text-white" size={28} />
              </div>
              <h3 className="font-semibold text-lg mb-2">No Events Found</h3>
              <p className="text-gray-500">
                {events.length === 0 
                  ? 'Events will appear here as you use the platform'
                  : 'No events match your search criteria'
                }
              </p>
            </div>
          ) : (
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />
              
              <div className="space-y-4">
                {filteredEvents.map((event, index) => {
                  const Icon = getEventIcon(event.type);
                  return (
                    <div key={event.id || index} className="relative flex items-start pl-14">
                      {/* Timeline dot */}
                      <div className="absolute left-4 w-5 h-5 rounded-full bg-purple-100 border-2 border-purple-500 flex items-center justify-center">
                        <div className="w-2 h-2 rounded-full bg-purple-500" />
                      </div>
                      
                      {/* Event card */}
                      <div className="flex-1 p-4 bg-gray-50 rounded-xl hover:bg-purple-50 transition-colors">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                              <Icon className="text-purple-600" size={20} />
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900">
                                {formatEventType(event.type)}
                              </h4>
                              <p className="text-sm text-gray-500 flex items-center">
                                <Clock size={12} className="mr-1" />
                                {new Date(event.occurredAt).toLocaleString()}
                              </p>
                            </div>
                          </div>
                        </div>
                        {event.data && Object.keys(event.data).length > 0 && (
                          <div className="mt-3 text-sm text-gray-600 bg-white p-3 rounded-lg">
                            <pre className="whitespace-pre-wrap text-xs">
                              {JSON.stringify(event.data, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
