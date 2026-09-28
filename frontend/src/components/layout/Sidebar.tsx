import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  AlertTriangle,
  Radio,
  PhoneCall,
  CloudSun,
  Newspaper,
  Network,
  MessageSquare
} from 'lucide-react';
import { useAlerts } from '../../hooks/useData';

export const Sidebar: React.FC = () => {
  const { t } = useTranslation();
  const { data: alerts = [] } = useAlerts({ status: 'open' });
  const openAlertsCount = alerts.length;

  const navItems = [
    { to: '/', label: t('nav.dashboard'), icon: LayoutDashboard },
    { to: '/alerts', label: t('nav.alerts'), icon: AlertTriangle, badge: openAlertsCount > 0 ? openAlertsCount : null },
    { to: '/broadcast', label: t('nav.broadcast'), icon: Radio },
    { to: '/contacts', label: t('nav.contacts'), icon: PhoneCall },
    { to: '/weather', label: t('nav.weather'), icon: CloudSun },
    { to: '/news', label: t('nav.news'), icon: Newspaper },
    { to: '/mesh', label: t('nav.mesh'), icon: Network },
    { to: '/whatsapp', label: t('nav.whatsapp'), icon: MessageSquare }
  ];

  return (
    <aside className="w-16 md:w-56 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0">
      <nav className="p-2 space-y-1.5 mt-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-3 rounded-lg text-xs md:text-sm font-medium transition min-h-[48px] ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/80'
                }`
              }
            >
              <Icon size={18} className="shrink-0" />
              <span className="hidden md:inline truncate">{item.label}</span>
              {item.badge !== null && (
                <span className="hidden md:flex ml-auto bg-rose-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Deployment Sector Tag */}
      <div className="p-3 border-t border-slate-800/80 hidden md:block">
        <div className="bg-slate-950/80 p-2.5 rounded-lg border border-slate-800">
          <p className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Deployment Basin</p>
          <p className="text-xs font-bold text-slate-200 mt-0.5 truncate">Assam (16 June Incident)</p>
          <p className="text-[10px] text-emerald-400 flex items-center gap-1 mt-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            Brahmaputra - Kopili Basin
          </p>
        </div>
      </div>
    </aside>
  );
};
