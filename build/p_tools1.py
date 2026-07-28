# -*- coding: utf-8 -*-
"""Left recursion, left factoring, FIRST & FOLLOW pages."""
from shell import page, sec

E = '<span class="sym e">&epsilon;</span>'


def d(title, tag, body, variant=""):
    v = (" " + variant) if variant else ""
    return '<div class="def%s"><h4>%s <span class="tag">%s</span></h4>%s</div>' % (v, title, tag, body)


def hero(num, title, gradient, lead):
    return """
<section class="hero" style="padding:52px 0 26px">
  <div class="wrap">
    <span class="pill">Section %s</span>
    <h1>%s <span class="g">%s</span></h1>
    <p>%s</p>
  </div>
</section>""" % (num, title, gradient, lead)


def workbench(examples, extra_controls="", btn="Solve", placeholder=""):
    chips = "".join('<button class="chip" data-ex="%d">%s</button>' % (i, lbl)
                    for i, (lbl, _) in enumerate(examples))
    return """
<div class="card">
  <div class="split-wide">
    <div>
      <label class="lb">Grammar &mdash; one non-terminal per line</label>
      <textarea id="gin" spellcheck="false" placeholder="%s"></textarea>
      <p class="muted" style="margin:8px 0 0;font-size:.82rem">
        Use <code>-&gt;</code> or <code>&rarr;</code>. Separate alternatives with <code>|</code> or <code>/</code>.
        Empty string: <code>e</code>, <code>&epsilon;</code>, <code>&euro;</code> or <code>eps</code>.
        Capitals are non-terminals; <code>id</code> counts as one token.</p>
      %s
      <div class="btn-row">
        <button class="btn" id="run">%s</button>
        <button class="btn ghost" id="clear">Clear</button>
      </div>
      <label class="lb" style="margin-top:20px">Saved examples &mdash; click to load</label>
      <div class="chips">%s</div>
    </div>
    <div>
      <div id="msg"></div>
      <div id="out"><p class="muted center" style="padding:56px 20px">Load an example or type your own grammar,
      then press <b>%s</b>.<br>The full working appears here, step by step.</p></div>
    </div>
  </div>
</div>""" % (placeholder, extra_controls, btn, chips, btn)


# ============================================================
# LEFT RECURSION
# ============================================================
LR_EX = [
    ("A &rarr; Aa | b", "A -> Aa | b"),
    ("S/A indirect", "S -> Aa | b\nA -> Ac | Sd | \u03b5"),
    ("A &rarr; Ad|Ae|aB|aC", "S -> A\nA -> Ad | Ae | aB | aC\nB -> bBC | f\nC -> g"),
    ("A &rarr; Ax|Ay|AB|c|d", "A -> A x | A y | A B | c | d\nB -> e"),
    ("S &rarr; A; A &rarr; aB|Ad", "S -> A\nA -> aB / Ad\nB -> bBC / f\nC -> g"),
    ("Expression grammar", "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id"),
]


