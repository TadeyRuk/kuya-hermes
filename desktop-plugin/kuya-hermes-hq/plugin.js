// LAYER 3 — DESKTOP PLUGIN (the face) · Kuya Hermes HQ
//
// HQ control surface for Suki Mart branch operations inside Hermes Desktop:
//   * a full "Kuya Hermes HQ" page (sidebar nav) with a network-wide "Run full
//     sweep", a 12-branch picker and per-branch actions
//   * a compact right-side pane that sits next to the chat
//   * Ctrl/Cmd+K palette commands
// Every button sends a prompt that names the kuya-hermes-ops skill, which chains
// the suki MCP tools over data/store.db. The same skill + MCP also answer branch
// managers on Telegram through the Hermes gateway.
//
// Install (folder name MUST equal the id below):
//   Windows: %LOCALAPPDATA%\hermes\desktop-plugins\kuya-hermes-hq\plugin.js
//   macOS/Linux: ~/.hermes/desktop-plugins/kuya-hermes-hq/plugin.js
// Then Ctrl/Cmd+K → "Reload desktop plugins".
//
// Loader rules: only '@hermes/plugin-sdk', 'react', 'react/jsx-runtime' resolve;
// no JSX syntax (jsx()/jsxs() only); theme variables, never hardcoded colors.

import {
  host, useValue, Button,
  PANES_AREA, PALETTE_AREA, ROUTES_AREA, SIDEBAR_NAV_AREA
} from '@hermes/plugin-sdk'
import { useState } from 'react'
import { jsx, jsxs } from 'react/jsx-runtime'

const PLUGIN_ID = 'kuya-hermes-hq'
const PAGE_PATH = '/kuya-hermes'
const SKILL = 'kuya-hermes-ops'

const BRANCHES = [
  { code: 'ALB', name: 'Alabang', delivery: true },
  { code: 'BGC', name: 'BGC High Street', delivery: true },
  { code: 'CUB', name: 'Cubao', delivery: true },
  { code: 'ERM', name: 'Ermita', delivery: false },
  { code: 'KAT', name: 'Katipunan', delivery: true },
  { code: 'KPT', name: 'Kapitolyo', delivery: true },
  { code: 'MAN', name: 'Mandaluyong Shaw', delivery: false },
  { code: 'MKN', name: 'Marikina', delivery: true },
  { code: 'MKT', name: 'Makati Legazpi', delivery: true },
  { code: 'ORT', name: 'Ortigas Center', delivery: true },
  { code: 'PQE', name: 'Parañaque BF', delivery: true },
  { code: 'TMR', name: 'Tomas Morato', delivery: true }
]

const SWEEP_PROMPT =
  `Use the ${SKILL} skill to run a full network sweep of all Suki Mart branches: ` +
  'rank every branch by risk, then drill into the worst branch with a branch pulse ' +
  'and draft the fixes (purchase orders that are not duplicates, and shift covers) for my approval.'

const BRANCH_ACTIONS = [
  {
    id: 'pulse',
    label: 'Branch pulse',
    hint: 'Stock, staffing, tickets, deliveries',
    prompt: (b) => `Use the ${SKILL} skill to give me the branch pulse for ${b.code} (${b.name}).`
  },
  {
    id: 'stock',
    label: 'Fix stockouts',
    hint: 'Checks open POs first, drafts new ones',
    prompt: (b) => `Use the ${SKILL} skill to fix stockouts at ${b.code} (${b.name}): check each alert, skip anything with an open PO, and draft purchase orders for my approval.`
  },
  {
    id: 'staff',
    label: 'Cover shift gaps',
    hint: 'Tomorrow and the day after vs targets',
    prompt: (b) => `Use the ${SKILL} skill to cover the shift gaps at ${b.code} (${b.name}) for the next two days and propose the most reliable cover for my approval.`
  }
]

// Send into the chat the user is in; if none is focused, open a fresh chat and
// send there. composer.submit is fail-closed, so retry briefly while it mounts.
async function send(prompt) {
  if (host.composer.submit(null, prompt)) return
  host.newChat()
  for (let i = 0; i < 20; i++) {
    await new Promise((r) => setTimeout(r, 150))
    if (host.composer.submit('new', prompt) || host.composer.submit(null, prompt)) return
  }
  host.notify({ kind: 'info', message: 'Open a chat first, then click again.' })
}

// ---------------------------------------------------------------- pieces

function Pill({ children, tone }) {
  const color = tone === 'ok' ? 'text-(--ui-text-success, var(--ui-text-secondary))' : 'text-(--ui-text-tertiary)'
  return jsx('span', {
    className: `rounded-full border border-(--ui-stroke-secondary) px-2 py-0.5 text-[0.6875rem] ${color}`,
    children
  })
}

