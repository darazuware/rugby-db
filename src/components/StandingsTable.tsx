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
                bg: 'bg-gray-900',
                accent: 'text-yellow-400',
                border: 'border-yellow-400/20',
                highlight: 'bg-yellow-400/5',
                name: leagueId.toUpperCase()
            };
    }
};

const StandingsTable: React.FC<Props> = ({ leagueId, standings, results }) => {
    const config = getLeagueConfig(leagueId);

    // ディビジョンごとにグループ化
    const hasDivisions = standings?.some(s => s.division);
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
                <tr key={team.slug} className={`hover:bg-gray-50 transition-colors ${index < 4 ? config.highlight : ''}`}>
                    <td className={`px-2 py-4 text-center font-black text-gray-900 border-r border-gray-50/50 ${index < 4 ? config.accent : ''} text-[10px]`}>
                        {team.rank}
                    </td>
                    <td className="px-2 py-4">
                        <div className="flex flex-col min-w-[100px]">
                            <div className="flex items-center gap-1 mb-0.5">
                                {team.flag && <span className="text-xs scale-110 mr-1 flex-shrink-0">{team.flag}</span>}
                                <span className={`font-black text-gray-900 leading-tight tracking-tighter break-keep ${(displayName.length > 10) ? 'text-[9px]' : 'text-[11px]'}`}>
                                    {displayName}
                                </span>
                            </div>
                        </div>
                    </td>
                    <td className="px-2 py-4 text-center font-bold text-gray-600 border-l border-gray-50/50 text-[12px]">{team.played}</td>
                    <td className="px-2 py-4 text-center font-bold text-gray-600 text-[12px]">{team.won}</td>
                    <td className="px-2 py-4 text-center font-bold text-gray-600 text-[12px] md:table-cell hidden">{team.drawn}</td>
                    <td className="px-2 py-4 text-center font-bold text-gray-600 text-[12px] md:table-cell hidden">{team.lost}</td>
                    <td className="px-2 py-4 text-center font-bold text-gray-400 text-[12px] lg:table-cell hidden">{team.diff}</td>
                    <td className={`px-2 py-4 text-center font-black text-gray-900 bg-gray-50/50 text-[11px] border-l border-gray-100 shadow-[inset_-1px_0_0_rgba(0,0,0,0.05)]`}>
                        {team.points}
                    </td>
                </tr>
            );
        })
    );

    return (
        <div className="flex flex-col gap-6">
            <div className="bg-white rounded-3xl shadow-xl border border-gray-200/50 overflow-hidden">
                <div className={`p-4 border-b border-gray-50 flex justify-between items-center ${config.bg}`}>
                    <h2 className="text-lg font-black text-white italic tracking-tighter uppercase">
                        {config.name} <span className="text-white/60">順位表</span>
                    </h2>
                    <span className="text-[9px] font-black text-white/50 uppercase tracking-widest bg-black/10 px-2 py-0.5 rounded-full">Standings</span>
                </div>
                {(!standings || standings.length === 0) ? (
                    <div className="p-8 text-center">
                        <p className="text-gray-400 font-bold italic">順位データがありません</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-gray-100/50 border-b border-gray-100 text-[9px] font-black text-gray-500 uppercase tracking-widest">
                                    <th className="px-2 py-3 text-center w-8">位</th>
                                    <th className="px-2 py-3">チーム</th>
                                    <th className="px-2 py-3 text-center text-[12px]">試</th>
                                    <th className="px-2 py-3 text-center text-[12px]">勝</th>
                                    <th className="px-2 py-3 text-center md:table-cell hidden text-[12px]">分</th>
                                    <th className="px-2 py-3 text-center md:table-cell hidden text-[12px]">負</th>
                                    <th className="px-2 py-3 text-center lg:table-cell hidden text-[12px]">±</th>
                                    <th className="px-2 py-3 text-center text-gray-900 bg-gray-100">勝点</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50">
                                {hasDivisions ? (
                                    Object.keys(groups).sort().map(div => (
                                        <React.Fragment key={div}>
                                            <tr className="bg-gray-100/80 border-y border-gray-200">
                                                <td colSpan={8} className="px-4 py-2.5">
                                                    <div className="flex items-center gap-2">
                                                        <span className={`w-1.5 h-4 ${config.bg} rounded-full`}></span>
                                                        <span className="text-[11px] font-black text-gray-900 uppercase tracking-[0.2em]">
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
                <div className="bg-white rounded-3xl shadow-xl border border-gray-200/50 overflow-hidden">
                    <div className={`p-4 border-b border-gray-50 flex justify-between items-center ${config.bg}`}>
                        <h2 className="text-lg font-black text-white italic tracking-tighter uppercase">
                            RECENT <span className="text-white/60">RESULTS</span>
                        </h2>
                        <span className="text-[9px] font-black text-white/50 uppercase tracking-widest bg-black/10 px-2 py-0.5 rounded-full">Matches</span>
                    </div>
                    <div className="p-4 space-y-3">
                        {results.map((result, idx) => {
                            const dateStr = result.date ? new Date(result.date).toLocaleDateString('ja-JP', { month: '2-digit', day: '2-digit' }) : '';
                            return (
                                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-2xl border border-gray-100 group hover:border-yellow-200 transition-colors">
                                    <div className="flex flex-col items-center flex-1 min-w-0">
                                        <span className="text-base md:text-lg mb-0.5 shrink-0">{result.home_flag}</span>
                                        <span className="text-[9px] md:text-[10px] font-black text-gray-900 text-center leading-tight truncate w-full">{result.home}</span>
                                    </div>
                                    <div className="flex flex-col items-center px-2 shrink-0">
                                        {dateStr && (
                                            <span className="text-[7px] font-black text-gray-400 uppercase mb-0.5 tabular-nums">
                                                {dateStr}
                                            </span>
                                        )}
                                        {!dateStr && <span className="text-[8px] font-black text-gray-300 uppercase italic mb-0.5">VS</span>}
                                        <span className="text-base md:text-xl font-black text-gray-900 tracking-tighter bg-white px-2 py-0.5 rounded-lg border border-gray-100 shadow-sm group-hover:bg-yellow-50 group-hover:border-yellow-200 transition-colors tabular-nums min-w-[55px] text-center">
                                            {result.score}
                                        </span>
                                    </div>
                                    <div className="flex flex-col items-center flex-1 min-w-0">
                                        <span className="text-base md:text-lg mb-0.5 shrink-0">{result.away_flag}</span>
                                        <span className="text-[9px] md:text-[10px] font-black text-gray-900 text-center leading-tight truncate w-full">{result.away}</span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
};

export default StandingsTable;
