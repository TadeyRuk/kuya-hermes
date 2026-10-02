// ==========================================================================
// Kuya Hermes · Front-end helpers & fluid interactions
// Apple-grade tactile feedback, physical motion, and chat interface
// ==========================================================================

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
  desktop: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8"/><path d="M12 16v4"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  play: '<polygon points="5 3 19 12 5 21 5 3"/>',
  soundOn: '<path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z"/><path d="M15.5 9a3.5 3.5 0 0 1 0 6"/><path d="M17.8 6.7a7 7 0 0 1 0 10.6"/>',
  soundOff: '<path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z"/><path d="M16 9.5l4 5"/><path d="M20 9.5l-4 5"/>'
}

export function icon(name, cls = 'icon') {
  return `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON_PATHS[name] || ''}</svg>`
}

export function hydrateIcons(root = document) {
  root.querySelectorAll('[data-icon]').forEach((el) => {
    el.outerHTML = icon(el.dataset.icon, el.className || 'icon')
  })
}

export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))

// §4 Behavior Over Animation — Smooth spring count-up for statistics
export function countUp(el, endVal, duration = 650) {
  if (!el || isNaN(endVal)) return
  const start = 0
  const startTime = performance.now()
  function update(now) {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    // Apple critically damped spring ease-out
    const ease = 1 - Math.pow(1 - progress, 3)
    const current = Math.round(start + (endVal - start) * ease)
    el.textContent = current
    if (progress < 1) requestAnimationFrame(update)
    else el.textContent = endVal
  }
  requestAnimationFrame(update)
}
// ---------------------------------------------------------------- §13 Multimodal Feedback (Sound + Haptics)
// Zero-dependency Web Audio sound generator. No external audio assets, no
// network requests. The AudioContext is created and resumed strictly inside
// a user-gesture (pointerdown) handler to comply with autoplay policies —
// nothing plays before the visitor has interacted with the page at least once.
export const AppleAudio = (() => {
  const WHISPER_MIN = 0.04
  const WHISPER_MAX = 0.08
  const MUTE_KEY = 'kuya-sound-muted'

  let ctx = null
  let noiseBuffer = null
  let muted = false
  try { muted = localStorage.getItem(MUTE_KEY) === '1' } catch { /* storage unavailable */ }

  // Lazily create (and resume) the AudioContext. Must be invoked synchronously
  // from within a trusted user-gesture event the first time, per autoplay policy.
  function unlock() {
    if (ctx) return
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    if (!AudioCtx) return
    ctx = new AudioCtx()
    if (ctx.state === 'suspended') ctx.resume().catch(() => {})
  }
  if (typeof window !== 'undefined') {
    window.addEventListener('pointerdown', unlock, { once: true, passive: true })
  }

  // One shared white-noise buffer reused for every noise-based transient.
  function noise() {
    if (!ctx) return null
    if (!noiseBuffer || noiseBuffer.sampleRate !== ctx.sampleRate) {
      const len = Math.floor(ctx.sampleRate * 0.3)
      noiseBuffer = ctx.createBuffer(1, len, ctx.sampleRate)
      const data = noiseBuffer.getChannelData(0)
      for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1
    }
    return noiseBuffer
  }

  // Linear attack → exponential decay envelope, so every sound starts and
  // settles smoothly with no audible clicks from abrupt gain jumps.
  function envelope(gain, peak, attack, release, when) {
    const g = gain.gain
    g.cancelScheduledValues(when)
    g.setValueAtTime(0.0001, when)
    g.linearRampToValueAtTime(peak, when + attack)
    g.exponentialRampToValueAtTime(0.0001, when + attack + release)
  }

  const canPlay = () => !muted && !!ctx

  return {
    isMuted: () => muted,
    setMuted(v) {
      muted = !!v
      try { localStorage.setItem(MUTE_KEY, muted ? '1' : '0') } catch { /* storage unavailable */ }
    },
    toggleMute() {
      this.setMuted(!muted)
      return muted
    },

    // Ultra-crisp, subtle tactile click: a ~5ms band-passed noise transient.
    playTap() {
      if (!canPlay()) return
      const buf = noise()
      if (!buf) return
      const t = ctx.currentTime
      const src = ctx.createBufferSource()
      src.buffer = buf
      const filter = ctx.createBiquadFilter()
      filter.type = 'bandpass'
      filter.frequency.value = 3200
      filter.Q.value = 1.1
      const gain = ctx.createGain()
      src.connect(filter)
      filter.connect(gain)
      gain.connect(ctx.destination)
      envelope(gain, WHISPER_MIN, 0.001, 0.005, t)
      src.start(t)
      src.stop(t + 0.012)
    },

    // Soft wooden/glass tick for branch-card selection: a brief pitched
    // body with a short noise transient riding on top.
    playSelect() {
      if (!canPlay()) return
      const t = ctx.currentTime

      const osc = ctx.createOscillator()
      osc.type = 'triangle'
      osc.frequency.setValueAtTime(820, t)
      osc.frequency.exponentialRampToValueAtTime(240, t + 0.05)
      const oscGain = ctx.createGain()
      osc.connect(oscGain)
      oscGain.connect(ctx.destination)
      envelope(oscGain, WHISPER_MAX * 0.8, 0.002, 0.045, t)
      osc.start(t)
      osc.stop(t + 0.06)

      const buf = noise()
      if (!buf) return
      const src = ctx.createBufferSource()
      src.buffer = buf
      const filter = ctx.createBiquadFilter()
      filter.type = 'highpass'
      filter.frequency.value = 2200
      const nGain = ctx.createGain()
      src.connect(filter)
      filter.connect(nGain)
      nGain.connect(ctx.destination)
      envelope(nGain, WHISPER_MIN * 0.7, 0.001, 0.008, t)
      src.start(t)
      src.stop(t + 0.015)
    },

    // Gentle two-tone harmonic chime (C5 → G5) with a smooth decay, for
    // confirming an order or a shift cover.
    playSuccess() {
      if (!canPlay()) return
      const t = ctx.currentTime
      const notes = [
        { freq: 523.25, start: 0, dur: 0.42 },  // C5
        { freq: 783.99, start: 0.08, dur: 0.5 } // G5
      ]
      notes.forEach(({ freq, start, dur }) => {
        const osc = ctx.createOscillator()
        osc.type = 'sine'
        osc.frequency.value = freq
        const gain = ctx.createGain()
        osc.connect(gain)
        gain.connect(ctx.destination)
        envelope(gain, WHISPER_MAX * 0.9, 0.012, dur, t + start)
        osc.start(t + start)
        osc.stop(t + start + dur + 0.05)
      })
    },

    // Gentle, subtle air swoosh when a chat message is sent.
    playSend() {
      if (!canPlay()) return
      const buf = noise()
      if (!buf) return
      const t = ctx.currentTime
      const src = ctx.createBufferSource()
      src.buffer = buf
      const filter = ctx.createBiquadFilter()
      filter.type = 'bandpass'
      filter.Q.value = 0.8
      filter.frequency.setValueAtTime(500, t)
      filter.frequency.exponentialRampToValueAtTime(2600, t + 0.16)
      const gain = ctx.createGain()
      src.connect(filter)
      filter.connect(gain)
      gain.connect(ctx.destination)
      envelope(gain, WHISPER_MIN * 1.15, 0.02, 0.17, t)
      src.start(t)
      src.stop(t + 0.22)
    }
  }
})()

