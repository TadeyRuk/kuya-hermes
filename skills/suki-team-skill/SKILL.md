---
name: suki-team-skill
description: >-
  TEMPLATE — replace this line. One or two sentences telling Hermes WHEN to use
  this skill, e.g. "Use when a Suki Mart branch manager asks for a morning
  restock brief or which products to transfer between branches."
---

# Suki Team Skill (template)

> **LAYER 2 — SKILL (the playbook).** A skill is a markdown procedure Hermes
> loads on demand. It teaches the agent *how* to chain your MCP tools into a
> real multi-step workflow. Rename the folder and the `name:` field to your
> team's skill name (lowercase, hyphens) — they must match.

## When to use this skill

- Trigger phrases or situations, e.g. "morning brief", "what should I restock",
  "which customers should we win back".
- Who is asking (branch manager? CSR lead? ops head?) and what they need.

## Tools this skill uses

List the MCP tools from **your** server (they appear to Hermes as
`mcp_<server>_<tool>`), and what each one is for in this workflow:

1. `mcp_suki_describe_sandbox` — only if the data model is unclear.
2. `mcp_suki_<your_tool>` — ...
3. `mcp_suki_<your_tool>` — ...

## Procedure

1. Clarify the scope if missing (which branch? what date range?). The sandbox's
   "today" is **2026-09-30** — use it for "this week", "last 30 days", etc.
2. Call `<tool>` to gather ...
3. Call `<tool>` to check ...
4. Decide / rank / recommend using these rules: ...
5. (Optional) Take an action with a write tool, and confirm with the user first.

## Output format

Describe exactly how the answer should look, e.g.:

- A one-line headline with the single most important finding.
- A table: `branch | product | on hand | days of cover | suggested action`.
- Max 3 recommended next actions, each with a reason from the data.

## Pitfalls

- Things the agent should NOT do (e.g. don't recommend reordering an item that
  already has a pending purchase order).
- Data quirks your team discovered (duplicates, missing values, ...).
