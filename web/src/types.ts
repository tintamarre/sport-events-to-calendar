export interface CalendarEvent {
  code: string
  date: string
  time: string
  team1: string
  team2: string
  category: string
  other: string
  location?: string
}

export interface Club {
  id: string
  name: string
  slug: string
  categories: string[]
  jsonPath: string | null
  csvPath: string
  icsFiles: { [category: string]: string }
}

export interface DataManifest {
  lastUpdated: string
  clubs: Club[]
}

export interface ClubData {
  club: {
    id: string
    name: string
    slug: string
  }
  events: CalendarEvent[]
}

export interface FilterOptions {
  club?: string
  category?: string
  dateFrom?: string
  dateTo?: string
  searchText?: string
}