// Routes a pressed element to its matching whisper-level feedback sound.
function routeTactileSound(el) {
  if (el.matches('.branch')) { AppleAudio.playSelect(); return }
  if (el.matches('.proposal-btn.yes') || el.matches('.tg-action-btn[data-action="confirm"]')) { AppleAudio.playSuccess(); return }
  AppleAudio.playTap()
}

// §1 Response — Instant tactile response on pointerdown
export function setupTactileFeedback(root = document) {
  const isInteractive = (el) => el.closest('.btn, .branch, .action, .chat-quick button, .tg-action-btn, .phone-chip-trigger, .proposal-btn')
  
  root.addEventListener('pointerdown', (e) => {
    const target = isInteractive(e.target)
    if (!target) return
    target.classList.add('is-pressed')
    routeTactileSound(target)
    
    const release = () => {
      target.classList.remove('is-pressed')
      window.removeEventListener('pointerup', release)
      window.removeEventListener('pointercancel', release)
    }
    window.addEventListener('pointerup', release, { once: true })
    window.addEventListener('pointercancel', release, { once: true })
  }, { passive: true })
}

// Markdown renderer with Apple-style structured output & robust table parser
export function md(src) {
  const inline = (t) => esc(t)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*]+)\*/g, '$1<em>$2</em>')
    
  const lines = String(src || '').replace(/\r/g, '').split('\n')
  let html = ''
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const trimmed = line.trim()
    if (!trimmed) continue

    // Code blocks
    if (trimmed.startsWith('```')) {
      let code = ''
      i++
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        code += esc(lines[i]) + '\n'
        i++
      }
      html += '<div class="code-block"><pre><code>' + code + '</code></pre></div>'
      continue
    }

    // Separators (Major Unicode ━, Minor Unicode ─, or markdown --- / ===)
    if (/^[━─\-_=]{3,}$/.test(trimmed)) {
      const isMajor = /^[━=]{3,}$/.test(trimmed)
      html += `<div class="ai-divider ${isMajor ? 'major' : 'minor'}"></div>`
      continue
    }

    // Robust Markdown Table detection (with or without outer pipes)
    if (trimmed.includes('|') && i + 1 < lines.length && /^[\s|:-]+$/.test(lines[i + 1]) && lines[i + 1].includes('-')) {
      const getCells = (row) => {
        let r = row.trim()
        if (r.startsWith('|')) r = r.slice(1)
        if (r.endsWith('|')) r = r.slice(0, -1)
        return r.split('|').map((c) => c.trim())
      }

      const headerCells = getCells(line)
      const delimCells = getCells(lines[i + 1])
      
      const aligns = delimCells.map((d) => {
        const left = d.startsWith(':')
        const right = d.endsWith(':')
        if (left && right) return 'center'
        if (right) return 'right'
        return 'left'
      })

      let tableHtml = '<div class="md-table"><table><thead><tr>'
      headerCells.forEach((h, idx) => {
        const align = aligns[idx] || 'left'
        tableHtml += `<th class="align-${align}">${inline(h)}</th>`
      })
      tableHtml += '</tr></thead><tbody>'

      i += 2
      while (i < lines.length && lines[i].trim().includes('|')) {
        const rowCells = getCells(lines[i])
        tableHtml += '<tr>'
        rowCells.forEach((c, idx) => {
          const align = aligns[idx] || (isNaN(Number(c.replace(/[^0-9.-]/g, ''))) ? 'left' : 'right')
          const isNum = align === 'right' || /^[₱$]?[0-9,]+(\.[0-9]+)?(%|d|h)?$/.test(c.trim())
          tableHtml += `<td class="align-${align}${isNum ? ' tnum' : ''}">${inline(c)}</td>`
        })
        tableHtml += '</tr>'
        i++
      }
      i--
      tableHtml += '</tbody></table></div>'
      html += tableHtml
      continue
    }

    // Blockquotes
    if (trimmed.startsWith('>')) {
      html += `<blockquote class="ai-quote">${inline(trimmed.replace(/^>\s*/, ''))}</blockquote>`
      continue
    }

    // Bullet lists
    if (/^[-*•]\s+/.test(trimmed)) {
      html += '<ul>'
      while (i < lines.length && /^[-*•]\s+/.test(lines[i].trim())) { 
        html += `<li>${inline(lines[i].trim().replace(/^[-*•]\s+/, ''))}</li>`
        i++ 
      }
      i--
      html += '</ul>'
      continue
    }

    // Numbered lists
    if (/^\d+[.)]\s+/.test(trimmed)) {
      html += '<ol>'
      while (i < lines.length && /^\d+[.)]\s+/.test(lines[i].trim())) { 
        html += `<li>${inline(lines[i].trim().replace(/^\d+[.)]\s+/, ''))}</li>`
        i++ 
      }
      i--
      html += '</ol>'
      continue
    }

    // Headings
    if (/^#{1,4}\s+/.test(trimmed)) {
      const level = trimmed.match(/^#+/)[0].length
      const tag = 'h' + Math.min(level + 2, 5)
      html += `<${tag} class="ai-heading">${inline(trimmed.replace(/^#+\s+/, ''))}</${tag}>`
      continue
    }

    html += `<p>${inline(trimmed)}</p>`
  }
  return html
}
// ---------------------------------------------------------------- Chat Widget
export function mountChat(root, { mascot = '/assets/kuya-hermes-avatar-160.png' } = {}) {
  if (!root) return { ask: () => {} }

  const getStoredConv = () => {
    try { return sessionStorage.getItem('kuya-conv') || `kuya-web-${Date.now()}` } catch { return `kuya-web-${Date.now()}` }
  }
  const setStoredConv = (val) => {
    try { sessionStorage.setItem('kuya-conv', val) } catch {}
  }
  const removeStoredConv = () => {
    try { sessionStorage.removeItem('kuya-conv') } catch {}
  }
  const conversation = getStoredConv()
  setStoredConv(conversation)
  root.innerHTML = `
    <div class="chat-head">
      <img src="${mascot}" alt="Kuya Hermes">
      <div>
        <b>Kuya Hermes</b>
        <span><i class="dot"></i> Suki Mart copilot</span>
      </div>
      <button class="sound-toggle${AppleAudio.isMuted() ? ' is-muted' : ''}" title="${AppleAudio.isMuted() ? 'Unmute sound' : 'Mute sound'}" type="button" aria-pressed="${AppleAudio.isMuted()}">${icon(AppleAudio.isMuted() ? 'soundOff' : 'soundOn')}</button>
      <button class="chat-reset" title="New conversation" type="button">Reset</button>
    </div>
    <div class="chat-log" aria-live="polite"></div>
    <div class="chat-quick"></div>
    <form class="chat-form">
      <input name="q" autocomplete="off" placeholder="Ask Kuya… e.g. kumusta ang Alabang?">
      <button class="btn btn-accent" type="submit">${icon('send')}</button>
    </form>`

  const log = root.querySelector('.chat-log')
  const form = root.querySelector('.chat-form')
  const input = form.querySelector('input')
  const quick = root.querySelector('.chat-quick')
  const soundToggle = root.querySelector('.sound-toggle')
  let busy = false

  const add = (who, html, extra = '') => {
    const el = document.createElement('div')
    el.className = `bubble-msg ${who} ${extra}`
    el.innerHTML = html
    log.appendChild(el)
    // Smooth scroll down
    log.scrollTo({ top: log.scrollHeight, behavior: 'smooth' })
    return el
  }

  const welcome = () => add('bot', md("Kumusta! Ako si **Kuya Hermes**, ang branch-ops copilot ng Suki Mart.\n\nTanungin mo ako tungkol sa kahit aling branch, o mag-run ng **full sweep**. Walang mababago sa inventory o schedule hangga't hindi mo kinukumpirma."))
  welcome()

  const setQuick = (items) => {
    quick.innerHTML = items.map((q) => `<button type="button">${esc(q)}</button>`).join('')
    quick.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => ask(b.textContent)))
  }
  setQuick(['kumusta ang Alabang?', 'Aling branch ang pinaka-delikado?', 'Ubos na ba ang bottled water sa ERM?'])

  async function ask(text) {
    const q = String(text || '').trim()
    if (!q || busy) return
    busy = true
    root.classList.add('busy')
    add('me', esc(q))

    const thinking = add('bot', '<span class="typing"><i></i><i></i><i></i></span> <span class="muted" style="font-size:12.5px;margin-left:6px">Analyzing store data…</span>', 'thinking')
    const started = Date.now()

    try {
      const r = await fetch('/api/chat', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify({ message: q, conversation }) 
      })

      if ([404, 405, 501].includes(r.status)) {
        thinking.remove()
        add('bot', md("This is the **public static snapshot** of Kuya Hermes. Live agent replies run on our **local demo** (`web/app.py` connected to Hermes Gateway) and on **Telegram (@kuyahermes_bot)**.\n\nAll numbers on this dashboard reflect real Suki Mart data as of Sep 30, 2026."))
        return
      }
      let data
      const contentType = r.headers.get('content-type') || ''
      if (contentType.includes('application/json')) {
        try {
          data = await r.json()
        } catch (jsonErr) {
          throw new Error(`Invalid response format from server (${jsonErr.message})`)
        }
      } else {
        const textPayload = await r.text()
        if (!r.ok) {
          throw new Error(`Server returned HTTP ${r.status}: ${textPayload.slice(0, 140) || r.statusText}`)
        }
        data = { reply: textPayload }
      }

      thinking.remove()

      if (data.error) {
        const errEl = add('bot', `
          <div class="chat-callout chat-callout-error" role="alert">
            <div class="chat-callout-title">⚠️ Service Notice</div>
            <div class="chat-callout-body">${esc(data.error)}</div>
            <div class="chat-callout-actions">
              <button type="button" class="btn btn-sm chat-retry-btn">Retry</button>
            </div>
          </div>`, 'error-bubble')
        errEl.querySelector('.chat-retry-btn')?.addEventListener('click', () => ask(q))
      } else {
        const used = [...new Set((data.tools || []).filter((t) => /suki/.test(t)).map((t) => t.replace(/^mcp_+suki_+/, '')))]
        const toolsMarkup = used.length ? `<div class="tools">${used.map((t) => `<span class="chip">🔧 ${esc(t)}</span>`).join('')}<span class="muted" style="font-size:11px;margin-left:4px">${Math.round((Date.now() - started) / 1000)}s</span></div>` : ''
        
        let replyHtml = md(data.reply || '(no reply)')
        
        // Structured approval card if Kuya is proposing an action
        const needsApproval = /i-file ko na|confirm|approve|\?\s*$/i.test(data.reply || '')
        if (needsApproval) {
          replyHtml += `
            <div class="proposal-card">
              <div class="proposal-head">${icon('shield', 'icon')} Action confirmation required</div>
              <div class="proposal-actions">
                <button class="proposal-btn yes" data-confirm="yes">✓ Yes, file it</button>
                <button class="proposal-btn no" data-confirm="no">Not yet</button>
              </div>
            </div>`
        }

        const botMsg = add('bot', replyHtml + toolsMarkup)

        // Attach listeners to proposal buttons if present
        if (needsApproval) {
          botMsg.querySelectorAll('.proposal-btn').forEach((btn) => {
            btn.addEventListener('click', () => {
              if (btn.dataset.confirm === 'yes') {
                ask('Oo, i-file mo na')
              } else {
                ask('Hindi muna, patingin muna ng details')
              }
            })
          })
          setQuick(['Oo, i-file mo na', 'Hindi muna', 'Ipakita ang detalye'])
        } else {
          setQuick(['Fix stockouts there', 'Cover shift gaps', 'Run full sweep'])
        }
        document.dispatchEvent(new CustomEvent('kuya:reply', { detail: data }))
      }
    } catch (e) {
      thinking.remove()
      const errEl = add('bot', `
        <div class="chat-callout chat-callout-error" role="alert">
          <div class="chat-callout-title">⚠️ Connection Error</div>
          <div class="chat-callout-body">${esc(e.message || 'Unable to connect to Kuya Hermes backend.')}</div>
          <div class="chat-callout-actions">
            <button type="button" class="btn btn-sm chat-retry-btn">Retry</button>
          </div>
        </div>`, 'error-bubble')
      errEl.querySelector('.chat-retry-btn')?.addEventListener('click', () => ask(q))
    } finally {
      busy = false
      root.classList.remove('busy')
      input.focus()
    }
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault()
    const v = input.value
    input.value = ''
    if (v.trim()) AppleAudio.playSend()
    ask(v)
  })

  soundToggle.addEventListener('click', () => {
    const nowMuted = AppleAudio.toggleMute()
    soundToggle.classList.toggle('is-muted', nowMuted)
    soundToggle.setAttribute('aria-pressed', String(nowMuted))
    soundToggle.title = nowMuted ? 'Unmute sound' : 'Mute sound'
    soundToggle.innerHTML = icon(nowMuted ? 'soundOff' : 'soundOn')
  })

  root.querySelector('.chat-reset').addEventListener('click', () => {
    removeStoredConv()
    location.reload()
  })

  return { ask }
}

