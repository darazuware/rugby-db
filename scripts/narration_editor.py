#!/usr/bin/env python3.11
"""スマホ用ナレーション編集エディタ（videos/ep*/gen_audio.py の LINES を編集・再生成）

起動:  python3.11 scripts/narration_editor.py
       → 表示された http://<LAN IP>:8765 をスマホのブラウザで開く
"""
import ast
import asyncio
import json
import mimetypes
import re
import socket
import subprocess
import sys
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEOS = ROOT / "videos"
PORT = 8765
LINES_RE = re.compile(r"^LINES = \[.*?^\]", re.S | re.M)


# ---------- gen_audio.py の LINES 読み書き ----------

def ep_dirs():
    return sorted(d for d in VIDEOS.iterdir() if (d / "gen_audio.py").exists())


def read_lines(ep: Path):
    src = (ep / "gen_audio.py").read_text(encoding="utf-8")
    m = LINES_RE.search(src)
    if not m:
        raise ValueError(f"LINES が見つかりません: {ep.name}")
    rows = ast.literal_eval(m.group(0).split("=", 1)[1].strip())
    out = []
    for r in rows:
        if len(r) == 3:
            out.append({"key": r[0], "who": r[1], "text": r[2]})
        else:
            out.append({"key": r[0], "who": "N", "text": r[1]})
    return out


def write_lines(ep: Path, rows):
    path = ep / "gen_audio.py"
    src = path.read_text(encoding="utf-8")
    m = LINES_RE.search(src)
    arity3 = len(ast.literal_eval(m.group(0).split("=", 1)[1].strip())[0]) == 3
    body = []
    for r in rows:
        if arity3:
            body.append(f'    ({json.dumps(r["key"], ensure_ascii=False)}, '
                        f'{json.dumps(r["who"], ensure_ascii=False)}, '
                        f'{json.dumps(r["text"], ensure_ascii=False)}),')
        else:
            body.append(f'    ({json.dumps(r["key"], ensure_ascii=False)}, '
                        f'{json.dumps(r["text"], ensure_ascii=False)}),')
    block = "LINES = [\n" + "\n".join(body) + "\n]"
    path.write_text(src[:m.start()] + block + src[m.end():], encoding="utf-8")


def durations(ep: Path):
    f = ep / "durations.json"
    return json.loads(f.read_text()) if f.exists() else {}


# ---------- TTS ----------

def voicevox(text, base: Path, speaker=3):
    q = urllib.parse.urlencode({"text": text, "speaker": speaker})
    req = urllib.request.Request(f"http://127.0.0.1:50021/audio_query?{q}", method="POST")
    query = json.loads(urllib.request.urlopen(req).read())
    query["speedScale"] = 1.05
    req2 = urllib.request.Request(
        f"http://127.0.0.1:50021/synthesis?speaker={speaker}",
        data=json.dumps(query).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    wav = base.with_suffix(".wav")
    wav.write_bytes(urllib.request.urlopen(req2).read())
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(wav),
                    str(base.with_suffix(".mp3"))], check=True)
    wav.unlink(missing_ok=True)


def synth(ep: Path, key: str, who: str, text: str) -> float:
    import edge_tts
    (ep / "audio").mkdir(exist_ok=True)
    base = ep / "audio" / key
    if who == "Z":
        voicevox(text, base)
    else:
        asyncio.run(edge_tts.Communicate(text, "ja-JP-NanamiNeural").save(str(base.with_suffix(".mp3"))))
    d = float(subprocess.check_output(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(base.with_suffix(".mp3"))]))
    d = round(d, 3)
    durs = durations(ep)
    durs[key] = d
    (ep / "durations.json").write_text(json.dumps(durs, ensure_ascii=False, indent=1), encoding="utf-8")
    return d


