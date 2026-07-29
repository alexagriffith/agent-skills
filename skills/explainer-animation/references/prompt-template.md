# Prompt template

Load when writing or rewriting a full paste block. Fill brackets. **No color or font
words anywhere.**

```
Create a NEW file in this project named "<Title>.dc.html". Do NOT modify the other files.
Match the reference file's export contract exactly: clock-driven EXPORTABLE video
(Share > Export > Video, seek/export frame-accurate), 16:9 1920x1080. Always follow
the style tokens already loaded in this project for colors, fonts, and components.
Do not invent a palette or name a design system. Concise on-screen text. Icons where a label is enough; a real
diagram plus one plain-English sentence where a concept needs explaining. NO em dashes
and NO colons. Playback controls hidden in the exported video. Quiet progress chrome from
the design system is fine; do not draw Back, Pause, Next, or a labeled scrubber.

Title card contract (both bookends):
- STATIC. Every mark drawn in frame one. Nothing animates, fades, or types in.
  Thumbnail at 0:00 shows the finished card.
- Series / numbered piece text: identifier + title only.
  1) Series identifier on its OWN centered line above the title
     ("Episode <N>" or "Episode A1" — use the series' own word; do not invent one).
  2) Title centered on the line directly below it.
  The identifier is visibly smaller than the title (design-system secondary / caption
  scale). Never the same size as the title, never larger. At least 24px clear between
  the identifier's bottom edge and the title's top edge.
  No subtitle, series name, tagline, or comma-joined id ("A-1").
- Standalone piece: ONE title text run. Do not invent an episode number.
- **Always a simple static diagram on the title card**, already fully drawn at 0:00,
  below the title. It previews the through-line in one glance (mini architecture or the
  key comparison — not a pile of unlabeled vibes). Not a full scene, not a paragraph.
- Closing card: same title framing (identifier + title if series), plus a short visual
  review of the beats walked through.

Box style (state this in every prompt, it is not inherited reliably):
- Every box is a normal, solid, placed box. Rounded rectangle, flat opaque fill from the
  style tokens, ONE clean stroke of uniform weight, at least 2px, consistent on all four
  sides.
- Forbidden: sketch or hand-drawn effect, wobbling or jittered outlines, doubled or offset
  outlines, dashed or dotted or broken strokes, hairline 1px outlines, transparent fills
  that show the background, open corners.
- Boxes must look placed, not drawn by hand. Apply to outer boxes, nested boxes and every
  box-shaped mark, so the whole piece reads as one set of components.

DIAGRAM KIND (choose before motion):
- Match the visual to the claim. Technical topology → architectural diagram (components,
  connectors, interiors). Quantity change → meters/fills. Do not default to labeled
  rectangles sliding in as the whole lesson.
- Interaction happens inside that diagram. Furniture rearranging is not enough.

THE MOTION LAW (for things that actually move — traffic, fills, counters):
- Traffic (request, token, job) moves as a small unlabeled solid along a path. It never
  materialises at the end. It is not a labeled box (see DO NOT BOX OR LABEL TRAFFIC).
- Quantity changes are watchable across their beat (fill, grow, climb).
- FORBIDDEN for moving traffic: popping in, fading up, scaling in, stroke-by-stroke draw,
  halo or pulse on arrival.
- Architecture scaffold lands as one grouped settle in 1.0–1.5s. Do not introduce every
  component by sliding it in from off frame as its own beat.

Emphasis and focus:
- Header scale-pop ONLY when something else shares the frame; otherwise draw in place.
- New elements emphasize then settle to the default stroke. Existing elements stay at
  full strength unless they compete with the new focus (name why if dimming).
- Group elements that are one idea into a single highlight beat.
- Any shade or fill uses the exact left, width, top, and height of its named target
  segment. Asymmetric composites: compute each column’s segments independently.
- Cold-viewer test before shipping a scene: mute jargon labels; the diagram must still
  show the domain and the mechanism. Labels name what is visible; they are not the diagram.

Progress:
- Never a labeled step tracker. The closing summary card reviews the beats.
- Four or fewer content scenes: NO tracker of any kind.
- More than four content scenes: small unlabeled dots at the bottom only.

Pacing:
- Scaffold lands in 1.0–1.5s as one grouped block. Interaction beats get the time.
- Every content scene has at least one named interaction beat with its own duration.
- A QUANTITY THAT CHANGES MUST BE WATCHABLE. A bar that fills, a counter that climbs, a
  needle that swings, a cache that populates: the change is spread linearly and legibly
  across its whole beat. No instant jump to the end state, and no ease so steep it is
  visually instant. If the viewer cannot watch it move, the beat bought nothing and the
  seconds were wasted.
- CONNECTORS ROUTE AROUND, NOT THROUGH. A loop or return arrow travels the outside of the
  composition, back around the diagram, never straight down or across the middle of the
  frame. An arrow cutting through the center of a composition is a defect.
- Titles and headers: concise but specific. Name the thing. Do not be vague.
- Boxes carry their contents. Empty labelled rectangles are not diagrams.
- DO NOT BOX OR LABEL TRAFFIC. A request, a token, a message, a job: draw it as a small
  solid filled circle, roughly 28px, no label, no outline flourish. The viewer already
  knows what a moving thing entering a system is; labelling it adds nothing and litters the
  frame with boxes that are not components. Rectangles with labels are reserved for actual
  named components whose names carry information.
- ARROW ALIGNMENT. Every connector runs along the exact shared center axis of the two boxes
  it joins. A horizontal connector sits at the precise vertical midpoint of both ends with
  no drift. Arrowheads terminate exactly at the destination box edge, never overlapping in
  and never stopping short. A travelling mark's center rides exactly on the connector line
  for the entire trip. Check this at the start, middle and end frame of every travel beat,
  not only at rest.
- Visual-only scenes 6–8s. Text scenes 10–15s. Title 3.0s. Closing 2.5s. Gaps 0.3s.

Layout rules (text must never overlap a box, arrow, or other text):
- Bands top→bottom: 40px margin, header 120px, point-line 90px (leave empty if unused),
  diagram 640px (550px if tracker), sentence 130px (leave empty if unused), tracker 90px
  if any, 60px margin. Width 1760px usable. Nothing crosses bands.
- Size boxes from longest label + 48px padding. No wrap, no shrink-to-fit.
- Side-by-side gap ≥120px unless this scene states a tighter token-sequence exception.
- Labels anchored to one element. Arrow labels at midpoint on an opaque pill.
- Clear each scene fully before the next. Check every boundary frame.
- FILL THE FRAME. The diagram group occupies at least 70% of the usable width and is
  centered on x 960, left and right margins equal to within 20px. A group using ~37% of the
  width with 500px dead on both shoulders is a defect, not a style. Do not leave the bottom
  of the diagram band empty; spread the content into it.
- A component that appears in more than one scene keeps the SAME interior in every scene.
  A pod that holds a cache in scene 2 and is an empty rectangle in scene 4 reads as two
  different objects. Scale it, never hollow it.

Text rules:
- Do not invent captions. Use only text listed in this prompt.
- DEFAULT TO NO POINT LINE. Absent is the correct state. A point line survives only if it
  carries a number or condition the header lacks AND the diagram cannot show it. If the
  diagram makes the point obvious, saying it as well is clutter, not reinforcement. Two
  cards of visibly different height beside two diverging counters do not need a line
  explaining that verbose costs more.
- Point line under the header is optional. Omit it unless it adds a condition or number
  the header does not already carry. Never restate the header. Read the header and the
  point line aloud as one sentence; if the second says nothing the first did not, cut it.
- SHOW, DO NOT TELL. For every point line and sentence, ask whether the diagram could make
  that claim on its own. If it could, the diagram must make it and the words are deleted.
  Text is a caption of last resort, never the delivery mechanism. A scene that states a
  fact in words while the diagram sits underneath as decoration has it backwards.
- Convert claims into mechanisms. "The pod fills up and requests queue" becomes drawn slots
  that fill one at a time until a request has nowhere to go and parks behind the pod, with
  more stacking behind it. "llm-d adds a layer" becomes one request taking the old direct
  path, then the new tiers appearing, then a second request visibly detouring through them,
  both routes on screen at once. A bracket that announces a claim is telling; a changed path
  the viewer watches is showing.
- Sentence below the diagram only if the picture cannot carry the meaning. Otherwise
  leave the sentence band empty and say so. A scene carrying no sentence needs only a 1.5s
  visual hold at the end, not 3.0s, so added motion partly pays for itself.
- One short line per idea. If the sentence band needs a compound sentence with "which" or
  two clauses joined by "and", split it into two or three short lines, center them, and
  reveal them one at a time on the beat each line describes. A reader should never meet a
  whole paragraph at once. Never dump the conclusion as one long line at the end.
- The diagram must depict every direction of motion the header claims. If the header says
  requests go in and tokens come back, the return path is drawn and animated, not implied.
  A one-directional diagram under a two-directional header is a defect.
- Name the concrete task on screen before showing the loop. A file name alone is not a use
  case. Say what the person asked the agent to do, then show the file that request touches.
- Show the actual thing, not a stand-in for it. If a scene argues that something is verbose,
  bloated, noisy or wrong, the viewer has to be able to SEE that in the frame. Abstract
  stacked rows standing in for code prove nothing. Render the real content, legibly, at
  22px or larger, and let the reader judge it. A generic placeholder interior is the same
  defect as an empty labelled rectangle.
- Rendered code samples are exempt from the no-colon rule, since code needs colons. The
  rule still binds every header, point line, label and sentence.
- Expand acronyms on first on-screen use. No question marks or arrow glyphs in text.
- Do not name colors anywhere in on-screen text or in this prompt body.
- PLAIN LANGUAGE, NO APHORISMS. Every line states a mechanism a newcomer can act on.
  If a line could appear on a motivational poster, it is wrong. "One pod has a ceiling and
  traffic finds it" is the failure mode: it sounds clever and explains nothing. The fix is
  to say what actually happens, e.g. "When every slot is busy, new requests wait in a queue
  instead of being served." Prefer a dull true sentence over a memorable empty one.
- A label on a bracket or annotation may not repeat a label already on the box beneath it.
  A bracket reading "Upstream gateway resources" over a box reading "Inference Gateway" is
  redundant; drop the bracket label and keep the bracket only if it still groups something.
- Do not let a proper noun in a title contradict corrected terminology inside the scenes.
  If the scenes say routing, the bookends may not say scheduling.
- NO ANTITHESIS CONSTRUCTIONS. Never write "this is X, not Y". "This is a mechanism, not a
  measurement" is the failure mode. The negated half is filler; the reader was never
  thinking Y. State the positive claim alone, or cut the line. The same ban covers "not
  about A, about B" and "less A, more B".
- TITLE CASE LOWERCASES SMALL WORDS. Articles, prepositions and conjunctions are lowercase
  unless they are the first word of the line. "Choosing a Pod", not "Choosing A Pod".
  "Inside One vLLM Pod" is correct because "One" is a numeral, not an article.
- A closing card may be a title plus miniatures with no sentence at all. Prefer that to a
  closing card carrying a line that only exists to fill the band.

- BIND EVERY SENTENCE LINE TO THE THING IT NAMES. When a line of the sentence band appears,
  the element that line is about must simultaneously emphasise: its outline thickens and
  comes forward, easing in over about 0.3s, and releases when the next line takes over.
  Nothing else is dimmed. A sentence that names the context window bar while nothing on
  screen responds is a defect; the viewer cannot tell which of six boxes the words are
  about. Text and visual are one beat, never two.

- DOTTED MEANS ASKING, SOLID MEANS TRAFFIC. A query, probe, score fetch, health check or
  any request for information travels on a DOTTED line, and that line disappears when the
  exchange is over because it was temporary. Actual traffic, a request being served or a
  token being returned, travels on a SOLID connector that persists. The two must be
  distinguishable at a glance. Drawing a score fetch the same way as a served request
  makes the scoring step illegible.

- A CONTAINER MUST CONTAIN. A box that represents something with an inside gets real
  labelled interior components, each a solid filled box visibly smaller than its parent and
  clearly nested within the parent outline, centred inside it with equal padding. A pod
  drawn as one large outline with a single word in it is the same defect as a bare labelled
  rectangle, only larger. Two or three named interior components is the working minimum.

- WARNING AND ALERT MARKS. When a scene needs to flag that something has gone wrong, draw a
  solid filled triangle with an exclamation mark inside it, roughly 72px tall, in the style
  tokens' alert colour. It slides into place from just off its resting spot over about 0.3s
  and then holds steady for the rest of the scene. It never pulses, blinks, glows or
  throbs, and it is never explained by added text. The mark is the explanation.

CONTENT SPINE (see references/principles.md). Write this above the scenes; omit from
the Claude Design paste only if every scene already proves a stake):
- Claim: <one sentence>
- Stakes: <2–4 consequences>
- Show plan: scene 1 → …; scene 2 → …; scene 3 → …

CONTENT, title "<Title>". One through-line that matches the claim.
1) Static title card.
2) <Beat> ...
N) Closing card with beat review.

Per scene: Maximum N element types (...); animation order; Timing: <arithmetic>.
Do not add any extra writing or labels beyond what is listed.
Do not change any other files or scenes.

Update duration to the true content end (no frozen tail).

SELF-AUDIT BEFORE YOU REPORT. Seek the middle frame and the last frame of EVERY scene
including both bookends, look at each one, and answer these seven for each scene from what
is actually rendered, not from what the code intends. Do not sample. Fix what fails, then
report the answers.
1. Read the header and the point line aloud as one sentence. Does the point line add a
   condition or a number the header lacks? If not, delete it.
2. List every box. Does each have a drawn interior, or is it a label floating in an empty
   rectangle? Empty rectangles are defects.
3. Is every box solid, uniform-stroked and placed, with no sketch, wobble, dash, doubling
   or hairline outline?
4. Does the diagram draw every motion, direction, rise or comparison the text promises?
   A promised traversal that is only a color pulse is a defect.
5. Does every recurring component keep the same interior it had in earlier scenes?
6. Report the diagram group's x span and its left and right margins. Under 70% of usable
   width, or margins differing by more than 20px, is a defect.
7. Does any line sound clever rather than mechanical? Rewrite it plainly.
Then confirm in one line that no bare labelled rectangle remains anywhere in the piece.

Verify alignment and no text/stroke overlap. Do NOT export; I will review first.
```
