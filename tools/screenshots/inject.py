# さつえい よう に www/index.html を かきかえる（npm run build の あと に つかう。もと の index.html は かえない）
# ・ひらく たび に みほん の きろく を いれなおす（あんしょうばんごう は 2580）
# ・シーン 7（せいかい の ひょうじ）の あいだ は つぎ の もんだい に すすまない
# ・capture.js を いれる
# つかいかた：python3 tools/screenshots/inject.py みほん.json
import hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))

sample = json.load(open(sys.argv[1], encoding="utf-8"))
data = sample["data"]
data["keisan-renshu-lock"] = json.dumps({"salt": "s", "hash": hashlib.sha256(b"s:2580").hexdigest()})
seed = f"""<script>
(() => {{
  const D = {json.dumps(data, ensure_ascii=False)};
  Object.keys(localStorage).filter((k) => k.startsWith("keisan-renshu-")).forEach((k) => localStorage.removeItem(k));
  for (const [k, v] of Object.entries(D)) localStorage.setItem(k, v);
  // シーン 8（ふりかえり）では レベルアップ の おいわい が でない ように けいけんち を へらす
  if (sessionStorage.getItem("scene") === "8") {{ const g = JSON.parse(D["keisan-renshu-growth"]); g.xp = 1500; localStorage.setItem("keisan-renshu-growth", JSON.stringify(g)); }}
}})();
</script>"""

p = os.path.join(ROOT, "www", "index.html")
s = open(p, encoding="utf-8").read()
i = s.index("<script")
s = s[:i] + seed + s[i:]
a = "const AUTO_NEXT_OK_MS = 1500;"
assert s.count(a) == 1, "AUTO_NEXT_OK_MS が みつからない（index.html が かわった？）"
s = s.replace(a, 'const AUTO_NEXT_OK_MS = sessionStorage.getItem("scene") === "7" ? 600000 : 500;')
s = s.replace("</body>", "<script>" + open(os.path.join(HERE, "capture.js"), encoding="utf-8").read() + "</script></body>", 1)
open(p, "w", encoding="utf-8").write(s)
print("www/index.html を さつえい よう に しました")
