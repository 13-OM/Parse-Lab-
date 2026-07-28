# -*- coding: utf-8 -*-
"""LL(1) top-down, bottom-up shift-reduce, operator precedence pages."""
from shell import page, sec

E = '<span class="sym e">&epsilon;</span>'


def d(title, tag, body, variant=""):
    v = (" " + variant) if variant else ""
    return '<div class="def%s"><h4>%s <span class="tag">%s</span></h4>%s</div>' % (v, title, tag, body)


def hero(num, a, b, lead):
    return """
<section class="hero" style="padding:52px 0 26px">
  <div class="wrap">
    <span class="pill">Section %s</span>
    <h1>%s <span class="g">%s</span></h1>
    <p>%s</p>
  </div>
</section>""" % (num, a, b, lead)


SIM_BLOCK = """
<div class="card" id="simCard">
  <h3 id="simTitle">%(title)s</h3>
  <div class="player" id="player"></div>
  <div class="action init" id="action"><span class="bdg">Ready</span><span>Press play to start the animation.</span></div>
  <label class="lb" style="margin-top:18px">Input tape &mdash; the token being read is highlighted</label>
  <div class="tape" id="tape"></div>
  <div class="sim" style="margin-top:18px">
    <div class="stack-box" id="stack"></div>
    <div>
      <label class="lb">%(right)s</label>
      <div class="tree-wrap" id="tree"></div>
    </div>
  </div>
</div>"""


# ============================================================
# LL(1)
# ============================================================
LL_EX = [
    ("E&rarr;TA &nbsp;&middot;&nbsp; id*(id+id)", "E -> TA\nA -> +TA | \u03b5\nT -> VB\nB -> *VB | \u03b5\nV -> id | (E)", "id * ( id + id )"),
    ("S&rarr;aAC|Bb", "S -> aAC | Bb\nA -> eD\nB -> f | g\nC -> h | i\nD -> bE | \u03b5\nE -> eD | dD", "a e b e b h"),
    ("S&rarr;AaAb|BbBa", "S -> AaAb | BbBa\nA -> \u03b5\nB -> \u03b5", "a b"),
    ("Dangling else", "S -> iCtSeS | iCtS | a\nC -> b", "i b t a e a"),
    ("&#9888; Left recursive (fails!)", "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id", "id + id * id"),
]


