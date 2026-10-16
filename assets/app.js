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

  /* ---- タブ切替（A Day in the Life / CAREER PATH / FAQ）----
     FAQページでカテゴリタブと職種タブの2段構成を使うため、
     ページ内の全タブを1グループとして扱っていた処理を、
     tab が属する [role="tablist"] 単位にスコープした。
     タブリストが1つしかないページの挙動は変わらない。 */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab[role="tab"]'));
  var tabGroup = function (tab) {
    var list = tab.closest ? tab.closest('[role="tablist"]') : null;
    return list
      ? Array.prototype.slice.call(list.querySelectorAll(':scope > .tab[role="tab"]'))
      : tabs;
  };
  var selectTab = function (tab) {
    tabGroup(tab).forEach(function (t) {
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
  /* JS有効時だけ未選択パネルを隠す。HTMLに hidden を書かないページ（FAQ）では、
     JSが無効でもすべての質問が本文として読める。 */
  tabs.forEach(function (tab) {
    var panel = document.getElementById(tab.getAttribute('aria-controls'));
    if (panel && tab.getAttribute('aria-selected') !== 'true') panel.hidden = true;
  });
  tabs.forEach(function (tab, i) {
    tab.setAttribute('tabindex', tab.getAttribute('aria-selected') === 'true' ? '0' : '-1');
    tab.addEventListener('click', function () { selectTab(tab); });
    tab.addEventListener('keydown', function (e) {
      var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!d) return;
      e.preventDefault();
      var g = tabGroup(tab);
      var gi = g.indexOf(tab);
      var next = g[(gi + d + g.length) % g.length];
      selectTab(next);
      next.focus();
    });
  });

  /* ---- 右側固定CTA（HOMEのみ）：FVを過ぎたら表示し、ENTRY手前で隠す ---- */
  var sideCta = document.getElementById('sideCta');
  if (sideCta) {
    var entrySec = document.querySelector('.entry');
    var syncCta = function () {
      var passedHero = window.scrollY > 360;
      var nearEnd = false;
      if (entrySec) {
        nearEnd = entrySec.getBoundingClientRect().top < window.innerHeight * 0.9;
      }
      sideCta.classList.toggle('is-visible', passedHero && !nearEnd);
    };
    syncCta();
    window.addEventListener('scroll', syncCta, { passive: true });
    window.addEventListener('resize', syncCta);
  }

  /* ---- 募集要項：ひとつ開いたら他を閉じる ---- */
  var jobs = Array.prototype.slice.call(document.querySelectorAll('details.job'));
  jobs.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (!d.open) return;
      jobs.forEach(function (o) { if (o !== d) o.open = false; });
    });
  });
})();

/* ============================================================
   ===== HASH-LANDING v1：ハッシュ付きURLで開いたときの着地を確実にする =====
   html{scroll-behavior:smooth} があると、読み込み中のレイアウト確定や
   Webフォントの反映で、ブラウザ任せのスクロールが取り消されることがある。
   読み込み完了後とフォント確定後に、ページ先頭のままなら対象へ合わせ直す。
   すでにスクロールされている場合（＝利用者が動かした／ブラウザが成功した）
   場合は何もしない。位置合わせは CSS の scroll-padding-top /
   scroll-margin-top に任せる。
   ============================================================ */
(function () {
  if (!location.hash || location.hash.length < 2) return;
  var id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch (e) { return; }
  var el = document.getElementById(id);
  if (!el) return;

  var land = function () {
    if (Math.round(window.scrollY) !== 0) return;      // すでに動いていれば触らない
    if (el.getBoundingClientRect().top < window.innerHeight) return; // 画面内なら不要
    el.scrollIntoView({ behavior: 'auto', block: 'start' });
  };

  if (document.readyState === 'complete') land();
  else window.addEventListener('load', land);

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(function () { setTimeout(land, 80); });
  }
})();
