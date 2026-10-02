// Shared front-end helpers for the Kuya Hermes website: icons, a small
// markdown renderer for Kuya's replies, and the chat widget that talks to the
// real Hermes agent through POST /api/chat.

const ICON_PATHS = {
  fullSweep: '<path d="M4 18.5h16"/><path d="M5.5 18.5v-4h3v4"/><path d="M10.5 18.5v-5.5h3v5.5"/><path d="M15.5 18.5v-3h3v3"/><path d="M4.5 11.5a8.5 8.5 0 0 1 15.8-4.3"/><path d="M12 11l6.7-4.2"/><circle cx="12" cy="11" r="1"/><path d="M7.5 8.5h.01"/><path d="M9 5.5h.01"/>',
  branchPulse: '<path d="M4 9h16"/><path d="M5 9l1-4h12l1 4"/><path d="M5.5 9v9.5h13V9"/><path d="M8 18.5v-4h3v4"/><path d="M7 12.5h2l1.2-2.2 2.1 4.4 1.5-3 1 1.8H17"/>',
  store: '<path d="M4 9h16"/><path d="M5 9l1-4h12l1 4"/><path d="M5.5 9v9.5h13V9"/><path d="M10 18.5v-4h4v4"/>',
  fixStockouts: '<path d="M4 6.5h11"/><path d="M4 11.5h8"/><path d="M4 16.5h8"/><path d="M5 6.5v12"/><path d="M12 6.5v4"/><circle cx="17.5" cy="15.5" r="3.5"/><path d="M17.5 13.5v4"/><path d="M15.5 15.5h4"/>',
  purchaseOrder: '<path d="M8 5h-2a1.5 1.5 0 0 0-1.5 1.5v12A1.5 1.5 0 0 0 6 20h8"/><path d="M12 5h2a1.5 1.5 0 0 1 1.5 1.5V10"/><rect x="8" y="3.5" width="4" height="3" rx="1"/><path d="m8 11 1.5 1.5 3-3"/><path d="M15 13.5 19 12l3 1.5v5L19 20l-4-1.5z"/><path d="M15 13.5 19 15l3-1.5"/><path d="M19 15v5"/>',
  duplicate: '<path d="M8 5.5h8l3 3v10H8z"/><path d="M16 5.5v3h3"/><path d="M6 8.5H5a1 1 0 0 0-1 1v9.5h10"/><path d="M13.5 11v3.5"/><path d="M13.5 17h.01"/>',
  shiftCover: '<circle cx="8" cy="7.5" r="2.5"/><circle cx="16" cy="7.5" r="2.5"/><path d="M3.5 17c.4-2.8 2.1-4.5 4.5-4.5 1 0 1.9.3 2.6.8"/><path d="M20.5 17c-.4-2.8-2.1-4.5-4.5-4.5-1 0-1.9.3-2.6.8"/><path d="M8 18.5h8"/><path d="m14 16.5 2 2-2 2"/><path d="M16 14.5H8"/><path d="m10 12.5-2 2 2 2"/>',
  fieldReport: '<path d="M5.5 5h9A2.5 2.5 0 0 1 17 7.5v5A2.5 2.5 0 0 1 14.5 15H10l-4 3v-3.2A2.5 2.5 0 0 1 3 12.5v-5A2.5 2.5 0 0 1 5.5 5z"/><path d="M19.5 13.5c1.5 0 2.5 1.1 2.5 2.5 0 2-2.5 4.5-2.5 4.5S17 18 17 16c0-1.4 1-2.5 2.5-2.5z"/><circle cx="19.5" cy="16" r=".6"/>',
  lateDelivery: '<circle cx="6" cy="17.5" r="2"/><circle cx="15" cy="17.5" r="2"/><path d="M8 17.5h5"/><path d="M5.5 15.5 7 11h5l2 4.5"/><path d="M7 11 5.5 9.5H3.5"/><path d="M12 11h2.5l1.5 2"/><circle cx="18.5" cy="7.5" r="3.5"/><path d="M18.5 5.5v2.2l1.5 1"/>',
  send: '<path d="M21 3 10 14"/><path d="M21 3l-6.5 18-4.5-7-7-4.5z"/>',
  chat: '<path d="M5.5 5h13A2.5 2.5 0 0 1 21 7.5v7a2.5 2.5 0 0 1-2.5 2.5H11l-4.5 3.5V17h-1A2.5 2.5 0 0 1 3 14.5v-7A2.5 2.5 0 0 1 5.5 5z"/>',
  telegram: '<path d="M21.5 4.5 2.8 11.7c-.9.4-.9 1.6.1 1.9l4.6 1.4 1.8 5.4c.3.8 1.3 1 1.9.4l2.6-2.5 4.8 3.5c.7.5 1.7.1 1.9-.8l3-14.9c.2-1-.8-1.8-1.9-1.5z"/><path d="m7.5 15 10-7.5-7.6 9"/>',
  arrow: '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
  shield: '<path d="M12 3 4.5 6v5.5c0 4.5 3.2 8.2 7.5 9.5 4.3-1.3 7.5-5 7.5-9.5V6z"/><path d="m9 12 2 2 4-4"/>',
  desktop: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8"/><path d="M12 16v4"/>'
}

