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
2. **Content spine (required before any scene).** Write three lines, then check them:
   - **Claim** — the one sentence a viewer should leave with
   - **Stakes** — 2–4 concrete consequences if the claim is true (latency, memory, cost,
     routing, failure mode — whatever the source actually implies)
   - **Show plan** — which stake each scene will *demonstrate* (not restate)
   Fail this step if the spine is only a visual metaphor (“two bar lengths”) with no
   consequences. Short labels and clean bands cannot rescue a missing argument.
   “Fight invented words” forbids filler. It does **not** forbid teaching. If the source
   is thin, ask for the stakes or pull them from the cited docs — do not ship geometry
   with an empty lesson.
3. **Scenes** — prefer short (fewer scenes → fewer builder errors). Longer step-by-step
   or decision maps are fine when total duration reconciles.
   Each content scene advances one spine item: header · visual that proves it · optional
   sentence from source / spine wording.
   A line under the header is optional — omit unless it adds a condition or number the
   header does not already carry.
   Bookend with a static title card and a closing card that reviews beats
   (icon row + short labels, not a text list).
4. **Write** — follow the load table; fill `references/prompt-template.md`.
5. **Save** — write the prompt to a markdown file the user can keep. On request, copy
   the paste block to the clipboard (no frontmatter).

## Where it is built

- Open the design project that already has the user’s design system
- Always create a **NEW** canvas file. Never overwrite. Say so explicitly
- Match the **reference file’s** export contract (clock-driven video when available,
  16:9 1920×1080)
- Hold export until the user approves: “do not export, I will review first” on every
  iteration until they say it looks good

## Hard principles (always on)

- **Content spine before geometry.** Claim + stakes + show plan exist before scene layout.
  A piece that only rearranges shapes around a topic name has failed, even if bands and
  timing are perfect.
- **Headers name nouns, not vibes.** Concise and specific. No “both / shapes / it / this”
  without the things named in the header itself.
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
