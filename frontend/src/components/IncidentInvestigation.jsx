import React, { useState } from 'react';
import { 
  ArrowLeft, 
  CheckCircle2, 
  AlertTriangle, 
  Activity, 
  GitPullRequest, 
  Bot, 
  Sparkles, 
  Check, 
  X, 
  RotateCcw,
  Zap,
  ShieldCheck,
  TrendingUp,
  FileCode2,
  ListChecks
} from 'lucide-react';
import confetti from 'canvas-confetti';

export default function IncidentInvestigation({ onBack, onResolveIncident }) {
  const [pipelineStep, setPipelineStep] = useState(2); // 1: Detected, 2: Investigating, 3: Root Cause, 4: Repair, 5: Approval, 6: Resolved
  const [isApplyingFix, setIsApplyingFix] = useState(false);
  const [fixApplied, setFixApplied] = useState(false);

  const steps = [
    { id: 1, label: 'Detected' },
    { id: 2, label: 'Investigating' },
    { id: 3, label: 'Root Cause' },
    { id: 4, label: 'Repair' },
    { id: 5, label: 'Approval' },
    { id: 6, label: 'Resolved' },
  ];

  const handleApproveRepair = () => {
    setIsApplyingFix(true);
    setPipelineStep(4);

    setTimeout(() => {
      setPipelineStep(5);
    }, 1200);

    setTimeout(() => {
      setPipelineStep(6);
      setIsApplyingFix(false);
      setFixApplied(true);
      
      // Trigger celebrate confetti
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 }
      });

      if (onResolveIncident) {
        onResolveIncident();
      }
    }, 2500);
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto animate-in fade-in duration-300">
      {/* Top Header Navigation */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition-colors"
            title="Back to Command Center"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-bold text-slate-900 font-mono">INC-4821</h1>
              <span className="text-lg text-slate-300">|</span>
              <h2 className="text-lg font-semibold text-slate-800">Payment API Outage</h2>
              <span className="px-2.5 py-0.5 rounded bg-red-600 text-white font-mono text-xs font-bold uppercase">
                SEV-1
              </span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium flex items-center gap-1.5 ${
                fixApplied 
                  ? 'bg-emerald-100 text-emerald-800' 
                  : 'bg-blue-100 text-blue-800'
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${fixApplied ? 'bg-emerald-500' : 'bg-blue-500 animate-ping'}`} />
                {fixApplied ? 'Resolved' : 'Investigating'}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-400">Timer: <strong className="text-slate-700">T+0:14:22</strong></span>
        </div>
      </div>

      {/* Progress Lifecycle Pipeline Stepper */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex items-center justify-between relative max-w-4xl mx-auto">
          {/* Connector Line */}
          <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-slate-200 -translate-y-1/2 z-0" />
          <div 
            className="absolute top-1/2 left-0 h-0.5 bg-blue-600 -translate-y-1/2 z-0 transition-all duration-500" 
            style={{ width: `${((pipelineStep - 1) / (steps.length - 1)) * 100}%` }}
          />

          {steps.map((step) => {
            const isCompleted = step.id < pipelineStep;
            const isCurrent = step.id === pipelineStep;

            return (
              <div key={step.id} className="relative z-10 flex flex-col items-center group">
                <button
                  onClick={() => setPipelineStep(step.id)}
                  className={`w-9 h-9 rounded-full flex items-center justify-center font-mono text-xs font-bold transition-all ${
                    isCompleted
                      ? 'bg-blue-600 text-white shadow-sm'
                      : isCurrent
                      ? 'bg-white border-2 border-blue-600 text-blue-600 shadow-md ring-4 ring-blue-100 animate-pulse'
                      : 'bg-slate-100 border border-slate-300 text-slate-400'
                  }`}
                >
                  {isCompleted ? <Check className="w-4 h-4 stroke-[3]" /> : step.id}
                </button>
                <span className={`mt-2 text-xs font-medium ${
                  isCurrent ? 'text-blue-600 font-semibold' : isCompleted ? 'text-slate-800' : 'text-slate-400'
                }`}>
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Service Impact Alert Card */}
      <div className="bg-red-50/70 border border-red-200 rounded-xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <h3 className="text-xs font-bold text-red-800 uppercase tracking-wider">Service Impact Summary</h3>
          </div>
          <div className="mt-2 flex items-baseline gap-4 flex-wrap">
            <div>
              <span className="text-xs text-red-600 font-medium">Failure Rate: </span>
              <span className="text-xl font-bold font-mono text-red-700">
                {fixApplied ? '0.01%' : '38.2%'}
              </span>
            </div>
            <div className="text-xs text-red-900">
              <strong>Primary Symptom:</strong> Payment checkout flow is completely unavailable for a subset of users. High volume of <code className="bg-red-100 text-red-800 px-1 py-0.5 rounded font-mono">500 Internal Server Error</code> responses from <code className="bg-red-100 text-red-800 px-1 py-0.5 rounded font-mono">/v1/checkout/process</code>.
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Telemetry + Investigation Stream + Code Diff + Repair Proposal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (Telemetry & Git Diff) */}
        <div className="lg:col-span-2 space-y-6">
          {/* System Telemetry Section */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Activity className="w-4 h-4 text-blue-600" />
                System Telemetry
              </h3>
              <span className="text-xs font-mono text-slate-400">Live 15m Window</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
              {/* Chart 1: Error Rate */}
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-[11px] font-medium text-slate-500 block">Error Rate</span>
                <div className="h-24 mt-2 flex items-end gap-1">
                  {[1.2, 1.4, 1.1, 1.3, 1.5, 38.2, 36.5, 38.2].map((val, idx) => (
                    <div key={idx} className="flex-1 flex flex-col justify-end h-full">
                      <div 
                        style={{ height: `${(val / 40) * 100}%` }}
                        className={`w-full rounded-t transition-all ${idx >= 5 ? (fixApplied ? 'bg-emerald-500' : 'bg-red-500') : 'bg-blue-400'}`} 
                        title={`Error Rate: ${val}%`}
                      />
                    </div>
                  ))}
                </div>
                <div className="flex justify-between text-[10px] text-slate-400 mt-2 font-mono">
                  <span>-15m</span>
                  <span>Now</span>
                </div>
              </div>

              {/* Chart 2: Latency */}
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-[11px] font-medium text-slate-500 block">Latency (p99)</span>
                <div className="h-24 mt-2 flex items-end gap-1">
                  {[120, 115, 130, 125, 928, 910, 928].map((val, idx) => (
                    <div key={idx} className="flex-1 flex flex-col justify-end h-full">
                      <div 
                        style={{ height: `${(val / 1000) * 100}%` }}
                        className={`w-full rounded-t transition-all ${idx >= 4 ? (fixApplied ? 'bg-emerald-500' : 'bg-red-500') : 'bg-blue-400'}`}
                        title={`p99: ${val}ms`}
                      />
                    </div>
                  ))}
                </div>
                <div className="flex justify-between text-[10px] text-slate-400 mt-2 font-mono">
                  <span>-15m</span>
                  <span>928ms</span>
                </div>
              </div>

              {/* Chart 3: DB Connections */}
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-[11px] font-medium text-slate-500 block">DB Connections</span>
                <div className="h-24 mt-2 flex items-end gap-1">
                  {[45, 48, 50, 240, 248, 250, 248].map((val, idx) => (
                    <div key={idx} className="flex-1 flex flex-col justify-end h-full">
                      <div 
                        style={{ height: `${(val / 250) * 100}%` }}
                        className={`w-full rounded-t transition-all ${idx >= 3 ? (fixApplied ? 'bg-emerald-500' : 'bg-amber-500') : 'bg-blue-400'}`}
                        title={`Connections: ${val}`}
                      />
                    </div>
                  ))}
                </div>
                <div className="flex justify-between text-[10px] text-slate-400 mt-2 font-mono">
                  <span>Pool: 250</span>
                  <span>248/250</span>
                </div>
              </div>
            </div>
          </div>

          {/* Deployment v42 Code Diff Widget */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
            <div className="p-4 bg-slate-50/80 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileCode2 className="w-4 h-4 text-slate-600" />
                <h3 className="text-xs font-semibold text-slate-900 font-mono">
                  Deployment v42 Diff (services/payment/db.py)
                </h3>
              </div>
              <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 text-[11px] font-semibold flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-blue-600" />
                AI Analysis Active
              </span>
            </div>

            {/* Code Diff Block */}
            <div className="p-4 bg-slate-950 font-mono text-xs text-slate-200 overflow-x-auto">
              <div className="space-y-1">
                <div className="text-slate-500">12 12 pool = db.create_pool(</div>
                <div className="bg-red-950/80 text-red-300 px-2 py-0.5 rounded flex items-center gap-3">
                  <span className="text-red-500 select-none">- 13</span>
                  <span>- max_connections=50,</span>
                </div>
                <div className="bg-emerald-950/80 text-emerald-300 px-2 py-0.5 rounded flex items-center gap-3">
                  <span className="text-emerald-500 select-none">+ 13</span>
                  <span>+ max_connections=int(os.environ.get('DB_POOL_SIZE', 250)),</span>
                </div>
                <div className="text-slate-500">14 14 )</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Investigation Stream + Repair Proposal */}
        <div className="space-y-6">
          {/* Investigation Stream */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <ListChecks className="w-4 h-4 text-slate-400" />
                Investigation Stream
              </h3>
              <span className="text-xs font-mono text-blue-600 font-medium">Auto-Ingest</span>
            </div>

            <div className="mt-4 space-y-3">
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                <p className="text-xs text-slate-600">
                  Checked <code className="text-slate-800 font-mono">payment-gateway</code> health endpoints. Found 500s.
                </p>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                <p className="text-xs text-slate-600">
                  Analyzed Datadog metrics. Error rate spike correlates with Deploy v42.
                </p>
              </div>

              <div className="p-2.5 rounded-lg bg-blue-50/70 border border-blue-200 flex items-start gap-2.5">
                <Bot className="w-4 h-4 text-blue-600 mt-0.5 shrink-0 animate-spin" />
                <p className="text-xs text-blue-900 font-medium">
                  Correlating database connection behavior with <code className="font-mono bg-blue-100 px-1 py-0.5 rounded text-blue-900">max_connections</code> env var change..
                </p>
              </div>
            </div>
          </div>

          {/* AI Repair Proposal Box */}
          <div className="bg-white rounded-xl border-2 border-slate-900 shadow-md p-5 relative overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900">Repair Proposal</h3>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold uppercase tracking-wide">
                Risk Level: Low
              </span>
            </div>

            <div className="mt-3">
              <h4 className="text-xs font-semibold text-slate-900">
                Patch database connection cleanup
              </h4>
              <p className="text-[11px] text-slate-600 mt-1 leading-relaxed">
                <strong>Why:</strong> Deploy v42 increased pool size without updating connection timeout limits, causing Postgres connection exhaustion.
              </p>
              <p className="text-[11px] text-slate-600 mt-1 leading-relaxed">
                <strong>Expected Result:</strong> Immediate recovery of checkout flow; DB connections stabilize at ~80% capacity.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="mt-5 space-y-2 pt-3 border-t border-slate-100">
              <button
                onClick={handleApproveRepair}
                disabled={isApplyingFix || fixApplied}
                className={`w-full py-2.5 rounded-lg text-xs font-bold text-white shadow-sm flex items-center justify-center gap-2 transition-all ${
                  fixApplied
                    ? 'bg-emerald-600 hover:bg-emerald-700'
                    : 'bg-slate-900 hover:bg-slate-800'
                }`}
              >
                {isApplyingFix ? (
                  <>
                    <Bot className="w-4 h-4 animate-spin text-blue-400" />
                    <span>Applying Patch via CI/CD...</span>
                  </>
                ) : fixApplied ? (
                  <>
                    <Check className="w-4 h-4" />
                    <span>Repair Patch Executed!</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 text-blue-400" />
                    <span>Approve Repair</span>
                  </>
                )}
              </button>

              <div className="grid grid-cols-2 gap-2">
                <button 
                  disabled={fixApplied}
                  className="py-1.5 rounded-lg text-xs font-medium border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
                >
                  Modify Plan
                </button>
                <button 
                  disabled={fixApplied}
                  className="py-1.5 rounded-lg text-xs font-medium border border-red-200 text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50"
                >
                  Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
