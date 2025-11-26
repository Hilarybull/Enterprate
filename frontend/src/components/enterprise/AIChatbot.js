import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  MessageCircle, 
  X, 
  Send, 
  Loader2, 
  Sparkles,
  Trash2,
  Minimize2
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export default function AIChatbot() {
  const { token } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
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

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_URL}/chat`,
        { 
          message: userMessage,
          session_id: sessionId 
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (!sessionId) {
        setSessionId(response.data.session_id);
      }

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.response 
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.',
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

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
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          fixed bottom-6 right-6 z-50 
          w-14 h-14 rounded-full
          gradient-primary
          shadow-lg shadow-purple-500/30
          flex items-center justify-center
          transition-all duration-300 hover:scale-110
          ${isOpen ? 'rotate-0' : 'rotate-0'}
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
            fixed bottom-24 right-6 z-50
            w-[380px] h-[520px]
            bg-white rounded-2xl
            shadow-2xl shadow-purple-500/10
            border border-gray-200
            flex flex-col
            animate-slide-up
          "
          data-testid="chat-window"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center">
                <Sparkles className="text-white" size={20} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">AI Assistant</h3>
                <p className="text-xs text-gray-500">Powered by GPT-4o</p>
              </div>
            </div>
            <div className="flex items-center space-x-1">
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8 text-gray-400 hover:text-gray-600"
                onClick={clearChat}
                title="Clear chat"
              >
                <Trash2 size={16} />
              </Button>
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8 text-gray-400 hover:text-gray-600"
                onClick={() => setIsOpen(false)}
              >
                <Minimize2 size={16} />
              </Button>
            </div>
          </div>

          {/* Messages */}
          <ScrollArea className="flex-1 p-4">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center px-6">
                <div className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center mb-4">
                  <Sparkles className="text-white" size={28} />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">How can I help?</h4>
                <p className="text-sm text-gray-500">
                  Ask me about business ideas, operations, marketing strategies, or any feature in Enterprate OS.
                </p>
                <div className="mt-6 space-y-2 w-full">
                  {[
                    'How do I validate my business idea?',
                    'Help me create an invoice',
                    'What marketing strategies work best?'
                  ].map((suggestion, i) => (
                    <button
                      key={i}
                      onClick={() => setInput(suggestion)}
                      className="w-full text-left px-3 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-purple-50 hover:text-purple-700 transition-colors"
                    >
                      {suggestion}
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
                    <div
                      className={`
                        max-w-[85%] px-4 py-2.5 rounded-2xl
                        ${msg.role === 'user'
                          ? 'bg-purple-600 text-white rounded-br-md'
                          : msg.isError
                            ? 'bg-red-50 text-red-700 rounded-bl-md'
                            : 'bg-gray-100 text-gray-800 rounded-bl-md'
                        }
                      `}
                    >
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 text-gray-800 px-4 py-2.5 rounded-2xl rounded-bl-md">
                      <Loader2 className="w-5 h-5 animate-spin text-purple-600" />
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </ScrollArea>

          {/* Input */}
          <form onSubmit={sendMessage} className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <Input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                disabled={loading}
                className="flex-1 bg-gray-100 border-0 focus-visible:ring-1 focus-visible:ring-purple-500"
                data-testid="chat-input"
              />
              <Button 
                type="submit" 
                disabled={loading || !input.trim()}
                className="gradient-primary border-0 px-3"
                data-testid="chat-send"
              >
                <Send size={18} />
              </Button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}
