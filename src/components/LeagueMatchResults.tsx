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
  const [selectedDivision, setSelectedDivision] = useState<string | 'all'>('all');

  // 1. Divisionのリストを抽出
  const divisions = useMemo(() => {
    const d = new Set<string>();
    matches.forEach(m => {
      if (m.division) d.add(m.division);
    });
    return Array.from(d).sort();
  }, [matches]);

  // 2. フィルタリングと制限ロジック
  const { displayGroups, currentMode } = useMemo(() => {
    // 全試合をラウンドごとに分割
    // ゴミデータ等を除外するフィルタ（VSも含めるように変更）
    const filteredMatches = matches.filter(m => m.score);

    const groups: Record<number, Match[]> = {};
    filteredMatches.forEach(m => {
      const r = m.round || 0;
      if (!groups[r]) groups[r] = [];
      groups[r].push(m);
    });

    const sortedRounds = Object.keys(groups).map(Number).sort((a, b) => b - a);
    
    // --- モード A: リーグ全体表示 (ALL) ---
    if (selectedDivision === 'all') {
      const latestRound = sortedRounds[0] || 0;
      const roundMatches = groups[latestRound] || [];
      
      // D1 -> D2 -> D3 の順にソート
      const sortedMatches = [...roundMatches].sort((a, b) => {
        const divA = (a.division || '').toUpperCase();
        const divB = (b.division || '').toUpperCase();
        return divA.localeCompare(divB);
      });

      const displayGroups: [string, Match[]][] = latestRound ? [[`第${latestRound}節 (最新)`, sortedMatches]] : [];
      return {
        displayGroups,
        currentMode: 'ALL'
      };
    }

    // --- モード B: Division 選択時 (D1, D2, D3) ---
    const divMatches = filteredMatches.filter(m => m.division === selectedDivision);
    const divGroups: Record<number, Match[]> = {};
    divMatches.forEach(m => {
      const r = m.round || 0;
      if (!divGroups[r]) divGroups[r] = [];
      divGroups[r].push(m);
    });

    const divRounds = Object.keys(divGroups).map(Number).sort((a, b) => b - a).slice(0, 3);
    const result: [string, Match[]][] = divRounds.map(r => [`第${r}節`, divGroups[r]]);

    return {
      displayGroups: result,
      currentMode: 'DIV'
    };
  }, [matches, selectedDivision]);

  return (
    <div className="mt-16">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
        <div className="flex-1">
            <div className="flex items-center gap-4 mb-4">
                <h2 className="text-2xl font-black text-foreground italic tracking-tight uppercase">Recent Results</h2>
                <div className="h-px flex-1 bg-border-dim"></div>
            </div>
            <p className="text-foreground/40 text-xs font-bold uppercase tracking-widest">
                {selectedDivision === 'all' 
                  ? 'リーグ共通：最新節の全試合' 
                  : `${selectedDivision}：最新3節分の結果`}
            </p>
        </div>

        {/* Division Filter */}
        {divisions.length > 0 && (
          <div className="flex gap-1.5 bg-card/50 p-1.5 rounded-2xl border border-border-dim/50 backdrop-blur-sm shadow-xl">
            <button
              onClick={() => setSelectedDivision('all')}
              className={`px-4 py-2 rounded-xl text-[10px] font-black transition-all uppercase tracking-wider ${
                selectedDivision === 'all' ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20' : 'text-foreground/40 hover:text-foreground hover:bg-foreground/5'
              }`}
            >
              ALL
            </button>
            {divisions.map(d => (
              <button
                key={d}
                onClick={() => setSelectedDivision(d)}
                className={`px-4 py-2 rounded-xl text-[10px] font-black transition-all uppercase tracking-wider ${
                  selectedDivision === d ? 'bg-red-600 text-white shadow-lg shadow-red-600/20' : 'text-foreground/40 hover:text-foreground hover:bg-foreground/5'
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Results List */}
      <div className="space-y-16">
        {displayGroups.map(([roundKey, roundMatches], gIdx) => (
          <div key={gIdx} className="space-y-6">
            <div className="flex items-center gap-3">
              <span className="text-yellow-400 font-black italic text-sm tracking-widest uppercase">{roundKey}</span>
              <div className="h-px flex-1 bg-border-dim/50"></div>
            </div>
            <div className="grid gap-4">
              {(roundMatches as Match[]).map((m, idx) => (
                <div key={idx} className="bg-card/60 backdrop-blur-md border border-border-dim/80 rounded-2xl p-4 md:p-6 hover:border-yellow-400/40 transition-all group overflow-hidden shadow-xl relative">
                  {selectedDivision === 'all' && m.division && (
                    <div className="absolute top-0 right-0 px-3 py-1 bg-red-600 text-[8px] font-black text-white italic rounded-bl-lg uppercase tracking-tighter">
                      {m.division}
                    </div>
                  )}
                  <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2 md:gap-8">
                    {/* Home */}
                    <div className="flex items-center gap-2 md:gap-4 justify-end text-right min-w-0">
                        <span className="text-xs md:text-lg font-black text-black bg-white px-3 py-1 rounded-lg shadow-sm truncate tracking-tight border border-gray-200">
                            {m.home}
                        </span>
                        <span className="text-xl md:text-3xl shrink-0 drop-shadow-sm">{m.home_flag}</span>
                    </div>

                    {/* Score */}
                    <div className="flex flex-col items-center min-w-[90px] md:min-w-[160px]">
                        <div className="text-xl md:text-4xl font-black text-yellow-400 italic tabular-nums bg-background px-4 py-1.5 md:px-8 md:py-3 rounded-xl border border-border-dim tracking-tighter shadow-[inset_0_2px_10px_rgba(0,0,0,0.5)] group-hover:border-yellow-400/30 transition-colors">
                            {m.score}
                        </div>
                        <span className="text-[10px] text-foreground/40 font-bold mt-2 uppercase tracking-[0.2em]">{m.date.replace(/-/g, '/')}</span>
                    </div>

                    {/* Away */}
                    <div className="flex items-center gap-2 md:gap-4 justify-start text-left min-w-0">
                        <span className="text-xl md:text-3xl shrink-0 drop-shadow-sm">{m.away_flag}</span>
                        <span className="text-xs md:text-lg font-black text-black bg-white px-3 py-1 rounded-lg shadow-sm truncate tracking-tight border border-gray-200">
                            {m.away}
                        </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Link to Results Page */}
      <div className="mt-16 flex justify-center">
        <a 
          href={`/results?league=${leagueId}${selectedDivision !== 'all' ? `-${selectedDivision.toLowerCase()}` : ''}`}
          className="group relative inline-flex items-center gap-3 px-8 py-4 bg-foreground/5 hover:bg-yellow-400 text-foreground/60 hover:text-black font-black rounded-2xl border border-border-dim hover:border-yellow-400 transition-all duration-500 overflow-hidden"
        >
          <span className="relative z-10 text-xs uppercase tracking-[0.3em]">すべての戦績・試合詳細を見る</span>
          <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 relative z-10 transition-transform group-hover:translate-x-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
        </a>
      </div>
    </div>
  );
};

export default LeagueMatchResults;
