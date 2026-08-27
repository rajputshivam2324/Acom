import React from 'react';
import { 
  LayoutDashboard, 
  AlertTriangle, 
  Server, 
  SearchCode, 
  Zap, 
  BarChart3, 
  Layers, 
  Settings, 
  ShieldAlert,
  Bot
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, activeIncidentCount }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'incidents', label: 'Incidents', icon: AlertTriangle, badge: activeIncidentCount > 0 ? activeIncidentCount : null },
    { id: 'services', label: 'Services', icon: Server },
    { id: 'investigations', label: 'Investigations', icon: SearchCode, highlight: true },
    { id: 'actions', label: 'Actions', icon: Zap },
    { id: 'reports', label: 'Reports', icon: BarChart3 },
    { id: 'integrations', label: 'Integrations', icon: Layers },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen sticky top-0 shrink-0 select-none z-20">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-100 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-slate-950 flex items-center justify-center text-white shadow-sm ring-1 ring-slate-900/10">
          <Bot className="w-5 h-5 text-blue-400" />
        </div>
        <div>
          <h1 className="font-semibold text-slate-900 text-sm tracking-tight leading-none">
            AI Commander
          </h1>
          <span className="text-[11px] font-mono text-slate-400">Incidents v2.4</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-2 py-1.5 text-[11px] font-medium text-slate-400 uppercase tracking-wider">
          Workspace
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-all ${
                isActive
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-4 text-center">
                  {item.badge}
                </span>
              )}
              {item.id === 'investigations' && !item.badge && (
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-ai-pulse" />
              )}
            </button>
          );
        })}
      </nav>

      {/* User Footer */}
      <div className="p-3 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center gap-3 px-2 py-1.5 rounded-md hover:bg-white transition-colors cursor-pointer border border-transparent hover:border-slate-200">
          <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center font-medium text-xs shadow-xs">
            AE
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-slate-900 truncate">Alex Engineer</p>
            <p className="text-[10px] text-slate-500 truncate">Lead SRE • On-Call</p>
          </div>
          <div className="w-2 h-2 rounded-full bg-emerald-500" title="On-Call Status Active" />
        </div>
      </div>
    </aside>
  );
}