function SectionLabel({ children }) {
  return jsx('div', {
    className: 'text-[0.6875rem] font-medium uppercase tracking-wide text-(--ui-text-tertiary)',
    children
  })
}

function BranchCard({ branch, selected, onSelect }) {
  return jsxs('button', {
    type: 'button',
    onClick: () => onSelect(branch),
    className:
      'flex flex-col items-start gap-0.5 rounded-md border p-2 text-left transition-colors ' +
      (selected
        ? 'border-(--ui-stroke-primary) bg-(--ui-bg-tertiary)'
        : 'border-(--ui-stroke-secondary) hover:bg-(--ui-bg-secondary)'),
    children: [
      jsxs('div', {
        className: 'flex w-full items-center justify-between gap-2',
        children: [
          jsx('span', { className: 'font-mono text-xs font-semibold', children: branch.code }),
          branch.delivery ? null : jsx('span', { className: 'text-[0.625rem] text-(--ui-text-tertiary)', children: 'no delivery' })
        ]
      }),
      jsx('span', { className: 'truncate text-xs text-(--ui-text-secondary)', children: branch.name })
    ]
  })
}

function ActionButtons({ branch, busy, compact }) {
  return jsx('div', {
    className: compact ? 'flex flex-col gap-2' : 'grid grid-cols-3 gap-2',
    children: BRANCH_ACTIONS.map((a) =>
      jsxs('div', {
        className: 'flex flex-col gap-1 rounded-md border border-(--ui-stroke-secondary) p-2',
        children: [
          jsx(Button, { disabled: busy, onClick: () => send(a.prompt(branch)), children: a.label }),
          jsx('div', { className: 'text-[0.6875rem] text-(--ui-text-tertiary)', children: a.hint })
        ]
      }, a.id)
    )
  })
}

function AskBox({ branch, busy }) {
  const [text, setText] = useState('')
  const submit = () => {
    const q = text.trim()
    if (!q) return
    send(`Use the ${SKILL} skill for ${branch.code} (${branch.name}): ${q}`)
    setText('')
  }
  return jsxs('div', {
    className: 'flex gap-2',
    children: [
      jsx('input', {
        value: text,
        disabled: busy,
        placeholder: `Ask Kuya about ${branch.code}… e.g. "ubos na ba ang bottled water?"`,
        onChange: (e) => setText(e.target.value),
        onKeyDown: (e) => { if (e.key === 'Enter') submit() },
        className:
          'min-w-0 flex-1 rounded-md border border-(--ui-stroke-secondary) bg-transparent px-2 py-1 text-sm ' +
          'text-(--ui-text-primary) placeholder:text-(--ui-text-tertiary) outline-none focus:border-(--ui-stroke-primary)'
      }),
      jsx(Button, { disabled: busy || !text.trim(), onClick: submit, children: 'Ask' })
    ]
  })
}

function useBranch() {
  const [code, setCode] = useState('ALB')
  const branch = BRANCHES.find((b) => b.code === code) || BRANCHES[0]
  return [branch, (b) => setCode(b.code)]
}

// ---------------------------------------------------------------- full page

