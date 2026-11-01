# Claveria Escape

A community tourism guide to Claveria, Misamis Oriental, Philippines — staycations and resorts, waterfalls, cafés and restaurants, and emergency hotlines along Route 955.

Built from the [Claveria Escape Google Drive folder](https://drive.google.com/drive/u/1/folders/16dP8wM5esssPabmrOSprLUBkZwjeTtGK), including its place descriptions, rates, contacts, photographs, logo and homepage image.

## Features
- 14 staycations and resorts, 6 waterfalls, 12 cafés and restaurants, and 10 emergency hotline contacts
- A mobile-first Explore → coffee-shop list → place detail flow, with search and filters based on the place data
- 32 place-detail pages with photo galleries, interactive OpenStreetMap embeds, Google Maps directions, share/save/contact actions, rates and hours where supplied
- Overview map with all 32 place pins, plus an OSM fallback; four pins are explicitly marked approximate
- Saved places stored locally in the visitor's browser, category search, photo lightbox and tap-to-call hotline cards
- Touch-friendly controls, safe-area support and an accessible collapsible menu
- No fabricated ratings or reviews; decorative emoji removed in favor of photography, typography and clear labels
- Static HTML, CSS and JavaScript; no application server required to serve the site. Map tiles are provided by OpenStreetMap.

## Project structure
```
index.html            # homepage
staycation.html       # staycations and resorts
falls.html            # waterfalls
cafes.html            # cafés and restaurants
hotlines.html         # emergency hotlines
map.html              # interactive overview map and location directory
saved.html            # browser-local saved-place list
place/<slug>.html     # 32 detail pages
assets/css/style.css  # responsive styles
assets/js/main.js     # navigation, search, favorites, share and galleries
assets/js/map.js      # overview map pins and map filters
assets/js/leaflet.js  # locally served Leaflet library
assets/vendor/leaflet # Leaflet stylesheet and license
assets/img/...        # optimized photos and brand assets
data/places.json      # structured place data and map coordinates
data/map_locations.json # map pins for individual places
tools/                # image and site-generation scripts
sitemap.xml
```

## Run locally
```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Rebuild
```bash
python3 tools/build.py
```

The generated site is currently served at [claveria-website-ovus.vercel.app](https://claveria-website-ovus.vercel.app). The Vercel project is in the [claveria1 workspace](https://vercel.com/claveria1); GitHub status checks report Vercel deployments for commits on the repository.
