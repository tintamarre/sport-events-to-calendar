import ICAL from 'ical.js'
import type { CalendarEvent, DataManifest } from '../types'

const BASE_PATH = import.meta.env.DEV ? '/data' : '/sport-events-to-calendar/data'

export async function loadManifest(): Promise<DataManifest> {
  const response = await fetch(`${BASE_PATH}/manifest.json`)
  if (!response.ok) {
    throw new Error('Failed to load manifest')
  }
  return response.json()
}

export async function loadICSEvents(icsPath: string, categoryName: string): Promise<CalendarEvent[]> {
  const fullPath = import.meta.env.DEV ? icsPath : `/sport-events-to-calendar${icsPath}`
  const response = await fetch(fullPath)
  if (!response.ok) {
    throw new Error(`Failed to load ICS: ${icsPath}`)
  }

  const text = await response.text()
  const jcalData = ICAL.parse(text)
  const comp = new ICAL.Component(jcalData)
  const vevents = comp.getAllSubcomponents('vevent')

  const events: CalendarEvent[] = []

  for (const vevent of vevents) {
    const event = new ICAL.Event(vevent)
    const summary = event.summary || ''
    const startDate = event.startDate
    const code = event.uid ? event.uid.split('-')[0] : ''
    const description = event.description || ''

    // Extract teams from summary (format: "🏀 Category: Team1 et Team2")
    const match = summary.match(/:\s*(.+?)\s+et\s+(.+)$/)
    const team1 = match ? match[1].trim() : ''
    const team2 = match ? match[2].trim() : ''

    // Extract code from description if available (format: "[CODE] — ...")
    const codeMatch = description.match(/\[(\w+)\]/)
    const eventCode = codeMatch ? codeMatch[1] : code

    events.push({
      code: eventCode,
      date: startDate.toJSDate().toLocaleDateString('fr-BE', { day: '2-digit', month: '2-digit', year: 'numeric' }),
      time: startDate.toJSDate().toLocaleTimeString('fr-BE', { hour: '2-digit', minute: '2-digit' }),
      team1,
      team2,
      category: categoryName,
      other: ''
    })
  }

  return events
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

export async function loadAllClubEvents(club: any): Promise<CalendarEvent[]> {
  const allEvents: CalendarEvent[] = []

  // Load all ICS files for the club
  for (const [category, icsPath] of Object.entries(club.icsFiles)) {
    try {
      const events = await loadICSEvents(icsPath as string, category)
      allEvents.push(...events)
    } catch (e) {
      console.warn(`Failed to load ${category}:`, e)
    }
  }

  return allEvents
}

export function parseDate(dateStr: string): Date | null {
  if (!dateStr) return null

  const parts = dateStr.split(/[-/]/)
  if (parts.length !== 3) return null

  let year = parseInt(parts[2])
  const month = parseInt(parts[1]) - 1
  const day = parseInt(parts[0])

  if (year < 100) {
    year += 2000
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
