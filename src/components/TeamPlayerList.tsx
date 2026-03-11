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

    const sortedPlayers = useMemo(() => {
        const result = [...players];

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
                // 同じ値の場合はポジション順、名前順でタイブレイク
                const pA = posOrder[a.data.position] || 99;
                const pB = posOrder[b.data.position] || 99;
                if (pA !== pB) return pA - pB;
                return a.data.title.localeCompare(b.data.title, 'ja');
            };

            const order = sortOrder === 'asc' ? 1 : -1;
            return (valA > valB ? 1 : -1) * order;
        });

        return result;
    }, [players, sortKey, sortOrder]);

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
        <div className="space-y-8">
            {/* ソートボタン */}
            <div className="flex flex-wrap items-center gap-3 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
                <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mr-2">Sort By</span>
                {sortButtons.map((btn) => (
                    <button
                        key={btn.key}
                        onClick={() => toggleSort(btn.key)}
                        className={`px-4 py-2 rounded-xl font-black text-xs transition-all border-2 ${sortKey === btn.key
                            ? 'bg-yellow-400 border-yellow-400 text-black scale-105 shadow-md shadow-yellow-100'
                            : 'bg-gray-50 border-transparent text-gray-500 hover:bg-gray-100 hover:text-gray-900'
                            }`}
                    >
                        {btn.label} {sortKey === btn.key && (sortOrder === 'asc' ? '↑' : '↓')}
                    </button>
                ))}
            </div>

            {/* 選手リスト（PlayerList.tsx のカードスタイルを継承） */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                {sortedPlayers.map((player) => (
                    <a
                        key={player.slug}
                        href={`/players/${player.slug}/`}
                        className="group block bg-white rounded-3xl p-6 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all border border-gray-50 relative overflow-hidden"
                    >
                        {/* デコレーション */}
                        <div className="absolute top-0 right-0 w-16 h-16 translate-x-8 -translate-y-8 rotate-45 bg-yellow-400 z-10"></div>

                        <div className="mb-6 relative z-10">
                            <div className="flex flex-col gap-1 mb-3">
                                <div className="flex justify-between items-start">
                                    <span className="inline-block px-3 py-1 bg-gray-900 text-white text-[10px] font-black rounded-lg tracking-tighter">
                                        {player.data.position}
                                    </span>
                                </div>
                                {(player.data.league === 'league-one' || player.data.league === 'leagueone') && (
                                    <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest">{player.data.category}</span>
                                )}
                            </div>
                            {(() => {
                                const isItemLeagueOne = player.data.league === 'league-one' || player.data.league === 'leagueone';
                                const mainName = isItemLeagueOne ? player.data.title : (player.data.name_en || player.data.title);
                                const subName = isItemLeagueOne ? (player.data.name_en || player.data.title) : player.data.title;
                                const showSub = subName && subName !== mainName;

                                return (
                                    <>
                                        <h2 className={`text-2xl font-black text-gray-900 mb-3 leading-tight group-hover:text-yellow-600 transition-colors tracking-tighter ${!isItemLeagueOne ? 'uppercase' : ''}`}>
                                            {mainName}
                                        </h2>
                                        {showSub && (
                                            <p className="text-[12px] font-bold text-gray-400 mb-4 italic tracking-tight uppercase">
                                                {subName}
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
                                        <p className="text-xs font-black text-gray-600 uppercase tracking-tighter mb-5 leading-tight">
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
                                <div className="mt-3 text-[10px] font-black text-gray-400 uppercase tracking-widest">
                                    JOINED: {player.data.joined_year}
                                </div>
                            )}
                        </div>

                        <div className="flex justify-between items-end text-xs font-black text-gray-900 border-t border-gray-100 pt-4 uppercase tracking-tighter mt-auto">
                            <div className="flex flex-col">
                                <span className="text-[18px] leading-none">{player.data.age}<span className="text-[10px] ml-0.5 font-bold">歳</span></span>
                            </div>
                            <div className="flex flex-col text-right">
                                <span className="text-[15px] leading-none">{player.data.height}<span className="text-[9px] text-gray-400 font-bold mx-0.5">cm</span> / {player.data.weight}<span className="text-[9px] text-gray-400 font-bold ml-0.5">kg</span></span>
                            </div>
                        </div>
                    </a>
                ))}
            </div>
        </div>
    );
};

export default TeamPlayerList;
