#!/usr/bin/env python3
"""全ニュース記事に選手/チーム/代表の相互リンクを付与するリンカー（保守的）。
--write で書き込み。既定はドライラン（件数と各記事の付与結果を表示）。

選手リンクの対象は data/manual/player_pages.json（scripts/build_player_pages.py 生成）に載る
「個別ページのある選手」のみ（docs/adsense/01_DESIGN.md §2）。
--fix-dead: 既存記事内の /players/{slug}/ リンクのうち個別ページが無いものを、
チーム名簿アンカー（/teams/{lg}/{team}/#p-{slug} 等。src/lib/master.ts playerFallbackPath と同じ規則）へ
書き換える（行き先が /players/ だけになる場合はリンクを外して平文に戻す）。付与はしない。
"""
import re, json, glob, pathlib, collections, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import player_links as PL  # noqa: E402
WRITE = '--write' in sys.argv

# ---- 辞書構築 -------------------------------------------------------------
# 個別ページのある選手（player_pages.json）と、統合（player_merges.json）の解決は pipeline/player_links.py と共通
indexable_slugs = PL.indexable_slugs()
canon = PL.canon
master_players = PL.master_players()
slug_to_player = PL.slug_to_player()

# players: 一意な name_ja(4文字以上) -> /players/slug/（個別ページのある選手のみ）
# 一意性は全選手（統合後の人物単位）で判定し、非対象選手と同名の別人へ誤リンクしない
tmp = collections.defaultdict(set)
for pid, p in master_players.items():
    nm = p.get('name_ja')
    if nm and p.get('slug') and len(nm) >= 4:
        tmp[nm].add(canon(pid))
players = {}
for nm, ids in tmp.items():
    if len(ids) != 1:
        continue
    cp = master_players.get(next(iter(ids)))
    if cp and cp['slug'] in indexable_slugs:
        players[nm] = f"/players/{cp['slug']}/"

# clubs: data/teams.json + team_names_jp のエイリアス -> /teams/{lg}/{slug}/
clubs = {}
for t in json.load(open(ROOT/'data/teams.json')):
    slug, lg = t.get('slug'), t.get('league')
    if not slug or not lg or slug == '2025-26':
        continue
    url = f"/teams/{lg}/{slug}/"
    for k in (t.get('team_name'), t.get('team_en_name')):
        k = (k or '').strip()
        # 日本語（非ASCII）を含むキーのみ。純ASCII英語名は誤リンクの元なので除外
        if len(k) >= 4 and any(ord(c) > 127 for c in k):
            clubs.setdefault(k, url)
names_jp = json.load(open(ROOT/'data/team_names_jp.json'))
for lg_map in names_jp.values():
    if not isinstance(lg_map, dict):
        continue
    for data in lg_map.values():
        jp = (data or {}).get('jp')
        url = clubs.get(jp) if jp else None
        if not url:
            continue
        for al in (data.get('aliases') or []):
            al = al.strip()
            if len(al) >= 4 and any(ord(c) > 127 for c in al):
                clubs.setdefault(al, url)

# 誤リンクの元になる曖昧な別名（他チーム・企業名と衝突）
for _k in ('ライオン', 'JR東日本'):
    clubs.pop(_k, None)

# national: 「◯◯代表」-> /national-teams/{slug}/
national = {}
for t in json.load(open(ROOT/'data/national_teams_config.json')):
    nm, slug = t.get('name'), t.get('slug')
    if nm and slug:
        national[nm.strip()] = f"/national-teams/{slug}/"

# ---- リンク付与 -----------------------------------------------------------
# 保護スパン（既存リンク・画像・HTMLタグ・コード・URL）は書き換えない
PROTECT = re.compile(
    r'!?\[[^\]]*\]\([^)]*\)'      # markdown link / image
    r'|<[^>]+>'                    # html tag
    r'|`[^`]*`'                    # inline code
    r'|https?://\S+',              # bare url
)

def protected_spans(text):
    return [(m.start(), m.end()) for m in PROTECT.finditer(text)]

def in_protected(pos, spans):
    for s, e in spans:
        if s <= pos < e:
            return True
    return False

