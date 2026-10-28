# スクリーンショット よう の みほん の きろく（バックアップ の ファイル）を つくる。
# なまえ は「ゆう」。ほんとう の こども の きろく では ない。
# ひづけ は つくった ひ から かぞえる ので、とる ひ に つくりなおす（カレンダー の れんぞく が ずれない ように）。
# つかいかた：python3 tools/make-sample-backup.py [でる ファイル]（ない とき は ~/Desktop/keisan-sample.json）
#   シミュレーター の「ファイル」アプリ に いれる：python3 tools/make-sample-backup.py --sim
import json, os, random, subprocess, sys
from datetime import datetime, timedelta

random.seed(7)  # まいかい おなじ ないよう に する
PREFIX = "keisan-renshu-"
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
key = lambda d: d.strftime("%Y-%m-%d")

# ひ ごと の もんだい の かず（-13 は 13にち まえ、0 は きょう）。0 の ひ は やすみ。
# さいご の 12にち は つづけて とく（れんぞく）。20 いじょう は はなまる、10 いじょう は ○
PLAN = {-13: 10, -12: 0, -11: 20, -10: 10, -9: 10, -8: 22, -7: 10, -6: 12, -5: 20, -4: 10, -3: 10, -2: 20, -1: 10, 0: 12}
# よく まちがえる もんだい（レポート の「よく間違える問題」に でる）
WEAK = {("×", 7, 8), ("×", 6, 7), ("-", 13, 6)}

def problem(op, lv):
    big = lv.startswith("2")
    if op == "+":
        a, b = (random.randint(10, 60), random.randint(10, 39)) if big else (random.randint(1, 9), random.randint(1, 9))
    elif op == "-":
        b = random.randint(1, 9)
        a = random.randint(b + 1, 18 if lv == "1h" else 9 + b) if not big else random.randint(30, 99)
    elif op == "×":
        a, b = random.randint(2, 9), random.randint(1, 9)
    else:
        b, q = random.randint(2, 9), random.randint(1, 9)
        a = b * q
    if random.random() < 0.2:  # にがて の もんだい を ときどき だす
        w = random.choice(sorted(WEAK))
        if w[0] == op: a, b = w[1], w[2]
    return a, b

# 1かい（10もん）の しゅるい。st は ぶんしょうだい
KINDS = [("+", "1e", 0), ("-", "1h", 0), ("×", "1e", 0), ("+", "2e", 0), ("÷", "1e", 0), ("+", "1e", 1), ("-", "1e", 1), ("×", "1h", 0)]

log, records = [], {}
g = {"xp": 0, "perfect": 0, "ops": [], "kuku": [], "badges": {}, "stage2": "", "story": 0, "fixes": 3, "hard": 0,
     "perfRow": 0, "perfRowBest": 0, "perfOps": [], "perfLv": [], "randDans": [], "storyOps": []}
kind_i = 0
for off, n in sorted(PLAN.items()):
    day = today + timedelta(days=off)
    records[key(day)] = n
    t = day + timedelta(hours=17)
    for s in range(0, n, 10):
        op, lv, st = KINDS[kind_i % len(KINDS)]
        kind_i += 1
        size = min(10, n - s)
        perfect = size == 10 and random.random() < 0.35
        oks = 0
        for i in range(size):
            a, b = problem(op, lv)
            weak = (op, a, b) in WEAK
            ok = 1 if perfect else (0 if weak and random.random() < 0.6 else (1 if random.random() < 0.9 else 0))
            e = {"t": int((t + timedelta(minutes=s, seconds=i * 8)).timestamp() * 1000), "op": op, "lv": lv,
                 "a": a, "b": b, "ok": ok, "ms": random.randint(2500, 9000)}
            if st:
                e["st"], e["sk"] = 1, ok or (1 if random.random() < 0.5 else 0)
            log.append(e)
            oks += ok
            if ok:
                g["xp"] += 10
                if op not in g["ops"]: g["ops"].append(op)
                if op == "×" and f"{a} × {b}" not in g["kuku"] and a <= 9 and b <= 9: g["kuku"].append(f"{a} × {b}")
                if st:
                    g["story"] += 1
                    if op not in g["storyOps"]: g["storyOps"].append(op)
        if perfect:
            g["perfect"] += 1
            g["xp"] += 50
            if op not in g["perfOps"]: g["perfOps"].append(op)
            if lv not in g["perfLv"]: g["perfLv"].append(lv)

# もらった バッジ と その ひ（だん の バッジ は 1かい の なか で きまる ので、ここ で わたして おく）
got = {"first10": -13, "streak3": -9, "hanamaru1": -11, "allops": -9, "streak7": -5, "total100": -4, "dan2": -6, "dan5": -3}
if g["perfect"]: got["perfect1"] = -11
for b, off in got.items():
    g["badges"][b] = key(today + timedelta(days=off))

data = {
    PREFIX + "settings": {"guideSeen": True, "nameAsked": True, "name": "ゆう", "honor": "さん"},
    PREFIX + "records": records,
    PREFIX + "log": log,
    PREFIX + "growth": g,
}
backup = {"app": "keisan-renshu", "v": 1, "saved": datetime.now().astimezone().isoformat(), "name": "ゆう",
          "data": {k: json.dumps(v, ensure_ascii=False, separators=(",", ":")) for k, v in data.items()}}
text = json.dumps(backup, ensure_ascii=False)

if "--sim" in sys.argv:
    # うごいて いる シミュレーター の「ファイル」アプリ（この iPhone 内）に おく
    group = subprocess.run(["xcrun", "simctl", "get_app_container", "booted", "com.apple.DocumentsApp", "groups"],
                           check=True, capture_output=True, text=True).stdout
    base = next(l.split("\t")[1] for l in group.splitlines() if l.startswith("group.com.apple.FileProvider.LocalStorage"))
    out = os.path.join(base, "File Provider Storage", "keisan-sample.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
else:
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Desktop/keisan-sample.json")
open(out, "w", encoding="utf-8").write(text)
total = sum(records.values())
print(f"{out}\n  {total}もん・{len(log)}こ の きろく、けいけんち {g['xp']}、ぜんもん せいかい {g['perfect']}かい、バッジ {len(g['badges'])}こ")
