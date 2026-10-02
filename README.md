<p align="center"><img src="assets/kuya-hermes-fullbody.png" alt="Kuya Hermes mascot" width="220"></p>

# Kuya Hermes · Suki Mart branch-ops copilot

> **CAMP / RUN Hermes Agent hackathon · Track 3: Open Innovation**
> One Hermes agent on two surfaces: **HQ in Hermes Desktop** and **branch managers on Telegram**, sharing the same MCP tools and skill over the Suki Mart sandbox.

### 🔗 Links
| What | Link |
|---|---|
| 🌐 **Website** (landing page) | **https://kuya-hermes.vercel.app** |
| 📊 **Live dashboard** (snapshot of real Suki Mart data, Sep 30 2026) | https://kuya-hermes.vercel.app/dashboard |
| 🧢 **Live demo with real Hermes chat** (temporary tunnel, only while the team laptop is on) | https://packets-tract-streets-macintosh.trycloudflare.com: username **anything**, password **`suki-kuya-2026`** |
| 💬 **Telegram bot** (branch managers) | https://t.me/kuyahermes_bot |
| 💻 **Source code** | https://github.com/polsalarm/kuya-hermes |
| 🧰 **Hackathon starter kit** (upstream) | https://github.com/TadeyRuk/hermes |
| 📚 **Hermes Agent docs** | https://hermes-agent.nousresearch.com/docs |

> The Vercel site is a **static snapshot**: real numbers, pre-rendered from `store.db`. The live Kuya chat (the real Hermes agent) runs in the local demo (`uv run web/app.py`) and on Telegram. The Telegram bot and the live chat respond only while the team laptop is running the Hermes gateway.

**Problem.** Suki Mart's branches lose sales and goodwill for reasons nobody connects in time. In the sandbox (as of 2026-09-30):
- **47 items are out of stock**, and Ermita alone has 14 out of stock with no purchase order.
- **12 products have duplicate open purchase orders.** BGC's Calamansi Juice has 4 at once.
- Suppliers promise one lead time and deliver another: Visayas Canning promises 5 days and really takes **11.3**.
- Shift no-shows and sick calls leave blocks below staffing targets, with **46 support tickets never answered** on top.

**Solution.** Kuya Hermes turns that into one loop: **detect → check → propose → confirm → act**.

#### The three layers

| | Layer | Folder | What it does |
|:-:|---|---|---|
| 🔧 | **MCP server**: the hands | `mcp-server/` | 9 Suki Mart tools (listed below) |
| 📘 | **Skill**: the playbook | `skills/kuya-hermes-ops/` | Chains the tools into workflows and asks before every write |
| 🖥️ | **Desktop plugin**: the face | `desktop-plugin/kuya-hermes-hq/` | Kuya Hermes HQ page with **▶ Run full sweep** |
| 💬 | **Telegram**: bonus channel | Hermes gateway | Branch managers report from the floor in Taglish |
| 🌐 | **Website**: bonus | `web/` | Landing page and live dashboard |

#### MCP tools (`suki` server)

| Tool | What it answers | Type |
|---|---|:-:|
| `network_sweep` | Which of the 12 branches needs help most? | 👀 read |
| `branch_pulse` | How is this branch doing on stock, staff, tickets and deliveries? | 👀 read |
| `check_restock` | Should we reorder? Checks for open or **duplicate POs** and uses the supplier's **real** lead time | 👀 read |
| `create_purchase_order` | File a restock PO (refuses duplicates) | ✍️ write |
| `find_staff_shifts` | Find an absent person's upcoming shift | 👀 read |
| `find_shift_cover` | Who is the most reliable free colleague to cover? | 👀 read |
| `assign_cover` | Book the cover and mark the absence | ✍️ write |
| `list_branches` · `describe_sandbox` | Branch codes and the data model (from the starter kit) | 👀 read |

#### Skill workflows (`kuya-hermes-ops`)

