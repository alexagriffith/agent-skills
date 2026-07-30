---
name: explainer-animation
description: >
  Generate structured animation prompts for Claude Design. Structure, layout, box
  formatting, pacing, and on-screen text only — never colors, fonts, or styling.
  The user's uploaded design system owns all visual style. Use when asked for a
  Claude Design prompt, animation for a concept, explainer video prompt, or to
  visualize a technical idea.
---

# Explainer Animation Prompt Generator

Produces a paste-ready prompt for Claude Design (or a similar design canvas).

**Always follow the style tokens already loaded in the design project.**  
The prompt owns structure, layout, boxes, motion, and text. Never invent a palette,
never name a design-system project, never specify colors, fonts, or CSS.

## Load only what you need

| Task | Read |
|------|------|
| Write a new prompt | this file → `references/principles.md` → `layout.md` → `pacing.md` → `text.md` → `prompt-template.md` |
| Fix teaching / empty lesson / vague headers | `references/principles.md` + `references/text.md` |
| Fix layout / overlaps / arrows / fills | `references/layout.md` |
| Fix timing / reveals / interaction | `references/pacing.md` |
| Fix on-screen wording | `references/text.md` |
| Review before paste | `references/review.md` + `references/principles.md` (+ the prompt file) |

Do not load every reference for a one-line fix.

## Absolute: never style

Forbidden in the prompt: color names, hex codes, palettes, fonts, backgrounds,
borders, shadows, CSS, or a named design-system / template.

Required instead: match the reference file’s export contract; use the design system
already in this project for colors, fonts, and components.

Layout geometry (bands, gaps, box sizing from labels) is formatting — keep it.

## Process

1. **Have an idea** — a claim worth teaching (doc, paste, or verbal). Pull claim + stakes
   before any geometry (`references/principles.md`).
2. **Invoke this skill** — it writes a paste-ready Claude Design prompt (structure,
   layout, motion, on-screen text only — never colors or fonts).
3. **Paste into Claude Design** — project already has your design system / template.
   Always create a **NEW** canvas file. Match the reference file’s export contract.
   Do not export until you say it looks good.
4. **Iterate on the live render** — hope for something that works in under five passes.
   Not a guarantee. Batch fixes; scrub transitions; keep the tab focused on export.

When writing the prompt, follow the load table → `references/prompt-template.md`, then
the teaching test in `references/principles.md` before paste.

## Hard principles (always on)

Full text: `references/principles.md`. Short list:

1. Content spine before geometry (claim + stakes + show plan)
2. Titles and headers: concise but specific — name the thing, do not be vague
3. Cold-viewer test (mute jargon; domain still obvious)
4. Labels are not the diagram (mechanism first)
5. Diagram + motion fit the claim (travel / flow / settle+interact — choose, don’t default)
6. Highlight matches the box (exact segment geometry)
7. Title card = title + simple static through-line diagram
8. Form still matters (no invented style, timing, listed text only, no labeled tracker)

**Teaching test:** cold viewer can state the claim; each scene advances a stake;
jargon-covered picture still makes sense. Geometry-only form passes are fails.

## Iterate

Step 4 above. Batch change requests. Scrub transitions (ghost cards, detached
arrowheads, text over lines, frozen tails, fills that miss their box).

## Keeping this current

Edit the smallest reference that owns the rule. Solidified teaching/clarity rules live
in `references/principles.md`. Keep this router short.
