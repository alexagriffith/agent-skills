# Agent Skills

Skills for Claude Code and other agents that follow the
[Agent Skills](https://agentskills.io/) layout: one folder per skill, with a
`SKILL.md` router and optional `references/` loaded on demand.

## Skills

| Skill | What it does |
|-------|----------------|
| [`explainer-animation`](./skills/explainer-animation/) | Structure-only prompts for Claude Design explainer animations. Layout, pacing, and on-screen text — never colors or fonts. Your design system owns style. |

## Install

Copy a skill folder into your agent skills directory:

```bash
# one skill (references required; examples optional)
cp -R skills/explainer-animation ~/.claude/skills/

# or into a project
cp -R skills/explainer-animation .claude/skills/
```

Keep `references/` next to `SKILL.md`.

If you use [skills.sh](https://skills.sh):

```bash
npx skills add alexagriffith/agent-skills
```

## Writing cleanup (STYLE-LAW, short list)

I use these four when cleaning on-screen copy or any prose that ships with an
animation. The skill already encodes the animation-specific bits; this is the
shared writing spine for a pass when wording still feels soft.

- **Clear, not simplified.** Keep the precise term. Explain it. Do not swap a
  real mechanism for a vibe word.
- **Positive first, then the boundary.** Say what it is / what it does before
  what it is not.
- **Subject first, number second.** One heavy element per sentence. Name the
  metric, then the subject, then the number.
- **No restating headers.** A line under a title must add a condition or a
  number the header does not already carry. Otherwise omit it. Prefer show over
  tell when the diagram can carry the idea.

## First version vs final

Same beat (“one GPU can’t hold a 100B model”), two passes.

**First version** — style and filler baked into the prompt (purple gradient,
restating subtitle, tip pill, invented marketing line, labeled step tracker,
Back / Pause / Next chrome):

![First version — pre-skill](./skills/explainer-animation/examples/before-after/before-pre-skill.png)

Source: [`before-pre-skill.html`](./skills/explainer-animation/examples/before-after/before-pre-skill.html)

**Final** — structure-only prompt + design tokens. Header alone (no restating
line). Diagram shows the mismatch. No labeled tracker. No playback chrome in
the frame:

![Final — skill pass](./skills/explainer-animation/examples/before-after/after-with-skill.png)

Source: [`after-with-skill.html`](./skills/explainer-animation/examples/before-after/after-with-skill.html)

**Shipped animation** from that same concept (exported video frame):

![Shipped GPU parallelism frame](./skills/explainer-animation/examples/before-after/shipped-gpu-parallelism.jpg)

Full video: [`02-gpu-parallelism.mp4`](./skills/explainer-animation/examples/02-gpu-parallelism.mp4)

## Examples (`explainer-animation`)

Short pieces made with a loaded design system + structure-only prompts.
Style comes from the design tokens in the Claude Design project, not from the
prompt. Source files live in
[`skills/explainer-animation/examples/`](./skills/explainer-animation/examples/).

| Piece | Preview | Video |
|-------|---------|-------|
| We're not there yet | [poster](./skills/explainer-animation/examples/01-were-not-there-yet.jpg) | [mp4](./skills/explainer-animation/examples/01-were-not-there-yet.mp4) |
| Running large models across GPUs | [poster](./skills/explainer-animation/examples/02-gpu-parallelism.jpg) | [mp4](./skills/explainer-animation/examples/02-gpu-parallelism.mp4) |
| Why agents fail in production | [poster](./skills/explainer-animation/examples/03-agents-in-production.jpg) | [mp4](./skills/explainer-animation/examples/03-agents-in-production.mp4) |

### We're not there yet

![We're not there yet](./skills/explainer-animation/examples/01-were-not-there-yet.jpg)

### Running large models across GPUs

![GPU parallelism](./skills/explainer-animation/examples/02-gpu-parallelism.jpg)

### Why agents fail in production

![Why agents fail in production](./skills/explainer-animation/examples/03-agents-in-production.jpg)

## Add another skill

1. Create `skills/<skill-name>/SKILL.md` (YAML frontmatter: `name`, `description`).
2. Put deep rules in `skills/<skill-name>/references/` — keep the router short.
3. Optional demos go in `skills/<skill-name>/examples/`.
4. Do **not** put a README inside the skill folder (repo README covers install).
5. List it in the table above.
6. Push.

## License

MIT. See [LICENSE](./LICENSE).