| Workflow | Triggered by | Steps |
|---|---|---|
| **Full sweep** | ▶ Run full sweep | sweep → pulse of the worst branch → check restock → propose → ✅ confirm → write |
| **Branch pulse** | *"kumusta ang Alabang?"* | pulse → rank issues → next actions |
| **Fix stockouts** | *"ubos na ang bottled water sa ALB"* | check restock (skip open POs) → propose PO → ✅ confirm → create PO |
| **Cover absence** | *"di pumasok si John bukas, 7am"* | find shift → find cover → propose → ✅ confirm → assign |

**Flow:** HQ button / Telegram message / website chat → `kuya-hermes-ops` skill → `suki` MCP tools → `data/store.db` → answer, then a confirmed write → result back on screen.

### Run it (Windows)
```powershell
# MCP (absolute path)
hermes mcp add suki --command uv --args run C:\path\to\kuya-hermes\mcp-server\server.py
# Skill + plugin. On Windows the Hermes home is %LOCALAPPDATA%\hermes, not %USERPROFILE%\.hermes
xcopy /E /I skills\kuya-hermes-ops %LOCALAPPDATA%\hermes\skills\kuya-hermes-ops
xcopy /E /I desktop-plugin\kuya-hermes-hq %LOCALAPPDATA%\hermes\desktop-plugins\kuya-hermes-hq
copy persona-SOUL.md %LOCALAPPDATA%\hermes\SOUL.md   # optional: Kuya Hermes persona
hermes gateway restart
hermes desktop        # Ctrl+K → Reload desktop plugins → sidebar: Kuya Hermes HQ
```
Reset the data after a demo with `git checkout -- data/store.db`.

### Website (landing page + live dashboard with real Hermes chat)
```powershell
# 1. Turn on Hermes' local API server: add to %LOCALAPPDATA%\hermes\.env, then restart the gateway
#    API_SERVER_ENABLED=true
#    API_SERVER_KEY=<any long random string>
hermes gateway restart
# 2. Run the site
uv run web/app.py        # → http://localhost:8787  (dashboard: /dashboard)
```
- **`/`**: landing page. Its problem stats are pulled live from `store.db`.
- **`/dashboard`**: live KPIs, branch risk cards, and a click-through branch pulse, built with the same functions as the MCP server. The **Kuya chat** panel talks to the real Hermes agent (`kuya-hermes-ops` skill and `suki` tools) through Hermes' API server on `127.0.0.1:8642`. The key stays on the server and is never sent to the browser.
- Read-only by design: purchase orders and shift covers only happen through Kuya, after a yes.
- **Public tunnel demo** (optional): `$env:SITE_PASSWORD='…'; uv run web/app.py` adds a password, then run `cloudflared tunnel --url http://localhost:8787`. Before exposing it, lock the API-server agent to the suki tools: `hermes config set platform_toolsets.api_server '["mcp-suki"]'`, and disable any other MCP servers. Those load for every platform.
- **Vercel (static snapshot):** `uv run web/build_static.py`, then `cd web/dist && vercel deploy --prod`. All `/api/*` GETs are pre-rendered to JSON and wired up with rewrites.

### Demo script (for the video, ~5 min)
1. **Problem (30s):** Suki Mart branches have stockouts, duplicate POs, short shifts and unanswered tickets, and nobody connects them in time.
2. **HQ in Desktop (2 min):** sidebar → **Kuya Hermes HQ** → **Run full sweep**. Kuya ranks all 12 branches (Ermita and Alabang are worst) and the KPI tiles and risk badges fill in live. Click **ERM → Branch pulse**, then **Fix stockouts**: Kuya skips items with an open PO, drafts the rest, and asks *"I-file ko na ba?"*. Answer yes, and you get PO numbers back.
3. **Field on Telegram (1.5 min):** *"di pumasok si John Soriano bukas ng 7am sa Alabang"* → Kuya finds his shift, proposes Rowena Tomas (fewest absences), and books the cover after a yes. Only the final answers show in Telegram (tool progress is turned off there).
4. **Close (30s):** one agent, two surfaces, same MCP and skill, and every write needs a human yes.

