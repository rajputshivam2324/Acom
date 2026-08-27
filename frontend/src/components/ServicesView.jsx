import React from 'react';
import { Server, CheckCircle2, AlertTriangle, ShieldCheck, Activity, Cpu, HardDrive } from 'lucide-react';

export default function ServicesView({ servicesList, onSelectService }) {
  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Services & Infrastructure</h1>
          <p className="text-xs text-slate-500 mt-1">Active microservices health telemetry and node metrics.</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-700 text-xs font-semibold border border-emerald-200">
            18 / 19 Healthy
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {servicesList.map((service) => (
          <div 
            key={service.id} 
            className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition-all cursor-pointer"
            onClick={() => onSelectService && onSelectService(service.name)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${
                  service.status === 'Critical'
                    ? 'bg-red-50 text-red-600 border border-red-200'
                    : 'bg-slate-100 text-slate-700'
                }`}>
                  <Server className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-mono text-sm font-bold text-slate-900">{service.name}</h3>
                  <span className="text-[10px] text-slate-400 font-mono">cluster-us-east</span>
                </div>
              </div>

              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                service.status === 'Critical' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'
              }`}>
                {service.status}
              </span>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-[10px] text-slate-400 block">p99 Latency</span>
                <span className="font-mono font-medium text-slate-800">{service.latency}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 block">Uptime</span>
                <span className="font-mono font-medium text-slate-800">99.98%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
