import React, { useState } from 'react';
import { useNews } from '../../hooks/useData';

export const News: React.FC = () => {
  const { data: newsItems, isLoading } = useNews();
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const categories = [
    { id: 'ALL', label: 'All Bulletins' },
    { id: 'NDMA', label: 'NDMA Directives' },
    { id: 'IMD', label: 'IMD Weather Warnings' },
    { id: 'RIVER', label: 'River & Dam Inundation' },
    { id: 'FIELD_RELIEF', label: 'Field Operations' }
  ];

  const filteredNews = (newsItems || []).filter(item => {
    if (selectedCategory === 'ALL') return true;
    return item.category?.toUpperCase().includes(selectedCategory);
  });

  return (
    <div className="space-y-4 pb-12">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <span>📰</span>
            <span>Regional Incident Bulletins & Advisory Feed</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Verified updates from State Disaster Management Authority, IMD Dehradun, and Central Water Commission.
          </p>
        </div>

        <div className="text-xs font-mono text-cyan-400 bg-cyan-950/80 border border-cyan-800 px-3 py-1.5 rounded-lg">
          Live Wire Active
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex flex-wrap gap-2">
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              selectedCategory === cat.id
                ? 'bg-cyan-600 text-white border-cyan-500'
                : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800 hover:text-slate-200'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* News Cards Grid */}
      {isLoading ? (
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl text-center text-slate-400 text-xs">
          Fetching official bulletins...
        </div>
      ) : filteredNews.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl text-center text-slate-500 text-xs">
          No news bulletins found in this category.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {filteredNews.map(item => (
            <div
              key={item.id}
              className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-xl p-4 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[10px] font-mono uppercase bg-slate-800 text-cyan-300 border border-slate-700 px-2 py-0.5 rounded">
                    {item.source || 'SDMA'}
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono">
                    {new Date(item.published_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                <h3 className="text-sm font-semibold text-white mt-2 leading-snug">
                  {item.title}
                </h3>

                <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                  {item.summary || item.content}
                </p>
              </div>

              <div className="mt-4 pt-2 border-t border-slate-800 flex items-center justify-between text-[11px]">
                <span className="text-slate-400 font-mono">Verified Bulletin</span>
                <span className="text-cyan-400 flex items-center gap-1">
                  Official Record ✓
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
