export interface CalendarEvent {
  code: string
  date: string
  time: string
  team1: string
  team2: string
  category: string
  other: string
}

export interface Club {
  id: string
  name: string
  slug: string
  categories: string[]
  csvPath: string
  icsFiles: { [category: string]: string }
}

export interface DataManifest {
  lastUpdated: string
  clubs: Club[]
}

export interface FilterOptions {
  club?: string
  category?: string
  dateFrom?: string
  dateTo?: string
  searchText?: string
}
