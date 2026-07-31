---
name: html2deck
description: Turn an HTML page (benchmark walkthrough, README, or written explainer) into 16:9 presentation slides by MEASURING rendered height, projecting a visual-first face (strip excess prose to speaker notes), and splitting overflowing sections at safe child boundaries — never shrinking text below a readability floor. Emits .pptx and .pdf plus a contact sheet for human approval.
when_to_use: When you have a long HTML page and need it as a slide deck, and you care that charts, code, and numbers land on slides intact and legible rather than crushed to fit.
---

# html2deck

## What it does

Given an HTML page, html2deck renders it in headless Chromium at exactly
1280x720 (16:9), walks the page's top-level "units" (each `--unit-selector`
match), **projects a slide face** (visual-first; excess prose → speaker notes),
and decides — per unit — whether it fits on one slide or must be split.
It then writes one PNG per slide, a contact sheet for approval, and finally a
`.pptx` and `.pdf`.

## Fixed title bar (PowerPoint-master style)

The heading is pulled OUT of the flowing content into a pinned top zone — same
Y and same font size on EVERY content slide, like a PowerPoint master. Only the
content below it (figure / table / lead) is scaled to fit; the title never moves
or resizes from slide to slide. On a split unit the `N / M` part label sits
top-right of that title bar.

**Fit equation (hard — never overflow):**

\[
s_{\mathrm{fit}}=\min\!\Big(1,\ \tfrac{H_c}{h},\ \tfrac{W_c}{w}\Big),\quad
s=\begin{cases}
s_{\mathrm{fit}} & h>H_c\\
\min(s_{\max},\,0.72\,H_c/h) & \text{visual, under-filled}\\
1 & \text{otherwise}
\end{cases}
\]

Readability floors (0.90 / 0.80) decide *whether to split*, never whether to
spill. Content is clipped in `#__fit` under the title; the title zone is
z-stacked with an opaque background so transforms cannot paint over it.
Content stays **top-aligned** under the title.

**Title page exception:** the first unit's first slide uses a PowerPoint title
layout — title + optional lead stacked and centered on the full canvas (no
pinned title bar). **Never a graphic, table, card, or figure on a title page.**
If the opener needs a visual, the title page stays text-only and the visual
lands on the next slide (master title bar), or under the next section header.
The same title-page layout may be reused as a **section header** before a
graphic-heavy unit — title alone (or title + one lead), then the chart/table.

## Layout contract: best-fit equation

The height budget alone prevents overflow. Composition fit prevents awkward
slides (sparse, text-walled, or chart-crushed-by-prose).

### Canvas (fixed)

| Zone | px | Role |
| --- | --- | --- |
| Slide | 1280 × 720 | 16:9 |
| Margin | 48 each side | breathing room |
| Title bar | 96 | pinned, never scaled |
| Content `Hc` | **528** | the only zone we pack |
| Content width `Wc` | 1184 | |

### Measure

For a candidate packing \(B\) (blocks on one slide face):

\[
\begin{aligned}
h &= \mathrm{measure}(B) \\
s &= \mathrm{clamp}(H_c / h,\ s_{min},\ 1) \\
\phi &= (s \cdot h) / H_c \\
V &= h_{\mathrm{visual}} / h \\
\tau &= 1 - V
\end{aligned}
\]

### Hard constraints (must pass)

| Constraint | Value | Meaning |
| --- | --- | --- |
| Prefer no scale | \(s \ge 0.90\) | split or strip before scaling; 0.80 only as last resort for a single unsplittable atomic block |
| Fill band | \(\phi \in [0.50,\ 0.92]\) | not sparse, not jammed |
| Visual primacy | if a visual exists, \(V \ge 0.55\) and prose share \(\tau_{\mathrm{prose}} \le 0.30\) | chart owns the slide |
| Face text | ≤2 sentences / prose block; ≤4 bullets; ≤12 words / bullet; ≤1 caption sentence | see Face rules |

If hard constraints fail → **evict prose to notes** and/or **split again**. Do not
ship a slide that only passes by \(s < 0.90\) when it still has multiple blocks.

### Soft score (pick among valid packings)

\[
\mathrm{score}(B) =
\mathbf{1}[s=1]
+ e^{-(\phi-0.72)^2 / (2 \cdot 0.12^2)}
+ 0.5\,V
- \mathrm{prose\_words}/40
\]

Maximize score; tie-break with the linear-partition DP (minimize tallest part,
then fewer slides). Sweet-spot fill is ~72% of `Hc` at scale 1.0.

### Recipe budgets (allowed shapes)

| Recipe | Visual share \(V\) | Text on face | Align |
| --- | --- | --- | --- |
| Hero chart | 0.70–0.85 | ≤1 caption sentence | center |
| Chart + bullets | 0.55–0.70 | ≤4 one-liners | center |
| Table | table owns zone | ≤1 lead sentence | center |
| Bignums | row + optional sparkline | labels only | center |
| Text-only | 0 | ≤55% of `Hc`, ≤4 bullets | **top** |
| Title + one idea | optional small visual | 1 sentence | top |
| **Title page** (first slide) | — | title + lead, **centered** on full canvas | center |

Anything outside these bands is rewritten (strip) or split — not scaled into place.

## Face rules (strip-to-notes, default on)

Source HTML may stay long-form for the web page. The deck path is a **projection**.

