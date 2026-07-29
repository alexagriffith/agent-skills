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
# one skill
cp -R skills/explainer-animation ~/.claude/skills/

# or into a project
cp -R skills/explainer-animation .claude/skills/
```

Keep `references/` next to `SKILL.md`.

If you use [skills.sh](https://skills.sh):

```bash
npx skills add alexagriffith/agent-skills
```

## Add another skill

1. Create `skills/<skill-name>/SKILL.md` (YAML frontmatter: `name`, `description`).
2. Put deep rules in `skills/<skill-name>/references/` — keep the router short.
3. Do **not** put a README inside the skill folder (repo README covers install).
4. List it in the table above.
5. Push.

## License

MIT. See [LICENSE](./LICENSE).
