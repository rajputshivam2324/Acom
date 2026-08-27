import React from 'react';
import { Search, Bell, ChevronDown, Sparkles, Globe, Server } from 'lucide-react';

export default function HeaderBar({ 
  onOpenCommandPalette, 
  environment, 
  setEnvironment, 
  aiProvider, 
  setAiProvider,
  unreadNotifications,
  onNotificationClick
}) {
  return (
    <header className="h-14 border-b border-slate-200 bg-white/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-10">
      {/* Title / Breadcrumbs */}
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-semibold text-slate-900">AI Incident Commander</h2>
        <span className="text-slate-300">/</span>
        <span className="text-xs text-slate-500 font-mono">prod-us-east-1</span>
      </div>

      {/* Center Search Input */}
      <div className="flex-1 max-w-md mx-6">
        <button
          onClick={onOpenCommandPalette}
          className="w-full flex items-center justify-between bg-slate-50 hover:bg-slate-100/80 border border-slate-200 hover:border-slate-300 px-3 py-1.5 rounded-lg text-xs text-slate-400 transition-all shadow-xs group"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 transition-colors" />
            <span className="text-slate-500 group-hover:text-slate-700">Search resources, incidents or run AI actions...</span>
          </div>
          <kbd className="hidden sm:inline-flex items-center gap-0.5 text-[10px] font-mono text-slate-400 bg-white px-1.5 py-0.5 rounded border border-slate-200 shadow-2xs">
            ⌘K
          </kbd>
        </button>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Environment Selector */}
        <div className="relative flex items-center text-xs bg-slate-50 border border-slate-200 rounded-md px-2.5 py-1 text-slate-700 font-medium">
          <Globe className="w-3.5 h-3.5 mr-1.5 text-slate-400" />
          <span className="mr-1 text-slate-400 font-normal">Env:</span>
          <select 
            value={environment}
            onChange={(e) => setEnvironment(e.target.value)}
            className="bg-transparent appearance-none pr-4 font-semibold text-slate-900 cursor-pointer focus:outline-none"
          >
            <option value="Production">Production</option>
            <option value="Staging">Staging</option>
            <option value="Dev-Cluster">Dev-Cluster</option>
          </select>
          <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2 pointer-events-none" />
        </div>

        {/* AI Provider Selector */}
        <div className="relative flex items-center text-xs bg-blue-50/60 border border-blue-200/80 rounded-md px-2.5 py-1 text-blue-900 font-medium">
          <Sparkles className="w-3.5 h-3.5 mr-1.5 text-blue-600" />
          <span className="mr-1 text-blue-500 font-normal">Provider:</span>
          <select 
            value={aiProvider}
            onChange={(e) => setAiProvider(e.target.value)}
            className="bg-transparent appearance-none pr-4 font-semibold text-blue-900 cursor-pointer focus:outline-none"
          >
            <option value="GPT-4">GPT-4</option>
            <option value="GPT-4-Turbo">GPT-4-Turbo</option>
            <option value="Claude-3.5-Sonnet">Claude 3.5 Sonnet</option>
            <option value="Local-Ollama">Local Ollama</option>
          </select>
          <ChevronDown className="w-3 h-3 text-blue-400 absolute right-2 pointer-events-none" />
        </div>

        {/* Notification Bell */}
        <button 
          onClick={onNotificationClick}
          className="relative p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
          title="Notifications"
        >
          <Bell className="w-4 h-4" />
          {unreadNotifications > 0 && (
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-red-500 ring-2 ring-white" />
          )}
        </button>
      </div>
    </header>
  );
}
