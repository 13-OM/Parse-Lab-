/* ============================================================
   PARSE LAB — shared UI helpers, animation, renderers
   ============================================================ */
(function (global) {
  'use strict';
  const PL = global.PL;
  const EPS = PL.EPS, END = PL.END;

  /* ---------- inline SVG icons (never render as tofu) ---------- */
  const SVG = (d, extra) => '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" ' +
    'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + d + '</svg>';
  const ICON = {
    first: SVG('<polygon points="19,20 9,12 19,4" fill="currentColor" stroke="none"/><line x1="6" y1="4" x2="6" y2="20"/>'),
    prev:  SVG('<polygon points="16,19 7,12 16,5" fill="currentColor" stroke="none"/>'),
    play:  SVG('<polygon points="7,4 20,12 7,20" fill="currentColor" stroke="none"/>'),
    pause: SVG('<rect x="7" y="4" width="4" height="16" rx="1" fill="currentColor" stroke="none"/><rect x="14" y="4" width="4" height="16" rx="1" fill="currentColor" stroke="none"/>'),
    next:  SVG('<polygon points="8,5 17,12 8,19" fill="currentColor" stroke="none"/>'),
    last:  SVG('<polygon points="5,4 15,12 5,20" fill="currentColor" stroke="none"/><line x1="18" y1="4" x2="18" y2="20"/>'),
    moon:  SVG('<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" fill="currentColor" stroke="none"/>'),
    sun:   SVG('<circle cx="12" cy="12" r="4.2" fill="currentColor" stroke="none"/><g stroke-width="2"><line x1="12" y1="1.6" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22.4"/><line x1="1.6" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="22.4" y2="12"/><line x1="4.5" y1="4.5" x2="6.2" y2="6.2"/><line x1="17.8" y1="17.8" x2="19.5" y2="19.5"/><line x1="4.5" y1="19.5" x2="6.2" y2="17.8"/><line x1="17.8" y1="6.2" x2="19.5" y2="4.5"/></g>'),
    proj:  SVG('<rect x="2" y="7" width="20" height="12" rx="2.5"/><circle cx="9" cy="13" r="3"/><line x1="16" y1="13" x2="19" y2="13"/><line x1="6" y1="19" x2="5" y2="22"/><line x1="18" y1="19" x2="19" y2="22"/>'),
    menu:  SVG('<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>')
  };

  /* ---------- tiny DOM ---------- */
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => [...(r || document).querySelectorAll(s)];
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  /* ---------- symbol chips ---------- */
  function symCls(g, s) {
    if (s === EPS) return 'e';
    if (s === END) return 'end';
    return (g && g.isNT(s)) ? 'nt' : 't';
  }
  function chip(g, s) { return '<span class="sym ' + symCls(g, s) + '">' + esc(s) + '</span>'; }
  function chips(g, arr) { return (arr && arr.length) ? arr.map(s => chip(g, s)).join(' ') : chip(g, EPS); }
  function prodHTML(g, p) { return chip(g, p.lhs) + '<span class="arrow">→</span>' + chips(g, p.rhs); }

  function grammarHTML(g) {
    const order = [g.start].concat(g.nonterminals.filter(n => n !== g.start));
    const seen = new Set();
    return order.map(n => {
      if (seen.has(n)) return ''; seen.add(n);
      const ps = g.byLhs.get(n) || [];
      if (!ps.length) return '';
      return '<div>' + chip(g, n) + '<span class="arrow">→</span>' +
        ps.map(p => chips(g, p.rhs)).join(' <span class="arrow">|</span> ') + '</div>';
    }).join('');
  }

  function setHTML(g, set, kind) {
    const arr = [...set];
    const order = arr.filter(x => x !== EPS && x !== END).sort()
      .concat(arr.includes(EPS) ? [EPS] : []).concat(arr.includes(END) ? [END] : []);
    return '<span class="setval ' + (kind || '') + '">{ ' + (order.length ? order.map(s => chip(g, s)).join(' ') : '∅') + ' }</span>';
  }

  /* ---------- grammar input parse + error surface ---------- */
  function readGrammar(text, box) {
    const r = PL.parseGrammar(text);
    if (!r.ok) {
      if (box) box.innerHTML = '<div class="banner bad"><span class="bi">⚠</span><div>Grammar error<small>' +
        r.errors.map(esc).join('<br>') + '</small></div></div>';
      return null;
    }
    if (box && r.grammar.warnings.length) {
      box.innerHTML = '<div class="note warn"><span class="ni">💡</span><div>' + r.grammar.warnings.map(esc).join('<br>') + '</div></div>';
    } else if (box) box.innerHTML = '';
    return r.grammar;
  }

  /* ---------- FIRST/FOLLOW panel ---------- */
  function renderSets(g, first, follow, host) {
    let h = '<div class="grid g2">';
    h += '<div><h4 style="color:var(--term)">FIRST sets</h4>';
    g.nonterminals.forEach(n => {
      h += '<div class="setrow"><span class="setname">FIRST(' + esc(n) + ')</span>' + setHTML(g, first.get(n), 'first') + '</div>';
    });
    h += '</div><div><h4 style="color:var(--nt)">FOLLOW sets</h4>';
    g.nonterminals.forEach(n => {
      h += '<div class="setrow"><span class="setname">FOLLOW(' + esc(n) + ')</span>' + setHTML(g, follow.get(n), 'follow') + '</div>';
    });
    h += '</div></div>';
    host.innerHTML = h;
  }

  /* ---------- LL(1) table ---------- */
  function renderLL1Table(g, tbl, host, opts) {
    opts = opts || {};
    const terms = tbl.terminals;
    let h = '<div class="tw"><table class="ptable"><thead><tr><th class="rowh">NT \\ Terminal</th>';
    terms.forEach(t => h += '<th class="colh">' + esc(t) + '</th>');
    h += '</tr></thead><tbody>';
    g.nonterminals.forEach(nt => {
      h += '<tr><td class="rowh">' + esc(nt) + '</td>';
      terms.forEach(t => {
        const cell = tbl.table.get(nt).get(t);
        const id = 'c_' + nt.replace(/[^\w]/g, '_') + '_' + t.replace(/[^\w]/g, 'x');
        if (!cell || !cell.length) h += '<td class="empty" data-cell="' + esc(nt) + '|' + esc(t) + '">–</td>';
        else if (cell.length > 1)
          h += '<td class="conflict" data-cell="' + esc(nt) + '|' + esc(t) + '">' +
            cell.map(p => esc(PL.prodStr(p))).join('<br>') + '<br><small>⚠ ' + cell.length + ' entries</small></td>';
        else h += '<td class="filled" data-cell="' + esc(nt) + '|' + esc(t) + '">' + esc(PL.prodStr(cell[0])) + '</td>';
      });
      h += '</tr>';
    });
    h += '</tbody></table></div>';
    h += '<div class="legend"><span><i style="background:var(--ok-bg);border-color:var(--ok)"></i>filled entry</span>' +
      '<span><i style="background:var(--bad-bg);border-color:var(--bad)"></i>conflict (not LL(1))</span>' +
      '<span><i style="background:var(--bg-2);border-color:var(--line-2)"></i>error / blank</span></div>';
    host.innerHTML = h;
  }

  function ll1Verdict(tbl) {
    if (tbl.isLL1) return '<div class="banner ok"><span class="bi">✓</span><div>The grammar IS LL(1)<small>Every cell of the parsing table holds at most one production — no conflicts.</small></div></div>';
    let s = '<div class="banner bad"><span class="bi">✗</span><div>The grammar is NOT LL(1)<small>' +
      tbl.conflicts.length + ' cell' + (tbl.conflicts.length > 1 ? 's have' : ' has') + ' more than one production:</small></div></div>';
    s += '<div class="steps">';
    tbl.conflicts.forEach((c, i) => {
      s += '<div class="step"><span class="n">' + (i + 1) + '</span><div class="bd"><b>M[' + esc(c.nt) + ', ' + esc(c.term) + '] holds ' + c.prods.length + ' productions</b>' +
        '<pre>' + c.prods.map(p => esc(PL.prodStr(p))).join('\n') + '</pre>' +
        '<span class="muted">With lookahead <b>' + esc(c.term) + '</b> the parser cannot decide which one to use.</span></div></div>';
    });
    s += '</div>';
    return s;
  }

  /* ============================================================
     PARSE TREE renderer (SVG, animated)
     ============================================================ */
  function drawTree(root, host, opts) {
    opts = opts || {};
    host.innerHTML = '';
    if (!root) { host.innerHTML = '<p class="muted center" style="padding:40px">No tree yet — run a parse.</p>'; return null; }
    const lay = PL.layoutTree(root, { dx: opts.dx || 78, dy: opts.dy || 88 });
    const PAD = 34;
    const W = lay.width + PAD * 2, H = lay.height + PAD;
    const NS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('width', Math.max(W, 320));
    svg.setAttribute('height', Math.max(H, 200));
    svg.setAttribute('viewBox', '0 0 ' + Math.max(W, 320) + ' ' + Math.max(H, 200));

    const gEdges = document.createElementNS(NS, 'g');
    const gNodes = document.createElementNS(NS, 'g');
    svg.appendChild(gEdges); svg.appendChild(gNodes);

    const px = n => n.x + PAD + 30;
    const py = n => n.y + PAD;
    const map = new Map();

    /* edges */
    lay.nodes.forEach(n => n.children.forEach(c => {
      const p = document.createElementNS(NS, 'path');
      const x1 = px(n), y1 = py(n) + 17, x2 = px(c), y2 = py(c) - 17;
      const mid = (y1 + y2) / 2;
      p.setAttribute('d', 'M' + x1 + ',' + y1 + ' C' + x1 + ',' + mid + ' ' + x2 + ',' + mid + ' ' + x2 + ',' + y2);
      p.setAttribute('class', 'tedge');
      p.dataset.child = c.id;
      gEdges.appendChild(p);
    }));

    /* nodes */
    lay.nodes.forEach(n => {
      const g2 = document.createElementNS(NS, 'g');
      g2.setAttribute('class', 'tnode');
      g2.dataset.id = n.id;
      const label = n.sym;
      const w = Math.max(38, label.length * 12 + 22);
      const r = document.createElementNS(NS, 'rect');
      r.setAttribute('x', px(n) - w / 2); r.setAttribute('y', py(n) - 17);
      r.setAttribute('width', w); r.setAttribute('height', 34);
      const st = getComputedStyle(document.documentElement);
      const kind = n.kind === 'eps' ? 'e' : (n.kind === 'nt' ? 'nt' : 't');
      const fill = kind === 'nt' ? '--nt-bg' : kind === 't' ? '--term-bg' : '--eps-bg';
      const stroke = kind === 'nt' ? '--nt' : kind === 't' ? '--term' : '--eps';
      r.setAttribute('fill', st.getPropertyValue(fill).trim());
      r.setAttribute('stroke', st.getPropertyValue(stroke).trim());
      const t = document.createElementNS(NS, 'text');
      t.setAttribute('x', px(n)); t.setAttribute('y', py(n) + 1);
      t.setAttribute('fill', st.getPropertyValue(stroke).trim());
      t.textContent = label;
      g2.appendChild(r); g2.appendChild(t);
      gNodes.appendChild(g2);
      map.set(n.id, { g: g2, node: n });
    });

    host.appendChild(svg);
    return {
      svg: svg, map: map, nodes: lay.nodes,
      hideAll() { map.forEach(v => v.g.style.opacity = '0'); $$('.tedge', svg).forEach(e => e.style.opacity = '0'); },
      showAll() { map.forEach(v => { v.g.style.opacity = '1'; v.g.classList.remove('pulse'); }); $$('.tedge', svg).forEach(e => e.style.opacity = '1'); },
      show(id, pulse) {
        const v = map.get(id); if (!v) return;
        v.g.style.opacity = '1';
        v.g.classList.add('show');
        const e = $$('.tedge', svg).find(x => +x.dataset.child === id);
        if (e) e.style.opacity = '1';
        if (pulse) { map.forEach(x => x.g.classList.remove('pulse')); v.g.classList.add('pulse'); }
      },
      clearPulse() { map.forEach(x => x.g.classList.remove('pulse')); }
    };
  }

  /* nodes that exist after step i of an LL(1) parse */
  function visibleAfter(steps, i, root) {
    /* replay: root always visible; each expand reveals children of the expanded node */
    const vis = new Set([root.id]);
    const order = [];
    (function walk(n) { order.push(n); n.children.forEach(walk); })(root);
    /* Reconstruct by counting expansions: expansion k corresponds to the k-th 'expand' step */
    let k = 0;
    const expands = [];
    (function bfs(n) {
      if (n.children.length) expands.push(n);
      n.children.forEach(bfs);
    })(root);
    /* expands is in DFS pre-order = the order LL(1) expands them */
    for (let s = 0; s <= i; s++) {
      if (steps[s] && steps[s].cls === 'expand') {
        const n = expands[k++];
        if (n) n.children.forEach(c => vis.add(c.id));
      }
    }
    return { vis: vis, last: expands[k - 1] || null };
  }

  /* ============================================================
     STACK + TAPE renderers
     ============================================================ */
  function renderStack(g, arr, host, label) {
    let h = '<h4>' + (label || 'Parse stack') + '<span class="muted" style="font-size:.75rem">' + arr.length + ' items</span></h4>' +
      '<div class="st-label top">&#9650; top of stack</div><div class="stack-items">';
    arr.forEach((raw, i) => {
      /* an entry may be {v,k} to force a class, or a plain string */
      const s = (raw && typeof raw === 'object') ? raw.v : raw;
      let c;
      if (raw && typeof raw === 'object' && raw.k) c = raw.k;
      else if (s === '⋖' || s === '⋗' || s === '≐') c = 'rel';
      else if (s === END) c = 'end';
      else if (g && g.isNT(s)) c = 'nt';
      else if (s === 'N' || /^[A-Z]/.test(s)) c = 'nt';
      else c = 't';
      const top = i === arr.length - 1 ? ' top' : '';
      h += '<div class="st ' + c + top + '" style="animation-delay:' + Math.min(i * 22, 260) + 'ms">' + esc(s) + '</div>';
    });
    h += '</div><div class="st-label">bottom &#9660;</div>';
    host.innerHTML = h;
  }

  function renderTape(g, all, pos, host) {
    let h = '';
    all.forEach((t, i) => {
      const c = i < pos ? 'done' : (i === pos ? 'cur' : '');
      h += '<span class="tk ' + c + '">' + esc(t) + '</span>';
    });
    host.innerHTML = h;
  }

  /* ============================================================
     STEP PLAYER
     ============================================================ */
  function makePlayer(host, total, onStep, opts) {
    opts = opts || {};
    host.innerHTML =
      '<button class="pbtn" data-a="first" title="First step" aria-label="First step">' + ICON.first + '</button>' +
      '<button class="pbtn" data-a="prev" title="Previous step" aria-label="Previous step">' + ICON.prev + '</button>' +
      '<button class="pbtn main" data-a="play" title="Play / pause" aria-label="Play or pause">' + ICON.play + '</button>' +
      '<button class="pbtn" data-a="next" title="Next step" aria-label="Next step">' + ICON.next + '</button>' +
      '<button class="pbtn" data-a="last" title="Last step" aria-label="Last step">' + ICON.last + '</button>' +
      '<span class="cnt"></span>' +
      '<div class="spd">Speed <input type="range" min="1" max="10" value="' + (opts.speed || 5) + '"></div>' +
      '<div class="prog"><i style="width:0"></i></div>';

    let i = 0, timer = null, playing = false;
    const cnt = $('.cnt', host), bar = $('.prog i', host), rng = $('input[type=range]', host);
    const playBtn = $('[data-a=play]', host);

    function delay() { return 1500 - (rng.value - 1) * 145; }
    function paint() {
      cnt.textContent = 'Step ' + (i + 1) + ' / ' + total;
      bar.style.width = (total > 1 ? (i / (total - 1)) * 100 : 100) + '%';
      $('[data-a=first]', host).disabled = i === 0;
      $('[data-a=prev]', host).disabled = i === 0;
      $('[data-a=next]', host).disabled = i >= total - 1;
      $('[data-a=last]', host).disabled = i >= total - 1;
      onStep(i);
    }
    function stop() { playing = false; clearInterval(timer); playBtn.innerHTML = ICON.play; }
    function play() {
      if (i >= total - 1) i = 0;
      playing = true; playBtn.innerHTML = ICON.pause;
      clearInterval(timer);
      timer = setInterval(() => {
        if (i >= total - 1) { stop(); return; }
        i++; paint();
      }, delay());
    }
    host.addEventListener('click', e => {
      const b = e.target.closest('[data-a]'); if (!b) return;
      const a = b.dataset.a;
      if (a === 'play') { playing ? stop() : play(); return; }
      stop();
      if (a === 'first') i = 0;
      if (a === 'prev' && i > 0) i--;
      if (a === 'next' && i < total - 1) i++;
      if (a === 'last') i = total - 1;
      paint();
    });
    rng.addEventListener('input', () => { if (playing) play(); });
    paint();
    return { goto(n) { stop(); i = Math.max(0, Math.min(total - 1, n)); paint(); }, stop: stop, get index() { return i; } };
  }

  /* ============================================================
     Full LL(1) simulator widget
     ============================================================ */
  function mountLL1Sim(cfg) {
    /* cfg: {g, tbl, tokens, hosts:{stack,tape,action,tree,table,deriv}} */
    const { g, tbl, tokens, hosts } = cfg;
    const res = PL.ll1Parse(g, tbl, tokens);
    const all = tokens.concat([END]);
    let treeView = null;
    if (hosts.tree) treeView = drawTree(res.tree, hosts.tree);

    const step = i => {
      const s = res.steps[i];
      if (hosts.stack) renderStack(g, s.stack, hosts.stack);
      if (hosts.tape) renderTape(g, all, s.pos, hosts.tape);
      if (hosts.action) {
        const bdg = { init: 'Start', expand: 'Expand', match: 'Match', accept: 'Accept', error: 'Error' }[s.cls] || 'Step';
        hosts.action.className = 'action ' + s.cls;
        hosts.action.innerHTML = '<span class="bdg">' + bdg + '</span><span>' + esc(s.action) + '</span>';
      }
      if (treeView) {
        const v = visibleAfter(res.steps, i, res.tree);
        treeView.map.forEach((val, id) => {
          val.g.style.opacity = v.vis.has(id) ? '1' : '0.07';
          val.g.classList.remove('pulse');
        });
        $$('.tedge', treeView.svg).forEach(e => { e.style.opacity = v.vis.has(+e.dataset.child) ? '1' : '0.07'; });
        if (v.last && s.cls === 'expand') { const x = treeView.map.get(v.last.id); if (x) x.g.classList.add('pulse'); }
      }
      if (hosts.table) {
        $$('.ptable td.hot', hosts.table).forEach(td => td.classList.remove('hot'));
        if (s.cls === 'expand' && s.expand) {
          const look = s.input[0];
          const td = $$('.ptable td[data-cell]', hosts.table).find(x => x.dataset.cell === s.expand + '|' + look);
          if (td) { td.classList.add('hot'); }
        }
      }
    };
    return { res: res, step: step, total: res.steps.length };
  }

  /* ---------- derivation renderer ---------- */
  function renderDeriv(g, tree, host, leftmost) {
    if (!tree) { host.innerHTML = '<p class="muted">No parse tree.</p>'; return; }
    const steps = PL.derivation(tree, leftmost);
    host.innerHTML = steps.map((s, i) =>
      '<div style="animation-delay:' + i * 45 + 'ms">' + (i ? '<span class="ar">⇒</span>' : '<span class="ar" style="opacity:.35">&nbsp;&nbsp;</span>') +
      s.split(' ').map(x => chip(g, x)).join(' ') + '</div>').join('');
  }

  /* ============================================================
     Global chrome: theme, projector, nav, mobile menu
     ============================================================ */
  function initBackToLab() {
    const button = document.getElementById('backToLab');
    if (!button) return;

    const params = new URLSearchParams(window.location.search);
    const returnUrl = params.get('return');

    // A fresh return parameter always wins, so an older practical is never reused.
    if (returnUrl) {
      try {
        sessionStorage.setItem('pl-return-url', returnUrl);
        localStorage.setItem('pl-return-url', returnUrl);
      } catch (e) {
        console.warn('Could not save Lab Manual return URL:', e);
      }
    }

    const savedUrl = sessionStorage.getItem('pl-return-url') || localStorage.getItem('pl-return-url');
    if (!savedUrl) return;

    button.href = savedUrl;
    button.textContent = '← Back to Practical';
    button.style.display = 'inline-flex';
  }

     function chrome() {
    const html = document.documentElement;
    const th = localStorage.getItem('pl-theme');
    if (th) html.dataset.theme = th;
    if (localStorage.getItem('pl-proj') === 'on') html.dataset.proj = 'on';

    document.addEventListener('click', e => {
      const b = e.target.closest('[data-act]');
      if (!b) return;
      const a = b.dataset.act;
      if (a === 'theme') {
        const cur = html.dataset.theme === 'dark' ? 'light' : 'dark';
        html.dataset.theme = cur; localStorage.setItem('pl-theme', cur);
        b.innerHTML = cur === 'dark' ? ICON.sun : ICON.moon;
        document.dispatchEvent(new CustomEvent('pl-theme'));
      }
      if (a === 'proj') {
        const on = html.dataset.proj === 'on' ? '' : 'on';
        html.dataset.proj = on; localStorage.setItem('pl-proj', on);
        b.classList.toggle('live', on === 'on');
        b.title = on ? 'Projector mode ON (big text)' : 'Projector mode';
      }
      if (a === 'menu') $('.nav').classList.toggle('open');
    });
    /* set initial icon states */
    const tb = $('[data-act=theme]'); if (tb) tb.innerHTML = html.dataset.theme === 'dark' ? ICON.sun : ICON.moon;
    const pb = $('[data-act=proj]'); if (pb) { pb.innerHTML = ICON.proj; if (html.dataset.proj === 'on') pb.classList.add('live'); }
    const mb = $('[data-act=menu]'); if (mb) mb.innerHTML = ICON.menu;

    /* mark active nav link */
    const here = location.pathname.split('/').pop() || 'index.html';
    $$('.nav a').forEach(a => { if ((a.getAttribute('href') || '').split('/').pop() === here) a.classList.add('on'); });
  }

  global.UI = {
    $, $$, el, esc, chip, chips, prodHTML, grammarHTML, setHTML, readGrammar,
    renderSets, renderLL1Table, ll1Verdict, drawTree, renderStack, renderTape,
    makePlayer, mountLL1Sim, renderDeriv, chrome, symCls
  };
  document.addEventListener('DOMContentLoaded', () => {
  chrome();
  initBackToLab();
});
})(typeof window !== 'undefined' ? window : globalThis);
