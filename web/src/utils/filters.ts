import type { CalendarEvent, FilterOptions } from '../types'
import { parseDate } from './dataLoader'

export function filterEvents(events: CalendarEvent[], filters: FilterOptions): CalendarEvent[] {
  return events.filter(event => {
    if (filters.category && event.category !== filters.category) {
      return false
    }

    if (filters.searchText) {
      const search = filters.searchText.toLowerCase()
      const searchIn = [
        event.team1,
        event.team2,
        event.category,
        event.other
      ].join(' ').toLowerCase()

      if (!searchIn.includes(search)) {
        return false
      }
    }

    if (filters.dateFrom || filters.dateTo) {
      const eventDate = parseDate(event.date)
      if (!eventDate) return false

      if (filters.dateFrom) {
        const fromDate = new Date(filters.dateFrom)
        fromDate.setHours(0, 0, 0, 0)
        if (eventDate < fromDate) return false
      }

      if (filters.dateTo) {
        const toDate = new Date(filters.dateTo)
        toDate.setHours(23, 59, 59, 999)
        if (eventDate > toDate) return false
      }
    }

    return true
  })
}

export function sortEvents(events: CalendarEvent[]): CalendarEvent[] {
  return [...events].sort((a, b) => {
    const dateA = parseDate(a.date)
    const dateB = parseDate(b.date)

    if (!dateA && !dateB) return 0
    if (!dateA) return 1
    if (!dateB) return -1

    if (dateA.getTime() !== dateB.getTime()) {
      return dateA.getTime() - dateB.getTime()
    }

    return a.time.localeCompare(b.time)
  })
}

export function groupEventsByDate(events: CalendarEvent[]): Map<string, CalendarEvent[]> {
  const grouped = new Map<string, CalendarEvent[]>()

  for (const event of events) {
    const date = event.date
    if (!grouped.has(date)) {
      grouped.set(date, [])
    }
    grouped.get(date)!.push(event)
  }

  return grouped
}
