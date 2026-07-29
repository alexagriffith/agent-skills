---
name: visual-style-laws
description: >
  Rules for visual output — HTML explainers, walkthroughs, slide decks, data-viz.
  Governs headings, wording, tables, boxes, and theming so pages read clean and
  consistent. Use when building or reviewing any visual page, deck, or chart.
---

# Visual style laws

Rules for anything visual (walkthrough HTML, slides, interactive explainers,
data-viz). Prose voice lives in the voice guide; this governs the visual layer.

**Principles, not templates.** Examples illustrate a rule, they are not the only
right phrasing. Apply the principle in the author's voice — don't pattern-match
the example.

## 1. Headings name the subject, plainly

A heading names what the section IS — the concept or the move — in the fewest
plain words. It reads like a nav label. It does not moralize: no "don't", no
"before you trust X", no problem framing that makes the reader parse a warning
before they learn the topic.

- Good: "Establish baseline", "Find the operating point", "Verify".
- Wrong, same sections: "Check the cluster before trusting any prior number",
  "Sweep to the knee, don't guess it", "One run is not a result".
- **Test:** could it be a tab label, and does it say the topic, not the pitfall?

## 2. Page-topic lines command; feature verbs come from the source

The hero line introducing a page is a command or a question, never a limp verb.
"Measuring flow control under pressure" — not "Flow control keeps…", "…lets…".
When you say what a feature does, use the verb its own docs use ("flow control
**enables** intelligent request queuing"), not a softer invented one.

## 3. Name a real contrast; never the rhetorical not-Y

If a section is genuinely a two-sided comparison, name it ("Separation vs SLO").
Banned everywhere — headings, labels, sentences — is the not-Y flourish: "it's
not just A, it's B", "what it is and what it is not". State the thing.

## 4. No eyebrow kickers

No small uppercase kicker above a heading — no "SECTION · LABEL", no numbered
"① STEP NAME", no per-slide tag. The heading leads. A kicker is a second type
level repeating the title; if you want one for orientation, fix the title.

## 5. Visuals carry the evidence, not paragraphs

A visual unit is **title + one takeaway line (≤ 15 words) + the visual**. The
chart or number cards carry the evidence. Longer explanation goes to notes or a
collapsible, never the face — a paragraph on a visual unit is a blog.

- **Prose is complete sentences; structure enumerates.** A comma-strung
  verbless fragment ("Four scenarios, gate on and off, three repeats. 72 runs.")
  is slide-speak. The table or diagram enumerates the dimensions; the lead says
  the purpose or the conclusion — and never restates what the visual directly
  below already shows.
- **Technical detail goes in a table, not prose.** Configs, sweep points, and
  per-tier numbers read better as a small table. Takeaway in one line, values in
  the table.
- **One "what we learned" callout, once.** A walkthrough earns exactly one place
  to name where a measurement misled us and which metrics guard against it — a
  single callout framed as a checklist, not a confessional, not spread around.

## 6. Say the plain word, not the jargon

Use the term a reader already knows. Cut a fancier word that doesn't earn its
place: "throughput", not "goodput". Label metrics plainly on the face; keep the
exact metric id for the table or the docs.

## 7. Charts and pages honor the theme

Keep light and dark. A chart MATCHES the active theme — dark chart on a dark
slide, light on light — it never floats as a white plate on a dark page (that
reads as unfinished). Charts read the design system's light/dark token ramps;
one theme flag flows through page, slides, and charts.

## 8. Tables: tight, consistent, centered

A key/value table is two columns, densely padded, with a center divider, both
columns aligned the same way (left), and centered on the page. It should not
sprawl. Use one compact table style across a page so every table matches.

## 9. Fixed title level on slides

Every slide's title sits at the same position and size, like a PowerPoint master
— a pinned title zone, content in a box below. Titles never float or scale with
content.
