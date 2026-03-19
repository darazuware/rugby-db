import React, { useState, useMemo } from 'react';

interface Player {
    slug: string;
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

const FLAG_MAP: Record<string, string> = {
    '日本': '🇯🇵',
    'オーストラリア': '🇦🇺',
    'AUS': '🇦🇺',
    'ニュージーランド': '🇳🇿',
    'NZ': '🇳🇿',
    '南アフリカ': '🇿🇦',
    'SA': '🇿🇦',
    'フィジー': '🇫🇯',
    'FIJ': '🇫🇯',
    'トンガ': '🇹🇴',
    'TGA': '🇹🇴',
    'サモア': '🇼🇸',
    'SAM': '🇼🇸',
    'フランス': '🇫🇷',
    'FRA': '🇫🇷',
    'イングランド': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
    'ENG': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
    'ウェールズ': '🏴󠁧󠁢󠁷󠁬󠁳󠁿',
    'WAL': '🏴󠁧󠁢󠁷󠁬󠁳󠁿',
    'スコットランド': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
    'SCO': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
    'アイルランド': '🇮🇪',
    'IRE': '🇮🇪',
    'イタリア': '🇮🇹',
    'ITA': '🇮🇹',
    'アルゼンチン': '🇦🇷',
    'ARG': '🇦🇷',
    'アメリカ': '🇺🇸',
    'USA': '🇺🇸',
    'カナダ': '🇨🇦',
    'CAN': '🇨🇦',
    'ジョージア': '🇬🇪',
    'GEO': '🇬🇪',
    'ウルグアイ': '🇺🇾',
    'URU': '🇺🇾',
    'ポルトガル': '🇵🇹',
    'POR': '🇵🇹',
    'ルーマニア': '🇷🇴',
    'ROU': '🇷🇴',
    'ナミビア': '🇳🇦',
    'NAM': '🇳🇦',
    'チリ': '🇨🇱',
    'CHL': '🇨🇱',
    '韓国': '🇰🇷',
    'KOR': '🇰🇷',
    '中国': '🇨🇳',
    'CHN': '🇨🇳',
    '香港': '🇭🇰',
    'HKG': '🇭🇰',
};

interface Props {
    players: Player[];
    isLeagueOne?: boolean;
}

const TeamPlayerList: React.FC<Props> = ({ players, isLeagueOne = false }) => {
    const [sortKey, setSortKey] = useState<string>('position');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedPosition, setSelectedPosition] = useState<string>('');

    const POSITIONS = ['PR', 'HO', 'LO', 'FL', 'No8', 'SH', 'SO', 'CTB', 'WTB', 'FB'];

