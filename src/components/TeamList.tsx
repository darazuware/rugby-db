import React, { useState, useMemo } from 'react';

interface Team {
    team_name: string;
    team_name_jp?: string;
    flag?: string;
    team_en_name?: string;
    slug: string;
    league: string;
    division?: string;
    host_area?: string;
    legal_entity?: string;
}

interface Props {
    initialTeams: Team[];
    leagueContext?: string;
}

const LEAGUES = [
    { id: 'all', name: 'ALL' },
    { id: 'league-one', name: 'LEAGUE ONE' },
    { id: 'super-rugby', name: 'SUPER RUGBY' },
    { id: 'top14', name: 'TOP 14' },
    { id: 'urc', name: 'URC' }
];

const DIVISIONS = [
    { id: 'all', name: 'ALL' },
    { id: 'Division 1', name: 'D1' },
    { id: 'Division 2', name: 'D2' },
    { id: 'Division 3', name: 'D3' }
];

const TeamList: React.FC<Props> = ({ initialTeams, leagueContext }) => {
    const [selectedLeague, setSelectedLeague] = useState(leagueContext || 'all');
    const [selectedDivision, setSelectedDivision] = useState('all');
    const [search, setSearch] = useState('');

    // UIテーマ設定の取得
    const theme = useMemo(() => {
        const themeLeague = leagueContext === 'league-one' ? 'league-one' : selectedLeague;
        switch (themeLeague) {
            case 'league-one':
                return {
                    accent: 'bg-[#E60012]',
                    textAccent: 'text-[#E60012]',
                    border: 'border-[#E60012]',
                    focus: 'focus:border-[#E60012]',
                    shadow: 'shadow-[#E60012]/20'
                };
            case 'top14':
                return {
                    accent: 'bg-[#C5A059]',
                    textAccent: 'text-[#C5A059]',
                    border: 'border-[#C5A059]',
                    focus: 'focus:border-[#C5A059]',
                    shadow: 'shadow-[#C5A059]/20'
                };
            case 'super-rugby':
                return {
                    accent: 'bg-[#0055A4]',
                    textAccent: 'text-[#0055A4]',
                    border: 'border-[#0055A4]',
                    focus: 'focus:border-[#0055A4]',
                    shadow: 'shadow-[#0055A4]/20'
                };
            case 'urc':
                return {
                    accent: 'bg-[#003366]',
                    textAccent: 'text-[#003366]',
                    border: 'border-[#003366]',
                    focus: 'focus:border-[#003366]',
                    shadow: 'shadow-[#003366]/20'
                };
            default:
                return {
                    accent: 'bg-yellow-400',
                    textAccent: 'text-yellow-400',
                    border: 'border-yellow-400',
                    focus: 'focus:border-yellow-400',
                    shadow: 'shadow-yellow-200'
                };
        }
    }, [selectedLeague, leagueContext]);

    const getLeagueColor = (league: string) => {
        switch (league) {
            case 'league-one': return 'bg-[#E60012]';
            case 'top14': return 'bg-[#C5A059]';
            case 'super-rugby': return 'bg-[#0055A4]';
            case 'urc': return 'bg-[#003366]';
            default: return 'bg-yellow-400';
        }
    };

    const filteredTeams = useMemo(() => {
        return initialTeams.filter(team => {
            const matchLeague = selectedLeague === 'all' || team.league === selectedLeague;
            const matchDivision = selectedDivision === 'all' || team.division === selectedDivision;
            const matchSearch =
                team.team_name.toLowerCase().includes(search.toLowerCase()) ||
                (team.team_name_jp?.toLowerCase() ?? '').includes(search.toLowerCase()) ||
                (team.team_en_name?.toLowerCase() ?? '').includes(search.toLowerCase());
            return matchLeague && matchDivision && matchSearch;
        });
    }, [initialTeams, selectedLeague, selectedDivision, search]);

    const groupedTeams = useMemo(() => {
        const groups: { [key: string]: Team[] } = {};

        filteredTeams.forEach(team => {
            const div = team.division || (
                team.league === 'league-one' ? 'League One' :
                    team.league === 'top14' ? 'Top 14' :
                        team.league === 'super-rugby' ? 'Super Rugby' :
                            team.league === 'urc' ? 'URC' :
                                team.league.replace('-', ' ')
            );
            if (!groups[div]) groups[div] = [];
            groups[div].push(team);
        });

        return Object.entries(groups).sort(([a], [b]) => {
            if (a.includes('1') || a.includes('D1')) return -1;
            if (b.includes('1') || b.includes('D1')) return 1;
            return a.localeCompare(b);
        });
    }, [filteredTeams]);

    return (
        <div className="space-y-12">
            <div className="bg-card p-6 rounded-3xl shadow-xl border border-border-dim space-y-6">
                {/* 検索 */}
                <div>
                    <label className="block text-xs font-black text-foreground/40 uppercase tracking-widest mb-2">チーム検索</label>
                    <input
                        type="text"
                        placeholder="チーム名（日本語・英語）で検索..."
                        className={`w-full p-4 bg-background border-2 border-transparent rounded-2xl focus:bg-card ${theme.focus} outline-none transition-all font-bold text-foreground`}
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>

                {/* フィルター */}
                {leagueContext === 'league-one' ? (
                    <div>
                        <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">ディビジョンで絞り込む</label>
                        <div className="flex flex-wrap gap-2">
                            {DIVISIONS.map(div => (
                                <button
                                    key={div.id}
                                    onClick={() => setSelectedDivision(div.id)}
                                    className={`px-4 py-2 rounded-xl font-black text-xs transition-all border-2 ${selectedDivision === div.id
                                        ? `${theme.accent} ${theme.border} text-white scale-105 shadow-md ${theme.shadow}`
                                        : 'bg-card border-border-dim text-foreground/40 hover:border-border-dim/80'
                                        }`}
                                >
                                    {div.name}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : !leagueContext && (
                    <div>
                        <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">リーグで絞り込む</label>
                        <div className="flex flex-wrap gap-2">
                            {LEAGUES.map(league => (
                                <button
                                    key={league.id}
                                    onClick={() => setSelectedLeague(league.id)}
                                    className={`px-4 py-2 rounded-xl font-black text-xs transition-all border-2 ${selectedLeague === league.id
                                        ? `${theme.accent} ${theme.border} text-white scale-105 shadow-md ${theme.shadow}`
                                        : 'bg-card border-border-dim text-foreground/40 hover:border-border-dim/80'
                                        }`}
                                >
                                    {league.name}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {groupedTeams.length > 0 ? (
                groupedTeams.map(([division, teams]) => (
                    <div key={division} className="space-y-6">
                        <div className="flex items-center gap-3">
                            <span className={`w-2 h-8 ${getLeagueColor(teams[0].league)} rounded-full transition-colors`}></span>
                            <h2 className="text-xl font-black text-foreground uppercase tracking-tighter italic">
                                {division}
                            </h2>
                            <span className="text-xs font-bold text-foreground/40 bg-background px-2 py-0.5 rounded-full">
                                {teams.length} チーム
                            </span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {teams.map((team) => {
                                const leagueColor = getLeagueColor(team.league);
                                return (
                                    <a
                                        key={`${team.league}-${team.slug}`}
                                        href={`/teams/${team.league}/${team.slug}`}
                                        className="group block bg-card rounded-3xl p-6 shadow-sm hover:shadow-2xl hover:-translate-y-1 transition-all border border-border-dim relative overflow-hidden h-full flex flex-col"
                                    >
                                        <div className="relative z-20 flex-grow">

                                            <h3 className="text-xl font-black text-foreground mb-2 group-hover:text-yellow-600 transition-colors leading-tight flex items-start flex-wrap gap-2">
                                            {(team.flag || (team.league !== 'league-one' && team.legal_entity)) && (
                                                <div className="flex items-center gap-1.5 bg-background px-2 py-0.5 rounded-lg text-xs font-black text-foreground/40 mb-1">
                                                    {team.flag && <span className="text-base">{team.flag}</span>}
                                                    {team.league !== 'league-one' && team.legal_entity && <span>{team.legal_entity}</span>}
                                                </div>
                                            )}
                                                <div className="w-full">
                                                    {team.league === 'league-one' ? (
                                                        team.team_name_jp || team.team_name
                                                    ) : (
                                                        <span className="uppercase">{team.team_en_name || team.team_name}</span>
                                                    )}
                                                </div>
                                            </h3>
                                            {team.league === 'league-one' ? (
                                                (team.team_en_name && team.team_en_name !== (team.team_name_jp || team.team_name)) && (
                                                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-4 italic break-all">
                                                        {team.team_en_name}
                                                    </p>
                                                )
                                            ) : (
                                                (team.team_name_jp || team.team_name) && (team.team_name_jp || team.team_name) !== (team.team_en_name || team.team_name) && (
                                                    <p className="text-[11px] font-bold text-gray-400 mb-4 italic tracking-tight uppercase">
                                                        {team.team_name_jp || team.team_name}
                                                    </p>
                                                )
                                            )}

                                            {team.host_area && (
                                                <div className="flex items-center gap-2 mt-auto">
                                                    <span className={`text-[10px] font-black ${leagueColor} text-white px-2 py-0.5 rounded uppercase tracking-tighter`}>
                                                        Host
                                                    </span>
                                                    <span className="text-xs font-bold text-gray-700">
                                                        {team.host_area}
                                                    </span>
                                                </div>
                                            )}
                                        </div>

                                        <div className="mt-6 pt-4 border-t border-border-dim flex justify-between items-center text-xs font-black text-foreground/40 uppercase tracking-widest group-hover:text-foreground transition-colors">
                                            <span>選手一覧を見る</span>
                                            <span>→</span>
                                        </div>
                                    </a>
                                );
                            })}
                        </div>
                    </div>
                ))
            ) : (
                <div className="text-center py-20 text-foreground/40 font-bold italic bg-card rounded-3xl border-2 border-dashed border-border-dim">
                    一致するチームが見つかりません。
                </div>
            )}
        </div>
    );
};

export default TeamList;
