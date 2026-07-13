import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const TEAMS_DIR = path.join(ROOT, 'src/content/teams');
const PLAYERS_DIR = path.join(ROOT, 'src/content/players');
const STUB_OUT_DIR = path.join(PLAYERS_DIR, 'pro');

// ---- helpers ----

function walkDir(dir, ext = '.md') {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) results.push(...walkDir(full, ext));
    else if (entry.isFile() && entry.name.endsWith(ext)) results.push(full);
  }
  return results;
}

function parseFrontmatter(content) {
  const m = content.match(/^---\n([\s\S]*?)\n---/);
  if (!m) return {};
  const fm = {};
  for (const line of m[1].split('\n')) {
    const idx = line.indexOf(':');
    if (idx < 0) continue;
    const key = line.slice(0, idx).trim();
    let val = line.slice(idx + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) ||
        (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    fm[key] = val;
  }
  return fm;
}

// All known rugby position codes
const POSITION_CODES = new Set([
  'PR','HO','LO','FL','No8','NO8','No.8','SH','SO','CTB','WTB','FB',
  'LOC','LOCK','FLANK','PROP','HOOKER','SCRUM','FLY','CENTRE','CENTER','WING','FULLBACK',
  'WH','PC','TL','SL','SB','AR',
]);

function extractPositionFromInfo(info) {
  // Split on Japanese/ASCII comma and whitespace
  const parts = info.split(/[,、，\s]+/);
  for (const p of parts) {
    const t = p.trim();
    if (POSITION_CODES.has(t)) return t;
    // 2-3 uppercase: could be position (PR, HO, LO, FL, SH, SO, etc.)
    if (/^[A-Z]{2,3}$/.test(t) && !['HC','AC','OB','NZ','AU','SA','EN','SC','IR','WA','FR','IT','CA','NA','UR','GE','RO','SP','PO','NR','SR','WC','RW','WC','WR','FW','BK'].includes(t)) return t;
    // No.8 style
    if (/^No\.?[0-9]$/.test(t)) return t;
  }
  return '';
}

function extractCapsFromInfo(info) {
  const m = info.match(/([0-9]+)キャップ|([0-9]+)\s*caps/i);
  return m ? (m[1] || m[2]) + 'caps' : '';
}

/**
 * An info string inside （...） qualifies as player info if it contains:
 * - a position code, OR
 * - a known country/nationality indicator, OR
 * - "代表" (national team), OR
 * - "出身" or "大学卒" (player background info), OR
 * - N caps info
 */
function infoQualifiesAsPlayer(info) {
  if (!info || info.length > 80) return false;

  const pos = extractPositionFromInfo(info);
  if (pos) return true;

  // Country/nationality patterns
  if (/代表|キャップ|caps|出身|大学卒|高校卒|育ち/i.test(info)) return true;

  // Known country names
  const countries = ['サモア','フィジー','トンガ','南アフリカ','アルゼンチン','ニュージーランド',
    'オーストラリア','イングランド','スコットランド','アイルランド','ウェールズ','フランス','イタリア',
    'ジョージア','ナミビア','ウルグアイ','カナダ','ルーマニア','スペイン','ポルトガル','日本'];
  if (countries.some(c => info.includes(c))) return true;

  return false;
}

/**
 * Validate that a name string looks like a person's name, not a team/place/phrase.
 */
function isValidPersonName(name) {
  if (!name || name.length < 2 || name.length > 20) return false;

  // Reject if contains sentence-like patterns
  if (/。|、|「|」|【|】|『|』|…/.test(name)) return false;

  // Reject if starts with hiragana particles or common non-name hiragana
  if (/^[はがをにでもとのへやからまでよりは]/.test(name)) return false;

  // Reject if contains numbers
  if (/[0-9０-９]/.test(name)) return false;

  // Reject known non-person words (these appear as section headers or team refs)
  const rejectWords = [
    '現役','歴代','外国籍','日本人','レジェンド','期待','功労','スター',
    'ヘッドコーチ','チーム','リーグ','スタジアム','フィールド','ホーム',
    '代表ロック','代表SO','代表SH','代表FL',
    'ルーキー','新星','招集','スクラム','ラインアウト','モール',
    // team name fragments
    'レグリオンズ','シーウェイブス','ライナーズ','ドルフィンズ',
    'ブルーシャークス','ブルーレヴズ','グリーンロケッツ','ブレイブルーパス',
    'ブラックラムズ','ヴェルブリッツ','イーグルス','サンゴリアス',
    'ワイルドナイツ','スティーラーズ','スパークス','レッドハリケーンズ',
    'ビアズ','ダイナボアーズ',
    // English team fragments
    'Regulions', 'Gush', 'Rockets', 'Sharks', 'Revs', 'Lupus', 'Fijians',
  ];
  if (rejectWords.some(w => name === w || name.startsWith(w + '・') || name.includes(w))) return false;

  // Reject if it looks like a sentence fragment (contains verb forms etc)
  if (/てきた|のです|している|として|により|おいて|以来|にかけ/.test(name)) return false;

  return true;
}

// ---- Extract player mentions from team articles (line-by-line) ----

function extractPlayersFromArticle(content) {
  const players = [];
  const LPAR = '\uff08'; // （
  const RPAR = '\uff09'; // ）

  for (const rawLine of content.split('\n')) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#') || line.startsWith('|') || line.startsWith('---')) continue;
    if (!line.includes(LPAR)) continue;

    // Find all occurrences of <name>（<info>）on this line
    // name: non-paren chars before （
    // We scan left from each （ to find the name
    let searchLine = line;
    let offset = 0;

    while (true) {
      const lIdx = searchLine.indexOf(LPAR);
      if (lIdx < 0) break;

      const rIdx = searchLine.indexOf(RPAR, lIdx);
      if (rIdx < 0) break;

      const info = searchLine.slice(lIdx + 1, rIdx);

      // Extract name: everything between last sentence boundary and lIdx
      const beforeParen = searchLine.slice(0, lIdx);
      // Find last "name boundary" - period, colon, whitespace, bracket, etc.
      const nameMatch = beforeParen.match(/(?:^|[。、：\uff1a\s「」【】\n])([^\s。、：\uff1a「」【】（）]{2,20})$/);
      const name = nameMatch ? nameMatch[1].trim() : '';

      if (name && isValidPersonName(name) && infoQualifiesAsPlayer(info)) {
        const position = extractPositionFromInfo(info);
        const caps = extractCapsFromInfo(info);
        players.push({ name, nameType: /^[A-Z]/.test(name) ? 'en' : 'ja', position, caps });
      }

      // Move past this match
      searchLine = searchLine.slice(rIdx + 1);
    }
  }

  return players;
}

