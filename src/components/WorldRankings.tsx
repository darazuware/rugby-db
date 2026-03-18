import React, { useState } from 'react';

interface RankingEntry {
    rank: number;
    previousRank: number;
    points: number;
    team_en: string;
    team_jp: string;
    abbreviation: string;
    flag: string;
}

interface Props {
    mens: RankingEntry[];
    womens: RankingEntry[];
    updatedAt: string;
}

const WorldRankings: React.FC<Props> = ({ mens, womens, updatedAt }) => {
    const [category, setCategory] = useState<'mens' | 'womens'>('mens');
    const data = category === 'mens' ? mens : womens;

    return (
        <div className="w-full">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
                <div className="flex bg-card/50 backdrop-blur-xl border border-border-dim p-1.5 rounded-2xl w-fit shadow-2xl">
                    <button
                        onClick={() => setCategory('mens')}
                        className={`px-8 py-3 rounded-xl font-black text-xs uppercase tracking-widest transition-all ${
                            category === 'mens' 
                            ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20' 
                            : 'text-foreground/40 hover:text-foreground hover:bg-white/5'
                        }`}
                    >
                        Men's
                    </button>
                    <button
                        onClick={() => setCategory('womens')}
                        className={`px-8 py-3 rounded-xl font-black text-xs uppercase tracking-widest transition-all ${
                            category === 'womens' 
                            ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20' 
                            : 'text-foreground/40 hover:text-foreground hover:bg-white/5'
                        }`}
                    >
                        Women's
                    </button>
                </div>
                
                <div className="flex items-center gap-3 text-[10px] font-black uppercase tracking-[0.2em] text-foreground/30 bg-card/30 px-4 py-2 rounded-full border border-border-dim w-fit">
                    <span className="w-1.5 h-1.5 bg-yellow-400 rounded-full animate-pulse"></span>
                    Last Updated: {updatedAt}
                </div>
            </div>

            <div className="bg-card/30 backdrop-blur-xl border border-border-dim rounded-[2.5rem] overflow-hidden shadow-2xl relative">
                {/* Decorative gradients */}
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-yellow-400/30 to-transparent"></div>
                
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse min-w-[800px]">
                        <thead>
                            <tr className="border-b border-border-dim bg-foreground/[0.02]">
                                <th className="px-8 py-8 text-[11px] font-black uppercase tracking-[0.2em] text-foreground/40 text-center w-24">Rank</th>
                                <th className="px-8 py-8 text-[11px] font-black uppercase tracking-[0.2em] text-foreground/40">Country / Team</th>
                                <th className="px-8 py-8 text-[11px] font-black uppercase tracking-[0.2em] text-foreground/40 text-right">Points</th>
                                <th className="px-8 py-8 text-[11px] font-black uppercase tracking-[0.2em] text-foreground/40 text-center w-32">Movement</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border-dim/50">
                            {data.map((entry) => (
                                <tr key={entry.team_en} className="group hover:bg-foreground/[0.03] transition-all duration-300">
                                    <td className="px-8 py-8">
                                        <div className="flex flex-col items-center justify-center">
                                            <span className={`text-3xl font-black italic tracking-tighter leading-none ${
                                                entry.rank <= 3 ? 'text-yellow-400 drop-shadow-[0_0_15px_rgba(250,204,21,0.3)]' : 'text-foreground'
                                            }`}>
                                                {entry.rank}
                                            </span>
                                            {entry.rank <= 3 && (
                                                <div className="w-1 h-1 bg-yellow-400 rounded-full mt-2"></div>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-8 py-8">
                                        <div className="flex items-center gap-6">
                                            <span className="text-5xl drop-shadow-lg grayscale-[0.2] group-hover:grayscale-0 transition-all duration-500 scale-100 group-hover:scale-110">
                                                {entry.flag || '🏳️'}
                                            </span>
                                            <div className="flex flex-col">
                                                <span className="text-2xl font-black tracking-tight text-foreground uppercase group-hover:text-yellow-400 transition-colors">
                                                    {entry.team_en}
                                                </span>
                                                <span className="text-xs font-bold text-foreground/40 mt-1 flex items-center gap-2">
                                                    {entry.team_jp}
                                                    <span className="w-1 h-1 bg-border-dim rounded-full"></span>
                                                    {entry.abbreviation}
                                                </span>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-8 py-8 text-right">
                                        <div className="flex flex-col items-end">
                                            <span className="text-2xl font-black italic tracking-tighter text-foreground tabular-nums">
                                                {entry.points.toFixed(2)}
                                            </span>
                                            <span className="text-[10px] font-black text-foreground/20 uppercase tracking-widest mt-1">Rating pts</span>
                                        </div>
                                    </td>
                                    <td className="px-8 py-8">
                                        <div className="flex items-center justify-center">
                                            {entry.rank < entry.previousRank ? (
                                                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/10 text-green-500 rounded-full border border-green-500/20">
                                                    <svg className="w-3 h-3 fill-current mt-0.5" viewBox="0 0 24 24"><path d="M12 4l-8 8h16l-8-8z"/></svg>
                                                    <span className="text-[11px] font-black">{entry.previousRank - entry.rank}</span>
                                                </div>
                                            ) : entry.rank > entry.previousRank ? (
                                                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/10 text-red-500 rounded-full border border-red-500/20">
                                                    <svg className="w-3 h-3 fill-current" viewBox="0 0 24 24"><path d="M12 20l8-8H4l8 8z"/></svg>
                                                    <span className="text-[11px] font-black">{entry.rank - entry.previousRank}</span>
                                                </div>
                                            ) : (
                                                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-foreground/5 text-foreground/30 rounded-full border border-border-dim">
                                                    <div className="w-2 h-0.5 bg-current rounded-full"></div>
                                                    <span className="text-[11px] font-black">Stable</span>
                                                </div>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <p className="mt-8 text-center text-[10px] font-bold text-foreground/20 uppercase tracking-[0.3em] italic">
                Data provided by World Rugby official rankings
            </p>
        </div>
    );
};

export default WorldRankings;
