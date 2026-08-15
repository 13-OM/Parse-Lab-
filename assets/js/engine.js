/* ============================================================
   PARSE LAB ENGINE  —  Context-Free Grammar algorithms
   Pure, dependency-free. Exposed as window.PL
   ============================================================ */
(function (global) {
  'use strict';

  const EPS = 'ε';
  const END = '$';

  /* Multi-character lowercase terminals recognised as ONE token. */
  const MULTI = ['id', 'num', 'int', 'float', 'real', 'digit', 'letter',
    'if', 'then', 'else', 'while', 'begin', 'end', 'print', 'call'];

  const EPS_CHARS = new Set(['ε', '€', '∈', 'λ', 'ϵ', '∊', '#']);
  const EPS_WORDS = new Set(['epsilon', 'eps', 'lambda', 'empty', 'null']);

  /* ---------- tokenizer ---------- */
  function tokenize(str, opts) {
    opts = opts || {};
    const useMulti = opts.multi !== false;
    const out = [];
    let i = 0;
    while (i < str.length) {
      const c = str[i];
      if (/\s/.test(c)) { i++; continue; }

      /* quoted literal terminal */
      if (c === "'" || c === '"' || c === '`') {
        let j = i + 1, buf = '';
        while (j < str.length && str[j] !== c) { buf += str[j]; j++; }
        if (buf.length) out.push(buf);
        i = j + 1; continue;
      }

      /* epsilon symbols */
      if (EPS_CHARS.has(c)) { out.push(EPS); i++; continue; }

      /* nonterminal: uppercase + primes/digits/subscripts */
      if (/[A-Z]/.test(c)) {
        let j = i + 1, buf = c;
        while (j < str.length && /['′’`0-9₀-₉]/.test(str[j])) { buf += str[j]; j++; }
        out.push(buf); i = j; continue;
      }

      /* epsilon written as a word */
      const restLower = str.slice(i).toLowerCase();
      let wordHit = null;
      for (const w of EPS_WORDS) {
        if (restLower.startsWith(w) && !/[a-z0-9]/i.test(str[i + w.length] || '')) { wordHit = w; break; }
      }
      if (wordHit) { out.push(EPS); i += wordHit.length; continue; }

      /* known multi-character terminal */
      if (useMulti && /[a-z]/.test(c)) {
        let best = null;
        for (const w of MULTI) {
          if (restLower.startsWith(w) && w.length > (best ? best.length : 0)) {
            const nxt = str[i + w.length] || '';
            if (!/[a-z]/.test(nxt)) best = w;
          }
        }
        if (best) { out.push(str.substr(i, best.length)); i += best.length; continue; }
      }

      out.push(c); i++;
    }
    return out;
  }

  /* ---------- grammar parsing ---------- */
  function parseGrammar(text, opts) {
    opts = opts || {};
    const slashAlt = opts.slashAlt !== false;
    const lines = text.split(/\r?\n/);
    const prods = [];
    const ntSet = new Set();
    const order = [];
    let start = null;
    const errors = [];

    lines.forEach((raw, ln) => {
      let line = raw.trim();
      if (!line || line.startsWith('//') || line.startsWith('#!')) return;
      line = line.replace(/->|=>|::=|:=|-&gt;/g, '→');
      if (!line.includes('→')) { errors.push('Line ' + (ln + 1) + ': missing "→" or "->"'); return; }
      const parts = line.split('→');
      const lhsRaw = parts[0].trim();
      const rhsRaw = parts.slice(1).join('→');
      const lhsTok = tokenize(lhsRaw, opts);
      if (lhsTok.length !== 1 || !/^[A-Z]/.test(lhsTok[0])) {
        errors.push('Line ' + (ln + 1) + ': left side "' + lhsRaw + '" must be a single non-terminal (start with a capital letter)');
        return;
      }
      const lhs = lhsTok[0];
      if (!ntSet.has(lhs)) { ntSet.add(lhs); order.push(lhs); }
      if (start === null) start = lhs;

      let alts = rhsRaw.split('|');
      if (slashAlt) {
        const re = /(?<!['"`])\//;
        alts = alts.flatMap(a => a.split('/'));
      }
      alts.forEach(a => {
        const toks = tokenize(a, opts);
        const rhs = toks.filter(t => t !== EPS);
        if (toks.length && rhs.length !== toks.length && rhs.length > 0) {
          /* ε mixed with real symbols -> ignore the ε */
        }
        if (a.trim() === '' && alts.length > 1) { errors.push('Line ' + (ln + 1) + ': empty alternative'); return; }
        prods.push({ lhs: lhs, rhs: rhs });
      });
    });

    if (!prods.length) errors.push('No productions found.');
    if (errors.length) return { ok: false, errors: errors };

    /* classify symbols */
    prods.forEach(p => p.rhs.forEach(s => { if (/^[A-Z]/.test(s) && !ntSet.has(s)) { /* undefined NT */ } }));
    const nts = order.slice();
    const ntLookup = new Set(nts);
    const terms = [];
    const tSeen = new Set();
    prods.forEach(p => p.rhs.forEach(s => {
      if (!ntLookup.has(s) && !tSeen.has(s)) { tSeen.add(s); terms.push(s); }
    }));

    const g = makeGrammar(nts, terms, prods, opts.start || start);
    /* warn about undefined nonterminals used on RHS */
    g.warnings = [];
    prods.forEach(p => p.rhs.forEach(s => {
      if (/^[A-Z]/.test(s) && !ntLookup.has(s) && !g.warnings.includes(s)) {
        g.warnings.push(s);
      }
    }));
    g.warnings = g.warnings.map(s => 'Symbol "' + s + '" looks like a non-terminal but has no production — treated as a terminal.');
    return { ok: true, grammar: g };
  }

  function makeGrammar(nts, terms, prods, start) {
    prods = prods.map((p, i) => ({ id: i, lhs: p.lhs, rhs: p.rhs.slice() }));
    const byLhs = new Map();
    nts.forEach(n => byLhs.set(n, []));
    prods.forEach(p => { if (!byLhs.has(p.lhs)) byLhs.set(p.lhs, []); byLhs.get(p.lhs).push(p); });
    return {
      start: start, nonterminals: nts.slice(), terminals: terms.slice(),
      prods: prods, byLhs: byLhs,
      isNT: s => byLhs.has(s),
      warnings: []
    };
  }

  function cloneGrammar(g) {
    return makeGrammar(g.nonterminals, g.terminals, g.prods.map(p => ({ lhs: p.lhs, rhs: p.rhs.slice() })), g.start);
  }

  function rhsStr(rhs) { return rhs.length ? rhs.join(' ') : EPS; }
  function prodStr(p) { return p.lhs + ' → ' + rhsStr(p.rhs); }

  function grammarText(g) {
    const lines = [];
    const seen = new Set();
    const order = [g.start].concat(g.nonterminals.filter(n => n !== g.start));
    order.forEach(n => {
      if (seen.has(n)) return; seen.add(n);
      const ps = g.byLhs.get(n) || [];
      if (!ps.length) return;
      lines.push(n + ' → ' + ps.map(p => rhsStr(p.rhs)).join(' | '));
    });
    return lines.join('\n');
  }

  /* ---------- FIRST ---------- */
  function computeFirst(g) {
    const F = new Map();
    g.nonterminals.forEach(n => F.set(n, new Set()));
    const trace = [];
    let changed = true, round = 0;
    while (changed) {
      changed = false; round++;
      const snap = [];
      g.prods.forEach(p => {
        const set = F.get(p.lhs);
        const before = set.size;
        if (p.rhs.length === 0) { set.add(EPS); }
        else {
          let allNullable = true;
          for (const s of p.rhs) {
            if (!g.isNT(s)) { set.add(s); allNullable = false; break; }
            const fs = F.get(s);
            fs.forEach(x => { if (x !== EPS) set.add(x); });
            if (!fs.has(EPS)) { allNullable = false; break; }
          }
          if (allNullable) set.add(EPS);
        }
        if (set.size !== before) { changed = true; snap.push({ nt: p.lhs, prod: prodStr(p), set: [...set] }); }
      });
      if (snap.length) trace.push({ round: round, changes: snap });
      if (round > 200) break;
    }
    return { first: F, trace: trace };
  }

  function firstOfSeq(g, F, seq) {
    const out = new Set();
    let nullable = true;
    for (const s of seq) {
      if (!g.isNT(s)) { out.add(s); nullable = false; break; }
      const fs = F.get(s);
      fs.forEach(x => { if (x !== EPS) out.add(x); });
      if (!fs.has(EPS)) { nullable = false; break; }
    }
    if (nullable) out.add(EPS);
    return out;
  }

  /* ---------- FOLLOW ---------- */
  function computeFollow(g, F) {
    const FL = new Map();
    g.nonterminals.forEach(n => FL.set(n, new Set()));
    FL.get(g.start).add(END);
    const trace = [];
    let changed = true, round = 0;
    while (changed) {
      changed = false; round++;
      const snap = [];
      g.prods.forEach(p => {
        for (let i = 0; i < p.rhs.length; i++) {
          const B = p.rhs[i];
          if (!g.isNT(B)) continue;
          const beta = p.rhs.slice(i + 1);
          const set = FL.get(B);
          const before = set.size;
          const fb = firstOfSeq(g, F, beta);
          fb.forEach(x => { if (x !== EPS) set.add(x); });
          if (fb.has(EPS) || beta.length === 0) FL.get(p.lhs).forEach(x => set.add(x));
          if (set.size !== before) {
            changed = true;
            snap.push({
              nt: B, prod: prodStr(p), set: [...set],
              reason: (beta.length ? 'FIRST(' + rhsStr(beta) + ')' : 'FOLLOW(' + p.lhs + ')') +
                ((fb.has(EPS) && beta.length) ? ' and FOLLOW(' + p.lhs + ') because β is nullable' : '')
            });
          }
        }
      });
      if (snap.length) trace.push({ round: round, changes: snap });
      if (round > 200) break;
    }
    return { follow: FL, trace: trace };
  }

  function analyse(g) {
    const f = computeFirst(g);
    const fl = computeFollow(g, f.first);
    return { first: f.first, firstTrace: f.trace, follow: fl.follow, followTrace: fl.trace };
  }

  /* ---------- LL(1) table ---------- */
  function ll1Table(g) {
    const a = analyse(g);
    const terms = g.terminals.filter(t => t !== EPS).concat([END]);
    const table = new Map();
    g.nonterminals.forEach(n => table.set(n, new Map()));
    const rows = [];
    g.prods.forEach(p => {
      const fa = firstOfSeq(g, a.first, p.rhs);
      const cols = [];
      fa.forEach(x => { if (x !== EPS) cols.push(x); });
      if (fa.has(EPS)) a.follow.get(p.lhs).forEach(x => cols.push(x));
      const uniq = [...new Set(cols)];
      uniq.forEach(t => {
        const m = table.get(p.lhs);
        if (!m.has(t)) m.set(t, []);
        m.get(t).push(p);
      });
      rows.push({ prod: p, first: [...fa], cols: uniq });
    });
    const conflicts = [];
    table.forEach((m, nt) => m.forEach((ps, t) => { if (ps.length > 1) conflicts.push({ nt: nt, term: t, prods: ps }); }));
    return {
      table: table, terminals: terms, first: a.first, follow: a.follow,
      firstTrace: a.firstTrace, followTrace: a.followTrace,
      conflicts: conflicts, isLL1: conflicts.length === 0, rows: rows
    };
  }

  /* ---------- LL(1) parse simulation (top-down, with parse tree) ---------- */
  let NODE_ID = 0;
  function node(sym, kind) { return { id: ++NODE_ID, sym: sym, kind: kind, children: [], x: 0, y: 0 }; }

  function ll1Parse(g, tbl, tokens) {
    const input = tokens.concat([END]);
    const root = node(g.start, 'nt');
    const stack = [{ sym: END, node: null }, { sym: g.start, node: root }];
    const steps = [];
    let ip = 0, guard = 0, ok = true, err = null;

    const snapshot = (action, cls, extra) => {
      steps.push({
        stack: stack.map(e => e.sym),
        input: input.slice(ip),
        matched: input.slice(0, ip),
        action: action, cls: cls || '',
        prod: (extra && extra.prod) || null,
        expand: (extra && extra.expand) || null,
        pos: ip
      });
    };

    snapshot('Initialise: push $ and start symbol ' + g.start, 'init');

    const LIMIT = 1200;
    let expandsWithoutConsuming = 0;
    while (stack.length && guard++ < LIMIT) {
      const top = stack[stack.length - 1];
      const look = input[ip];
      if (top.sym === END && look === END) { snapshot('Stack top = $ and lookahead = $  →  ACCEPT', 'accept'); break; }

      if (!g.isNT(top.sym)) {
        if (top.sym === look) {
          stack.pop(); ip++; expandsWithoutConsuming = 0;
          snapshot('Match terminal ' + top.sym + '  →  pop it and advance the input pointer', 'match');
        } else {
          ok = false; err = 'Syntax error: stack top is terminal "' + top.sym + '" but lookahead is "' + look + '".';
          snapshot(err, 'error'); break;
        }
      } else {
        const m = tbl.table.get(top.sym);
        const cell = m && m.get(look);
        if (!cell || !cell.length) {
          ok = false; err = 'Syntax error: table cell M[' + top.sym + ', ' + look + '] is empty.';
          snapshot(err, 'error'); break;
        }
        const p = cell[0];
        stack.pop();
        const kids = p.rhs.length ? p.rhs.map(s => node(s, g.isNT(s) ? 'nt' : 't')) : [node(EPS, 'eps')];
        top.node.children = kids;
        if (p.rhs.length) {
          for (let i = p.rhs.length - 1; i >= 0; i--) stack.push({ sym: p.rhs[i], node: kids[i] });
        }
        if (++expandsWithoutConsuming > 250) {
          ok = false;
          err = 'Aborted: the parser expanded 250 times without consuming a token. ' +
                'This almost always means the grammar is LEFT RECURSIVE — remove the left recursion first.';
          snapshot(err, 'error'); break;
        }
        snapshot('M[' + top.sym + ', ' + look + '] = ' + prodStr(p) + '  →  pop ' + top.sym +
          (p.rhs.length ? ', push ' + p.rhs.slice().reverse().join(' ') + ' (reversed)' : ' (nothing pushed, ε)'),
          'expand', { prod: p, expand: top.sym });
      }
    }
    if (guard >= LIMIT) { ok = false; err = 'Aborted: step limit reached — the grammar appears to loop (check for left recursion).'; }
    return { ok: ok && !err, error: err, steps: steps, tree: root };
  }

  /* ---------- Left recursion ---------- */
  function hasLeftRecursion(g) {
    const direct = [], indirect = [];
    g.nonterminals.forEach(A => {
      (g.byLhs.get(A) || []).forEach(p => { if (p.rhs.length && p.rhs[0] === A) direct.push(p); });
    });
    /* indirect: reachability of A =>+ A alpha through leading nonterminals */
    const F = computeFirst(g).first;
    const nullable = s => g.isNT(s) && F.get(s).has(EPS);
    const edges = new Map();
    g.nonterminals.forEach(A => edges.set(A, new Set()));
    g.prods.forEach(p => {
      for (const s of p.rhs) {
        if (!g.isNT(s)) break;
        edges.get(p.lhs).add(s);
        if (!nullable(s)) break;
      }
    });
    g.nonterminals.forEach(A => {
      const seen = new Set(); const st = [...edges.get(A)];
      while (st.length) { const x = st.pop(); if (seen.has(x)) continue; seen.add(x); (edges.get(x) || []).forEach(y => st.push(y)); }
      if (seen.has(A) && !direct.some(p => p.lhs === A)) indirect.push(A);
      else if (seen.has(A) && direct.some(p => p.lhs === A)) { /* both */ }
    });
    return { direct: direct, indirect: indirect, any: direct.length > 0 || indirect.length > 0 };
  }

  function primeName(base, used) {
    let n = base + "'";
    while (used.has(n)) n += "'";
    used.add(n); return n;
  }

  /* Paull's algorithm + immediate elimination, with a readable log. */
  function removeLeftRecursion(g) {
    const log = [];
    const A = g.nonterminals.slice();
    const used = new Set(A);
    let prods = g.prods.map(p => ({ lhs: p.lhs, rhs: p.rhs.slice() }));
    const newNTs = [];

    const get = L => prods.filter(p => p.lhs === L);
    const setFor = (L, list) => { prods = prods.filter(p => p.lhs !== L).concat(list); };

    log.push({ type: 'head', text: 'Order the non-terminals: ' + A.join(', ') });

    for (let i = 0; i < A.length; i++) {
      const Ai = A[i];
      for (let j = 0; j < i; j++) {
        const Aj = A[j];
        const cur = get(Ai);
        const hits = cur.filter(p => p.rhs.length && p.rhs[0] === Aj);
        if (!hits.length) continue;
        const repl = [];
        cur.forEach(p => {
          if (p.rhs.length && p.rhs[0] === Aj) {
            get(Aj).forEach(q => repl.push({ lhs: Ai, rhs: q.rhs.concat(p.rhs.slice(1)) }));
          } else repl.push(p);
        });
        /* de-dup */
        const seen = new Set(); const ded = [];
        repl.forEach(p => { const k = rhsStr(p.rhs); if (!seen.has(k)) { seen.add(k); ded.push(p); } });
        setFor(Ai, ded);
        log.push({
          type: 'sub',
          text: 'Substitute ' + Aj + ' inside ' + Ai + ' (removes the indirect cycle ' + Ai + ' ⇒ ' + Aj + ' … ⇒ ' + Ai + ')',
          detail: Ai + ' → ' + ded.map(p => rhsStr(p.rhs)).join(' | ')
        });
      }

      /* immediate elimination for Ai */
      const cur = get(Ai);
      const alpha = [], beta = [];
      cur.forEach(p => {
        if (p.rhs.length && p.rhs[0] === Ai) { if (p.rhs.length > 1) alpha.push(p.rhs.slice(1)); /* A→A dropped */ }
        else beta.push(p.rhs.slice());
      });
      if (!alpha.length) {
        log.push({ type: 'ok', text: 'No left recursion on ' + Ai + ' — nothing to do.' });
        continue;
      }
      if (!beta.length) {
        log.push({ type: 'warn', text: Ai + ' has only left-recursive productions — it can never derive a string. Grammar is faulty.' });
        continue;
      }
      const Ap = primeName(Ai, used);
      newNTs.push(Ap);
      const nb = beta.map(b => ({ lhs: Ai, rhs: b.concat([Ap]) }));
      const na = alpha.map(a => ({ lhs: Ap, rhs: a.concat([Ap]) }));
      na.push({ lhs: Ap, rhs: [] });
      setFor(Ai, nb);
      prods = prods.concat(na);
      log.push({
        type: 'elim',
        text: 'Eliminate immediate left recursion on ' + Ai,
        alpha: alpha.map(rhsStr), beta: beta.map(rhsStr), nt: Ai, prime: Ap,
        detail: Ai + ' → ' + nb.map(p => rhsStr(p.rhs)).join(' | ') + '\n' + Ap + ' → ' + na.map(p => rhsStr(p.rhs)).join(' | ')
      });
    }

    /* rebuild ordered grammar: original order, primes right after their base */
    const order = [];
    A.forEach(n => {
      order.push(n);
      newNTs.filter(p => p.replace(/'+$/, '') === n).forEach(p => order.push(p));
    });
    newNTs.forEach(p => { if (!order.includes(p)) order.push(p); });
    const ordered = [];
    order.forEach(n => prods.filter(p => p.lhs === n).forEach(p => ordered.push(p)));
    prods.forEach(p => { if (!order.includes(p.lhs)) ordered.push(p); });

    const nts = order.filter(n => ordered.some(p => p.lhs === n));
    const tSeen = new Set(), terms = [];
    ordered.forEach(p => p.rhs.forEach(s => { if (!nts.includes(s) && !tSeen.has(s)) { tSeen.add(s); terms.push(s); } }));
    return { grammar: makeGrammar(nts, terms, ordered, g.start), log: log };
  }

  /* ---------- Left factoring ---------- */
  function longestCommonPrefix(list) {
    if (list.length < 2) return [];
    let p = list[0].slice();
    for (let i = 1; i < list.length; i++) {
      const q = list[i]; let k = 0;
      while (k < p.length && k < q.length && p[k] === q[k]) k++;
      p = p.slice(0, k);
      if (!p.length) break;
    }
    return p;
  }

  function leftFactor(g) {
    const log = [];
    const used = new Set(g.nonterminals);
    let prods = g.prods.map(p => ({ lhs: p.lhs, rhs: p.rhs.slice() }));
    const order = g.nonterminals.slice();
    let guard = 0, changed = true;

    while (changed && guard++ < 100) {
      changed = false;
      for (const L of order.slice()) {
        const cur = prods.filter(p => p.lhs === L);
        if (cur.length < 2) continue;
        /* best prefix = longest prefix shared by >= 2 alternatives */
        let best = [], group = [];
        for (let i = 0; i < cur.length; i++) {
          for (let len = cur[i].rhs.length; len > 0; len--) {
            const pre = cur[i].rhs.slice(0, len);
            const grp = cur.filter(p => p.rhs.length >= len && pre.every((s, k) => p.rhs[k] === s));
            if (grp.length > 1 && len > best.length) { best = pre; group = grp; }
          }
        }
        if (!best.length) continue;
        const Lp = primeName(L, used);
        order.splice(order.indexOf(L) + 1, 0, Lp);
        const rest = prods.filter(p => p.lhs === L && !group.includes(p));
        const newL = rest.concat([{ lhs: L, rhs: best.concat([Lp]) }]);
        const newLp = group.map(p => ({ lhs: Lp, rhs: p.rhs.slice(best.length) }));
        prods = prods.filter(p => p.lhs !== L).concat(newL, newLp);
        log.push({
          type: 'factor', nt: L, prime: Lp, prefix: rhsStr(best),
          text: 'Common prefix "' + rhsStr(best) + '" found in ' + L,
          detail: L + ' → ' + newL.map(p => rhsStr(p.rhs)).join(' | ') + '\n' + Lp + ' → ' + newLp.map(p => rhsStr(p.rhs)).join(' | ')
        });
        changed = true;
      }
    }
    if (!log.length) log.push({ type: 'ok', text: 'No two alternatives of any non-terminal share a common prefix — the grammar is already left factored.' });

    const ordered = [];
    order.forEach(n => prods.filter(p => p.lhs === n).forEach(p => ordered.push(p)));
    const nts = order.filter(n => ordered.some(p => p.lhs === n));
    const tSeen = new Set(), terms = [];
    ordered.forEach(p => p.rhs.forEach(s => { if (!nts.includes(s) && !tSeen.has(s)) { tSeen.add(s); terms.push(s); } }));
    return { grammar: makeGrammar(nts, terms, ordered, g.start), log: log };
  }

  /* ---------- Operator grammar ---------- */
  function isOperatorGrammar(g) {
    const bad = [];
    g.prods.forEach(p => {
      if (p.rhs.length === 0) bad.push({ prod: prodStr(p), why: 'ε-production is not allowed in an operator grammar' });
      for (let i = 0; i + 1 < p.rhs.length; i++) {
        if (g.isNT(p.rhs[i]) && g.isNT(p.rhs[i + 1]))
          bad.push({ prod: prodStr(p), why: 'two adjacent non-terminals "' + p.rhs[i] + ' ' + p.rhs[i + 1] + '"' });
      }
    });
    return { ok: bad.length === 0, problems: bad };
  }

  /* substitute single-symbol "operator holder" nonterminals to fix adjacency */
  function toOperatorGrammar(g) {
    const log = [];
    let prods = g.prods.map(p => ({ lhs: p.lhs, rhs: p.rhs.slice() }));
    let nts = g.nonterminals.slice();
    let guard = 0;

    while (guard++ < 50) {
      const chk = isOperatorGrammar(makeGrammar(nts, [], prods, g.start));
      if (chk.ok) break;
      /* find an NT whose every production is a single terminal -> inline it */
      let victim = null;
      for (const n of nts) {
        if (n === g.start) continue;
        const ps = prods.filter(p => p.lhs === n);
        if (ps.length && ps.every(p => p.rhs.length === 1 && !nts.includes(p.rhs[0]))) {
          const usedAdj = prods.some(p => p.rhs.some((s, i) =>
            s === n && ((i > 0 && nts.includes(p.rhs[i - 1])) || (i + 1 < p.rhs.length && nts.includes(p.rhs[i + 1])))));
          if (usedAdj) { victim = n; break; }
        }
      }
      if (!victim) break;
      const repl = prods.filter(p => p.lhs === victim).map(p => p.rhs[0]);
      const out = [];
      prods.filter(p => p.lhs !== victim).forEach(p => {
        const idx = p.rhs.indexOf(victim);
        if (idx < 0) { out.push(p); return; }
        repl.forEach(r => {
          const nr = p.rhs.slice(); nr[idx] = r; out.push({ lhs: p.lhs, rhs: nr });
        });
      });
      const seen = new Set(); prods = [];
      out.forEach(p => { const k = p.lhs + '§' + rhsStr(p.rhs); if (!seen.has(k)) { seen.add(k); prods.push(p); } });
      nts = nts.filter(n => n !== victim);
      log.push({
        type: 'inline', nt: victim, with: repl,
        text: 'Every production of ' + victim + ' is a single terminal (' + repl.join(', ') +
          '). Substitute it back into the right-hand sides so no two non-terminals stay adjacent.'
      });
      guard++;
    }
    const tSeen = new Set(), terms = [];
    prods.forEach(p => p.rhs.forEach(s => { if (!nts.includes(s) && !tSeen.has(s)) { tSeen.add(s); terms.push(s); } }));
    const ng = makeGrammar(nts, terms, prods, g.start);
    return { grammar: ng, log: log, check: isOperatorGrammar(ng) };
  }

  /* ---------- Operator precedence table from precedence levels ---------- */
  /* levels: [{ops:['*','/'], assoc:'left'}, ...]  lowest first */
  function precedenceTable(levels, atoms) {
    const ops = [];
    levels.forEach((l, i) => l.ops.forEach(o => ops.push({ op: o, prec: i + 1, assoc: l.assoc || 'left' })));
    const cols = ops.map(o => o.op).concat(atoms, [END]);
    const rowsOrder = cols.slice();
    const T = new Map();
    const setc = (a, b, v) => { if (!T.has(a)) T.set(a, new Map()); T.get(a).set(b, v); };
    const info = o => ops.find(x => x.op === o);

    rowsOrder.forEach(a => rowsOrder.forEach(b => {
      let v = '';
      const ia = info(a), ib = info(b);
      const aAtom = atoms.includes(a), bAtom = atoms.includes(b);
      if (a === END && b === END) v = 'accept';
      else if (a === END) v = '⋖';
      else if (b === END) v = '⋗';
      else if (aAtom && bAtom) v = '';               /* id id : error */
      else if (aAtom) v = '⋗';                       /* id op  : reduce */
      else if (bAtom) v = '⋖';                       /* op id  : shift  */
      else if (ia && ib) {
        if (ia.prec > ib.prec) v = '⋗';
        else if (ia.prec < ib.prec) v = '⋖';
        else v = (ia.assoc === 'left') ? '⋗' : '⋖';
      }
      setc(a, b, v);
    }));
    return { table: T, symbols: rowsOrder, ops: ops, atoms: atoms };
  }

  /* ---------- Operator precedence parsing simulation ---------- */
  function opPrecParse(pt, tokens) {
    const input = tokens.concat([END]);
    const stack = [END];
    const steps = [];
    let ip = 0, guard = 0, ok = true, err = null;
    const rel = (a, b) => { const m = pt.table.get(a); return m ? (m.get(b) || '') : ''; };
    const topTerm = () => { for (let i = stack.length - 1; i >= 0; i--) if (pt.symbols.includes(stack[i])) return { s: stack[i], i: i }; return null; };

    const snap = (action, cls) => steps.push({
      stack: stack.slice(), input: input.slice(ip), action: action, cls: cls || '', pos: ip
    });

    snap('Initialise: stack holds $, the whole input is ahead.', 'init');
    while (guard++ < 2000) {
      const t = topTerm();
      const a = t ? t.s : END, b = input[ip];
      if (a === END && b === END) { snap('$ … $  →  ACCEPT', 'accept'); break; }
      const r = rel(a, b);
      if (r === '⋖' || r === '≐' || r === '') {
        if (r === '') { ok = false; err = 'No precedence relation between "' + a + '" and "' + b + '" — syntax error.'; snap(err, 'error'); break; }
        stack.push(r);
        stack.push(b); ip++;
        snap(a + ' ' + r + ' ' + b + '  →  SHIFT ' + b, 'shift');
      } else {
        /* reduce: pop until  ⋖  is found */
        let popped = [];
        let i = stack.length - 1;
        while (i >= 0) {
          if (stack[i] === '⋖') break;
          popped.unshift(stack[i]); i--;
        }
        if (i < 0) { ok = false; err = 'Reduce failed: no ⋖ on the stack.'; snap(err, 'error'); break; }
        const handle = popped.filter(x => x !== '⋗' && x !== '≐');
        stack.length = i;                 /* drop the ⋖ too */
        stack.push('N');
        snap(a + ' ⋗ ' + b + '  →  REDUCE handle « ' + handle.join(' ') + ' » to N', 'reduce');
      }
    }
    return { ok: ok && !err, error: err, steps: steps };
  }

  /* ============================================================
     SLR(1)  —  proper bottom-up parsing
     Augment, build LR(0) canonical collection, then an
     ACTION/GOTO table whose reductions are guarded by FOLLOW.
     ============================================================ */
  function augment(g) {
    const S2 = (function () { let n = g.start + "'"; const used = new Set(g.nonterminals); while (used.has(n)) n += "'"; return n; })();
    const prods = [{ lhs: S2, rhs: [g.start] }].concat(g.prods.map(p => ({ lhs: p.lhs, rhs: p.rhs.slice() })));
    const nts = [S2].concat(g.nonterminals);
    const terms = g.terminals.slice();
    const ag = makeGrammar(nts, terms, prods, S2);
    ag.origStart = g.start;
    return ag;
  }

  const itemKey = it => it.p + '.' + it.d;
  function closure(g, items) {
    const out = items.slice();
    const seen = new Set(out.map(itemKey));
    let changed = true;
    while (changed) {
      changed = false;
      for (let i = 0; i < out.length; i++) {
        const it = out[i];
        const p = g.prods[it.p];
        const B = p.rhs[it.d];
        if (!B || !g.isNT(B)) continue;
        (g.byLhs.get(B) || []).forEach(q => {
          const ni = { p: q.id, d: 0 };
          if (!seen.has(itemKey(ni))) { seen.add(itemKey(ni)); out.push(ni); changed = true; }
        });
      }
    }
    out.sort((a, b) => a.p - b.p || a.d - b.d);
    return out;
  }
  function goto_(g, items, X) {
    const moved = items.filter(it => g.prods[it.p].rhs[it.d] === X).map(it => ({ p: it.p, d: it.d + 1 }));
    return moved.length ? closure(g, moved) : [];
  }
  const stateKey = its => its.map(itemKey).join(',');

  function lr0Collection(g) {
    const start = closure(g, [{ p: 0, d: 0 }]);
    const states = [start];
    const index = new Map([[stateKey(start), 0]]);
    const trans = [];                       /* [{from,sym,to}] */
    const symbols = g.nonterminals.concat(g.terminals);
    for (let i = 0; i < states.length; i++) {
      symbols.forEach(X => {
        const t = goto_(g, states[i], X);
        if (!t.length) return;
        const k = stateKey(t);
        let j = index.get(k);
        if (j === undefined) { j = states.length; states.push(t); index.set(k, j); }
        trans.push({ from: i, sym: X, to: j });
      });
    }
    return { states: states, trans: trans, index: index };
  }

  function itemStr(g, it) {
    const p = g.prods[it.p];
    const r = p.rhs.slice();
    r.splice(it.d, 0, '•');
    return p.lhs + ' → ' + (r.length ? r.join(' ') : '•');
  }

  function slr1Table(gRaw) {
    const g = augment(gRaw);
    const a = analyse(g);                    /* FIRST/FOLLOW on the augmented grammar */
    const col = lr0Collection(g);
    const terms = g.terminals.filter(t => t !== EPS).concat([END]);
    const ACTION = [], GOTO = [];
    for (let i = 0; i < col.states.length; i++) { ACTION.push(new Map()); GOTO.push(new Map()); }
    const conflicts = [];

    const put = (i, t, act) => {
      const m = ACTION[i];
      const cur = m.get(t);
      if (cur && (cur.type !== act.type || cur.n !== act.n)) {
        const kind = (cur.type === 'shift' || act.type === 'shift') ? 'shift-reduce' : 'reduce-reduce';
        conflicts.push({ state: i, term: t, a: cur, b: act, kind: kind });
        /* resolve like yacc: shift wins; otherwise lower production number wins */
        if (kind === 'shift-reduce') { if (cur.type === 'reduce') m.set(t, act.type === 'shift' ? act : cur); }
        else if (act.n < cur.n) m.set(t, act);
        return;
      }
      m.set(t, act);
    };

    col.trans.forEach(tr => {
      if (g.isNT(tr.sym)) GOTO[tr.from].set(tr.sym, tr.to);
      else put(tr.from, tr.sym, { type: 'shift', n: tr.to });
    });
    col.states.forEach((its, i) => {
      its.forEach(it => {
        const p = g.prods[it.p];
        if (it.d < p.rhs.length) return;     /* not a complete item */
        if (it.p === 0) { put(i, END, { type: 'accept' }); return; }
        (a.follow.get(p.lhs) || new Set()).forEach(t => put(i, t, { type: 'reduce', n: it.p }));
      });
    });

    return {
      grammar: g, states: col.states, trans: col.trans, ACTION: ACTION, GOTO: GOTO,
      terminals: terms, nonterminals: g.nonterminals.filter(n => n !== g.start),
      first: a.first, follow: a.follow, conflicts: conflicts, isSLR1: conflicts.length === 0,
      itemStr: it => itemStr(g, it)
    };
  }

  function slr1Parse(T, tokens) {
    const g = T.grammar;
    const input = tokens.concat([END]);
    const stStack = [0], symStack = [];
    const forest = [];
    const steps = [];
    let ip = 0, guard = 0, ok = false, err = null;

    const snap = (action, cls) => steps.push({
      states: stStack.slice(), stack: symStack.slice(), input: input.slice(ip),
      action: action, cls: cls || '', pos: ip
    });
    snap('Initialise: state 0 on the stack, full input ahead.', 'init');

    while (guard++ < 3000) {
      const s = stStack[stStack.length - 1], la = input[ip];
      const act = T.ACTION[s].get(la);
      if (!act) {
        err = 'Syntax error: no ACTION entry for state ' + s + ' on lookahead "' + la + '".';
        snap(err, 'error'); break;
      }
      if (act.type === 'shift') {
        stStack.push(act.n); symStack.push(la);
        forest.push(node(la, 't')); ip++;
        snap('ACTION[' + s + ', ' + la + '] = shift ' + act.n + '  →  push ' + la + ' and go to state ' + act.n, 'shift');
      } else if (act.type === 'reduce') {
        const p = g.prods[act.n];
        const len = p.rhs.length;
        const kids = forest.splice(forest.length - len, len);
        for (let i = 0; i < len; i++) { stStack.pop(); symStack.pop(); }
        const n = node(p.lhs, 'nt');
        n.children = kids.length ? kids : [node(EPS, 'eps')];
        forest.push(n);
        const t = stStack[stStack.length - 1];
        const gt = T.GOTO[t].get(p.lhs);
        if (gt === undefined) { err = 'No GOTO for state ' + t + ' on ' + p.lhs; snap(err, 'error'); break; }
        stStack.push(gt); symStack.push(p.lhs);
        snap('ACTION[' + s + ', ' + la + '] = reduce ' + act.n + '  →  pop ' + len +
          ' symbol(s) « ' + (p.rhs.length ? p.rhs.join(' ') : 'ε') + ' », push ' + p.lhs +
          ', GOTO[' + t + ', ' + p.lhs + '] = ' + gt, 'reduce');
      } else if (act.type === 'accept') {
        ok = true;
        snap('ACTION[' + s + ', $] = accept  →  the input is a valid sentence.', 'accept');
        break;
      }
    }
    return { ok: ok, error: err, steps: steps, tree: ok ? forest[forest.length - 1] : null };
  }

  /* ---------- Shift-reduce (bottom-up) with LR-free heuristic ---------- */
  function shiftReduceParse(g, tokens, maxSteps) {
    const input = tokens.concat([END]);
    const stack = [];
    const steps = [];
    const forest = [];
    let ip = 0, guard = 0;
    const snap = (action, cls) => steps.push({
      stack: stack.slice(), input: input.slice(ip), action: action, cls: cls || ''
    });
    snap('Start: empty stack, full input.', 'init');
    while (guard++ < (maxSteps || 400)) {
      /* try longest reduction at the stack top that keeps a parse alive */
      let done = false;
      for (let len = Math.min(stack.length, 6); len >= 0 && !done; len--) {
        const top = stack.slice(stack.length - len);
        const cand = g.prods.filter(p => p.rhs.length === len && p.rhs.every((s, i) => s === top[i]));
        if (!cand.length) continue;
        const p = cand[0];
        if (stack.length === len && p.lhs === g.start && input[ip] === END) {
          for (let i = 0; i < len; i++) stack.pop();
          const n = node(p.lhs, 'nt'); n.children = forest.splice(forest.length - len, len);
          if (!n.children.length) n.children = [node(EPS, 'eps')];
          stack.push(p.lhs); forest.push(n);
          snap('REDUCE by ' + prodStr(p), 'reduce');
          snap('Stack = start symbol, input exhausted  →  ACCEPT', 'accept');
          return { ok: true, steps: steps, tree: forest[0] };
        }
        if (len === 0) continue;
        for (let i = 0; i < len; i++) stack.pop();
        const n = node(p.lhs, 'nt'); n.children = forest.splice(forest.length - len, len);
        stack.push(p.lhs); forest.push(n);
        snap('REDUCE by ' + prodStr(p), 'reduce');
        done = true;
      }
      if (done) continue;
      if (input[ip] === END) { snap('Cannot reduce further and input is finished — parse failed.', 'error'); return { ok: false, steps: steps, tree: null }; }
      stack.push(input[ip]); forest.push(node(input[ip], 't'));
      snap('SHIFT ' + input[ip], 'shift'); ip++;
    }
    snap('Step limit reached.', 'error');
    return { ok: false, steps: steps, tree: null };
  }

  /* ---------- leftmost / rightmost derivation from a parse tree ---------- */
  function derivation(tree, leftmost) {
    const steps = [];
    let sent = [tree];
    const render = arr => arr.map(n => n.sym).join(' ') || EPS;
    steps.push(render(sent));
    let guard = 0;
    while (guard++ < 500) {
      let idx = -1;
      if (leftmost) { for (let i = 0; i < sent.length; i++) if (sent[i].children.length) { idx = i; break; } }
      else { for (let i = sent.length - 1; i >= 0; i--) if (sent[i].children.length) { idx = i; break; } }
      if (idx < 0) break;
      const n = sent[idx];
      const kids = n.children.filter(c => c.kind !== 'eps');
      sent = sent.slice(0, idx).concat(kids, sent.slice(idx + 1));
      steps.push(render(sent));
    }
    return steps;
  }

  /* ---------- tidy tree layout ---------- */
  function layoutTree(root, opt) {
    opt = opt || {};
    const dx = opt.dx || 74, dy = opt.dy || 86;

    /* iterative post-order so very deep trees cannot blow the JS stack */
    const order = [];
    const st = [[root, 0, false]];
    while (st.length) {
      const fr = st.pop();
      const n = fr[0], d = fr[1], visited = fr[2];
      if (visited) { order.push(n); continue; }
      n.depth = d;
      st.push([n, d, true]);
      for (let i = n.children.length - 1; i >= 0; i--) st.push([n.children[i], d + 1, false]);
    }

    let leaf = 0;
    order.forEach(n => {
      if (!n.children.length) { n.x = leaf++ * dx; n.y = n.depth * dy; }
      else {
        const f = n.children[0], l = n.children[n.children.length - 1];
        n.x = (f.x + l.x) / 2; n.y = n.depth * dy;
      }
    });

    let maxX = 0, maxY = 0;
    order.forEach(n => { if (n.x > maxX) maxX = n.x; if (n.y > maxY) maxY = n.y; });
    /* return nodes in pre-order for stable rendering */
    const all = [];
    const st2 = [root];
    while (st2.length) {
      const n = st2.pop(); all.push(n);
      for (let i = n.children.length - 1; i >= 0; i--) st2.push(n.children[i]);
    }
    return { nodes: all, width: maxX + dx, height: maxY + dy, dx: dx, dy: dy };
  }

  global.PL = {
    EPS, END, tokenize, parseGrammar, makeGrammar, cloneGrammar, grammarText, prodStr, rhsStr,
    computeFirst, computeFollow, firstOfSeq, analyse, ll1Table, ll1Parse,
    hasLeftRecursion, removeLeftRecursion, leftFactor,
    isOperatorGrammar, toOperatorGrammar, precedenceTable, opPrecParse,
    shiftReduceParse, derivation, layoutTree,
    augment, closure, lr0Collection, slr1Table, slr1Parse, itemStr
  };
})(typeof window !== 'undefined' ? window : globalThis);
