// Chụp website ở cỡ ĐIỆN THOẠI (và máy tính) để Claude tự soi trước khi giao link.
//
//   node cong-cu/chup-man-hinh.mjs khach-hang/<slug>
//
// Ra: khach-hang/<slug>/soi/  dt-trang-chu-man-dau.png · dt-trang-chu-muc-NN.png (từng mục) · dt-san-pham*.png
//                             · mt-trang-chu.png (màn đầu máy tính) · dt-trang-chu.png (toàn trang, chỉ xem bố cục)
// Tự bắt lỗi điện thoại hay gặp mà nhìn mã không thấy:
//   · trang TRÀN NGANG (vuốt ngang được cả trang)
//   · nút/link bấm được nhỏ hơn 40 px (ngón tay bấm trượt)
//   · chữ nhỏ hơn 14 px · ảnh lỗi không tải · lỗi JavaScript
//
// Cần Playwright. Phiên đám mây lần đầu:
//   npm i --no-save playwright && npx playwright install --with-deps chromium
// Không cài được (mạng chặn) → bỏ qua bước này, KHÔNG được chặn việc deploy vì nó.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const thuMuc = process.argv[2];
if (!thuMuc) { console.error('Cách dùng: node cong-cu/chup-man-hinh.mjs khach-hang/<slug>'); process.exit(2); }
const dist = path.resolve(thuMuc, 'dist');
const ra = path.resolve(thuMuc, 'soi');
fs.mkdirSync(ra, { recursive: true });

let pw;
try { pw = await import(process.env.PLAYWRIGHT_PATH ? 'file://' + process.env.PLAYWRIGHT_PATH : 'playwright'); }
catch { console.error('✘ Chưa có Playwright. Chạy: npm i --no-save playwright && npx playwright install --with-deps chromium'); process.exit(3); }
const chromium = pw.chromium || pw.default?.chromium;

const KIEU = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.webp': 'image/webp',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.xml': 'application/xml', '.txt': 'text/plain' };
const may = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  let f = path.join(dist, p);
  if (p.endsWith('/')) f = path.join(f, 'index.html');
  if (!fs.existsSync(f)) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': KIEU[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
}).listen(0);
const goc = 'http://127.0.0.1:' + may.address().port;

const spDau = fs.existsSync(path.join(dist, 'san-pham'))
  ? fs.readdirSync(path.join(dist, 'san-pham'))[0] : null;

const trinh = await chromium.launch();
const loi = [];

async function soi(trang, ten) {
  const kq = await trang.evaluate(() => {
    const r = { tran: document.documentElement.scrollWidth - window.innerWidth, nho: [], chuNho: [], anhHong: [] };
    for (const el of document.querySelectorAll('a[href], button')) {
      const b = el.getBoundingClientRect(), s = getComputedStyle(el);
      if (s.display === 'none' || s.visibility === 'hidden' || b.width === 0 || !el.getClientRects().length) continue;
      if (el.closest('.mo-ta, .gioi-thieu p, .chan')) continue;          // link nằm trong đoạn văn thì chấp nhận
      if (b.height < 40 || b.width < 40) r.nho.push((el.innerText || el.getAttribute('aria-label') || el.className).trim().slice(0, 30) + ` (${Math.round(b.width)}×${Math.round(b.height)})`);
    }
    for (const el of document.querySelectorAll('p, li, span, td, th, small, a, h3')) {
      const s = getComputedStyle(el);
      if (!el.getClientRects().length) continue;                         // nằm trong khối đang ẩn
      if (el.innerText && el.innerText.trim() && parseFloat(s.fontSize) < 13.5 && s.display !== 'none' && !el.closest('.thanh-day'))
        r.chuNho.push(el.innerText.trim().slice(0, 30) + ` (${s.fontSize})`);
    }
    for (const im of document.images) {
      if (!im.getClientRects().length || im.closest('.anh-muc, .chon-vis')) continue;   // ảnh trong khối đang thu gọn
      if (!im.complete || im.naturalWidth === 0) r.anhHong.push(im.getAttribute('src'));
    }
    return r;
  });
  if (kq.tran > 1) loi.push(`${ten}: TRÀN NGANG ${kq.tran}px`);
  if (kq.nho.length) loi.push(`${ten}: nút nhỏ hơn 40px → ${[...new Set(kq.nho)].slice(0, 6).join(' · ')}`);
  if (kq.chuNho.length) loi.push(`${ten}: chữ nhỏ → ${[...new Set(kq.chuNho)].slice(0, 4).join(' · ')}`);
  if (kq.anhHong.length) loi.push(`${ten}: ảnh hỏng → ${kq.anhHong.join(', ')}`);
}

