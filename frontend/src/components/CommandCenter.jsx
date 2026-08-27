import React, { useState } from 'react';
import { 
  CheckCircle2, 
  AlertCircle, 
  Server, 
  Clock, 
  ArrowRight, 
  Activity, 
  ShieldAlert, 
  Radio, 
  GitCommit, 
  Database,
  ExternalLink,
  ChevronRight,
  Layers
} from 'lucide-react';

export default function CommandCenter({ onJoinWarRoom, activeIncident, servicesList }) {
  const [selectedNode, setSelectedNode] = useState('Payment API');
  const [isAcknowledged, setIsAcknowledged] = useState(false);

  const topologyNodes = [
    { id: 'Frontend', name: 'Frontend Gateway', status: 'healthy', type: 'Gateway', load: '14.2k rpm' },
    { id: 'Payment API', name: 'Payment API', status: activeIncident ? 'critical' : 'healthy', type: 'Microservice', load: '4.8k rpm' },
    { id: 'Auth', name: 'Auth Service', status: 'healthy', type: 'Auth', load: '8.1k rpm' },
    { id: 'Database', name: 'User DB Cluster', status: 'healthy', type: 'Storage', connections: '248/250' }
  ];

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto animate-in fade-in duration-300">
      {/* Top Banner / Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Command Center</h1>
          <p className="text-xs text-slate-500 mt-1">Production health and active incidents overview.</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            Telemetry Stream Active
          </span>
        </div>
      </div>

      {/* 4 Metric Status Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: System Status */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition-shadow">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>System Status</span>
            <Activity className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">
              {activeIncident ? 'Degraded' : 'Healthy'}
            </span>
            <span className={`w-2.5 h-2.5 rounded-full ${activeIncident ? 'bg-amber-500 animate-ping' : 'bg-emerald-500'}`} />
          </div>
          <p className="mt-1 text-[11px] text-slate-500">
            {activeIncident ? '1 Service experiencing high error rate' : 'All systems operating within normal parameters'}
          </p>
        </div>

        {/* Card 2: Active Incidents */}
        <div className={`p-4 rounded-xl border transition-all ${
          activeIncident 
            ? 'bg-red-50/70 border-red-200 shadow-2xs' 
            : 'bg-white border-slate-200 shadow-2xs'
        }`}>
          <div className="flex items-center justify-between text-xs font-medium">
            <span className={activeIncident ? 'text-red-700' : 'text-slate-500'}>Active Incidents</span>
            <AlertCircle className={`w-4 h-4 ${activeIncident ? 'text-red-600 animate-bounce' : 'text-slate-400'}`} />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className={`text-2xl font-bold ${activeIncident ? 'text-red-600' : 'text-slate-900'}`}>
              {activeIncident ? '1' : '0'}
            </span>
            {activeIncident && (
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-red-100 text-red-700 uppercase tracking-wide">
                SEV-1
              </span>
            )}
          </div>
          <p className={`mt-1 text-[11px] ${activeIncident ? 'text-red-600' : 'text-slate-500'}`}>
            {activeIncident ? 'Payment API Outage (INC-4821)' : 'No active incident reports'}
          </p>
        </div>

        {/* Card 3: Services */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition-shadow">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>Services</span>
            <Server className="w-4 h-4 text-slate-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">
              {activeIncident ? '18/19' : '19/19'}
            </span>
            <span className="text-xs text-slate-500">healthy</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-500">94.7% operational capacity</p>
        </div>

        {/* Card 4: Actions Pending */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition-shadow">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>Actions Pending</span>
            <Radio className="w-4 h-4 text-blue-500" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">2</span>
            <span className="text-xs px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 font-mono">AI Suggestions</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-500">1 patch proposal ready for approval</p>
        </div>
      </div>

      {/* Main Content Grid: Hero Incident Card + Topology Vector */}
      {activeIncident && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Active Incident Hero Card */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-red-200 shadow-sm p-6 relative overflow-hidden flex flex-col justify-between">
            <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/5 rounded-full blur-2xl pointer-events-none" />

            <div>
              {/* Header tags */}
              <div className="flex items-center justify-between gap-2 flex-wrap">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-md bg-red-600 text-white font-mono text-xs font-bold uppercase tracking-wide">
                    SEV-1
                  </span>
                  <h3 className="font-semibold text-slate-900 text-base">
                    INC-4821: Payment API Outage
                  </h3>
                </div>
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 text-xs font-mono">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-ping" />
                  Investigating
                </span>
              </div>

              {/* Metrics Row */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-6 p-4 rounded-lg bg-slate-50 border border-slate-100">
                <div>
                  <span className="text-slate-400 text-[11px] block">Error Rate</span>
                  <span className="text-2xl font-bold text-red-600 font-mono">38.2%</span>
                  <span className="text-[10px] text-red-500 block font-mono mt-0.5">Threshold: 5.0%</span>
                </div>
                <div>
                  <span className="text-slate-400 text-[11px] block">p99 Latency</span>
                  <span className="text-2xl font-bold text-red-600 font-mono">928ms</span>
                  <span className="text-[10px] text-red-500 block font-mono mt-0.5">+480% vs baseline</span>
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <span className="text-slate-400 text-[11px] block">Impacted Endpoint</span>
                  <code className="text-xs text-slate-800 bg-white px-2 py-1 rounded border border-slate-200 block truncate mt-1">
                    POST /v1/checkout/process
                  </code>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between gap-3 flex-wrap">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span>Elapsed: <strong className="font-mono text-slate-700">14m 22s</strong></span>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setIsAcknowledged(!isAcknowledged)}
                  className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
                    isAcknowledged
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-300'
                      : 'bg-white text-slate-700 border border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  {isAcknowledged ? '✓ Acknowledged' : 'Acknowledge'}
                </button>
                <button
                  onClick={onJoinWarRoom}
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white shadow-sm flex items-center gap-2 transition-all hover:gap-3"
                >
                  <span>Join War Room</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* Topology Vector Graph */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  <Layers className="w-3.5 h-3.5 text-slate-400" />
                  Topology Vector
                </h4>
                <span className="text-[10px] font-mono text-slate-400">Click node to focus</span>
              </div>

              {/* Node Visual Box */}
              <div className="mt-4 p-4 bg-slate-50/70 border border-slate-200/80 rounded-lg min-h-[200px] flex flex-col items-center justify-center relative">
                {/* SVG Connecting Lines */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
                  {/* Top node to Center alert node */}
                  <line x1="50%" y1="28%" x2="50%" y2="52%" stroke="#cbd5e1" strokeWidth="2" strokeDasharray="4 2" />
                  {/* Center node to bottom left */}
                  <line x1="50%" y1="58%" x2="30%" y2="82%" stroke="#cbd5e1" strokeWidth="2" />
                  {/* Center node to bottom right */}
                  <line x1="50%" y1="58%" x2="70%" y2="82%" stroke="#cbd5e1" strokeWidth="2" />
                </svg>

                {/* Nodes Stack */}
                <div className="w-full flex flex-col items-center gap-6 z-10">
                  {/* Top Node */}
                  <button
                    onClick={() => setSelectedNode('Frontend')}
                    className={`px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all ${
                      selectedNode === 'Frontend'
                        ? 'bg-slate-900 text-white shadow-md ring-2 ring-slate-400'
                        : 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    Frontend
                  </button>

                  {/* Alert Node */}
                  <button
                    onClick={() => setSelectedNode('Payment API')}
                    className={`px-4 py-2 rounded-md text-xs font-mono font-bold transition-all ${
                      selectedNode === 'Payment API'
                        ? 'bg-red-600 text-white shadow-lg ring-4 ring-red-200 animate-pulse'
                        : 'bg-red-100 border border-red-300 text-red-700 hover:bg-red-200'
                    }`}
                  >
                    Payment API ⚠️
                  </button>

                  {/* Bottom Nodes */}
                  <div className="flex items-center gap-8">
                    <button
                      onClick={() => setSelectedNode('Auth')}
                      className={`px-3 py-1 rounded text-xs font-mono transition-all ${
                        selectedNode === 'Auth'
                          ? 'bg-slate-900 text-white shadow'
                          : 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      Auth
                    </button>
                    <button
                      onClick={() => setSelectedNode('Database')}
                      className={`px-3 py-1 rounded text-xs font-mono transition-all ${
                        selectedNode === 'Database'
                          ? 'bg-slate-900 text-white shadow'
                          : 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      Database
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Selected Node Inspector Footer */}
            <div className="mt-4 p-3 bg-slate-100 rounded-lg text-xs flex items-center justify-between">
              <div>
                <span className="text-slate-400 block text-[10px]">Selected Node:</span>
                <span className="font-semibold text-slate-900">{selectedNode}</span>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase ${
                selectedNode === 'Payment API' && activeIncident
                  ? 'bg-red-100 text-red-700 font-bold'
                  : 'bg-emerald-100 text-emerald-700'
              }`}>
                {selectedNode === 'Payment API' && activeIncident ? 'CRITICAL' : 'HEALTHY'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Row: Operation Timeline + Core Services List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Operation Timeline */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-400" />
              Operation Timeline
            </h3>
            <span className="text-xs text-slate-400 font-mono">Live UTC Logs</span>
          </div>

          <div className="mt-4 space-y-4">
            {/* Event 1 */}
            <div className="flex gap-3 relative">
              <div className="flex flex-col items-center">
                <div className="w-3 h-3 rounded-full bg-red-500 ring-4 ring-red-100 mt-1" />
                <div className="w-0.5 h-full bg-slate-200 mt-2" />
              </div>
              <div className="flex-1 pb-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono font-medium text-slate-400">14:32:05 UTC</span>
                  <span className="px-1.5 py-0.5 rounded bg-red-50 text-red-700 text-[10px] font-semibold">Alert</span>
                </div>
                <p className="text-xs font-semibold text-slate-900 mt-0.5">
                  Alert triggered: High Error Rate
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Payment API error rate exceeded 20% threshold over 5m window.
                </p>
              </div>
            </div>

            {/* Event 2 */}
            <div className="flex gap-3 relative">
              <div className="flex flex-col items-center">
                <div className="w-3 h-3 rounded-full bg-slate-400 ring-4 ring-slate-100 mt-1" />
                <div className="w-0.5 h-full bg-slate-200 mt-2" />
              </div>
              <div className="flex-1 pb-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono font-medium text-slate-400">14:28:12 UTC</span>
                  <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px]">Deploy</span>
                </div>
                <p className="text-xs font-semibold text-slate-900 mt-0.5">
                  Deploy started: Payment Service v2.4.1
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Automated deployment initiated by CI/CD pipeline (commit #a8f42).
                </p>
              </div>
            </div>

            {/* Event 3 */}
            <div className="flex gap-3">
              <div className="flex flex-col items-center">
                <div className="w-3 h-3 rounded-full bg-emerald-400 ring-4 ring-emerald-100 mt-1" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono font-medium text-slate-400">14:15:00 UTC</span>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[10px]">Maintenance</span>
                </div>
                <p className="text-xs font-semibold text-slate-900 mt-0.5">
                  Database Maintenance (Routine)
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Scheduled vacuum operation completed successfully.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Core Services Table */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Server className="w-4 h-4 text-slate-400" />
              Core Services
            </h3>
            <button className="text-xs font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1">
              View All <ChevronRight className="w-3 h-3" />
            </button>
          </div>

          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 font-medium">
                  <th className="pb-2 font-normal">Service Name</th>
                  <th className="pb-2 font-normal">Status</th>
                  <th className="pb-2 font-normal text-right">Latency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {servicesList.map((service) => (
                  <tr key={service.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${
                          service.status === 'Critical' ? 'bg-red-500 animate-ping' : 'bg-emerald-500'
                        }`} />
                        <span className="font-mono font-medium text-slate-900">{service.name}</span>
                      </div>
                    </td>
                    <td className="py-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        service.status === 'Critical'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-emerald-100 text-emerald-700'
                      }`}>
                        {service.status}
                      </span>
                    </td>
                    <td className="py-2.5 text-right font-mono text-slate-600">
                      {service.latency}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
