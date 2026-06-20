const api = {
    getSpots: () => fetch('/api/spots').then(r => r.json()),
    reserve: (id) => fetch(`/api/spots/${id}/reserve`, { method: 'POST' }).then(r => r.json()),
    release: (id) => fetch(`/api/spots/${id}/release`, { method: 'POST' }).then(r => r.json()),
    sensor: (id, occupied) => fetch('/api/sensor', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, occupied }) }).then(r => r.json())
}

function render(spots) {
    const container = document.getElementById('spots')
    // Map existing cards by spot id for in-place updates
    const existing = new Map()
    Array.from(container.children).forEach(child => {
        const id = child.dataset && child.dataset.spotId
        if (id) existing.set(id, child)
    })

    const seen = new Set()
    spots.forEach((s, idx) => {
        seen.add(String(s.id))
        let card = existing.get(String(s.id))
        const isNew = !card

        if (isNew) {
            card = document.createElement('div')
            card.className = 'spot-card'
            card.setAttribute('role', 'group')
            card.dataset.spotId = String(s.id)
            card.style.setProperty('--d', (idx * 70) + 'ms')
            card.classList.add('grow-ans')

            const inner = document.createElement('div')
            inner.className = 'card-inner'

            const idEl = document.createElement('div')
            idEl.className = 'spot-id'
            idEl.textContent = `Spot ${s.id}`

            const status = document.createElement('div')
            status.className = 'spot-status'
            const pill = document.createElement('span')
            pill.className = 'status-pill'
            status.appendChild(pill)

            const btnRow = document.createElement('div')
            btnRow.className = 'btn-row'

            const btn = document.createElement('button')
            btn.className = 'primary'

            const sim = document.createElement('button')
            sim.className = 'ghost'
            sim.textContent = 'Sensor'
            sim.title = 'Toggle via sensor'

            btnRow.appendChild(btn)
            btnRow.appendChild(sim)

            inner.appendChild(idEl)
            inner.appendChild(status)
            inner.appendChild(btnRow)
            card.appendChild(inner)

            // append in order
            container.appendChild(card)
        }

        // update attributes and content without recreating nodes
        card.classList.toggle('occupied', !!s.occupied)
        card.classList.toggle('free', !s.occupied)
        card.setAttribute('aria-label', `Spot ${s.id} ${s.occupied ? 'Occupied' : 'Free'}`)

        const pill = card.querySelector('.status-pill')
        if (pill) {
            pill.className = 'status-pill ' + (s.occupied ? 'status-occupied' : 'status-free')
            pill.textContent = s.occupied ? 'Occupied' : 'Free'
        }

        const btn = card.querySelector('button.primary')
        if (btn) {
            btn.textContent = s.occupied ? 'Release' : 'Reserve'
            // replace onclick to capture current spot state
            btn.onclick = () => {
                const action = s.occupied ? api.release : api.reserve
                // optimistically update UI to avoid flicker; then refresh
                btn.disabled = true
                action(s.id).then(() => load()).finally(() => { btn.disabled = false })
            }
        }

        const sim = card.querySelector('button.ghost')
        if (sim) {
            sim.onclick = () => {
                sim.disabled = true
                api.sensor(s.id, !s.occupied).then(() => load()).finally(() => { sim.disabled = false })
            }
        }

        // remove possible animation class after first reveal to avoid retrigger on updates
        if (!isNew) {
            card.classList.remove('grow-ans')
        }
    })

    // remove any cards that no longer exist
    Array.from(container.children).forEach(child => {
        const id = child.dataset && child.dataset.spotId
        if (id && !seen.has(id)) child.remove()
    })
}

function load() {
    api.getSpots().then(render)
}

// subscribe to server-sent events for real-time updates
function subscribeEvents() {
    if (!window.EventSource) return
    try {
        const es = new EventSource('/api/events')
        es.onmessage = (ev) => {
            try {
                const data = JSON.parse(ev.data)
                if (data && data.type === 'update' && data.spot) {
                    // update only the changed spot by reloading full list or merging
                    load()
                }
            } catch (e) {
                console.error('Invalid SSE payload', e)
            }
        }
        es.onerror = (e) => {
            console.warn('SSE error, falling back to polling', e)
            // fallback: poll periodically
            setInterval(load, 3000)
            es.close()
        }
    } catch (e) {
        console.warn('SSE not available, falling back to polling')
        setInterval(load, 3000)
    }
}

window.onload = () => { load(); subscribeEvents(); }

// Theme toggle
function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    const btn = document.getElementById('theme-toggle');
    if (btn) {
        btn.textContent = t === 'light' ? '☀️' : '🌙';
        btn.setAttribute('aria-pressed', t === 'light');
    }
}

function initTheme() {
    try {
        const saved = localStorage.getItem('theme');
        const initial = saved || (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
        applyTheme(initial);
        const tbtn = document.getElementById('theme-toggle');
        if (tbtn) {
            tbtn.addEventListener('click', () => {
                const current = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
                applyTheme(current);
                try { localStorage.setItem('theme', current); } catch (e) { }
            })
        }
    } catch (e) { console.warn('Theme init failed', e) }
}

initTheme();
