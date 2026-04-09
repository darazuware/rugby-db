import React, { useState, useMemo, useCallback, useEffect } from 'react';

interface Player {
  slug: string;
  name: string;
  name_en?: string;
  position?: string;
  team?: string;
  country?: string;
}

interface SelectedPlayer extends Player {
  slotIndex: number;
}

const POSITIONS: { index: number; label: string; abbr: string; row: number; col: number; isReserve?: boolean }[] = [
  // Forwards
  { index: 1, label: 'PR(1)', abbr: 'PR', row: 1, col: 1 },
  { index: 2, label: 'HO(2)', abbr: 'HO', row: 1, col: 2 },
  { index: 3, label: 'PR(3)', abbr: 'PR', row: 1, col: 3 },
  { index: 4, label: 'LO(4)', abbr: 'LO', row: 2, col: 1 },
  { index: 5, label: 'LO(5)', abbr: 'LO', row: 2, col: 2 },
  { index: 6, label: 'FL(6)', abbr: 'FL', row: 3, col: 1 },
  { index: 7, label: 'FL(7)', abbr: 'FL', row: 3, col: 3 },
  { index: 8, label: 'No.8', abbr: 'No8', row: 3, col: 2 },
  // Backs
  { index: 9, label: 'SH(9)', abbr: 'SH', row: 4, col: 2 },
  { index: 10, label: 'SO(10)', abbr: 'SO', row: 5, col: 2 },
  { index: 11, label: 'WTB(11)', abbr: 'WTB', row: 6, col: 1 },
  { index: 12, label: 'CTB(12)', abbr: 'CTB', row: 6, col: 2 },
  { index: 13, label: 'CTB(13)', abbr: 'CTB', row: 6, col: 3 },
  { index: 14, label: 'WTB(14)', abbr: 'WTB', row: 7, col: 3 },
  { index: 15, label: 'FB(15)', abbr: 'FB', row: 7, col: 2 },
  // Reserves
  { index: 16, label: 'リザーブ1', abbr: 'R1', row: 0, col: 0, isReserve: true },
  { index: 17, label: 'リザーブ2', abbr: 'R2', row: 0, col: 0, isReserve: true },
  { index: 18, label: 'リザーブ3', abbr: 'R3', row: 0, col: 0, isReserve: true },
  { index: 19, label: 'リザーブ4', abbr: 'R4', row: 0, col: 0, isReserve: true },
  { index: 20, label: 'リザーブ5', abbr: 'R5', row: 0, col: 0, isReserve: true },
  { index: 21, label: 'リザーブ6', abbr: 'R6', row: 0, col: 0, isReserve: true },
  { index: 22, label: 'リザーブ7', abbr: 'R7', row: 0, col: 0, isReserve: true },
  { index: 23, label: 'リザーブ8', abbr: 'R8', row: 0, col: 0, isReserve: true },
];

const FLAG_MAP: Record<string, string> = {
  '日本': '🇯🇵', 'Japan': '🇯🇵',
  'ニュージーランド': '🇳🇿', 'NZ': '🇳🇿', 'New Zealand': '🇳🇿',
  'オーストラリア': '🇦🇺', 'AUS': '🇦🇺', 'Australia': '🇦🇺',
  '南アフリカ': '🇿🇦', 'SA': '🇿🇦', 'South Africa': '🇿🇦',
  'フランス': '🇫🇷', 'FRA': '🇫🇷', 'France': '🇫🇷',
  'イングランド': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'ENG': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
  'アイルランド': '🇮🇪', 'IRE': '🇮🇪', 'Ireland': '🇮🇪',
  'スコットランド': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'SCO': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
  'ウェールズ': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'WAL': '🏴󠁧󠁢󠁷󠁬󠁳󠁿',
  'フィジー': '🇫🇯', 'FIJ': '🇫🇯',
  'サモア': '🇼🇸', 'SAM': '🇼🇸',
  'トンガ': '🇹🇴', 'TGA': '🇹🇴',
  'イタリア': '🇮🇹', 'ITA': '🇮🇹',
  'アルゼンチン': '🇦🇷', 'ARG': '🇦🇷',
  'ジョージア': '🇬🇪', 'GEO': '🇬🇪',
  'ルーマニア': '🇷🇴', 'ROU': '🇷🇴',
  'ポルトガル': '🇵🇹', 'POR': '🇵🇹',
  'ウルグアイ': '🇺🇾', 'URU': '🇺🇾',
  'ナミビア': '🇳🇦', 'NAM': '🇳🇦',
  'チリ': '🇨🇱', 'CHI': '🇨🇱',
  'カナダ': '🇨🇦', 'CAN': '🇨🇦',
  'アメリカ': '🇺🇸', 'USA': '🇺🇸',
  'スペイン': '🇪🇸', 'ESP': '🇪🇸',
  'ロシア': '🇷🇺', 'RUS': '🇷🇺',
  'ケニア': '🇰🇪', 'KEN': '🇰🇪',
};