// ---------------------------------------------------------------- Interactive Telegram Floor Simulator
export function mountFloorDemo(container) {
  if (!container) return
  
  const scenarios = {
    water: [
      { who: 'user', text: 'ubos na ang bottled water sa Ermita, wala pang PO 😩' },
      { who: 'bot', text: 'Checked Ermita (ERM):\n• **Bottled Water 6L**: 0 on hand (daily avg: 42 bottles)\n• **Open PO**: None found\n• Supplier real lead time: **3.1 days**\n\nI-draft ko na ba ang PO para sa **5 cases**?' }
    ],
    shift: [
      { who: 'user', text: 'di pumasok si John Soriano bukas 7am sa Alabang' },
      { who: 'bot', text: 'Nakita ko: **cashier shift Oct 1, 07:00–11:00** sa ALB.\n\nBest cover: **Rowena Tomas** (1 absence in 8 weeks, free that slot).\n\nI-book ko na ba si Rowena?' }
    ],
    risk: [
      { who: 'user', text: 'aling branch ang pinaka-delikado ngayon?' },
      { who: 'bot', text: '🔥 **Ermita (ERM)** has the highest risk score: **66.0**.\n\n• 14 stockouts with **no purchase order**\n• 44 items below reorder point\n• Recommend running stockout fix for ERM immediately.' }
    ]
  }

  const messagesBox = container.querySelector('.phone-messages')
  const triggers = container.querySelectorAll('.phone-chip-trigger')

  function renderScenario(key) {
    const list = scenarios[key] || scenarios.water
    messagesBox.innerHTML = ''
    
    // First message immediately
    const userMsg = document.createElement('div')
    userMsg.className = 'tg-bubble user'
    userMsg.textContent = list[0].text
    messagesBox.appendChild(userMsg)

    // Second message with subtle delay to simulate Kuya processing
    setTimeout(() => {
      const botMsg = document.createElement('div')
      botMsg.className = 'tg-bubble bot'
      botMsg.innerHTML = md(list[1].text) + `
        <div class="tg-actions">
          <button type="button" class="tg-action-btn" data-action="confirm">Oo, i-file mo ✅</button>
          <button type="button" class="tg-action-btn" data-action="cancel">Iba na lang</button>
        </div>`
      messagesBox.appendChild(botMsg)

      botMsg.querySelectorAll('.tg-action-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
          const isConfirm = btn.dataset.action === 'confirm'
          const followUpUser = document.createElement('div')
          followUpUser.className = 'tg-bubble user'
          followUpUser.textContent = isConfirm ? 'oo' : 'huwag muna'
          messagesBox.appendChild(followUpUser)

          setTimeout(() => {
            const finalBot = document.createElement('div')
            finalBot.className = 'tg-bubble bot'
            finalBot.innerHTML = isConfirm 
              ? '✅ <strong>Na-file na!</strong> PO sent to supplier. Status: in_transit. Updated inventory alert in store.db.'
              : '👍 Cancelled. Walang binago sa database.'
            messagesBox.appendChild(finalBot)
            messagesBox.scrollTop = messagesBox.scrollHeight
          }, 350)
        })
      })

      messagesBox.scrollTop = messagesBox.scrollHeight
    }, 400)
  }

  triggers.forEach((t) => {
    t.addEventListener('click', () => {
      renderScenario(t.dataset.scenario)
    })
  })

  // Start with water scenario
  renderScenario('water')
}