| On the slide face | Goes to speaker notes |
| --- | --- |
| Title | Any prose / callout block with >2 sentences **or** >40 words |
| One lead sentence (optional) | Remaining intro paragraphs |
| Figure / table / diagram + ≤1-sentence caption | Body paragraphs under figures |
| ≤4 bullets, each ≤1 sentence / ≤12 words | 5th+ bullets; multi-sentence or long bullets |
| Bignums / callout **one-liners** | Callout paragraph bodies |
| Part label `N / M` | Setup / verification narrative |

Default mode **enforces** these rules (strip automatically; full prose lands in
`notes_text`). `--keep-source` skips projection and only warns (debug the HTML).

After eviction, a slide whose face still exceeds ~60 words is flagged
`text_heavy` as a residual sanity check. Contact sheet / report mark slides
that had content stripped (`stripped: true`).

## The principle: measure, project, then split

1. **Measure.** Each unit is rendered alone and its true (unclipped) height is
   read from the DOM after fonts and images have loaded.
2. **Project face.** Classify blocks (`visual` / `table` / `caption` / `lead` /
   `prose` / `list` / `callout`); apply face rules; excess → speaker notes.
3. **Fit-or-split.** A projected unit within ~10% of the content budget stays
   whole. A genuinely taller unit is split.
4. **Split at safe boundaries, balanced.** Parts are cut only at child
   boundaries. Part count is amortized — a unit ~2x the budget makes 2 parts,
   not 3 — and blocks are distributed to minimize the tallest part (linear-
   partition DP), preferring higher composition score. The heading rides on
   every part.
5. **Never orphan a figure.** A figure (svg/img/figure/`.fig`) is welded to an
   adjacent caption or bignums row and treated as one atomic block.
6. **Scale only as last resort.** Prefer strip/split. Scale floor for ordinary
   packings is **0.90**; a single atomic overflow may go to 0.80 rather than
   clip unreadably.

What the contact sheet shows is what the `.pptx` contains — the same measuring
code feeds both.

## Usage

```bash
# 1. slice: measure + project face + decide + render slide PNGs + slice-report.json
python3 slice.py <src.html> --unit-selector section [--theme light|dark]
# debug without stripping prose off the face:
python3 slice.py <src.html> --keep-source

# 2. approve: open the contact sheet (thumbnail grid) a human can eyeball
python3 contact_sheet.py _out            # writes _out/contact-sheet.html

# 3. build: assemble the approved slides
python3 build.py _out --pptx --pdf       # writes _out/deck.pptx and _out/deck.pdf
```

Every run always writes `_out/slides/*.png`, `_out/slice-report.json`, and
(after step 2) `_out/contact-sheet.html`.

### `--theme light|dark` (default light)

The page already reads `data-theme` on its root, so before rendering, slice.py
stamps `document.documentElement.setAttribute('data-theme', theme)` and every
slide inherits the page's own light or dark tokens. **Interim (stopgap):** under
`--theme dark`, any chart that is still a baked light-background image is wrapped
in a soft neutral figure-plate card (rounded, subtle border) so it reads as an
intentional inset rather than a raw white rectangle. This goes away once charts
render natively from a dark palette; it is not the end state.

## Source types and the right `--unit-selector`

| Source | Typical structure | `--unit-selector` |
| --- | --- | --- |
| Benchmark walkthrough | hero + numbered `<section class="chapter">` | `section` |
| Written explainer | one `<section>` (or `<article>`) per idea | `section` or `article` |
| README rendered to HTML | flat headings, no sections | `h2` (or wrap content, then `section`) |

Pick the selector that matches the page's natural slide boundaries. If the page
has no sections, add them (or select on headings) so each match is one topic.

## Readability guarantees (enforced by tests)

`tests/test_slice.py` asserts, on a real render:

- every slide PNG is exactly **2560x1440** (16:9 at 2x device scale);
- every slide carries a **title**;
- a unit marked `fits=True` is **never split**;
- all parts of a split unit **share one title** and carry sequential
  `1/N … N/N` labels;
- the total slide count stays in a **sane, measure-driven band**;
- a **figure is never separated from its bignums**, and the block partitioner
  produces exactly N contiguous, balanced parts;
- the **title bar sits at an identical Y and height on every slide** (master-style);
- **`--theme dark` visibly darkens** the rendered slide background vs light;
- **face projection** moves >2-sentence / >40-word prose blocks off the face
  into notes (unless `--keep-source`);
- a **residual text-heavy** face (>60 words after projection) is flagged;
- a **text-only slide is top-aligned** while a slide with a visual stays centered;
- the **title page** (first unit, first slide) is **centered** like a PowerPoint
  title slide (no pinned title bar).

## Build notes

`build.py` sets each slide's real title (in the outline / accessibility tree)
and puts the unit's prose (plus any face-stripped text) in the **speaker notes**.
Slides are image-per-slide today. `TODO: native editable text boxes/shapes later.`

## External visual grader

`grade_slides.py` sends every slide PNG to **Gemini** (not the authoring
model) with a paid-PPT rubric and writes `_out/grade-report.json`. Target is
every slide ≥ 9. Re-run after each slicer change:

```bash
HTML2DECK_GRADER_MODEL=gemini-3.1-pro-preview python3 grade_slides.py _out-current
```

Screenshot-of-webpage decks typically ceiling in the mid-6s to high-7s until
charts/cards are laid out in a deck-native template (SVG text size and card
chrome are baked into the source HTML).

## Related
**Customers**
[[att]]

