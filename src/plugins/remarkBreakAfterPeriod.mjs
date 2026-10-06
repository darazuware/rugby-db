// 本文の「。」の直後で改行する（読みやすさ）。段落・リスト内のtextノードのみ対象。
// 閉じ括弧/引用符が続く場合や、ノード末尾（リンク・強調の手前）は触らない。
const SKIP = new Set(['code', 'inlineCode', 'link', 'linkReference', 'heading', 'table', 'html', 'mdxJsxFlowElement']);

function split(value) {
  const parts = [];
  let last = 0;
  const re = /。(?![」』）)\]】”"'\s])(?=.)/gs;
  let m;
  while ((m = re.exec(value))) {
    parts.push({ type: 'text', value: value.slice(last, m.index + 1) });
    parts.push({ type: 'break' });
    last = m.index + 1;
  }
  if (!parts.length) return null;
  parts.push({ type: 'text', value: value.slice(last) });
  return parts;
}

function walk(node) {
  if (!node.children || SKIP.has(node.type)) return;
  const out = [];
  for (const c of node.children) {
    if (c.type === 'text') {
      const p = split(c.value);
      if (p) out.push(...p);
      else out.push(c);
    } else {
      walk(c);
      out.push(c);
    }
  }
  node.children = out;
}

export default function remarkBreakAfterPeriod() {
  return (tree) => walk(tree);
}
