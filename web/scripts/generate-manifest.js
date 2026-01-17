import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const dataDir = path.join(__dirname, '../../data')
const outputPath = path.join(dataDir, 'manifest.json')

function extractClubInfo(dirName) {
  const match = dirName.match(/^(\d+)-(.+)$/)
  if (!match) return null

  return {
    id: match[1],
    slug: dirName,
    name: match[2]
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }
}

function extractCategoryFromICS(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8')
    const match = content.match(/X-WR-CALNAME:.+? - (.+)$/m)
    if (match) {
      return match[1].trim()
    }
  } catch (e) {
    console.warn(`Failed to read ICS file: ${filePath}`)
  }
  return null
}

function generateManifest() {
  console.log('Generating manifest from data directory...')

  if (!fs.existsSync(dataDir)) {
    console.error(`Data directory not found: ${dataDir}`)
    process.exit(1)
  }

  const clubs = []
  const entries = fs.readdirSync(dataDir, { withFileTypes: true })

  for (const entry of entries) {
    if (!entry.isDirectory()) continue

    const clubInfo = extractClubInfo(entry.name)
    if (!clubInfo) continue

    const clubPath = path.join(dataDir, entry.name)
    const files = fs.readdirSync(clubPath)

    const csvFile = files.find(f => f.endsWith('.csv'))
    if (!csvFile) {
      console.warn(`No CSV file found for club: ${entry.name}`)
      continue
    }

    const icsFiles = files.filter(f => f.endsWith('.ics'))
    const categories = []
    const icsFilesMap = {}

    for (const icsFile of icsFiles) {
      const icsPath = path.join(clubPath, icsFile)
      const category = extractCategoryFromICS(icsPath)

      if (category) {
        categories.push(category)
        icsFilesMap[category] = `/data/${entry.name}/${icsFile}`
      }
    }

    categories.sort()

    clubs.push({
      id: clubInfo.id,
      name: clubInfo.name,
      slug: clubInfo.slug,
      categories,
      csvPath: `/data/${entry.name}/${csvFile}`,
      icsFiles: icsFilesMap
    })
  }

  clubs.sort((a, b) => a.name.localeCompare(b.name))

  const manifest = {
    lastUpdated: new Date().toISOString(),
    clubs
  }

  fs.writeFileSync(outputPath, JSON.stringify(manifest, null, 2))
  console.log(`✓ Manifest generated successfully!`)
  console.log(`  - ${clubs.length} clubs indexed`)
  console.log(`  - Output: ${outputPath}`)
}

generateManifest()
