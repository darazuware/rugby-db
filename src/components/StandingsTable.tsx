import React from 'react';

interface Standing {
    rank: string;
    team_name: string;
    team_name_jp?: string;
    display_name?: string; // standings.json の互換性のため追加
    flag?: string;
    slug: string;
    played: string;
    won: string;
    drawn: string;
    lost: string;
    diff: string;
    points: string;
    division?: string;
}

interface MatchResult {
    home: string;
    home_flag?: string;
    away: string;
    away_flag?: string;
    score: string;
    date?: string;
    display_name?: string;
}

interface Props {
    leagueId: string;
    standings: Standing[];
    results?: MatchResult[];
}

const getLeagueConfig = (leagueId: string) => {
    switch (leagueId) {
        case 'league-one':
            return {
                bg: 'bg-[#E60012]',
                accent: 'text-[#E60012]',
                border: 'border-[#E60012]/20',
                highlight: 'bg-[#E60012]/5',
                name: 'LEAGUE ONE'
            };
        case 'top14':
            return {
                bg: 'bg-[#C5A059]',
                accent: 'text-[#C5A059]',
                border: 'border-[#C5A059]/20',
                highlight: 'bg-[#C5A059]/5',
                name: 'TOP 14'
            };
        case 'super-rugby':
            return {
                bg: 'bg-[#0055A4]',
                accent: 'text-[#0055A4]',
                border: 'border-[#0055A4]/20',
                highlight: 'bg-[#0055A4]/5',
                name: 'SUPER RUGBY'
            };
        case 'urc':
            return {
                bg: 'bg-[#0097D7]',
                accent: 'text-[#0097D7]',
                border: 'border-[#0097D7]/20',
                highlight: 'bg-[#0097D7]/5',
                name: 'URC'
            };
        default:
            return {
                bg: 'bg-foreground',
                accent: 'text-accent',
                border: 'border-accent/20',
                highlight: 'bg-accent/5',
                name: leagueId.toUpperCase()
            };
    }
};

