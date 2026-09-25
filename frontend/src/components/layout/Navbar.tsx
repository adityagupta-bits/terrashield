import React from 'react';
import { useTranslation } from 'react-i18next';
import { Shield, Radio, Wifi, WifiOff, Globe, Power, UserCheck, ExternalLink } from 'lucide-react';
import { useUIStore } from '../../store/uiStore';
import { useAuthStore } from '../../store/authStore';
import { ConnectionStatus } from '../../hooks/useWebSocket';

interface NavbarProps {
  wsStatus: ConnectionStatus;
  onOpenCitizenPortal?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ wsStatus }) => {
  const { t, i18n } = useTranslation();
  const { language, setLanguage, demoMode, setDemoMode } = useUIStore();
  const { isAuthenticated, role, logout } = useAuthStore();

  const toggleLanguage = () => {
    const nextLang = language === 'en' ? 'hi' : 'en';
    setLanguage(nextLang);
    i18n.changeLanguage(nextLang);
  };

  const getStatusBadge = () => {
    switch (wsStatus) {
      case 'LIVE':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            {t('status.live')}
          </span>
        );
      case 'RECONNECTING':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-400 border border-amber-800">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
            {t('status.reconnecting')}
          </span>
        );
      case 'MESH-OFFLINE':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <WifiOff size={12} />
            {t('status.meshOffline')}
          </span>
        );
    }
  };

  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 px-4 flex items-center justify-between z-30 sticky top-0">
      {/* Brand & Project Info */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-600/20">
          <Shield size={22} />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold tracking-tight text-white">TERRA SHIELD</h1>
            <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-blue-950 text-blue-400 border border-blue-800">
              SIH26178
            </span>
          </div>
          <p className="text-xs text-slate-400 hidden sm:block">
            Resilient Environmental Hazard Monitoring & Early Warning
          </p>
        </div>
      </div>

      {/* Center status */}
      <div className="flex items-center gap-3">
        {getStatusBadge()}
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2.5">
        {/* Language Toggle */}
        <button
          onClick={toggleLanguage}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          title="Switch Language"
        >
          <Globe size={14} />
          <span>{language === 'en' ? 'हिन्दी' : 'English'}</span>
        </button>

        {/* Demo Mode Toggle */}
        <button
          onClick={() => setDemoMode(!demoMode)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition ${
            demoMode
              ? 'bg-amber-500/20 text-amber-300 border-amber-500/50'
              : 'bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700'
          }`}
        >
          <Radio size={14} className={demoMode ? 'text-amber-400 animate-pulse' : ''} />
          <span>{t('nav.demoMode')}</span>
        </button>

        {/* Citizen Portal Link */}
        <a
          href="/citizen"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-sm"
        >
          <ExternalLink size={13} />
          <span className="hidden md:inline">{t('nav.citizenPortal')}</span>
        </a>

        {/* User Status / Logout */}
        {isAuthenticated && (
          <button
            onClick={logout}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-rose-950/60 hover:text-rose-400 text-slate-300 border border-slate-700 transition"
            title="Log Out"
          >
            <Power size={13} />
          </button>
        )}
      </div>
    </header>
  );
};
