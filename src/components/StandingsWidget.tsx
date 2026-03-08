import React from 'react';

interface TeamStanding {
    rank: string;
    display_name: string;
    points: string;
    flag?: string;
    slug: string;
}

interface LeagueData {
    id: string;
    name: string;
    fullName: string;
    accentColor: string;
    teams: TeamStanding[];
}

interface Props {
    leagueStandings: LeagueData[];
}

const StandingsWidget: React.FC<Props> = ({ leagueStandings }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {leagueStandings.map((league) => (
                <div
                    key={league.id}
                    className="group relative bg-[#1a1a1a] border border-white/10 rounded-[2.5rem] overflow-hidden hover:border-white/20 transition-all duration-500 hover:shadow-2xl hover:shadow-black/60"
                >
                    {/* Top Accent Bar */}
                    <div className={`h-2 w-full ${league.accentColor}`}></div>

                    <div className="p-8">
                        <div className="flex justify-between items-start mb-8">
                            <div>
                                <h3 className="text-3xl font-black italic tracking-tighter text-white leading-none mb-2 uppercase">
                                    {league.name}
                                </h3>
                                <span className="text-[11px] font-black text-gray-400 uppercase tracking-[0.25em]">
                                    STANDINGS TOP 3
                                </span>
                            </div>
                            <div className={`p-2.5 rounded-2xl bg-white/5 border border-white/10 ${league.accentColor.replace('bg-', 'text-')}`}>
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                            </div>
                        </div>

                        <div className="space-y-4">
                            {league.teams.slice(0, 3).map((team, idx) => (
                                <a
                                    key={team.slug || team.display_name}
                                    href={`/teams/${league.id}`}
                                    className="flex items-center justify-between p-4 rounded-3xl bg-white/[0.04] border border-white/[0.05] hover:bg-white/[0.08] hover:border-white/10 transition-all group/item shadow-sm"
                                >
                                    <div className="flex items-center gap-4">
                                        <span className={`w-8 h-8 flex items-center justify-center rounded-xl font-black text-sm ${idx === 0 ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20' : 'bg-white/10 text-gray-300'
                                            }`}>
                                            {idx + 1}
                                        </span>
                                        <div className="flex flex-col">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-xl leading-none">{team.flag || '🇯🇵'}</span>
                                                <span className="text-base font-black text-white tracking-tight leading-tight">
                                                    {team.display_name}
                                                </span>
                                            </div>
                                            <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">
                                                {league.fullName.split(' ')[0]} CLUB
                                            </span>
                                        </div>
                                    </div>
                                    <div className="text-right ml-4">
                                        <span className="block text-[10px] font-black text-gray-500 uppercase leading-none mb-1">PTS</span>
                                        <span className="text-2xl font-black text-white italic tracking-tighter tabular-nums leading-none">
                                            {team.points && team.points !== '0' ? team.points : '-'}
                                        </span>
                                    </div>
                                </a>
                            ))}
                        </div>

                        <a
                            href={`/teams/${league.id}`}
                            className="mt-8 w-full py-4 rounded-3xl bg-white/5 border border-white/10 text-white font-black text-xs uppercase tracking-widest hover:bg-yellow-400 hover:text-black hover:border-yellow-400 transition-all flex items-center justify-center gap-3 active:scale-95 shadow-lg"
                        >
                            View Full Standings
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M9 5l7 7-7 7" />
                            </svg>
                        </a>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default StandingsWidget;
