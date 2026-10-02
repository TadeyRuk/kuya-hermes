# Mechanics & Judging

## How the hackathon works

| | |
|---|---|
| **Teams** | 6 teams · 5 developers each |
| **Build time** | 45–60 minutes |
| **Demo** | 5 minutes per team, live from your laptop |
| **Track** | Business Operations or Customer Experience (Open Innovation may also be considered) |

**The challenge:** build all three layers on the Suki Mart sandbox — and connect them.

1. **MCP server — the hands.** Wrap the sandbox in domain-specific tools.
2. **Skill — the playbook.** Teach Hermes a multi-step workflow using your tools.
3. **Desktop plugin — the face.** A pane or command in Hermes Desktop that runs it.

**Setup:** your own laptop with Hermes Desktop running locally, your own model provider, and this repo.

**Demo:** build freeze at the call — stop coding. Then 5 minutes: **problem → how Hermes is used → working output.** The clock starts when the mic starts.

## Scoring — 100 points

| # | Criterion | Points | What judges look for |
|---|---|---:|---|
| 1 | **MCP Server** (Layer 1) | 20 | Tools run correctly on the sandbox and are domain-specific — not a generic `run_sql` passthrough. |
| 2 | **Skill** (Layer 2) | 20 | Chains MCP tools into a real multi-step workflow that triggers reliably from a natural prompt. |
| 3 | **Desktop Plugin GUI** (Layer 3) | 20 | Works inside Hermes Desktop, is usable, and looks native — not bolted on. |
| 4 | **End-to-End Integration** | 10 | GUI action → skill → MCP → real data back in the GUI. |
| 5 | **Relevance** | 15 | Solves an actual problem in the data for Business Operations or Customer Experience. |
| 6 | **Uniqueness** | 10 | An original idea — not a copy of another team or an existing Hermes plugin. |
| 7 | **Demo & Pitch** | 5 | Clear problem → solution → live proof within the 5-minute limit. |
| | **Total** | **100** | |

### Scoring guide for the 20-point layers

| Score | Meaning |
|---|---|
| 0 | Not built |
| 1–7 | Started, not working |
| 8–14 | Works |
| 15–20 | Works well, thoughtful design |

### Tie-breaker

1. Higher **Integration** score
2. Higher **Relevance** score

## House rules

- Build on the Suki Mart sandbox data (`data/store.db`).
- Write your own MCP — catalog MCPs (Neon, Supabase, …) or existing plugins don't count as your team's build.
- AI-assisted coding is allowed and encouraged — the idea and the integration are judged.
- Broke your data? `python data/seed.py` restores it.