def link_body(body, dicts_in_order):
    """辞書順（players→clubs→national ではなく、キー長で最長一致）に第1出現のみリンク。"""
    # 全キーを (キー, url, kind) で集約し長い順に
    entries = []
    for kind, d in dicts_in_order:
        for k, url in d.items():
            entries.append((k, url, kind))
    entries.sort(key=lambda x: len(x[0]), reverse=True)

    # 事前フィルタ: 空白無視で本文に現れるものだけ
    body_ns = body.replace(' ', '').replace('　', '')
    done = set()
    report = []
    for k, url, kind in entries:
        if k in done:
            continue
        k_ns = k.replace(' ', '')
        if k_ns not in body_ns:
            continue
        # 空白を許容する検索パターン（選手名の姓名間スペース対策）
        pat = re.compile(r'[ 　]*'.join(re.escape(c) for c in k_ns))
        spans = protected_spans(body)
        m = None
        for cand in pat.finditer(body):
            if not in_protected(cand.start(), spans) and not in_protected(cand.end()-1, spans):
                # 直前が '[' や '/' の場合はスキップ（リンク内・パス内）
                prev = body[cand.start()-1] if cand.start() > 0 else ''
                if prev in '[/':
                    continue
                m = cand
                break
        if not m:
            continue
        seg = body[m.start():m.end()]
        body = body[:m.start()] + f"[{seg}]({url})" + body[m.end():]
        done.add(k)
        report.append((kind, seg, url))
    return body, report

# ---- --fix-dead: 個別ページの無い選手リンクの書き換え -----------------------
FIX_DEAD = '--fix-dead' in sys.argv

DEAD_LINK = re.compile(r'\[([^\]]*)\]\(/players/([^/)\s]+)/?\)')
dead_fixed = collections.Counter()

def fix_dead_links(body):
    def repl(m):
        text, slug = m.group(1), m.group(2)
        if slug in indexable_slugs:
            return m.group(0)
        p = slug_to_player.get(slug)
        if p is None or p.get('league') == 'highschool':
            return m.group(0)          # master に無い/高校生は触らない（別系統の301に任せる）
        if p['slug'] in indexable_slugs:
            dead_fixed['merged'] += 1
            return f"[{text}](/players/{p['slug']}/)"
        target = PL.fallback_path(p)
        if target == '/players/':
            dead_fixed['unlink'] += 1
            return text
        dead_fixed['anchor'] += 1
        return f"[{text}]({target})"
    return DEAD_LINK.sub(repl, body)

def split_frontmatter(text):
    if text.startswith('---'):
        i = text.find('\n---', 3)
        if i != -1:
            j = text.find('\n', i+1)
            return text[:j+1], text[j+1:]
    return '', text

dicts = [('player', players), ('club', clubs), ('national', national)]
total_links = 0
per_kind = collections.Counter()
changed_files = 0
for fp in sorted(glob.glob(str(ROOT/'src/content/news/*.md'))):
    p = pathlib.Path(fp)
    text = p.read_text(encoding='utf-8')
    fm, body = split_frontmatter(text)
    if FIX_DEAD:
        new_body = fix_dead_links(body)
        if new_body != body:
            changed_files += 1
            if WRITE:
                p.write_text(fm + new_body, encoding='utf-8')
        continue
    if 'category: "auto"' in fm:  # pipeline再生成される記事はpipeline側でリンク
        continue
    new_body, report = link_body(body, dicts)
    if report:
        total_links += len(report)
        for kind, seg, url in report:
            per_kind[kind] += 1
        print(f"\n{p.name}: +{len(report)}")
        for kind, seg, url in report[:40]:
            print(f"   [{kind}] {seg} -> {url}")
    if WRITE and report:
        p.write_text(fm + new_body, encoding='utf-8')

if FIX_DEAD:
    print(f"=== fix-dead: files={changed_files} {dict(dead_fixed)} ; write={WRITE} ===")
else:
    print(f"\n=== total {total_links} links; by kind {dict(per_kind)} ; write={WRITE} ===")
    print(f"dict sizes: players={len(players)} clubs={len(clubs)} national={len(national)}")
