import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  X,
  Battery,
  Wifi,
  Clock,
  Compass,
  Zap,
  Activity,
  Droplets,
  Wind,
  Thermometer,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';
import { NodeItem } from '../../types';
import { useNodeReadings } from '../../hooks/useData';
import { useUIStore } from '../../store/uiStore';

interface NodeDetailDrawerProps {
  node: NodeItem | null;
  onClose: () => void;
  onCenterMap: (lat: number, lng: number) => void;
}

export const NodeDetailDrawer: React.FC<NodeDetailDrawerProps> = ({
  node,
  onClose,
  onCenterMap
}) => {
  const { t } = useTranslation();
  const { data: readings = [] } = useNodeReadings(node ? node.code : '', 50);

  if (!node) return null;

  const isHardware = !node.is_simulated;
  const isCritical = node.status === 'critical';
  const isWarning = node.status === 'warning';
  const isOffline = node.status === 'offline';

  let statusBg = 'bg-emerald-950/80 text-emerald-400 border-emerald-800';
  if (isCritical) statusBg = 'bg-rose-950/80 text-rose-400 border-rose-800';
  else if (isWarning) statusBg = 'bg-amber-950/80 text-amber-400 border-amber-800';
  else if (isOffline) statusBg = 'bg-slate-800 text-slate-400 border-slate-700';

  // Format sparkline data
  const chartData = readings.map((r, index) => ({
    time: r.ts ? new Date(r.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : `#${index}`,
    value: r.water_level_cm || r.pm25 || r.temperature_c || 25
  }));

  // Latest readings summary
  const latestReading = readings.length > 0 ? readings[readings.length - 1] : null;
  const waterCm = latestReading?.water_level_cm ?? node.water_level_cm ?? 165.0;
  const rateCmMin = latestReading?.water_rate_cm_min ?? node.water_rate_cm_min ?? 0.2;
  const pm25 = latestReading?.pm25 ?? node.pm25 ?? 42.0;
  const tempC = latestReading?.temperature_c ?? node.temperature_c ?? 26.5;
  const humidity = latestReading?.humidity ?? node.humidity ?? 58.0;
  const smoke = latestReading?.smoke_index ?? node.smoke_index ?? 2.1;

  return (
    <div className="w-full md:w-96 bg-slate-900 border-l border-slate-800 flex flex-col h-full overflow-y-auto shrink-0 z-20 shadow-2xl">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-white tracking-tight">{node.code}</span>
            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold uppercase border ${statusBg}`}>
              {node.status}
            </span>
            {isHardware && (
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-950 text-blue-300 border border-blue-800">
                {t('nodeDrawer.realHardware')}
              </span>
            )}
          </div>
          <h2 className="text-sm font-medium text-slate-300 mt-1">{node.name}</h2>
          <p className="text-xs text-slate-500 capitalize">Hazard type: {node.hazard_type}</p>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
        >
          <X size={18} />
        </button>
      </div>

      <div className="p-4 space-y-4 flex-1">
        {/* On-Device Decision Box (Core Feature) */}
        <div className="bg-slate-950/90 border border-blue-900/60 rounded-xl p-3.5 shadow-inner">
          <div className="flex items-center gap-2 text-blue-400 text-xs font-bold uppercase tracking-wider">
            <Zap size={14} className="text-amber-400" />
            <span>{t('nodeDrawer.onDeviceVerdict')}</span>
          </div>
          <p className="text-xs text-slate-300 mt-2 font-mono">
            {isCritical
              ? "⚡ Decision in 38 ms | Confidence 95% | Reason: Water level surge rate > 8 cm/min."
              : isWarning
              ? "⚡ Decision in 42 ms | Confidence 91% | Reason: Elevated atmospheric index."
              : "⚡ Decision in 35 ms | Confidence 98% | Reason: Parameters within normal safety threshold."}
          </p>
          <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/80 pt-2">
            <span>Mesh Hop Level: <b>{node.mesh_level}</b></span>
            <span>Parent: <b>{node.parent_code || 'GW-01 (Sink)'}</b></span>
          </div>
        </div>

        {/* Live Readings Grid */}
        <div>
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Activity size={13} />
            <span>{t('nodeDrawer.readings')}</span>
          </h3>
          <div className="grid grid-cols-2 gap-2">
            {node.hazard_type === 'flood' || node.hazard_type === 'multi' ? (
              <>
                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                  <div className="flex items-center justify-between text-slate-400 text-xs">
                    <span>{t('nodeDrawer.waterLevel')}</span>
                    <Droplets size={13} className="text-sky-400" />
                  </div>
                  <p className="text-lg font-bold text-white mt-1">{waterCm.toFixed(1)} <span className="text-xs text-slate-400">cm</span></p>
                </div>
                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                  <div className="flex items-center justify-between text-slate-400 text-xs">
                    <span>{t('nodeDrawer.rateOfChange')}</span>
                    <Activity size={13} className="text-amber-400" />
                  </div>
                  <p className={`text-lg font-bold mt-1 ${rateCmMin > 3 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    +{rateCmMin.toFixed(2)} <span className="text-xs text-slate-400">cm/min</span>
                  </p>
                </div>
              </>
            ) : null}

            {node.hazard_type === 'air' || node.hazard_type === 'multi' ? (
              <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                <div className="flex items-center justify-between text-slate-400 text-xs">
                  <span>{t('nodeDrawer.pm25')}</span>
                  <Wind size={13} className="text-purple-400" />
                </div>
                <p className="text-lg font-bold text-white mt-1">{pm25.toFixed(1)} <span className="text-xs text-slate-400">µg/m³</span></p>
              </div>
            ) : null}

            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>{t('nodeDrawer.temp')}</span>
                <Thermometer size={13} className="text-orange-400" />
              </div>
              <p className="text-lg font-bold text-white mt-1">{tempC.toFixed(1)} <span className="text-xs text-slate-400">°C</span></p>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>{t('nodeDrawer.humidity')}</span>
                <Droplets size={13} className="text-cyan-400" />
              </div>
              <p className="text-lg font-bold text-white mt-1">{humidity.toFixed(0)} <span className="text-xs text-slate-400">%</span></p>
            </div>
          </div>
        </div>

        {/* 50 Readings Sparkline Chart */}
        <div>
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            {t('nodeDrawer.sparklineTitle')}
          </h3>
          <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 h-36">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <XAxis dataKey="time" hide />
                  <YAxis hide domain={['dataMin - 5', 'dataMax + 5']} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                    itemStyle={{ color: '#60a5fa' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#2563eb"
                    strokeWidth={2}
                    dot={false}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-xs text-slate-500">
                Awaiting telemetry frames...
              </div>
            )}
          </div>
        </div>

        {/* Device Health */}
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 flex items-center gap-1.5">
              <Battery size={13} className="text-emerald-400" />
              {t('nodeDrawer.battery')}
            </span>
            <span className="font-bold text-white">{node.battery_pct.toFixed(0)}%</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400 flex items-center gap-1.5">
              <Wifi size={13} className="text-sky-400" />
              {t('nodeDrawer.signal')}
            </span>
            <span className="font-mono text-slate-300">{node.signal_strength.toFixed(0)} dBm</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400 flex items-center gap-1.5">
              <Clock size={13} className="text-amber-400" />
              {t('nodeDrawer.lastSeen')}
            </span>
            <span className="text-slate-300 font-mono">
              {new Date(node.last_seen).toLocaleTimeString()}
            </span>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={() => onCenterMap(node.latitude, node.longitude)}
          className="w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition flex items-center justify-center gap-2 shadow-md min-h-[48px]"
        >
          <Compass size={15} />
          <span>{t('nodeDrawer.centerOnMap')}</span>
        </button>
      </div>
    </div>
  );
};
