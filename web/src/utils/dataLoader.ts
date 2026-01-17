import type { CalendarEvent, DataManifest } from '../types'

const BASE_PATH = import.meta.env.DEV ? '/data' : '/sport-events-to-calendar/data'

export async function loadManifest(): Promise<DataManifest> {
  const response = await fetch(`${BASE_PATH}/manifest.json`)
  if (!response.ok) {
    throw new Error('Failed to load manifest')
  }
  return response.json()
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