def ll1():
    theory = d("LL(1) parsing", "definition", """
<p><b>L</b>eft-to-right scan &middot; <b>L</b>eftmost derivation &middot; <b>1</b> token of lookahead.
A <b>predictive parser</b> is a top-down parser that never backtracks: the lookahead token plus the
non-terminal on top of the stack uniquely select the production to apply.</p>
<p>The parser is a table plus a stack plus a driver loop &mdash; no recursion needed.</p>""", "v-a") + \
        d("The driver algorithm", "algorithm", """
<p>Push <span class="sym end">$</span> then the start symbol. Let <b>X</b> = top of stack, <b>a</b> = lookahead.</p>
<ol>
<li>If X = a = <span class="sym end">$</span> &rarr; <b>accept</b>.</li>
<li>If X is a terminal: if X = a, pop X and advance the input (<b>match</b>); otherwise <b>error</b>.</li>
<li>If X is a non-terminal: look up <b>M[X, a]</b>.
 <ul><li>Empty &rarr; <b>error</b>.</li>
 <li>Holds <code>X &rarr; Y&#8321;Y&#8322;&hellip;Y&#8342;</code> &rarr; pop X and push Y&#8342;&hellip;Y&#8322;Y&#8321;
 (<b>reversed</b>, so Y&#8321; ends up on top). This is an <b>expand</b> step; nothing is consumed.</li>
 <li>For <code>X &rarr; %s</code> pop X and push nothing.</li></ul></li>
</ol>
<div class="note tip"><span class="ni">&#128161;</span><div><b>Why reversed?</b> A stack pops last-in-first-out.
The parser must meet Y&#8321; first, so Y&#8321; has to be pushed last.</div></div>""" % E, "v-nt") + \
        d("Building the table", "rule", """
<p>For every production <code>A &rarr; &alpha;</code>: put it in M[A, a] for each terminal a in FIRST(&alpha;);
and if %s &isin; FIRST(&alpha;), put it in M[A, b] for each b in FOLLOW(A).
<b>Any cell receiving two productions means the grammar is not LL(1).</b></p>""" % E, "v-t")

    chips = "".join('<button class="chip" data-ex="%d">%s</button>' % (i, lbl)
                    for i, (lbl, _, _) in enumerate(LL_EX))

    tool = """
<div class="card">
  <div class="split-wide">
    <div>
      <label class="lb">Grammar</label>
      <textarea id="gin" spellcheck="false" style="min-height:150px"></textarea>
      <label class="lb" style="margin-top:16px">Input string to parse</label>
      <input type="text" id="win" spellcheck="false" placeholder="id * ( id + id )">
      <p class="muted" style="margin:8px 0 0;font-size:.82rem">Spaces optional. <code>id</code> is read as one token.</p>
      <div class="btn-row">
        <button class="btn" id="run">Build table &amp; parse</button>
        <button class="btn ghost" id="tblOnly">Table only</button>
      </div>
      <label class="lb" style="margin-top:20px">Saved examples</label>
      <div class="chips">%s</div>
      <div class="note warn" style="margin-top:16px"><span class="ni">&#9888;</span><div style="font-size:.87rem">
      The last example is <b>deliberately left recursive</b>. Load it to see exactly how an LL(1) parser dies:
      the table fills with conflicts and the parser expands forever without ever consuming a token.
      Fix it on the <a href="left-recursion.html">left recursion page</a>, then bring it back here.</div></div>
    </div>
    <div>
      <div id="msg"></div>
      <div id="sets" class="card" style="box-shadow:none;margin-bottom:18px"></div>
      <div id="verdict"></div>
      <label class="lb">Predictive parsing table &mdash; the active cell lights up during the animation</label>
      <div id="tbl"></div>
    </div>
  </div>
</div>
<div id="simHost" style="margin-top:20px"></div>
<div id="derivHost" style="margin-top:20px"></div>""" % chips

    body = hero("5", "LL(1)", "Top-Down Parsing",
                "Build the predictive table, then watch the stack, the input tape, the table cell and the "
                "parse tree move together on every single step.") + \
        sec("5.1", "Definition and algorithm", "", theory, "def") + \
        sec("5.2", "Table builder &amp; animated parser", "Load an example, then press play.", tool, "tool")

    js = """<script>
(function(){
  var $=UI.$, EX=%s;
  var gin=$('#gin'), win=$('#win'), msg=$('#msg');

  UI.$$('.chip[data-ex]').forEach(function(c){
    c.onclick=function(){UI.$$('.chip[data-ex]').forEach(function(x){x.classList.remove('on')});
      c.classList.add('on'); var e=EX[+c.dataset.ex]; gin.value=e[0]; win.value=e[1]; run(true);};
  });
  $('#run').onclick=function(){run(true)};
  $('#tblOnly').onclick=function(){run(false)};
  win.addEventListener('keydown',function(e){if(e.key==='Enter')run(true);});

  function run(doParse){
    var g=UI.readGrammar(gin.value,msg); if(!g)return;
    var t=PL.ll1Table(g);
    UI.renderSets(g,t.first,t.follow,$('#sets'));
    $('#verdict').innerHTML=UI.ll1Verdict(t);
    UI.renderLL1Table(g,t,$('#tbl'));
    $('#simHost').innerHTML=''; $('#derivHost').innerHTML='';
    if(!doParse) return;

    var toks=PL.tokenize(win.value||'');
    if(!toks.length){ $('#simHost').innerHTML='<div class="note warn"><span class="ni">&#9888;</span><div>Type an input string to run the animation.</div></div>'; return; }

    $('#simHost').innerHTML=%s;
    var sim=UI.mountLL1Sim({g:g,tbl:t,tokens:toks,hosts:{
      stack:$('#stack'),tape:$('#tape'),action:$('#action'),tree:$('#tree'),table:$('#tbl')}});
    UI.makePlayer($('#player'),sim.total,sim.step,{speed:5});

    var r=sim.res;
    var banner = r.ok
      ? '<div class="banner ok"><span class="bi">&#10003;</span><div>String ACCEPTED<small>'+UI.esc(toks.join(' '))+' &mdash; parsed in '+r.steps.length+' steps.</small></div></div>'
      : '<div class="banner bad"><span class="bi">&#10007;</span><div>String REJECTED<small>'+UI.esc(r.error||'Parse failed.')+'</small></div></div>';
    $('#simCard').insertAdjacentHTML('afterbegin',banner);

    /* full move table + derivation */
    var h='<div class="card"><h3>Complete parsing trace</h3><div class="tw"><table><thead><tr>'+
      '<th style="width:44px">#</th><th>Stack</th><th>Input remaining</th><th>Action</th></tr></thead><tbody>';
    r.steps.forEach(function(s,i){
      var col=s.cls==='accept'?'var(--ok)':s.cls==='error'?'var(--bad)':s.cls==='match'?'var(--term)':s.cls==='expand'?'var(--nt)':'var(--ink-3)';
      h+='<tr><td class="mono">'+(i+1)+'</td><td class="mono">'+UI.esc(s.stack.join(' '))+
         '</td><td class="mono">'+UI.esc(s.input.join(' '))+
         '</td><td style="color:'+col+';font-weight:600">'+UI.esc(s.action)+'</td></tr>';
    });
    h+='</tbody></table></div></div>';
    if(r.ok){
      h+='<div class="card" style="margin-top:20px"><h3>Leftmost derivation produced</h3>'+
         '<p class="muted">A top-down parser always traces the leftmost derivation &mdash; each line is one expand step.</p>'+
         '<div class="deriv" id="dv"></div></div>';
    }
    $('#derivHost').innerHTML=h;
    if(r.ok) UI.renderDeriv(g,r.tree,$('#dv'),true);
  }
  UI.$$('.chip[data-ex]')[0].click();
})();
</script>""" % (
        repr([[g, w] for _, g, w in LL_EX]).replace("'", '"'),
        repr(SIM_BLOCK % {"title": "Animated parse &mdash; stack, tape and parse tree",
                          "right": "Parse tree &mdash; grows as the parser expands"}).replace("\n", "")
    )

    return page("LL(1) Parsing", "Predictive parsing table and animated top-down parse", body, js)


