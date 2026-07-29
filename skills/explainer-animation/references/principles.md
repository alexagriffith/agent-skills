# Hard principles (solidified)

Load when writing or reviewing a prompt. These are pass/fail, not vibes.
Detail for layout/text/timing lives in the sibling reference files; this file is the spine.

## 1. Content spine before geometry

Before any scene layout, write:

1. **Claim** — one sentence the viewer should leave with
2. **Stakes** — 2–4 concrete consequences if the claim is true (latency, memory, cost,
   routing, failure mode — only what the source implies)
3. **Show plan** — which stake each scene will *demonstrate*

**Fail if** the spine is only a visual metaphor (“two bar lengths”, “boxes side by side”)
with no consequences. Clean bands and short labels cannot rescue a missing argument.

**Fight filler, not teaching.** “Do not invent captions” bans marketing glue and
restated headers. It does **not** mean delete the stakes. Thin source → ask, or pull
stakes from cited docs/lexicon. Do not ship geometry with an empty lesson.

## 2. Headers name nouns, not vibes

Headers are titles: concise **and** unambiguous.

- Name the concrete things on screen (prompt, reply, first token, KV cache).
- Ban bare referents used as the point: “both”, “shapes”, “it”, “this”, “they”,
  “the split”, “what changes”.
- **Fail:** “Latency splits across both” / “Same model, two shapes”
- **Pass:** “Input length sets first token” / “Long prompt or long reply”
- If the animation shows the verb, the header supplies the nouns. Specific beats clever.

## 3. Cold-viewer test

Mute every jargon label. A smart newcomer must still see *what system* this is
(e.g. a request into a model, not two abstract bars).

**Fail if** they would not know what the piece is about. Fix the visual. Do not add
a paragraph of labels.

## 4. Labels are not the diagram

Labels name what is already visible. They are stickers on a mechanism, not the mechanism.

**Fail if** stripping labels leaves only “wide vs narrow” or identical columns with
different words. Draw path, containment, fill, or motion first — then label.

Show, don’t tell: structural claims get a reveal; metrics get counters/gauges/fills;
a sentence is optional when the picture already carries the idea.

## 5. Highlight matches the box

Any shade, fill, underline, progress clip, or callout is owned by **one named segment**.

- Same left, width, top, height as that segment (state any inset, e.g. 2px).
- Asymmetric / composite bars: compute each column’s segments independently.
  Never reuse bar A’s “long region starts at X” for bar B when the long region moved.
- Under-labels center on the **same** width as the filled segment.

**Fail if** the fill stops short, overruns, or sits under the wrong block.

## 6. Title card = title + simple static visual

- Static at 0:00. Every mark already drawn. Nothing animates in.
- Standalone: one title text run + a small through-line diagram below it.
- Series: Episode id (own line, visibly smaller) + title + same simple diagram.
- No subtitle, series name, or paragraph on the title card.
- Closing card: same title framing + short visual review of the beats.

## 7. Form still matters (do not drop these)

- Never invent style (colors, fonts, named design systems) — use project tokens
- Scaffold ~1.0–1.5s; interaction beats get the time; every content scene has one
- Only listed on-screen text; empty bands stated when unused
- Max element types stated per scene; count matches the list; no “X or Y” choices
- `Timing:` line per scene; scene sum + gaps = stated total
- No labeled step tracker; unlabeled dots only if content scenes > 4
- No interactive playback chrome in the export
- Ownership/containment claims verified against source docs

## Teaching test (final gate)

After the draft exists, answer yes to all three or rewrite:

1. Can a cold viewer state the **claim** after watching?
2. Did each scene advance a **stake**, not only rearrange shapes?
3. Would the piece still make sense with jargon labels covered?

Geometry-only passes of the form checklist are still **fails**.
