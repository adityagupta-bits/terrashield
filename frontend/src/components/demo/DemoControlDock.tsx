import React, { useState } from 'react';
import { useUIStore } from '../../store/uiStore';
import { api } from '../../api/client';
import { useQueryClient } from '@tanstack/react-query';

export const DemoControlDock: React.FC = () => {
  const { selectedNodeId, demoMode, setDemoMode } = useUIStore();
  const queryClient = useQueryClient();
  const [isBlackoutActive, setIsBlackoutActive] = useState(false);
  const [isNetworkCut, setIsNetworkCut] = useState(false);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 4000);
  };

  const handleBlackoutToggle = async () => {
    const nextState = !isBlackoutActive;
    setLoadingAction('blackout');
    try {
      await api.toggleBlackout(nextState);
      setIsBlackoutActive(nextState);
      queryClient.invalidateQueries({ queryKey: ['mesh-topology'] });
      queryClient.invalidateQueries({ queryKey: ['nodes'] });
      showToast(nextState ? '⚠️ Blackout enabled: NODE-08 rerouted via LoRa mesh' : '✅ Blackout disabled: Standard routing restored');
    } catch (err: any) {
      showToast(`Failed blackout: ${err.message}`);
    } finally {
      setLoadingAction(null);
    }
  };

  const handleTrigger = async (type: string, label: string) => {
    setLoadingAction(type);
    try {
      await api.triggerDemo(selectedNodeId, type);
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['node', selectedNodeId] });
      queryClient.invalidateQueries({ queryKey: ['node-readings', selectedNodeId] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      showToast(`🚨 Triggered ${label} on ${selectedNodeId}`);
    } catch (err: any) {
      showToast(`Trigger failed: ${err.message}`);
    } finally {
      setLoadingAction(null);
    }
  };

  const handleNetworkControl = async (action: 'cut' | 'restore') => {
    setLoadingAction(`net-${action}`);
    try {
      await api.controlDemoNetwork(selectedNodeId, action);
      setIsNetworkCut(action === 'cut');
      queryClient.invalidateQueries({ queryKey: ['nodes'] });
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      showToast(
        action === 'cut'
          ? `📵 Field comms CUT on ${selectedNodeId} (Buffering to LittleFS)`
          : `📶 Field comms RESTORED on ${selectedNodeId} (Batch flushed, check Delayed Alerts)`
      );
    } catch (err: any) {
      showToast(`Network control failed: ${err.message}`);
    } finally {
      setLoadingAction(null);
    }
  };

  if (!demoMode) {
    return (
      <div className="fixed bottom-4 right-4 z-40">
        <button
          onClick={() => setDemoMode(true)}
          className="bg-slate-800 hover:bg-slate-700 text-amber-400 border border-amber-500/40 text-xs px-3 py-1.5 rounded-md shadow-lg flex items-center gap-1.5 backdrop-blur-md transition-all font-mono"
        >
          <span>⚡</span>
          <span>Show Demo Controls</span>
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-40 w-[95%] max-w-4xl bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-xl shadow-2xl p-3 text-white transition-all">
      {toastMsg && (
        <div className="absolute -top-12 left-1/2 -translate-x-1/2 bg-slate-800 text-amber-300 border border-amber-500/40 px-4 py-1.5 rounded-lg text-xs font-mono shadow-xl whitespace-nowrap animate-bounce">
          {toastMsg}
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Left: Selected Node & Mode */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-slate-800/80 px-2.5 py-1 rounded border border-slate-700">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-400">Target Node:</span>
            <span className="font-bold text-cyan-300 font-mono">{selectedNodeId}</span>
          </div>
          <button
            onClick={() => setDemoMode(false)}
            className="text-slate-500 hover:text-slate-300 text-xs px-1"
            title="Minimize Dock"
          >
            ✕
          </button>
        </div>

        {/* Center: Hazard Injectors */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-slate-400 uppercase tracking-wider text-[10px] font-semibold">Simulate Hazard:</span>
          
          <button
            disabled={loadingAction !== null}
            onClick={() => handleTrigger('flood', 'Flash Flood')}
            className="bg-blue-600/80 hover:bg-blue-600 active:bg-blue-700 disabled:opacity-50 text-white font-medium px-2.5 py-1 rounded border border-blue-400/40 transition-colors flex items-center gap-1"
          >
            <span>🌊</span>
            <span>Flash Flood</span>
          </button>

          <button
            disabled={loadingAction !== null}
            onClick={() => handleTrigger('wildfire', 'Wildfire')}
            className="bg-amber-600/80 hover:bg-amber-600 active:bg-amber-700 disabled:opacity-50 text-white font-medium px-2.5 py-1 rounded border border-amber-400/40 transition-colors flex items-center gap-1"
          >
            <span>🔥</span>
            <span>Wildfire</span>
          </button>

          <button
            disabled={loadingAction !== null}
            onClick={() => handleTrigger('smoke', 'Dense Smoke')}
            className="bg-purple-600/80 hover:bg-purple-600 active:bg-purple-700 disabled:opacity-50 text-white font-medium px-2.5 py-1 rounded border border-purple-400/40 transition-colors flex items-center gap-1"
          >
            <span>💨</span>
            <span>Smoke</span>
          </button>

          <button
            disabled={loadingAction !== null}
            onClick={() => handleTrigger('normal', 'Normal Reset')}
            className="bg-slate-700/80 hover:bg-slate-600 active:bg-slate-700 disabled:opacity-50 text-slate-300 font-medium px-2.5 py-1 rounded border border-slate-600 transition-colors flex items-center gap-1"
          >
            <span>🔄</span>
            <span>Reset</span>
          </button>
        </div>

        {/* Right: Resiliency and Outage Controls */}
        <div className="flex items-center gap-2 border-l border-slate-800 pl-3">
          <button
            disabled={loadingAction !== null}
            onClick={handleBlackoutToggle}
            className={`font-mono text-xs px-2.5 py-1 rounded border transition-colors flex items-center gap-1.5 ${
              isBlackoutActive
                ? 'bg-rose-900/70 border-rose-500 text-rose-200'
                : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-300'
            }`}
            title="Simulate cellular blackout: NODE-08 routes via LoRa mesh"
          >
            <span>⚡</span>
            <span>{isBlackoutActive ? 'Blackout ON' : 'Blackout'}</span>
          </button>

          <button
            disabled={loadingAction !== null}
            onClick={() => handleNetworkControl(isNetworkCut ? 'restore' : 'cut')}
            className={`font-mono text-xs px-2.5 py-1 rounded border transition-colors flex items-center gap-1.5 ${
              isNetworkCut
                ? 'bg-emerald-900/70 border-emerald-500 text-emerald-200 animate-pulse'
                : 'bg-rose-900/40 hover:bg-rose-900/60 border-rose-700/60 text-rose-300'
            }`}
            title="Simulate field network severance and store-and-forward batch recovery"
          >
            <span>{isNetworkCut ? '📶' : '📵'}</span>
            <span>{isNetworkCut ? 'Restore Comms' : 'Cut Comms'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
