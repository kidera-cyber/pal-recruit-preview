/* =========================================================
   PAL RECRUIT — interactions
   ========================================================= */
(function(){
  'use strict';

  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- NAV: scrolled state + mobile toggle ---------- */
  const hdr = document.getElementById('hdr');
  const onScroll = () => hdr.classList.toggle('scrolled', window.scrollY > 40);
  onScroll();
  window.addEventListener('scroll', onScroll, {passive:true});

  const menuBtn = document.getElementById('menuToggle');
  const navLinks = document.getElementById('navLinks');
  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', () => {
      const open = navLinks.classList.toggle('open');
      menuBtn.classList.toggle('open', open);
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      navLinks.classList.remove('open');
      menuBtn.classList.remove('open');
    }));
  }

  /* ---------- REVEAL on scroll ----------
     Uses IntersectionObserver, with a scroll+resize fallback because IO
     is unreliable in some iframe contexts (never fires isIntersecting=true). */
  const revealEls = () => Array.from(document.querySelectorAll('.reveal:not(.in)'));

  function revealInView() {
    const vh = window.innerHeight || document.documentElement.clientHeight;
    revealEls().forEach(el => {
      const r = el.getBoundingClientRect();
      // reveal if the element's top is above (vh * 1.1) — i.e. near or in view
      if (r.top < vh * 1.1 && r.bottom > -40) el.classList.add('in');
    });
  }

  let ioFired = false;
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          ioFired = true;
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    }, {threshold: 0.14, rootMargin: '0px 0px -40px 0px'});
    revealEls().forEach(el => io.observe(el));
  }

  // Immediate first pass (hero + above-fold)
  revealInView();

  // Fallback: if IO never fired within 500ms, fully rely on scroll-based reveal
  setTimeout(() => {
    if (!ioFired) {
      revealInView();
    }
  }, 500);

  // Continuous scroll/resize pass — safe: no-op once elements have .in
  window.addEventListener('scroll', revealInView, {passive: true});
  window.addEventListener('resize', revealInView);

  /* ---------- FLOW-STEP stagger (why section) ---------- */
  const flowVisual = document.querySelector('.why-visual');
  let flowFired = false;
  function fireFlowStagger() {
    if (flowFired || !flowVisual) return;
    const r = flowVisual.getBoundingClientRect();
    const vh = window.innerHeight;
    if (r.top < vh * 0.9 && r.bottom > 0) {
      flowFired = true;
      const items = flowVisual.querySelectorAll('.flow-step, .flow-conn');
      items.forEach((s, i) => setTimeout(() => s.classList.add('in'), i * 140));
    }
  }
  if (flowVisual) {
    if ('IntersectionObserver' in window) {
      const fio = new IntersectionObserver((entries) => {
        entries.forEach(e => {
          if (e.isIntersecting && !flowFired) {
            flowFired = true;
            const items = flowVisual.querySelectorAll('.flow-step, .flow-conn');
            items.forEach((s, i) => setTimeout(() => s.classList.add('in'), i * 140));
            fio.disconnect();
          }
        });
      }, {threshold: 0.35});
      fio.observe(flowVisual);
    }
    // fallback
    window.addEventListener('scroll', fireFlowStagger, {passive: true});
    fireFlowStagger();
  }

  /* ---------- COUNTER animation ---------- */
  function animateCount(el) {
    const target = +el.dataset.count;
    const suf = el.dataset.suffix || '';
    if (reduceMotion) {
      el.innerHTML = target.toLocaleString('en-US') + (suf ? `<span class="u">${suf}</span>` : '');
      return;
    }
    const dur = 1600, t0 = performance.now();
    function tick(t) {
      const p = Math.min((t - t0) / dur, 1);
      const ease = 1 - Math.pow(1 - p, 3);
      const v = Math.round(target * ease);
      el.textContent = v.toLocaleString('en-US');
      if (p < 1) requestAnimationFrame(tick);
      else el.innerHTML = target.toLocaleString('en-US') + (suf ? `<span class="u">${suf}</span>` : '');
    }
    requestAnimationFrame(tick);
  }
  const statEls = document.querySelectorAll('.stat');
  const countedSet = new WeakSet();
  function countInView() {
    const vh = window.innerHeight;
    statEls.forEach(s => {
      if (countedSet.has(s)) return;
      const r = s.getBoundingClientRect();
      if (r.top < vh * 0.9 && r.bottom > 0) {
        countedSet.add(s);
        const num = s.querySelector('.num');
        if (num) animateCount(num);
      }
    });
  }
  if ('IntersectionObserver' in window) {
    const cio = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting && !countedSet.has(e.target)) {
          countedSet.add(e.target);
          const num = e.target.querySelector('.num');
          if (num) animateCount(num);
          cio.unobserve(e.target);
        }
      });
    }, {threshold: 0.5});
    statEls.forEach(s => cio.observe(s));
  }
  // fallback
  window.addEventListener('scroll', countInView, {passive: true});
  countInView();

  /* ---------- DAY IN THE LIFE tabs ---------- */
  const tabs = document.querySelectorAll('.day-tab');
  const panels = document.querySelectorAll('.day-panel');
  function revealTl(panel) {
    const items = panel.querySelectorAll('.tl-item');
    items.forEach((it, i) => {
      it.classList.remove('in');
      setTimeout(() => it.classList.add('in'), 60 + i * 80);
    });
  }
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const key = tab.dataset.day;
      const panel = document.querySelector(`.day-panel[data-panel="${key}"]`);
      if (panel) {
        panel.classList.add('active');
        revealTl(panel);
      }
    });
  });
  // reveal initial panel when scrolled into view
  const daySec = document.getElementById('day');
  let dayFired = false;
  function fireDayReveal() {
    if (dayFired || !daySec) return;
    const r = daySec.getBoundingClientRect();
    const vh = window.innerHeight;
    if (r.top < vh * 0.85 && r.bottom > 0) {
      dayFired = true;
      const active = document.querySelector('.day-panel.active');
      if (active) revealTl(active);
    }
  }
  if (daySec) {
    if ('IntersectionObserver' in window) {
      const dio = new IntersectionObserver((entries) => {
        entries.forEach(e => {
          if (e.isIntersecting && !dayFired) {
            dayFired = true;
            const active = document.querySelector('.day-panel.active');
            if (active) revealTl(active);
            dio.disconnect();
          }
        });
      }, {threshold: 0.25});
      dio.observe(daySec);
    }
    window.addEventListener('scroll', fireDayReveal, {passive: true});
    fireDayReveal();
  }

  /* ---------- ACCORDION (募集要項) ---------- */
  document.querySelectorAll('.acc-head').forEach(head => {
    head.addEventListener('click', () => {
      const acc = head.closest('.acc');
      const body = acc.querySelector('.acc-body');
      const open = acc.classList.toggle('open');
      head.setAttribute('aria-expanded', open ? 'true' : 'false');
      body.style.maxHeight = open ? body.scrollHeight + 'px' : '0px';
    });
  });

  /* ---------- HERO PARTICLES ---------- */
  const canvas = document.getElementById('particles');
  if (canvas && !reduceMotion) {
    const ctx = canvas.getContext('2d');
    const hero = document.querySelector('.hero');
    let W, H, particles = [];

    function resize() {
      const rect = hero.getBoundingClientRect();
      W = canvas.width = rect.width * (window.devicePixelRatio || 1);
      H = canvas.height = rect.height * (window.devicePixelRatio || 1);
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
    }
    resize();
    window.addEventListener('resize', resize);

    const COUNT = Math.min(90, Math.max(40, Math.floor(window.innerWidth / 22)));
    for (let i = 0; i < COUNT; i++) {
      particles.push({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        r: Math.random() * 1.4 + 0.4,
        c: Math.random() > 0.6 ? 'rgba(0,212,200,' : 'rgba(143,166,255,'
      });
    }

    const MAX_D = 130 * (window.devicePixelRatio || 1);

    function draw() {
      ctx.clearRect(0, 0, W, H);
      // draw connections
      for (let i = 0; i < particles.length; i++) {
        const a = particles[i];
        for (let j = i + 1; j < particles.length; j++) {
          const b = particles[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const d = Math.sqrt(dx * dx + dy * dy);
          if (d < MAX_D) {
            const alpha = (1 - d / MAX_D) * 0.28;
            ctx.strokeStyle = `rgba(143,166,255,${alpha})`;
            ctx.lineWidth = 1 * (window.devicePixelRatio || 1);
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      }
      // draw particles
      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * (window.devicePixelRatio || 1), 0, Math.PI * 2);
        ctx.fillStyle = p.c + '0.7)';
        ctx.fill();
      });
      requestAnimationFrame(draw);
    }
    draw();
  }

  /* ---------- HERO PHOTO PARALLAX (subtle) ---------- */
  const heroPhoto = document.querySelector('.hero-photo');
  if (heroPhoto && !reduceMotion) {
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if (y < window.innerHeight * 1.2) {
        heroPhoto.style.transform = `scale(1.05) translateY(${y * 0.15}px)`;
      }
    }, {passive: true});
  }

  /* ---------- SMOOTH SCROLL offset (accounted for by scroll-padding, but ensure hash close mobile menu) ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const href = a.getAttribute('href');
      if (href && href.length > 1 && document.querySelector(href)) {
        // let browser handle smooth scroll via scroll-behavior:smooth
        // but close mobile menu
        if (navLinks) navLinks.classList.remove('open');
        if (menuBtn) menuBtn.classList.remove('open');
      }
    });
  });

})();