export function icon(name, cls = 'icon') {
  return `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON_PATHS[name] || ''}</svg>`
}

// Replace <i data-icon="name"></i> placeholders with inline SVG.
export function hydrateIcons(root = document) {
  root.querySelectorAll('[data-icon]').forEach((el) => {
    el.outerHTML = icon(el.dataset.icon, el.className || 'icon')
  })
}

export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))

// Minimal markdown: headings, bold/italic/code, lists, tables, paragraphs.
export function md(src) {
  const inline = (t) => esc(t)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*]+)\*/g, '$1<em>$2</em>')
  const lines = String(src || '').replace(/\r/g, '').split('\n')
  let html = ''
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (/^\s*\|.*\|\s*$/.test(line) && i + 1 < lines.length && /^\s*\|?\s*:?-{2,}/.test(lines[i + 1])) {
      const cells = (l) => l.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim())
      let t = '<div class="md-table"><table><thead><tr>' + cells(line).map((c) => `<th>${inline(c)}</th>`).join('') + '</tr></thead><tbody>'
      i += 2
      while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) {
        t += '<tr>' + cells(lines[i]).map((c) => `<td>${inline(c)}</td>`).join('') + '</tr>'
        i++
      }
      i--
      html += t + '</tbody></table></div>'
    } else if (/^\s*[-*•]\s+/.test(line)) {
      html += '<ul>'
      while (i < lines.length && /^\s*[-*•]\s+/.test(lines[i])) { html += `<li>${inline(lines[i].replace(/^\s*[-*•]\s+/, ''))}</li>`; i++ }
      i--
      html += '</ul>'
    } else if (/^\s*\d+[.)]\s+/.test(line)) {
      html += '<ol>'
      while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])) { html += `<li>${inline(lines[i].replace(/^\s*\d+[.)]\s+/, ''))}</li>`; i++ }
      i--
      html += '</ol>'
    } else if (/^#{1,4}\s+/.test(line)) {
      html += `<h4>${inline(line.replace(/^#+\s+/, ''))}</h4>`
    } else if (line.trim()) {
      html += `<p>${inline(line)}</p>`
    }
  }
  return html
}

// ---------------------------------------------------------------- chat widget

