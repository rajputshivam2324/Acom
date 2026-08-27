import React, { useState } from 'react';
import { 
  Layers, 
  GitBranch, 
  Activity, 
  FileText, 
  Boxes, 
  Plus, 
  CheckCircle2, 
  AlertTriangle, 
  Eye, 
  EyeOff, 
  Sparkles, 
  Bot, 
  Save, 
  RefreshCw,
  SlidersHorizontal
} from 'lucide-react';

export default function IntegrationsConfig({ onSaveNotification }) {
  const [showApiKey, setShowApiKey] = useState(false);
  const [providerType, setProviderType] = useState('OpenAI (Standard)');
  const [baseUrl, setBaseUrl] = useState('https://api.openai.com/v1');
  const [apiKey, setApiKey] = useState('sk-proj-98237498234987239487239482');
  const [defaultModel, setDefaultModel] = useState('gpt-4-turbo-preview');
  const [systemPromptToggle, setSystemPromptToggle] = useState(true);
  const [systemPrompt, setSystemPrompt] = useState(
    'You are an expert SRE AI assistant. Analyze the provided logs and metrics to identify root causes...'
  );
  const [isSaving, setIsSaving] = useState(false);
  const [k8sStatus, setK8sStatus] = useState('Degraded');

  const handleSave = () => {
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
      if (onSaveNotification) {
        onSaveNotification('AI & Integrations settings updated successfully!');
      }
    }, 600);
  };

  const handleRenewK8s = () => {
    setK8sStatus('Connected');
    if (onSaveNotification) {
      onSaveNotification('Kubernetes auth token renewed successfully!');
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto animate-in fade-in duration-300">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Integrations & AI Config</h1>
          <p className="text-xs text-slate-500 mt-1">Manage external tool connections and configure AI provider settings.</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => onSaveNotification('Connections tested: All systems operational.')}
            className="px-4 py-2 rounded-lg text-xs font-medium border border-slate-300 text-slate-700 bg-white hover:bg-slate-50 transition-colors shadow-2xs"
          >
            Test Connections
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white shadow-sm flex items-center gap-2 transition-all"
          >
            {isSaving ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Save className="w-3.5 h-3.5" />
            )}
            <span>Save Changes</span>
          </button>
        </div>
      </div>

      {/* Grid: Integrations List (2 Cols) + AI Config Sidebar (1 Col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Active Integrations */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Active Integrations
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Integration 1: GitHub */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition-shadow flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-slate-900 text-white flex items-center justify-center">
                      <GitBranch className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-slate-900">GitHub</h3>
                      <span className="text-[10px] text-emerald-600 font-medium flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        CONNECTED
                      </span>
                    </div>
                  </div>
                  <button className="text-slate-400 hover:text-slate-600">•••</button>
                </div>
                <p className="text-xs text-slate-500 mt-3 leading-relaxed">
                  Source code, PRs, and commit history for root cause analysis.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="font-mono text-slate-500 text-[11px]">org: sre-commander</span>
                <button className="font-medium text-slate-700 hover:text-slate-900 border border-slate-200 px-2.5 py-1 rounded bg-slate-50">
                  Configure
                </button>
              </div>
            </div>

            {/* Integration 2: Prometheus */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition-shadow flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-orange-50 text-orange-600 border border-orange-200 flex items-center justify-center">
                      <Activity className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-slate-900">Prometheus</h3>
                      <span className="text-[10px] text-emerald-600 font-medium flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        CONNECTED
                      </span>
                    </div>
                  </div>
                  <button className="text-slate-400 hover:text-slate-600">•••</button>
                </div>
                <p className="text-xs text-slate-500 mt-3 leading-relaxed">
                  Metrics and alerting infrastructure integration.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="font-mono text-slate-500 text-[11px]">endpoint: /api/v1/query</span>
                <button className="font-medium text-slate-700 hover:text-slate-900 border border-slate-200 px-2.5 py-1 rounded bg-slate-50">
                  Configure
                </button>
              </div>
            </div>

            {/* Integration 3: Loki */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition-shadow flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-600 border border-blue-200 flex items-center justify-center">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-slate-900">Loki</h3>
                      <span className="text-[10px] text-emerald-600 font-medium flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        CONNECTED
                      </span>
                    </div>
                  </div>
                  <button className="text-slate-400 hover:text-slate-600">•••</button>
                </div>
                <p className="text-xs text-slate-500 mt-3 leading-relaxed">
                  Log aggregation and stream analysis for AI context.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="font-mono text-slate-500 text-[11px]">retention: 30d</span>
                <button className="font-medium text-slate-700 hover:text-slate-900 border border-slate-200 px-2.5 py-1 rounded bg-slate-50">
                  Configure
                </button>
              </div>
            </div>

            {/* Integration 4: Kubernetes */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition-shadow flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-200 flex items-center justify-center">
                      <Boxes className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-slate-900">Kubernetes</h3>
                      <span className={`text-[10px] font-medium flex items-center gap-1 ${
                        k8sStatus === 'Connected' ? 'text-emerald-600' : 'text-amber-600'
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          k8sStatus === 'Connected' ? 'bg-emerald-500' : 'bg-amber-500 animate-ping'
                        }`} />
                        {k8sStatus.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <button className="text-slate-400 hover:text-slate-600">•••</button>
                </div>
                <p className="text-xs text-slate-500 mt-3 leading-relaxed">
                  Cluster state, pod events, and deployment tracking.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className={`font-mono text-[11px] ${k8sStatus === 'Connected' ? 'text-emerald-600' : 'text-amber-600 font-semibold'}`}>
                  {k8sStatus === 'Connected' ? 'token active' : 'auth token expiring'}
                </span>
                <button
                  onClick={handleRenewK8s}
                  className={`font-semibold text-xs border px-3 py-1 rounded transition-colors ${
                    k8sStatus === 'Connected'
                      ? 'bg-slate-50 text-slate-700 border-slate-200'
                      : 'bg-amber-500 hover:bg-amber-600 text-white border-amber-600 shadow-2xs'
                  }`}
                >
                  {k8sStatus === 'Connected' ? 'Configure' : 'Renew Token'}
                </button>
              </div>
            </div>
          </div>

          {/* Add New Integration Button Card */}
          <button className="w-full p-4 rounded-xl border border-dashed border-slate-300 hover:border-slate-400 hover:bg-slate-50 transition-colors flex items-center justify-center gap-2 text-xs font-medium text-slate-600">
            <Plus className="w-4 h-4 text-slate-400" />
            <span>Add New Integration (Datadog, PagerDuty, Grafana, Slack)</span>
          </button>
        </div>

        {/* Right Column: AI Provider Config */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              AI Provider Config
            </h2>
            <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-700 text-[10px] font-bold">
              Active Provider
            </span>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs space-y-4">
            {/* Header / Subtitle */}
            <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
              <Bot className="w-4 h-4 text-blue-600" />
              <h3 className="text-xs font-semibold text-slate-900">Model Settings</h3>
            </div>

            {/* Provider Type Dropdown */}
            <div>
              <label className="text-xs font-medium text-slate-700 block mb-1">
                Provider Type
              </label>
              <select
                value={providerType}
                onChange={(e) => setProviderType(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="OpenAI (Standard)">OpenAI (Standard)</option>
                <option value="Anthropic Claude">Anthropic Claude</option>
                <option value="Google Gemini 1.5">Google Gemini</option>
                <option value="Ollama / Local">Ollama (Local)</option>
              </select>
            </div>

            {/* Base URL */}
            <div>
              <label className="text-xs font-medium text-slate-700 block mb-1">
                Base URL
              </label>
              <input
                type="text"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* API Key */}
            <div>
              <label className="text-xs font-medium text-slate-700 block mb-1">
                API Key
              </label>
              <div className="relative">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 pr-9 text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showApiKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            {/* Default Model */}
            <div>
              <label className="text-xs font-medium text-slate-700 block mb-1">
                Default Model
              </label>
              <select
                value={defaultModel}
                onChange={(e) => setDefaultModel(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="gpt-4-turbo-preview">gpt-4-turbo-preview</option>
                <option value="gpt-4o">gpt-4o</option>
                <option value="claude-3-5-sonnet">claude-3-5-sonnet</option>
              </select>
            </div>

            {/* System Prompt Override Toggle */}
            <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs font-medium text-slate-700">System Prompt Override</span>
              <button
                type="button"
                onClick={() => setSystemPromptToggle(!systemPromptToggle)}
                className={`w-9 h-5 rounded-full transition-colors relative ${
                  systemPromptToggle ? 'bg-blue-600' : 'bg-slate-300'
                }`}
              >
                <span className={`w-3.5 h-3.5 rounded-full bg-white absolute top-0.75 transition-transform ${
                  systemPromptToggle ? 'left-[18px]' : 'left-1'
                }`} />
              </button>
            </div>

            {/* System Prompt Textarea */}
            {systemPromptToggle && (
              <div>
                <textarea
                  rows={4}
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs font-mono text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
