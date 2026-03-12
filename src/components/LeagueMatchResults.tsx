import React, { useState, useMemo } from 'react';

interface Match {
  round: number;
  date: string;
  home: string;
  away: string;
  score: string;
  home_flag: string;
  away_flag: string;
  division?: string;
  detail_url?: string;
}

interface Props {
  matches: Match[];
  leagueId: string;
}

const LeagueMatchResults: React.FC<Props> = ({ matches, leagueId }) => {
  // 1. Divisionのリストを抽出 (League One用)
  const divisions = useMemo(() => {
    const d = new Set<string>();
    matches.forEach(m => {
      if (m.division) d.add(m.division);
    });
    return Array.from(d).sort();
  }, [matches]);

  // 2. Roundのリストを抽出
  const rounds = useMemo(() => {
    const r = new Set<number>();
    matches.forEach(m => {
      if (m.round > 0) r.add(m.round);
    });
    return Array.from(r).sort((a, b) => b - a); // 降順
  }, [matches]);

  const [selectedRound, setSelectedRound] = useState<number | 'all'>(rounds.length > 0 ? rounds[0] : 'all');
  const [selectedDivision, setSelectedDivision] = useState<string | 'all'>('all');

  // 3. フィルタリング
  const filteredMatches = useMemo(() => {
    return matches.filter(m => {
      const matchRound = selectedRound === 'all' || m.round === selectedRound;
      const matchDiv = selectedDivision === 'all' || m.division === selectedDivision;
      return matchRound && matchDiv;
    });
  }, [matches, selectedRound, selectedDivision]);

  // Round表示ラベルの生成
  const getRoundLabel = (r: number | 'all') => {
    if (r === 'all') return '全て表示';
    if (leagueId.startsWith('league-one')) return `第${r}節`;
    return `Round ${r}`;
  };

  // 4. グループ化 (Roundごと)
  const groupedMatches = useMemo(() => {
    // 試合をラウンドごとにグループ化
    const groups = filteredMatches.reduce((acc, match) => {
      let roundKey = match.round && match.round !== 0 ? getRoundLabel(match.round) : 'OTHER MATCHES';
      
      if (leagueId === 'league-one' && (!match.round || match.round === 0)) {
          roundKey = 'MATCHES';
      }

      if (!acc[roundKey]) {
        acc[roundKey] = [];
      }
      acc[roundKey].push(match);
      return acc;
    }, {} as Record<string, Match[]>);
    
    // ソート (Round 降順)
    return Object.entries(groups).sort((a, b) => {
        // ラベルから数値を抽出して比較
        const getNum = (s: string) => {
            const m = s.match(/\d+/);
            return m ? parseInt(m[0]) : 0;
        };
        const numA = getNum(a[0]);
        const numB = getNum(b[0]);
        if (numA !== 0 && numB !== 0) return numB - numA;

        if (a[0] === 'MATCHES') return -1;
        if (b[0] === 'MATCHES') return 1;
        return a[0].localeCompare(b[0]);
    });
  }, [filteredMatches, leagueId]);

  return (
    <div className="mt-16">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
        <div className="flex-1">
            <div className="flex items-center gap-4 mb-4">
                <h2 className="text-2xl font-black text-white italic tracking-tight uppercase">Match Results</h2>
                <div className="h-px flex-1 bg-gray-900"></div>
            </div>
            <p className="text-gray-500 text-xs font-bold uppercase tracking-widest">
                {selectedRound === 'all' ? '全ての節を表示中' : `${getRoundLabel(selectedRound as number)} の結果`}
            </p>
        </div>

        {/* Division Filter (Compact) */}
        {divisions.length > 0 && (
          <div className="flex gap-1.5 bg-gray-900/50 p-1.5 rounded-2xl border border-gray-800/50 backdrop-blur-sm shadow-xl">
            <button
              onClick={() => setSelectedDivision('all')}
              className={`px-4 py-2 rounded-xl text-[10px] font-black transition-all uppercase tracking-wider ${
                selectedDivision === 'all' ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20' : 'text-gray-500 hover:text-white hover:bg-white/5'
              }`}
            >
              ALL
            </button>
            {divisions.map(d => (
              <button
                key={d}
                onClick={() => setSelectedDivision(d)}
                className={`px-4 py-2 rounded-xl text-[10px] font-black transition-all uppercase tracking-wider ${
                  selectedDivision === d ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20' : 'text-gray-500 hover:text-white hover:bg-white/5'
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Round Selection Scroll Bar */}
      <div className="relative mb-12 group">
        <div className="flex gap-2 overflow-x-auto pb-4 scrollbar-hide -mx-4 px-4 md:mx-0 md:px-0 mask-fade-right">
          <button
            onClick={() => setSelectedRound('all')}
            className={`shrink-0 px-6 py-3 rounded-2xl text-xs font-black transition-all border uppercase tracking-widest leading-none ${
              selectedRound === 'all' 
                ? 'bg-yellow-400 border-yellow-500 text-black shadow-xl shadow-yellow-400/20 scale-105' 
                : 'bg-gray-900/80 border-gray-800 text-gray-400 hover:border-gray-600 hover:text-white'
            }`}
          >
            ALL
          </button>
          {rounds.map(r => (
            <button
              key={r}
              onClick={() => setSelectedRound(r)}
              className={`shrink-0 px-6 py-3 rounded-2xl text-xs font-black transition-all border uppercase tracking-widest leading-none ${
                selectedRound === r 
                    ? 'bg-yellow-400 border-yellow-500 text-black shadow-xl shadow-yellow-400/20 scale-105' 
                    : 'bg-gray-900/80 border-gray-800 text-gray-400 hover:border-gray-600 hover:text-white'
              }`}
            >
              {getRoundLabel(r)}
            </button>
          ))}
        </div>
        {/* Scroll Hint */}
        <div className="absolute right-0 top-0 bottom-4 w-12 bg-gradient-to-l from-gray-950 to-transparent pointer-events-none md:hidden" />
      </div>

      {/* Results List */}
      <div className="space-y-12">
        {groupedMatches.map(([roundKey, roundMatches]) => (
          <div key={roundKey} className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="text-yellow-400/50 font-black italic text-sm tracking-widest">{roundKey}</span>
              <div className="h-px flex-1 bg-gray-800/50"></div>
            </div>
            <div className="grid gap-3">
              {roundMatches.sort((a, b) => b.date.localeCompare(a.date)).map((m, idx) => (
                <div key={idx} className="bg-gray-900/60 backdrop-blur-md border border-gray-800/80 rounded-2xl p-4 md:p-6 hover:border-yellow-400/40 transition-all group overflow-hidden shadow-xl">
                  <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2 md:gap-8">
                    {/* Home */}
                    <div className="flex items-center gap-2 md:gap-4 justify-end text-right min-w-0">
                        <span className="text-xs md:text-lg font-black text-white truncate tracking-tight">{m.home}</span>
                        <span className="text-xl md:text-3xl shrink-0 drop-shadow-sm">{m.home_flag}</span>
                    </div>

                    {/* Score */}
                    <div className="flex flex-col items-center min-w-[90px] md:min-w-[160px]">
                        <div className="text-xl md:text-4xl font-black text-yellow-400 italic tabular-nums bg-black/80 px-4 py-1.5 md:px-8 md:py-3 rounded-xl border border-gray-800 tracking-tighter shadow-[inset_0_2px_10px_rgba(0,0,0,0.5)] group-hover:border-yellow-400/30 transition-colors">
                            {m.score}
                        </div>
                        <span className="text-[10px] text-gray-500 font-bold mt-2 uppercase tracking-[0.2em]">{m.date.replace(/-/g, '/')}</span>
                    </div>

                    {/* Away */}
                    <div className="flex items-center gap-2 md:gap-4 justify-start text-left min-w-0">
                        <span className="text-xl md:text-3xl shrink-0 drop-shadow-sm">{m.away_flag}</span>
                        <span className="text-xs md:text-lg font-black text-white truncate tracking-tight">{m.away}</span>
                    </div>
                  </div>
                  
                  {m.detail_url && (
                    <div className="mt-4 pt-3 border-t border-gray-800/30 flex justify-center md:justify-end">
                      <a 
                        href={m.detail_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-900/50 hover:bg-yellow-400 text-gray-400 hover:text-black rounded-lg border border-gray-800 hover:border-yellow-400 transition-all duration-300 group/link"
                      >
                        <span className="text-[10px] font-black uppercase tracking-wider">MATCH CENTER</span>
                        <svg xmlns="http://www.w3.org/2000/svg" className="w-3 h-3 translate-y-[0.5px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                      </a>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LeagueMatchResults;
