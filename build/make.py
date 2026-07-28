# -*- coding: utf-8 -*-
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p_home, p_theory, p_tools1, p_tools2, p_questions

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

pages = {
    "index.html":          p_home.build(),
    "theory.html":         p_theory.build(),
    "left-recursion.html": p_tools1.left_recursion(),
    "left-factoring.html": p_tools1.left_factoring(),
    "first-follow.html":   p_tools1.first_follow(),
    "ll1.html":            p_tools2.ll1(),
    "bottom-up.html":      p_tools2.bottom_up(),
    "operator.html":       p_tools2.operator(),
    "questions.html":      p_questions.build(),
}
for name, html in pages.items():
    with io.open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %-22s %6d bytes" % (name, len(html)))
