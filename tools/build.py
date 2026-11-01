# -*- coding: utf-8 -*-
"""Static site generator for Claveria Escape."""
import html
import json
import os
import re
import unicodedata
from urllib.parse import quote

from site_data import SITE, CATEGORIES, PLACES, HOTLINES, HOTLINE_GROUPS

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMG = os.path.join(ROOT, "assets", "img")
with open(os.path.join(ROOT, "data", "map_locations.json"), encoding="utf-8") as f:
    MAP_LOCATIONS = json.load(f)
MAP_APPROXIMATE = {"mailig-falls", "bindol-falls", "lantawon-falls", "hamugaway-ni-dodongstan"}


def plain(s):
    """Drop decorative emoji/symbol glyphs from user-facing copy."""
    cleaned = []
    for ch in str(s):
        code = ord(ch)
        category = unicodedata.category(ch)
        if category == "So" or category == "Cf" or ch in "\ufe0e\ufe0f\u20e3":
            continue
        if 0x1F3FB <= code <= 0x1F3FF or 0xE0020 <= code <= 0xE007F:
            continue
        cleaned.append(ch)
    return "".join(cleaned).strip()


def esc(s):
    return html.escape(plain(s), quote=True)


def clean_data(value):
    if isinstance(value, str):
        return plain(value)
    if isinstance(value, list):
        return [clean_data(item) for item in value]
    if isinstance(value, tuple):
        return [clean_data(item) for item in value]
    if isinstance(value, dict):
        return {key: clean_data(item) for key, item in value.items()}
    return value


def maps_url(q):
    return "https://www.google.com/maps/search/?api=1&query=" + quote(q)


def osm_embed_url(slug):
    point = MAP_LOCATIONS.get(slug, {"lat": 8.6119415, "lon": 124.8933887})
    lat, lon = float(point["lat"]), float(point["lon"])
    lat_pad, lon_pad = 0.009, 0.009
    bbox = f"{lon - lon_pad:.6f},{lat - lat_pad:.6f},{lon + lon_pad:.6f},{lat + lat_pad:.6f}"
    marker = f"{lat:.7f},{lon:.7f}"
    return "https://www.openstreetmap.org/export/embed.html?bbox=" + quote(bbox, safe=",") + "&layer=mapnik&marker=" + quote(marker, safe=",")