// ---- Build DB from existing player files ----

function buildPlayerDB() {
  const files = walkDir(PLAYERS_DIR);
  const db = [];

  for (const fp of files) {
    const content = fs.readFileSync(fp, 'utf8');
    const fm = parseFrontmatter(content);
    const names = new Set();
    if (fm.title) names.add(fm.title.trim());
    if (fm.name_en) names.add(fm.name_en.trim());
    if (fm.name_ja) {
      names.add(fm.name_ja.trim());
      names.add(fm.name_ja.replace(/\s/g, '').trim());
    }

    // Parse existing aliases
    const aliasLineMatch = content.match(/^aliases:\s*\[([^\]]*)\]/m);
    const aliases = [];
    if (aliasLineMatch) {
      const raw = aliasLineMatch[1];
      for (const m of raw.matchAll(/"([^"]+)"|'([^']+)'/g)) {
        aliases.push((m[1] || m[2]).trim());
      }
    }
    for (const a of aliases) names.add(a);

    db.push({
      slug: fm.slug || path.basename(fp, '.md'),
      filePath: fp,
      names: [...names].filter(Boolean),
      name_ja: fm.name_ja || '',
      name_en: fm.name_en || '',
      aliases,
    });
  }
  return db;
}

function normalizeForLookup(name) {
  return name.toLowerCase().replace(/\s/g, '').replace(/　/g, '');
}

function findInDB(db, name) {
  const norm = normalizeForLookup(name);
  for (const entry of db) {
    for (const n of entry.names) {
      if (normalizeForLookup(n) === norm) return entry;
    }
  }
  return null;
}

/**
 * Strict fuzzy match: same first 4+ chars for katakana names.
 * Also checks that the names are similar length (within 3 chars).
 * Used only to suggest aliases, not auto-apply.
 */
function findFuzzyMatch(db, name) {
  if (/^[A-Za-z]/.test(name)) return null;
  // Need at least 4 katakana/kanji chars
  const nameChars = [...name];
  if (nameChars.length < 4) return null;
  const prefix4 = nameChars.slice(0, 4).join('');

  for (const entry of db) {
    for (const n of entry.names) {
      if (n === name) continue;
      const nChars = [...n];
      // Check prefix
      if (!n.startsWith(prefix4)) continue;
      // Check length similarity
      if (Math.abs(nChars.length - nameChars.length) > 3) continue;
      return entry;
    }
  }
  return null;
}

