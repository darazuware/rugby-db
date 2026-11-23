#!/usr/bin/env python3
"""花園出身選手記事(draft)を生成。使い方: python3 scripts/hanazono_ob_article.py 桐蔭学園 toin
データ: data/unified_player_database_final.json(リーグワン2025-26登録)。戦績は51校記事の該当ブロックを転記。
"""
import json, collections, re, sys
short = sys.argv[1]; rom = sys.argv[2]; hs = short + '高校'
d = json.load(open('data/unified_player_database_final.json'))
aliases = ['東海大仰星高校', '東海大学付属大阪仰星高校', '東海大学付属仰星高校', '東海大大阪仰星高校', '東海大学大阪仰星高校', '東海大学仰星高校'] if short == '東海大仰星' else [hs]
p = [x for x in d.values() if x.get('high_school') in aliases]
if len(p) < 10: sys.exit(f'{hs}: {len(p)}人のみ。薄くなるので別の型を使う')
sh = lambda t: t.split('（')[0]
uv = lambda x: x.get('university') if x.get('university') not in (None, '', 'nan') else None
def g(x):
    y = int(x['birthdate'][:4]); m = int(x['birthdate'][5:7]); return y+18 if m <= 3 else y+19
def bars(items, cls=''):
    m = max(n for _, n in items)
    return '<div class="ob-bars">\n'+'\n'.join(f'<div class="ob-bar {cls}"><span>{k}</span><i style="width:{n/m*100:.0f}%"></i><b>{n}</b></div>' for k, n in items)+'\n</div>'
N = len(p)
teams = collections.Counter(sh(x['team']) for x in p).most_common(9)
pos = collections.Counter(x['position'] for x in p).most_common()
cut = sorted(g(x) for x in p); a, b = cut[N//3], cut[2*N//3]
grp = [('A', f'{a-1}年以前卒', lambda v: v < a), ('B', f'{a}〜{b-1}年卒', lambda v: a <= v < b), ('C', f'{b}年以降卒', lambda v: v >= b)]
gt = '| 卒業年（推定） | 人数 | 進学先の多い大学 |\n|---|---|---|\n'
for _, lab, f in grp:
    v = [x for x in p if f(g(x))]
    c = collections.Counter(uv(x) for x in v if uv(x)).most_common(4)
    gt += f'| {lab} | {len(v)} | '+'、'.join(f'{u}{n}' for u, n in c)+' |\n'
top = sorted(p, key=lambda x: -(x['league_one_caps'] or 0))[:7]
rk = '<div class="ob-rank">\n'+''.join(f'<div class="ob-row"><em>{i}</em><div><b>{x["name_ja"]}</b><small><span class="ob-pos">{x["position"]}</span>{x["age"]}歳・{g(x)}年卒・{sh(x["team"])}・{uv(x) or "大学なし"}</small></div><strong>{x["league_one_caps"]}<small>試合</small></strong></div>\n' for i, x in enumerate(top, 1))+'</div>'
source = open('src/content/news/hanazono-2026-51-teams-contenders.md').read()
source_name = '東海大大阪仰星' if short == '東海大仰星' else short
m = re.search(rf'### {source_name}.*?(?=\n### |\n## |\Z)', source, re.S)
cards = re.findall(rf'<div class="hs-c[^"\n]*"><b>{source_name}</b>.*?</div>', source)
if m:
    rec = m.group(0)
elif cards:
    rec = cards[-1]
elif short == '御所実業':
    rec = next(line for line in source.splitlines() if line.startswith('- **御所実（'))
else:
    sys.exit(f'{source_name}: 51校記事に該当ブロックなし')
rec = rec.replace('**', '')
rec = re.sub(r'^### ', '#### ', rec, flags=re.M)
scope = '、'.join(f'「{name}」' for name in aliases)
school_links = '\n\n'.join(f'[{name} 出身選手一覧 →](/schools/{name})' for name in aliases)
season_intro = f'花園2026に出場する{short}。' if short != '御所実業' else '花園2026の奈良予選決勝で敗れた御所実業。'
slug = f'hanazono-school-{rom}-ob-2026'
out = f'''---
title: "{short}ラグビー部の出身選手{N}人（要推敲：見出しの訴求を学校ごとに作る）"
description: "{season_intro}リーグワン2025-26に登録された出身{N}人を、所属チーム・進路大学（卒業年別）・ポジション・年齢つき出場数で集計。"
pubDate: 2026-11-23
category: "NEWS"
tags: ["高校ラグビー", "花園", "{short}", "出身選手", "リーグワン", "ラグビー"]
draft: true
---

（要記入：導入。出場回数・前回成績・予選結果を51校記事から1〜2文）

> データ基準日：2026年11月23日。リーグワン2025-26の登録選手のうち出身高校が{scope}の{N}人です。引退した選手、海外クラブの選手、リーグワン外の選手は含みません。年齢はDB登録時点、卒業年は生年月日からの推定です。

{rec}

## {N}人の所属チーム

{bars(teams)}

## 進路（現役選手の世代別）

{gt}
現役選手のみの集計です。引退した世代の進路は含まれません。

## ポジション

{bars(pos, 'ob-q')}

## リーグワン出場数の多い選手

出場数と年齢をあわせて見られるよう、年齢と卒業年（推定）を併記します。

{rk}

（要記入：年齢と出場数の関係を1〜2文。事実はこの表の範囲で）

## 全{N}人の一覧

{school_links}

---

出典：リーグワン公式サイトの2025-26登録選手情報を集計。大会成績は第106回大会の各予選結果と公式発表に基づきます。
'''
open(f'src/content/news/{slug}.md', 'w').write(out)
print(slug, N, '人 / 要記入箇所:', out.count('要記入')+out.count('要推敲'))