def left_recursion():
    theory = d("Left Recursion", "definition", """
<p>A grammar is <b>left recursive</b> if a non-terminal A can derive a sentential form whose leftmost symbol
is A itself: <code>A &rArr;<sup>+</sup> A&alpha;</code>.</p>
<p><b>Direct</b>: the production starts with A &mdash; <code>A &rarr; A&alpha;</code>.<br>
<b>Indirect</b>: it takes two or more steps &mdash; <code>A &rarr; B&beta;</code>, <code>B &rarr; A&gamma;</code>.</p>
<p>A recursive-descent parser for <code>A &rarr; A&alpha;</code> would call <code>A()</code> as its first action,
consuming nothing, and loop forever. So left recursion must be removed before any top-down parsing.</p>""", "v-bad") + \
        d("The elimination rule", "rule", """
<p>Group the productions of A into the ones that <b>start with A</b> and the ones that <b>do not</b>:</p>
<div class="gbox in"><div>A &rarr; A&alpha;<sub>1</sub> | A&alpha;<sub>2</sub> | &hellip; | A&alpha;<sub>m</sub>
&nbsp;|&nbsp; &beta;<sub>1</sub> | &beta;<sub>2</sub> | &hellip; | &beta;<sub>n</sub></div></div>
<p style="margin:14px 0 10px"><b>Replace</b> them with a right-recursive pair using a fresh non-terminal A&prime;:</p>
<div class="gbox out">
<div>A&nbsp; &rarr; &beta;<sub>1</sub>A&prime; | &beta;<sub>2</sub>A&prime; | &hellip; | &beta;<sub>n</sub>A&prime;</div>
<div>A&prime; &rarr; &alpha;<sub>1</sub>A&prime; | &alpha;<sub>2</sub>A&prime; | &hellip; | &alpha;<sub>m</sub>A&prime; | %s</div></div>
<p style="margin-top:14px"><b>In words:</b> A must now <i>start</i> with one of the &beta; strings (the only way it
could ever really start), and A&prime; repeats the &alpha; parts zero or more times before stopping with %s.</p>
<div class="note warn"><span class="ni">&#9888;</span><div>If there is no &beta; alternative at all, A can never
produce a terminal string &mdash; the grammar is faulty, not just left recursive.</div></div>""" % (E, E), "v-ok") + \
        d("Indirect left recursion &mdash; the substitution algorithm", "algorithm", """
<p>Order the non-terminals A<sub>1</sub>, A<sub>2</sub>, &hellip;, A<sub>n</sub>. Then:</p>
<pre style="background:var(--bg-2);padding:16px 20px;border-radius:10px;border:1px solid var(--line);font-family:var(--mono);font-size:.92rem;line-height:1.8;overflow-x:auto">for i = 1 to n:
    for j = 1 to i-1:
        replace every production  A&#7522; &rarr; A&#11388;&gamma;
        by       A&#7522; &rarr; &delta;&#8321;&gamma; | &delta;&#8322;&gamma; | ...   where A&#11388; &rarr; &delta;&#8321; | &delta;&#8322; | ...
    eliminate the immediate left recursion on A&#7522;</pre>
<p>The inner loop rewrites every "backward" reference so that any remaining recursion becomes direct,
and the last line then clears it with the rule above.</p>""", "v-a")

    body = hero("2", "Left Recursion", "Elimination",
                "Spot it, understand why it breaks a top-down parser, and remove it with the "
                "&alpha;/&beta; rule &mdash; every substitution shown.") + \
        sec("2.1", "Definition and rule", "Read this before running the tool.", theory, "def") + \
        sec("2.2", "Interactive workbench", "Load a saved question or paste your own grammar.",
            workbench(LR_EX, placeholder="A -> Aa | b"), "tool")

    js = """<script>
(function(){
  var $=UI.$, EX=%s;
  var gin=$('#gin'), out=$('#out'), msg=$('#msg');
  UI.$$('.chip[data-ex]').forEach(function(c){
    c.onclick=function(){
      UI.$$('.chip[data-ex]').forEach(function(x){x.classList.remove('on')});
      c.classList.add('on'); gin.value=EX[+c.dataset.ex]; run();
    };
  });
  $('#clear').onclick=function(){gin.value='';out.innerHTML='';msg.innerHTML='';};
  $('#run').onclick=run;
  gin.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&e.key==='Enter')run();});

  function run(){
    var g=UI.readGrammar(gin.value,msg); if(!g)return;
    var chk=PL.hasLeftRecursion(g);
    var res=PL.removeLeftRecursion(g);
    var h='';

    if(!chk.any){
      h+='<div class="banner ok"><span class="bi">&#10003;</span><div>No left recursion found'+
         '<small>No non-terminal can derive a form starting with itself. This grammar is already fit for top-down parsing.</small></div></div>';
    } else {
      var bits=[];
      if(chk.direct.length) bits.push('<b>Direct</b> on '+[...new Set(chk.direct.map(function(p){return p.lhs}))].join(', '));
      if(chk.indirect.length) bits.push('<b>Indirect</b> on '+chk.indirect.join(', '));
      h+='<div class="banner bad"><span class="bi">&#10007;</span><div>Left recursion detected<small>'+bits.join(' &nbsp;&middot;&nbsp; ')+'</small></div></div>';
    }

    h+='<div class="grid g2"><div><h4 style="color:var(--bad)">Input grammar</h4><div class="gbox in">'+UI.grammarHTML(g)+'</div></div>';
    h+='<div><h4 style="color:var(--ok)">Left-recursion-free grammar</h4><div class="gbox out">'+UI.grammarHTML(res.grammar)+'</div></div></div>';

    if(chk.any){
      h+='<h4 style="margin-top:26px">Step-by-step working</h4><div class="steps">';
      var n=0;
      res.log.forEach(function(l){
        if(l.type==='head'){ h+='<div class="step"><span class="n">&#9679;</span><div class="bd"><b>'+UI.esc(l.text)+'</b></div></div>'; return; }
        if(l.type==='ok'){ return; }
        n++;
        var cls=l.type==='warn'?'warn':(l.type==='sub'?'sub':'elim');
        h+='<div class="step '+cls+'"><span class="n">'+n+'</span><div class="bd"><b>'+UI.esc(l.text)+'</b>';
        if(l.type==='elim'){
          h+='<div class="kv" style="margin:6px 0 4px">';
          l.alpha.forEach(function(a,i){h+='<span>&alpha;'+(i+1)+' = '+UI.esc(a)+'</span>';});
          l.beta.forEach(function(b,i){h+='<span>&beta;'+(i+1)+' = '+UI.esc(b)+'</span>';});
          h+='</div><span class="muted">Apply A &rarr; &beta;A&prime;, &nbsp; A&prime; &rarr; &alpha;A&prime; | &epsilon; with A = '+UI.esc(l.nt)+', A&prime; = '+UI.esc(l.prime)+'</span>';
        }
        if(l.detail) h+='<pre>'+UI.esc(l.detail)+'</pre>';
        h+='</div></div>';
      });
      h+='</div>';
      h+='<div class="note tip" style="margin-top:20px"><span class="ni">&#128161;</span><div>'+
         'Notice the shape of the result: every new rule is <b>right</b> recursive, and each primed non-terminal ends with an '+
         '<span class="sym e">&epsilon;</span> alternative &mdash; that is what lets the repetition stop.</div></div>';
    }
    out.innerHTML=h;
  }
  UI.$$('.chip[data-ex]')[0].click();
})();
</script>""" % (repr([g for _, g in LR_EX]).replace("'", '"'),)

    return page("Left Recursion", "Eliminate direct and indirect left recursion step by step", body, js)