function encodeTeam(slots: Record<number, Player>): string {
  const arr = POSITIONS.map(p => slots[p.index]?.slug || '');
  return btoa(unescape(encodeURIComponent(arr.join(','))));
}

function decodeTeam(encoded: string, players: Player[]): Record<number, Player> {
  try {
    const decoded = decodeURIComponent(escape(atob(encoded)));
    const slugs = decoded.split(',');
    const result: Record<number, Player> = {};
    const playerMap = new Map(players.map(p => [p.slug, p]));
    slugs.forEach((slug, i) => {
      if (slug && playerMap.has(slug)) {
        result[i + 1] = playerMap.get(slug)!;
      }
    });
    return result;
  } catch {
    return {};
  }
}

interface Props {
  players: Player[];
  initialEncoded?: string;
}

export default function DreamTeamBuilder({ players, initialEncoded }: Props) {
  const [slots, setSlots] = useState<Record<number, Player>>(() => {
    if (initialEncoded) return decodeTeam(initialEncoded, players);
    try {
      const saved = localStorage.getItem('rugby_dream_team');
      if (saved) return decodeTeam(saved, players);
    } catch {}
    return {};
  });
  const [activeSlot, setActiveSlot] = useState<number | null>(null);
  const [search, setSearch] = useState('');
  const [posFilter, setPosFilter] = useState('');
  const [copied, setCopied] = useState(false);
  const [teamName, setTeamName] = useState('最強のラグビー15');
  const [cartPlayers, setCartPlayers] = useState<Player[]>([]);
  const [modalTab, setModalTab] = useState<'search' | 'cart'>('search');

  // 自動保存
  useEffect(() => {
    try { localStorage.setItem('rugby_dream_team', encodeTeam(slots)); } catch {}
  }, [slots]);

  // カート読み込み
  useEffect(() => {
    try {
      const cartData: {slug: string}[] = JSON.parse(localStorage.getItem('rugby_draft_cart') || '[]');
      const playerMap = new Map(players.map(p => [p.slug, p]));
      setCartPlayers(cartData.map(item => playerMap.get(item.slug)).filter(Boolean) as Player[]);
    } catch {}
  }, [players]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return players.filter(p => {
      const matchSearch = !q ||
        p.name.toLowerCase().includes(q) ||
        (p.name_en?.toLowerCase().includes(q) ?? false) ||
        (p.team?.toLowerCase().includes(q) ?? false);
      const matchPos = !posFilter || (p.position?.toUpperCase() === posFilter.toUpperCase());
      return matchSearch && matchPos;
    }).slice(0, 200);
  }, [players, search, posFilter]);

  const getShareUrl = useCallback(() => {
    const encoded = encodeTeam(slots);
    return `${window.location.origin}/dream-team?team=${encoded}`;
  }, [slots]);

  const handleShare = useCallback(async () => {
    const url = getShareUrl();
    const text = `【${teamName}】私が選んだ最強のラグビー23人 #rugbypicks\n${url}`;
    const shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
    window.open(shareUrl, '_blank', 'noopener,noreferrer');
  }, [getShareUrl, teamName]);

  const handleCopyLink = useCallback(async () => {
    const url = getShareUrl();
    await navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [getShareUrl]);

  const handleSelectPlayer = useCallback((player: Player) => {
    if (activeSlot === null) return;
    setSlots(prev => ({ ...prev, [activeSlot]: player }));
    setActiveSlot(null);
    setSearch('');
    setPosFilter('');
  }, [activeSlot]);

  const handleRemove = useCallback((index: number) => {
    setSlots(prev => {
      const next = { ...prev };
      delete next[index];
      return next;
    });
  }, []);

  const filledCount = Object.keys(slots).length;

  const mainPositions = POSITIONS.filter(p => !p.isReserve);
  const reserves = POSITIONS.filter(p => p.isReserve);

  // Build a 7-row grid for main positions
  const rows: typeof mainPositions[] = [[], [], [], [], [], [], []];
  mainPositions.forEach(p => {
    rows[p.row - 1]?.push(p);
  });

  const colClass = ['', 'justify-center', 'justify-around', 'justify-between'];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <input
          value={teamName}
          onChange={e => setTeamName(e.target.value)}
          className="w-full bg-transparent text-4xl font-black italic tracking-tighter text-foreground border-b-2 border-yellow-400 pb-2 mb-2 focus:outline-none"
          maxLength={30}
          placeholder="チーム名を入力"
        />
        <p className="text-foreground/40 text-sm font-bold">
          {filledCount}/23名選択済み
        </p>
      </div>

      {/* Formation */}
      <div className="bg-card border border-border-dim rounded-3xl p-6 mb-6 relative overflow-hidden">
        {/* Field lines decoration */}
        <div className="absolute inset-0 pointer-events-none opacity-5">
          <div className="w-full h-full border-4 border-foreground rounded-3xl" />
          <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-foreground" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 rounded-full border-4 border-foreground" />
        </div>

        <p className="text-[10px] font-black uppercase tracking-widest text-foreground/30 mb-5 text-center">STARTING XV</p>

        <div className="space-y-3 relative z-10">
          {rows.map((row, ri) => (
            <div key={ri} className={`flex gap-2 ${colClass[Math.min(row.length, 3)]}`}>
              {row.sort((a, b) => a.col - b.col).map(pos => {
                const player = slots[pos.index];
                return (
                  <SlotCard
                    key={pos.index}
                    pos={pos}
                    player={player}
                    onClick={() => setActiveSlot(pos.index)}
                    onRemove={() => handleRemove(pos.index)}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Reserves */}
      <div className="bg-card border border-border-dim rounded-3xl p-6 mb-6">
        <p className="text-[10px] font-black uppercase tracking-widest text-foreground/30 mb-4">RESERVES (16-23)</p>
        <div className="grid grid-cols-4 gap-2">
          {reserves.map(pos => {
            const player = slots[pos.index];
            return (
              <SlotCard
                key={pos.index}
                pos={pos}
                player={player}
                onClick={() => setActiveSlot(pos.index)}
                onRemove={() => handleRemove(pos.index)}
                compact
              />
            );
          })}
        </div>
      </div>

      {/* Share buttons */}
      <div className="flex flex-wrap gap-3 mb-8">
        <button
          onClick={handleShare}
          className="flex items-center gap-2 px-6 py-3 bg-[#1DA1F2] text-white font-black text-sm rounded-xl hover:bg-[#1a8fd1] transition-all shadow-lg"
        >
          <span>𝕏 でシェア</span>
        </button>
        <button
          onClick={handleCopyLink}
          className="flex items-center gap-2 px-6 py-3 bg-yellow-400 text-black font-black text-sm rounded-xl hover:bg-yellow-300 transition-all shadow-lg"
        >
          {copied ? 'コピー完了 ✓' : 'リンクをコピー'}
        </button>
        <button
          onClick={() => { setSlots({}); try { localStorage.removeItem('rugby_dream_team'); } catch {} }}
          className="flex items-center gap-2 px-6 py-3 bg-foreground/10 text-foreground/60 font-black text-sm rounded-xl hover:bg-foreground/20 transition-all border border-border-dim"
        >
          リセット
        </button>
      </div>

      {/* Modal */}
      {activeSlot !== null && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={() => { setActiveSlot(null); setSearch(''); setPosFilter(''); setModalTab('search'); }} />
          <div className="relative bg-card w-full sm:max-w-lg max-h-[85vh] sm:max-h-[70vh] rounded-t-3xl sm:rounded-3xl flex flex-col overflow-hidden border border-border-dim shadow-2xl">
            {/* Header */}
            <div className="p-4 border-b border-border-dim">
              <div className="flex items-center gap-3 mb-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-foreground/40 flex-1">
                  {POSITIONS.find(p => p.index === activeSlot)?.label} を選択
                </p>
                <button onClick={() => { setActiveSlot(null); setSearch(''); setPosFilter(''); setModalTab('search'); }} className="text-foreground/40 hover:text-foreground text-xl font-bold w-8 h-8 flex items-center justify-center">×</button>
              </div>
              {/* タブ */}
              <div className="flex gap-2 mb-3">
                <button
                  onClick={() => setModalTab('search')}
                  className={`flex-1 py-2 text-xs font-black rounded-lg transition-all ${modalTab === 'search' ? 'bg-yellow-400 text-black' : 'bg-foreground/10 text-foreground/50 hover:bg-foreground/20'}`}
                >
                  検索
                </button>
                <button
                  onClick={() => setModalTab('cart')}
                  className={`flex-1 py-2 text-xs font-black rounded-lg transition-all relative ${modalTab === 'cart' ? 'bg-yellow-400 text-black' : 'bg-foreground/10 text-foreground/50 hover:bg-foreground/20'}`}
                >
                  カート {cartPlayers.length > 0 && <span className={`ml-1 px-1.5 py-0.5 rounded-full text-[10px] ${modalTab === 'cart' ? 'bg-black/20 text-black' : 'bg-yellow-400 text-black'}`}>{cartPlayers.length}</span>}
                </button>
              </div>
              {/* 検索タブのみ検索バー表示 */}
              {modalTab === 'search' && (
                <div className="flex items-center gap-2">
                  <input
                    autoFocus
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    placeholder="選手名・チームで検索..."
                    className="flex-1 bg-transparent text-foreground font-bold text-base focus:outline-none placeholder:text-foreground/30"
                  />
                  <select
                    value={posFilter}
                    onChange={e => setPosFilter(e.target.value)}
                    className="bg-foreground/10 text-foreground text-xs font-black rounded-lg px-3 py-2 border border-border-dim focus:outline-none"
                  >
                    <option value="">全ポジ</option>
                    {['PR', 'HO', 'LO', 'FL', 'No8', 'SH', 'SO', 'CTB', 'WTB', 'FB'].map(p => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>
              )}
            </div>
            {/* リスト */}
            <div className="overflow-y-auto flex-1">
              {modalTab === 'cart' ? (
                cartPlayers.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-foreground/30 font-bold text-sm mb-2">カートは空です</p>
                    <p className="text-foreground/20 text-xs">選手名鑑・チーム別メンバー表から<br/>「カートに追加」ボタンで選手を追加できます</p>
                  </div>
                ) : (
                  <>
                    {cartPlayers.map(player => (
                      <button
                        key={player.slug}
                        onClick={() => handleSelectPlayer(player)}
                        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-yellow-400/10 text-left border-b border-border-dim/40 transition-colors group"
                      >
                        <span className="text-[10px] font-black text-foreground/30 w-10 text-center bg-foreground/5 rounded-lg py-1 group-hover:bg-yellow-400/20">
                          {player.position || '—'}
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="font-black text-sm text-foreground truncate">
                            {FLAG_MAP[player.country || ''] || ''} {player.name}
                          </p>
                          {player.name_en && player.name_en !== player.name && (
                            <p className="text-[10px] text-foreground/40 truncate">{player.name_en}</p>
                          )}
                        </div>
                        {player.team && (
                          <span className="text-[10px] text-foreground/30 font-bold truncate max-w-[100px]">{player.team}</span>
                        )}
                      </button>
                    ))}
                    <button
                      onClick={() => { try { localStorage.removeItem('rugby_draft_cart'); } catch {} setCartPlayers([]); }}
                      className="w-full py-3 text-xs text-foreground/30 font-black hover:text-red-400 transition-colors"
                    >
                      カートをクリア
                    </button>
                  </>
                )
              ) : (
                filtered.length === 0 ? (
                  <p className="text-center text-foreground/30 py-12 font-bold">選手が見つかりません</p>
                ) : (
                  filtered.map(player => (
                    <button
                      key={player.slug}
                      onClick={() => handleSelectPlayer(player)}
                      className="w-full flex items-center gap-3 px-4 py-3 hover:bg-yellow-400/10 text-left border-b border-border-dim/40 transition-colors group"
                    >
                      <span className="text-[10px] font-black text-foreground/30 w-10 text-center bg-foreground/5 rounded-lg py-1 group-hover:bg-yellow-400/20">
                        {player.position || '—'}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="font-black text-sm text-foreground truncate">
                          {FLAG_MAP[player.country || ''] || ''} {player.name}
                        </p>
                        {player.name_en && player.name_en !== player.name && (
                          <p className="text-[10px] text-foreground/40 truncate">{player.name_en}</p>
                        )}
                      </div>
                      {player.team && (
                        <span className="text-[10px] text-foreground/30 font-bold truncate max-w-[100px]">{player.team}</span>
                      )}
                    </button>
                  ))
                )
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

interface SlotCardProps {
  pos: typeof POSITIONS[0];
  player?: Player;
  onClick: () => void;
  onRemove: () => void;
  compact?: boolean;
}

function SlotCard({ pos, player, onClick, onRemove, compact }: SlotCardProps) {
  if (compact) {
    return (
      <div className="relative group">
        <button
          onClick={onClick}
          className={`w-full rounded-xl border-2 transition-all text-center py-2 px-1 ${
            player
              ? 'border-yellow-400 bg-yellow-400/10 hover:bg-yellow-400/20'
              : 'border-border-dim border-dashed hover:border-yellow-400/50 hover:bg-foreground/5'
          }`}
        >
          <p className="text-[9px] font-black text-foreground/30 uppercase tracking-widest mb-0.5">{pos.index}</p>
          {player ? (
            <p className="text-[10px] font-black text-foreground leading-tight truncate px-1">{player.name}</p>
          ) : (
            <p className="text-[11px] font-black text-foreground/20">+</p>
          )}
        </button>
        {player && (
          <button
            onClick={e => { e.stopPropagation(); onRemove(); }}
            className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-red-500 text-white text-[9px] font-black hidden group-hover:flex items-center justify-center z-10"
          >×</button>
        )}
      </div>
    );
  }

  return (
    <div className="relative group flex-1 max-w-[140px] min-w-[80px]">
      <button
        onClick={onClick}
        className={`w-full rounded-2xl border-2 transition-all text-center py-3 px-2 ${
          player
            ? 'border-yellow-400 bg-yellow-400/10 hover:bg-yellow-400/20'
            : 'border-border-dim border-dashed hover:border-yellow-400/50 hover:bg-foreground/5'
        }`}
      >
        <p className="text-[9px] font-black text-foreground/30 uppercase tracking-widest mb-1">{pos.label}</p>
        {player ? (
          <>
            <p className="text-xs font-black text-foreground leading-tight truncate">
              {FLAG_MAP[player.country || ''] || ''} {player.name}
            </p>
            {player.team && <p className="text-[9px] text-foreground/40 mt-0.5 truncate">{player.team}</p>}
          </>
        ) : (
          <p className="text-lg font-black text-foreground/15">+</p>
        )}
      </button>
      {player && (
        <button
          onClick={e => { e.stopPropagation(); onRemove(); }}
          className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-red-500 text-white text-[10px] font-black hidden group-hover:flex items-center justify-center z-10 shadow-lg"
        >×</button>
      )}
    </div>
  );
}
