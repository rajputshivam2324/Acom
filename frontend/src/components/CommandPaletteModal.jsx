import React, { useState, useEffect } from 'react';
import { Search, LayoutDashboard, AlertTriangle, Server, Layers, Sparkles, X, ArrowRight } from 'lucide-react';

export default function CommandPaletteModal({ isOpen, onClose, onNavigate }) {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        onClose(!isOpen);
      }
      if (e.key === 'Escape' && isOpen) {
        onClose(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const options = [
    { id: 'overview', title: 'Go to Command Center Overview', category: 'Navigation', icon: LayoutDashboard },
    { id: 'investigations', title: 'Open INC-4821 War Room (Payment Outage)', category: 'Active Incident', icon: AlertTriangle },
    { id: 'incidents', title: 'View All Incidents & AI Analysis', category: 'Navigation', icon: AlertTriangle },
    { id: 'integrations', title: 'Configure AI Provider & Integrations', category: 'Settings', icon: Layers },
    { id: 'services', title: 'View Core Services Topology', category: 'Navigation', icon: Server },
  ];

  const filtered = options.filter((o) =>
    o.title.toLowerCase().includes(query.toLowerCase()) ||
    o.category.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-50 flex items-start justify-center pt-20 px-4 animate-in fade-in duration-200">
      <div className="bg-white w-full max-w-xl rounded-xl shadow-2xl border border-slate-200 overflow-hidden">
        {/* Search Header */}
        <div className="p-3 border-b border-slate-100 flex items-center gap-3">
          <Search className="w-4 h-4 text-slate-400 ml-2" />
          <input
            type="text"
            autoFocus
            placeholder="Type a command or search resources..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full text-xs text-slate-900 focus:outline-none placeholder-slate-400 bg-transparent font-medium"
          />
          <button 
            onClick={() => onClose(false)}
            className="p-1 text-slate-400 hover:text-slate-600 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results list */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400">
              No matching commands or resources found.
            </div>
          ) : (
            filtered.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onNavigate(item.id);
                    onClose(false);
                  }}
                  className="w-full flex items-center justify-between p-2.5 rounded-lg text-xs hover:bg-slate-50 transition-colors text-left group"
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4 text-slate-400 group-hover:text-blue-600 transition-colors" />
                    <div>
                      <span className="font-medium text-slate-900 block">{item.title}</span>
                      <span className="text-[10px] text-slate-400">{item.category}</span>
                    </div>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-300 group-hover:text-slate-600 group-hover:translate-x-0.5 transition-all" />
                </button>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="p-2.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400 font-mono">
          <span>Navigate with ↑ ↓ • Press ESC to exit</span>
          <span className="flex items-center gap-1 text-blue-600">
            <Sparkles className="w-3 h-3" />
            AI Command Palette
          </span>
        </div>
      </div>
    </div>
  );
}
