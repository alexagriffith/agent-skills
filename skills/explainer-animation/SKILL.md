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
| Write a new prompt | this file → `references/layout.md` → `references/pacing.md` → `references/text.md` → `references/prompt-template.md` |
| Fix layout / overlaps / arrows | `references/layout.md` |
| Fix timing / reveals / interaction | `references/pacing.md` |
| Fix on-screen wording | `references/text.md` |
| Review before paste | `references/review.md` (+ the prompt file) |

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
2. **Scenes** — prefer short (fewer scenes → fewer builder errors). Longer step-by-step
   or decision maps are fine when total duration reconciles.
   Each content scene: header · visual · optional sentence from source wording.
   A line under the header is optional — omit unless it adds a condition or number the
   header does not already carry.
   Bookend with a static title card and a closing card that reviews beats
   (icon row + short labels, not a text list).
3. **Write** — follow the load table; fill `references/prompt-template.md`.
4. **Save** — write the prompt to a markdown file the user can keep. On request, copy
   the paste block to the clipboard (no frontmatter).

## Where it is built

- Open the design project that already has the user’s design system
- Always create a **NEW** canvas file. Never overwrite. Say so explicitly
- Match the **reference file’s** export contract (clock-driven video when available,
  16:9 1920×1080)
- Hold export until the user approves: “do not export, I will review first” on every
  iteration until they say it looks good

## Hard principles (always on)

- **Cold-viewer test.** Mute the jargon labels. A newcomer must still see *what system*
  this is (e.g. a request into a model, not two abstract bars). If they would not know
  what the piece is about, rewrite the visual — do not add more words.
- **Labels name what is already visible; they are not the diagram.** If stripping labels
  leaves shapes that only mean “wide vs narrow,” the scene is telling with stickers.
  Draw the mechanism (path, containment, fill, motion), then label it.
- **Highlight matches the box.** Any shade, fill, underline, or callout uses the exact
  left / width / top / height of its target segment. Asymmetric composites: compute each
  segment independently — never reuse one bar’s geometry for its sibling.
- Scaffold fast (~1.0–1.5s); interaction beats get the time; every content scene has one
- Fight invented words — only listed text; empty sentence band if the picture is enough
- Ownership / containment claims verified against the project’s own docs
- Max element types stated per scene; count matches the list; no “X or Y” visual choices
- `Timing:` line per scene; scene sum + gaps = stated total
- Title card static at 0:00 with title + simple through-line diagram; no playback chrome

## Iterate

Strong first version, then react to the live render. Batch change requests. Scrub
transitions (ghost cards, detached arrowheads, text over lines, frozen tails, **fills
that miss their box**). Keep the tab focused while exporting video.

## Keeping this current

Edit the smallest reference that owns the rule. Keep this router short.