    const filteredAndSortedPlayers = useMemo(() => {
        // 1. フィルタリング
        let result = players.filter((p) => {
            const searchLower = searchTerm.toLowerCase();
            const matchSearch = searchTerm === '' || 
                p.data.title.toLowerCase().includes(searchLower) ||
                (p.data.name_en?.toLowerCase() || '').includes(searchLower) ||
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

            {/* 選手リスト（PlayerList.tsx のカードスタイルを継承） */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                {filteredAndSortedPlayers.length > 0 ? (
                    filteredAndSortedPlayers.map((player) => (
                    <a
                        key={player.slug}
                        href={`/players/${player.slug}/`}
                        className="group block bg-card rounded-3xl p-6 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all border border-border-dim relative overflow-hidden"
                    >
                        {/* デコレーション */}
                        <div className="absolute top-0 right-0 w-16 h-16 translate-x-8 -translate-y-8 rotate-45 bg-yellow-400 z-10"></div>

                        <div className="mb-6 relative z-10">
                            <div className="flex flex-col gap-1 mb-3">
                                <div className="flex justify-between items-start">
                                    <span className="inline-block px-3 py-1 bg-foreground text-background text-[10px] font-black rounded-lg tracking-tighter">
                                        {player.data.position}
                                    </span>
                                </div>
                                {(player.data.league === 'league-one' || player.data.league === 'leagueone') && (
                                    <span className="text-[9px] font-black text-foreground/40 uppercase tracking-widest">{player.data.category}</span>
                                )}
                            </div>
                            {(() => {
                                const isItemLeagueOne = player.data.league === 'league-one' || player.data.league === 'leagueone';
                                const isItemJapanese = player.data.country === '日本';
                                const isItemForeign = player.data.country && player.data.country !== '日本';
                                
                                // 日本語を優先（メインに表示）するかどうかの判定
                                const prefersItemJapaneseMain = isItemJapanese || (!isItemForeign && isItemLeagueOne);

                                const itemMainName = prefersItemJapaneseMain ? player.data.title : (player.data.name_en || player.data.title);
                                const itemSubName = prefersItemJapaneseMain ? (player.data.name_en || player.data.title) : player.data.title;
                                const showItemSub = itemSubName && itemSubName !== itemMainName;

                                return (
                                    <>
                                        <h2 className={`text-2xl font-black text-foreground mb-3 leading-tight group-hover:text-yellow-600 transition-colors tracking-tighter ${!prefersItemJapaneseMain ? 'uppercase' : ''}`}>
                                            {prefersItemJapaneseMain ? itemMainName : itemMainName?.split(' ').join('  ')}
                                        </h2>
                                        {showItemSub && (
                                            <p className="text-[12px] font-bold text-foreground/40 mb-4 italic tracking-tight uppercase">
                                                {itemSubName}
                                            </p>
                                        )}
                                    </>
                                );
                            })()}

                            {/* 学歴 (League Oneのみ表示) */}
                            {(() => {
                                const isItemLeagueOne = player.data.league === 'league-one' || player.data.league === 'leagueone';
                                if (isItemLeagueOne && (player.data.high_school || player.data.university)) {
                                    return (
                                        <p className="text-xs font-black text-foreground/60 uppercase tracking-tighter mb-5 leading-tight">
                                            {player.data.high_school && <span>{player.data.high_school}</span>}
                                            {player.data.high_school && player.data.university && <span className="mx-1 text-yellow-500 font-bold">→</span>}
                                            {player.data.university && <span>{player.data.university}</span>}
                                        </p>
                                    );
                                }
                                return null;
                            })()}

                            {/* 代表歴 */}
                            {player.data.caps && (
                                <div className="inline-block px-3 py-1.5 bg-yellow-50 text-yellow-700 text-xs font-black rounded-md border border-yellow-100 italic">
                                    <span className="mr-1.5 not-italic text-base">
                                        {FLAG_MAP[player.data.country || ''] || (player.data.caps.includes('日本') ? '🇯🇵' : '')}
                                    </span>
                                    {player.data.caps}
                                </div>
                            )}

                            {/* 入部年を表示 (入部順ソート時などに有用) */}
                            {player.data.joined_year && (
                                <div className="mt-3 text-[10px] font-black text-foreground/40 uppercase tracking-widest">
                                    JOINED: {player.data.joined_year}
                                </div>
                            )}
                        </div>

                                    <div className="flex justify-between items-end text-xs font-black text-foreground border-t border-border-dim pt-4 uppercase tracking-tighter mt-auto">
                            <div className="flex flex-col">
                                <span className="text-[18px] leading-none">{player.data.age}<span className="text-[10px] ml-0.5 font-bold">歳</span></span>
                            </div>
                            <div className="flex flex-col text-right">
                                <span className="text-[15px] leading-none">{player.data.height}<span className="text-[10px] text-foreground/40 font-bold mx-0.5">cm</span> / {player.data.weight}<span className="text-[10px] text-foreground/40 font-bold ml-0.5">kg</span></span>
                            </div>
                        </div>
                    </a>
                ))
                ) : (
                    <div className="col-span-full py-20 text-center animate-in fade-in zoom-in duration-500">
                        <div className="inline-block p-6 bg-card rounded-[2rem] border border-border-dim border-dashed">
                            <p className="text-foreground/40 font-black italic uppercase tracking-widest mb-2">No Players Match Your Search</p>
                            <p className="text-yellow-500 font-bold">検索条件を変えてお試しください</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TeamPlayerList;
