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
