---
name: suki-team-skill
description: >-
  SCAFFOLD (rename after the team picks its problem). Use when a Suki Mart
  manager asks <TRIGGER PHRASES, e.g. "morning restock brief", "which customers
  should we win back">. Chains the suki MCP tools over the Suki Mart sandbox
  (store.db, sandbox date 2026-09-30) and returns a fixed-format brief.
---

# Suki Team Skill (scaffold)

> LAYER 2 - the playbook. Folder name and `name:` above must match
> (lowercase, hyphens). Rename both together once the problem is chosen.
> Everything marked `<SLOT>` is team-specific and must be filled before the demo.

## When to use this skill

- <SLOT: trigger phrases. Keep identical to the prompt the desktop plugin button sends.>
- Asked by: <SLOT: branch manager / CSR lead / ops head>.

## Data rules (apply to every step)

Read `references/data-rules.md` in this skill folder first. Key points:

- "Today" is **2026-09-30** (`sandbox_now` 2026-09-30 21:00). Never use the real clock.
- Money is PHP, shown as ₱.
- Use enum strings exactly as listed in `data-rules.md`.
- Column names come from `data/SCHEMA.md`. Do not guess.
- Use only data returned by the suki MCP tools. No outside data, no invented rows.

## Tools this skill uses

Tools appear to Hermes as `mcp_suki_<tool>`.

| # | Tool | Purpose in this workflow | Status |
|---|---|---|---|
| 1 | `mcp_suki_describe_sandbox` | Only if the data model is unclear. | exists |
| 2 | `mcp_suki_list_branches` | Resolve a branch name to its code. | exists |
| 3 | `mcp_suki_<SLOT>` | <SLOT: gather> | to build |
| 4 | `mcp_suki_<SLOT>` | <SLOT: cross-check> | to build |
| 5 | `mcp_suki_<SLOT>` | <SLOT: optional write action> | to build |

The skill must chain at least tools 3 and 4. A one-tool skill does not meet the
hackathon's "multi-step workflow" bar.

## Procedure

1. Resolve scope. If branch or date range is missing, ask once. Branch codes
   come from `mcp_suki_list_branches`.
2. Call `mcp_suki_<SLOT>` to gather <SLOT>.
3. Call `mcp_suki_<SLOT>` to cross-check <SLOT>. Drop anything the check rules out.
4. Rank / decide using: <SLOT: thresholds and rules>.
5. If an action is warranted, state exactly what will change and **ask the user
   to confirm**. Only then call the write tool. Report rows affected.

## Output format

Fixed layout, so the desktop pane can render it:

1. **Headline:** one line with the single most important finding.
2. **Table:** `<SLOT: columns>`. Maximum 10 rows.
3. **Next actions:** at most 3, each with the data point that justifies it.
4. **Scope line:** branch, date range, and "as of 2026-09-30".

## Pitfalls

- Never recommend a reorder when a `pending`, `in_transit` or `partially_received`
  purchase order already exists for that branch and product.
- Never suggest delivery fixes for the two branches without delivery.
- Never include customers without marketing opt-in in outreach lists.
- Never write without explicit user confirmation.
- Never invent numbers. If a tool returns nothing, say so.
- Add team-found data quirks to `references/data-rules.md`.
