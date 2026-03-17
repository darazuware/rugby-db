import React, { useState, useMemo } from 'react';

interface Player {
  name_ja: string;
  name_en: string;
  slug: string;
  position: string;
  team: string;
  league: string;
  caps: number;
  age: number | null;
  height: number;
  weight: number;
  caps_display?: string;
}

interface Props {
  initialPlayers: Player[];
  teamColor: string;
  textColor: string;
}

const NationalPlayerList: React.FC<Props> = ({ initialPlayers, teamColor, textColor }) => {
  const [sortBy, setSortBy] = useState<string>('caps');
  const [filterPos, setFilterPos] = useState<string>('ALL');
  const [filterLeague, setFilterLeague] = useState<string>('ALL');

  const positions = useMemo(() => {
    const ps = initialPlayers.map(p => p.position).filter(Boolean);
    return ['ALL', ...Array.from(new Set(ps))];
  }, [initialPlayers]);

  const leagues = useMemo(() => {
    const ls = initialPlayers.map(p => p.league).filter(Boolean);
    return ['ALL', ...Array.from(new Set(ls))];
  }, [initialPlayers]);

  const sortedPlayers = useMemo(() => {
    let result = [...initialPlayers];
    
    if (filterPos !== 'ALL') {
      result = result.filter(p => p.position === filterPos);
    }

    if (filterLeague !== 'ALL') {
      result = result.filter(p => p.league === filterLeague);
    }

    result.sort((a, b) => {
      switch (sortBy) {
        case 'caps': return (b.caps || 0) - (a.caps || 0);
        case 'age_asc': return (a.age || 999) - (b.age || 999);
        case 'age_desc': return (b.age || 0) - (a.age || 0);
        case 'height': return (b.height || 0) - (a.height || 0);
        case 'weight': return (b.weight || 0) - (a.weight || 0);
        default: return 0;
      }
    });
    return result;
  }, [initialPlayers, sortBy, filterPos, filterLeague]);

  return (
    <div className="space-y-8">
      {/* フィルター・ソートパネル */}
      <div className="bg-card/30 backdrop-blur-xl border border-border-dim/50 rounded-3xl p-6 md:p-8 sticky top-20 z-30 shadow-2xl">
        <div className="flex flex-col md:flex-row gap-6 justify-between items-start md:items-center">
          <div className="space-y-3 w-full md:w-auto">
            <h3 className="text-[10px] font-black text-foreground/40 uppercase tracking-[0.2em] italic">Sort By</h3>
            <div className="flex flex-wrap gap-2">
              {[
                { id: 'caps', label: 'CAPS' },
                { id: 'age_asc', label: '年齢 (昇順)' },
                { id: 'age_desc', label: '年齢 (降順)' },
                { id: 'height', label: '身長' },
                { id: 'weight', label: '体重' },
              ].map(opt => (
                <button
                  key={opt.id}
                  onClick={() => setSortBy(opt.id)}
                  style={sortBy === opt.id ? { backgroundColor: teamColor, color: textColor } : {}}
                  className={`px-4 py-2 rounded-xl text-[10px] font-black italic transition-all border border-border-dim/30 hover:border-yellow-400/50 uppercase tracking-wider ${
                    sortBy === opt.id ? 'shadow-lg' : 'bg-card/50 text-foreground/40'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto">
            <div className="space-y-3 flex-1 md:w-40">
              <h3 className="text-[10px] font-black text-foreground/40 uppercase tracking-[0.2em] italic">League</h3>
              <div className="relative">
                <select
                  value={filterLeague}
                  onChange={(e) => setFilterLeague(e.target.value)}
                  className="w-full bg-card/50 border border-border-dim/30 rounded-xl px-4 py-2.5 text-[10px] font-black text-foreground/60 appearance-none cursor-pointer focus:outline-none focus:border-yellow-400 transition-all uppercase tracking-widest"
                >
                  {leagues.map(l => <option key={l} value={l}>{l.toUpperCase()}</option>)}
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-foreground/20">
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="m6 9 6 6 6-6"/></svg>
                </div>
              </div>
            </div>

            <div className="space-y-3 flex-1 md:w-40">
              <h3 className="text-[10px] font-black text-foreground/40 uppercase tracking-[0.2em] italic">Position</h3>
              <div className="relative">
                <select
                  value={filterPos}
                  onChange={(e) => setFilterPos(e.target.value)}
                  className="w-full bg-card/50 border border-border-dim/30 rounded-xl px-4 py-2.5 text-[10px] font-black text-foreground/60 appearance-none cursor-pointer focus:outline-none focus:border-yellow-400 transition-all uppercase tracking-widest"
                >
                  {positions.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-foreground/20">
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="m6 9 6 6 6-6"/></svg>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-border-dim/10">
          <div className="text-[10px] font-bold text-foreground/30 uppercase tracking-widest italic">
            Showing <span className="text-yellow-400 font-black">{sortedPlayers.length}</span> players
          </div>
        </div>
      </div>

      {/* 選手グリッド */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedPlayers.map((player) => (
          <a
            key={player.slug}
            href={`/players/${player.slug}`}
            className="group block bg-card/40 backdrop-blur-md border border-border-dim/50 rounded-2xl p-5 hover:border-yellow-400/50 transition-all duration-500 relative overflow-hidden"
          >
            {/* 背景デコレーション */}
            <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br opacity-[0.03] group-hover:opacity-[0.1] transition-opacity duration-700 rounded-bl-full" style={{ backgroundColor: teamColor }}></div>
            
            <div className="relative z-10 flex flex-col h-full">
              <div className="flex justify-between items-start mb-4">
                <div className="space-y-1">
                  <div className="text-[9px] font-black text-yellow-500/80 uppercase tracking-widest italic">{player.position}</div>
                  <h4 className="text-lg font-black text-foreground group-hover:text-yellow-400 transition-colors leading-tight">
                    {player.name_ja}
                  </h4>
                  <p className="text-[10px] font-bold text-foreground/40 uppercase italic tracking-tighter">{player.name_en}</p>
                </div>
                {player.caps > 0 && (
                  <div className="flex flex-col items-end">
                    <div className="text-[18px] font-black text-yellow-400 italic leading-none">{player.caps}</div>
                    <div className="text-[8px] font-black text-foreground/30 uppercase tracking-tighter">CAPS</div>
                  </div>
                )}
              </div>

              <div className="mt-auto pt-4 border-t border-border-dim/10 grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <span className="text-[8px] font-bold text-foreground/30 uppercase block">Vital Stats</span>
                  <div className="text-[10px] font-black text-foreground/60 italic">
                    {player.age ? `${player.age}歳` : '不明'} / {player.height}cm / {player.weight}kg
                  </div>
                </div>
                <div className="space-y-1 text-right">
                  <span className="text-[8px] font-bold text-foreground/30 uppercase block">Current Club</span>
                  <div className="text-[10px] font-black text-foreground hover:text-yellow-300 truncate transition-colors">
                    {player.team}
                  </div>
                </div>
              </div>
            </div>
            
            {/* 装飾アクセント */}
            <div 
              className="absolute bottom-0 left-0 w-1 h-0 group-hover:h-full transition-all duration-500"
              style={{ backgroundColor: teamColor }}
            ></div>
          </a>
        ))}
      </div>
    </div>
  );
};

export default NationalPlayerList;
