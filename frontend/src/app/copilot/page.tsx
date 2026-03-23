"use client";

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User, Quote, ChevronRight, AlertCircle, RefreshCw } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import ChatModeSelector, { CopilotMode } from '@/components/chat/ChatModeSelector';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: any; // Can be string or structured object from API
  citations?: string[];
  timestamp: Date;
}

export default function CopilotPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<CopilotMode>('soc');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await apiClient.chat(input, mode);
      
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer || response.content,
        citations: response.citations,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMsg]);
    } catch (error) {
      console.error('Chat error:', error);
      // Add error message to chat
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] max-w-5xl mx-auto space-y-6 animate-in fade-in duration-700">
      <div className="space-y-2">
        <h2 className="text-3xl font-bold tracking-tight text-white glow-text">AI Copilot</h2>
        <p className="text-slate-400">Contextual intelligence across multiple security and governance domains.</p>
      </div>

      <ChatModeSelector currentMode={mode} onModeChange={setMode} />

      <div className="flex-1 glass rounded-2xl border border-slate-700/50 flex flex-col overflow-hidden relative">
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-8 scroll-smooth">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-50">
              <Bot className="w-16 h-16 text-blue-500" />
              <div className="space-y-1">
                <p className="text-white font-medium">System Ready</p>
                <p className="text-sm text-slate-500 max-w-xs">Select a mode and ask a question grounded in your environment's data.</p>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}
              
              <div className={`max-w-[85%] space-y-3 ${msg.role === 'user' ? 'text-right' : ''}`}>
                <div className={`p-4 rounded-2xl inline-block text-left relative ${
                  msg.role === 'user' 
                  ? 'bg-blue-600 text-white shadow-xl shadow-blue-500/10' 
                  : 'bg-slate-800/50 border border-slate-700 text-slate-200'
                }`}>
                  {typeof msg.content === 'string' ? (
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  ) : (
                    <div className="space-y-4">
                      {msg.content.summary && <p className="font-semibold text-blue-400 text-xs uppercase tracking-wider">Executive Summary: {msg.content.summary}</p>}
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content.answer || msg.content}</p>
                      {msg.content.actions && msg.content.actions.length > 0 && (
                        <div className="mt-4 p-3 rounded-lg bg-slate-900/50 border border-slate-700">
                          <p className="text-xs font-bold text-slate-400 mb-2 flex items-center gap-2">
                             <ChevronRight className="w-3 h-3" /> Recommended Next Actions
                          </p>
                          <ul className="space-y-1">
                            {msg.content.actions.map((action: string, idx: number) => (
                              <li key={idx} className="text-xs text-slate-300 flex gap-2">
                                <span className="text-blue-500">•</span> {action}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>


                {msg.citations && msg.citations.length > 0 && (
                  <div className="flex flex-wrap gap-2 animate-in fade-in zoom-in duration-300">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1 mt-1">
                      <Quote className="w-3 h-3" /> Grounding Sources:
                    </span>
                    {msg.citations.map((cite, i) => (
                      <span key={i} className="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-800 text-[10px] text-slate-400 font-medium">
                        {cite}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center shrink-0 border border-slate-600">
                  <User className="w-5 h-5 text-slate-300" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-4 animate-in fade-in duration-300">
              <div className="w-8 h-8 rounded-lg bg-blue-900 flex items-center justify-center shrink-0">
                <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
              </div>
              <div className="flex gap-1 items-center p-4 bg-slate-800/30 rounded-2xl border border-dashed border-slate-700">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce"></span>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
          <form onSubmit={handleSend} className="relative group">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Ask the ${mode.toUpperCase()} assistant...`}
              disabled={isLoading}
              className="w-full bg-slate-800/50 border border-slate-700 rounded-2xl py-4 pl-6 pr-14 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all focus:border-blue-500/50"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50 disabled:bg-slate-700 transition-all shadow-lg"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
          <div className="mt-3 flex items-center justify-center gap-6 text-[10px] font-medium text-slate-600">
            <span className="flex items-center gap-1"><Shield className="w-3 h-3" /> Encrypted Session</span>
            <span className="flex items-center gap-1"><RefreshCw className="w-3 h-3" /> LLM Grounding Active</span>
          </div>
        </div>
      </div>
    </div>
  );
}