### Assets
- `assets/kuya-hermes-fullbody.png`, `assets/kuya-hermes-avatar.png`: mascot (the 160px avatar is embedded in the plugin)
- `assets/icons.md`: the UI icon set (inline SVG, `currentColor`)
- `assets/ui-inspo.png`: the design reference for the HQ page

`sari-sari/` holds our earlier prototype: the same Kuya Hermes persona keeping utang and stock for a single sari-sari store via Telegram and Google Sheets.

---

# Camp Run with Hermes Agent

**The official starter kit for the CAMP / RUN Hermes Agent hackathon** — October 2, 2026 · Avtica Office.

Fork this repo, and in 45–60 minutes build one connected solution on top of a realistic business sandbox:

```
  LAYER 3 · DESKTOP PLUGIN      LAYER 2 · SKILL            LAYER 1 · MCP SERVER        SANDBOX
  "the face"                    "the playbook"             "the hands"
 ┌──────────────────┐        ┌──────────────────┐       ┌──────────────────┐       ┌──────────────┐
 │ Pane / command in│ ─────▶ │ SKILL.md teaches │ ────▶ │ Python tools that│ ────▶ │ data/store.db│
 │ Hermes Desktop   │        │ Hermes a workflow│       │ read & act on the│       │ Suki Mart    │
 └──────────────────┘        └──────────────────┘       │ data             │       └──────────────┘
                                                        └──────────────────┘
```

Everything runs **locally on your laptop** — no cloud, no accounts, no API keys for the data. Works offline.

---

## Contents

