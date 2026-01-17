# Outils pour transformer des calendriers en invitations calendriers

par Martin Erpicum

## Vue d'ensemble

Ce projet récupère automatiquement les calendriers de matchs de basketball depuis CPLiège (http://www.cpliege.be) et les convertit en fichiers CSV et ICS (iCalendar) pour faciliter leur intégration dans vos applications de calendrier.

Un site web interactif permet également de consulter et filtrer les matchs en ligne.

## Fonctionnalités

### Génération de calendriers (Python)
- Récupération automatique des matchs depuis cpliege.be
- Export en format CSV et ICS pour chaque club et catégorie
- Mise à jour automatique via GitHub Actions (chaque jeudi)

### Application web (Vue.js)
- Interface interactive pour consulter les calendiers
- Filtrage par club, catégorie, date et équipe
- Liens directs avec paramètres URL
- Téléchargement des fichiers ICS et CSV

## Utilisation

### Consulter les calendriers en ligne
Visitez l'application web: https://geantvert.github.io/sport-events-to-calendar/ *(à configurer dans les paramètres GitHub)*

### Télécharger les fichiers
Les fichiers CSV et ICS sont disponibles dans le dossier `/data/` de ce dépôt.

### Exécuter localement

#### Génération des calendriers
```bash
uv run basket-to-calendar.py
```

#### Application web
```bash
cd web
npm install
npm run generate-manifest
npm run dev
```

## Structure du projet

```
.
├── basket-to-calendar.py   # Script Python pour récupérer les calendriers
├── data/                   # Calendriers générés (CSV/ICS)
│   ├── manifest.json      # Index des clubs et catégories
│   └── [club-folders]/    # Dossiers par club
├── web/                   # Application web Vue.js
│   ├── src/              # Code source
│   └── scripts/          # Scripts de génération
└── docs/                 # Build de production (GitHub Pages)
```

## Licence

Ce code est publié sous do WTFPL, voir le fichier `LICENSE` pour plus de détails.