# ============================================================
# LEFT FACTORING
# ============================================================
LF_EX = [
    ("Dangling else", "S -> iCtSeS | iCtS | a\nC -> b"),
    ("A &rarr; ab | abc | abd", "A -> ab | abc | abd | e"),
    ("S &rarr; aAB | aBc | aAc", "S -> aAB | aBc | aAc\nA -> d\nB -> f"),
    ("Statement grammar", "S -> if E then S | if E then S else S | other\nE -> b"),
]


def left_factoring():
    theory = d("Left Factoring", "definition", """
<p><b>Left factoring</b> is a grammar transformation that removes the need to guess. If two or more
alternatives of the same non-terminal begin with the same string of symbols, a parser with one token
of lookahead cannot tell them apart.</p>
<div class="gbox in"><div>A &rarr; &alpha;&beta;<sub>1</sub> | &alpha;&beta;<sub>2</sub> | &gamma;</div></div>
<p style="margin:14px 0 10px">Pull the longest common prefix &alpha; out into its own production:</p>
<div class="gbox out"><div>A&nbsp; &rarr; &alpha;A&prime; | &gamma;</div>
<div>A&prime; &rarr; &beta;<sub>1</sub> | &beta;<sub>2</sub></div></div>
<p style="margin-top:14px">Now the parser consumes &alpha; first, and only <i>afterwards</i> has to choose between
&beta;<sub>1</sub> and &beta;<sub>2</sub> &mdash; by which time the deciding token is the lookahead.
Repeat until no two alternatives of any non-terminal share a prefix.</p>""", "v-a") + \
        d("Where you meet it", "note", """
<p>The famous case is the <b>dangling else</b>: <code>S &rarr; iCtSeS | iCtS | a</code>. Both alternatives start
with <code>iCtS</code>, so the grammar is not LL(1) as written.</p>
<div class="note warn"><span class="ni">&#9888;</span><div>Left factoring is <b>necessary but not sufficient</b>.
After factoring the dangling-else grammar you get <code>S&prime; &rarr; eS | &epsilon;</code>, and because
<code>e</code> is in both FIRST(eS) and FOLLOW(S&prime;), the table <i>still</i> has a conflict.
The grammar is genuinely ambiguous &mdash; factoring cannot fix ambiguity.</div></div>""", "v-bad")

    body = hero("3", "Left", "Factoring",
                "Remove common prefixes so a predictive parser can decide with a single lookahead token.") + \
        sec("3.1", "Definition and rule", "", theory, "def") + \
        sec("3.2", "Interactive workbench", "Watch each prefix get pulled out.",
            workbench(LF_EX, btn="Left factor", placeholder="A -> ab | abc | abd"), "tool")

    js = """<script>
(function(){
  var $=UI.$, EX=%s;
  var gin=$('#gin'), out=$('#out'), msg=$('#msg');
  UI.$$('.chip[data-ex]').forEach(function(c){
    c.onclick=function(){UI.$$('.chip[data-ex]').forEach(function(x){x.classList.remove('on')});
      c.classList.add('on'); gin.value=EX[+c.dataset.ex]; run();};
  });
  $('#clear').onclick=function(){gin.value='';out.innerHTML='';msg.innerHTML='';};
  $('#run').onclick=run;
  gin.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&e.key==='Enter')run();});

  function run(){
    var g=UI.readGrammar(gin.value,msg); if(!g)return;
    var res=PL.leftFactor(g);
    var did=res.log.some(function(l){return l.type==='factor';});
    var h='';
    h+= did
      ? '<div class="banner warn"><span class="bi">&#9986;</span><div>Common prefixes found &mdash; grammar factored<small>'+res.log.filter(function(l){return l.type==="factor"}).length+' factoring step(s) applied.</small></div></div>'
      : '<div class="banner ok"><span class="bi">&#10003;</span><div>Already left factored<small>No two alternatives of any non-terminal share a common prefix.</small></div></div>';

    h+='<div class="grid g2"><div><h4 style="color:var(--bad)">Input grammar</h4><div class="gbox in">'+UI.grammarHTML(g)+'</div></div>';
    h+='<div><h4 style="color:var(--ok)">Left-factored grammar</h4><div class="gbox out">'+UI.grammarHTML(res.grammar)+'</div></div></div>';

    if(did){
      h+='<h4 style="margin-top:26px">Step-by-step working</h4><div class="steps">';
      var n=0;
      res.log.forEach(function(l){
        if(l.type!=='factor')return; n++;
        h+='<div class="step factor"><span class="n">'+n+'</span><div class="bd"><b>'+UI.esc(l.text)+'</b>'+
           '<span class="muted">Apply A &rarr; &alpha;A&prime;, &nbsp; A&prime; &rarr; &beta;&#8321; | &beta;&#8322; with &alpha; = <b>'+UI.esc(l.prefix)+
           '</b>, A = '+UI.esc(l.nt)+', A&prime; = '+UI.esc(l.prime)+'</span><pre>'+UI.esc(l.detail)+'</pre></div></div>';
      });
      h+='</div>';
    }

    /* LL(1) status before/after */
    var t1=PL.ll1Table(g), t2=PL.ll1Table(res.grammar);
    h+='<hr class="sep"><h4>Did it become LL(1)?</h4><div class="grid g2">'+
       '<div class="card" style="padding:18px"><b>Before factoring</b><br>'+
       (t1.isLL1?'<span style="color:var(--ok);font-weight:800">LL(1) &#10003;</span>':'<span style="color:var(--bad);font-weight:800">Not LL(1) &mdash; '+t1.conflicts.length+' conflict(s)</span>')+'</div>'+
       '<div class="card" style="padding:18px"><b>After factoring</b><br>'+
       (t2.isLL1?'<span style="color:var(--ok);font-weight:800">LL(1) &#10003;</span>':'<span style="color:var(--bad);font-weight:800">Still not LL(1) &mdash; '+t2.conflicts.length+' conflict(s)</span>')+'</div></div>';
    if(!t2.isLL1){
      h+='<div class="note bad" style="margin-top:16px"><span class="ni">&#9888;</span><div><b>Still conflicting.</b> ';
      h+=t2.conflicts.map(function(c){return 'M['+UI.esc(c.nt)+', '+UI.esc(c.term)+'] holds '+c.prods.length+' productions';}).join('<br>');
      h+='<br>Left factoring removes <i>prefix</i> ambiguity only. A grammar that is genuinely ambiguous (like dangling-else) stays non-LL(1).</div></div>';
    }
    out.innerHTML=h;
  }
  UI.$$('.chip[data-ex]')[0].click();
})();
</script>""" % (repr([g for _, g in LF_EX]).replace("'", '"'),)

    return page("Left Factoring", "Remove common prefixes from grammar alternatives", body, js)


