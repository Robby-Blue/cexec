function parseTimestamp(timestamp) {
    return new Date(timestamp.replace(' ', 'T') + 'Z')
}

function formatTimespan(dt1, dt2) {
    const t1 = parseTimestamp(dt1)
    const t2 = parseTimestamp(dt2)
    let seconds = Math.round((t2 - t1) / 1000)

    const units = [
        ['day', 86400],
        ['hour', 3600],
        ['minute', 60],
        ['second', 1],
    ]

    const parts = []
    let remaining = seconds

    for (const [name, secs] of units) {
        const value = Math.floor(remaining / secs)
        remaining = remaining % secs
        if (value > 0) {
            const displayName = value !== 1 ? `${name}s` : name
            parts.push(`${value} ${displayName}`)
        }
        if (parts.length === 2) break
    }

    if (parts.length === 0) return "instantly"
    if (parts.length === 1) return parts[0]
    return `${parts[0]} and ${parts[1]}`
}

export {
    parseTimestamp,
    formatTimespan
}