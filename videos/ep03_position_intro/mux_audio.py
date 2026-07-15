import json, subprocess, sys, glob, os

# ナレーション開始オフセット（index.html のタイムラインコメントと一致）
OFFSETS = {
    "e1": 0.4, "e2": 14.8, "e3": 27.2, "e4": 43.6, "e5": 58.6,
    "e6": 73.4, "e7": 83.1, "e8": 94.2, "e9": 103.4, "e10": 127.5,
}
OUT = "ep03_final.mp4"

video = sys.argv[1] if len(sys.argv) > 1 else max(glob.glob("renders/*.mp4"), key=os.path.getmtime)
durs = json.load(open("durations.json"))
keys = list(OFFSETS)

# 尺オーバー検査（次の行に食い込んでいないか）
for a, b in zip(keys, keys[1:]):
    end = OFFSETS[a] + durs[a]
    if end > OFFSETS[b]:
        raise SystemExit(f"overlap: {a} ends {end:.2f} > {b} starts {OFFSETS[b]}")

cmd = ["ffmpeg", "-y", "-i", video]
for k in keys:
    cmd += ["-i", f"audio/{k}.mp3"]

delays = "".join(
    f"[{i+1}:a]adelay={int(OFFSETS[k]*1000)}|{int(OFFSETS[k]*1000)}[a{i}];"
    for i, k in enumerate(keys)
)
mix = "".join(f"[a{i}]" for i in range(len(keys)))
filt = f"{delays}{mix}amix=inputs={len(keys)}:dropout_transition=0:normalize=0[out]"

cmd += ["-filter_complex", filt, "-map", "0:v", "-map", "[out]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", OUT]
subprocess.run(cmd, check=True)
print("wrote", OUT, "from", video)
