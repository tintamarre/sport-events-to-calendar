# CPLiège Calendar Web Viewer

A Vue 3 + TypeScript + Tailwind CSS web application for viewing CPLiège basketball calendars.

## Features

- Browse calendars by club
- Filter by category/division
- Filter by date range
- Search for specific teams
- URL-based filtering for deep linking
- Download ICS and CSV files
- Responsive design

## Development

### Using Make (recommended)

```bash
# View all available commands
make help

# Install dependencies
make install

# Start development server
make dev

# Build for production
make build

# Preview production build
make preview
```

### Using Docker

```bash
# Start development server with hot reload
make docker-dev
# or
docker-compose up dev

# Build and run production server
make docker-prod
# or
docker-compose up --build prod

# Stop containers
make docker-stop

# Clean up containers and images
make docker-clean
```

### Using npm directly

```bash
# Install dependencies
npm install

# Generate data manifest
npm run generate-manifest

# Start development server
npm run dev

# Build for production
npm run build
```

## URL Filtering

The application supports URL query parameters for filtering:

- `club`: Club slug (e.g., `1034-rbc-haneffe`)
- `category`: Category name (e.g., `DD - DIVISION 2 A`)
- `from`: Start date (YYYY-MM-DD)
- `to`: End date (YYYY-MM-DD)
- `q`: Search text

Example:
```
/#/?club=1034-rbc-haneffe&category=U%2012%20-%20MM%20B&from=2026-01-17&to=2026-01-24
```

## Deployment

The application is automatically built and deployed to GitHub Pages via GitHub Actions after each calendar update.
