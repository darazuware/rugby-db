import asyncio, json, subprocess, edge_tts

# ep01 ナレーション（ナレーターのみ / ja-JP-NanamiNeural）
# 時制に依存する表現（W杯・大会名・年）は入れない = YouTubeストック用
LINES = [
    ("e1", "ラグビー超入門。今日は、ラグビーがどんなスポーツなのかを、数字でざっくりつかんでいきます。"),
    ("e2", "まずはグラウンド。トライラインの間が縦100メートル、横は70メートル。サッカーコートと、ほぼ同じ広さです。"),
    ("e3", "人数は、1チーム15人。2つのチームで、合わせて30人が同時にぶつかり合います。"),
    ("e4", "試合時間は、前半40分、後半40分。あいだにハーフタイムをはさんで、合計80分です。"),
    ("e5", "点の取り方は4つ。ひとつめ、トライ。相手のインゴールにボールをつけて5点。ふたつめ、コンバージョン。トライのあとのキックを、ポールの間、バーの上に通して2点。みっつめ、ペナルティゴール。相手の反則からのキックを決めて3点。よっつめ、ドロップゴール。プレー中にワンバウンドさせて蹴り、決めれば3点です。"),
    ("e6", "そして80分が終わった時点で、点が多いほうが勝ち。シンプルです。"),
    ("e7", "ここまで分かれば、ラグビーの試合はもう楽しめます。ひとつひとつのルールは、次の動画から、くわしく解説していきます。"),
]


async def main():
    durs = {}
    for key, text in LINES:
        path = f"audio/{key}.mp3"
        await edge_tts.Communicate(text, "ja-JP-NanamiNeural").save(path)
        d = float(subprocess.check_output(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path]))
        durs[key] = round(d, 3)
        print(key, durs[key])
    json.dump(durs, open("durations.json", "w"), indent=1)


asyncio.run(main())
