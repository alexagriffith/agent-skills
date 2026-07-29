# Prompt template

Load when writing or rewriting a full paste block. Fill brackets. **No color or font
words anywhere.**

```
Create a NEW file in this project named "<Title>.dc.html". Do NOT modify the other files.
Match the reference file's export contract exactly: clock-driven EXPORTABLE video
(Share > Export > Video, seek/export frame-accurate), 16:9 1920x1080. Always follow
the style tokens already loaded in this project for colors, fonts, and components.
Do not invent a palette or name a design system. Concise on-screen text. Icons where a
label is enough; a real diagram plus one plain-English sentence where a concept needs
explaining. NO em dashes and NO colons. Playback controls hidden in the exported video.
Quiet progress chrome from the design system is fine; do not draw Back, Pause, Next, or
a labeled scrubber.

Title card contract (both bookends):
- STATIC. Every mark drawn in frame one. Nothing animates, fades, or types in.
  Thumbnail at 0:00 shows the finished card.
- Series piece: "Chapter <N>" centered on its own line, title centered below. No subtitle,
  series name, tagline, or decorative marks.
- Standalone piece: ONE text run, the title alone. Do not invent a chapter number.
- Closing card: same framing, plus a short visual review of the beats walked through.

Emphasis and focus:
- Header scale-pop ONLY when something else shares the frame; otherwise draw in place.
- New elements emphasize then settle to the default stroke. Existing elements stay at
  full strength unless they compete with the new focus (name why if dimming).
- Group elements that are one idea into a single highlight beat.

Progress:
- Never a labeled step tracker. The closing summary card reviews the beats.
- Four or fewer content scenes: NO tracker of any kind.
- More than four content scenes: small unlabeled dots at the bottom only.

Pacing:
- Scaffold lands in 1.0–1.5s as one grouped block. Interaction beats get the time.
- Every content scene has at least one named interaction beat with its own duration.
- Boxes carry their contents. Empty labelled rectangles are not diagrams.
- Visual-only scenes 6–8s. Text scenes 10–15s. Title 3.0s. Closing 2.5s. Gaps 0.3s.

Layout rules (text must never overlap a box, arrow, or other text):
- Bands top→bottom: 40px margin, header 120px, optional line under header 90px
  (leave empty if unused), diagram 640px (550px if tracker), sentence 130px
  (leave empty if unused), tracker 90px if any, 60px margin. Width 1760px usable.
  Nothing crosses bands.
- Size boxes from longest label + 48px padding. No wrap, no shrink-to-fit.
- Side-by-side gap ≥120px unless this scene states a tighter token-sequence exception.
- Labels anchored to one element. Arrow labels at midpoint on an opaque pill.
- Clear each scene fully before the next. Check every boundary frame.

Text rules:
- Do not invent captions. Use only text listed in this prompt.
- Line under the header is optional. Omit unless it adds a condition or number the
  header does not already carry. Never restate the header.
- Sentence below the diagram only if the picture cannot carry the meaning. Otherwise
  leave the sentence band empty and say so.
- Expand acronyms on first on-screen use. No question marks or arrow glyphs in text.
- Do not name colors anywhere in on-screen text or in this prompt body.

CONTENT, title "<Title>". One through-line.
1) Static title card.
2) <Beat> ...
N) Closing card with beat review.

Per scene: Maximum N element types (...); animation order; Timing: <arithmetic>.
Do not add any extra writing or labels beyond what is listed.
Do not change any other files or scenes.

Update duration to the true content end (no frozen tail).
Verify alignment and no text/stroke overlap. Do NOT export; I will review first.
```
