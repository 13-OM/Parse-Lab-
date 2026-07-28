# -*- coding: utf-8 -*-
"""Shared page shell for Parse Lab."""

NAV = [
    ("index.html",         "",  "Home"),
    ("theory.html",        "1", "Theory"),
    ("left-recursion.html","2", "Left Recursion"),
    ("left-factoring.html","3", "Left Factoring"),
    ("first-follow.html",  "4", "FIRST &amp; FOLLOW"),
    ("ll1.html",           "5", "LL(1)"),
    ("bottom-up.html",     "6", "Bottom-Up"),
    ("operator.html",      "7", "Operator Prec."),
    ("questions.html",     "8", "Questions"),
]


def page(title, subtitle, body, extra_js=""):
    nav = "\n".join(
        '      <a href="%s">%s%s</a>' % (h, ('<span class="nnum">%s</span>' % n) if n else "", t)
        for h, n, t in NAV
    )
    return """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s · Parse Lab</title>
<meta name="description" content="%(subtitle)s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>%(emoji)s</text></svg>">
</head>
<body>

<header class="top">
  <div class="wrap top-in">
    <a class="brand" href="index.html"><span class="logo">&#8594;</span> Parse&nbsp;Lab</a>
    <nav class="nav">
%(nav)s
    </nav>
    <div class="tools">
      <button class="icon-btn burger" data-act="menu" title="Menu">&#9776;</button>
      <button class="icon-btn" data-act="proj" title="Projector mode (bigger text)">&#128253;</button>
      <button class="icon-btn" data-act="theme" title="Dark / light">&#127769;</button>
    </div>
  </div>
</header>

%(body)s

<footer>
  <div class="wrap foot">
    <div><b>Parse Lab</b> &mdash; interactive compiler-design playground for syntax analysis.<br>
    <span class="muted">Theory &rarr; animated tools &rarr; solved university questions. Works fully offline.</span></div>
    <div><a href="index.html">Home</a> &nbsp;&middot;&nbsp; <a href="theory.html">Theory</a> &nbsp;&middot;&nbsp; <a href="questions.html">Questions</a></div>
  </div>
</footer>

<script src="assets/js/engine.js"></script>
<script src="assets/js/ui.js"></script>
%(extra)s
</body>
</html>
""" % {
        "title": title, "subtitle": subtitle, "nav": nav, "body": body,
        "extra": extra_js, "emoji": "&#127793;",
    }


def sec(num, h2, sub, inner, sid=""):
    idattr = ' id="%s"' % sid if sid else ""
    return """<section%s>
  <div class="wrap">
    <div class="sec-head">
      <div class="sec-num">%s</div>
      <div><h2>%s</h2><p class="sub">%s</p></div>
    </div>
    %s
  </div>
</section>""" % (idattr, num, h2, sub, inner)