def img_dir(cat, slug):
    d = os.path.join(IMG, cat, slug)
    if not os.path.isdir(d):
        return []
    files = sorted(f for f in os.listdir(d) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
    return [f"assets/img/{cat}/{slug}/{f}" for f in files]


def place_images(p):
    return img_dir(p["category"], p["slug"])


PIN = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
SEARCH = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>'
PHONE = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.08 4.18 2 2 0 0 1 4.06 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
INFO = {
    "pin": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "phone": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.08 4.18 2 2 0 0 1 4.06 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
    "clock": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "tag": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.6 13.4 12 22 2 12V2h10l8.6 8.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>',
}


def header(prefix, active):
    links = [
        ("index.html", "Home", ""),
        ("staycation.html", "Staycations", "staycation"),
        ("falls.html", "Falls", "falls"),
        ("cafes.html", "Cafés & Restos", "cafes"),
        ("hotlines.html", "Hotlines", "hotlines"),
    ]
    nav = "".join(
        f'<a href="{prefix}{href}" class="{"active" if act == active else ""} {"hot" if act == "hotlines" else ""}">{label}</a>'
        for href, label, act in links
    )
    return f'''<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="{prefix}index.html">
      <img src="{prefix}assets/img/brand/logo.png" alt="Claveria Escape logo" width="46" height="46">
      <span class="brand-text">Claveria Escape<small>Misamis Oriental</small></span>
    </a>
    <button class="burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="primary-navigation"><span></span><span></span><span></span></button>
    <nav class="nav-links" id="primary-navigation" aria-label="Primary navigation">{nav}</nav>
  </div>
</header>'''


def footer(prefix):
    year = 2026
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="{prefix}index.html">
          <img src="{prefix}assets/img/brand/logo.png" alt="Claveria Escape logo" width="54" height="54">
          <span class="brand-text" style="color:#fff">Claveria Escape<small>Misamis Oriental</small></span>
        </a>
        <p style="margin-top:14px;max-width:340px;font-size:.93rem">Your community guide to the highlands of Claveria — staycations, waterfalls, cafés & restaurants along scenic Route 955.</p>
      </div>
      <div>
        <h4>Explore</h4>
        <ul>
          <li><a href="{prefix}staycation.html">Staycations & Resorts</a></li>
          <li><a href="{prefix}falls.html">Waterfalls</a></li>
          <li><a href="{prefix}cafes.html">Coffee Shops & Restaurants</a></li>
          <li><a href="{prefix}hotlines.html">Emergency Hotlines</a></li>
        </ul>
      </div>
      <div>
        <h4>Good to know</h4>
        <ul>
          <li>Municipality of Claveria, Misamis Oriental, Philippines</li>
          <li>Most spots are along Route 955 (Gingoog–Claveria Road)</li>
          <li>Highland weather can be cold and misty — bring a jacket</li>
          <li>Save the <a href="{prefix}hotlines.html">emergency hotlines</a> before you go</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© {year} Claveria Escape — community tourism guide. Content compiled from the Claveria Escape community Drive folder.</span>
      <span>A community guide from Claveria, Misamis Oriental</span>
    </div>
  </div>
</footer>
<button class="back-top" aria-label="Back to top">Top</button>'''


def head(title, description, prefix, og=True):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#024023">
<title>{esc(title)} · Claveria Escape</title>
<meta name="description" content="{esc(description)}">
<meta property="og:title" content="{esc(title)} · Claveria Escape">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{prefix}assets/img/brand/og.jpg">
<link rel="icon" type="image/png" href="{prefix}assets/img/brand/favicon.png">
<link rel="apple-touch-icon" href="{prefix}assets/img/brand/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,700;0,9..144,900;1,9..144,600&family=DM+Sans:opsz,wght@9..40,400;9..40,600;9..40,700;9..40,800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/css/style.css">
</head>
<body>'''


def scripts(prefix):
    return f'<script src="{prefix}assets/js/main.js" defer></script>\n</body>\n</html>\n'


def place_card(p, prefix):
    imgs = place_images(p)
    thumb = imgs[0] if imgs else None
    warn = ' warn' if p["slug"] == "twin-falls" else ""
    badge_txt = "Temporarily closed" if p["slug"] == "twin-falls" else f"{len(imgs)} photos" if imgs else ""
    badge_html = f'<span class="badge{warn}">{esc(badge_txt)}</span>' if badge_txt else ""
    img_html = f'<img src="{prefix}{thumb}" alt="{esc(p["name"])}" loading="lazy" decoding="async">' if thumb else ""
    return f'''<a class="place-card reveal" href="{prefix}place/{p["slug"]}.html">
  <div class="thumb">{img_html}{badge_html}</div>
  <div class="body">
    <h3>{esc(p["name"])}</h3>
    <span class="tagline">{esc(p["tagline"])}</span>
    <span class="loc">{esc(p["location"])}</span>
  </div>
</a>'''


def category_page(cat_key):
    cat = CATEGORIES[cat_key]
    places = [p for p in PLACES if p["category"] == cat_key]
    cards = "\n".join(place_card(p, "") for p in places)
    body = f'''{header("", cat_key)}
<main>
  <section class="section" style="padding-bottom:20px">
    <div class="wrap">
      <div class="section-head">
        <div>
          <span class="eyebrow">Explore Claveria</span>
          <h2>{esc(cat['title'])}</h2>
          <p>{esc(cat['blurb'])}</p>
        </div>
        <span class="chip">{len(places)} places</span>
      </div>
      <div class="search-bar">
        <input id="place-search" type="search" placeholder="Search {esc(cat['title'].lower())} by name, barangay or tag" autocomplete="off">
      </div>
      <div class="card-grid" id="card-grid">
{cards}
      </div>
      <div class="no-results" id="no-results">No places match your search. Try another name or barangay.</div>
    </div>
  </section>
</main>
{footer("")}'''
    return head(cat["title"], cat["blurb"] + f" — {len(places)} places in Claveria, Misamis Oriental.", "") + body + scripts("")


def place_page(p):
    prefix = "../"
    cat = CATEGORIES[p["category"]]
    imgs = place_images(p)
    gallery = ""
    for i, src in enumerate(imgs):
        cls = "g-main" if i == 0 else ""
        gallery += f'<figure class="{cls}"><img src="{prefix}{src}" alt="{esc(p["name"])} photo {i+1}" loading="{"eager" if i==0 else "lazy"}" decoding="async"></figure>'
    if not gallery:
        gallery = '<figure class="g-main"><img src="../assets/img/brand/og.jpg" alt="Claveria"></figure>'

    contacts = ""
    for label, value, href in p["contact"]:
        action = "Call" if href.startswith("tel:") else "Email" if href.startswith("mailto:") else "Message" if "wa.me" in href else "Open"
        contacts += f'<a class="contact-link" href="{esc(href)}"><span><small>{esc(label)}</small><br>{esc(value)}</span><span class="contact-action">{action}</span></a>'
    if not contacts:
        contacts = '<p style="color:var(--muted);font-size:.92rem">No direct contact listed — ask locals or check their Facebook page.</p>'

    extras = ""
    for label, text in p["extras"]:
        extras += f'<div class="info-block"><div class="label">{esc(label)}</div><p>{esc(text)}</p></div>'

    tags = "".join(f'<span class="chip">#{esc(t)}</span>' for t in p["tags"])
    related = [q for q in PLACES if q["category"] == p["category"] and q["slug"] != p["slug"]][:3]
    related_cards = "\n".join(place_card(q, "../") for q in related)

    warn_chip = '<span class="chip warn">Temporarily closed</span>' if p["slug"] == "twin-falls" else ""
    map_note = (
        "Pin marks the nearest mapped area; use Google Maps to verify the exact spot and plan directions."
        if p["slug"] in MAP_APPROXIMATE
        else "Pan or zoom to explore. Use Google Maps for turn-by-turn directions."
    )
    map_html = f'''<section class="place-map reveal" aria-labelledby="place-map-title">
  <div class="place-map-head">
    <div>
      <span class="eyebrow">Location</span>
      <h2 id="place-map-title">Explore the area</h2>
      <p>{esc(p["location"])}</p>
    </div>
    <a class="btn btn-green map-directions" href="{esc(maps_url(p["maps_query"]))}" target="_blank" rel="noopener">Directions on Google Maps</a>
  </div>
  <div class="map-frame">
    <iframe title="Interactive map for {esc(p["name"])}" src="{esc(osm_embed_url(p["slug"]))}" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
  </div>
  <p class="map-note">{esc(map_note)} Map data © OpenStreetMap contributors.</p>
</section>'''
    body = f'''{header(prefix, p["category"])}
<main>
  <div class="wrap">
    <nav class="crumbs"><a href="{prefix}index.html">Home</a> › <a href="{prefix}{p["category"]}.html">{esc(cat["title"])}</a> › {esc(p["name"])}</nav>
    <div class="place-hero">
      <h1>{esc(p["name"])}</h1>
      <p class="tagline">{esc(p["tagline"])}</p>
      <div class="meta-row">
        <span class="chip">{esc(cat["title"])}</span>
        {warn_chip}
        {tags}
      </div>
    </div>
    <div class="place-layout">
      <div>
        <div class="gallery" id="gallery">
{gallery}
        </div>
        <div class="about-section" style="margin-top:30px">
          <h2>About {esc(p["name"])}</h2>
          <p>{esc(p["about"])}</p>
        </div>
      </div>
      <aside class="info-card">
        <h2>Visitor info</h2>
        <div class="info-block">
          <div class="label">Location</div>
          <p>{esc(p["location"])}</p>
        </div>
        <div class="info-block">
          <div class="label">Contact</div>
          {contacts}
        </div>
        {extras}
      </aside>
    </div>
    {map_html}
    <section class="related">
      <h2>More {esc(cat["title"].lower())} in Claveria</h2>
      <div class="card-grid">
{related_cards}
      </div>
    </section>
  </div>
</main>
<div class="lightbox" id="lightbox" role="dialog" aria-label="Photo viewer">
  <button class="lb-close" aria-label="Close">×</button>
  <button class="lb-nav lb-prev" aria-label="Previous">‹</button>
  <img src="" alt="">
  <button class="lb-nav lb-next" aria-label="Next">›</button>
  <div class="lb-count"></div>
</div>
{footer(prefix)}'''
    desc = f"{p['tagline']} — {p['location']}. {p['about'][:140]}…"
    return head(p["name"], desc, prefix) + body + scripts(prefix)


def hotlines_page():
    groups_html = ""
    by_name = {h[0]: h for h in HOTLINES}
    for gtitle, names in HOTLINE_GROUPS:
        cards = ""
        for n in names:
            h = by_name[n]
            cards += f'''<div class="hl-card">
  <div class="hl-details"><div class="hl-name">{esc(h[0])}</div><div class="hl-num">{esc(h[1])}</div></div>
  <a class="call-btn" href="{esc(h[2])}" aria-label="Call {esc(h[1])}">Call</a>
</div>'''
        groups_html += f'<div class="hl-group"><h2>{esc(gtitle)}</h2><div class="hl-grid">{cards}</div></div>'
    body = f'''{header("", "hotlines")}
<main>
  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <div>
          <span class="eyebrow">Travel information</span>
          <h2>Claveria Emergency Hotlines</h2>
          <p>Keep these numbers saved on your phone while exploring Claveria, Misamis Oriental. Tap the green button to call directly.</p>
        </div>
      </div>
      <div class="emergency-banner">
        <div>
          <h2>General emergency</h2>
          <p>For any life-threatening emergency anywhere in the Philippines, dial the national emergency hotline.</p>
        </div>
        <a class="btn" href="tel:911">Call 911</a>
      </div>
{groups_html}
      <div class="hl-note">Numbers compiled from the official <em>Claveria Emergency Hotlines</em> list (MDDRMO Claveria, Municipal Police Station, MisOr PDRRMO & hospital contacts). Save them before heading to the highlands — signal can be spotty in mountain barangays.</div>
    </div>
  </section>
</main>
{footer("")}'''
    return head("Emergency Hotlines", "Claveria, Misamis Oriental emergency hotlines — MDDRMO, police, hospital & rescue contacts. Save them before you travel.", "") + body + scripts("")


def index_page():
    cats_html = ""
    for key in ("staycation", "falls", "cafes"):
        cat = CATEGORIES[key]
        n = len([p for p in PLACES if p["category"] == key])
        sample = next(p for p in PLACES if p["category"] == key)
        imgs = place_images(sample)
        img = imgs[0] if imgs else "assets/img/brand/hero.jpg"
        cats_html += f'''<a class="cat-card reveal" href="{key}.html">
  <div class="cat-img"><img src="{img}" alt="{esc(cat['title'])}" loading="lazy" decoding="async"></div>
  <span class="count">{n} places</span>
  <div class="cat-body">
    <div class="cat-kicker">{key.upper()}</div>
    <h3>{esc(cat['title'])}</h3>
    <p>{esc(cat['blurb'])}</p>
  </div>
</a>'''
    featured = [p for p in PLACES if p["slug"] in ("baqs-bonfires", "cabinscape-ridge-resort", "lantawon-falls", "skye-88-cafe", "lone-wolf-cafe", "hiraya-farm-escape")]
    feat_cards = "\n".join(place_card(p, "") for p in featured)
    counts = {k: len([p for p in PLACES if p["category"] == k]) for k in ("staycation", "falls", "cafes")}
    body = f'''{header("", "")}
<main>
  <section class="hero">
    <div class="hero-bg"><img src="assets/img/brand/hero.jpg" alt="Municipality of Claveria, Misamis Oriental" fetchpriority="high" decoding="async"></div>
    <div class="hero-content">
      <h1>Escape to <em>Claveria</em></h1>
      <p class="sub">Cool mountain air, hidden waterfalls, cozy cabins and the best café stops along Route 955 — your complete guide to Claveria, Misamis Oriental.</p>
      <div class="hero-cta">
        <a class="btn btn-lime" href="staycation.html">Explore Staycations</a>
        <a class="btn btn-ghost" href="falls.html">Find Waterfalls</a>
        <a class="btn btn-ghost" href="cafes.html">Café & Resto Stops</a>
      </div>
      <div class="hero-stats">
        <div class="stat"><b>{counts['staycation']}</b><span>Staycations</span></div>
        <div class="stat"><b>{counts['falls']}</b><span>Waterfalls</span></div>
        <div class="stat"><b>{counts['cafes']}</b><span>Cafés & Restos</span></div>
        <div class="stat"><b>{len(HOTLINES)}</b><span>Hotlines</span></div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <div>
          <span class="eyebrow">Discover</span>
          <h2>What do you want to explore today?</h2>
          <p>Three ways to experience the Claveria highlands — pick a trail, a bed, or a brew.</p>
        </div>
      </div>
      <div class="cat-grid">
{cats_html}
      </div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap">
      <div class="section-head">
        <div>
          <span class="eyebrow">Handpicked</span>
          <h2>Featured spots</h2>
          <p>A few favorites from the community — from bonfire camps to glass-house cafés.</p>
        </div>
        <a class="btn btn-green" href="staycation.html">View all</a>
      </div>
      <div class="card-grid">
{feat_cards}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <div>
          <span class="eyebrow">Why Claveria</span>
          <h2>The highland escape of Misamis Oriental</h2>
        </div>
      </div>
      <div class="why-grid">
        <div class="why-card reveal"><span class="why-index">01</span><h3>Route 955 corridor</h3><p>Most attractions line the scenic Gingoog–Claveria Road — easy to hop from falls to café to cabin in one day.</p></div>
        <div class="why-card reveal"><span class="why-index">02</span><h3>Cool mountain weather</h3><p>Claveria's highlands stay misty and cold — perfect for bonfires, hot sikwate and cozy overnight stays.</p></div>
        <div class="why-card reveal"><span class="why-index">03</span><h3>Falls & springs</h3><p>From free-entry Mailig and Bindol Falls to cottage-side Nasaad — bring a towel and a picnic.</p></div>
        <div class="why-card reveal"><span class="why-index">04</span><h3>Travel safe</h3><p>Save the <a href="hotlines.html">emergency hotlines</a> — MDDRMO, police and hospital contacts for Claveria.</p></div>
      </div>
    </div>
  </section>

  <section class="section alt" style="padding:44px 0">
    <div class="wrap">
      <div class="emergency-banner" style="margin-bottom:0">
        <div>
          <h2>Heading to the mountains?</h2>
          <p>Save Claveria's emergency hotlines before you go — signal gets spotty up in the barangays.</p>
        </div>
        <a class="btn" href="hotlines.html">View emergency hotlines</a>
      </div>
    </div>
  </section>
</main>
{footer("")}'''
    return head(SITE["tagline"], SITE["description"], "") + body + scripts("")


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path, f"({len(content)/1024:.1f} KB)")


def sitemap():
    pages = ["", "staycation.html", "falls.html", "cafes.html", "hotlines.html"]
    pages += [f"place/{p['slug']}.html" for p in PLACES]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        xml.append(f"  <url><loc>https://claveria-website-ovus.vercel.app/{p}</loc><changefreq>weekly</changefreq></url>")
    xml.append("</urlset>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(xml))
    print("wrote sitemap.xml")


def data_json():
    out = []
    for p in PLACES:
        out.append({**p, "images": place_images(p)})
    with open(os.path.join(ROOT, "data", "places.json"), "w", encoding="utf-8") as f:
        json.dump(clean_data({"site": SITE, "categories": CATEGORIES, "places": out, "hotlines": HOTLINES, "map_locations": MAP_LOCATIONS}), f, ensure_ascii=False, indent=2)
    print("wrote data/places.json")


def main():
    write("index.html", index_page())
    for key in ("staycation", "falls", "cafes"):
        write(f"{key}.html", category_page(key))
    write("hotlines.html", hotlines_page())
    for p in PLACES:
        write(f"place/{p['slug']}.html", place_page(p))
    sitemap()
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    data_json()
    print("\nAll pages built.")


if __name__ == "__main__":
    main()
