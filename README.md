# Parse Lab — Interactive Compiler-Design Parsing Playground

An offline, single-folder website for teaching **syntax analysis** (Compiler Design, Unit 3).
Inspired by the *parsing-toys* concept, rebuilt with a teaching-first UI: **definition → animated tool → solved exam questions**.

## How to use it

Just open **`index.html`** in any browser. No server, no install, no internet needed.

To serve it locally instead:
```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Putting it on GitHub

```bash
cd compiler-parsing-lab
git init
git add .
git commit -m "Parse Lab — interactive compiler-design parsing playground"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### Publishing it live (free)

The repo ships with `.github/workflows/deploy.yml`, so publishing takes one click:

1. Push the repo (above).
2. On GitHub go to **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **GitHub Actions**.

Every push to `main` then republishes automatically, and your site goes live at
`https://<your-username>.github.io/<your-repo>/`.

> Prefer not to use Actions? **Settings → Pages → Source: Deploy from a branch → `main` / `(root)`**
> also works, because the site is plain static HTML. Delete the `.github/` folder in that case.

## The nine sections

| # | Page | What it does |
|---|------|--------------|
| — | `index.html` | Landing page + toolkit overview |
| 1 | `theory.html` | Every definition: grammar, CFG, derivation, parse tree, ambiguity (two trees side by side), recursion, LL vs LR |
| 2 | `left-recursion.html` | Direct **and** indirect elimination (Paull's algorithm) with every substitution shown |
| 3 | `left-factoring.html` | Longest-common-prefix factoring + before/after LL(1) status |
| 4 | `first-follow.html` | FIRST/FOLLOW with a full **iteration trace** (which rule added which symbol) |
| 5 | `ll1.html` | Predictive table + **animated top-down parse**: stack, tape, live table cell, growing parse tree |
| 6 | `bottom-up.html` | Real **SLR(1)**: LR(0) item sets, ACTION/GOTO table, conflicts, animated shift-reduce |
| 7 | `operator.html` | Operator-grammar check & conversion, ⋖ ≐ ⋗ precedence table, animated parse |
| 8 | `questions.html` | **11 solved exam questions**, each fully worked + "run your own" solver |

## Classroom features

- **Projector mode** (film icon, top right) — scales the whole site up for a lecture hall. Persists across pages.
- **Dark mode** (moon icon) — for bright rooms.
- **Step player** on every animation — first / prev / play / next / last, with a speed slider.
- **Consistent colour code everywhere**: <span>non-terminal = purple</span>, terminal = teal, ε = pink, $ = grey.
- Fully responsive (tested 390 px → 1920 px) and print-friendly (solutions expand when printed).

## Grammar input syntax

```
S -> Aa | b          # '->' or '→' ; alternatives with '|' or '/'
A -> Ac | Sd | ε     # empty string: ε, €, ∈, e, eps, epsilon
E -> ( E ) | id      # 'id' is read as ONE token
```
Capital letters start non-terminals (`A`, `A'`, `S1`). Everything else is a terminal.
Quote a symbol (`'+'`) to force it to be a terminal.

## Project layout

```
index.html … questions.html   generated pages
assets/css/style.css          design system (colour, layout, animation)
assets/js/engine.js           all algorithms — pure, no dependencies
assets/js/ui.js               rendering, animation, step player
build/                        Python generators (rebuild with: cd build && python3 make.py)
```

The pages are generated, but they are **plain static HTML** — you can edit them directly if you
don't want to touch the build scripts. To regenerate after editing `build/*.py`:

```bash
cd build && python3 make.py
```

## Engine coverage

`assets/js/engine.js` implements, dependency-free:
tokenizer · grammar parser · FIRST · FOLLOW · LL(1) table + parse · left-recursion elimination
(direct + indirect) · left factoring · operator-grammar test & conversion · precedence table &
parse · LR(0) closure/goto/canonical collection · SLR(1) table + parse · leftmost/rightmost
derivations · tidy tree layout.

All 11 bundled questions were verified against their textbook answers.