# ============================================================
# BOTTOM-UP
# ============================================================
BU_EX = [
    ("E&rarr;E+T (classic)", "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id", "id + id * id"),
    ("S&rarr;aABe", "S -> a A B e\nA -> A b c | b\nB -> d", "a b b c d e"),
    ("S&rarr;(L)|a", "S -> ( L ) | a\nL -> L , S | S", "( a , ( a , a ) )"),
    ("Ambiguous E&rarr;E+E", "E -> E + E | E * E | id", "id + id * id"),
    ("LL(1) but not SLR(1)", "S -> AaAb | BbBa\nA -> \u03b5\nB -> \u03b5", "a b"),
]


def bottom_up():
    theory = d("Bottom-up parsing", "definition", """
<p>A bottom-up parser starts at the <b>leaves</b> (the tokens) and works towards the <b>root</b>.
At each step it replaces a substring matching the right side of a production by that production's left side.
This is a <b>reduction</b>, and the whole process traces a <b>rightmost derivation in reverse</b>.</p>""", "v-t") + \
        d("Handle", "definition", """
<p>A <b>handle</b> is a substring that (a) matches the right-hand side of some production, and
(b) whose reduction is one correct step backwards along a rightmost derivation.</p>
<p>Not every match is a handle &mdash; reducing the wrong match leads to a dead end. Finding the handle
reliably is the entire job of the LR machinery.</p>""", "v-nt") + \
        d("Shift-reduce parsing", "algorithm", """
<p>Uses a stack and four actions:</p>
<ul>
<li><b>Shift</b> &mdash; push the next input token onto the stack.</li>
<li><b>Reduce</b> &mdash; the top of the stack is a handle: pop it, push the left-hand non-terminal.</li>
<li><b>Accept</b> &mdash; the start symbol has been reduced and the input is finished.</li>
<li><b>Error</b> &mdash; no move is possible.</li>
</ul>
<div class="note tip"><span class="ni">&#128161;</span><div><b>The key contrast.</b> In a top-down parser the stack
holds what the parser <i>still expects</i>. In a bottom-up parser the stack holds what it has
<i>already recognised</i>. Open the <a href="ll1.html">LL(1) page</a> in another tab and run both &mdash;
the stacks move in opposite directions.</div></div>""", "v-ok") + \
        d("LR(0) items and the automaton", "definition", """
<p>An <b>LR(0) item</b> is a production with a dot marking how much has been seen:
<code>A &rarr; &alpha; &bull; &beta;</code> means &alpha; is already on the stack and &beta; is still expected.</p>
<p><b>CLOSURE</b> of a set of items adds, for every item <code>A &rarr; &alpha; &bull; B&beta;</code>,
all items <code>B &rarr; &bull; &gamma;</code> &mdash; because if we expect a B we may be starting any B production.
<b>GOTO(I, X)</b> advances the dot past X and takes the closure. Starting from the augmented production
<code>S&prime; &rarr; &bull; S</code> and repeating gives the <b>canonical collection</b> of item sets:
the states of a DFA that recognises viable prefixes.</p>""", "v-nt") + \
        d("SLR(1) table construction", "rule", """
<p>From the automaton, for each state <b>i</b>:</p>
<ul>
<li>if <code>A &rarr; &alpha; &bull; a&beta;</code> is in state i and GOTO(i, a) = j, set <b>ACTION[i, a] = shift j</b>;</li>
<li>if <code>A &rarr; &alpha; &bull;</code> is complete (A &ne; S&prime;), set <b>ACTION[i, a] = reduce A &rarr; &alpha;</b>
for every <b>a in FOLLOW(A)</b> &mdash; this FOLLOW guard is what makes it <i>S</i>LR rather than LR(0);</li>
<li>if <code>S&prime; &rarr; S &bull;</code> is in state i, set <b>ACTION[i, $] = accept</b>;</li>
<li>if GOTO(i, A) = j for a non-terminal A, set <b>GOTO[i, A] = j</b>.</li>
</ul>""", "v-a") + \
        d("Conflicts", "definition", """
<p><b>Shift-reduce conflict</b> &mdash; a cell could legally shift or reduce (the dangling else, or any
ambiguous operator grammar).<br>
<b>Reduce-reduce conflict</b> &mdash; two different productions are complete in the same state and share a
FOLLOW symbol.</p>
<div class="note warn"><span class="ni">&#9888;</span><div>If any conflict appears the grammar is <b>not SLR(1)</b>.
This tool still parses by resolving them the way YACC does &mdash; <b>shift beats reduce</b>, and for
reduce-reduce the earlier production wins &mdash; but it flags every conflict so you can see exactly where the
grammar fails. Try the <b>"LL(1) but not SLR(1)"</b> example: it is perfectly LL(1), yet SLR(1) breaks on it.</div></div>""", "v-bad")

    chips = "".join('<button class="chip" data-ex="%d">%s</button>' % (i, lbl)
                    for i, (lbl, _, _) in enumerate(BU_EX))

    tool = """
<div class="card">
  <div class="split-wide">
    <div>
      <label class="lb">Grammar</label>
      <textarea id="gin" spellcheck="false" style="min-height:150px"></textarea>
      <label class="lb" style="margin-top:16px">Input string</label>
      <input type="text" id="win" spellcheck="false" placeholder="id + id * id">
      <div class="btn-row"><button class="btn ok" id="run">Build SLR(1) table &amp; parse</button></div>
      <label class="lb" style="margin-top:20px">Saved examples</label>
      <div class="chips">%s</div>
    </div>
    <div>
      <div id="msg"></div>
      <div id="verdict"></div>
      <label class="lb">ACTION / GOTO table &mdash; the active cell lights up during the animation</label>
      <div id="tbl"></div>
    </div>
  </div>
</div>
<div id="simHost" style="margin-top:20px"></div>
<div id="traceHost" style="margin-top:20px"></div>
<div id="statesHost" style="margin-top:20px"></div>""" % chips

    body = hero("6", "Bottom-Up", "SLR(1) Shift &amp; Reduce",
                "Build the LR(0) item sets, derive the ACTION/GOTO table, then watch the state stack, the "
                "symbol stack and the parse tree assemble from the leaves upward.") + \
        sec("6.1", "Definitions", "", theory, "def") + \
        sec("6.2", "Animated SLR(1) parser", "Table, conflicts, stack and tree.", tool, "tool")

    js = """<script>
(function(){
  var $=UI.$, EX=%s;
  var gin=$('#gin'), win=$('#win'), msg=$('#msg');
  UI.$$('.chip[data-ex]').forEach(function(c){
    c.onclick=function(){UI.$$('.chip[data-ex]').forEach(function(x){x.classList.remove('on')});
      c.classList.add('on'); var e=EX[+c.dataset.ex]; gin.value=e[0]; win.value=e[1]; run();};
  });
  $('#run').onclick=run;
  win.addEventListener('keydown',function(e){if(e.key==='Enter')run();});

  function actStr(T,a){
    if(!a) return '';
    if(a.type==='shift') return 's'+a.n;
    if(a.type==='reduce') return 'r'+a.n;
    return 'acc';
  }

  function run(){
    var g=UI.readGrammar(gin.value,msg); if(!g)return;
    var T=PL.slr1Table(g);
    var ag=T.grammar;

    /* verdict */
    var v='';
    if(T.isSLR1) v='<div class="banner ok"><span class="bi">&#10003;</span><div>The grammar IS SLR(1)'+
      '<small>'+T.states.length+' states, no conflicts in the ACTION table.</small></div></div>';
    else{
      v='<div class="banner bad"><span class="bi">&#10007;</span><div>The grammar is NOT SLR(1)'+
        '<small>'+T.conflicts.length+' conflict(s) found &mdash; resolved YACC-style so the parse can still run.</small></div></div>';
      v+='<div class="steps" style="margin-bottom:16px">';
      T.conflicts.slice(0,8).forEach(function(c,i){
        v+='<div class="step warn"><span class="n">'+(i+1)+'</span><div class="bd"><b>'+c.kind+' conflict in state '+c.state+' on "'+UI.esc(c.term)+'"</b>'+
           '<span class="muted">'+UI.esc(actStr(T,c.a))+' vs '+UI.esc(actStr(T,c.b))+
           ' &mdash; '+(c.kind==='shift-reduce'?'shift wins':'lower production number wins')+'</span></div></div>';
      });
      v+='</div>';
    }
    $('#verdict').innerHTML=v;

    /* numbered productions */
    var pl='<label class="lb">Numbered productions (used by r<i>n</i> in the table)</label><div class="gbox" style="font-size:.98rem;line-height:1.9">';
    ag.prods.forEach(function(p,i){
      pl+='<div><b style="color:var(--ink-3)">'+i+'.</b> &nbsp;'+UI.chip(ag,p.lhs)+'<span class="arrow">&rarr;</span>'+UI.chips(ag,p.rhs)+'</div>';
    });
    pl+='</div>';

    /* ACTION/GOTO table */
    var h=pl+'<div class="tw" style="margin-top:16px"><table class="ptable"><thead><tr><th class="rowh" rowspan="2">State</th>'+
      '<th class="colh" colspan="'+T.terminals.length+'">ACTION</th>'+
      '<th class="colh" colspan="'+T.nonterminals.length+'" style="background:var(--nt-bg);color:var(--nt)">GOTO</th></tr><tr>';
    T.terminals.forEach(function(t){h+='<th class="colh">'+UI.esc(t)+'</th>';});
    T.nonterminals.forEach(function(n){h+='<th class="colh" style="background:var(--nt-bg);color:var(--nt)">'+UI.esc(n)+'</th>';});
    h+='</tr></thead><tbody>';
    T.states.forEach(function(_,i){
      h+='<tr><td class="rowh">'+i+'</td>';
      T.terminals.forEach(function(t){
        var a=T.ACTION[i].get(t);
        var conf=T.conflicts.some(function(c){return c.state===i&&c.term===t;});
        if(!a) h+='<td class="empty" data-ag="'+i+'|'+UI.esc(t)+'">&ndash;</td>';
        else h+='<td class="'+(conf?'conflict':'filled')+'" data-ag="'+i+'|'+UI.esc(t)+'">'+actStr(T,a)+'</td>';
      });
      T.nonterminals.forEach(function(n){
        var gt=T.GOTO[i].get(n);
        h+='<td class="'+(gt===undefined?'empty':'filled')+'" style="'+(gt===undefined?'':'background:color-mix(in srgb,var(--nt) 12%%,transparent);color:var(--nt)')+'" data-ag="'+i+'|'+UI.esc(n)+'">'+(gt===undefined?'&ndash;':gt)+'</td>';
      });
      h+='</tr>';
    });
    h+='</tbody></table></div>';
    h+='<div class="legend"><span><b>s<i>n</i></b> shift and go to state n</span><span><b>r<i>n</i></b> reduce by production n</span>'+
       '<span><b>acc</b> accept</span><span><b>&ndash;</b> error</span></div>';
    $('#tbl').innerHTML=h;

    /* parse */
    var toks=PL.tokenize(win.value||'');
    $('#simHost').innerHTML=''; $('#traceHost').innerHTML='';
    if(toks.length){
      var r=PL.slr1Parse(T,toks);
      var all=toks.concat(['$']);
      $('#simHost').innerHTML=%s;
      $('#simCard').insertAdjacentHTML('afterbegin', r.ok
        ? '<div class="banner ok"><span class="bi">&#10003;</span><div>String ACCEPTED<small>'+UI.esc(toks.join(' '))+' &mdash; reduced to the start symbol in '+r.steps.length+' steps.</small></div></div>'
        : '<div class="banner bad"><span class="bi">&#10007;</span><div>String REJECTED<small>'+UI.esc(r.error||'')+'</small></div></div>');

      var tv = r.tree ? UI.drawTree(r.tree,$('#tree'),{dx:72,dy:82}) : null;
      if(!r.tree) $('#tree').innerHTML='<p class="muted center" style="padding:40px">No complete parse tree &mdash; the parse did not reach the start symbol.</p>';

      function step(i){
        var s=r.steps[i];
        /* interleave states and symbols like a real LR stack */
        var disp=[]; 
        for(var k=0;k<s.states.length;k++){
          disp.push({v:String(s.states[k]),k:'state'});
          if(s.stack[k]!==undefined) disp.push(s.stack[k]);
        }
        UI.renderStack(ag,disp,$('#stack'),'LR stack (state / symbol)');
        UI.renderTape(ag,all,all.length-s.input.length,$('#tape'));
        var bdg={init:'Start',shift:'Shift',reduce:'Reduce',accept:'Accept',error:'Error'}[s.cls]||'Step';
        $('#action').className='action '+s.cls;
        $('#action').innerHTML='<span class="bdg">'+bdg+'</span><span>'+UI.esc(s.action)+'</span>';

        UI.$$('.ptable td.hot',$('#tbl')).forEach(function(td){td.classList.remove('hot')});
        if(s.cls==='shift'||s.cls==='reduce'||s.cls==='accept'){
          var st=s.states[s.states.length-1], la=s.input[0];
          if(s.cls!=='init'){
            var prev=r.steps[i-1];
            if(prev){ st=prev.states[prev.states.length-1]; la=prev.input[0]; }
          }
          var td=UI.$$('.ptable td[data-ag]',$('#tbl')).filter(function(x){return x.dataset.ag===st+'|'+la})[0];
          if(td) td.classList.add('hot');
        }
        if(tv){
          var reds=0; for(var q=0;q<=i;q++) if(r.steps[q].cls==='reduce') reds++;
          var order=[]; (function post(n){n.children.forEach(post); if(n.children.length) order.push(n);})(r.tree);
          var vis=new Set();
          (function leaves(n){ if(!n.children.length) vis.add(n.id); n.children.forEach(leaves);})(r.tree);
          for(var z=0;z<reds&&z<order.length;z++){ vis.add(order[z].id); order[z].children.forEach(function(c){vis.add(c.id)}); }
          tv.map.forEach(function(val,id){ val.g.style.opacity=vis.has(id)?'1':'0.07'; val.g.classList.remove('pulse'); });
          UI.$$('.tedge',tv.svg).forEach(function(e){ e.style.opacity=vis.has(+e.dataset.child)?'1':'0.07'; });
          if(s.cls==='reduce'&&order[reds-1]){var x=tv.map.get(order[reds-1].id); if(x)x.g.classList.add('pulse');}
        }
      }
      UI.makePlayer($('#player'),r.steps.length,step,{speed:5});

      var m='<div class="card"><h3>Complete SLR(1) parse trace</h3><div class="tw"><table><thead><tr>'+
        '<th style="width:44px">#</th><th>State stack</th><th>Symbol stack</th><th>Input</th><th>Action</th></tr></thead><tbody>';
      r.steps.forEach(function(s,i){
        var col=s.cls==='accept'?'var(--ok)':s.cls==='error'?'var(--bad)':s.cls==='reduce'?'var(--nt)':'var(--info)';
        m+='<tr><td class="mono">'+(i+1)+'</td><td class="mono">'+s.states.join(' ')+'</td><td class="mono">'+
           UI.esc(s.stack.join(' ')||'&nbsp;')+'</td><td class="mono">'+UI.esc(s.input.join(' '))+
           '</td><td style="color:'+col+';font-weight:600">'+UI.esc(s.action)+'</td></tr>';
      });
      m+='</tbody></table></div>';
      if(r.ok) m+='<h4 style="margin-top:22px">Rightmost derivation (the reductions read backwards)</h4><div class="deriv" id="dv"></div>';
      m+='</div>';
      $('#traceHost').innerHTML=m;
      if(r.ok) UI.renderDeriv(ag,r.tree,$('#dv'),false);
    }

    /* canonical collection */
    var sc='<div class="card"><h3>Canonical collection of LR(0) item sets</h3>'+
      '<p class="muted">Each state is a set of items; the dot &bull; shows how much of the production has been seen. '+
      'Arrows are the GOTO transitions of the automaton.</p><div class="grid g3">';
    T.states.forEach(function(its,i){
      sc+='<div class="card" style="padding:14px;box-shadow:none"><b style="color:var(--primary)">I'+i+'</b>'+
          '<div class="gbox" style="font-size:.86rem;line-height:1.7;padding:10px 12px;margin-top:8px">';
      its.forEach(function(it){ sc+='<div>'+UI.esc(T.itemStr(it))+'</div>'; });
      sc+='</div>';
      var outs=T.trans.filter(function(t){return t.from===i});
      if(outs.length){
        sc+='<div class="kv" style="margin-top:8px">';
        outs.forEach(function(t){ sc+='<span>'+UI.esc(t.sym)+' &rarr; I'+t.to+'</span>'; });
        sc+='</div>';
      }
      sc+='</div>';
    });
    sc+='</div></div>';
    $('#statesHost').innerHTML=sc;
  }
  UI.$$('.chip[data-ex]')[0].click();
})();
</script>""" % (
        repr([[g, w] for _, g, w in BU_EX]).replace("'", '"'),
        repr(SIM_BLOCK % {"title": "Animated SLR(1) parse",
                          "right": "Parse tree &mdash; assembles from the leaves upward"}).replace("\n", "")
    )

    return page("Bottom-Up Parsing", "SLR(1) table construction and animated shift-reduce parsing", body, js)


