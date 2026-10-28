#!/bin/zsh
# App Store よう の スクリーンショット を とって、キャッチコピー いり の がぞう に する。
# 1. きょう の ひづけ で みほん の きろく を つくる（なまえ は「ゆう」）
# 2. さつえい よう の アプリ を つくる（www/ の うつし に だけ capture.js を いれる）
# 3. iPhone 18 Pro Max と iPad Pro 13-inch (M5) で、9つ の がめん を じどう で だして とる（とけい は 9:41）
# 4. キャッチコピー いり の がぞう を つくる（iPhone 1320×2868、iPad 2064×2752）
# 5. ふつう の アプリ に もどして、シミュレーター に いれなおす
# つかいかた：tools/screenshots/make-screenshots.sh [でる フォルダ]（ない とき は ~/Desktop/keisan-screenshots）
# ひつよう な もの：Xcode（シミュレーター）、Node.js、Google Chrome、Python の Pillow
# がぞう は GitHub には あげない（でる フォルダ は リポジトリ の そと）
set -e
HERE=${0:a:h}
ROOT=${HERE:h:h}
OUT=${1:-$HOME/Desktop/keisan-screenshots}
WORK=${TMPDIR:-/tmp}/keisan-screenshots-work
APP_ID=jp.katsuya.keisanrenshu
DEVICES=("iPhone 18 Pro Max:iphone" "iPad Pro 13-inch (M5):ipad")
cd $ROOT
rm -rf $WORK; mkdir -p $WORK/raw

# シミュレーター の なまえ から ID を さがす
udid() {
  xcrun simctl list devices available -j | python3 -c "
import json, sys
for rt in json.load(sys.stdin)['devices'].values():
    for d in rt:
        if d['name'] == sys.argv[1]: print(d['udid']); sys.exit()
sys.exit('シミュレーター が みつかりません：' + sys.argv[1])" "$1"
}

build_app() {
  local log=$WORK/build.txt
  (cd ios/App && xcodebuild -project App.xcodeproj -scheme App -destination 'generic/platform=iOS Simulator' \
    -derivedDataPath $WORK/dd build > $log 2>&1) || true
  grep -q "BUILD SUCCEEDED" $log || { grep -E "error:" $log | head; echo "ビルド に しっぱい しました（$log）"; exit 1; }
}

echo "== 1. みほん の きろく"
python3 tools/make-sample-backup.py $WORK/sample.json

echo "== 2. さつえい よう の アプリ"
npm run build >/dev/null
python3 $HERE/inject.py $WORK/sample.json
npx cap sync ios >/dev/null
build_app
APP=$WORK/dd/Build/Products/Debug-iphonesimulator/App.app

echo "== 3. さつえい"
for pair in $DEVICES; do
  NAME=${pair%%:*}; DEV=${pair##*:}; D=$(udid $NAME)
  RAW=$WORK/raw/$DEV; mkdir -p $RAW
  xcrun simctl boot $D 2>/dev/null || true
  xcrun simctl bootstatus $D -b >/dev/null
  xcrun simctl status_bar $D override --time 9:41 --dataNetwork wifi --wifiMode active --wifiBars 3 \
    --cellularMode active --cellularBars 4 --batteryState discharging --batteryLevel 100
  xcrun simctl uninstall $D $APP_ID 2>/dev/null || true
  xcrun simctl install $D $APP
  LOG=$WORK/log-$DEV.txt; : > $LOG
  xcrun simctl launch --console-pty $D $APP_ID > $LOG 2>&1 &
  # ログ に「SHOT なまえ」が でたら とる。「SHOT done」で おわり
  seen=""; ok=""
  for i in {1..900}; do
    for s in $(grep -a -o "SHOT [0-9a-z-]*" $LOG | awk '{print $2}'); do
      [[ " $seen " == *" $s "* ]] && continue
      seen="$seen $s"
      if [[ $s == done ]]; then ok=1; break; fi
      sleep 0.4; xcrun simctl io $D screenshot $RAW/$s.png >/dev/null 2>&1
    done
    [[ -n $ok ]] && break
    sleep 0.2
  done
  xcrun simctl terminate $D $APP_ID 2>/dev/null || true
  if [[ -z $ok ]]; then echo "$NAME：とちゅう で とまりました（$seen）"; grep -a "SHOT-ERR" $LOG; exit 1; fi
  echo "$NAME：$seen"
done

echo "== 4. キャッチコピー いり の がぞう"
rm -rf $OUT
python3 $HERE/compose.py $WORK/raw $OUT

echo "== 5. ふつう の アプリ に もどす"
npm run build >/dev/null
npx cap sync ios >/dev/null
build_app
for pair in $DEVICES; do
  D=$(udid ${pair%%:*})
  xcrun simctl uninstall $D $APP_ID 2>/dev/null || true
  xcrun simctl install $D $APP
done
echo "できました：$OUT（とった まま の がめん は $WORK/raw）"
echo "とけい の ひょうじ を もどす とき：xcrun simctl status_bar booted clear"
