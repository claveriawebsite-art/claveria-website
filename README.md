# 🌿 Claveria Escape

A community tourism website for **Claveria, Misamis Oriental, Philippines** — staycations & resorts, waterfalls, coffee shops & restaurants, and emergency hotlines along scenic **Route 955**.

Built 100% from the content of the [Claveria Escape Google Drive folder](https://drive.google.com/drive/u/1/folders/16dP8wM5esssPabmrOSprLUBkZwjeTtGK) (descriptions, rates, contacts, photos, logo & homepage image).

## ✨ Features
- 🏕️ **14 staycations & resorts** · 💧 **6 waterfalls** · ☕ **12 cafés & restaurants** · 🚨 **10 emergency hotlines**
- Full photo galleries per spot with a lightbox viewer
- Per-place pages with location (Google Maps link), contacts (tap-to-call), rates, hours & "about"
- Live search/filter on every category page
- Fully static — no build step, no backend; deploys anywhere (Vercel, Netlify, GitHub Pages)

## 📁 Structure
```
index.html            # homepage (hero = Municipality of Claveria photo)
staycation.html       # category: staycations & resorts
falls.html            # category: waterfalls
cafes.html            # category: coffee shops & restaurants
hotlines.html         # emergency hotlines (tap-to-call)
place/<slug>.html     # one detail page per spot (32 pages)
assets/css/style.css  # styles (Claveria green theme from the logo)
assets/js/main.js     # nav, search, lightbox, reveal animations
assets/img/...        # optimized photos (135 images, WebP-ready JPEGs)
data/places.json      # all content as structured data
tools/                # build scripts (download, process, generate)
sitemap.xml
```

## 🚀 Run locally
```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## 🔧 Rebuild
```bash
python3 tools/download.py        # fetch images from Google Drive (needs public files)
python3 tools/process_images.py  # optimize into assets/img
python3 tools/build.py           # generate all HTML pages + sitemap + data/places.json
```

## 🌐 Deploy
Pushed to GitHub and deployed on **Vercel** (static site, zero config — see `vercel.json`).
