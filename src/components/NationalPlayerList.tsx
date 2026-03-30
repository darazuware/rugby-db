import React, { useState, useMemo } from 'react';

interface Player {
  name_ja: string;
  name_en: string;
  slug: string;
  position: string;
  team: string;
  league: string;
  caps: string; // Changed to string for flexibility
  age: string | null;
  height: string;
  weight: string;
  caps_display?: string;
}

const FLAG_MAP: Record<string, string> = {
  '日本': '🇯🇵', 'Japan': '🇯🇵',
  'オーストラリア': '🇦🇺', 'Australia': '🇦🇺',
  'ニュージーランド': '🇳🇿', 'New Zealand': '🇳🇿',
  '南アフリカ': '🇿🇦', 'South Africa': '🇿🇦',
  'フィジー': '🇫🇯', 'Fiji': '🇫🇯',
  'トンガ': '🇹🇴', 'Tonga': '🇹🇴',
  'サモア': '🇼🇸', 'Samoa': '🇼🇸',
  'フランス': '🇫🇷', 'France': '🇫🇷',
  'イングランド': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
  'ウェールズ': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'Wales': '🏴󠁧󠁢󠁷󠁬󠁳󠁿',
  'スコットランド': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
  'アイルランド': '🇮🇪', 'Ireland': '🇮🇪',
  'イタリア': '🇮🇹', 'Italy': '🇮🇹',
  'アルゼンチン': '🇦🇷', 'Argentina': '🇦🇷',
  'アメリカ': '🇺🇸', 'USA': '🇺🇸',
  'カナダ': '🇨🇦', 'Canada': '🇨🇦',
  'ジョージア': '🇬🇪', 'Georgia': '🇬🇪',
  'ウルグアイ': '🇺🇾', 'Uruguay': '🇺🇾',
  'ポルトガル': '🇵🇹', 'Portugal': '🇵🇹',
  'ルーマニア': '🇷🇴', 'Romania': '🇷🇴',
  'ナミビア': '🇳🇦', 'Namibia': '🇳🇦',
  'チリ': '🇨🇱', 'Chile': '🇨🇱'
};

const getFlag = (capsStr: string) => {
  if (!capsStr) return "";
  for (const [name, flag] of Object.entries(FLAG_MAP)) {
    if (capsStr.includes(name)) return flag;
  }
  return "";
};

interface Props {
  initialPlayers: Player[];
  teamColor: string;
  textColor: string;
}

const NationalPlayerList: React.FC<Props> = ({ initialPlayers, teamColor, textColor }) => {
  const [sortBy, setSortBy] = useState<string>('caps_desc');
  const [filterPos, setFilterPos] = useState<string>('ALL');
  const [filterLeague, setFilterLeague] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

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

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const qNoSpace = q.replace(/\s+/g, '');
      result = result.filter(p => {
        const nameJa = p.name_ja.toLowerCase();
        const nameEn = p.name_en.toLowerCase();
        return nameJa.includes(q) ||
          nameJa.replace(/\s+/g, '').includes(qNoSpace) ||
          nameEn.includes(q) ||
          nameEn.replace(/\s+/g, '').includes(qNoSpace) ||
          p.team.toLowerCase().includes(q);
      });
    }

      result.sort((a, b) => {
      const capsA = parseInt(String(a.caps).match(/\d+/)?.[0] || '0');
      const capsB = parseInt(String(b.caps).match(/\d+/)?.[0] || '0');
      const ageA = parseInt(String(a.age).match(/\d+/)?.[0] || '999');
      const ageB = parseInt(String(b.age).match(/\d+/)?.[0] || '0');
      const heightA = parseFloat(a.height) || 0;
      const heightB = parseFloat(b.height) || 0;
      const weightA = parseFloat(a.weight) || 0;
      const weightB = parseFloat(b.weight) || 0;

      switch (sortBy) {
        case 'caps_desc': return capsB - capsA;
        case 'caps_asc': return capsA - capsB;
        case 'age_asc': return ageA - ageB;
        case 'age_desc': return ageB - ageA;
        case 'height_desc': return heightB - heightA;
        case 'height_asc': return heightA - heightB;
        case 'weight_desc': return weightB - weightA;
        case 'weight_asc': return weightA - weightB;
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
                { id: 'caps_desc', label: 'CAPS (多)' },
                { id: 'caps_asc', label: 'CAPS (少)' },
                { id: 'age_desc', label: '年齢 (高)' },
                { id: 'age_asc', label: '年齢 (低)' },
                { id: 'height_desc', label: '身長 (高)' },
                { id: 'height_asc', label: '身長 (低)' },
                { id: 'weight_desc', label: '体重 (重)' },
                { id: 'weight_asc', label: '体重 (軽)' },
              ].map(opt => (
                <button
                  key={opt.id}
                  onClick={() => setSortBy(opt.id)}
                  style={sortBy === opt.id ? { backgroundColor: teamColor, color: textColor } : {}}
                  className={`px-4 py-2 rounded-xl text-[10px] font-black italic transition-all border border-border-dim/30 hover:border-yellow-400/50 uppercase tracking-wider whitespace-nowrap ${
                    sortBy === opt.id ? 'shadow-lg' : 'bg-card/50 text-foreground/40'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto items-end">
            <div className="space-y-3 w-full md:w-64">
              <h3 className="text-[10px] font-black text-foreground/40 uppercase tracking-[0.2em] italic">Search Player / Team</h3>
              <div className="relative">
                <input
                  type="text"
                  placeholder="名前・チーム名で検索..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-card/50 border border-border-dim/30 rounded-xl px-4 py-2.5 pl-10 text-[10px] font-black text-foreground focus:outline-none focus:border-yellow-400 transition-all placeholder:text-foreground/20"
                />
                <div className="absolute left-3.5 top-1/2 -translate-y-1/2 text-foreground/20">
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                </div>
                {searchQuery && (
                   <button 
                    onClick={() => setSearchQuery('')}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-foreground/30 hover:text-yellow-400 transition-colors"
                   >
                     <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M18 6 6 18M6 6l12 12"/></svg>
                   </button>
                )}
              </div>
            </div>

            <div className="space-y-3 flex-1 md:w-32">
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

            <div className="space-y-3 flex-1 md:w-32">
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
                  <h4 className="text-lg font-black text-foreground group-hover:text-yellow-400 transition-colors leading-tight flex items-center gap-2">
                    {getFlag(player.caps) && <span className="text-xl">{getFlag(player.caps)}</span>}
                    {player.name_ja || player.name_en}
                  </h4>
                  <p className="text-[10px] font-bold text-foreground/40 uppercase italic tracking-tighter">{player.name_en}</p>
                </div>
                {parseInt(String(player.caps).match(/\d+/)?.[0] || '0') > 0 && (
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
