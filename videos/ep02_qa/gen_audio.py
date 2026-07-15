import asyncio, json, subprocess, urllib.request, urllib.parse, edge_tts

LINES = [
    ("n1", "N", "ラグビー超入門、素朴なギモン編。今日はずんだもんの質問に、ぜんぶ答えていきます。"),
    ("z1", "Z", "よろしくなのだ！"),
    ("z2", "Z", "補欠は何人まで登録できるのだ？"),
    ("n2", "N", "リザーブは8人まで。先発の15人と合わせて、1試合に23人まで登録できます。"),
    ("z3", "Z", "一回交代した選手は、もう一回出られるのだ？"),
    ("n3", "N", "原則、再出場はできません。ただし、出血や、脳振とうの検査による一時的な交代なら、戻ってくることができます。"),
    ("z4", "Z", "同点で終わったら、サドンデスはあるのだ？"),
    ("n4", "N", "リーグ戦では引き分けもあります。ワールドカップの決勝トーナメントでは延長戦。続いてサドンデス方式の延長。それでも決まらなければ、キック合戦で勝敗を決めます。"),
    ("n5", "N", "気になるギモンは、コメントで教えてください。"),
    ("z5", "Z", "次回も見るのだ！"),
]

def voicevox(text, path, speaker=3):
    q = urllib.parse.urlencode({"text": text, "speaker": speaker})
    req = urllib.request.Request(f"http://127.0.0.1:50021/audio_query?{q}", method="POST")
    query = json.loads(urllib.request.urlopen(req).read())
    query["speedScale"] = 1.05
    req2 = urllib.request.Request(
        f"http://127.0.0.1:50021/synthesis?speaker={speaker}",
        data=json.dumps(query).encode(), headers={"Content-Type": "application/json"}, method="POST")
    wav = urllib.request.urlopen(req2).read()
    open(path + ".wav", "wb").write(wav)
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", path + ".wav", path + ".mp3"], check=True)
    subprocess.run(["rm", path + ".wav"], check=True)

async def main():
    durs = {}
    for key, who, text in LINES:
        path = f"audio/{key}"
        if who == "N":
            await edge_tts.Communicate(text, "ja-JP-NanamiNeural").save(path + ".mp3")
        else:
            voicevox(text, path)
        d = float(subprocess.check_output(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path + ".mp3"]))
        durs[key] = round(d, 3)
        print(key, who, durs[key])
    json.dump(durs, open("durations.json", "w"), indent=1)

asyncio.run(main())