const StandingsTable: React.FC<Props> = ({ leagueId, standings: rawStandings, results }) => {
    const config = getLeagueConfig(leagueId);

    // standings が配列であることを保証
    const standings = Array.isArray(rawStandings) ? rawStandings : 
                    (rawStandings ? Object.values(rawStandings) as Standing[] : []);

    // ディビジョンごとにグループ化
    const hasDivisions = standings.length > 0 && standings.some(s => s.division);
    const groups: { [key: string]: Standing[] } = {};

    if (hasDivisions) {
        standings.forEach(s => {
            const div = s.division || 'Other';
            if (!groups[div]) groups[div] = [];
            groups[div].push(s);
        });
    }

    const renderRows = (items: Standing[]) => (
        items.map((team, index) => {
            const displayName = team.display_name || team.team_name_jp || team.team_name;
            return (
                <tr key={team.slug} className={`hover:bg-background transition-colors ${index < 4 ? config.highlight : ''}`}>
                    <td className={`px-2 py-4 text-center font-black text-foreground border-r border-border-dim/20 ${index < 4 ? config.accent : ''} text-[10px]`}>
                        {team.rank}
                    </td>
                    <td className="px-2 py-4">
                        <div className="flex flex-col min-w-[100px]">
                            <div className="flex items-center gap-1 mb-0.5">
                                {team.flag && <span className="text-xs scale-110 mr-1 flex-shrink-0">{team.flag}</span>}
                                <span className={`font-black text-foreground leading-tight tracking-tighter break-keep ${((displayName || '').length > 10) ? 'text-[9px]' : 'text-[11px]'}`}>
                                    {displayName}
                                </span>
                            </div>
                        </div>
                    </td>
                    <td className="px-2 py-4 text-center font-bold text-foreground/60 border-l border-border-dim/10 text-[10px] sm:text-[12px]">{team.played}</td>
                    <td className="px-2 py-4 text-center font-bold text-foreground/60 text-[10px] sm:text-[12px]">{team.won}</td>
                    <td className="px-2 py-4 text-center font-bold text-foreground/60 text-[10px] sm:text-[12px]">{team.drawn}</td>
                    <td className="px-2 py-4 text-center font-bold text-foreground/60 text-[10px] sm:text-[12px]">{team.lost}</td>
                    <td className="px-2 py-4 text-center font-bold text-foreground/40 text-[10px] sm:text-[12px]">{team.diff}</td>
                    <td className={`px-2 py-4 text-center font-black text-foreground bg-foreground/5 text-[10px] sm:text-[11px] border-l border-border-dim/20 shadow-[inset_-1px_0_0_rgba(0,0,0,0.05)]`}>
                        {team.points}
                    </td>
                </tr>
            );
        })
    );

    return (
        <div className="flex flex-col gap-6">
                    <div className="bg-card rounded-3xl shadow-xl border border-border-dim/50 overflow-hidden">
                <div className={`p-4 border-b border-border-dim/20 flex justify-between items-center ${config.bg}`}>
                    <h2 className="text-lg font-black text-white italic tracking-tighter uppercase">
                        {config.name} <span className="text-white/60">順位表</span>
                    </h2>
                    <span className="text-[9px] font-black text-white/50 uppercase tracking-widest bg-black/10 px-2 py-0.5 rounded-full">Standings</span>
                </div>
                {(!standings || standings.length === 0) ? (
                    <div className="p-8 text-center">
                        <p className="text-foreground/40 font-bold italic">順位データがありません</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-background border-b border-border-dim text-[9px] font-black text-foreground/40 uppercase tracking-widest">
                                    <th className="px-2 py-3 text-center w-8">位</th>
                                    <th className="px-2 py-3 min-w-[80px]">チーム</th>
                                    <th className="px-2 py-3 text-center text-[10px] sm:text-[12px]">試</th>
                                    <th className="px-2 py-3 text-center text-[10px] sm:text-[12px]">勝</th>
                                    <th className="px-2 py-3 text-center text-[10px] sm:text-[12px]">分</th>
                                    <th className="px-2 py-3 text-center text-[10px] sm:text-[12px]">負</th>
                                    <th className="px-2 py-3 text-center text-[10px] sm:text-[12px]">±</th>
                                    <th className="px-2 py-3 text-center text-foreground bg-foreground/5">勝点</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border-dim/10">
                                {hasDivisions ? (
                                    Object.keys(groups).sort().map(div => (
                                        <React.Fragment key={div}>
                                            <tr className="bg-background border-y border-border-dim">
                                                <td colSpan={8} className="px-4 py-2.5">
                                                    <div className="flex items-center gap-2">
                                                        <span className={`w-1.5 h-4 ${config.bg} rounded-full`}></span>
                                                        <span className="text-[11px] font-black text-foreground uppercase tracking-[0.2em]">
                                                            {div === 'D1' ? 'Division 1' : div === 'D2' ? 'Division 2' : div === 'D3' ? 'Division 3' : div}
                                                        </span>
                                                    </div>
                                                </td>
                                            </tr>
                                            {renderRows(groups[div])}
                                        </React.Fragment>
                                    ))
                                ) : (
                                    renderRows(standings)
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* 最新の試合結果 */}
            {results && results.length > 0 && (
                <div className="bg-card rounded-3xl shadow-xl border border-border-dim/50 overflow-hidden">
                    <div className={`p-4 border-b border-border-dim/20 flex justify-between items-center ${config.bg}`}>
                        <h2 className="text-lg font-black text-white italic tracking-tighter uppercase">
                            RECENT <span className="text-white/60">RESULTS</span>
                        </h2>
                        <span className="text-[9px] font-black text-white/50 uppercase tracking-widest bg-black/10 px-2 py-0.5 rounded-full">Matches</span>
                    </div>
                    <div className="p-4 space-y-6">
                        {(() => {
                            // 結果をディビジョンごとにグループ化
                            const resultGroups: { [key: string]: typeof results } = {};
                            results.forEach(r => {
                                const div = (r as any).division || 'Default';
                                if (!resultGroups[div]) resultGroups[div] = [];
                                resultGroups[div].push(r);
                            });

                            return Object.keys(resultGroups).sort().map(div => (
                                <div key={div} className="space-y-3">
                                    {div !== 'Default' && (
                                        <div className="flex items-center gap-2 mb-2 px-1">
                                            <span className={`w-1 h-3 ${config.bg} rounded-full`}></span>
                                            <span className="text-[10px] font-black text-foreground/40 uppercase tracking-widest">
                                                {div === 'D1' ? 'Division 1' : div === 'D2' ? 'Division 2' : div === 'D3' ? 'Division 3' : div}
                                            </span>
                                        </div>
                                    )}
                                    <div className="space-y-3">
                                        {resultGroups[div].map((result, idx) => {
                                            const dateStr = result.date ? new Date(result.date).toLocaleDateString('ja-JP', { month: '2-digit', day: '2-digit' }) : '';
                                            return (
                                                <div key={idx} className="flex items-center justify-between p-3 bg-background rounded-2xl border border-border-dim group hover:border-yellow-200 transition-colors">
                                                    <div className="flex flex-col items-center flex-1 min-w-0">
                                                        <span className="text-base md:text-lg mb-0.5 shrink-0">{result.home_flag}</span>
                                                        <span className="text-[9px] md:text-[10px] font-black text-foreground text-center leading-tight truncate w-full">{result.home}</span>
                                                    </div>
                                                    <div className="flex flex-col items-center px-2 shrink-0">
                                                        {dateStr && (
                                                            <span className="text-[7px] font-black text-foreground/40 uppercase mb-0.5 tabular-nums">
                                                                {dateStr}
                                                            </span>
                                                        )}
                                                        {!dateStr && <span className="text-[8px] font-black text-foreground/20 uppercase italic mb-0.5">VS</span>}
                                                        <span className="text-base md:text-xl font-black text-foreground tracking-tighter bg-card px-2 py-0.5 rounded-lg border border-border-dim shadow-sm group-hover:bg-yellow-50 dark:group-hover:bg-yellow-900 group-hover:border-yellow-200 transition-colors tabular-nums min-w-[55px] text-center">
                                                            {result.score}
                                                        </span>
                                                    </div>
                                                    <div className="flex flex-col items-center flex-1 min-w-0">
                                                        <span className="text-base md:text-lg mb-0.5 shrink-0">{result.away_flag}</span>
                                                        <span className="text-[9px] md:text-[10px] font-black text-foreground text-center leading-tight truncate w-full">{result.away}</span>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            ));
                        })()}
                    </div>
                </div>
            )}
        </div>
    );
};

export default StandingsTable;