export function mountChat(root, { mascot = '/assets/kuya-hermes-avatar-160.png' } = {}) {
  const conversation = sessionStorage.getItem('kuya-conv') || `kuya-web-${Date.now()}`
  sessionStorage.setItem('kuya-conv', conversation)

  root.innerHTML = `
    <div class="chat-head">
      <img src="${mascot}" alt="">
      <div><b>Kuya Hermes</b><span><i class="dot"></i> live · Hermes Agent</span></div>
      <button class="chat-reset" title="New conversation">New</button>
    </div>
    <div class="chat-log" aria-live="polite"></div>
    <div class="chat-quick"></div>
    <form class="chat-form">
      <input name="q" autocomplete="off" placeholder="Message Kuya… e.g. kumusta ang Alabang?">
      <button class="btn btn-gold" type="submit">${icon('send')}</button>
    </form>`
  const log = root.querySelector('.chat-log')
  const form = root.querySelector('.chat-form')
  const input = form.querySelector('input')
  const quick = root.querySelector('.chat-quick')
  let busy = false

  const add = (who, html, extra = '') => {
    const el = document.createElement('div')
    el.className = `bubble-msg ${who} ${extra}`
    el.innerHTML = html
    log.appendChild(el)
    log.scrollTop = log.scrollHeight
    return el
  }

  const welcome = () => add('bot', md("👋 Kumusta! Ako si **Kuya Hermes**, ang branch-ops copilot ng Suki Mart. Tanungin mo ako about any branch, or click **Run full sweep**. Walang mababago hangga't hindi ka nag-yes. ✅"))
  welcome()

  const setQuick = (items) => {
    quick.innerHTML = items.map((q) => `<button type="button">${esc(q)}</button>`).join('')
    quick.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => ask(b.textContent)))
  }
  setQuick(['kumusta ang Alabang?', 'which branch needs help most?', 'ubos na ba ang bottled water sa ERM?'])

  async function ask(text) {
    const q = String(text || '').trim()
    if (!q || busy) return
    busy = true
    root.classList.add('busy')
    add('me', esc(q))
    const thinking = add('bot', '<span class="typing"><i></i><i></i><i></i></span> <span class="muted">Kuya is checking the Suki Mart data…</span>', 'thinking')
    const started = Date.now()
    try {
      const r = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: q, conversation }) })
      // Static (Vercel) build has no chat backend: explain instead of erroring.
      if ([404, 405, 501].includes(r.status)) {
        thinking.remove()
        add('bot', md("🧢 This is the **public snapshot** of Kuya Hermes. Live chat runs on our **local demo** (Hermes Desktop + this site on the team laptop) and on **Telegram (@kuyahermes_bot)**. The numbers on this page are real Suki Mart data from Sep 30, 2026."))
        return
      }
      const data = await r.json()
      thinking.remove()
      if (data.error) {
        add('bot', `<p class="err">⚠️ ${esc(data.error)}</p>`)
      } else {
        const used = [...new Set((data.tools || []).filter((t) => /suki/.test(t)).map((t) => t.replace(/^mcp_+suki_+/, '')))]
        const meta = `<div class="tools">${used.map((t) => `<span class="chip">🔧 ${esc(t)}</span>`).join('')}<span class="muted">${Math.round((Date.now() - started) / 1000)}s</span></div>`
        add('bot', md(data.reply || '(no reply)') + meta)
        if (/i-file ko na|confirm|approve|\?\s*$/i.test(data.reply || '')) setQuick(['Oo, i-file mo na ✅', 'Hindi muna', 'Show me the details'])
        else setQuick(['Fix stockouts there', 'Cover the shift gaps', 'Run full sweep'])
      }
      document.dispatchEvent(new CustomEvent('kuya:reply', { detail: data }))
    } catch (e) {
      thinking.remove()
      add('bot', `<p class="err">⚠️ Can't reach Kuya: ${esc(e.message)}</p>`)
    } finally {
      busy = false
      root.classList.remove('busy')
      input.focus()
    }
  }

  form.addEventListener('submit', (e) => { e.preventDefault(); const v = input.value; input.value = ''; ask(v) })
  root.querySelector('.chat-reset').addEventListener('click', () => {
    sessionStorage.removeItem('kuya-conv')
    location.reload()
  })
  return { ask }
}
