/* ============================================================
   ===== PAL RECRUIT app.js v1：ドロワー / ヘッダー / リビール / タブ / アコーディオン =====
   ============================================================ */
(function () {
  'use strict';

  /* ---- ヘッダー：スクロールで影を出す ---- */
  var hdr = document.getElementById('hdr');
  var onScroll = function () {
    if (!hdr) return;
    hdr.classList.toggle('is-scrolled', window.scrollY > 10);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---- ドロワー開閉 ---- */
  var toggle = document.getElementById('navToggle');
  var drawer = document.getElementById('drawer');
  var setDrawer = function (open) {
    if (!toggle || !drawer) return;
    document.documentElement.classList.toggle('is-open', open);
    drawer.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
    document.body.style.overflow = open ? 'hidden' : '';
  };
  if (toggle && drawer) {
    toggle.addEventListener('click', function () {
      setDrawer(!drawer.classList.contains('is-open'));
    });
    drawer.addEventListener('click', function (e) {
      if (e.target.closest('a')) setDrawer(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setDrawer(false);
    });
  }

  /* ---- リビール（.rv を画面内で表示） ---- */
  var targets = document.querySelectorAll('.rv');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(targets, function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add('is-in');
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: '0px 0px -60px 0px', threshold: 0 });
    Array.prototype.forEach.call(targets, function (el) { io.observe(el); });

    /* 保険：タブ非表示などで IntersectionObserver が発火しない環境でも
       スクロール位置から判定して必ず表示する（.rv が透明のまま残らないように） */
    var ticking = false;
    var sweep = function () {
      ticking = false;
      var left = 0;
      Array.prototype.forEach.call(targets, function (el) {
        if (el.classList.contains('is-in')) return;
        var r = el.getBoundingClientRect();
        if (r.top < window.innerHeight - 40 && r.bottom > 0) {
          el.classList.add('is-in');
          io.unobserve(el);
        } else { left++; }
      });
      if (!left) {
        window.removeEventListener('scroll', request);
        window.removeEventListener('resize', request);
      }
    };
    var request = function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(sweep);
    };
    window.addEventListener('scroll', request, { passive: true });
    window.addEventListener('resize', request);
    window.addEventListener('load', request);
    setTimeout(request, 600);
  }

  /* ---- A Day in the Life：タブ切替 ---- */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab[role="tab"]'));
  var selectTab = function (tab) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.setAttribute('tabindex', on ? '0' : '-1');
      var panel = document.getElementById(t.getAttribute('aria-controls'));
      if (panel) {
        panel.hidden = !on;
        if (on) {
          Array.prototype.forEach.call(panel.querySelectorAll('.rv'), function (el) {
            el.classList.add('is-in');
          });
        }
      }
    });
  };
  tabs.forEach(function (tab, i) {
    tab.setAttribute('tabindex', tab.getAttribute('aria-selected') === 'true' ? '0' : '-1');
    tab.addEventListener('click', function () { selectTab(tab); });
    tab.addEventListener('keydown', function (e) {
      var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!d) return;
      e.preventDefault();
      var next = tabs[(i + d + tabs.length) % tabs.length];
      selectTab(next);
      next.focus();
    });
  });

  /* ---- 募集要項：ひとつ開いたら他を閉じる ---- */
  var jobs = Array.prototype.slice.call(document.querySelectorAll('details.job'));
  jobs.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (!d.open) return;
      jobs.forEach(function (o) { if (o !== d) o.open = false; });
    });
  });
})();
