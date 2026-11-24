/* 胡天宇的小站 · 交互脚本
   主题切换 / 侧栏抽屉 / 站内搜索 / 文章目录高亮 / 阅读进度 / 代码复制
   不依赖任何框架，也不需要网络请求。 */
(function () {
  'use strict';

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------- 主题 ---------- */
  var media = window.matchMedia('(prefers-color-scheme: dark)');
  var themeColorMeta = $('meta[name="theme-color"]');

  function pref() {
    var v = store.get('theme-pref');
    return v === 'light' || v === 'dark' || v === 'system' ? v : 'system';
  }

  function resolve(p) {
    return p === 'system' ? (media.matches ? 'dark' : 'light') : p;
  }

  function paint(p) {
    var mode = resolve(p);
    var root = document.documentElement;
    root.dataset.theme = mode;
    root.dataset.themePref = p;
    if (themeColorMeta) themeColorMeta.setAttribute('content', mode === 'dark' ? '#161614' : '#fbf9f4');
    $$('[data-theme-set]').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-theme-set') === p ? 'true' : 'false');
    });
  }

  function setPref(p) {
    store.set('theme-pref', p);
    paint(p);
  }

  paint(pref());

  $$('[data-theme-set]').forEach(function (btn) {
    btn.addEventListener('click', function () { setPref(btn.getAttribute('data-theme-set')); });
  });

  var onSystem = function () { if (pref() === 'system') paint('system'); };
  if (media.addEventListener) media.addEventListener('change', onSystem);
  else if (media.addListener) media.addListener(onSystem);

  /* ---------- 侧栏抽屉 ---------- */
  var body = document.body;
  var menuBtn = $('#menuBtn');
  var sidebar = $('#sidebar');
  var backdrop = $('#backdrop');

  function closeNav() {
    body.classList.remove('nav-open');
    if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
  }
  function toggleNav() {
    var open = body.classList.toggle('nav-open');
    if (menuBtn) menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open && sidebar) {
      var first = sidebar.querySelector('a, button');
      if (first && window.innerWidth > 900) first.focus();
    }
  }
  if (menuBtn) menuBtn.addEventListener('click', toggleNav);
  if (backdrop) backdrop.addEventListener('click', closeNav);
  if (sidebar) {
    sidebar.addEventListener('click', function (e) {
      if (e.target.closest('a') && window.innerWidth <= 900) closeNav();
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && body.classList.contains('nav-open')) closeNav();
  });

  /* ---------- 阅读进度 ---------- */
  var bar = $('#progress');
  if (bar) {
    var ticking = false;
    var updateBar = function () {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      var pct = max > 0 ? Math.min(100, Math.max(0, (h.scrollTop || body.scrollTop) / max * 100)) : 0;
      bar.style.width = pct.toFixed(2) + '%';
      ticking = false;
    };
    var onScroll = function () {
      if (!ticking) { ticking = true; requestAnimationFrame(updateBar); }
    };
    document.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    updateBar();
  }

  /* ---------- 回到顶部 ---------- */
  var toTop = $('#toTop');
  if (toTop) {
    var syncTop = function () {
      if ((window.scrollY || document.documentElement.scrollTop) > 500) toTop.classList.add('show');
      else toTop.classList.remove('show');
    };
    document.addEventListener('scroll', syncTop, { passive: true });
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    syncTop();
  }

  /* ---------- 代码复制 ---------- */
  $$('.prose pre').forEach(function (pre) {
    var code = pre.querySelector('code');
    if (!code) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'copy-btn';
    btn.textContent = '复制';
    btn.setAttribute('aria-label', '复制这段代码');
    btn.addEventListener('click', function () {
      var text = code.innerText;
      var done = function () {
        btn.textContent = '已复制';
        setTimeout(function () { btn.textContent = '复制'; }, 1500);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else {
        fallback();
      }
      function fallback() {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); done(); } catch (e) {}
        document.body.removeChild(ta);
      }
    });
    pre.appendChild(btn);
  });

  /* ---------- 目录高亮 ---------- */
  var tocLinks = $$('.toc a');
  if (tocLinks.length) {
    var heads = tocLinks
      .map(function (a) {
        var id = a.getAttribute('href').slice(1);
        return document.getElementById(id);
      })
      .filter(Boolean);

    var mark = function (id) {
      tocLinks.forEach(function (a) {
        a.classList.toggle('active', !!id && a.getAttribute('href') === '#' + id);
      });
    };

    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function () {
        var passed = heads.filter(function (h) { return h.getBoundingClientRect().top < 140; });
        mark(passed.length ? passed[passed.length - 1].id : null);
      }, { rootMargin: '-80px 0px -70% 0px', threshold: [0, 1] });
      heads.forEach(function (h) { obs.observe(h); });
    } else {
      document.addEventListener('scroll', function () {
        var passed = heads.filter(function (h) { return h.getBoundingClientRect().top < 140; });
        mark(passed.length ? passed[passed.length - 1].id : null);
      }, { passive: true });
    }
  }

  /* ---------- 站内搜索 ---------- */
  var posts = window.SITE_POSTS || [];
  var dialog = $('#searchDialog');
  var input = $('#searchInput');
  var results = $('#searchResults');
  var activeIndex = -1;
  var lastFocus = null;

  function normalize(s) { return (s || '').toLowerCase(); }

  function occurrences(hay, needle) {
    var n = 0, at = 0;
    while ((at = hay.indexOf(needle, at)) >= 0) { n++; at += needle.length; }
    return n;
  }

  function score(post, terms) {
    var title = normalize(post.title);
    var body = normalize(post.body || '');
    var tags = normalize((post.tags || []).join(' ') + ' ' + (post.categories || []).join(' '));
    var total = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i];
      var s = 0;
      if (title.indexOf(t) >= 0) s += 10;
      if (tags.indexOf(t) >= 0) s += 5;
      var hits = occurrences(body, t);
      if (hits) s += 2 + Math.min(hits, 6);
      if (!s) return 0;
      total += s;
    }
    return total;
  }

  function snippet(post, terms) {
    var text = post.excerpt || '';
    var lower = text.toLowerCase();
    for (var i = 0; i < terms.length; i++) {
      var at = lower.indexOf(terms[i]);
      if (at > 18) return '…' + text.slice(at - 14, at + 46) + '…';
    }
    return text;
  }

  function render(q) {
    if (!results) return;
    var terms = normalize(q).split(/\s+/).filter(Boolean);
    var list = !terms.length
      ? posts.slice(0, 6).map(function (p) { return { post: p, s: 0 }; })
      : posts
          .map(function (p) { return { post: p, s: score(p, terms) }; })
          .filter(function (r) { return r.s > 0; })
          .sort(function (a, b) { return b.s - a.s || (a.post.date < b.post.date ? 1 : -1); })
          .slice(0, 8);

    results.innerHTML = '';
    activeIndex = -1;

    if (!list.length) {
      var empty = document.createElement('li');
      empty.className = 'empty';
      empty.textContent = '没有找到相关文章。换个词试试，比如「梯度」「Codex」。';
      results.appendChild(empty);
      return;
    }

    list.forEach(function (row) {
      var p = row.post;
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = (document.documentElement.getAttribute('data-root') || '') + p.url;
      a.innerHTML =
        '<div class="ttl"></div>' +
        '<div class="sub"><span class="when"></span> · <span class="hits"></span></div>' +
        '<div class="snip"></div>';
      a.querySelector('.ttl').textContent = p.title;
      a.querySelector('.when').textContent = p.date;
      a.querySelector('.hits').textContent = p.tags && p.tags.length ? p.tags.slice(0, 3).join(' / ') : p.categories.join(' / ');
      var snip = a.querySelector('.snip');
      var text = snippet(p, terms);
      if (terms.length) snip.textContent = text;
      else snip.remove();
      li.appendChild(a);
      results.appendChild(li);
    });
  }

  function openSearch() {
    if (!dialog) return;
    lastFocus = document.activeElement;
    render('');
    if (typeof dialog.showModal === 'function') {
      if (!dialog.open) dialog.showModal();
    } else {
      dialog.setAttribute('open', '');
    }
    if (input) {
      input.value = '';
      input.focus();
    }
  }

  function closeSearch() {
    if (!dialog) return;
    if (typeof dialog.close === 'function' && dialog.open) dialog.close();
    else dialog.removeAttribute('open');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  $$('[data-search-open]').forEach(function (b) { b.addEventListener('click', openSearch); });

  if (input) {
    input.addEventListener('input', function () { render(input.value); });
  }

  if (dialog) {
    dialog.addEventListener('click', function (e) {
      if (e.target === dialog) closeSearch();
    });
    dialog.addEventListener('close', function () {
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    });
  }

  document.addEventListener('keydown', function (e) {
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || '')) || e.target.isContentEditable;

    if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      openSearch();
      return;
    }
    if (e.key === '/' && !typing && !body.classList.contains('nav-open')) {
      e.preventDefault();
      openSearch();
      return;
    }
    if (!dialog || !dialog.open) return;

    var links = $$('#searchResults a');
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      if (!links.length) return;
      e.preventDefault();
      activeIndex = e.key === 'ArrowDown'
        ? (activeIndex + 1) % links.length
        : (activeIndex - 1 + links.length) % links.length;
      links.forEach(function (a, i) { a.classList.toggle('active', i === activeIndex); });
      links[activeIndex].scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter') {
      var target = activeIndex >= 0 ? links[activeIndex] : links[0];
      if (target) { e.preventDefault(); window.location.href = target.href; }
    }
  });

  /* ---------- 标签 / 分类过滤 ---------- */
  var groups = $$('[data-filter-group]');
  var filterBar = $('#filterBar');

  function readFilter() {
    var h = window.location.hash.replace(/^#/, '');
    if (!h) return null;
    var parts = h.split('=');
    if (parts.length !== 2) return null;
    var keys = ['tag', 'cat'];
    if (keys.indexOf(parts[0]) < 0) return null;
    return { key: parts[0], value: decodeURIComponent(parts[1]) };
  }

  function applyFilter() {
    if (!groups.length) return;
    var f = readFilter();
    var shown = 0;
    groups.forEach(function (g) {
      var match = !f || (g.dataset.filterGroup === f.key && g.dataset.filterValue === f.value);
      g.hidden = !match;
      if (match) shown++;
    });
    if (filterBar) {
      if (f) {
        filterBar.hidden = false;
        var label = filterBar.querySelector('[data-filter-label]');
        if (label) label.textContent = (f.key === 'tag' ? '标签' : '分类') + '：' + f.value;
        var count = filterBar.querySelector('[data-filter-count]');
        if (count) count.textContent = shown + ' 组';
      } else {
        filterBar.hidden = true;
      }
    }
    var none = $('#filterEmpty');
    if (none) none.hidden = shown > 0;

    // 从别处带着 #tag=… 进来时，把筛选条和命中的那一组送到视线里
    if (f && shown === 1) {
      var target = groups.filter(function (g) { return !g.hidden; })[0];
      var anchor = filterBar && !filterBar.hidden ? filterBar : target;
      if (anchor) {
        requestAnimationFrame(function () {
          var top = anchor.getBoundingClientRect().top + window.pageYOffset - 76;
          if (Math.abs(window.pageYOffset - top) > 8) {
            window.scrollTo({ top: Math.max(0, top), behavior: 'instant' });
          }
        });
      }
    }
  }

  if (groups.length) {
    window.addEventListener('hashchange', applyFilter);
    applyFilter();
  }

  /* ---------- 页脚年份 ---------- */
  $$('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