// Generate slug
function toKebab(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function toHistSlug(name) {
  const chars = [...name].slice(0, 4);
  const hex = chars.map(c => c.codePointAt(0).toString(16)).join('');
  return 'hist-' + hex;
}

function makeSlug(name) {
  if (/^[A-Za-z]/.test(name)) return toKebab(name);
  return toHistSlug(name);
}

// ---- Generate stub file ----

function generateStub(player, slug) {
  const isEn = /^[A-Za-z]/.test(player.name);
  const name_en = isEn ? player.name : '';
  const name_ja = isEn ? '' : player.name;

  return `---
title: "${player.name}"
name_en: "${name_en}"
name_ja: "${name_ja}"
slug: "${slug}"
position: "${player.position || ''}"
height: ""
weight: ""
birth_date: ""
age: 0
country: ""
birth_place_scraped: ""
league: ""
team: ""
caps: "${player.caps || ''}"
high_school: ""
university: ""
junior_high_school: ""
rugby_school: ""
scraped_url: ""
league_one_caps: ""
career_history_json: '[]'
category: "pro"
---

## キャリア遍歴

`;
}

// ---- Add alias to existing DB file ----

function addAliasToFile(filePath, alias) {
  let content = fs.readFileSync(filePath, 'utf8');
  if (/^aliases:/m.test(content)) {
    content = content.replace(/^(aliases:\s*\[)(.*?)(\])/m, (_, pre, mid, suf) => {
      const existing = mid.trim();
      const newVal = existing ? `${existing}, "${alias}"` : `"${alias}"`;
      return `${pre}${newVal}${suf}`;
    });
  } else {
    content = content.replace(/^(---\n)/, `$1aliases: ["${alias}"]\n`);
  }
  fs.writeFileSync(filePath, content, 'utf8');
}

// ---- Main ----

const teamFiles = walkDir(TEAMS_DIR);
console.log(`Team articles found: ${teamFiles.length}`);

const db = buildPlayerDB();
console.log(`Player DB entries: ${db.length}`);

// Deduplicate extracted names
const allExtracted = new Map(); // normalizedName -> player info

for (const tf of teamFiles) {
  const content = fs.readFileSync(tf, 'utf8');
  const players = extractPlayersFromArticle(content);
  for (const p of players) {
    const key = normalizeForLookup(p.name);
    if (!allExtracted.has(key)) {
      allExtracted.set(key, p);
    } else {
      const existing = allExtracted.get(key);
      if (!existing.position && p.position) existing.position = p.position;
      if (!existing.caps && p.caps) existing.caps = p.caps;
    }
  }
}

console.log(`Unique player names extracted: ${allExtracted.size}`);

let matched = 0;
let stubsCreated = 0;
let aliasesAdded = 0;
let skipped = 0;
const fuzzyLog = [];

for (const [key, player] of allExtracted) {
  const dbEntry = findInDB(db, player.name);
  if (dbEntry) {
    matched++;
    continue;
  }

  // Check strict fuzzy match for alias
  const fuzzy = findFuzzyMatch(db, player.name);
  if (fuzzy) {
    const alreadyAliased = fuzzy.aliases.some(
      a => normalizeForLookup(a) === normalizeForLookup(player.name)
    );
    if (!alreadyAliased) {
      try {
        addAliasToFile(fuzzy.filePath, player.name);
        fuzzy.aliases.push(player.name);
        fuzzy.names.push(player.name);
        aliasesAdded++;
        fuzzyLog.push(`  ALIAS: "${player.name}" -> ${path.basename(fuzzy.filePath)}`);
      } catch (e) {
        console.error(`  Error adding alias: ${e.message}`);
      }
    }
    matched++;
    continue;
  }

  // Create stub
  const slug = makeSlug(player.name);
  const outPath = path.join(STUB_OUT_DIR, `${slug}.md`);

  if (fs.existsSync(outPath)) {
    skipped++;
    continue;
  }

  try {
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, generateStub(player, slug), 'utf8');
    stubsCreated++;
    console.log(`  STUB: ${slug}.md  [${player.name}] pos=${player.position || '(none)'}`);
  } catch (e) {
    console.error(`  Error creating stub for ${player.name}: ${e.message}`);
  }
}

// Print aliases at end
if (fuzzyLog.length) {
  console.log('\nAliases added:');
  fuzzyLog.forEach(l => console.log(l));
}

console.log('\n=== Summary ===');
console.log(`Team articles:  ${teamFiles.length}`);
console.log(`Player DB:      ${db.length}`);
console.log(`Extracted:      ${allExtracted.size}`);
console.log(`Matched in DB:  ${matched - aliasesAdded}`);
console.log(`Aliases added:  ${aliasesAdded}`);
console.log(`Stubs created:  ${stubsCreated}`);
console.log(`Already exist:  ${skipped}`);
