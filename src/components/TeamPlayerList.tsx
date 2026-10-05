import React, { useState, useMemo, useCallback } from 'react';
import { calcAge } from '../lib/age';

interface Player {
    slug: string;
    href?: string | null; // 個別ページがある選手のみ（無ければ名前はリンクにしない）
    data: {
        title: string;
        name_en: string;
        position: string;
        team: string;
        age: number | null;
        birth_date: string;
        height: string;
        weight: string;
        caps: string;
        league_one_caps: string;
        category: string;
        league: string;
        country?: string;
        division: string;
        high_school?: string;
        university?: string;
        joined_year?: number | null;
    };
}

interface Props {
    players: Player[];
    isLeagueOne?: boolean;
}

const TeamPlayerList: React.FC<Props> = ({ players: rawPlayers, isLeagueOne = false }) => {
    // age 固定値は使わず birth_date から閲覧日基準で計算（docs/adsense/01_DESIGN.md §3）
    const players = useMemo(
        () => rawPlayers.map(p => ({ ...p, data: { ...p.data, age: calcAge(p.data.birth_date) } })),
        [rawPlayers],
    );

    const [cartSlugs, setCartSlugs] = useState<Set<string>>(() => {
        try {
            const cart: {slug: string}[] = JSON.parse(localStorage.getItem('rugby_draft_cart') || '[]');
            return new Set(cart.map(p => p.slug));
        } catch { return new Set(); }
    });

    const addToCart = useCallback((e: React.MouseEvent, player: Player) => {
        e.preventDefault();
        e.stopPropagation();
        try {
            const cart: {slug: string; name: string; name_en?: string; position?: string; team?: string; country?: string}[] =
                JSON.parse(localStorage.getItem('rugby_draft_cart') || '[]');
            if (!cart.some(p => p.slug === player.slug)) {
                cart.push({
                    slug: player.slug,
                    name: player.data.title,
                    name_en: player.data.name_en,
                    position: player.data.position,
                    team: player.data.team,
                    country: player.data.country,
                });
                localStorage.setItem('rugby_draft_cart', JSON.stringify(cart));
            }
            setCartSlugs(prev => new Set([...prev, player.slug]));
        } catch {}
    }, []);

    const [sortKey, setSortKey] = useState<string>('position');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedPosition, setSelectedPosition] = useState<string>('');

    const POSITIONS = ['PR', 'HO', 'LO', 'FL', 'No8', 'SH', 'SO', 'CTB', 'WTB', 'FB'];

    const filteredAndSortedPlayers = useMemo(() => {
        // 1. フィルタリング
        let result = players.filter((p) => {
            const searchLower = searchTerm.toLowerCase();
            const searchNoSpace = searchLower.replace(/\s+/g, '');
            const titleLower = p.data.title.toLowerCase();
            const nameEnLower = (p.data.name_en?.toLowerCase() || '');
            const matchSearch = searchTerm === '' ||
                titleLower.includes(searchLower) ||
                titleLower.replace(/\s+/g, '').includes(searchNoSpace) ||
                nameEnLower.includes(searchLower) ||
                nameEnLower.replace(/\s+/g, '').includes(searchNoSpace) ||
                (p.data.position?.toLowerCase() || '').includes(searchLower) ||
                (p.data.high_school?.toLowerCase() || '').includes(searchLower) ||
                (p.data.university?.toLowerCase() || '').includes(searchLower);

            const matchPosition = selectedPosition === '' || 
                (p.data.position || '').split(/[/／・\s]+/).some(pos => pos.trim() === selectedPosition);

            return matchSearch && matchPosition;
        });

        // 2. ソート
        const posOrder: Record<string, number> = {
            'PR': 1, 'HO': 2, 'LO': 3, 'FL': 4, 'No8': 5,
            'SH': 6, 'SO': 7, 'CTB': 8, 'WTB': 9, 'FB': 10
        };

        result.sort((a, b) => {
            let valA: any;
            let valB: any;

            switch (sortKey) {
                case 'position':
                    valA = posOrder[a.data.position] || 99;
                    valB = posOrder[b.data.position] || 99;
                    break;
                case 'age':
                    valA = a.data.age ?? 999;
                    valB = b.data.age ?? 999;
                    break;
                case 'height':
                    valA = parseFloat(a.data.height) || 0;
                    valB = parseFloat(b.data.height) || 0;
                    break;
                case 'weight':
                    valA = parseFloat(a.data.weight) || 0;
                    valB = parseFloat(b.data.weight) || 0;
                    break;
                case 'high_school':
                    valA = a.data.high_school || 'ー';
                    valB = b.data.high_school || 'ー';
                    break;
                case 'university':
                    valA = a.data.university || 'ー';
                    valB = b.data.university || 'ー';
                    break;
                case 'joined_year':
                    valA = a.data.joined_year ?? 9999;
                    valB = b.data.joined_year ?? 9999;
                    break;
                default:
                    valA = a.data.title;
                    valB = b.data.title;
            }

            if (valA === valB) {
                const pA = posOrder[a.data.position] || 99;
                const pB = posOrder[b.data.position] || 99;
                if (pA !== pB) return pA - pB;
                return a.data.title.localeCompare(b.data.title, 'ja');
            };

            const order = sortOrder === 'asc' ? 1 : -1;
            return (valA > valB ? 1 : -1) * order;
        });

        return result;
    }, [players, sortKey, sortOrder, searchTerm, selectedPosition]);

    const toggleSort = (key: string) => {
        if (sortKey === key) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(key);
            setSortOrder(key === 'joined_year' || key === 'age' ? 'asc' : (key === 'height' || key === 'weight' ? 'desc' : 'asc'));
        }
    };

    const sortButtons = [
        { key: 'position', label: 'ポジション' },
        { key: 'age', label: '年齢' },
        { key: 'height', label: '身長' },
        { key: 'weight', label: '体重' },
        { key: 'high_school', label: '高校' },
        { key: 'university', label: '大学' },
        { key: 'joined_year', label: '入部順' },
    ];

    return (
        <div className="space-y-12">
            {/* 検索 & フィルタ UI */}
            <div className="bg-card p-6 md:p-8 rounded-[2rem] border border-border-dim shadow-xl space-y-8">
                {/* キーワード検索 */}
                <div>
                    <label className="block text-[10px] font-black text-foreground/40 uppercase tracking-[0.2em] mb-3 ml-1">
                        Search Players
                    </label>
                    <div className="relative group">
                        <input
                            type="text"
                            aria-label="名前・学校名・ポジションで選手を検索"
                            placeholder="名前、学校名、ポジションなどで検索..."
                            className="w-full p-5 bg-background border-2 border-transparent rounded-2xl focus:border-yellow-400/50 outline-none transition-all font-bold text-lg text-foreground shadow-sm group-hover:shadow-md"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                        <div className="absolute right-5 top-1/2 -translate-y-1/2 text-foreground/20 group-focus-within:text-yellow-400 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </div>
                    </div>
                </div>

                {/* ポジション・ソートのコンビネーション */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                    {/* ポジション選択 */}
                    <div className="space-y-3">
                        <label className="block text-[10px] font-black text-foreground/40 uppercase tracking-[0.2em] ml-1">
                            Filter by Position
                        </label>
                        <div className="flex flex-wrap gap-2">
                            <button
                                onClick={() => setSelectedPosition('')}
                                className={`px-4 py-2 rounded-xl font-black text-xs transition-all border-2 ${selectedPosition === ''
                                    ? 'bg-foreground border-foreground text-background scale-105 shadow-lg'
                                    : 'bg-background border-transparent text-foreground/40 hover:bg-border-dim hover:text-foreground'
                                    }`}
                            >
                                ALL
                            </button>
                            {POSITIONS.map(pos => (
                                <button
                                    key={pos}
                                    onClick={() => setSelectedPosition(pos === selectedPosition ? '' : pos)}
                                    className={`px-4 py-2 rounded-xl font-black text-xs transition-all border-2 ${selectedPosition === pos
                                        ? 'bg-yellow-400 border-yellow-400 text-black scale-105 shadow-lg'
                                        : 'bg-background border-transparent text-foreground/40 hover:bg-border-dim hover:text-foreground'
                                        }`}
                                >
                                    {pos}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* ソートボタン */}
                    <div className="space-y-3">
                        <label className="block text-[10px] font-black text-foreground/40 uppercase tracking-[0.2em] ml-1">
                            Sort By
                        </label>
                        <div className="flex flex-wrap gap-2">
                            {sortButtons.map((btn) => (
                                <button
                                    key={btn.key}
                                    onClick={() => toggleSort(btn.key)}
                                    className={`px-4 py-2 rounded-xl font-black text-xs transition-all border-2 ${sortKey === btn.key
                                        ? 'bg-indigo-500 border-indigo-500 text-white scale-105 shadow-lg shadow-indigo-500/20'
                                        : 'bg-background border-transparent text-foreground/40 hover:bg-border-dim hover:text-foreground'
                                        }`}
                                >
                                    {btn.label} {sortKey === btn.key && (sortOrder === 'asc' ? '↑' : '↓')}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* 検索結果件数 */}
                {searchTerm || selectedPosition ? (
                    <div className="pt-4 border-t border-border-dim flex items-center justify-between text-xs font-black italic">
                        <span className="text-foreground/40 uppercase tracking-widest">Search Results</span>
                        <span className="text-foreground">
                            <span className="text-yellow-500 text-lg mr-1">{filteredAndSortedPlayers.length}</span> players found
                        </span>
                    </div>
                ) : null}
            </div>

            {/* 選手名簿（表形式。各行は #p-{slug} アンカー。個別ページがある選手のみ名前がリンク） */}
            <div className="overflow-x-auto bg-card rounded-3xl border border-border-dim shadow-sm">
                <table className="w-full text-left text-sm">
                    <thead>
                        <tr className="border-b border-border-dim text-[10px] font-black uppercase tracking-widest text-foreground/40">
                            <th className="px-4 py-3">名前</th>
                            <th className="px-4 py-3">ポジション</th>
                            <th className="px-4 py-3">出身校</th>
                            <th className="px-4 py-3 text-right">年齢</th>
                            <th className="px-2 py-3 w-10"><span className="sr-only">ドリームチーム</span></th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredAndSortedPlayers.length > 0 ? (
                            filteredAndSortedPlayers.map((player) => {
                                const d = player.data;
                                const isJaName = /[\u3040-\u30FF\u4E00-\u9FFF]/.test(d.title || '');
                                const mainName = d.title.includes('|') ? d.title.split('|')[1].trim() : d.title;
                                const subName = isJaName && d.name_en && d.name_en !== mainName ? d.name_en : '';
                                const school = [d.high_school, d.university].filter(Boolean).join(' → ');
                                return (
                                    <tr
                                        key={player.slug}
                                        id={`p-${player.slug}`}
                                        className="scroll-mt-28 border-b border-border-dim/50 last:border-0 target:bg-yellow-400/10 hover:bg-background/60 transition-colors"
                                    >
                                        <td className="px-4 py-3">
                                            {player.href ? (
                                                <a href={player.href} className="font-black text-foreground hover:text-yellow-600 transition-colors">
                                                    {mainName}
                                                </a>
                                            ) : (
                                                <span className="font-black text-foreground">{mainName}</span>
                                            )}
                                            {subName && (
                                                <span className="block text-[10px] font-bold text-foreground/40 uppercase tracking-tight">{subName}</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 font-bold text-foreground/70 whitespace-nowrap">{d.position || '—'}</td>
                                        <td className="px-4 py-3 font-bold text-foreground/70">{school || '—'}</td>
                                        <td className="px-4 py-3 text-right font-black text-foreground whitespace-nowrap">
                                            {d.age != null ? <>{d.age}<span className="text-[10px] ml-0.5 font-bold text-foreground/40">歳</span></> : '—'}
                                        </td>
                                        <td className="px-2 py-3 text-center">
                                            <button
                                                type="button"
                                                onClick={e => addToCart(e, player)}
                                                title={cartSlugs.has(player.slug) ? 'ドリームチームに追加済み' : 'ドリームチームに追加'}
                                                className={`text-base leading-none transition-colors ${cartSlugs.has(player.slug) ? 'text-yellow-500' : 'text-foreground/20 hover:text-yellow-500'}`}
                                            >
                                                {cartSlugs.has(player.slug) ? '★' : '☆'}
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })
                        ) : (
                            <tr>
                                <td colSpan={5} className="py-16 text-center">
                                    <p className="text-foreground/40 font-black italic uppercase tracking-widest mb-2">No Players Match Your Search</p>
                                    <p className="text-yellow-500 font-bold">検索条件を変えてお試しください</p>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TeamPlayerList;