# ---------- HTTP ----------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body: bytes, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode())

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        parts = [x for x in p.path.split("/") if x]
        try:
            if not parts:
                return self._send(200, HTML.encode(), "text/html; charset=utf-8")
            if parts == ["api", "episodes"]:
                return self._json([d.name for d in ep_dirs()])
            if len(parts) == 3 and parts[:2] == ["api", "episode"]:
                ep = VIDEOS / parts[2]
                durs = durations(ep)
                rows = read_lines(ep)
                for r in rows:
                    r["dur"] = durs.get(r["key"])
                    r["has_audio"] = (ep / "audio" / f'{r["key"]}.mp3').exists()
                return self._json({"episode": ep.name, "lines": rows})
            if len(parts) == 3 and parts[0] == "audio":
                f = VIDEOS / parts[1] / "audio" / parts[2]
                if not f.exists():
                    return self._json({"error": "not found"}, 404)
                return self._send(200, f.read_bytes(),
                                  mimetypes.guess_type(f.name)[0] or "audio/mpeg")
            self._json({"error": "not found"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def do_POST(self):
        p = urllib.parse.urlparse(self.path)
        parts = [x for x in p.path.split("/") if x]
        n = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(n) or b"{}")
        try:
            ep = VIDEOS / data["episode"]
            if parts == ["api", "save"]:
                write_lines(ep, data["lines"])
                return self._json({"ok": True})
            if parts == ["api", "tts"]:
                rows = read_lines(ep)
                for r in rows:
                    if r["key"] == data["key"]:
                        r["text"] = data["text"]
                write_lines(ep, rows)
                row = next(r for r in rows if r["key"] == data["key"])
                d = synth(ep, row["key"], row["who"], row["text"])
                return self._json({"ok": True, "dur": d})
            self._json({"error": "not found"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)


HTML = r"""<!doctype html>
<html lang="ja"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>ナレーション編集</title>
<style>
:root{
  --bg:#0f1115; --card:#181b22; --line:#272b34; --fg:#e8eaef; --sub:#8b93a3;
  --acc:#4c9aff; --ok:#2fbf71; --row:36px;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;background:var(--bg);color:var(--fg);
  font:15px/1.6 -apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;
  padding:44px 8px calc(52px + env(safe-area-inset-bottom))}
header{position:fixed;top:0;left:0;right:0;height:44px;display:flex;gap:8px;align-items:center;
  padding:0 8px;background:rgba(15,17,21,.92);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--line);z-index:10}
select{flex:1;min-width:0;background:var(--card);color:var(--fg);border:1px solid var(--line);
  border-radius:8px;padding:6px 8px;font-size:15px}
#status{font-size:12px;color:var(--sub);white-space:nowrap}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;
  margin:8px 0;padding:8px}
.head{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--sub);margin-bottom:4px}
.who{border:1px solid var(--line);border-radius:4px;padding:0 5px}
textarea{width:100%;background:transparent;color:var(--fg);border:0;resize:none;
  font:inherit;padding:0;outline:none;overflow:hidden}
/* 操作行: 波形もボタンも1行に収める（縦を食わない） */
.bar{display:flex;align-items:center;gap:6px;height:var(--row);margin-top:4px}
.btn{flex:0 0 auto;width:var(--row);height:var(--row);border-radius:8px;border:1px solid var(--line);
  background:#20242d;color:var(--fg);font-size:15px;display:flex;align-items:center;
  justify-content:center;padding:0}
.btn:active{background:#2b3140}
.btn[disabled]{opacity:.4}
canvas{flex:1 1 auto;min-width:0;height:24px;display:block}
.dur{flex:0 0 auto;font-size:11px;color:var(--sub);font-variant-numeric:tabular-nums;min-width:38px;text-align:right}
.dirty{border-color:var(--acc)}
footer{position:fixed;left:0;right:0;bottom:0;display:flex;gap:8px;padding:8px;
  padding-bottom:calc(8px + env(safe-area-inset-bottom));background:rgba(15,17,21,.92);
  backdrop-filter:blur(8px);border-top:1px solid var(--line);z-index:10}
footer button{flex:1;height:36px;border-radius:8px;border:1px solid var(--line);
  background:#20242d;color:var(--fg);font-size:14px}
footer button.p{background:var(--acc);border-color:var(--acc);color:#fff}
</style></head><body>

<header>
  <select id="ep"></select>
  <span id="status"></span>
</header>
<main id="list"></main>
<footer>
  <button id="save" class="p">保存</button>
  <button id="regenAll">未生成を再生成</button>
</footer>

<script>
const $ = s => document.querySelector(s);
let EP = null, LINES = [], AC = null;

const status = t => { $('#status').textContent = t; };

async function api(path, body) {
  const r = await fetch(path, body ? {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({episode: EP, ...body})
  } : undefined);
  const j = await r.json();
  if (j.error) { status('エラー: ' + j.error); throw new Error(j.error); }
  return j;
}

function autosize(ta) { ta.style.height = 'auto'; ta.style.height = ta.scrollHeight + 'px'; }

async function drawWave(cv, url) {
  try {
    AC = AC || new (window.AudioContext || window.webkitAudioContext)();
    const buf = await AC.decodeAudioData(await (await fetch(url)).arrayBuffer());
    const dpr = devicePixelRatio || 1;
    const w = cv.clientWidth, h = cv.clientHeight;
    cv.width = w * dpr; cv.height = h * dpr;
    const g = cv.getContext('2d'); g.scale(dpr, dpr); g.clearRect(0, 0, w, h);
    const d = buf.getChannelData(0), bars = Math.max(1, Math.floor(w / 3));
    const step = Math.floor(d.length / bars);
    g.fillStyle = '#4c9aff';
    for (let i = 0; i < bars; i++) {
      let peak = 0;
      for (let j = 0; j < step; j += 8) { const v = Math.abs(d[i * step + j] || 0); if (v > peak) peak = v; }
      const bh = Math.max(1, peak * h);
      g.fillRect(i * 3, (h - bh) / 2, 2, bh);
    }
  } catch (e) { /* 波形は失敗しても操作を止めない */ }
}

function render(lines) {
  LINES = lines;
  const list = $('#list'); list.innerHTML = '';
  lines.forEach((L, i) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="head"><span class="who">${L.who}</span><span>${L.key}</span></div>
      <textarea rows="1"></textarea>
      <div class="bar">
        <button class="btn play" ${L.has_audio ? '' : 'disabled'}>▶</button>
        <canvas></canvas>
        <span class="dur">${L.dur ? L.dur.toFixed(1) + 's' : '—'}</span>
        <button class="btn gen">⟳</button>
      </div>`;
    const ta = card.querySelector('textarea');
    const cv = card.querySelector('canvas');
    const dur = card.querySelector('.dur');
    const play = card.querySelector('.play');
    const gen = card.querySelector('.gen');
    const src = () => `/audio/${EP}/${L.key}.mp3?t=${L.dur || 0}`;

    ta.value = L.text;
    ta.addEventListener('input', () => {
      autosize(ta); L.text = ta.value; card.classList.add('dirty');
    });

    let audio = null;
    play.onclick = () => {
      if (audio && !audio.paused) { audio.pause(); audio.currentTime = 0; play.textContent = '▶'; return; }
      audio = new Audio(src());
      audio.onended = () => play.textContent = '▶';
      audio.play(); play.textContent = '■';
    };

    gen.onclick = async () => {
      gen.disabled = true; gen.textContent = '…'; status(L.key + ' 生成中');
      try {
        const r = await api('/api/tts', {key: L.key, text: ta.value});
        L.dur = r.dur; L.has_audio = true;
        dur.textContent = r.dur.toFixed(1) + 's';
        play.disabled = false; card.classList.remove('dirty');
        await drawWave(cv, src());
        status(L.key + ' 完了');
      } finally { gen.disabled = false; gen.textContent = '⟳'; }
    };

    // 描画は DOM 挿入後（幅が確定してから）
    list.appendChild(card);
    autosize(ta);
    if (L.has_audio) drawWave(cv, src());
    card._redraw = () => { autosize(ta); if (L.has_audio) drawWave(cv, src()); };
  });
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(() => document.querySelectorAll('.card').forEach(c => c._redraw && c._redraw()));
  }
}

let rt = null;
addEventListener('resize', () => {
  clearTimeout(rt);
  rt = setTimeout(() => document.querySelectorAll('.card').forEach(c => c._redraw && c._redraw()), 200);
});

async function load(ep) {
  EP = ep; status('読込中');
  const d = await api('/api/episode/' + ep);
  render(d.lines); status('');
}

$('#save').onclick = async () => {
  status('保存中');
  await api('/api/save', {lines: LINES.map(({key, who, text}) => ({key, who, text}))});
  document.querySelectorAll('.dirty').forEach(e => e.classList.remove('dirty'));
  status('保存しました');
};

$('#regenAll').onclick = async () => {
  const targets = LINES.filter(L => !L.has_audio);
  for (const L of targets) {
    status(L.key + ' 生成中');
    await api('/api/tts', {key: L.key, text: L.text});
  }
  await load(EP);
  status('再生成 完了');
};

(async () => {
  const eps = await (await fetch('/api/episodes')).json();
  const sel = $('#ep');
  eps.forEach(e => sel.add(new Option(e, e)));
  sel.onchange = () => load(sel.value);
  if (eps.length) load(eps[0]);
})();
</script></body></html>
"""


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    print(f"スマホで開く: http://{lan_ip()}:{port}")
    print(f"PCで開く:     http://127.0.0.1:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