function HqPage() {
  const busy = useValue(host.state.busy)
  const gateway = useValue(host.state.gateway)
  const [branch, select] = useBranch()

  return jsx('div', {
    className: 'h-full overflow-auto',
    children: jsxs('div', {
      className: 'mx-auto flex max-w-4xl flex-col gap-5 p-6 text-sm',
      children: [
        // Header
        jsxs('div', {
          className: 'flex flex-wrap items-end justify-between gap-3',
          children: [
            jsxs('div', {
              children: [
                jsx('div', { className: 'text-xl font-semibold', children: 'Kuya Hermes HQ' }),
                jsx('div', {
                  className: 'text-(--ui-text-tertiary)',
                  children: 'Suki Mart branch-ops copilot · 12 branches · data as of Sep 30, 2026'
                })
              ]
            }),
            jsxs('div', {
              className: 'flex gap-2',
              children: [
                jsx(Pill, { tone: gateway === 'open' ? 'ok' : undefined, children: `gateway: ${gateway}` }),
                jsx(Pill, { children: 'Telegram: field managers' }),
                jsx(Pill, { children: busy ? 'Kuya is working…' : 'ready' })
              ]
            })
          ]
        }),

        // Hero: full sweep
        jsxs('div', {
          className: 'flex flex-wrap items-center justify-between gap-4 rounded-lg border border-(--ui-stroke-secondary) bg-(--ui-bg-secondary) p-4',
          children: [
            jsxs('div', {
              className: 'flex max-w-xl flex-col gap-1',
              children: [
                jsx('div', { className: 'text-base font-medium', children: 'Run full sweep' }),
                jsx('div', {
                  className: 'text-(--ui-text-secondary)',
                  children:
                    'Scores all 12 branches for stockouts, duplicate POs, staffing gaps, unanswered tickets and late deliveries, then drafts fixes for the worst branch. Nothing is written until you approve.'
                })
              ]
            }),
            jsx(Button, { disabled: busy, onClick: () => send(SWEEP_PROMPT), children: busy ? 'Working…' : '▶ Run full sweep' })
          ]
        }),

        // Branch picker
        jsxs('div', {
          className: 'flex flex-col gap-2',
          children: [
            jsx(SectionLabel, { children: 'Branches' }),
            jsx('div', {
              className: 'grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-6',
              children: BRANCHES.map((b) =>
                jsx(BranchCard, { branch: b, selected: b.code === branch.code, onSelect: select }, b.code)
              )
            })
          ]
        }),

        // Branch actions
        jsxs('div', {
          className: 'flex flex-col gap-2',
          children: [
            jsx(SectionLabel, { children: `${branch.code} · ${branch.name}` }),
            jsx(ActionButtons, { branch, busy }),
            jsx(AskBox, { branch, busy })
          ]
        }),

        // How it works
        jsxs('div', {
          className: 'flex flex-col gap-1 rounded-md border border-dashed border-(--ui-stroke-secondary) p-3 text-xs text-(--ui-text-tertiary)',
          children: [
            jsx('div', { className: 'font-medium text-(--ui-text-secondary)', children: 'How it works' }),
            jsx('div', { children: 'This page / Telegram  →  kuya-hermes-ops skill  →  suki MCP tools  →  Suki Mart store.db' }),
            jsx('div', { children: 'Branch managers report problems on Telegram in Taglish; HQ approves fixes here. Same agent, same tools.' })
          ]
        })
      ]
    })
  })
}

// ---------------------------------------------------------------- side pane

function HqPane() {
  const busy = useValue(host.state.busy)
  const [branch, select] = useBranch()

  return jsxs('div', {
    className: 'flex h-full flex-col gap-3 overflow-auto p-3 text-sm',
    children: [
      jsxs('div', {
        children: [
          jsx('div', { className: 'font-medium', children: 'Kuya Hermes HQ' }),
          jsx('div', {
            className: 'text-xs text-(--ui-text-tertiary)',
            children: busy ? 'Kuya is working…' : 'Suki Mart branch ops'
          })
        ]
      }),
      jsx(Button, { disabled: busy, onClick: () => send(SWEEP_PROMPT), children: '▶ Run full sweep' }),
      jsx(SectionLabel, { children: 'Branch' }),
      jsx('select', {
        value: branch.code,
        onChange: (e) => select({ code: e.target.value }),
        className:
          'rounded-md border border-(--ui-stroke-secondary) bg-transparent px-2 py-1 text-sm text-(--ui-text-primary)',
        children: BRANCHES.map((b) => jsx('option', { value: b.code, children: `${b.code} · ${b.name}` }, b.code))
      }),
      jsx(ActionButtons, { branch, busy, compact: true }),
      jsx(AskBox, { branch, busy }),
      jsx('button', {
        type: 'button',
        onClick: () => host.navigate(PAGE_PATH),
        className: 'text-left text-xs text-(--ui-text-tertiary) underline',
        children: 'Open full HQ page'
      })
    ]
  })
}

// ---------------------------------------------------------------- register

export default {
  id: PLUGIN_ID,
  name: 'Kuya Hermes HQ',
  register(ctx) {
    ctx.registerMany([
      {
        id: 'page',
        area: ROUTES_AREA,
        data: { path: PAGE_PATH },
        render: () => jsx(HqPage, {})
      },
      {
        id: 'nav',
        area: SIDEBAR_NAV_AREA,
        data: { path: PAGE_PATH, label: 'Kuya Hermes HQ', codicon: 'pulse' }
      },
      {
        id: 'pane',
        area: PANES_AREA,
        title: 'Kuya Hermes',
        data: { placement: 'right', width: '300px' },
        render: () => jsx(HqPane, {})
      },
      {
        id: 'sweep',
        area: PALETTE_AREA,
        data: {
          id: `${PLUGIN_ID}.sweep`,
          label: 'Kuya Hermes: Run full sweep',
          keywords: ['suki', 'sweep', 'kuya', 'branch'],
          run: () => send(SWEEP_PROMPT)
        }
      },
      {
        id: 'open',
        area: PALETTE_AREA,
        data: {
          id: `${PLUGIN_ID}.open`,
          label: 'Kuya Hermes: Open HQ page',
          keywords: ['suki', 'kuya', 'hq'],
          run: () => host.navigate(PAGE_PATH)
        }
      }
    ])
  }
}
