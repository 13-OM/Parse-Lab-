# -*- coding: utf-8 -*-
from shell import page, sec

NT = '<span class="sym nt">%s</span>'
T = '<span class="sym t">%s</span>'
E = '<span class="sym e">&epsilon;</span>'
AR = '<span class="arrow">&rarr;</span>'


def d(title, tag, body, variant=""):
    v = (" " + variant) if variant else ""
    return ('<div class="def%s"><h4>%s <span class="tag">%s</span></h4>%s</div>'
            % (v, title, tag, body))


def build():
    # ---------- 1. grammar basics ----------
    s1 = d("Grammar", "definition", """
<p>A <b>grammar</b> is a finite set of rules that describes exactly which strings belong to a language.
In a compiler the grammar describes the <i>syntax</i> of the programming language &mdash; what a legal
statement, expression or declaration looks like.</p>""") + d(
        "Context-Free Grammar (CFG)", "definition", """
<p>A CFG is written as a 4-tuple <b>G = (V, T, P, S)</b>:</p>
<ul>
<li><b>V</b> &mdash; the set of <span class="sym nt">non-terminals</span>: variables that still need to be replaced. Written with capital letters.</li>
<li><b>T</b> &mdash; the set of <span class="sym t">terminals</span>: the actual tokens of the language. They never appear on the left of a rule.</li>
<li><b>P</b> &mdash; the set of <b>productions</b>, each of the form <code>A &rarr; &alpha;</code> where A is a single non-terminal
and &alpha; is any string of terminals and non-terminals (possibly %s).</li>
<li><b>S</b> &mdash; the <b>start symbol</b>, one chosen non-terminal where every derivation begins.</li>
</ul>
<p>"Context-free" means the left side is always <i>exactly one</i> non-terminal: A can be replaced by &alpha;
no matter what surrounds it.</p>""" % E) + d(
        "Production, alternative, sentential form", "definition", """
<p>A <b>production</b> is one rewrite rule. When several productions share a left side we write them with a bar:
<code>A &rarr; &alpha; | &beta;</code> &mdash; these are called <b>alternatives</b>.</p>
<p>A <b>sentential form</b> is any string you can reach from S. If it contains only terminals it is a
<b>sentence</b> of the language.</p>""") + """
<div class="card">
  <h3>A worked example</h3>
  <div class="grid g2">
    <div><div class="gbox">
      <div>%s%s%s %s %s</div>
      <div>%s%s%s %s %s <span class="arrow">|</span> %s</div>
      <div>%s%s%s <span class="arrow">|</span> %s %s %s</div>
    </div>
    <div class="kv" style="margin-top:14px">
      <span>V = { E, A, V }</span><span>T = { +, id, (, ) }</span><span>S = E</span>
    </div></div>
    <div>
      <p><b>Reading it aloud:</b> "An expression E is a V followed by an A. An A is either a plus sign,
      another V and another A, or nothing at all. A V is either an identifier or a bracketed expression."</p>
      <p class="muted">The %s alternative is what lets the expression stop &mdash; without it the grammar
      would demand an infinite chain of <code>+ id + id + &hellip;</code></p>
    </div>
  </div>
</div>""" % (NT % "E", AR, NT % "V", NT % "A", "", NT % "A", AR, T % "+", NT % "V", NT % "A", E,
             NT % "V", AR, T % "id", T % "(", NT % "E", T % ")", E)

    # ---------- 2. derivation & parse tree ----------
    s2 = d("Derivation", "definition", """
<p>A <b>derivation</b> is the sequence of replacement steps that turns the start symbol into a string.
Each step uses the symbol <b>&rArr;</b> ("derives in one step"). <b>&rArr;*</b> means "derives in zero or more steps".</p>""") + \
        '<div class="grid g2">' + d(
        "Leftmost derivation (LMD)", "definition", """
<p>At every step you replace the <b>leftmost</b> non-terminal in the sentential form.
This is what a <b>top-down</b> parser produces.</p>
<div class="deriv" style="font-size:.95rem">
<div>%s</div>
<div><span class="ar">&rArr;</span>%s %s</div>
<div><span class="ar">&rArr;</span>%s %s</div>
<div><span class="ar">&rArr;</span>%s %s %s %s</div>
</div>""" % (NT % "E", NT % "V", NT % "A", T % "id", NT % "A", T % "id", T % "+", NT % "V", NT % "A"), "v-nt") + d(
        "Rightmost derivation (RMD)", "definition", """
<p>At every step you replace the <b>rightmost</b> non-terminal. A <b>bottom-up</b> parser builds a
rightmost derivation <i>in reverse</i> &mdash; that is why reductions look like RMD played backwards.</p>
<div class="deriv" style="font-size:.95rem">
<div>%s</div>
<div><span class="ar">&rArr;</span>%s %s</div>
<div><span class="ar">&rArr;</span>%s %s %s %s</div>
<div><span class="ar">&rArr;</span>%s %s %s %s</div>
</div>""" % (NT % "E", NT % "V", NT % "A", NT % "V", T % "+", NT % "V", NT % "A", NT % "V", T % "+", NT % "V", E), "v-t") + \
        '</div>' + d(
        "Parse tree (syntax tree)", "definition", """
<p>A <b>parse tree</b> is the derivation drawn as a tree:</p>
<ul>
<li>the <b>root</b> is the start symbol;</li>
<li>every <b>internal node</b> is a non-terminal, and its children (left to right) are exactly the right-hand
side of the production applied to it;</li>
<li>every <b>leaf</b> is a terminal or %s;</li>
<li>reading the leaves left to right gives back the input string &mdash; this is called the <b>yield</b>.</li>
</ul>
<p>The tree throws away the <i>order</i> in which you expanded things, so a leftmost and a rightmost
derivation of the same string give the <b>same</b> parse tree.</p>""" % E) + """
<div class="card">
  <h3>See it built</h3>
  <p class="muted">The tree for <code>id + id</code>. Press play to watch it grow the way a top-down parser builds it.</p>
  <div class="player" id="thPlayer"></div>
  <div class="tree-wrap" id="thTree"></div>
</div>"""

    # ---------- 3. ambiguity ----------
    s3 = d("Ambiguity", "definition", """
<p>A grammar is <b>ambiguous</b> if there exists at least one string that has <b>two or more distinct
parse trees</b> (equivalently, two or more distinct leftmost derivations).</p>
<p>Ambiguity is a property of the <i>grammar</i>, not of the language. It matters because the parse tree
decides the <i>meaning</i>: for <code>id - id * id</code> one tree computes <code>(a-b)*c</code> and the
other computes <code>a-(b*c)</code>. A compiler cannot be allowed to choose at random.</p>""", "v-bad") + """
<div class="card">
  <h3>The classic ambiguous grammar</h3>
  <div class="gbox in" style="margin-bottom:18px"><div>%s%s%s %s %s <span class="arrow">|</span> %s</div></div>
  <p>The string <code>id - id * id</code> has two different parse trees:</p>
  <div class="grid g2">
    <div><h4 style="text-align:center">Tree 1 &mdash; (id &minus; id) * id</h4><div class="tree-wrap" id="amb1" style="min-height:260px"></div></div>
    <div><h4 style="text-align:center">Tree 2 &mdash; id &minus; (id * id)</h4><div class="tree-wrap" id="amb2" style="min-height:260px"></div></div>
  </div>
  <div class="note bad" style="margin-top:18px"><span class="ni">&#9888;</span>
  <div><b>Two trees &rArr; ambiguous.</b> The usual cures are: rewrite the grammar with one non-terminal per
  precedence level, or keep the grammar and supply precedence/associativity rules separately (what
  operator-precedence parsing and tools like YACC do).</div></div>
</div>
<div class="note tip"><span class="ni">&#128161;</span><div><b>Exam phrasing.</b> "What is ambiguity in grammar?" &mdash;
answer with the definition above, add that it is undecidable in general to test whether an arbitrary CFG is
ambiguous, and give the dangling-else or <code>E &rarr; E A E</code> example.</div></div>""" % (
        NT % "E", AR, NT % "E", NT % "A", NT % "E", T % "id")

    # ---------- 4. recursion ----------
    s4 = d("Left recursion", "definition", """
<p>A grammar is <b>left recursive</b> if some non-terminal A can derive a string that <i>starts with A itself</i>:
<code>A &rArr;<sup>+</sup> A&alpha;</code>.</p>
<ul>
<li><b>Direct (immediate)</b> left recursion &mdash; the production itself begins with A: <code>A &rarr; A&alpha; | &beta;</code>.</li>
<li><b>Indirect</b> left recursion &mdash; it takes more than one step, e.g. <code>A &rarr; Bc</code>, <code>B &rarr; Ad</code>,
so <code>A &rArr; Bc &rArr; Adc</code>.</li>
</ul>
<p><b>Why it is fatal for top-down parsing:</b> a recursive-descent procedure for A would call itself as its
very first action without consuming any input &mdash; infinite recursion, stack overflow. Every top-down
parser therefore needs a left-recursion-free grammar.</p>""", "v-bad") + d(
        "Right recursion", "definition", """
<p><code>A &rarr; &alpha;A</code>. Harmless for top-down parsers (the recursive call happens <i>after</i> input is
consumed), which is why the elimination procedure converts left recursion into right recursion.</p>""", "v-ok") + d(
        "Left factoring", "definition", """
<p>When two alternatives of the same non-terminal begin with the same symbols &mdash;
<code>A &rarr; &alpha;&beta;<sub>1</sub> | &alpha;&beta;<sub>2</sub></code> &mdash; a predictive parser cannot
choose between them with only one token of lookahead. <b>Left factoring</b> pulls the common prefix out:</p>
<div class="gbox out"><div>A &rarr; &alpha;A&prime;</div><div>A&prime; &rarr; &beta;<sub>1</sub> | &beta;<sub>2</sub></div></div>
<p>Now the parser reads &alpha; first and only then has to decide.</p>""", "v-a")

    # ---------- 5. parsing families ----------
    s5 = d("Parser", "definition", """
<p>A <b>parser</b> takes the token stream from the lexical analyser and either builds a parse tree
(proving the input follows the grammar) or reports a syntax error.</p>""") + '<div class="grid g2">' + d(
        "Top-down parsing", "approach", """
<p>Builds the tree <b>from the root downwards</b>, expanding non-terminals until the leaves match the input.
It traces a <b>leftmost derivation</b>.</p>
<ul><li>Recursive descent (one function per non-terminal)</li>
<li>Predictive / <b>LL(1)</b> parsing &mdash; table driven, no backtracking</li></ul>
<p><b>Needs:</b> no left recursion, left factored.<br>
<b>Stack holds:</b> what the parser still <i>expects</i> to see.</p>""", "v-nt") + d(
        "Bottom-up parsing", "approach", """
<p>Builds the tree <b>from the leaves upwards</b>, replacing right-hand sides by their left-hand side until
only the start symbol remains. It traces a <b>rightmost derivation in reverse</b>.</p>
<ul><li>Shift-reduce parsing</li><li>Operator precedence parsing</li>
<li>LR family: LR(0), SLR(1), LR(1), LALR(1)</li></ul>
<p><b>Accepts:</b> a strictly larger class of grammars, including left recursion.<br>
<b>Stack holds:</b> what the parser has <i>already seen and grouped</i>.</p>""", "v-t") + '</div>' + d(
        "LL(1)", "definition", """
<p>The name decodes as: <b>L</b> = scan the input Left to right, <b>L</b> = produce a Leftmost derivation,
<b>(1)</b> = use 1 token of lookahead.</p>
<p>A grammar is LL(1) exactly when its predictive parsing table has <b>no cell with two or more productions</b>.
Equivalently, for every pair of alternatives <code>A &rarr; &alpha; | &beta;</code>:</p>
<ol><li>FIRST(&alpha;) &cap; FIRST(&beta;) = &empty;, and</li>
<li>if &beta; &rArr;* %s then FIRST(&alpha;) &cap; FOLLOW(A) = &empty;.</li></ol>""" % E, "v-a") + d(
        "Handle, shift, reduce", "definition", """
<p>In bottom-up parsing a <b>handle</b> is the substring that matches the right side of a production
<i>and</i> whose reduction is the correct next step backwards along a rightmost derivation.</p>
<p><b>Shift</b> = push the next input token onto the stack.
<b>Reduce</b> = pop the handle and push the non-terminal that produces it.
<b>Accept</b> = the stack holds just the start symbol and the input is exhausted.
<b>Error</b> = neither move is possible.</p>""", "v-ok")

    # ---------- 6. cheat sheet ----------
    s6 = """
<div class="card">
  <h3>Quick comparison</h3>
  <div class="tw"><table>
  <thead><tr><th></th><th>Top-down (LL)</th><th>Bottom-up (LR / operator precedence)</th></tr></thead>
  <tbody>
  <tr><td><b>Tree built</b></td><td>root &rarr; leaves</td><td>leaves &rarr; root</td></tr>
  <tr><td><b>Derivation</b></td><td>leftmost</td><td>rightmost, in reverse</td></tr>
  <tr><td><b>Left recursion</b></td><td>must be removed</td><td>allowed</td></tr>
  <tr><td><b>Left factoring</b></td><td>required</td><td>not required</td></tr>
  <tr><td><b>Ambiguity</b></td><td>not allowed</td><td>allowed if precedence rules are supplied</td></tr>
  <tr><td><b>Main moves</b></td><td>expand (predict) &amp; match</td><td>shift &amp; reduce</td></tr>
  <tr><td><b>Stack contains</b></td><td>expected symbols</td><td>symbols already recognised</td></tr>
  <tr><td><b>Grammar class</b></td><td>smaller</td><td>larger</td></tr>
  </tbody></table></div>
</div>
<div class="note good"><span class="ni">&#9989;</span><div><b>Ready?</b> Each following section takes one of these
ideas and lets you drive it. Start with <a href="left-recursion.html">left recursion</a>, or go straight to the
<a href="ll1.html">LL(1) animation</a>.</div></div>"""

    body = """
<section class="hero" style="padding:52px 0 26px">
  <div class="wrap">
    <span class="pill">Section 1</span>
    <h1>Theory &amp; <span class="g">Definitions</span></h1>
    <p>Everything a parsing question can ask you to "define", written once, clearly, with the example
    that usually follows it in the exam.</p>
  </div>
</section>""" + \
        sec("1.1", "Grammars and CFGs", "The vocabulary every later section assumes.", s1, "cfg") + \
        sec("1.2", "Derivations and parse trees", "How a grammar generates a string, and how we draw it.", s2, "deriv") + \
        sec("1.3", "Ambiguity", "When one string has two meanings.", s3, "ambiguity") + \
        sec("1.4", "Recursion and factoring", "The two grammar diseases that break top-down parsing.", s4, "recursion") + \
        sec("1.5", "Parsing approaches", "Top-down vs bottom-up, and the LL(1) condition.", s5, "parsers") + \
        sec("1.6", "One-page summary", "The table that answers most compare-and-contrast questions.", s6, "summary")

    js = """<script>
(function(){
  var $=UI.$;
  /* --- growing tree demo: E -> V A ; A -> + V A | eps ; V -> id --- */
  var g=PL.parseGrammar("E -> VA\\nA -> +VA | \\u03b5\\nV -> id").grammar;
  var tbl=PL.ll1Table(g);
  var toks=PL.tokenize("id + id");
  var sim=UI.mountLL1Sim({g:g,tbl:tbl,tokens:toks,hosts:{tree:$('#thTree')}});
  UI.makePlayer($('#thPlayer'), sim.total, sim.step, {speed:6});

  /* --- two ambiguous trees, hand-built --- */
  function N(s,k,kids){return {id:Math.random()*1e9|0,sym:s,kind:k,children:kids||[],x:0,y:0};}
  function E(kids){return N('E','nt',kids);}
  var id=function(){return N('id','t');}, A=function(o){return N('A','nt',[N(o,'t')]);};
  /* (id - id) * id */
  var t1=E([ E([ E([id()]), A('-'), E([id()]) ]), A('*'), E([id()]) ]);
  /* id - (id * id) */
  var t2=E([ E([id()]), A('-'), E([ E([id()]), A('*'), E([id()]) ]) ]);
  function paint(){
    UI.drawTree(t1,$('#amb1'),{dx:64,dy:74});
    UI.drawTree(t2,$('#amb2'),{dx:64,dy:74});
  }
  paint();
  document.addEventListener('pl-theme',function(){ paint(); });
})();
</script>"""

    return page("Theory", "Definitions of grammar, CFG, derivation, parse tree, ambiguity and parser types", body, js)
