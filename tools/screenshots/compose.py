# とった がめん から、キャッチコピー いり の App Store よう の がぞう を つくる。
# つかいかた：python3 tools/screenshots/compose.py とった がめん の フォルダ でる フォルダ
#   とった がめん の フォルダ には iphone/・ipad/ が あり、その なか に 01-start.png など が ある（make-screenshots.sh が つくる）
# ひつよう な もの：Google Chrome、Python の Pillow
import os, subprocess, sys, tempfile
from PIL import Image

RAW, OUT = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ICON = os.path.join(ROOT, "icons", "icon-512.png")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# （ならぶ じゅん, もと の がめん, タイトル, サブ）。タイトル の <br> で ぎょう を かえる。
# アプリ に ない きのう は かかない（しんさ で さしもどされる）
SLIDES = [
    ("01", "01-start", "こうこく なし・あんしん", "たのしく つづく けいさん れんしゅう"),
    ("02", "02-levelup", "キャラクターが そだつ！", "せいかい するたびに けいけんち アップ"),
    ("03", "03-calendar", "はなまる カレンダーで<br>まいにち つづく", "10もんで ○、20もんで はなまる"),
    ("04", "04-story", "文章題も 九九も<br>いろいろ れんしゅう", "たしざん・ひきざん・かけざん・わりざん"),
    ("05", "05-dan", "九九は だんを えらんで", "じゅんばん・ばらばら で れんしゅう"),
    ("06", "06-quiz", "おおきな ボタンで<br>こたえよう", "1けた〜2けた・4つの むずかしさ"),
    ("07", "07-correct", "せいかいすると ピンポン！", "なまえを よんで ほめてくれる"),
    ("08", "08-result", "10もんの ふりかえりで<br>まちがいも わかる", "まちがえた もんだいは こたえを ひょうじ"),
    ("09", None, "にがてが わかる<br>学習レポート", "おうちのかた むけ（暗証番号で保護）"),
]
REPORT = {"iphone": "10-report-weak", "ipad": "10-report-weak"}
SIZE = {"iphone": (1320, 2868), "ipad": (2064, 2752)}
# きりとる はんい（ひだり, うえ, みぎ, した）。iPhone は うえ の とけい の ひょうじ を、
# iPad は うえ の とけい と した の あき を のぞく（がめん を かえたら ここ も みなおす）
def crop_box(dev, name, w, h):
    if dev == "iphone":
        return (0, 170, w, h)
    boxes = {"01-start": (0, 60, w, 1720), "02-levelup": (440, 760, 1624, 1980), "03-calendar": (1100, 380, w, 1640),
             "04-story": (0, 100, w, 1360), "05-dan": (330, 100, 1734, 1600), "06-quiz": (330, 100, 1734, 1800),
             "07-correct": (330, 100, 1734, 1800), "08-result": (330, 100, 1734, 1720), "10-report-weak": (360, 140, 1704, 1330)}
    return boxes[name]

def render(html, w, h, out):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "p.html"); open(p, "w", encoding="utf-8").write(html)
    png = os.path.join(d, "o.png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={w},{h}", f"--screenshot={png}", "file://" + p], check=True, capture_output=True)
    Image.open(png).convert("RGB").save(out, optimize=True)

def html(dev, title, sub, shot, sw, sh_, first):
    W, H = SIZE[dev]
    k = W / 1320 if dev == "iphone" else W / 1500  # もじ の おおきさ の きじゅん
    pills = ""
    if first:
        pills = '<div class="pills"><span>広告なし</span><span>追加の課金なし</span><span>外部リンクなし</span></div>'
    icon = f'<img class="icon" src="file://{ICON}">' if first else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}
body{{background:radial-gradient(ellipse at 50% 18%,#fffbe0 0%,#fff0a0 45%,#ffd94a 100%);
  font-family:"Hiragino Maru Gothic ProN","Hiragino Sans",sans-serif;color:#7a3e00;position:relative}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(circle,#ffffffaa {8*k:.0f}px,transparent {9*k:.0f}px);
  background-size:{180*k:.0f}px {180*k:.0f}px;background-position:{40*k:.0f}px {60*k:.0f}px;opacity:.6}}
.head{{position:absolute;left:0;right:0;top:{(90 if not first else 60)*k:.0f}px;text-align:center;padding:0 {50*k:.0f}px}}
.icon{{width:{150*k:.0f}px;height:{150*k:.0f}px;border-radius:{34*k:.0f}px;box-shadow:0 {8*k:.0f}px {20*k:.0f}px #c9900033;margin-bottom:{18*k:.0f}px}}
h1{{margin:0;font-size:{96*k:.0f}px;line-height:1.25;font-weight:800;letter-spacing:.02em;
  paint-order:stroke fill;-webkit-text-stroke:{14*k:.0f}px #fff;text-shadow:0 {6*k:.0f}px 0 #ffc94d}}
p{{margin:{22*k:.0f}px 0 0;font-size:{50*k:.0f}px;font-weight:700;color:#8a5a12}}
.pills{{margin-top:{26*k:.0f}px;display:flex;gap:{16*k:.0f}px;justify-content:center;flex-wrap:wrap}}
.pills span{{background:#fff;border:{5*k:.0f}px solid #ff9f43;color:#c25b00;border-radius:999px;padding:{10*k:.0f}px {28*k:.0f}px;font-size:{40*k:.0f}px;font-weight:800}}
.shot{{position:absolute;left:50%;transform:translateX(-50%);top:{{TOP}}px;width:{sw}px;
  border:{20*k:.0f}px solid #fff;border-radius:{64*k:.0f}px;overflow:hidden;box-shadow:0 {24*k:.0f}px {60*k:.0f}px #b07a0055;background:#fff}}
.shot img{{display:block;width:100%}}
</style></head><body><div class="dots"></div>
<div class="head">{icon}<h1>{title}</h1><p>{sub}</p>{pills}</div>
<div class="shot"><img src="file://{shot}"></div></body></html>"""

def main():
    for dev in ["iphone", "ipad"]:
        W, H = SIZE[dev]
        os.makedirs(f"{OUT}/{dev}", exist_ok=True)
        for no, name, title, sub in SLIDES:
            name = name or REPORT[dev]
            src = Image.open(f"{RAW}/{dev}/{name}.png").convert("RGB")
            box = crop_box(dev, name, *src.size)
            cut = src.crop(box)
            tmp = os.path.join(tempfile.mkdtemp(), f"{name}.png"); cut.save(tmp)
            first = no == "01"
            lines = title.count("<br>") + 1
            k = W / 1320 if dev == "iphone" else W / 1500
            top_text = (60 if first else 90) * k + (150 + 18) * k * first + 96 * 1.25 * k * lines + 22 * k + 50 * 1.5 * k + (110 * k if first else 0)
            top = int(top_text + 70 * k)
            # はば を きめる：iPhone は 80%、iPad は あいて いる たかさ に あわせる（はば は 88% まで）
            if dev == "iphone":
                sw = int(W * 0.8)
            else:
                avail = H - top - 100
                sw = int(min(W * 0.88, avail * cut.width / cut.height))
            if dev == "ipad":
                sh_h = sw * cut.height / cut.width
                top = int(top + max(0, (H - top - 100 - sh_h) / 2))
            h = html(dev, title, sub, tmp, sw, None, first).replace("{TOP}", str(top))
            out = f"{OUT}/{dev}/{no}-{name.split('-', 1)[1]}.png"
            render(h, W, H, out)
            print(out, Image.open(out).size)

main()
