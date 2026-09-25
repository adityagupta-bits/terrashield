import React from 'react';
import { Newspaper } from 'lucide-react';
import { useNews } from '../../hooks/useData';

export const NewsTicker: React.FC = () => {
  const { data: news = [] } = useNews();
  const latestItem = news.length > 0 ? news[0] : null;

  if (!latestItem) return null;

  return (
    <div className="bg-slate-900/90 border-b border-slate-800/80 px-4 py-1.5 flex items-center gap-3 text-xs overflow-hidden">
      <div className="flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-rose-950 text-rose-300 border border-rose-800 shrink-0">
        <Newspaper size={11} />
        <span>NDMA Bulletin</span>
      </div>
      <div className="truncate text-slate-300 font-medium flex items-center gap-2">
        <span className="text-amber-400 font-semibold">[{latestItem.region}]</span>
        <span className="truncate">{latestItem.title}</span>
        <span className="text-slate-500 text-[11px] hidden sm:inline">— {latestItem.source}</span>
      </div>
    </div>
  );
};