# ============================================================
# FIRST & FOLLOW
# ============================================================
FF_EX = [
    ("S&rarr;Aa|bAc|Bc|bBa", "S -> Aa | bAc | Bc | bBa\nA -> d\nB -> d"),
    ("S&rarr;AaAb|BbBa", "S -> AaAb | BbBa\nA -> \u03b5\nB -> \u03b5"),
    ("S&rarr;aAC|Bb", "S -> aAC | Bb\nA -> eD\nB -> f | g\nC -> h | i\nD -> bE | \u03b5\nE -> eD | dD"),
    ("E&rarr;TA (expression)", "E -> TA\nA -> +TA | \u03b5\nT -> VB\nB -> *VB | \u03b5\nV -> id | (E)"),
    ("Dangling else", "S -> iCtSeS | iCtS | a\nC -> b"),
]


def first_follow():
    theory = d("FIRST set", "definition", """
<p><b>FIRST(&alpha;)</b> is the set of terminals that can appear as the <i>first symbol</i> of some string
derived from &alpha;. If &alpha; can derive the empty string, %s is also in FIRST(&alpha;).</p>
<p><b>Rules:</b></p>
<ol>
<li>If X is a terminal, FIRST(X) = { X }.</li>
<li>If <code>X &rarr; %s</code> is a production, add %s to FIRST(X).</li>
<li>If <code>X &rarr; Y<sub>1</sub>Y<sub>2</sub>&hellip;Y<sub>k</sub></code>: add
FIRST(Y<sub>1</sub>) &minus; {%s} to FIRST(X). If Y<sub>1</sub> can derive %s, also add
FIRST(Y<sub>2</sub>) &minus; {%s}, and so on. If <i>every</i> Y can derive %s, add %s to FIRST(X).</li>
</ol>""" % (E, E, E, E, E, E, E, E), "v-t") + \
        d("FOLLOW set", "definition", """
<p><b>FOLLOW(A)</b> is the set of terminals that can appear <i>immediately to the right</i> of A in some
sentential form derived from the start symbol.</p>
<p><b>Rules:</b></p>
<ol>
<li>Put <span class="sym end">$</span> in FOLLOW(S) for the start symbol S.</li>
<li>For a production <code>A &rarr; &alpha;B&beta;</code>: add FIRST(&beta;) &minus; {%s} to FOLLOW(B).</li>
<li>For <code>A &rarr; &alpha;B</code>, or <code>A &rarr; &alpha;B&beta;</code> where &beta; can derive %s:
add everything in FOLLOW(A) to FOLLOW(B).</li>
</ol>
<div class="note tip"><span class="ni">&#128161;</span><div>%s is <b>never</b> a member of a FOLLOW set.
FOLLOW answers "what real token can come next", and the end marker <span class="sym end">$</span> covers
"nothing comes next". Keep applying the rules until no set changes &mdash; this is a fixed-point computation.</div></div>"""
          % (E, E, E), "v-nt") + \
        d("The LL(1) test", "rule", """
<p>Build the predictive table: for each production <code>A &rarr; &alpha;</code>,</p>
<ul><li>for every terminal <code>a</code> in FIRST(&alpha;), put <code>A &rarr; &alpha;</code> in M[A, a];</li>
<li>if %s is in FIRST(&alpha;), put <code>A &rarr; &alpha;</code> in M[A, b] for every b in FOLLOW(A)
(including <span class="sym end">$</span> if present).</li></ul>
<p>The grammar is <b>LL(1)</b> if and only if <b>no cell ends up with two or more productions</b>.</p>""" % E, "v-a")

    body = hero("4", "FIRST &amp; FOLLOW", "Sets",
                "The two sets every predictive parser is built on &mdash; computed with a full iteration trace, "
                "then used to test whether the grammar is LL(1).") + \
        sec("4.1", "Definitions and rules", "", theory, "def") + \
        sec("4.2", "Interactive workbench", "Sets, iteration trace, table and LL(1) verdict.",
            workbench(FF_EX, btn="Compute sets", placeholder="S -> Aa | b\nA -> c"), "tool")

    js = """<script>
(function(){
  var $=UI.$, EX=%s;
  var gin=$('#gin'), out=$('#out'), msg=$('#msg');
  UI.$$('.chip[data-ex]').forEach(function(c){
    c.onclick=function(){UI.$$('.chip[data-ex]').forEach(function(x){x.classList.remove('on')});
      c.classList.add('on'); gin.value=EX[+c.dataset.ex]; run();};
  });
  $('#clear').onclick=function(){gin.value='';out.innerHTML='';msg.innerHTML='';};
  $('#run').onclick=run;
  gin.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&e.key==='Enter')run();});

  function run(){
    var g=UI.readGrammar(gin.value,msg); if(!g)return;
    var t=PL.ll1Table(g);
    out.innerHTML='<div id="sets" class="card"></div>'+
      '<div class="card" style="margin-top:20px"><h3>How each set was built</h3><div id="trace"></div></div>'+
      '<div class="card" style="margin-top:20px"><h3>LL(1) parsing table</h3><div id="verdict"></div><div id="tbl"></div></div>';
    UI.renderSets(g,t.first,t.follow,$('#sets'));

    /* trace */
    var h='<h4 style="color:var(--term)">FIRST &mdash; iteration trace</h4><div class="steps">';
    var n=0;
    t.firstTrace.forEach(function(r){
      r.changes.forEach(function(c){ n++;
        h+='<div class="step"><span class="n">'+n+'</span><div class="bd"><b>FIRST('+UI.esc(c.nt)+') grew &mdash; from '+UI.esc(c.prod)+'</b>'+
           '<span class="muted">Pass '+r.round+' &nbsp;&rarr;&nbsp; now { '+c.set.map(function(s){return UI.chip(g,s)}).join(' ')+' }</span></div></div>';
      });
    });
    h+='</div><h4 style="margin-top:24px;color:var(--nt)">FOLLOW &mdash; iteration trace</h4><div class="steps">';
    n=0;
    t.followTrace.forEach(function(r){
      r.changes.forEach(function(c){ n++;
        h+='<div class="step"><span class="n">'+n+'</span><div class="bd"><b>FOLLOW('+UI.esc(c.nt)+') grew &mdash; from '+UI.esc(c.prod)+'</b>'+
           '<span class="muted">Added via '+UI.esc(c.reason)+' &nbsp;&rarr;&nbsp; now { '+c.set.map(function(s){return UI.chip(g,s)}).join(' ')+' }</span></div></div>';
      });
    });
    h+='</div><p class="muted" style="margin-top:14px">The loop stops when a whole pass adds nothing new &mdash; that is the fixed point.</p>';
    $('#trace').innerHTML=h;

    $('#verdict').innerHTML=UI.ll1Verdict(t);
    UI.renderLL1Table(g,t,$('#tbl'));
  }
  UI.$$('.chip[data-ex]')[0].click();
})();
</script>""" % (repr([g for _, g in FF_EX]).replace("'", '"'),)

    return page("FIRST and FOLLOW", "Compute FIRST and FOLLOW sets and test LL(1)", body, js)
