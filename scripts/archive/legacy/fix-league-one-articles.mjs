/**
 * fix-league-one-articles.mjs
 * リーグワンチーム記事のセクション4（日本人選手）とセクション5（外国人選手）を
 * 実際の選手データから再生成して上書きする。
 * Usage: node scripts/fix-league-one-articles.mjs
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

// チーム名 → 記事スラッグ マッピング
const TEAM_TO_SLUG = {
  'クボタスピアーズ船橋・東京ベイ':     'kubota-spears-funabashi-tokyo-bay',
  '東京サントリーサンゴリアス':          'tokyo-suntory-sungoliath',
  'トヨタヴェルブリッツ':                'toyota-verblitz',
  'コベルコ神戸スティーラーズ':          'kobelco-kobe-steelers',
  '埼玉パナソニックワイルドナイツ':      'saitama-panasonic-wild-knights',
  '東芝ブレイブルーパス東京':            'toshiba-brave-lupus-tokyo',
  '横浜キヤノンイーグルス':              'yokohama-canon-eagles',
  '三重ホンダヒート':                    'mie-honda-heat',
  '三菱重工相模原ダイナボアーズ':        'mitsubishi-sagamihara-dynaboars',
  'リコーブラックラムズ東京':            'ricoh-black-rams-tokyo',
  'NECグリーンロケッツ東葛':             'nec-green-rockets-tokatsu',
  '九州電力キューデンヴォルテクス':      'kyuden-voltex',
  '清水建設江東ブルーシャークス':        'shimizu-koto-blue-sharks',
  '豊田自動織機シャトルズ愛知':          'toyota-shuttles-aichi',
  '日本製鉄釜石シーウェイブス':          'kamaishi-seawaves',
  '花園近鉄ライナーズ':                  'hanazono-kintetsu-liners',
  '日野レッドドルフィンズ':              'hino-red-dolphins',
  'レッドハリケーンズ大阪':              'hurricanes',
  'クリタウォーターガッシュ昭島':        'kurita-water-gush-akishima',
  '狭山セコムラガッツ':                  'secom-rugguts',
  '中国電力レッドレグリオンズ':          'chugoku-electric-red-regulions',
  'マツダスカイアクティブズ広島':        'mazda-skyactivs-hiroshima',
  'ヤクルトレビンズ戸田':                'yakult-levins',
  '静岡ブルーレヴズ':                    'shizuoka-blue-revs',
  '浦安D-Rocks':                         'urayasu-d-rocks',
  'ルリーロ福岡':                        'ruriro-fukuoka',
};

// 選手データ読み込み
function loadPlayers() {
  const dir = path.join(ROOT, 'src/content/players/pro');
  const players = [];
  for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith('.md')) continue;
    const content = fs.readFileSync(path.join(dir, f), 'utf-8');
    const fm = parseFrontmatter(content);
    if (!fm.league || !fm.league.includes('league-one')) continue;
    if (!fm.team) continue;
    // 年度部分を除去
    const team = fm.team.replace(/（\d{4}-\d{2,4}.*?）/, '').trim();
    if (!team) continue;
    players.push({
      slug: f.replace(/\.md$/, ''),
      name_ja: (fm.name_ja || '').trim(),
      name_en: (fm.name_en || '').trim(),
      position: (fm.position || '').trim(),
      caps: (fm.caps || '').trim(),
      league_one_caps: parseInt(fm.league_one_caps || '0', 10) || 0,
      team,
    });
  }
  return players;
}

// 簡易フロントマターパーサ
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};
  const fm = {};
  for (const line of match[1].split('\n')) {
    const m = line.match(/^(\w+):\s*["']?(.*?)["']?\s*$/);
    if (m) fm[m[1]] = m[2];
  }
  return fm;
}

// 日本語名に漢字が含まれるか（日本人判定）
function hasKanji(str) {
  return /[\u4e00-\u9fff\u3400-\u4dbf]/.test(str);
}

// 国代表キャップを抽出
function extractCaps(capsStr) {
  if (!capsStr) return null;
  // "NZ代表(125)" や "日本代表(63)" など（代表という漢字が含まれるパターン）
  const m = capsStr.match(/([\w\u3040-\u9fff\uFF00-\uFFEF]*代表)\s*[\(\（](\d+)[\)\）]/);
  if (m) return { label: m[1], count: parseInt(m[2], 10) };
  // "日本代表(63キャップ)"
  const m3 = capsStr.match(/([^\(]+代表)\((\d+)キャップ\)/);
  if (m3) return { label: m3[1], count: parseInt(m3[2], 10) };
  // "South Africa (63)" や "New Zealand (125)" など英語国名フォーマット（上記と非重複）
  const m2 = capsStr.match(/^([A-Za-z][A-Za-z\s]+?)\s*\((\d+)\)\s*$/);
  if (m2) return { label: m2[1].trim() + '代表', count: parseInt(m2[2], 10) };
  return null;
}

// 選手エントリ生成
function formatPlayer(p) {
  // 外国籍（カタカナ名）のみスペースを中黒に変換、日本人名はそのまま
  const name = hasKanji(p.name_ja)
    ? p.name_ja.replace(/\s+/g, '')   // 日本語名: スペース除去（例: "北川 賢吾" → "北川賢吾"）
    : p.name_ja.replace(/\s+/g, '・'); // 外国籍名: スペースを中黒に（例: "アーロン スミス" → "アーロン・スミス"）
  const cap = extractCaps(p.caps);
  const capStr = cap ? `${cap.label}${cap.count}キャップ` : '';
  const lo = p.league_one_caps > 0 ? `リーグワン${p.league_one_caps}キャップ` : '';
  return `**${name}**（${p.position}${capStr ? '、' + capStr : ''}）：${lo || 'チームの戦力として活躍'}。`;
}

// セクション4・5 を再生成
function buildSections(teamName, players) {
  const teamPlayers = players.filter(p => p.team === teamName);

  // 日本人代表選手（漢字名 + 代表歴 or リーグワン30キャップ以上）
  const jpInt = teamPlayers
    .filter(p => hasKanji(p.name_ja) && extractCaps(p.caps))
    .sort((a, b) => {
      const ca = extractCaps(a.caps)?.count || 0;
      const cb = extractCaps(b.caps)?.count || 0;
      return cb - ca;
    });

  // 外国籍代表選手（カタカナ名 + 代表歴）
  const foreignInt = teamPlayers
    .filter(p => !hasKanji(p.name_ja) && extractCaps(p.caps))
    .sort((a, b) => {
      const ca = extractCaps(a.caps)?.count || 0;
      const cb = extractCaps(b.caps)?.count || 0;
      return cb - ca;
    });

  // 代表歴なしでリーグワン実績（30キャップ以上）
  const jpVet = teamPlayers
    .filter(p => hasKanji(p.name_ja) && !extractCaps(p.caps) && p.league_one_caps >= 30)
    .sort((a, b) => b.league_one_caps - a.league_one_caps)
    .slice(0, 3);

  const foreignVet = teamPlayers
    .filter(p => !hasKanji(p.name_ja) && !extractCaps(p.caps) && p.league_one_caps >= 30)
    .sort((a, b) => b.league_one_caps - a.league_one_caps)
    .slice(0, 3);

  const sec4Lines = ['## 4. チームを牽引する日本人選手・代表勢', ''];
  if (jpInt.length > 0) {
    sec4Lines.push('### 現役代表（2026年所属選手）', '');
    for (const p of jpInt) sec4Lines.push(formatPlayer(p), '');
  }
  if (jpVet.length > 0) {
    sec4Lines.push('### リーグワン実績選手', '');
    for (const p of jpVet) sec4Lines.push(formatPlayer(p), '');
  }
  if (jpInt.length === 0 && jpVet.length === 0) {
    sec4Lines.push('現在、代表経験を持つ日本人選手のデータを更新中です。', '');
  }

  const sec5Lines = ['## 5. チームを支える外国人選手・世界的スター', ''];
  if (foreignInt.length > 0) {
    sec5Lines.push('### 現役外国籍選手（2026年所属）', '');
    for (const p of foreignInt) sec5Lines.push(formatPlayer(p), '');
  }
  if (foreignVet.length > 0) {
    sec5Lines.push('### リーグワン実績外国籍選手', '');
    for (const p of foreignVet) sec5Lines.push(formatPlayer(p), '');
  }
  if (foreignInt.length === 0 && foreignVet.length === 0) {
    sec5Lines.push('現在、外国籍選手のデータを更新中です。', '');
  }

  return {
    sec4: sec4Lines.join('\n').trimEnd(),
    sec5: sec5Lines.join('\n').trimEnd(),
  };
}

// 記事のセクション4・5を置換
function replaceArticleSections(articlePath, sec4, sec5) {
  const content = fs.readFileSync(articlePath, 'utf-8');

  // セクション4: "## 4." から次の "## 5." の直前まで
  // セクション5: "## 5." から次の "## 6." の直前まで（または EOF）

  let result = content;

  // まず sec4 置換: ## 4. ～ ## 5. の直前
  result = result.replace(
    /(## 4\.[\s\S]*?)(?=## 5\.)/,
    sec4 + '\n\n'
  );

  // 次に sec5 置換: ## 5. ～ ## 6. の直前（or EOF）
  result = result.replace(
    /(## 5\.[\s\S]*?)(?=## 6\.)/,
    sec5 + '\n\n'
  );

  if (result === content) {
    console.warn(`  ⚠️  セクション未検出、スキップ: ${path.basename(articlePath)}`);
    return false;
  }

  fs.writeFileSync(articlePath, result, 'utf-8');
  return true;
}

// メイン
function main() {
  const players = loadPlayers();
  console.log(`選手データ読み込み: ${players.length}名`);

  const articleDir = path.join(ROOT, 'src/content/teams/league-one');
  let updated = 0;

  for (const [teamName, slug] of Object.entries(TEAM_TO_SLUG)) {
    const articlePath = path.join(articleDir, `${slug}.md`);
    if (!fs.existsSync(articlePath)) {
      console.warn(`  記事ファイルなし: ${slug}.md`);
      continue;
    }

    const { sec4, sec5 } = buildSections(teamName, players);
    const ok = replaceArticleSections(articlePath, sec4, sec5);
    if (ok) {
      const count = players.filter(p => p.team === teamName).length;
      console.log(`  ✓ ${teamName} (${count}名) → ${slug}.md`);
      updated++;
    }
  }

  console.log(`\n完了: ${updated}/${Object.keys(TEAM_TO_SLUG).length} チーム更新`);
}

main();
