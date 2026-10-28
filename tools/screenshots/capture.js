// スクリーンショット の さつえい よう（make-screenshots.sh が www/ の うつし に だけ いれる。アプリ には はいらない）
// シーン を じゅんばん に だす。「SHOT なまえ」を ログ に だしたら 4びょう まつ（その あいだ に シェル が とる）。
// 1つ おわる ごと に みほん の きろく に もどして ひらきなおす
(() => {
  const $ = (id) => document.getElementById(id);
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const click = (el) => { el.dispatchEvent(new MouseEvent("click", { bubbles: true })); };
  const sel = (s) => document.querySelector(s);
  const ans = () => {
    const m = $("question").textContent.match(/(\d+)\s*([+＋\-−×÷])\s*(\d+)/);
    const a = +m[1], b = +m[3];
    return String({ "+": a + b, "＋": a + b, "-": a - b, "−": a - b, "×": a * b, "÷": a / b }[m[2]]);
  };
  const type = async (s) => { for (const c of s) { click(sel(`#keypad [data-key="${c}"]`)); await wait(120); } };
  const answer = async (right) => { let v = ans(); if (!right) v = String(+v + 1); await type(v); click($("checkBtn")); };
  const shot = async (name) => { console.log("SHOT " + name); await wait(4000); };
  // ステータスバー と かさならない ように、うえ に すきま を あけて とめる
  const scrollTo = (el, pad) => window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - pad);
  const scene = +(sessionStorage.getItem("scene") || 1);
  const nextScene = () => { sessionStorage.setItem("scene", scene + 1); location.reload(); };
  const startCalc = async (op, lv) => {
    click(sel('#modeChoices [data-mode="calc"]')); await wait(200);
    click(sel(`#opChoices [data-op="${op}"]`)); await wait(200);
    click(sel(`#levelChoices [data-level="${lv}"]`)); await wait(200);
    click($("startBtn")); await wait(800);
  };
  const run = async () => {
    await wait(2500);
    switch (scene) {
      case 1: window.scrollTo(0, 0); await shot("01-start"); break;
      case 2: // レベルアップ（10もん ぜんぶ せいかい）
        await startCalc("+", "1e");
        for (let i = 0; i < 10; i++) { await answer(true); await wait(700); }
        await wait(1500); await shot("02-levelup"); break;
      case 3: scrollTo($("startBtn"), 80); await wait(500); await shot("03-calendar"); break;
      case 4:
        click(sel('#modeChoices [data-mode="story"]')); await wait(200);
        click(sel('#opChoices [data-op="×"]')); await wait(200);
        click(sel('#levelChoices [data-level="1e"]')); await wait(200);
        click($("startBtn")); await wait(1200); await shot("04-story"); break;
      case 5:
        click(sel('#modeChoices [data-mode="calc"]')); await wait(200);
        click(sel('#opChoices [data-op="×"]')); await wait(800);
        click(sel('#danChoices [data-dan="7"]')); await wait(500); await shot("05-dan"); break;
      case 6: await startCalc("+", "1h"); await type(ans()); await wait(300); await shot("06-quiz"); break;
      case 7: await startCalc("+", "1h"); await answer(true); await wait(500); await shot("07-correct"); break;
      case 8: // ふりかえり（1もん だけ まちがい）
        await startCalc("+", "1h");
        for (let i = 0; i < 10; i++) { await answer(i !== 6); await wait(i === 6 ? 3600 : 700); }
        await wait(1500);
        if (!$("celebrate").hidden) { click($("celeOk")); await wait(800); }
        await shot("08-result"); break;
      case 9: // おうちのかたへ（あんしょうばんごう 2580）
        click($("parentBtn")); await wait(800);
        for (const c of "2580") { click(sel(`#pinPad [data-key="${c}"]`)); await wait(200); }
        await wait(1500); await shot("09-report");
        scrollTo($("rpWeak").closest(".rp-card"), 80); await wait(600); await shot("10-report-weak"); break;
      default: console.log("SHOT done"); return;
    }
    nextScene();
  };
  run().catch((e) => console.log("SHOT-ERR " + e));
})();
