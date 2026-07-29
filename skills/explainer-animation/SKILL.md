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

1. **Source** — read the doc, path, or paste. If verbal only, ask: audience, main point,
   rough scene count, source material?
2. **Content spine** — claim + 2–4 stakes + show plan. Required before any scene.
   Detail and failure modes: `references/principles.md` § 1.
3. **Scenes** — each scene advances one spine item: header · visual that proves it ·
   optional sentence from source / spine wording. Prefer short. Bookend with a static
   title card (title + simple diagram) and a closing card that reviews beats.
4. **Write** — follow the load table; fill `references/prompt-template.md`.
5. **Gate** — run the teaching test in `references/principles.md` before paste.
6. **Save** — write the prompt to a markdown file the user can keep. On request, copy
   the paste block to the clipboard (no frontmatter).

## Where it is built

- Open the design project that already has the user’s design system
- Always create a **NEW** canvas file. Never overwrite. Say so explicitly
- Match the **reference file’s** export contract (clock-driven video when available,
  16:9 1920×1080)
- Hold export until the user approves: “do not export, I will review first” on every
  iteration until they say it looks good

## Hard principles (always on)

Full text: `references/principles.md`. Short list:

1. Content spine before geometry (claim + stakes + show plan)
2. Titles and headers: concise but specific — name the thing, do not be vague
3. Cold-viewer test (mute jargon; domain still obvious)
4. Labels are not the diagram (mechanism first)
5. Highlight matches the box (exact segment geometry)
6. Title card = title + simple static through-line diagram
7. Form still matters (no invented style, timing, listed text only, no labeled tracker)

**Teaching test:** cold viewer can state the claim; each scene advances a stake;
jargon-covered picture still makes sense. Geometry-only form passes are fails.

## Iterate

Strong first version, then react to the live render. Batch change requests. Scrub
transitions (ghost cards, detached arrowheads, text over lines, frozen tails, fills
that miss their box). Keep the tab focused while exporting video.

## Keeping this current

Edit the smallest reference that owns the rule. Solidified teaching/clarity rules live
in `references/principles.md`. Keep this router short.
