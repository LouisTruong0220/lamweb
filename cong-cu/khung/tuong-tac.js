/* Hiệu ứng & tương tác — không thư viện. Web vẫn đọc được đủ khi JS tắt
   (lớp .js chỉ được gắn khi script chạy, mọi trạng thái "ẩn chờ hiệu ứng" đều treo vào nó). */
(function () {
  var $ = function (s, g) { return (g || document).querySelector(s); };
  var $$ = function (s, g) { return [].slice.call((g || document).querySelectorAll(s)); };
  var itChuyenDong = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var coChuot = matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* Thanh trên đổi nền khi cuộn */
  var nav = $('.nav');
  var cuon = function () { nav && nav.classList.toggle('cuon', scrollY > 16); };
  addEventListener('scroll', cuon, { passive: true }); cuon();

  /* Menu điện thoại */
  var burger = $('.burger'), menu = $('.menu');
  if (burger && menu) {
    burger.addEventListener('click', function () {
      var mo = !burger.classList.contains('mo');
      burger.classList.toggle('mo', mo); menu.classList.toggle('mo', mo);
      burger.setAttribute('aria-expanded', mo ? 'true' : 'false');
    });
    $$('a', menu).forEach(function (a) {
      a.addEventListener('click', function () { burger.classList.remove('mo'); menu.classList.remove('mo'); });
    });
  }

  /* Trượt lên khi cuộn tới */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: .12, rootMargin: '0px 0px -40px 0px' });
    $$('.reveal').forEach(function (el) { io.observe(el); });
  } else { $$('.reveal').forEach(function (el) { el.classList.add('in'); }); }

  /* Dải chữ chạy: nhân đôi để chạy vô tận */
  $$('.marquee-track').forEach(function (t) { t.innerHTML += t.innerHTML; });

  /* Ảnh bìa thay nhau */
  var bia = $$('.bia-anh img'), nhan = $('.bia-anh .nhan-anh');
  if (bia.length > 1 && !itChuyenDong) {
    var i = 0;
    setInterval(function () {
      bia[i].classList.remove('hien'); i = (i + 1) % bia.length; bia[i].classList.add('hien');
      if (nhan) nhan.innerHTML = bia[i].getAttribute('data-nhan') || '';
    }, 3800);
  }

  /* Đếm số */
  if ('IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return; co.unobserve(e.target);
        var el = e.target, to = +el.getAttribute('data-to'), t0 = performance.now(), dur = itChuyenDong ? 1 : 1800;
        (function buoc(t) {
          var p = Math.min((t - t0) / dur, 1), v = Math.round(to * (1 - Math.pow(1 - p, 4)));
          el.textContent = v.toLocaleString('vi-VN'); if (p < 1) requestAnimationFrame(buoc);
        })(t0);
      });
    }, { threshold: .5 });
    $$('.dem').forEach(function (el) { co.observe(el); });
  }

  /* "Vì sao chọn": thẻ ở giữa màn hình thì sáng lên, khung ảnh đổi theo */
  var muc = $$('.chon-item'), canh = $$('.chon-vis .canh');
  var bat = function (k) {
    muc.forEach(function (x, j) { x.classList.toggle('active', j === k); });
    canh.forEach(function (x, j) { x.classList.toggle('on', j === k); });
  };
  if (muc.length && 'IntersectionObserver' in window) {
    var io2 = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) bat(+e.target.getAttribute('data-i')); });
    }, { rootMargin: '-42% 0px -42% 0px' });
    muc.forEach(function (x) {
      io2.observe(x);
      x.addEventListener('mouseenter', function () { bat(+x.getAttribute('data-i')); });
      x.addEventListener('click', function () { bat(+x.getAttribute('data-i')); });
    });
  }

  /* Tab với viên thuốc trượt */
  var tabs = $$('.tab-link'), panes = $$('.tab-pane'), pill = $('.tab-pill');
  var dichPill = function () {
    var c = $('.tab-link.cur'); if (!c || !pill) return;
    pill.style.left = c.offsetLeft + 'px'; pill.style.width = c.offsetWidth + 'px';
  };
  tabs.forEach(function (l) {
    l.addEventListener('click', function () {
      var k = +l.getAttribute('data-t');
      tabs.forEach(function (x, j) { x.classList.toggle('cur', j === k); x.setAttribute('aria-selected', j === k ? 'true' : 'false'); });
      panes.forEach(function (x, j) { x.classList.toggle('cur', j === k); });
      dichPill(); l.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' });
    });
  });
  addEventListener('resize', dichPill); dichPill();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(dichPill);

  /* Chữ giới thiệu sáng dần theo cuộn */
  var sc = $('.scrub');
  if (sc) {
    sc.innerHTML = sc.textContent.trim().split(/\s+/).map(function (w) { return '<span class="w">' + w + '</span>'; }).join(' ');
    var tu = $$('.w', sc);
    var scrub = function () {
      var r = sc.getBoundingClientRect(), vh = innerHeight, p = (vh * .85 - r.top) / (r.height + vh * .35);
      p = Math.max(0, Math.min(1, p)); var n = Math.round(p * tu.length);
      tu.forEach(function (w, k) { w.classList.toggle('lit', k < n); });
    };
    addEventListener('scroll', scrub, { passive: true }); scrub();
  }

  /* Hỏi đáp: mở một câu, đóng câu khác */
  var faq = $$('.faq-item');
  faq.forEach(function (f) {
    $('.faq-q', f).addEventListener('click', function () {
      var dangMo = f.classList.contains('mo');
      faq.forEach(function (x) { x.classList.remove('mo'); $('.faq-q', x).setAttribute('aria-expanded', 'false'); });
      if (!dangMo) { f.classList.add('mo'); $('.faq-q', f).setAttribute('aria-expanded', 'true'); }
    });
  });

  /* Thẻ bìa nghiêng theo chuột + quầng sáng theo con trỏ (chỉ máy có chuột) */
  var sk = $('.san-khau'), tb = $('.the-bia'), ct = $('.con-tro');
  if (coChuot && !itChuyenDong) {
    if (sk && tb) {
      sk.addEventListener('mousemove', function (e) {
        var r = sk.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        tb.style.transform = 'rotateY(' + x * 10 + 'deg) rotateX(' + (-y * 10) + 'deg)';
      });
      sk.addEventListener('mouseleave', function () { tb.style.transform = ''; });
    }
    if (ct) addEventListener('mousemove', function (e) { ct.style.left = e.clientX + 'px'; ct.style.top = e.clientY + 'px'; });
  }

  /* Chữ thương hiệu khổng lồ ở chân trang: tự thu nhỏ cho vừa khung — tên dài ngắn gì cũng không bị cắt */
  var cl = $('.chu-lon');
  if (cl) {
    var vua = function () {
      cl.style.fontSize = '';
      var co = parseFloat(getComputedStyle(cl).fontSize), k = cl.clientWidth / cl.scrollWidth;
      if (k < 1) cl.style.fontSize = (co * k * 0.97) + 'px';
    };
    vua(); addEventListener('resize', vua);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(vua);
  }

  /* ─────────── phần dùng được việc ─────────── */
  var thongBao = function (chu) {
    var t = $('.thong-bao');
    if (!t) { t = document.createElement('div'); t.className = 'thong-bao'; t.setAttribute('role', 'status'); document.body.appendChild(t); }
    t.textContent = chu; t.classList.add('hien');
    clearTimeout(t._h); t._h = setTimeout(function () { t.classList.remove('hien'); }, 2800);
  };
  var chep = function (chu) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(chu);
    return new Promise(function (ok, loi) {
      var o = document.createElement('textarea'); o.value = chu; o.setAttribute('readonly', '');
      o.style.position = 'fixed'; o.style.opacity = '0'; document.body.appendChild(o); o.select();
      try { document.execCommand('copy') ? ok() : loi(); } catch (e) { loi(e); } finally { o.remove(); }
    });
  };
  var moZalo = function (link, chu, loiNhan) {
    chep(chu).then(function () { thongBao(loiNhan || 'Đã chép nội dung — mở Zalo rồi dán vào khung chat'); setTimeout(function () { location.href = link; }, 900); },
      function () { location.href = link; });
  };

  /* Lọc sản phẩm theo nhóm */
  var nutLoc = $$('.loc button');
  nutLoc.forEach(function (n) {
    n.addEventListener('click', function () {
      var dm = n.getAttribute('data-dm');
      nutLoc.forEach(function (k) { k.setAttribute('aria-pressed', k === n ? 'true' : 'false'); });
      $$('#luoi-sp .the-sp').forEach(function (the) { the.hidden = !(dm === '*' || the.getAttribute('data-dm') === dm); });
    });
  });

  /* Ảnh sản phẩm vuốt ngang: đếm 1/4 + chấm */
  $$('.bo-anh').forEach(function (bo) {
    var truot = $('.truot', bo), dem = $('.dem-anh', bo), cham = $$('.cham button', bo), tong = truot.children.length;
    var ve = function () {
      var k = Math.round(truot.scrollLeft / truot.clientWidth);
      if (dem) dem.textContent = (k + 1) + '/' + tong;
      cham.forEach(function (c, j) { c.setAttribute('aria-current', j === k ? 'true' : 'false'); });
    };
    truot.addEventListener('scroll', function () { requestAnimationFrame(ve); }, { passive: true });
    cham.forEach(function (c, j) { c.addEventListener('click', function () { truot.scrollTo({ left: j * truot.clientWidth, behavior: 'smooth' }); }); });
    ve();
  });

  /* Nút Zalo có data-chep: chép sẵn câu hỏi rồi mới mở Zalo */
  $$('a[data-chep]').forEach(function (a) {
    a.addEventListener('click', function (e) { e.preventDefault(); moZalo(a.href, a.getAttribute('data-chep'), 'Đã chép tên sản phẩm — mở Zalo rồi dán vào khung chat'); });
  });

  /* Chia sẻ */
  $$('[data-chia-se]').forEach(function (n) {
    n.addEventListener('click', function () {
      var dl = { title: document.title, url: location.href };
      if (navigator.share) { navigator.share(dl).catch(function () {}); return; }
      chep(dl.url).then(function () { thongBao('Đã chép đường link'); }, function () {});
    });
  });

  /* Form nhận báo giá: KHÔNG có máy chủ — soạn sẵn tin nhắn rồi mở Zalo / SMS */
  var f = $('form.dat');
  if (f) {
    var soan = function () {
      var g = function (n) { var el = f.elements[n]; return el ? el.value.trim() : ''; };
      var dong = ['Chào ' + f.getAttribute('data-ten') + ', tôi muốn nhận báo giá.'];
      if (g('ten')) dong.push('Tên: ' + g('ten'));
      if (g('sdt')) dong.push('SĐT: ' + g('sdt'));
      if (g('sp')) dong.push('Sản phẩm: ' + g('sp'));
      if (g('sl')) dong.push('Số lượng: ' + g('sl'));
      if (g('nhan')) dong.push('Lời nhắn: ' + g('nhan'));
      return dong.join('\n');
    };
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.reportValidity()) return;
      var cach = (e.submitter && e.submitter.getAttribute('data-cach')) || 'zalo', chu = soan();
      if (cach === 'sms') location.href = 'sms:' + f.getAttribute('data-sdt') + '?&body=' + encodeURIComponent(chu);
      else moZalo(f.getAttribute('data-zalo'), chu, 'Đã chép yêu cầu — mở Zalo rồi dán vào khung chat');
    });
  }
})();
