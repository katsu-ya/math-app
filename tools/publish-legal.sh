#!/bin/zsh
# プライバシーポリシー と サポート の ページ を、こうかい よう の リポジトリ（katsu-ya.github.io）に うつして push する。
# ほんぶん の もと は この リポジトリ の legal/（アプリ の なか でも よむ）。tokushoho.html は とくてい しょうとりひき ほう に もとづく ひょうき。legal/ を なおしたら これ を うごかす。
# こうかい さき：https://katsu-ya.github.io/keisan-renshu/privacy.html ・ support.html ・ tokushoho.html
# つかいかた：tools/publish-legal.sh
set -e
ROOT=${0:a:h:h}
REPO=katsu-ya/katsu-ya.github.io
DIR=keisan-renshu
WORK=$(mktemp -d)

gh repo clone $REPO $WORK -- -q
mkdir -p $WORK/$DIR
cp $ROOT/legal/privacy.html $ROOT/legal/support.html $ROOT/legal/tokushoho.html $ROOT/legal/icon-192.png $WORK/$DIR/
# keisan-renshu/ を ひらいた とき は サポート の ページ へ
cat > $WORK/$DIR/index.html <<'HTML'
<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><meta http-equiv="refresh" content="0; url=support.html">
<title>たまごと けいさん れんしゅう</title></head>
<body><p><a href="support.html">サポートのページへ</a></p></body></html>
HTML
cd $WORK
git add -A
if git diff --cached --quiet; then
  echo "かわった ところ は ありません"
else
  git commit -q -m "けいさん れんしゅう の プライバシーポリシー と サポート を こうしん"
  git push -q
  echo "push しました。1〜2ふん で https://katsu-ya.github.io/$DIR/privacy.html に はんえい されます"
fi
rm -rf $WORK
