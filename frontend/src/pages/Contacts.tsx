import React, { useState } from 'react';
import { useContacts } from '../../hooks/useData';
import { useUIStore } from '../../store/uiStore';

const TOLL_FREE_NUMBERS = [
  { label: 'National Emergency', number: '112', desc: 'Unified Police / Fire / Medical' },
  { label: 'State Disaster Helpline', number: '1070', desc: 'ASDMA State Operations (Assam)' },
  { label: 'District Disaster Control', number: '1077', desc: 'Kamrup Metro / Nagaon Desk' },
  { label: 'Emergency Ambulance', number: '108', desc: 'Free ALS / BLS Ambulance Dispatch' }
];

export const Contacts: React.FC = () => {
  const { mapCenter } = useUIStore();
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [sortByNearest, setSortByNearest] = useState<boolean>(false);

  const nearParam = sortByNearest ? `${mapCenter[0]},${mapCenter[1]}` : undefined;
  const categoryParam = selectedCategory === 'ALL' ? undefined : selectedCategory;

  const { data: contacts, isLoading } = useContacts(nearParam, categoryParam);

  const categories = [
    { id: 'ALL', label: 'All Contacts' },
    { id: 'AUTHORITY', label: 'District Administration' },
    { id: 'RESCUE', label: 'NDRF / SDRF' },
    { id: 'SHELTER', label: 'Safe Shelters' },
    { id: 'MEDICAL', label: 'Hospitals & Medical' }
  ];

  return (
    <div className="space-y-4 pb-12">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <span>📞</span>
            <span>Emergency Directory & Safe Shelters</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            PostGIS KNN nearest distance calculation and verified contact numbers for NDRF, SDRF, and civil shelters.
          </p>
        </div>

        {/* Spatial Sort Toggle */}
        <button
          onClick={() => setSortByNearest(!sortByNearest)}
          className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium border transition-colors flex items-center gap-1.5 ${
            sortByNearest
              ? 'bg-cyan-950 text-cyan-300 border-cyan-500'
              : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
          }`}
        >
          <span>📍</span>
          <span>{sortByNearest ? 'Sorted by Proximity (KNN)' : 'Sort by Proximity'}</span>
        </button>
      </div>

      {/* Toll-Free Quick Dial Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
        {TOLL_FREE_NUMBERS.map((tf, idx) => (
          <a
            key={idx}
            href={`tel:${tf.number}`}
            className="bg-slate-900 border border-slate-800 hover:border-slate-700 p-3 rounded-xl flex items-center justify-between transition-all group"
          >
            <div>
              <div className="text-[11px] text-slate-400">{tf.label}</div>
              <div className="text-xl font-bold font-mono text-cyan-400 group-hover:text-cyan-300 mt-0.5">
                {tf.number}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">{tf.desc}</div>
            </div>
            <div className="w-8 h-8 rounded-full bg-slate-800 group-hover:bg-cyan-900 text-slate-300 group-hover:text-cyan-300 flex items-center justify-center text-xs">
              📞
            </div>
          </a>
        ))}
      </div>

      {/* Category Filter Chips */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
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

      {/* Contacts Grid */}
      {isLoading ? (
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl text-center text-slate-400 text-xs">
          Loading verified emergency directory...
        </div>
      ) : !contacts || contacts.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl text-center text-slate-500 text-xs">
          No contacts found for this category.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {contacts.map((contact) => (
            <div
              key={contact.id}
              className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-xl p-4 flex flex-col justify-between transition-all"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="text-sm font-semibold text-white">{contact.name}</h3>
                    <div className="text-xs text-slate-400 mt-0.5">{contact.designation || contact.category}</div>
                  </div>
                  <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700 uppercase font-mono">
                    {contact.category}
                  </span>
                </div>

                <div className="mt-3 space-y-1 text-xs text-slate-300">
                  {contact.location_name && (
                    <div className="flex items-center gap-1.5 text-slate-400">
                      <span>📍</span>
                      <span>{contact.location_name}</span>
                    </div>
                  )}

                  {contact.capacity && (
                    <div className="flex items-center gap-1.5 text-emerald-400 font-mono">
                      <span>🏠</span>
                      <span>Capacity: {contact.capacity} persons</span>
                    </div>
                  )}

                  {contact.distance_km !== undefined && contact.distance_km !== null && (
                    <div className="flex items-center gap-1.5 text-cyan-400 font-mono text-[11px]">
                      <span>📏</span>
                      <span>Distance: {contact.distance_km.toFixed(1)} km away</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Tap to Call */}
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                <span className="font-mono text-xs text-slate-300">{contact.phone}</span>
                <a
                  href={`tel:${contact.phone}`}
                  className="bg-emerald-900/80 hover:bg-emerald-800 text-emerald-200 border border-emerald-700 px-3 py-1 rounded text-xs font-semibold flex items-center gap-1.5 transition-colors"
                >
                  <span>📞</span> Call
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
