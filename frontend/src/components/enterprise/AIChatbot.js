import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { 
  MessageCircle, 
  X, 
  Send, 
  Loader2, 
  Sparkles,
  Trash2,
  Minimize2,
  CheckCircle,
  FileText,
  BarChart3,
  Building2,
  AlertCircle,
  ChevronDown
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// Mode configurations
const MODE_CONFIG = {
  advisory: {
    icon: FileText,
    label: 'Advisory',
    color: 'bg-blue-100 text-blue-700 border-blue-200',
    description: 'General guidance'
  },
  data_backed: {
    icon: CheckCircle,
    label: 'Verified',
    color: 'bg-green-100 text-green-700 border-green-200',
    description: 'Companies House data'
  },
  presentation: {
    icon: BarChart3,
    label: 'Presentation',
    color: 'bg-purple-100 text-purple-700 border-purple-200',
    description: 'Structured output'
  }
};

// Domain configurations
const DOMAIN_CONFIG = {
  genesis: {
    icon: '💡',
    label: 'Genesis AI',
    description: 'Formation & Planning'
  },
  navigator: {
    icon: '🧭',
    label: 'Navigator AI',
    description: 'Operations & Compliance'
  },
  growth: {
    icon: '📈',
    label: 'Growth AI',
    description: 'Marketing & Expansion'
  }
};

export default function AIChatbot() {
  const { token } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [companyContext, setCompanyContext] = useState({ number: '', name: '' });
  const [showCompanyInput, setShowCompanyInput] = useState(false);
  const [currentMode, setCurrentMode] = useState('advisory');
  const [currentDomain, setCurrentDomain] = useState('navigator');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const submitMessage = async (userMessageRaw, injectedContext = null) => {
    const userMessage = (userMessageRaw || '').trim();
    if (!userMessage || loading) return;
    setInput('');
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: userMessage,
      timestamp: new Date().toISOString()
    }]);
    setLoading(true);

    try {
      const payload = { 
        message: userMessage,
        session_id: sessionId
      };
      if (injectedContext) {
        payload.context = injectedContext;
      }
      
      // Include company context if provided
      if (companyContext.number) {
        payload.company_number = companyContext.number;
      }
      if (companyContext.name) {
        payload.company_name = companyContext.name;
      }

      const response = await axios.post(
        `${API_URL}/chat`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (!sessionId) {
        setSessionId(response.data.session_id);
      }

      // Update mode and domain from response
      if (response.data.mode) {
        setCurrentMode(response.data.mode);
      }
      if (response.data.domain) {
        setCurrentDomain(response.data.domain);
      }

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.response,
        mode: response.data.mode,
        domain: response.data.domain,
        dataSource: response.data.data_source,
        confidence: response.data.confidence,
        timestamp: response.data.timestamp
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      const backendDetail = error?.response?.data?.detail;
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: backendDetail || 'I apologise, but I encountered an error processing your request. Please try again.',
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    await submitMessage(input);
  };

  useEffect(() => {
    const handleExternalAsk = async (event) => {
      const message = event?.detail?.message || '';
      const context = event?.detail?.context || null;
      const autoSend = event?.detail?.autoSend !== false;
      if (!message || loading) return;
      setIsOpen(true);
      if (autoSend) {
        await submitMessage(message, context);
      } else {
        setInput(message);
      }
    };

    window.addEventListener('enterprate:ask-ai', handleExternalAsk);
    return () => window.removeEventListener('enterprate:ask-ai', handleExternalAsk);
  }, [loading]);

  const clearChat = async () => {
    if (sessionId) {
      try {
        await axios.delete(
          `${API_URL}/chat/history/${sessionId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch (error) {
        console.error('Failed to clear chat history:', error);
      }
    }
    setMessages([]);
    setSessionId(null);
    setCompanyContext({ number: '', name: '' });
    setCurrentMode('advisory');
    setCurrentDomain('navigator');
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  const ModeIcon = MODE_CONFIG[currentMode]?.icon || FileText;
  const domainInfo = DOMAIN_CONFIG[currentDomain] || DOMAIN_CONFIG.navigator;

  // Render message with markdown-like formatting
  const renderMessage = (content) => {
    // Split by double newlines for paragraphs
    const parts = content.split(/\n\n/);
    
    return parts.map((part, i) => {
      // Handle bullet points
      if (part.includes('\n- ') || part.startsWith('- ')) {
        const lines = part.split('\n');
        return (
          <div key={i} className="space-y-1">
            {lines.map((line, j) => {
              if (line.startsWith('- ')) {
                return <div key={j} className="pl-3 flex"><span className="mr-2">•</span><span>{formatInline(line.substring(2))}</span></div>;
              }
              return <div key={j}>{formatInline(line)}</div>;
            })}
          </div>
        );
      }
      
      // Handle headers
      if (part.startsWith('**') && part.endsWith('**')) {
        return <div key={i} className="font-semibold">{formatInline(part)}</div>;
      }
      
      return <p key={i} className="mb-2">{formatInline(part)}</p>;
    });
  };

  // Format inline markdown
  const formatInline = (text) => {
    // Bold: **text**
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      // Italic: *text*
      if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
        return <em key={i}>{part.slice(1, -1)}</em>;
      }
      return part;
    });
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          fixed bottom-20 right-6 z-50 
          w-14 h-14 rounded-full
          gradient-primary
          shadow-lg shadow-purple-500/30
          flex items-center justify-center
          transition-all duration-300 hover:scale-110
        `}
        data-testid="chat-toggle"
      >
        {isOpen ? (
          <X className="text-white" size={24} />
        ) : (
          <MessageCircle className="text-white" size={24} />
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div 
          className="
            fixed bottom-36 right-6 z-50
            w-[420px] h-[580px]
            bg-white rounded-2xl
            shadow-2xl shadow-purple-500/10
            border border-gray-200
            flex flex-col
            animate-slide-up
          "
          data-testid="chat-window"
        >
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <img 
                  src="https://customer-assets.emergentagent.com/job_saas-dashboard-20/artifacts/aems110l_Enterprate%20Logo.png" 
                  alt="Enterprate AI" 
                  className="h-7"
                />
                <span className="text-xs font-medium text-gray-500">AI Assistant</span>
              </div>
              <div className="flex items-center space-x-1">
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-7 w-7 text-gray-400 hover:text-gray-600"
                  onClick={clearChat}
                  title="Clear chat"
                >
                  <Trash2 size={14} />
                </Button>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-7 w-7 text-gray-400 hover:text-gray-600"
                  onClick={() => setIsOpen(false)}
                >
                  <Minimize2 size={14} />
                </Button>
              </div>
            </div>
            
            {/* Mode & Domain Indicator */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className={`text-xs ${MODE_CONFIG[currentMode]?.color}`}>
                  <ModeIcon size={10} className="mr-1" />
                  {MODE_CONFIG[currentMode]?.label}
                </Badge>
                <Badge variant="outline" className="text-xs bg-gray-50 text-gray-600">
                  <span className="mr-1">{domainInfo.icon}</span>
                  {domainInfo.label}
                </Badge>
              </div>
              <button
                onClick={() => setShowCompanyInput(!showCompanyInput)}
                className="text-xs text-purple-600 hover:text-purple-800 flex items-center gap-1"
              >
                <Building2 size={12} />
                {companyContext.number || companyContext.name ? 'Company Set' : 'Set Company'}
                <ChevronDown size={12} className={`transition-transform ${showCompanyInput ? 'rotate-180' : ''}`} />
              </button>
            </div>

            {/* Company Context Input */}
            {showCompanyInput && (
              <div className="mt-2 p-2 bg-gray-50 rounded-lg space-y-2">
                <div className="flex gap-2">
                  <Input
                    value={companyContext.number}
                    onChange={(e) => setCompanyContext(prev => ({ ...prev, number: e.target.value }))}
                    placeholder="Company Number"
                    className="text-xs h-7"
                  />
                  <Input
                    value={companyContext.name}
                    onChange={(e) => setCompanyContext(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Company Name"
                    className="text-xs h-7"
                  />
                </div>
                <p className="text-[10px] text-gray-500">
                  Set company context for verified data lookups from Companies House
                </p>
              </div>
            )}
          </div>

          {/* Messages */}
          <ScrollArea className="flex-1 p-4">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center px-4">
                <div className="w-14 h-14 rounded-2xl gradient-primary flex items-center justify-center mb-4">
                  <Sparkles className="text-white" size={24} />
                </div>
                <h4 className="font-semibold text-gray-900 mb-1">EnterprateAI AI Assistant</h4>
                <p className="text-xs text-gray-500 mb-4">
                  Decision-grade business intelligence. I operate in Advisory, Data-Backed, or Presentation mode based on your queries.
                </p>
                
                {/* Quick Actions */}
                <div className="w-full space-y-2">
                  <p className="text-xs text-gray-400 font-medium">Try asking:</p>
                  {[
                    { text: 'What features does EnterprateAI offer?', domain: 'navigator' },
                    { text: 'How do I create a website with the AI Website Builder?', domain: 'growth' },
                    { text: 'Check company status for 00445790', domain: 'navigator' },
                    { text: 'How do I validate my business idea?', domain: 'genesis' },
                    { text: 'What marketing tools are available?', domain: 'growth' },
                  ].map((suggestion, i) => (
                    <button
                      key={i}
                      onClick={() => handleSuggestionClick(suggestion.text)}
                      className="w-full text-left px-3 py-2 text-xs text-gray-600 bg-gray-50 rounded-lg hover:bg-purple-50 hover:text-purple-700 transition-colors flex items-center gap-2"
                    >
                      <span>{DOMAIN_CONFIG[suggestion.domain]?.icon}</span>
                      {suggestion.text}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[90%] ${msg.role === 'assistant' ? 'space-y-1' : ''}`}>
                      {/* Mode badge for assistant messages */}
                      {msg.role === 'assistant' && msg.mode && !msg.isError && (
                        <div className="flex items-center gap-1 mb-1">
                          <Badge variant="outline" className={`text-[10px] py-0 ${MODE_CONFIG[msg.mode]?.color}`}>
                            {MODE_CONFIG[msg.mode]?.label}
                          </Badge>
                          {msg.dataSource && (
                            <Badge variant="outline" className="text-[10px] py-0 bg-green-50 text-green-600">
                              {msg.dataSource}
                            </Badge>
                          )}
                        </div>
                      )}
                      
                      <div
                        className={`
                          px-3 py-2 rounded-2xl
                          ${msg.role === 'user'
                            ? 'bg-purple-600 text-white rounded-br-sm'
                            : msg.isError
                              ? 'bg-red-50 text-red-700 rounded-bl-sm border border-red-200'
                              : 'bg-gray-100 text-gray-800 rounded-bl-sm'
                          }
                        `}
                      >
                        <div className="text-sm whitespace-pre-wrap">
                          {msg.role === 'assistant' && !msg.isError 
                            ? renderMessage(msg.content) 
                            : msg.content
                          }
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 text-gray-800 px-3 py-2 rounded-2xl rounded-bl-sm flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin text-purple-600" />
                      <span className="text-xs text-gray-500">Analysing...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </ScrollArea>

          {/* Input */}
          <form onSubmit={sendMessage} className="p-3 border-t border-gray-200">
            <div className="flex space-x-2">
              <Input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about your business..."
                disabled={loading}
                className="flex-1 bg-gray-100 border-0 text-sm focus-visible:ring-1 focus-visible:ring-purple-500"
                data-testid="chat-input"
              />
              <Button 
                type="submit" 
                disabled={loading || !input.trim()}
                className="gradient-primary border-0 px-3"
                data-testid="chat-send"
              >
                <Send size={16} />
              </Button>
            </div>
            <p className="text-[10px] text-gray-400 mt-1 text-center">
              Verified data from Companies House • Non-speculative • Enterprise-grade
            </p>
          </form>
        </div>
      )}
    </>
  );
}
