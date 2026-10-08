/* Tương tác nhỏ, không thư viện. Web vẫn dùng được đầy đủ khi JS tắt —
   JS chỉ thêm: lọc danh mục, đếm ảnh khi vuốt, chép tên sản phẩm trước khi
   mở Zalo, nút chia sẻ của điện thoại. */
(function () {
  var dau = document.querySelector('.dau');
  if (dau) {
    var capNhat = function () { dau.classList.toggle('cuon', window.scrollY > 8); };
    window.addEventListener('scroll', capNhat, { passive: true }); capNhat();
  }

  var thongBao = function (chu) {
    var t = document.querySelector('.thong-bao');
    if (!t) { t = document.createElement('div'); t.className = 'thong-bao'; t.setAttribute('role', 'status'); document.body.appendChild(t); }
    t.textContent = chu; t.classList.add('hien');
    clearTimeout(t._h); t._h = setTimeout(function () { t.classList.remove('hien'); }, 2600);
  };

  var chep = function (chu) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(chu);
    return new Promise(function (ok, loi) {
      var o = document.createElement('textarea'); o.value = chu; o.setAttribute('readonly', '');
      o.style.position = 'fixed'; o.style.opacity = '0'; document.body.appendChild(o); o.select();
      try { document.execCommand('copy') ? ok() : loi(); } catch (e) { loi(e); } finally { o.remove(); }
    });
  };

  /* Lọc sản phẩm theo danh mục */
  var nutLoc = document.querySelectorAll('.loc button');
  nutLoc.forEach(function (n) {
    n.addEventListener('click', function () {
      var dm = n.getAttribute('data-dm');
      nutLoc.forEach(function (k) { k.setAttribute('aria-pressed', k === n ? 'true' : 'false'); });
      document.querySelectorAll('.the-sp').forEach(function (the) {
        the.hidden = !(dm === '*' || the.getAttribute('data-dm') === dm);
      });
    });
  });

  /* Bộ ảnh vuốt ngang: đếm 1/4 + chấm */
  document.querySelectorAll('.bo-anh').forEach(function (bo) {
    var truot = bo.querySelector('.truot'), dem = bo.querySelector('.dem-anh');
    var cham = bo.querySelectorAll('.cham button'), tong = truot.children.length;
    var hienTai = function () { return Math.round(truot.scrollLeft / truot.clientWidth); };
    var ve = function () {
      var i = hienTai();
      if (dem) dem.textContent = (i + 1) + '/' + tong;
      cham.forEach(function (c, k) { c.setAttribute('aria-current', k === i ? 'true' : 'false'); });
    };
    truot.addEventListener('scroll', function () { window.requestAnimationFrame(ve); }, { passive: true });
    cham.forEach(function (c, k) {
      c.addEventListener('click', function () { truot.scrollTo({ left: k * truot.clientWidth, behavior: 'smooth' }); });
    });
    ve();
  });

  /* Nút Zalo có data-chep: chép sẵn câu hỏi rồi mới mở Zalo — khách chỉ việc dán */
  document.querySelectorAll('a[data-chep]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var di = function () { window.location.href = a.href; };
      chep(a.getAttribute('data-chep')).then(function () {
        thongBao('Đã chép tên sản phẩm — mở Zalo rồi dán vào khung chat');
        setTimeout(di, 900);
      }, di);
    });
  });

  /* Chia sẻ: dùng bảng chia sẻ của điện thoại (Zalo, Messenger…), máy tính thì chép link */
  document.querySelectorAll('[data-chia-se]').forEach(function (n) {
    n.addEventListener('click', function () {
      var dl = { title: document.title, url: window.location.href };
      if (navigator.share) { navigator.share(dl).catch(function () {}); return; }
      chep(dl.url).then(function () { thongBao('Đã chép đường link'); }, function () {});
    });
  });
})();