async function chup(url, ten, khung, motMan = false) {
  const ctx = await trinh.newContext(khung);
  const trang = await ctx.newPage();
  trang.on('pageerror', e => loi.push(`${ten}: lỗi JS ${e.message}`));
  await trang.goto(goc + url, { waitUntil: 'networkidle' }).catch(() => {});
  // Cuộn CHẬM như người thật: ảnh lazy tải xong và mọi khối "trượt lên khi cuộn" được kích hoạt.
  // (Cuộn nhanh rồi chụp ngay là chụp lúc các khối còn đang mờ dần — ảnh ra mảng trắng, trông như web hỏng.)
  await trang.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 350) { window.scrollTo({ top: y, behavior: 'instant' }); await new Promise(r => setTimeout(r, 140)); }
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'instant' }); await new Promise(r => setTimeout(r, 300));
  });
  // Ảnh lazy: buộc tải hết rồi chờ — chụp lúc ảnh chưa về là ra ô trống, trông như ảnh hỏng
  await trang.evaluate(() => document.querySelectorAll('img[loading="lazy"]').forEach(i => { i.loading = 'eager'; }));
  await trang.waitForLoadState('networkidle').catch(() => {});
  await trang.waitForTimeout(300);
  const anCon = await trang.evaluate(() => [...document.querySelectorAll('.reveal')].filter(x => !x.classList.contains('in') && x.getClientRects().length).length);
  if (anCon) loi.push(`${ten}: ${anCon} khối KHÔNG BAO GIỜ HIỆN dù đã cuộn qua (hiệu ứng trượt lên hỏng)`);
  // Chụp trạng thái cuối của hiệu ứng, không chụp giữa chừng
  await trang.addStyleTag({ content: '.js .reveal{opacity:1!important;transform:none!important;transition:none!important}' });
  await trang.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await trang.waitForTimeout(500);
  if (khung.isMobile) await soi(trang, ten);
  if (khung.isMobile && !motMan) {
    await trang.screenshot({ path: path.join(ra, ten + '-man-dau.png') });
    // Chụp TỪNG MỤC đúng khung điện thoại. Đây mới là ảnh để soi: ảnh toàn trang của trang dài
    // hay mất ảnh (Chromium bỏ ảnh đã giải mã khỏi bộ nhớ) → ô trống giả, trông như ảnh hỏng.
    const soMuc = await trang.evaluate(() => document.querySelectorAll('main > section, main > div > section, footer').length);
    for (let k = 0; k < Math.min(soMuc, 16); k++) {
      await trang.evaluate(k => {
        const el = document.querySelectorAll('main > section, main > div > section, footer')[k];
        window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 70, behavior: 'instant' });
      }, k);
      await trang.waitForTimeout(450);
      await trang.screenshot({ path: path.join(ra, `${ten}-muc-${String(k + 1).padStart(2, '0')}.png`) });
    }
    await trang.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  }
  await trang.screenshot({ path: path.join(ra, ten + '.png'), fullPage: !motMan });
  await ctx.close();
}

const DT = { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, locale: 'vi-VN' };
const MT = { viewport: { width: 1366, height: 860 }, locale: 'vi-VN' };
await chup('/', 'dt-trang-chu', DT);
if (spDau) await chup(`/san-pham/${spDau}/`, 'dt-san-pham', DT);
await chup('/', 'mt-trang-chu', MT, true);
await trinh.close();
may.close();

console.log('Ảnh chụp ở ' + ra + ' — đọc dt-trang-chu-man-dau.png rồi dt-trang-chu-muc-NN.png (mỗi mục một ảnh đúng khung điện thoại).\n  Ảnh toàn trang dt-trang-chu.png chỉ để xem bố cục chung — ô ảnh trống trong đó KHÔNG phải lỗi web.');
if (loi.length) { console.log('⚠ ' + loi.join('\n⚠ ')); process.exit(1); }
console.log('✔ Điện thoại: không tràn ngang, nút đủ to, chữ đủ lớn, không ảnh hỏng, không lỗi JS.');
