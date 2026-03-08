import React, { useState, useMemo, useEffect } from 'react';

interface Player {
    slug: string;
    data: {
        title: string;
        name_en?: string;
        position?: string;
        team?: string;
        age?: number | null;
        birth_date?: string;
        height?: string;
        weight?: string;
        caps?: string;
        league_one_caps?: string;
        category?: string;
        country?: string;
        division?: string;
        league?: string;
        high_school?: string;
        university?: string;
        tries?: number;
        matches?: number;
        starts?: number;
        minutes?: number;
        has_scores?: boolean | string;
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
    initialPlayers: Player[];
    leagueContext?: string;
}

const POSITIONS = ['PR', 'HO', 'LO', 'FL', 'No8', 'SH', 'SO', 'WTB', 'CTB', 'FB'];
const DIVISIONS = ['Division 1', 'Division 2', 'Division 3'];
const CATEGORIES = ['カテゴリーA', 'カテゴリーB', 'カテゴリーC'];
const LEAGUES = [
    { id: 'league-one', name: 'LEAGUE ONE' },
    { id: 'super-rugby', name: 'SUPER RUGBY' },
    { id: 'top14', name: 'TOP 14' }
];

const PlayerList: React.FC<Props> = ({ initialPlayers, leagueContext }) => {
    const [search, setSearch] = useState('');
    const [selectedLeagues, setSelectedLeagues] = useState<string[]>(
        leagueContext ? [leagueContext] : []
    );
    const [selectedPositions, setSelectedPositions] = useState<string[]>([]);
    const [selectedDivisions, setSelectedDivisions] = useState<string[]>([]);
    const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
    const [selectedTeams, setSelectedTeams] = useState<string[]>([]);
    const [sortKey, setSortKey] = useState<'title' | 'age' | 'height' | 'weight' | 'tries' | 'matches' | 'starts' | 'minutes'>('title');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

    // リーグマッピングの生成
    const TEAM_LEAGUE_MAP = useMemo(() => {
        const map: Record<string, string> = {};
        initialPlayers.forEach(p => {
            if (p.data.team && p.data.league) {
                map[p.data.team] = p.data.league;
            }
        });
        return map;
    }, [initialPlayers]);

    // 全チームのリストを動的に生成
    const ALL_TEAMS = useMemo(() => {
        const teams = Array.from(new Set(initialPlayers.map(p => p.data.team).filter(Boolean))) as string[];
        return teams.sort();
    }, [initialPlayers]);

    // フィルタリングされたチームリスト
    const VISIBLE_TEAMS = useMemo(() => {
        if (selectedLeagues.length === 0) return ALL_TEAMS;
        return ALL_TEAMS.filter(team => {
            const league = TEAM_LEAGUE_MAP[team];
            return selectedLeagues.includes(league);
        });
    }, [ALL_TEAMS, selectedLeagues, TEAM_LEAGUE_MAP]);

    // UIテーマ設定の取得
    const theme = useMemo(() => {
        // 選択されたチームのリーグを判定してテーマを適用（最初の選択チームを優先）
        if (selectedTeams.length > 0) {
            const firstTeam = selectedTeams[0];
            const player = initialPlayers.find(p => p.data.team === firstTeam);
            const league = player?.data.league;

            switch (league) {
                case 'league-one':
                    return {
                        accent: 'bg-[#E60012]',
                        textAccent: 'text-[#E60012]',
                        border: 'border-[#E60012]',
                        focus: 'focus:border-[#E60012]',
                        shadow: 'shadow-[#E60012]/20',
                        decoration: 'decoration-[#E60012]',
                        hex: '#E60012'
                    };
                case 'top14':
                    return {
                        accent: 'bg-[#C5A059]',
                        textAccent: 'text-[#C5A059]',
                        border: 'border-[#C5A059]',
                        focus: 'focus:border-[#C5A059]',
                        shadow: 'shadow-[#C5A059]/20',
                        decoration: 'decoration-[#C5A059]',
                        hex: '#C5A059'
                    };
                case 'super-rugby':
                    return {
                        accent: 'bg-[#0055A4]',
                        textAccent: 'text-[#0055A4]',
                        border: 'border-[#0055A4]',
                        focus: 'focus:border-[#0055A4]',
                        shadow: 'shadow-[#0055A4]/20',
                        decoration: 'decoration-[#0055A4]',
                        hex: '#0055A4'
                    };
                case 'urc':
                    return {
                        accent: 'bg-[#003366]',
                        textAccent: 'text-[#003366]',
                        border: 'border-[#003366]',
                        focus: 'focus:border-[#003366]',
                        shadow: 'shadow-[#003366]/20',
                        decoration: 'decoration-[#003366]',
                        hex: '#003366'
                    };
            }
        }

        // 外部コンテキスト（leagueContext）がある場合のデフォルトテーマ
        if (leagueContext) {
            const contextLeague = leagueContext;
            switch (contextLeague) {
                case 'league-one':
                    return {
                        accent: 'bg-[#E60012]',
                        textAccent: 'text-[#E60012]',
                        border: 'border-[#E60012]',
                        focus: 'focus:border-[#E60012]',
                        shadow: 'shadow-[#E60012]/20',
                        decoration: 'decoration-[#E60012]',
                        hex: '#E60012'
                    };
                case 'top14':
                    return {
                        accent: 'bg-[#C5A059]',
                        textAccent: 'text-[#C5A059]',
                        border: 'border-[#C5A059]',
                        focus: 'focus:border-[#C5A059]',
                        shadow: 'shadow-[#C5A059]/20',
                        decoration: 'decoration-[#C5A059]',
                        hex: '#C5A059'
                    };
                case 'super-rugby':
                    return {
                        accent: 'bg-[#0055A4]',
                        textAccent: 'text-[#0055A4]',
                        border: 'border-[#0055A4]',
                        focus: 'focus:border-[#0055A4]',
                        shadow: 'shadow-[#0055A4]/20',
                        decoration: 'decoration-[#0055A4]',
                        hex: '#0055A4'
                    };
                case 'urc':
                    return {
                        accent: 'bg-[#003366]',
                        textAccent: 'text-[#003366]',
                        border: 'border-[#003366]',
                        focus: 'focus:border-[#003366]',
                        shadow: 'shadow-[#003366]/20',
                        decoration: 'decoration-[#003366]',
                        hex: '#003366'
                    };
            }
        }

        return {
            accent: 'bg-yellow-400',
            textAccent: 'text-yellow-400',
            border: 'border-yellow-400',
            focus: 'focus:border-yellow-400',
            shadow: 'shadow-yellow-200',
            decoration: 'decoration-yellow-400',
            hex: '#facc15'
        };
    }, [selectedTeams, initialPlayers, leagueContext]);

    // URLパラメータから初期値を設定
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const p = params.get('position');
        const s = params.get('search');
        const d = params.get('division');
        const c = params.get('category');
        const t = params.get('team');

        if (p) setSelectedPositions(p.split(','));
        if (s) setSearch(decodeURIComponent(s));
        if (d) setSelectedDivisions(d.split(','));
        if (c) setSelectedCategories(c.split(','));
        if (t) setSelectedTeams(t.split(','));
    }, []);

    const filteredPlayers = useMemo(() => {
        let result = initialPlayers.filter((p) => {
            if (search.endsWith('歳')) {
                const targetAge = search.replace('歳', '');
                return String(p.data.age ?? '') === targetAge;
            }
            if (search.endsWith('cm')) {
                const targetHeight = search.replace('cm', '');
                return String(p.data.height ?? '').replace('cm', '') === targetHeight;
            }
            if (search.endsWith('kg')) {
                const targetWeight = search.replace('kg', '');
                return String(p.data.weight ?? '').replace('kg', '') === targetWeight;
            }

            const searchLower = search.toLowerCase();
            const matchSearch =
                p.data.title.toLowerCase().includes(searchLower) ||
                (p.data.team?.toLowerCase() ?? '').includes(searchLower) ||
                (p.data.position?.toLowerCase() ?? '').includes(searchLower) ||
                (p.data.high_school?.toLowerCase() ?? '').includes(searchLower) ||
                (p.data.university?.toLowerCase() ?? '').includes(searchLower) ||
                (p.data.age && String(p.data.age).includes(searchLower)) ||
                (p.data.height && String(p.data.height).includes(searchLower)) ||
                (p.data.weight && String(p.data.weight).includes(searchLower));

            // FL / No8 などの複数ポジション対応を強化
            const playerPos = (p.data.position ?? '').toLowerCase();
            const matchPosition = selectedPositions.length === 0 ||
                selectedPositions.some(pos =>
                    playerPos.split(/[/／・\s]+/).some(pPart => pPart.trim() === pos.toLowerCase().trim())
                );

            const pLeague = (p.data.league ?? '').toLowerCase();
            const matchLeague = selectedLeagues.length === 0 || selectedLeagues.some(l => l.toLowerCase() === pLeague);

            const matchDivision = selectedDivisions.length === 0 || selectedDivisions.includes(p.data.division ?? '');
            const matchCategory = selectedCategories.length === 0 || selectedCategories.includes(p.data.category ?? '');
            const matchTeam = selectedTeams.length === 0 || (p.data.team && selectedTeams.includes(p.data.team));

            return matchSearch && matchPosition && matchLeague && matchDivision && matchCategory && matchTeam;
        });

        result.sort((a, b) => {
            let valA = a.data[sortKey];
            let valB = b.data[sortKey];

            if (sortKey === 'height' || sortKey === 'weight') {
                valA = parseFloat(String(valA).replace(/[^0-9.]/g, '')) || 0;
                valB = parseFloat(String(valB).replace(/[^0-9.]/g, '')) || 0;
            } else if (['tries', 'matches', 'starts', 'minutes'].includes(sortKey)) {
                valA = Number(valA) || 0;
                valB = Number(valB) || 0;
            }

            if (valA === valB) return 0;
            const order = sortOrder === 'asc' ? 1 : -1;
            return (valA! > valB! ? 1 : -1) * order;
        });

        return result;
    }, [initialPlayers, search, selectedLeagues, selectedPositions, selectedDivisions, selectedCategories, selectedTeams, sortKey, sortOrder]);

    const toggleFilter = (setList: React.Dispatch<React.SetStateAction<string[]>>, value: string) => {
        setList(prev =>
            prev.includes(value) ? prev.filter(v => v !== value) : [...prev, value]
        );
    };

    const toggleSort = (key: typeof sortKey) => {
        if (sortKey === key) {
            setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(key);
            setSortOrder('asc');
        }
    };

    const isLeagueOneSelected = useMemo(() => {
        const check = (l: string) => {
            const normalized = l.toLowerCase().replace(/[-_]/g, '');
            return normalized === 'leagueone' || normalized === 'japanrugbyleagueone';
        };
        if (leagueContext) return check(leagueContext);
        return selectedLeagues.length > 0 && selectedLeagues.every(check);
    }, [selectedLeagues, leagueContext]);

    const getLeagueColor = (league?: string) => {
        if (!league) return 'bg-[#E60012]';
        switch (league) {
            case 'league-one': return 'bg-[#E60012]';
            case 'top14': return 'bg-[#C5A059]';
            case 'super-rugby': return 'bg-[#0055A4]';
            default: return 'bg-[#E60012]';
        }
    };

    const getCategoryColor = (league?: string) => {
        if (!league) return 'text-[#E60012]';
        switch (league) {
            case 'league-one': return 'text-[#E60012]';
            case 'top14': return 'text-[#C5A059]';
            case 'super-rugby': return 'text-[#0055A4]';
            default: return 'text-[#E60012]';
        }
    };

    return (
        <div className={`container mx-auto p-4 max-w-7xl ${leagueContext ? 'mt-0' : 'mt-8'}`}>
            <div className="mb-12 space-y-6">
                {!leagueContext && (
                    <h1 className="text-4xl font-black text-gray-900 tracking-tighter italic">
                        RUGBY<span className={theme.textAccent}>PICKS</span> <span className="not-italic">選手名鑑</span>
                    </h1>
                )}

                <div className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100 space-y-8">
                    {/* 1. 検索（最上部） */}
                    <div>
                        <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">キーワードで探す</label>
                        <input
                            type="text"
                            placeholder="選手名, 所属チーム..."
                            className={`w-full p-4 bg-gray-50 border-2 border-transparent rounded-2xl focus:bg-white ${theme.focus} outline-none transition-all font-bold text-lg`}
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {/* 2. リーグ選択 */}
                        {!leagueContext && (
                            <div className="col-span-1 md:col-span-2 lg:col-span-4">
                                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">リーグ</label>
                                <div className="flex flex-wrap gap-3">
                                    {LEAGUES.map(league => (
                                        <button
                                            key={league.id}
                                            onClick={() => toggleFilter(setSelectedLeagues, league.id)}
                                            className={`px-6 py-2.5 rounded-xl font-black text-sm transition-all border-2 ${selectedLeagues.includes(league.id)
                                                ? `${getLeagueColor(league.id)} border-transparent text-white scale-105 shadow-lg`
                                                : 'bg-white border-gray-100 text-gray-400 hover:border-gray-200'
                                                }`}
                                        >
                                            {league.name}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* 3. チーム選択 */}
                        <div className="col-span-1 md:col-span-2 lg:col-span-4">
                            <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">チーム（複数選択可）</label>
                            <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto p-4 bg-gray-50 rounded-2xl border border-gray-100">
                                {VISIBLE_TEAMS.map(team => (
                                    <button
                                        key={team}
                                        onClick={() => toggleFilter(setSelectedTeams, team)}
                                        className={`px-4 py-2 rounded-xl font-black text-xs transition-all border-2 ${selectedTeams.includes(team)
                                            ? `${theme.accent} ${theme.border} text-white scale-105 shadow-md ${theme.shadow}`
                                            : 'bg-white border-gray-100 text-gray-400 hover:border-gray-200'
                                            }`}
                                    >
                                        {team}
                                    </button>
                                ))}
                                {VISIBLE_TEAMS.length === 0 && (
                                    <span className="text-gray-400 text-xs font-bold p-2 italic">表示できるチームがありません</span>
                                )}
                            </div>
                        </div>

                        {/* 4. ポジション選択 */}
                        <div className="col-span-1 md:col-span-2 lg:col-span-4">
                            <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">ポジション</label>
                            <div className="flex flex-wrap gap-2">
                                {POSITIONS.map(pos => (
                                    <button
                                        key={pos}
                                        onClick={() => toggleFilter(setSelectedPositions, pos)}
                                        className={`px-3 py-1.5 rounded-xl font-black text-[11px] transition-all border-2 ${selectedPositions.includes(pos)
                                            ? `${theme.accent} ${theme.border} text-white scale-105 shadow-md ${theme.shadow}`
                                            : 'bg-white border-gray-100 text-gray-400 hover:border-gray-200'
                                            }`}
                                    >
                                        {pos}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* 5. リーグワン限定オプション (Division, Category) */}
                        {isLeagueOneSelected && (
                            <>
                                <div className="col-span-1 md:col-span-2 lg:col-span-2">
                                    <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">ディビジョン (LEAGUE ONE)</label>
                                    <div className="flex flex-wrap gap-2">
                                        {DIVISIONS.map(div => (
                                            <button
                                                key={div}
                                                onClick={() => toggleFilter(setSelectedDivisions, div)}
                                                className={`px-4 py-2 rounded-xl font-black text-sm text-left transition-all border-2 ${selectedDivisions.includes(div)
                                                    ? `${theme.accent} ${theme.border} text-white scale-102 shadow-md ${theme.shadow}`
                                                    : 'bg-white border-gray-100 text-gray-400 hover:border-gray-200'
                                                    }`}
                                            >
                                                {div}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                <div className="col-span-1 md:col-span-2 lg:col-span-2">
                                    <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">カテゴリー (LEAGUE ONE)</label>
                                    <div className="flex flex-wrap gap-2">
                                        {CATEGORIES.map(cat => (
                                            <button
                                                key={cat}
                                                onClick={() => toggleFilter(setSelectedCategories, cat)}
                                                className={`px-4 py-2 rounded-xl font-black text-sm text-left transition-all border-2 ${selectedCategories.includes(cat)
                                                    ? `${theme.accent} ${theme.border} text-white scale-102 shadow-md ${theme.shadow}`
                                                    : 'bg-white border-gray-100 text-gray-400 hover:border-gray-200'
                                                    }`}
                                            >
                                                {cat}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </>
                        )}

                        {/* 6. ソート */}
                        <div className="col-span-1 md:col-span-2 lg:col-span-4 flex flex-wrap items-center gap-4 pt-4 border-t border-gray-50">
                            <span className="text-xs font-black text-gray-400 uppercase tracking-widest">ソート順</span>
                            <div className="flex flex-wrap gap-2">
                                {(['age', 'height', 'weight', 'tries', 'matches', 'starts', 'minutes'] as const).map(key => {
                                    // スコアデータがないリーグのソートボタンを制限
                                    const isScoreSort = ['tries', 'matches', 'starts', 'minutes'].includes(key);
                                    const showSort = !isScoreSort || filteredPlayers.some(p => p.data.has_scores === true || p.data.has_scores === "true");

                                    if (!showSort) return null;

                                    return (
                                        <button
                                            key={key}
                                            onClick={() => toggleSort(key)}
                                            className={`px-4 py-2 rounded-lg font-bold text-xs transition-colors ${sortKey === key ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                                                }`}
                                        >
                                            {key === 'age' ? '年齢' :
                                                key === 'height' ? '身長' :
                                                    key === 'weight' ? '体重' :
                                                        key === 'tries' ? 'トライ' :
                                                            key === 'matches' ? '試合数' :
                                                                key === 'starts' ? '先発' : '分'} {sortKey === key && (sortOrder === 'asc' ? '↑' : '↓')}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    </div>

                    <p className="text-gray-400 font-bold ml-2 italic underline decoration-2 underline-offset-4" style={{ textDecorationColor: theme.hex }}>
                        検索結果: <span className="text-gray-900">{filteredPlayers.length}</span> 名
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                    {filteredPlayers.map((player) => {
                        const leagueColor = getLeagueColor(player.data.league);
                        const categoryColor = getCategoryColor(player.data.league);
                        return (
                            <a
                                key={player.slug}
                                href={`/players/${player.slug}`}
                                className="group block bg-white rounded-3xl p-6 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all border border-gray-50 relative overflow-hidden flex flex-col h-full"
                            >
                                {/* ディビジョン・アクセント（リーグ別カラー適用） */}
                                {player.data.division && (
                                    <>
                                        <div className={`absolute top-0 right-0 w-16 h-16 translate-x-8 -translate-y-8 rotate-45 ${leagueColor} z-10 transition-colors`}></div>
                                        <div className="absolute top-1.5 right-1.5 z-20 font-black leading-none flex flex-col items-center">
                                            <span className="text-[10px] text-gray-900/40 uppercase tracking-tighter mb-[-2px]">DIV</span>
                                            <span className="text-xl text-gray-900">
                                                {player.data.division.split(' ')[1]}
                                            </span>
                                        </div>
                                    </>
                                )}

                                {!player.data.division && player.data.league && (
                                    <div className={`absolute top-0 right-0 px-3 py-1 ${leagueColor} z-10 font-black text-[10px] rounded-bl-xl uppercase italic text-white`}>
                                        {player.data.league.replace('-', ' ')}
                                    </div>
                                )}

                                <div className="mb-6 relative z-10 flex-grow">
                                    <div className="flex flex-col gap-1 mb-3">
                                        <div className="flex justify-between items-start">
                                            <span className="inline-block px-3 py-1 bg-gray-900 text-white text-[10px] font-black rounded-lg tracking-tighter">
                                                {player.data.position}
                                            </span>
                                        </div>
                                        {player.data.category && (
                                            <span className={`text-[9px] font-black uppercase tracking-widest ${categoryColor}`}>{player.data.category}</span>
                                        )}
                                    </div>
                                    {/* 命名規則の適用: 海外リーグは英語メイン、リーグワンは日本語メイン */}
                                    {(() => {
                                        const isPLeagueOne = player.data.league === 'league-one' || player.data.league === 'leagueone';
                                        const mainName = isPLeagueOne ? player.data.title : (player.data.name_en || player.data.title);
                                        const subName = isPLeagueOne ? (player.data.name_en || player.data.title) : player.data.title;
                                        const showSub = subName && subName !== mainName;

                                        return (
                                            <>
                                                <h2 className={`text-2xl font-black text-gray-900 mb-3 leading-tight group-hover:text-yellow-600 transition-colors tracking-tighter ${!isPLeagueOne ? 'uppercase' : ''}`}>
                                                    {mainName}
                                                </h2>
                                                {showSub && (
                                                    <p className={`text-[13px] font-bold text-gray-400 mb-4 italic tracking-tight ${isPLeagueOne ? 'uppercase' : ''}`}>
                                                        {subName}
                                                    </p>
                                                )}
                                            </>
                                        );
                                    })()}

                                    {/* チーム名をボックス化 */}
                                    <div className="mb-4">
                                        <span className="inline-block px-3 py-1.5 bg-gray-100 text-gray-700 border border-gray-200 rounded-lg font-black text-sm tracking-tight shadow-sm">
                                            {player.data.team}
                                        </span>
                                    </div>

                                    {/* 学歴の表示 (League Oneのみ表示) */}
                                    {isLeagueOneSelected && (player.data.high_school || player.data.university) && (
                                        <p className="text-xs font-black text-gray-600 uppercase tracking-tighter mb-5 leading-tight">
                                            {player.data.high_school && <span>{player.data.high_school}</span>}
                                            {player.data.high_school && player.data.university && <span className="mx-1 text-yellow-500 font-bold">→</span>}
                                            {player.data.university && <span>{player.data.university}</span>}
                                        </p>
                                    )}

                                    {/* 代表歴の表示 */}
                                    {player.data.caps && (
                                        <div className="inline-block px-3 py-1.5 bg-yellow-50 text-yellow-700 text-xs font-black rounded-md border border-yellow-100 italic mb-4">
                                            <span className="mr-1.5 not-italic text-base">
                                                {FLAG_MAP[player.data.country || ''] || (player.data.caps.includes('日本') ? '🇯🇵' : '')}
                                            </span>
                                            {player.data.caps}
                                        </div>
                                    )}

                                    {/* 実戦スタッツ (海外リーグ向け) */}
                                    {(player.data.matches !== undefined || player.data.tries !== undefined) && (
                                        <div className="grid grid-cols-4 gap-2 py-3 px-4 bg-gray-50 rounded-2xl border border-gray-100 mb-2">
                                            <div className="flex flex-col items-center">
                                                <span className="text-[10px] font-black text-gray-400 uppercase">Played</span>
                                                <span className="text-sm font-black text-gray-900">{player.data.matches || 0}</span>
                                            </div>
                                            <div className="flex flex-col items-center">
                                                <span className="text-[10px] font-black text-gray-400 uppercase">Start</span>
                                                <span className="text-sm font-black text-gray-900">{player.data.starts || 0}</span>
                                            </div>
                                            <div className="flex flex-col items-center">
                                                <span className="text-[10px] font-black text-gray-400 uppercase">Tries</span>
                                                <span className={`text-sm font-black ${(player.data.tries || 0) > 0 ? 'text-yellow-600' : 'text-gray-900'}`}>{player.data.tries || 0}</span>
                                            </div>
                                            <div className="flex flex-col items-center">
                                                <span className="text-[10px] font-black text-gray-400 uppercase">Mins</span>
                                                <span className="text-sm font-black text-gray-900">{player.data.minutes || 0}</span>
                                            </div>
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
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default PlayerList;
