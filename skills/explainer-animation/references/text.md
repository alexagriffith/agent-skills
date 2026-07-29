# On-screen text

Load when writing a prompt or fixing labels and captions.

## Fight invented words

Claude Design invents captions, restates headers, and pads scenes with filler.
Counter that in every prompt:

- Use only text listed in the prompt. End every scene with “Do not add any extra
  writing or labels beyond what is listed above.”
- Prefer fewer words. If the diagram carries the idea, leave the sentence band empty
  and say so (“sentence band unused, do not invent a caption”)
- Never invent marketing phrasing. Takeaways come from the source or the user

## Titles and headers

Concise but specific. Name the thing. Do not be vague.

## What goes under the header

**A point line is optional, not required.**

A header followed by a line that restates it is the most common bad pattern on these
frames Skip the point line unless it adds a condition,
number, or meaning the header does not already carry. When in doubt, omit it.

Worked example. Header “A vLLM Pod Serving Traffic” over point line “A vLLM pod takes
requests in and sends generated tokens back” fails, because the second line says nothing
the first did not. Either drop it, or give it the fact the header cannot carry, for example
“Each pod holds its own Key-Value cache.”

If present: exactly one line, no second restating line, no “Bridge:” caption.

## Compression rules

Keep these on every frame so the prompt stays short and readable.

- No em dashes and no colons. Commas, parentheses, or shorter phrasing
- No bare acronyms on first use in a scene (TB/s, GB/s, p90, p99 stay as written)
- Labels ≤3 words, noun phrases. If longer, the visual is doing too little
- Clear, not dumbed down. Precise term + brief explain when needed
- Positive first, then the boundary. Do not lead with a negation
- Subject first, number second. One heavy element per sentence
- No analogies, no hype, no absolutes
- No question marks or arrow glyphs in on-screen text
- Do not name colors in on-screen text

## Correctness

Ownership / containment claims (“X runs inside Y”) must be verified against the
project’s own docs. If a sentence resists clean wording, suspect the claim.

## Show, don’t tell

If it can be demonstrated visually, demonstrate it. Labels name what is already visible.
A structural claim gets a reveal (bracket / enclosure), not a sentence while the diagram
sits idle. Metrics: counters, gauges, bars, flowing dots — not paragraphs.

**Cold-viewer test (required before paste).** Cover every jargon label. Ask: would a
smart newcomer still know what domain this is in? Failure mode: two width-coded
rectangles that only make sense after you read “Long in / Long out.” That is telling
with stickers, not showing. Fix by drawing the mechanism first (e.g. prompt into a
model, reply coming out; work lighting up on the long side), then short labels.

**Labels are not the diagram.** Prefer fewer words *after* the picture carries the idea.
Short labels on an empty metaphor still fail. If the only difference between two
columns is which word is printed on which rectangle, rewrite the visual.

**Fight filler, not teaching.** “Do not invent captions” blocks marketing glue and
restated headers. It does not mean delete the stakes. If the claim has consequences
(latency, memory, cost, failure), those stakes belong in the spine and must appear as
shown beats. A tidy piece that never says why the claim matters has failed.
