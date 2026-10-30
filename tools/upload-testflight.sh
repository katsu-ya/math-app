#!/bin/zsh
# ビルド ばんごう を 1つ あげて、App Store Connect（TestFlight）に アップロード する。
# Xcode の「Product → Archive」は、チーム に iPhone が とうろく されて いないと、かいはつ よう の しょめい が つくれず とまる。
# ここ では しょめい なし で アーカイブ して から、はいふ よう の しょめい（Apple が かんり する しょうめいしょ）を して アップロード する。
# iPhone を ケーブル で つながなくて よい。
# つかいかた：tools/upload-testflight.sh        （ビルド ばんごう を 1 あげて アップロード）
#             tools/upload-testflight.sh --no-bump（ばんごう は そのまま。アップロード が しっぱい した あと の やりなおし など）
# ひつよう な もの：Xcode に Apple ID で サインイン して いる こと（Settings → Accounts）
# おわったら、かわった project.pbxproj（ビルド ばんごう）を コミット する
set -e
ROOT=${0:a:h:h}
TEAM=5U4PUYRD3H
PROJ=$ROOT/ios/App/App.xcodeproj
PBX=$PROJ/project.pbxproj
WORK=${TMPDIR:-/tmp}/keisan-upload-work
cd $ROOT

# いま の ビルド ばんごう（CURRENT_PROJECT_VERSION）
current=$(grep -m1 -o "CURRENT_PROJECT_VERSION = [0-9]*;" $PBX | grep -o "[0-9]*")
if [[ $1 == --no-bump ]]; then
  build=$current
else
  build=$((current + 1))
  sed -i '' "s/CURRENT_PROJECT_VERSION = $current;/CURRENT_PROJECT_VERSION = $build;/g" $PBX
fi
version=$(grep -m1 -o "MARKETING_VERSION = [0-9.]*;" $PBX | grep -o "[0-9.]*[0-9]")
echo "== $version ($build) を つくります"

echo "== 1. ウェブ の ファイル を アプリ に うつす"
npm run build >/dev/null
npx cap sync ios >/dev/null

echo "== 2. アーカイブ（しょめい なし・Release）"
rm -rf $WORK; mkdir -p $WORK
xcodebuild archive -project $PROJ -scheme App -configuration Release -destination 'generic/platform=iOS' \
  -archivePath $WORK/App.xcarchive CODE_SIGNING_ALLOWED=NO > $WORK/archive.txt 2>&1 \
  || { grep -E "error:" $WORK/archive.txt | head; echo "アーカイブ に しっぱい しました（$WORK/archive.txt）"; exit 1; }

echo "== 3. はいふ よう の しょめい を して アップロード"
cat > $WORK/ExportOptions.plist <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>method</key><string>app-store-connect</string>
	<key>destination</key><string>upload</string>
	<key>signingStyle</key><string>automatic</string>
	<key>teamID</key><string>$TEAM</string>
	<key>uploadSymbols</key><true/>
</dict>
</plist>
PLIST
xcodebuild -exportArchive -archivePath $WORK/App.xcarchive -exportOptionsPlist $WORK/ExportOptions.plist \
  -exportPath $WORK/upload -allowProvisioningUpdates > $WORK/upload.txt 2>&1 \
  || { grep -iE "error" $WORK/upload.txt | head; echo "アップロード に しっぱい しました（$WORK/upload.txt）"; exit 1; }
grep -q "Upload succeeded" $WORK/upload.txt || { tail -20 $WORK/upload.txt; echo "アップロード が おわった か わかりません（$WORK/upload.txt）"; exit 1; }

echo "できました：$version ($build) を アップロード しました。"
echo "App Store Connect の TestFlight で しょり が おわる（5〜30ぷん）と、iPhone の TestFlight に とどきます。"
echo "ビルド ばんごう が かわった ので、ios/App/App.xcodeproj/project.pbxproj を コミット して ください。"