- [The sandbox: Suki Mart](#the-sandbox-suki-mart)
- [Before the event](#before-the-event)
- [Quick start](#quick-start)
- [Layer 1 — MCP server](#layer-1--mcp-server)
- [Layer 2 — Skill](#layer-2--skill)
- [Layer 3 — Desktop plugin](#layer-3--desktop-plugin)
- [Suggested timebox](#suggested-timebox)
- [Rules & judging](#rules--judging)
- [Troubleshooting](#troubleshooting)

---

## The sandbox: Suki Mart

**Suki Mart** is a fictional grocery and delivery chain with **12 branches across Metro Manila** — BGC, Makati, Ortigas, Kapitolyo, Cubao, Katipunan, Tomas Morato, Shaw, Alabang, BF Parañaque, Marikina and Ermita.

It lives in one SQLite file, `data/store.db`, with **~230,000 rows across 18 tables** and six months of history:

| Area | Tables |
|---|---|
| Stores & supply | `branches`, `suppliers`, `products`, `inventory`, `purchase_orders` |
| Customers & sales | `customers`, `loyalty_accounts`, `loyalty_transactions`, `promos`, `orders`, `order_items` |
| Delivery | `riders`, `deliveries` |
| People & operations | `staff`, `staffing_targets`, `shifts` |
| Customer experience | `support_tickets`, `reviews` |

📖 Full column reference: **[data/SCHEMA.md](data/SCHEMA.md)**

Three things to know:

1. **"Today" inside the data is `2026-09-30`.** Use it for "this week", "last 30 days", "overdue", etc.
2. **The data is messy on purpose.** Every department has real problems planted in it — the kind a real operations or customer team would lose sleep over. Finding one worth solving is part of the challenge.
3. **You can't break it for good.** `python data/seed.py` rebuilds the exact same database in seconds.

The challenge track is **Business Operations** or **Customer Experience** (Open Innovation may also be considered).

---

## Before the event

Do this at home — venue Wi-Fi is not the place to install things.

- [ ] **Hermes Agent + Hermes Desktop** installed → [docs](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart)
- [ ] A working model provider (`hermes model`) — your own account
- [ ] `hermes doctor` passes
- [ ] `uv` available (`uv --version`) — the Hermes installer includes it
- [ ] `git` installed and this repo forked & cloned
- [ ] Python 3.10+ (only needed if you run the scripts directly)

---

## Quick start

```bash
# 1. Fork this repo on GitHub, then clone YOUR fork
git clone https://github.com/<your-username>/Camp-Run-with-Hermes-Agent.git
cd Camp-Run-with-Hermes-Agent

# 2. Check the MCP server starts (Ctrl+C to stop — it waits silently for Hermes)
uv run mcp-server/server.py

# 3. Register it with Hermes — use the ABSOLUTE path to server.py
pwd        # macOS / Linux  →  e.g. /Users/you/Camp-Run-with-Hermes-Agent
cd         # Windows (cmd)  →  e.g. C:\Users\you\Camp-Run-with-Hermes-Agent

hermes mcp add suki --command uv --args run /ABSOLUTE/PATH/Camp-Run-with-Hermes-Agent/mcp-server/server.py

# 4. Restart Hermes (no hot-reload for MCP), then verify
hermes mcp test suki
```

Then ask Hermes: *"Use the suki MCP server to describe the Suki Mart sandbox."*

> **Alternative to step 3** — add it to `~/.hermes/config.yaml` yourself:
> ```yaml
> mcp_servers:
>   suki:
>     command: uv
>     args: ["run", "/ABSOLUTE/PATH/Camp-Run-with-Hermes-Agent/mcp-server/server.py"]
> ```

---

## Layer 1 — MCP server

📁 `mcp-server/server.py`

A working Python MCP server (FastMCP) with the database already wired up and two tools: `describe_sandbox` (exploration helper) and `list_branches` (an example domain tool). **Your job: add the tools your idea needs.**

```python
@mcp.tool()
def find_stockout_risks(branch_code: str, days_of_cover: int = 3) -> list[dict]:
    """Products at a branch that will run out within N days at current sales pace."""
    return query("SELECT ... WHERE ...", (branch_code, days_of_cover))
```

Good tools:

- **Answer one business question each**, with clear parameters (`branch_code`, `days`, `limit`…).
- **Keep SQL inside the tool.** A generic "run any SQL" tool scores low — the judges want domain design.
- **Return small, structured results.** 20 clean rows beat 2,000 raw ones.
- **Have a docstring written for the AI** — it's how Hermes decides when to call the tool.
- **Can take action** with the `execute()` helper (resolve a ticket, create a purchase order, flag a customer…).

After every change: **restart Hermes**, then `hermes mcp test suki`. Tools appear to the agent as `mcp_suki_<tool_name>`.

> The server pins `mcp<2` (the classic `FastMCP` API most docs and AI assistants use). `uv run` installs it automatically — no `pip install` needed.

---

## Layer 2 — Skill

📁 `skills/suki-team-skill/SKILL.md`

A skill is a markdown procedure Hermes loads on demand. It teaches the agent **when** to act and **how to chain your MCP tools** into a real multi-step workflow — the sequence, the decision rules, and the output format.

```bash
# 1. Rename the folder AND the `name:` field to your skill's name (they must match)
# 2. Fill in the template, then install it:
cp -r skills/<your-skill> ~/.hermes/skills/                      # macOS / Linux
xcopy /E /I skills\<your-skill> %USERPROFILE%\.hermes\skills\<your-skill>   # Windows
```

Installed skills take effect in **new sessions** — start a new chat after installing. Test it by asking something that matches your skill's description, or name it directly: *"Use the \<your-skill\> skill to…"*

📖 [Working with Skills](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills)

---

## Layer 3 — Desktop plugin

📁 `desktop-plugin/suki-panel/plugin.js`

A pane inside Hermes Desktop with buttons that trigger your skill, plus a ⌘K / Ctrl+K command. It's a single JavaScript file — no build step.

```bash
# Rename the folder AND the `id` in plugin.js (they must match), then:
cp -r desktop-plugin/<your-plugin> ~/.hermes/desktop-plugins/                               # macOS / Linux
xcopy /E /I desktop-plugin\<your-plugin> %USERPROFILE%\.hermes\desktop-plugins\<your-plugin>   # Windows
```

In Hermes Desktop: **⌘K / Ctrl+K → "Reload desktop plugins"**, and enable it under **Capabilities → Plugins** if needed. Saves hot-reload after that.

Loader rules (from the SDK):

- Only three imports work: `@hermes/plugin-sdk`, `react`, `react/jsx-runtime`.
- The file isn't compiled — write UI with `jsx()` / `jsxs()`, **not** `<JSX/>` syntax.
- Use theme variables (`var(--ui-text-secondary)`), never hardcoded colors.

**Going further:** the template sends prompts into the chat with `host.composer.submit()`. The SDK can do much more — sidebar pages, status-bar widgets, transcript directives that render your own components inside the agent's reply, and a Python backend via `ctx.rest`. Hermes ships a bundled **`hermes-desktop-plugins`** skill — ask your agent to help you build the pane.

📖 [Desktop Plugin SDK](https://hermes-agent.nousresearch.com/docs/developer-guide/desktop-plugin-sdk)

---

## Suggested timebox

| Minutes | Goal |
|---|---|
| 0–15 | MCP tools written; `hermes mcp test` passes |
| 15–30 | Skill written, installed, and triggering from a natural prompt |
| 30–50 | Desktop pane wired to the skill |
| 50–60 | Polish and rehearse the 5-minute demo |

Using Hermes (or any AI) to help write your code is **allowed and encouraged**. The idea, the design and the integration are what's judged.

---

## Rules & judging

📋 Full mechanics and scoring: **[docs/JUDGING.md](docs/JUDGING.md)**

| Criterion | Points |
|---|---:|
| MCP Server (Layer 1) | 20 |
| Skill (Layer 2) | 20 |
| Desktop Plugin GUI (Layer 3) | 20 |
| End-to-End Integration | 10 |
| Relevance | 15 |
| Uniqueness | 10 |
| Demo & Pitch | 5 |
| **Total** | **100** |

- Build on the Suki Mart sandbox data.
- Write your own MCP — catalog MCPs or existing plugins don't count as your team's build.
- Demo live from your laptop: **problem → how Hermes is used → working output**, in 5 minutes.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `hermes mcp test suki` fails | Use the **absolute** path to `server.py`. Run `uv run mcp-server/server.py` directly to see errors. Restart Hermes after any change. |
| `No module named 'mcp.server.fastmcp'` | You're on `mcp` v2. Run through `uv run` (it respects the `mcp<2` pin in the file header). |
| Tools don't show up in chat | Restart Hermes — MCP servers load at startup only. Check `hermes mcp list`. |
| `unable to open database file` | Don't move `server.py` out of the repo — it finds `data/store.db` relative to its own location. |
| Skill doesn't trigger | Start a **new** session. Make the `description:` specific about *when* to use it. Folder name must equal `name:`. |
| Plugin doesn't appear | Folder name must equal the `id` in `plugin.js`. ⌘K → "Reload desktop plugins". Check the error toast. |
| `ReferenceError` in plugin | Every identifier used in `jsx()` must be in the import line. |
| Broke the data | `python data/seed.py` — rebuilds the identical database. |

---

## Repository layout

```
Camp-Run-with-Hermes-Agent/
├── data/
│   ├── store.db              ← the Suki Mart sandbox (SQLite)
│   ├── seed.py               ← deterministic generator = reset command
│   └── SCHEMA.md             ← tables, columns, relationships, enums
├── mcp-server/
│   └── server.py             ← Layer 1 template
├── skills/
│   └── suki-team-skill/
│       └── SKILL.md          ← Layer 2 template
├── desktop-plugin/
│   └── suki-panel/
│       └── plugin.js         ← Layer 3 template
└── docs/
    └── JUDGING.md            ← mechanics & scoring
```

---

## License

[MIT](LICENSE) — fork it, remix it, ship it. Suki Mart and every person, business and record in the dataset are **fictional**; any resemblance to real entities is coincidental.

Built for **CAMP / RUN** · Avtica × DEVCON Manila · Powered by [Hermes Agent](https://hermes-agent.nousresearch.com) by Nous Research.
