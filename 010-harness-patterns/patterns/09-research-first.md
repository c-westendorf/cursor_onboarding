# P9: Research-First

## The Pattern

Before writing any code, search for existing solutions: packages, documentation,
and patterns in the current codebase. A skill enforces this order. A docs-lookup
agent fetches current documentation via llms.txt and web fetching.

## Why It Matters

Without a research-first discipline, Claude writes implementations from training
data — which may be outdated, incorrect, or reinventing something that already
exists in your codebase. With a search-first skill, every implementation starts
with a reconnaissance pass.

## Key Concepts

**llms.txt:** Many libraries publish a machine-readable documentation summary at
`/llms.txt` (e.g., `docs.react.dev/llms.txt`). The docs-lookup agent checks this
first — it's faster and more current than training data.

**The search-first skill:** A `/search-first` skill forces a "what exists?" pass
before any implementation work. It outputs a recommendation (Adopt/Extend/Build)
before touching any files.

**The docs-lookup agent:** A dedicated docs research agent with only `Read` and
`WebFetch` tools. It cannot touch the codebase — it only researches and reports.

## Example Files

→ `examples/skills/search-first/README.md` → copy as SKILL.md
→ `examples/agents/docs-lookup.md`

## VS Code Equivalent

Same files — skills and agents work identically in VS Code with the Claude extension.

## Implementation Notes

**For the search-first skill:**
- The key enforcement is: "Do not write a single line of code until the search
  is complete." Make this explicit in the skill file.
- Add a required output: "Before implementing, output: what you searched, what
  you found, and your recommendation."

**For llms.txt:**
- Check `[library-docs-domain]/llms.txt` for any library you're integrating
- If it exists, it's the best source — machine-readable, curated by the library maintainers
- If it doesn't, fall back to WebFetch of the actual docs pages

**For the docs-lookup agent:**
- Keep tool permissions minimal: `Read, WebFetch` only
- The agent should never touch project files
