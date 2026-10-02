// LAYER 3 — DESKTOP PLUGIN (the face)
//
// A pane inside Hermes Desktop that triggers your skill with one click.
// Flow: button → prompt sent to the chat → Hermes loads your SKILL → calls your MCP tools.
//
// Install (the folder name MUST equal the `id` below):
//   macOS/Linux:  ~/.hermes/desktop-plugins/suki-panel/plugin.js
//   Windows:      %USERPROFILE%\.hermes\desktop-plugins\suki-panel\plugin.js
// Then in Hermes Desktop: Ctrl/Cmd+K → "Reload desktop plugins", and enable it
// in Capabilities → Plugins if needed. The app hot-reloads every save.
//
// Rules of the disk-plugin loader (from the Desktop Plugin SDK docs):
//   * Only these imports resolve: '@hermes/plugin-sdk', 'react', 'react/jsx-runtime'.
//   * The file is NOT compiled — use jsx()/jsxs() calls, not <JSX/> syntax.
//   * No hardcoded colors — use theme variables like var(--ui-text-secondary).
//   * Every identifier used in jsx() must be imported.
// Docs: https://hermes-agent.nousresearch.com/docs/developer-guide/desktop-plugin-sdk
// Tip: ask Hermes to help — it ships a bundled `hermes-desktop-plugins` skill.

import { host, useValue, Button, PANES_AREA, PALETTE_AREA } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'

const PLUGIN_ID = 'suki-panel' // TODO(team): rename (and rename the folder to match)

// TODO(team): replace with actions that trigger YOUR skill. Mention the skill
// by name so Hermes loads it reliably.
const ACTIONS = [
  {
    label: 'Run my team skill',
    hint: 'Sends a prompt that triggers the skill',
    prompt: 'Use the suki-team-skill skill to give me the brief for the BGC branch.'
  },
  {
    label: 'Explore the sandbox',
    hint: 'Uses the describe_sandbox MCP tool',
    prompt: 'Use the suki MCP server to describe the Suki Mart sandbox in 5 bullet points.'
  }
]

async function send(prompt) {
  // Sends the prompt as if the user typed it into the focused chat and pressed Enter.
  const ok = host.composer.submit(null, prompt)
  if (!ok) {
    host.notify({ kind: 'info', message: 'Open or focus a chat first, then click again.' })
  }
}

function ActionRow({ action, disabled }) {
  return jsxs('div', {
    className: 'flex flex-col gap-1 rounded-md border border-(--ui-stroke-secondary) p-2',
    children: [
      jsx(Button, {
        disabled,
        onClick: () => send(action.prompt),
        children: action.label
      }),
      jsx('div', { className: 'text-xs text-(--ui-text-tertiary)', children: action.hint })
    ]
  })
}

function SukiPanel() {
  const busy = useValue(host.state.busy) // true while the focused chat is working
  return jsxs('div', {
    className: 'flex h-full flex-col gap-3 overflow-auto p-3 text-sm',
    children: [
      jsxs('div', {
        children: [
          jsx('div', { className: 'font-medium', children: 'Suki Mart · Team Panel' }),
          jsx('div', {
            className: 'text-xs text-(--ui-text-tertiary)',
            children: busy ? 'Hermes is working…' : 'Pick an action to run it in the chat.'
          })
        ]
      }),
      ...ACTIONS.map((a) => jsx(ActionRow, { action: a, disabled: busy }, a.label))
    ]
  })
}

export default {
  id: PLUGIN_ID,
  name: 'Suki Team Panel', // TODO(team): your plugin's display name
  register(ctx) {
    // A pane docked on the right side of the window.
    ctx.register({
      id: 'pane',
      area: PANES_AREA,
      title: 'Suki Panel',
      data: { placement: 'right', width: '300px' },
      render: () => jsx(SukiPanel, {})
    })
    // A ⌘K / Ctrl+K palette command that runs your first action.
    ctx.register({
      id: 'run-first',
      area: PALETTE_AREA,
      data: {
        id: `${PLUGIN_ID}.run`,
        label: `Suki: ${ACTIONS[0].label}`,
        keywords: ['suki', 'camp', 'run'],
        run: () => send(ACTIONS[0].prompt)
      }
    })
  }
}
