import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import HeaderBar from './components/HeaderBar';
import CommandCenter from './components/CommandCenter';
import IncidentInvestigation from './components/IncidentInvestigation';
import IntegrationsConfig from './components/IntegrationsConfig';
import IncidentsList from './components/IncidentsList';
import ServicesView from './components/ServicesView';
import CommandPaletteModal from './components/CommandPaletteModal';
import NotificationToast from './components/NotificationToast';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [environment, setEnvironment] = useState('Production');
  const [aiProvider, setAiProvider] = useState('GPT-4');
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [activeIncident, setActiveIncident] = useState(true);
  const [toast, setToast] = useState(null);

  const [servicesList, setServicesList] = useState([
    { id: 1, name: 'payment-api', status: 'Critical', latency: '928ms' },
    { id: 2, name: 'auth-service', status: 'Healthy', latency: '24ms' },
    { id: 3, name: 'user-db-cluster', status: 'Healthy', latency: '12ms' },
    { id: 4, name: 'frontend-gateway', status: 'Healthy', latency: '18ms' }
  ]);

  const showToast = (message) => {
    setToast({ message, id: Date.now() });
    setTimeout(() => setToast(null), 4000);
  };

  const handleResolveIncident = () => {
    setActiveIncident(false);
    setServicesList((prev) =>
      prev.map((s) => (s.name === 'payment-api' ? { ...s, status: 'Healthy', latency: '32ms' } : s))
    );
    showToast('INC-4821 Payment API Outage has been successfully resolved!');
  };

  return (
    <div className="flex h-screen w-full bg-[#f8f8f6] font-sans antialiased overflow-hidden">
      {/* Left Sidebar */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        activeIncidentCount={activeIncident ? 1 : 0} 
      />

      {/* Right Main Panel */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header Bar */}
        <HeaderBar 
          onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
          environment={environment}
          setEnvironment={setEnvironment}
          aiProvider={aiProvider}
          setAiProvider={setAiProvider}
          unreadNotifications={activeIncident ? 1 : 0}
          onNotificationClick={() => showToast(activeIncident ? 'Alert: SEV-1 INC-4821 requires attention!' : 'No new notifications')}
        />

        {/* Dynamic Content View Area */}
        <main className="flex-1 overflow-y-auto bg-[#f8f8f6]">
          {activeTab === 'overview' && (
            <CommandCenter 
              onJoinWarRoom={() => setActiveTab('investigations')}
              activeIncident={activeIncident}
              servicesList={servicesList}
            />
          )}

          {activeTab === 'investigations' && (
            <IncidentInvestigation 
              onBack={() => setActiveTab('overview')}
              onResolveIncident={handleResolveIncident}
            />
          )}

          {activeTab === 'incidents' && (
            <IncidentsList 
              onSelectIncident={(id) => {
                if (id === 'INC-4821') {
                  setActiveTab('investigations');
                } else {
                  showToast(`Viewing details for ${id}`);
                }
              }}
              activeIncident={activeIncident}
              onResolveIncident={handleResolveIncident}
            />
          )}

          {activeTab === 'integrations' && (
            <IntegrationsConfig 
              onSaveNotification={showToast}
            />
          )}

          {activeTab === 'services' && (
            <ServicesView 
              servicesList={servicesList}
              onSelectService={(name) => showToast(`Selected service: ${name}`)}
            />
          )}

          {(activeTab === 'actions' || activeTab === 'reports' || activeTab === 'settings') && (
            <div className="p-12 text-center text-slate-500 animate-in fade-in duration-300">
              <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3 text-slate-400">
                ⚡
              </div>
              <h2 className="text-lg font-bold text-slate-800 capitalize">{activeTab} Panel</h2>
              <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                AI Incident Commander active node. Configure automated triggers, SRE reports, and workspace permissions.
              </p>
              <button 
                onClick={() => setActiveTab('overview')}
                className="mt-4 px-4 py-2 rounded-lg text-xs font-semibold bg-slate-900 text-white hover:bg-slate-800"
              >
                Return to Overview
              </button>
            </div>
          )}
        </main>
      </div>

      {/* Command Palette Modal */}
      <CommandPaletteModal 
        isOpen={isCommandPaletteOpen}
        onClose={setIsCommandPaletteOpen}
        onNavigate={(tab) => setActiveTab(tab)}
      />

      {/* Toast Feed */}
      <NotificationToast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}
