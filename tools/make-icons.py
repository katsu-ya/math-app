# アイコン と きどう がめん の え を つくりなおす。
# icons/icon.svg（もと の え）と icons/splash.svg（きどう がめん。<!--ART--> に icon.svg の キャラクター が はいる）から PNG を つくる。
# ひつよう な もの：Google Chrome、Python の Pillow（pip install pillow）
# つかいかた：python3 tools/make-icons.py
import os, re, subprocess, tempfile
from PIL import Image

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = tempfile.mkdtemp()

def render(svg, size):
    # Chrome で SVG を PNG に する（とうめい は つかわない）
    src = os.path.join(TMP, "in.svg"); html = os.path.join(TMP, "p.html"); png = os.path.join(TMP, "out.png")
    open(src, "w", encoding="utf-8").write(svg)
    open(html, "w").write(f"<body style='margin:0'><img src='file://{src}' style='display:block;width:{size}px;height:{size}px'>")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={size},{size}", f"--screenshot={png}", "file://" + html], check=True, capture_output=True)
    return Image.open(png).convert("RGB")

def save(img, path):
    img.save(os.path.join(ROOT, path), optimize=True)
    print(path, img.size)

icon = open(os.path.join(ROOT, "icons/icon.svg"), encoding="utf-8").read()
defs = re.search(r"<defs>.*?</defs>", icon, re.S).group(0)
art = re.search(r'<g id="art">.*?\n  </g>', icon, re.S).group(0)

big = render(icon, 1024)
save(big, "ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png")
for size, name in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png")]:
    save(render(icon, size), "icons/" + name)
# Android の まるい かたち など で きりぬかれて も よい ように、え を 80% に する
mask = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">{defs}<rect width="1024" height="1024" fill="url(#sun)"/><g transform="translate(102.4 102.4) scale(.8)">{art}</g></svg>'
save(render(mask, 512), "icons/icon-maskable-512.png")

splash = open(os.path.join(ROOT, "icons/splash.svg"), encoding="utf-8").read().replace("<!--ART-->", art)
sp = render(splash, 2732)
for name in ["splash-2732x2732.png", "splash-2732x2732-1.png", "splash-2732x2732-2.png"]:
    save(sp, "ios/App/App/Assets.xcassets/Splash.imageset/" + name)
