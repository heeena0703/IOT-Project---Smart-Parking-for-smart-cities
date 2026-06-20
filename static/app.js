const api = {
    getSpots: () => fetch('/api/spots').then(r => r.json()),
    reserve: (id) => fetch(`/api/spots/${id}/reserve`, { method: 'POST' }).then(r => r.json()),
    release: (id) => fetch(`/api/spots/${id}/release`, { method: 'POST' }).then(r => r.json()),
    sensor: (id, occupied) => fetch('/api/sensor', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, occupied }) }).then(r => r.json())
}

function render(spots) {
    const container = document.getElementById('spots')
    container.innerHTML = ''
    spots.forEach(s => {
        const div = document.createElement('div')
        div.className = 'spot ' + (s.occupied ? 'occupied' : 'free')
        div.innerHTML = `<strong>Spot ${s.id}</strong><div>${s.occupied ? 'Occupied' : 'Free'}</div>`

        const btn = document.createElement('button')
        btn.textContent = s.occupied ? 'Release' : 'Reserve'
        btn.onclick = () => {
            const action = s.occupied ? api.release : api.reserve
            action(s.id).then(() => load())
        }
        div.appendChild(btn)

        const sim = document.createElement('button')
        sim.textContent = 'Toggle (sensor)'
        sim.style.marginLeft = '6px'
        sim.onclick = () => {
            api.sensor(s.id, !s.occupied).then(() => load())
        }
        div.appendChild(sim)

        container.appendChild(div)
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
