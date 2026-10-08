// Chụp website ở cỡ ĐIỆN THOẠI (và máy tính) để Claude tự soi trước khi giao link.
//
//   node cong-cu/chup-man-hinh.mjs khach-hang/<slug>
//
// Ra: khach-hang/<slug>/soi/  dt-trang-chu.png · dt-trang-chu-man-dau.png · dt-san-pham.png · mt-trang-chu.png
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
      if (s.display === 'none' || s.visibility === 'hidden' || b.width === 0) continue;
      if (el.closest('.mo-ta, .gioi-thieu p, .chan')) continue;          // link nằm trong đoạn văn thì chấp nhận
      if (b.height < 40 || b.width < 40) r.nho.push((el.innerText || el.getAttribute('aria-label') || el.className).trim().slice(0, 30) + ` (${Math.round(b.width)}×${Math.round(b.height)})`);
    }
    for (const el of document.querySelectorAll('p, li, span, td, th, small, a, h3')) {
      const s = getComputedStyle(el);
      if (el.innerText && el.innerText.trim() && parseFloat(s.fontSize) < 13.5 && s.display !== 'none' && !el.closest('.thanh-day'))
        r.chuNho.push(el.innerText.trim().slice(0, 30) + ` (${s.fontSize})`);
    }
    for (const im of document.images) if (im.complete && im.naturalWidth === 0) r.anhHong.push(im.getAttribute('src'));
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
  await trang.evaluate(async () => {           // cuộn hết để ảnh lazy tải xong
    for (let y = 0; y < document.body.scrollHeight; y += 500) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
    window.scrollTo(0, 0);
  });
  await trang.waitForTimeout(400);
  if (khung.isMobile) await soi(trang, ten);
  await trang.screenshot({ path: path.join(ra, ten + '.png'), fullPage: !motMan });
  if (khung.isMobile && !motMan) await trang.screenshot({ path: path.join(ra, ten + '-man-dau.png') });
  await ctx.close();
}

const DT = { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, locale: 'vi-VN' };
const MT = { viewport: { width: 1366, height: 860 }, locale: 'vi-VN' };
await chup('/', 'dt-trang-chu', DT);
if (spDau) await chup(`/san-pham/${spDau}/`, 'dt-san-pham', DT);
await chup('/', 'mt-trang-chu', MT, true);
await trinh.close();
may.close();

console.log('Ảnh chụp ở ' + ra + ' — đọc dt-trang-chu-man-dau.png trước (khách thấy gì đầu tiên).');
if (loi.length) { console.log('⚠ ' + loi.join('\n⚠ ')); process.exit(1); }
console.log('✔ Điện thoại: không tràn ngang, nút đủ to, chữ đủ lớn, không ảnh hỏng, không lỗi JS.');
