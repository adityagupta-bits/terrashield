import React from 'react';
import { useTranslation } from 'react-i18next';
import { Phone, ShieldAlert, Flame, Ambulance, LifeBuoy } from 'lucide-react';

export const EmergencyStrip: React.FC = () => {
  const { t } = useTranslation();

  const helplines = [
    { label: '112', title: t('helpline.national'), tel: '112', icon: LifeBuoy, color: 'text-amber-400' },
    { label: 'NDRF', title: t('helpline.ndrf'), tel: '+911124363260', icon: ShieldAlert, color: 'text-rose-400' },
    { label: 'SDRF 1070', title: t('helpline.sdrf'), tel: '1070', icon: ShieldAlert, color: 'text-orange-400' },
    { label: '101 Fire', title: t('helpline.fire'), tel: '101', icon: Flame, color: 'text-red-400' },
    { label: '108 Ambulance', title: t('helpline.ambulance'), tel: '108', icon: Ambulance, color: 'text-emerald-400' }
  ];

  return (
    <div className="bg-slate-950 border-t border-slate-800 px-3 py-2 flex items-center justify-between overflow-x-auto gap-2 shrink-0 z-20">
      <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider shrink-0 mr-2">
        <Phone size={13} className="text-rose-500 animate-pulse" />
        <span>Emergency Dispatch:</span>
      </div>

      <div className="flex items-center gap-2 sm:gap-4 overflow-x-auto">
        {helplines.map((item) => {
          const Icon = item.icon;
          return (
            <a
              key={item.label}
              href={`tel:${item.tel}`}
              className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 transition shrink-0 group min-h-[40px]"
              title={`Call ${item.title}`}
            >
              <Icon size={14} className={item.color} />
              <div className="text-left">
                <span className="text-xs font-bold text-white group-hover:text-blue-400 transition">
                  {item.label}
                </span>
                <span className="text-[10px] text-slate-500 hidden lg:inline ml-1.5">
                  ({item.title})
                </span>
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
};
