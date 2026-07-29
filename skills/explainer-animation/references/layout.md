# Box and layout formatting

Load when writing a prompt or fixing overlaps, arrows, spacing, or scene density.

## Boxes

- Pixel-aligned on a grid. No overlapping elements
- Group related elements: equal widths, even gaps
- Size from text: longest label width + 48px padding. Never size the box first
- Text inside a box never wraps and is never shrunk — widen the box
- Internal state is drawn (cache region, queue cells, meter fill). An empty labelled
  rectangle is a placeholder, not a diagram
- Max 3 element groups stacked per column; split scenes rather than cram
- Side-by-side columns: clear gutter, balanced visual weight

## Arrows and labels

- Arrows start at the exact border of the source and end at the exact border of the target
- Prefer straight lines with 90° turns. Arrowheads joined to shafts; diagonals auto-orient
- Labels on or immediately below their element — no floating labels
- Text never overlaps a drawing, arrow, or other text
- Label above/below a box: ≥24px clear. Beside: ≥32px clear
- Arrow labels at the midpoint on an opaque design-system pill so the stroke does not
  read through the text

## Spatial language

- Use “left of,” “below,” “centered between,” “stacked vertically”
- Never bare “next to” or “near”
- Spanning elements need anchor points (top of X to bottom of Y)
- State a maximum number of element types per scene. Uniform grids of same-sized boxes
  count as one type. Every element in the animation order must already appear in the
  scene description. The number must equal the length of its parenthetical list
- Never offer the builder a choice (“bracket or bar”) — specify exactly one visual

## Canvas bands

No step tracker (normal case), top→bottom:

| Band | Height |
|------|--------|
| Top margin | 40px |
| Header | 120px |
| Optional line under header | 90px (leave empty if unused — do not invent a caption) |
| Diagram | 640px |
| Sentence | 130px (leave empty if unused) |
| Bottom margin | 60px |

With unlabeled dots (only when content scenes > 4): diagram 550px + tracker 90px.
Usable width 1760px after 80px side margins. Nothing crosses band boundaries. Never put
beat-name labels in the tracker band.

## Gaps and scene clears

- Two boxes side by side: ≥120px clear (connectors and labels fit inside)
- Token sequences may use a tighter gap (e.g. 16px) — state that exception in the scene
- Clear the previous scene fully before the next. Seek every boundary frame
- Closing-card text must never print on top of a live scene

## Decision maps

- One decision box, Yes/No stubs, two outcome boxes side by side
- Chart does **not** accumulate across scenes
- Outcome boxes ≤6 words
- Condition is a phrase, not a question
