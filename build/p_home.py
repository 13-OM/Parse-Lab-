# -*- coding: utf-8 -*-
from shell import page, sec

TOOLS = [
    ("theory.html", "&#128218;", "Theory &amp; Definitions", "Every term defined in plain language first: grammar, CFG, derivation, parse tree, ambiguity, recursion, parser families.", "var(--primary)"),
    ("left-recursion.html", "&#128257;", "Left Recursion Removal", "Direct and indirect left recursion, removed step by step with the &alpha;/&beta; split shown visually.", "var(--nt)"),
    ("left-factoring.html", "&#9986;", "Left Factoring", "Find the longest common prefix and split it out so a predictive parser can decide with one lookahead.", "var(--info)"),
    ("first-follow.html", "&#127919;", "FIRST &amp; FOLLOW Sets", "Rule-by-rule computation with an iteration trace showing exactly which rule added which symbol.", "var(--term)"),
    ("ll1.html", "&#11015;", "LL(1) Top-Down Parser", "Build the predictive table, detect conflicts, then watch the stack, the tape and the parse tree grow together.", "var(--accent)"),
    ("bottom-up.html", "&#11014;", "Bottom-Up Shift-Reduce", "Handles, shifts and reductions animated on a stack, with the parse tree assembling from the leaves upward.", "var(--ok)"),
    ("operator.html", "&#10133;", "Operator Precedence", "Operator grammar checking, precedence-relation table (&#8918; &#8919; &#8784;) and a full parse animation.", "var(--warn)"),
    ("questions.html", "&#127891;", "Solved Question Bank", "11 university exam questions worked out in full, each with its own animated parse tree or stack trace.", "var(--eps)"),
]


def build():
    cards = "".join(
        '<a class="tcard" href="%s" style="--c:%s"><span class="ic">%s</span><h3>%s</h3><p>%s</p><div class="go">Open &rarr;</div></a>'
        % (h, c, ic, t, d) for h, ic, t, d, c in TOOLS
    )

    hero = """
<section class="hero">
  <div class="wrap">
    <span class="pill">&#9679; Compiler Design &middot; Unit 3 &middot; Syntax Analysis</span>
    <h1>Learn parsing by <span class="g">watching it happen</span></h1>
    <p>Every concept starts with a clear definition, then you drive the algorithm yourself &mdash;
       stacks that push and pop, parse trees that grow node by node, and tables that light up
       the exact cell the parser is reading. Built big and bright for classroom projectors.</p>
    <div class="btn-row" style="justify-content:center">
      <a class="btn" href="theory.html">&#128218; Start with the theory</a>
      <a class="btn amber" href="ll1.html">&#9654; Jump to the animation</a>
      <a class="btn ghost" href="questions.html">&#127891; Solved questions</a>
    </div>
  </div>
</section>"""

    how = """
<div class="grid g3">
  <div class="card">
    <h3>&#9312; Read the definition</h3>
    <p class="muted">Each section opens with a boxed definition, the formal rule, and a tiny worked example &mdash;
    so nobody is guessing what a term means before the animation starts.</p>
  </div>
  <div class="card">
    <h3>&#9313; Watch the animation</h3>
    <p class="muted">Press play. The stack, the input tape, the parsing table and the parse tree all update
    on the same step, so the link between them is impossible to miss.</p>
  </div>
  <div class="card">
    <h3>&#9314; Run your own</h3>
    <p class="muted">Every tool has an editable grammar box. Paste any question from your syllabus,
    press solve, and get the same full working &mdash; not just a final answer.</p>
  </div>
</div>"""

    feat = """
<div class="card">
  <div class="grid g2" style="align-items:center">
    <div>
      <h3>Colour is the grammar</h3>
      <p>One colour code runs through the whole site &mdash; the table, the stack, the tree and the derivations
      all use the same three colours, so students can read any diagram at a glance from the back of the room.</p>
      <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:16px">
        <span class="sym nt">A</span><span class="muted" style="align-self:center">non-terminal</span>
        <span class="sym t">id</span><span class="muted" style="align-self:center">terminal</span>
        <span class="sym e">&epsilon;</span><span class="muted" style="align-self:center">empty string</span>
        <span class="sym end">$</span><span class="muted" style="align-self:center">end marker</span>
      </div>
      <div class="note tip" style="margin-top:20px"><span class="ni">&#128253;</span>
      <div><b>Projector mode</b> &mdash; the film icon in the top bar scales the whole site up for a lecture hall.
      The moon icon flips to a dark theme for bright rooms.</div></div>
    </div>
    <div class="gbox">
      <div><span class="sym nt">E</span><span class="arrow">&rarr;</span><span class="sym nt">T</span> <span class="sym nt">A</span></div>
      <div><span class="sym nt">A</span><span class="arrow">&rarr;</span><span class="sym t">+</span> <span class="sym nt">T</span> <span class="sym nt">A</span> <span class="arrow">|</span> <span class="sym e">&epsilon;</span></div>
      <div><span class="sym nt">T</span><span class="arrow">&rarr;</span><span class="sym nt">V</span> <span class="sym nt">B</span></div>
      <div><span class="sym nt">B</span><span class="arrow">&rarr;</span><span class="sym t">*</span> <span class="sym nt">V</span> <span class="sym nt">B</span> <span class="arrow">|</span> <span class="sym e">&epsilon;</span></div>
      <div><span class="sym nt">V</span><span class="arrow">&rarr;</span><span class="sym t">id</span> <span class="arrow">|</span> <span class="sym t">(</span> <span class="sym nt">E</span> <span class="sym t">)</span></div>
    </div>
  </div>
</div>"""

    body = hero + \
        sec("&#9733;", "The toolkit", "Nine sections, each self-contained: definition, interactive tool, and saved examples.",
            '<div class="grid g4">' + cards + '</div>', "tools") + \
        sec("&#8594;", "How each section works", "The same three-beat rhythm everywhere.", how) + \
        sec("&#9679;", "Designed for the classroom", "Readable from the back row.", feat)

    return page("Home", "Interactive compiler-design parsing playground", body)
