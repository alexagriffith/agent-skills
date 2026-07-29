# Motion and pacing

Load when writing a prompt or fixing reveals, timing, or dead air.

## Core rule

**Structure arrives fast. Interaction gets the time.**

- Land the whole scaffold (boxes, arrows, labels) in ~1.0–1.5s as one or two grouped
  reveals. Do not stagger one reveal per box
- Reserve stroke-travel drawing for moments where drawing *is* the point (boundary,
  first connection, grouping bracket). Elsewhere boxes appear crisp with contents in them
- Every content scene needs at least one **interaction beat**: motion between elements
  that already exist (request along an arrow, queue filling, bar crossing a threshold,
  cache hit lighting up). Named step, named duration. A scene that is only reveals is a
  captioned diagram — merge or cut

## Focus

- Announce in place; do not glide captions across the canvas
- Header scale-pop **only** when something else shares the frame. Alone → draw in place
- New elements emphasize then settle to the default stroke (design system). Existing
  elements stay at full strength by default. Dim only when the old element competes with
  the new one, and say why. No reflexive dimming
- One focus per beat (single element or a group highlighted as one idea)
- Moving objects: moderate readable speed — not frozen, not frantic

## Progress chrome

- **Never a labeled tracker.** Beat names do not live in a bottom rail. The closing
  summary card reviews the beats (miniatures + short labels).
- **Unlabeled dots only when content scenes > 4** (i.e. 5 or more technical scenes).
  Four or fewer: no tracker at all.
- Playback controls must not appear in the exported video. Quiet design-system progress
  chrome without Back / Pause / Next is fine.

## Timing formula

```
scene_time = header(0.5s) + optional_point_line(0 or 1.0s) + scaffold(1.0–1.5s)
             + sum(interaction beats) + read_hold
```

| Term | Value |
|------|--------|
| optional_point_line | 0s if omitted (preferred default); 1.0s if present |
| read_hold (visual-only / empty sentence band) | 1.5s |
| read_hold (one sentence) | 3.0s |
| read_hold (two sentences) | 3.5s |
| Title card | 3.0s static |
| Closing card | 2.5s (or ~6s if dense icon synthesis) |
| Scene gap | 0.3s |
| Visual-only scene target | 6–8s |
| Text scene target | 10–15s |

Put a `Timing:` line after each scene’s animation order. Sum scenes + gaps into
“Target total duration.” The stated total must match the arithmetic.

No frozen tail — set duration to true content end.
