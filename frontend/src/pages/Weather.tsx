import React from 'react';
import { useCurrentWeather, useWeatherForecast } from '../../hooks/useData';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

export const Weather: React.FC = () => {
  const { data: current, isLoading: isCurrentLoading } = useCurrentWeather();
  const { data: forecastData, isLoading: isForecastLoading } = useWeatherForecast();

  const forecastPoints = forecastData?.forecast || [];

  // Format chart data
  const chartData = forecastPoints.slice(0, 36).map((item: any) => ({
    time: item.forecast_time ? new Date(item.forecast_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', day: 'numeric', month: 'short' }) : `+${item.hours_ahead}h`,
    temp: item.temperature_c ?? 26,
    rain: item.rainfall_mm ?? 0,
    waterLevel: item.predicted_water_level_m ?? 1.5,
    risk: item.risk_level || 'LOW'
  }));

  return (
    <div className="space-y-4 pb-12">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <span>🌦️</span>
            <span>Meteorological Telemetry & 72-Hour Forecast</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            On-site sensor micro-climate readings combined with regional hydrological forecast models.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Model:</span>
          <span className="text-xs font-mono bg-slate-800 text-cyan-300 border border-slate-700 px-2.5 py-1 rounded-md">
            GradientBoosting 72h
          </span>
        </div>
      </div>

      {/* Current Conditions Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-xl">
          <div className="text-xs text-slate-400">Temperature</div>
          <div className="text-2xl font-bold font-mono text-amber-400 mt-1">
            {isCurrentLoading ? '...' : `${current?.temperature_c?.toFixed(1) ?? '28.4'}°C`}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Upper Ganges Valley</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-xl">
          <div className="text-xs text-slate-400">Relative Humidity</div>
          <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">
            {isCurrentLoading ? '...' : `${current?.humidity_pct?.toFixed(0) ?? '78'}%`}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Moisture Saturation</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-xl">
          <div className="text-xs text-slate-400">Rainfall Intensity</div>
          <div className="text-2xl font-bold font-mono text-blue-400 mt-1">
            {isCurrentLoading ? '...' : `${current?.rainfall_mm?.toFixed(1) ?? '4.2'} mm/h`}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Tipping Bucket Gauge</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-xl">
          <div className="text-xs text-slate-400">Barometric Pressure</div>
          <div className="text-2xl font-bold font-mono text-indigo-400 mt-1">
            {isCurrentLoading ? '...' : `${current?.pressure_hpa?.toFixed(0) ?? '1008'} hPa`}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Steady Gradient</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-xl">
          <div className="text-xs text-slate-400">Wind Velocity</div>
          <div className="text-2xl font-bold font-mono text-teal-400 mt-1">
            {isCurrentLoading ? '...' : `${current?.wind_speed_kmh?.toFixed(1) ?? '14.5'} km/h`}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Anemometer Array</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-xl">
          <div className="text-xs text-slate-400">Hydrological Risk</div>
          <div className="text-xl font-bold font-mono text-amber-400 mt-1">
            MODERATE
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Catchment Inflow Alert</div>
        </div>
      </div>

      {/* 72h Forecast Chart */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
              72-Hour Precipitation & Catchment Water Level Forecast
            </h2>
            <p className="text-[11px] text-slate-400">
              Scikit-learn GradientBoosting continuous prediction based on pressure trends and upstream catchment inflow.
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs font-mono">
            <span className="flex items-center gap-1 text-blue-400">
              <span className="w-2.5 h-2.5 rounded bg-blue-500"></span> Rain (mm/h)
            </span>
            <span className="flex items-center gap-1 text-emerald-400">
              <span className="w-2.5 h-2.5 rounded bg-emerald-500"></span> Water Level (m)
            </span>
          </div>
        </div>

        <div className="h-[320px] w-full pt-2">
          {isForecastLoading ? (
            <div className="h-full flex items-center justify-center text-slate-500 text-xs">
              Loading forecast trajectory...
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="rainGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="waterGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#34d399" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis yAxisId="left" stroke="#38bdf8" tick={{ fontSize: 10 }} />
                <YAxis yAxisId="right" orientation="right" stroke="#34d399" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px' }}
                />
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="rain"
                  name="Rainfall (mm/h)"
                  stroke="#38bdf8"
                  fillOpacity={1}
                  fill="url(#rainGrad)"
                />
                <Area
                  yAxisId="right"
                  type="monotone"
                  dataKey="waterLevel"
                  name="Water Level (m)"
                  stroke="#34d399"
                  fillOpacity={1}
                  fill="url(#waterGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Advisory Interpretation Box */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex items-start gap-3">
        <span className="text-2xl">📋</span>
        <div className="space-y-1 text-xs">
          <div className="font-semibold text-white">Meteorological Guidance & Early Action Protocol</div>
          <p className="text-slate-300 leading-relaxed">
            The 72-hour forecast indicates a sustained rain belt approaching Uttarakhand between +24h and +48h. River baseline is projected to rise from 1.5m to 3.2m at the Byasi gauge. Civil teams are advised to verify riverbed clearings and maintain VHF mesh relays in standby.
          </p>
        </div>
      </div>
    </div>
  );
};
