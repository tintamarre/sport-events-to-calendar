import type { CalendarEvent, DataManifest, ClubData, Club } from '../types'

const BASE_PATH = import.meta.env.DEV ? '/data' : '/sport-events-to-calendar/data'

export async function loadManifest(): Promise<DataManifest> {
  const response = await fetch(`${BASE_PATH}/manifest.json`)
  if (!response.ok) {
    throw new Error('Failed to load manifest')
  }
  return response.json()
}

export async function loadClubJSON(club: Club): Promise<CalendarEvent[]> {
  if (!club.jsonPath) {
    // Fallback to CSV if JSON not available
    return loadClubEvents(club.csvPath)
  }

  const fullPath = import.meta.env.DEV ? club.jsonPath : `/sport-events-to-calendar${club.jsonPath}`
  const response = await fetch(fullPath)
  if (!response.ok) {
    throw new Error(`Failed to load JSON: ${club.jsonPath}`)
  }

  const data: ClubData = await response.json()

  // Convert date format from YYYY-MM-DD to DD/MM/YYYY for consistency
  return data.events.map(event => ({
    ...event,
    date: formatDateForDisplay(event.date)
  }))
}

function formatDateForDisplay(dateStr: string): string {
  // Convert YYYY-MM-DD to DD/MM/YYYY
  const parts = dateStr.split('-')
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`
  }
  return dateStr
}

export async function loadClubEvents(csvPath: string): Promise<CalendarEvent[]> {
  const fullPath = import.meta.env.DEV ? csvPath : `/sport-events-to-calendar${csvPath}`
  const response = await fetch(fullPath)
  if (!response.ok) {
    throw new Error(`Failed to load CSV: ${csvPath}`)
  }

  const text = await response.text()
  const lines = text.trim().split('\n')

  if (lines.length < 2) return []

  const events: CalendarEvent[] = []

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue

    const parts = line.split(',')
    if (parts.length >= 6) {
      events.push({
        code: parts[0],
        date: parts[1],
        time: parts[2],
        team1: parts[3],
        team2: parts[4],
        category: parts[5],
        other: parts[6] || ''
      })
    }
  }

  return events
}

// Generate ICS content client-side for download
export function generateICSFromEvents(events: CalendarEvent[], calName: string): string {
  const lines: string[] = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//CPLiège Calendar//cpliege.be//',
    `X-WR-CALNAME:${calName}`,
  ]

  for (const event of events) {
    const dateObj = parseDate(event.date)
    if (!dateObj) continue

    const [hours, minutes] = event.time.split(':').map(Number)
    dateObj.setHours(hours || 0, minutes || 0, 0, 0)

    const endDate = new Date(dateObj.getTime() + 2 * 60 * 60 * 1000) // 2 hours duration

    const uid = `${event.code}-${formatICSDate(dateObj)}@cpliege.be`
    const summary = `🏀 ${event.category}: ${event.team1} et ${event.team2}`
    const description = `[${event.code}] — ${summary}`
    const location = event.team1 || ''

    lines.push('BEGIN:VEVENT')
    lines.push(`UID:${uid}`)
    lines.push(`DTSTART:${formatICSDate(dateObj)}`)
    lines.push(`DTEND:${formatICSDate(endDate)}`)
    lines.push(`SUMMARY:${escapeICS(summary)}`)
    lines.push(`DESCRIPTION:${escapeICS(description)}`)
    lines.push(`LOCATION:${escapeICS(location)}`)
    lines.push('END:VEVENT')
  }

  lines.push('END:VCALENDAR')
  return lines.join('\r\n')
}

function formatICSDate(date: Date): string {
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}T${pad(date.getHours())}${pad(date.getMinutes())}00`
}

function escapeICS(str: string): string {
  return str.replace(/[\\;,]/g, c => `\\${c}`).replace(/\n/g, '\\n')
}

// Download ICS file
export function downloadICS(events: CalendarEvent[], calName: string, filename: string): void {
  const icsContent = generateICSFromEvents(events, calName)
  const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function parseDate(dateStr: string): Date | null {
  if (!dateStr) return null

  const parts = dateStr.split(/[-/]/)
  if (parts.length !== 3) return null

  let year: number, month: number, day: number

  if (parts[0].length === 4) {
    // YYYY-MM-DD format
    year = parseInt(parts[0])
    month = parseInt(parts[1]) - 1
    day = parseInt(parts[2])
  } else {
    // DD/MM/YYYY format
    year = parseInt(parts[2])
    month = parseInt(parts[1]) - 1
    day = parseInt(parts[0])

    if (year < 100) {
      year += 2000
    }
  }

  const date = new Date(year, month, day)
  return isNaN(date.getTime()) ? null : date
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('fr-BE', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}

export function getWeekRange(date: Date = new Date()): { start: Date; end: Date } {
  const start = new Date(date)
  start.setDate(date.getDate() - date.getDay() + (date.getDay() === 0 ? -6 : 1))
  start.setHours(0, 0, 0, 0)

  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  end.setHours(23, 59, 59, 999)

  return { start, end }
}
