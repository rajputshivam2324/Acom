import React, { useState } from 'react';
import { 
  Search, 
  AlertCircle, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  Sparkles, 
  Bot, 
  ExternalLink, 
  ChevronRight,
  Filter,
  Check
} from 'lucide-react';
import confetti from 'canvas-confetti';

export default function IncidentsList({ onSelectIncident, activeIncident, onResolveIncident }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIncidentForAnalysis, setSelectedIncidentForAnalysis] = useState(
    activeIncident ? 'INC-4821' : null
  );
  const [appliedFixes, setAppliedFixes] = useState({});

  const incidents = [
    {
      id: 'INC-4821',
      service: 'payment-api',
      issue: 'Payment API Outage - High latency & 500 errors in token validation',
      status: activeIncident ? 'Active' : 'Resolved',
      duration: '42m 15s',
      severity: 'SEV-1',
      created: '14:32 UTC',
      confidence: '94%',
      hypothesis: 'Deployment v2.4.1 introduced database connection pool limit mismatch.',
      pr: 'PR #1042'
    },
    {
      id: 'INC-4820',
      service: 'payment-gateway',
      issue: 'Stripe webhook parsing failure on recurring subscriptions',
      status: 'Resolved',
      duration: '1h 12m',
      severity: 'SEV-2',
      created: '11:15 UTC',
      confidence: '98%',
      hypothesis: 'JSON payload schema change in Stripe API header v2026-06.',
      pr: 'PR #1038'
    },
    {
      id: 'INC-4819',
      service: 'user-db-cluster',
      issue: 'CPU spike causing read timeouts on secondary replica',
      status: 'Resolved',
      duration: '45m',
      severity: 'SEV-3',
      created: '08:40 UTC',
      confidence: '99%',
      hypothesis: 'Unindexed query on user_sessions table after reporting job start.',
      pr: 'PR #1031'
    }
  ];

  const filteredIncidents = incidents.filter(
    (inc) =>
      inc.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.service.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.issue.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectedData = incidents.find((i) => i.id === selectedIncidentForAnalysis) || incidents[0];

  const handleApplyFix = (id) => {
    setAppliedFixes((prev) => ({ ...prev, [id]: true }));
    confetti({ particleCount: 70, spread: 60, origin: { y: 0.7 } });
    if (id === 'INC-4821' && onResolveIncident) {
      onResolveIncident();
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Incidents & Investigations</h1>
          <p className="text-xs text-slate-500 mt-1">Real-time status and AI-led root cause analysis.</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search incidents or ID... ⌘K"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-white border border-slate-200 rounded-lg pl-9 pr-4 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 w-64 shadow-2xs"
            />
          </div>
          <button className="p-2 border border-slate-200 rounded-lg bg-white text-slate-600 hover:bg-slate-50">
            <Filter className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Layout: Incident Table (2 cols) + AI Investigation Inspector (1 col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Incident Table */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-2xs p-5">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Incident Command History
            </h2>
            <span className="text-xs text-slate-400 font-mono">3 Total Records</span>
          </div>

          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 font-medium">
                  <th className="pb-2.5 font-normal">ID</th>
                  <th className="pb-2.5 font-normal">SERVICE / ISSUE</th>
                  <th className="pb-2.5 font-normal">STATUS</th>
                  <th className="pb-2.5 font-normal">DURATION</th>
                  <th className="pb-2.5 font-normal text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredIncidents.map((inc) => {
                  const isActive = inc.status === 'Active' && !appliedFixes[inc.id];
                  const isSelected = selectedIncidentForAnalysis === inc.id;

                  return (
                    <tr
                      key={inc.id}
                      onClick={() => setSelectedIncidentForAnalysis(inc.id)}
                      className={`cursor-pointer transition-colors ${
                        isSelected ? 'bg-slate-50 font-medium' : 'hover:bg-slate-50/70'
                      }`}
                    >
                      <td className="py-3 font-mono font-bold text-slate-900">
                        <div className="flex items-center gap-1.5">
                          {isActive && <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />}
                          <span>{inc.id}</span>
                        </div>
                      </td>
                      <td className="py-3 max-w-xs">
                        <span className="font-mono text-[11px] text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded mr-2 font-semibold">
                          {inc.service}
                        </span>
                        <span className="text-slate-800 line-clamp-1">{inc.issue}</span>
                      </td>
                      <td className="py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                          isActive
                            ? 'bg-red-100 text-red-700'
                            : 'bg-emerald-100 text-emerald-700'
                        }`}>
                          {isActive ? 'Active' : 'Resolved'}
                        </span>
                      </td>
                      <td className="py-3 font-mono text-slate-500">
                        {inc.duration}
                      </td>
                      <td className="py-3 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectIncident(inc.id);
                          }}
                          className="text-xs font-semibold text-slate-900 hover:text-blue-600 flex items-center gap-1 ml-auto"
                        >
                          <span>Inspect</span>
                          <ChevronRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* AI Auto-Analysis Side Panel */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              AI Auto-Analysis
            </h2>
            <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 text-[10px] font-bold">
              {selectedData.confidence} Confidence
            </span>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Diagnosis: {selectedData.id}
                </h3>
              </div>
              <span className="font-mono text-xs text-slate-400">{selectedData.service}</span>
            </div>

            {/* Hypothesis text */}
            <div>
              <span className="text-[11px] font-medium text-slate-400 block mb-1">
                Root Cause Hypothesis
              </span>
              <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
                {selectedData.hypothesis}
              </p>
            </div>

            {/* Linked PR */}
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100">
              <div>
                <span className="text-[10px] text-slate-400 block">Correlated Code PR</span>
                <span className="font-mono font-bold text-xs text-slate-900">{selectedData.pr}</span>
              </div>
              <button 
                onClick={() => onSelectIncident(selectedData.id)}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
              >
                <span>View Diff</span>
                <ExternalLink className="w-3 h-3" />
              </button>
            </div>

            {/* Recommended Action */}
            <div className="pt-2">
              <button
                onClick={() => handleApplyFix(selectedData.id)}
                disabled={appliedFixes[selectedData.id] || selectedData.status === 'Resolved'}
                className={`w-full py-2.5 rounded-lg text-xs font-bold text-white shadow-sm flex items-center justify-center gap-2 transition-all ${
                  appliedFixes[selectedData.id] || selectedData.status === 'Resolved'
                    ? 'bg-emerald-600'
                    : 'bg-slate-900 hover:bg-slate-800'
                }`}
              >
                {appliedFixes[selectedData.id] || selectedData.status === 'Resolved' ? (
                  <>
                    <Check className="w-4 h-4" />
                    <span>Fix Applied & Verified</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-blue-400" />
                    <span>Apply AI Mitigation</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