# ============================================================
# OPERATOR PRECEDENCE
# ============================================================
def operator():
    theory = d("Operator grammar", "definition", """
<p>A grammar is an <b>operator grammar</b> if it satisfies <b>both</b> conditions:</p>
<ol>
<li>No production right-hand side is %s (no &epsilon;-productions), and</li>
<li>No production right-hand side has <b>two adjacent non-terminals</b>.</li>
</ol>
<p>So every pair of non-terminals in a right-hand side must be separated by at least one terminal &mdash;
an <i>operator</i>. That is where the name comes from.</p>
<div class="grid g2" style="margin-top:14px">
  <div><div class="gbox in" style="font-size:.98rem"><div>E &rarr; E A E | id</div><div>A &rarr; &minus; | *</div></div>
  <p class="muted" style="margin-top:8px"><b>Not</b> an operator grammar: <code>E A E</code> has E next to A, and A next to E.</p></div>
  <div><div class="gbox out" style="font-size:.98rem"><div>E &rarr; E &minus; E | E * E | id</div></div>
  <p class="muted" style="margin-top:8px"><b>Is</b> an operator grammar: every pair of non-terminals is separated by an operator.</p></div>
</div>""" % E, "v-a") + \
        d("Converting to an operator grammar", "rule", """
<p>When a non-terminal exists only to hold operators (every one of its productions is a single terminal),
<b>substitute it back</b> into the right-hand sides where it appears. The adjacency disappears and the
language is unchanged.</p>
<p>For <code>E &rarr; E A E</code> with <code>A &rarr; &minus; | *</code>, replacing A by each of its
alternatives gives <code>E &rarr; E &minus; E | E * E | id</code>.</p>""", "v-ok") + \
        d("Precedence relations", "definition", """
<p>Between two terminals a and b exactly one relation may hold:</p>
<div class="grid g3" style="margin:14px 0">
  <div class="card" style="padding:16px;text-align:center"><div style="font-size:2rem;color:var(--warn)">&#8918;</div>
  <b>a &#8918; b</b><p class="muted" style="margin:6px 0 0;font-size:.86rem">"a yields precedence to b" &mdash; b has higher precedence, so <b>shift</b>.</p></div>
  <div class="card" style="padding:16px;text-align:center"><div style="font-size:2rem;color:var(--warn)">&#8784;</div>
  <b>a &#8784; b</b><p class="muted" style="margin:6px 0 0;font-size:.86rem">"equal precedence" &mdash; they appear in the same right-hand side, like ( and ).</p></div>
  <div class="card" style="padding:16px;text-align:center"><div style="font-size:2rem;color:var(--warn)">&#8919;</div>
  <b>a &#8919; b</b><p class="muted" style="margin:6px 0 0;font-size:.86rem">"a takes precedence over b" &mdash; a is higher, so <b>reduce</b>.</p></div>
</div>
<p>These are <b>not</b> the same as &lt; and &gt;: it is perfectly possible for neither
<code>a &#8918; b</code> nor <code>a &#8919; b</code> to hold, which signals a syntax error.</p>""", "v-nt") + \
        d("Parsing algorithm", "algorithm", """
<p>Scan with the stack top terminal <b>a</b> and the lookahead <b>b</b>:</p>
<ul><li><code>a &#8918; b</code> or <code>a &#8784; b</code> &rarr; push the relation and <b>shift</b> b.</li>
<li><code>a &#8919; b</code> &rarr; <b>reduce</b>: pop back to the most recent &#8918; and replace the popped
handle by a non-terminal N.</li>
<li>stack = <code>$</code> and lookahead = <code>$</code> &rarr; <b>accept</b>.</li>
<li>no relation &rarr; <b>error</b>.</li></ul>
<div class="note tip"><span class="ni">&#128161;</span><div>Operator-precedence parsers ignore which non-terminal
is which &mdash; every reduction just produces "N". That is why they are small and fast, and why they are only
used for expression grammars.</div></div>""", "v-t")

    tool = """
<div class="card">
  <h3>Step 1 &mdash; Check / convert to an operator grammar</h3>
  <div class="split-wide">
    <div>
      <label class="lb">Grammar</label>
      <textarea id="gin" spellcheck="false" style="min-height:130px">E -> EAE | id
A -> - | *</textarea>
      <div class="btn-row"><button class="btn" id="chk">Check &amp; convert</button></div>
      <label class="lb" style="margin-top:18px">Saved examples</label>
      <div class="chips">
        <button class="chip" data-g="E -> EAE | id&#10;A -> - | *">E&rarr;EAE, A&rarr;&minus;|*</button>
        <button class="chip" data-g="E -> E + E | E * E | ( E ) | id">E&rarr;E+E|E*E|(E)|id</button>
        <button class="chip" data-g="S -> S A S | a&#10;A -> + | -">S&rarr;SAS|a</button>
      </div>
    </div>
    <div><div id="msg"></div><div id="opOut"></div></div>
  </div>
</div>

<div class="card" style="margin-top:20px">
  <h3>Step 2 &mdash; Precedence table &amp; parse</h3>
  <div class="split-wide">
    <div>
      <label class="lb">Precedence levels (lowest first, comma separated)</label>
      <input type="text" id="lv1" value="+ , -" placeholder="+ , -">
      <input type="text" id="lv2" value="* , /" style="margin-top:8px">
      <input type="text" id="lv3" value="^" style="margin-top:8px" placeholder="(optional)">
      <label class="lb" style="margin-top:16px">Operands / atoms</label>
      <input type="text" id="atoms" value="id">
      <label class="lb" style="margin-top:16px">Input string</label>
      <input type="text" id="win" value="id + id * id">
      <div class="btn-row"><button class="btn amber" id="run">Build table &amp; parse</button></div>
    </div>
    <div><div id="tblOut"></div></div>
  </div>
</div>
<div id="simHost" style="margin-top:20px"></div>
<div id="traceHost" style="margin-top:20px"></div>"""

    body = hero("7", "Operator", "Precedence",
                "Check the operator-grammar conditions, convert a grammar that fails them, build the "
                "&#8918; &#8784; &#8919; table, and parse with an animated stack.") + \
        sec("7.1", "Definitions", "", theory, "def") + \
        sec("7.2", "Interactive workbench", "", tool, "tool")

    js = """<script>
(function(){
  var $=UI.$;
  var gin=$('#gin'), msg=$('#msg');
  UI.$$('.chip[data-g]').forEach(function(c){
    c.onclick=function(){UI.$$('.chip[data-g]').forEach(function(x){x.classList.remove('on')});
      c.classList.add('on'); gin.value=c.dataset.g; chk();};
  });
  $('#chk').onclick=chk;
  function chk(){
    var g=UI.readGrammar(gin.value,msg); if(!g)return;
    var c=PL.isOperatorGrammar(g);
    var h='';
    if(c.ok){
      h+='<div class="banner ok"><span class="bi">&#10003;</span><div>This IS an operator grammar<small>No &epsilon;-productions and no two adjacent non-terminals.</small></div></div>';
      h+='<div class="gbox out">'+UI.grammarHTML(g)+'</div>';
    } else {
      h+='<div class="banner bad"><span class="bi">&#10007;</span><div>NOT an operator grammar<small>'+c.problems.length+' violation(s) found.</small></div></div>';
      h+='<div class="steps" style="margin-bottom:16px">';
      c.problems.forEach(function(p,i){
        h+='<div class="step"><span class="n">'+(i+1)+'</span><div class="bd"><b>'+UI.esc(p.prod)+'</b><span class="muted">'+UI.esc(p.why)+'</span></div></div>';
      });
      h+='</div>';
      var conv=PL.toOperatorGrammar(g);
      h+='<div class="grid g2"><div><h4 style="color:var(--bad)">Original</h4><div class="gbox in">'+UI.grammarHTML(g)+'</div></div>'+
         '<div><h4 style="color:var(--ok)">Operator grammar</h4><div class="gbox out">'+UI.grammarHTML(conv.grammar)+'</div></div></div>';
      if(conv.log.length){
        h+='<h4 style="margin-top:20px">Conversion steps</h4><div class="steps">';
        conv.log.forEach(function(l,i){
          h+='<div class="step ok"><span class="n">'+(i+1)+'</span><div class="bd"><b>Substitute '+UI.esc(l.nt)+' &rarr; '+l.with.map(UI.esc).join(' | ')+'</b><span class="muted">'+UI.esc(l.text)+'</span></div></div>';
        });
        h+='</div>';
        h+= conv.check.ok
          ? '<div class="note good" style="margin-top:16px"><span class="ni">&#9989;</span><div>The converted grammar now satisfies both operator-grammar conditions.</div></div>'
          : '<div class="note warn" style="margin-top:16px"><span class="ni">&#9888;</span><div>Some adjacency remains &mdash; it cannot be fixed by simple substitution.</div></div>';
      }
    }
    $('#opOut').innerHTML=h;
  }

  $('#run').onclick=function(){
    var lv=[];
    [$('#lv1'),$('#lv2'),$('#lv3')].forEach(function(inp){
      var ops=inp.value.split(',').map(function(s){return s.trim()}).filter(Boolean);
      if(ops.length) lv.push({ops:ops,assoc:'left'});
    });
    var atoms=$('#atoms').value.split(',').map(function(s){return s.trim()}).filter(Boolean);
    if(!lv.length||!atoms.length){$('#tblOut').innerHTML='<div class="note warn"><span class="ni">&#9888;</span><div>Enter at least one precedence level and one atom.</div></div>';return;}
    /* include brackets automatically if present in the input */
    var w=$('#win').value;
    var toks=PL.tokenize(w);
    var pt=PL.precedenceTable(lv,atoms);

    var syms=pt.symbols;
    var h='<label class="lb">Precedence relation table &mdash; row = stack top, column = lookahead</label>';
    h+='<div class="tw"><table class="ptable"><thead><tr><th class="rowh">&#9660; stack \\\\ input &#9654;</th>';
    syms.forEach(function(s){h+='<th class="colh">'+UI.esc(s)+'</th>';});
    h+='</tr></thead><tbody>';
    syms.forEach(function(a){
      h+='<tr><td class="rowh">'+UI.esc(a)+'</td>';
      syms.forEach(function(b){
        var v=pt.table.get(a).get(b);
        if(v==='accept') h+='<td class="filled" style="background:var(--ok-bg);color:var(--ok)">acc</td>';
        else if(!v) h+='<td class="empty">&ndash;</td>';
        else h+='<td class="filled" style="font-size:1.25rem">'+v+'</td>';
      });
      h+='</tr>';
    });
    h+='</tbody></table></div>';
    h+='<div class="legend"><span><b style="color:var(--warn);font-size:1.1rem">&#8918;</b> shift (input has higher precedence)</span>'+
       '<span><b style="color:var(--warn);font-size:1.1rem">&#8919;</b> reduce (stack has higher precedence)</span>'+
       '<span><b>&ndash;</b> no relation &rarr; error</span></div>';
    $('#tblOut').innerHTML=h;

    if(!toks.length){$('#simHost').innerHTML='';$('#traceHost').innerHTML='';return;}
    var r=PL.opPrecParse(pt,toks);
    var all=toks.concat(['$']);
    $('#simHost').innerHTML='<div class="card" id="simCard"><h3>Animated operator-precedence parse</h3>'+
      '<div class="player" id="player"></div>'+
      '<div class="action init" id="action"></div>'+
      '<label class="lb" style="margin-top:18px">Input tape</label><div class="tape" id="tape"></div>'+
      '<div style="margin-top:18px;max-width:340px"><div class="stack-box" id="stack"></div></div></div>';
    $('#simCard').insertAdjacentHTML('afterbegin', r.ok
      ? '<div class="banner ok"><span class="bi">&#10003;</span><div>String ACCEPTED</div></div>'
      : '<div class="banner bad"><span class="bi">&#10007;</span><div>Parse failed<small>'+UI.esc(r.error||'')+'</small></div></div>');

    function step(i){
      var s=r.steps[i];
      UI.renderStack(null,s.stack,$('#stack'),'Operator stack');
      UI.renderTape(null,all,all.length-s.input.length,$('#tape'));
      var bdg={init:'Start',shift:'Shift',reduce:'Reduce',accept:'Accept',error:'Error'}[s.cls]||'Step';
      $('#action').className='action '+s.cls;
      $('#action').innerHTML='<span class="bdg">'+bdg+'</span><span>'+UI.esc(s.action)+'</span>';
    }
    UI.makePlayer($('#player'),r.steps.length,step,{speed:5});

    var t='<div class="card"><h3>Complete trace</h3><div class="tw"><table><thead><tr><th style="width:44px">#</th><th>Stack</th><th>Input</th><th>Action</th></tr></thead><tbody>';
    r.steps.forEach(function(s,i){
      var col=s.cls==='accept'?'var(--ok)':s.cls==='error'?'var(--bad)':s.cls==='reduce'?'var(--nt)':'var(--info)';
      t+='<tr><td class="mono">'+(i+1)+'</td><td class="mono">'+UI.esc(s.stack.join(' '))+'</td><td class="mono">'+
         UI.esc(s.input.join(' '))+'</td><td style="color:'+col+';font-weight:600">'+UI.esc(s.action)+'</td></tr>';
    });
    t+='</tbody></table></div></div>';
    $('#traceHost').innerHTML=t;
  };

  chk();
  $('#run').click();
})();
</script>"""

    return page("Operator Precedence", "Operator grammar check, precedence table and animated parse", body, js)
