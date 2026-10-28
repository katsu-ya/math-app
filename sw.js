// オフライン でも つかえる ように、アプリ の ファイル を この たんまつ に とっておく。
// あたらしい バージョン が あっても すぐ には いれかえず、
// 「あたらしい バージョン が あります」を タップ した とき に いれかえる。
const CACHE = "keisan-app";        // いま つかって いる ファイル
const NEXT = "keisan-app-next";    // とどいた けど まだ つかって いない あたらしい ファイル
const FILES = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./privacy.html",           // おうちのかたへ の なか で よむ
  "./icons/icon.svg",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
  "./icons/apple-touch-icon.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // sw.js だけ かわった とき は、いま の ファイル を そのまま つかう
    if (!(await cache.match("./"))) await cache.addAll(FILES.map((f) => new Request(f, { cache: "reload" })));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    // アプリ の ページ（./ と index.html）を ひらく とき だけ アプリ を かえす。
    // ほか の ページ（privacy.html・support.html など）は、とっておいた もの か サーバー から もらう
    const app = req.mode === "navigate" && /\/(index\.html)?$/.test(new URL(req.url).pathname);
    const hit = await cache.match(app ? "./" : req, { ignoreSearch: true });
    return hit || fetch(req);
  })());
});

const sameBody = async (a, b) => {
  const [x, y] = await Promise.all([a.arrayBuffer(), b.arrayBuffer()]);
  if (x.byteLength !== y.byteLength) return false;
  const u = new Uint8Array(x), v = new Uint8Array(y);
  for (let i = 0; i < u.length; i++) if (u[i] !== v[i]) return false;
  return true;
};

// サーバー の ファイル と くらべて、ちがって いたら NEXT に いれて しらせる
async function checkUpdate() {
  const cache = await caches.open(CACHE);
  const fresh = await Promise.all(FILES.map((f) => fetch(f, { cache: "no-cache" })));
  if (fresh.some((r) => !r.ok)) return;
  let changed = false;
  for (let i = 0; i < FILES.length; i++) {
    const old = await cache.match(FILES[i]);
    if (!old || !(await sameBody(old, fresh[i].clone()))) changed = true;
  }
  if (!changed) { await caches.delete(NEXT); return; }
  const next = await caches.open(NEXT);
  await Promise.all(FILES.map((f, i) => next.put(f, fresh[i])));
  (await self.clients.matchAll()).forEach((c) => c.postMessage({ type: "update-ready" }));
}

// NEXT の ファイル を いま の ファイル に する
async function applyUpdate() {
  const next = await caches.open(NEXT);
  const cache = await caches.open(CACHE);
  for (const req of await next.keys()) await cache.put(req, await next.match(req));
  await caches.delete(NEXT);
}

self.addEventListener("message", (e) => {
  const type = e.data && e.data.type;
  if (type === "check") e.waitUntil(checkUpdate().catch(() => {})); // オフライン の とき は なにも しない
  if (type === "apply") e.waitUntil(applyUpdate().then(() => e.source.postMessage({ type: "applied" })));
});
