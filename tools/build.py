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


def osm_region_embed_url():
    points = list(MAP_LOCATIONS.values())
    lats = [float(point["lat"]) for point in points]
    lons = [float(point["lon"]) for point in points]
    lat_pad, lon_pad = 0.018, 0.025
    bbox = f"{min(lons) - lon_pad:.6f},{min(lats) - lat_pad:.6f},{max(lons) + lon_pad:.6f},{max(lats) + lat_pad:.6f}"
    lat_mid, lon_mid = (min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2
    return "https://www.openstreetmap.org/export/embed.html?bbox=" + quote(bbox, safe=",") + "&layer=mapnik&marker=" + quote(f"{lat_mid:.7f},{lon_mid:.7f}", safe=",")


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

ICON_PATHS = {
    "home": '<path d="m3 10 9-7 9 7"/><path d="M5 9v12h14V9"/><path d="M9 21v-7h6v7"/>',
    "map": '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/>',
    "heart": '<path d="M20.8 8.8c0 5.5-8.8 11.2-8.8 11.2S3.2 14.3 3.2 8.8A4.8 4.8 0 0 1 12 6.2a4.8 4.8 0 0 1 8.8 2.6Z"/>',
    "share": '<path d="M12 15V3m-5 5 5-5 5 5"/><path d="M5 12v8h14v-8"/>',
    "back": '<path d="m15 18-6-6 6-6"/>',
    "directions": '<path d="M12 21 3 12l9-9 9 9-9 9Z"/><path d="M12 16V8m-3 3 3-3 3 3"/>',
    "close": '<path d="m18 6-12 12M6 6l12 12"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.08 4.18 2 2 0 0 1 4.06 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
}


def icon(name, size=20):
    return f'<svg class="ui-icon" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON_PATHS[name]}</svg>'


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


def footer(prefix, active=""):
    year = 2026
    tabs = [("index.html", "Home", "home"), ("map.html", "Map", "map"), ("saved.html", "Saved", "saved"), ("hotlines.html", "Hotlines", "hotlines")]
    tab_html = "".join(
        f'<a class="mobile-tab {"active" if key == active else ""}" href="{prefix}{href}" {"aria-current=page" if key == active else ""}>{icon("heart" if key == "saved" else "phone" if key == "hotlines" else key)}<span>{label}</span>{"<b class=tab-count data-saved-count></b>" if key == "saved" else ""}</a>'
        for href, label, key in tabs
    )
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
          <li><a href="{prefix}map.html">Area map</a></li>
          <li><a href="{prefix}saved.html">Saved places</a></li>
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
<nav class="mobile-tabbar" aria-label="Quick navigation">{tab_html}</nav>
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


def scripts(prefix, include_map=False):
    map_scripts = f'<script src="{prefix}assets/js/leaflet.js" defer></script>\n<script src="{prefix}assets/js/map.js" defer></script>\n' if include_map else ""
    return map_scripts + f'<script src="{prefix}assets/js/main.js" defer></script>\n</body>\n</html>\n'


def place_card(p, prefix):
    imgs = place_images(p)
    thumb = imgs[0] if imgs else None
    warn = ' warn' if p["slug"] == "twin-falls" else ""
    badge_txt = "Temporarily closed" if p["slug"] == "twin-falls" else f"{len(imgs)} photos" if imgs else ""
    badge_html = f'<span class="badge{warn}">{esc(badge_txt)}</span>' if badge_txt else ""
    img_html = f'<img src="{prefix}{thumb}" alt="{esc(p["name"])}" loading="lazy" decoding="async">' if thumb else ""
    search_text = " ".join([p["name"], p["tagline"], p["location"], *p["tags"]])
    tags_text = " | ".join(plain(tag).lower() for tag in p["tags"])
    return f'''<article class="place-card reveal" data-place-card data-place-slug="{esc(p["slug"])}" data-tags="{esc(tags_text)}" data-search="{esc(search_text)}">
  <a class="place-card-link" href="{prefix}place/{p["slug"]}.html">
    <div class="thumb">{img_html}{badge_html}</div>
    <div class="body">
      <h3>{esc(p["name"])}</h3>
      <span class="tagline">{esc(p["tagline"])}</span>
      <span class="loc">{esc(p["location"])}</span>
    </div>
  </a>
  <button class="save-toggle" type="button" data-save-place="{esc(p["slug"])}" data-place-name="{esc(p["name"])}" aria-label="Save {esc(p["name"])}" aria-pressed="false" title="Save place">{icon("heart")}<span class="sr-only">Save place</span></button>
</article>'''


def category_page(cat_key):
    cat = CATEGORIES[cat_key]
    places = [p for p in PLACES if p["category"] == cat_key]
    cards = "\n".join(place_card(p, "") for p in places)
    filters_html = ""
    if cat_key == "cafes":
        filters = [
            ("all", "All"),
            ("coffee", "Coffee"),
            ("scenic|view|mountain view", "Scenic views"),
            ("cozy", "Cozy"),
            ("restaurant", "Restaurants"),
            ("route 955", "Route 955"),
            ("24/7", "24/7"),
        ]
        filters_html = '<div class="filter-row" role="group" aria-label="Filter coffee shops">' + "".join(
            f'<button class="filter-chip{" active" if value == "all" else ""}" type="button" data-filter-value="{esc(value)}" aria-pressed="{"true" if value == "all" else "false"}">{esc(label)}</button>'
            for value, label in filters
        ) + '</div>'
    main_class = "app-screen category-screen cafe-screen" if cat_key == "cafes" else "app-screen category-screen"
    search_placeholder = "Search coffee shops, food, or area" if cat_key == "cafes" else f"Search {cat['title'].lower()} by name, barangay or tag"
    body = f'''{header("", cat_key)}
<main class="{main_class}">
  <section class="section category-section" style="padding-bottom:20px">
    <div class="wrap">
      <div class="section-head category-heading">
        <div>
          <span class="eyebrow">Explore Claveria</span>
          <h2>{esc(cat['title'])}</h2>
          <p>{esc(cat['blurb'])}</p>
        </div>
        <span class="chip place-count">{len(places)} places</span>
      </div>
      <div class="search-bar">
        <label class="sr-only" for="place-search">Search places</label>
        {SEARCH}
        <input id="place-search" type="search" placeholder="{esc(search_placeholder)}" autocomplete="off">
      </div>
{filters_html}
      <div class="card-grid" id="card-grid">
{cards}
      </div>
      <div class="no-results" id="no-results">No places match your search. Try another name, area, or filter.</div>
    </div>
  </section>
</main>
{footer("", "home")}'''
    return head(cat["title"], cat["blurb"] + f" — {len(places)} places in Claveria, Misamis Oriental.", "") + body + scripts("")


def place_page(p):
    prefix = "../"
    cat = CATEGORIES[p["category"]]
    imgs = place_images(p)
    cover_img = imgs[0] if imgs else "assets/img/brand/og.jpg"
    gallery = ""
    for i, src in enumerate(imgs):
        cls = "g-main" if i == 0 else ""
        gallery += f'<figure class="{cls}"><img src="{prefix}{src}" alt="{esc(p["name"])} photo {i+1}" loading="{"eager" if i==0 else "lazy"}" decoding="async"></figure>'
    if not gallery:
        gallery = '<figure class="g-main"><img src="../assets/img/brand/og.jpg" alt="Claveria"></figure>'

    contacts = ""
    for label, value, href in p["contact"]:
        action = "Call" if href.startswith("tel:") else "Email" if href.startswith("mailto:") else "Message" if "wa.me" in href else "Open"
        display_value = esc(value)
        if href.startswith("mailto:"):
            display_value = display_value.replace("@", "<wbr>@<wbr>", 1)
        contacts += f'<a class="contact-link" href="{esc(href)}"><span><small>{esc(label)}</small><br>{display_value}</span><span class="contact-action">{action}</span></a>'
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

    mobile_cover = f'''<div class="mobile-place-cover">
  <img src="{prefix}{cover_img}" alt="{esc(p["name"])} in Claveria" fetchpriority="high" decoding="async">
  <div class="cover-shade"></div>
  <div class="cover-controls">
    <a class="cover-back" href="{prefix}{p["category"]}.html" aria-label="Back to {esc(cat["title"])}">{icon("back")}<span>Back</span></a>
    <div class="cover-actions">
      <button class="cover-icon save-toggle" type="button" data-save-place="{esc(p["slug"])}" data-place-name="{esc(p["name"])}" aria-label="Save {esc(p["name"])}" aria-pressed="false" title="Save place">{icon("heart")}</button>
      <button class="cover-icon" type="button" data-share-place data-share-title="{esc(p["name"])}" aria-label="Share {esc(p["name"])}" title="Share place">{icon("share")}</button>
    </div>
  </div>
</div>'''

    desktop_tools = f'''<div class="place-tools">
  <button class="tool-button save-toggle" type="button" data-save-place="{esc(p["slug"])}" data-place-name="{esc(p["name"])}" aria-label="Save {esc(p["name"])}" aria-pressed="false">{icon("heart")}<span>Save</span></button>
  <button class="tool-button" type="button" data-share-place data-share-title="{esc(p["name"])}">{icon("share")}<span>Share</span></button>
</div>'''

    action_contact = ""
    if p["contact"]:
        _, _, contact_href = p["contact"][0]
        contact_label = "Call" if contact_href.startswith("tel:") else "Email" if contact_href.startswith("mailto:") else "Message" if "wa.me" in contact_href else "Contact"
        action_icon = icon("phone") if contact_href.startswith("tel:") else icon("share")
        action_contact = f'<a class="detail-action secondary-action" href="{esc(contact_href)}">{action_icon}<span>{contact_label}</span></a>'
    action_dock = f'''<div class="place-action-dock" aria-label="Place actions">
  <a class="detail-action primary-action" href="{esc(maps_url(p["maps_query"]))}" target="_blank" rel="noopener">{icon("directions")}<span>Directions</span></a>
{action_contact}
</div>'''

    body = f'''{header(prefix, p["category"])}
<main class="place-screen">
  {mobile_cover}
  <div class="wrap">
    <nav class="crumbs"><a href="{prefix}index.html">Home</a> › <a href="{prefix}{p["category"]}.html">{esc(cat["title"])}</a> › {esc(p["name"])}</nav>
    <div class="place-hero">
      <div class="place-title-row">
        <div>
          <h1>{esc(p["name"])}</h1>
          <p class="tagline">{esc(p["tagline"])}</p>
        </div>
        {desktop_tools}
      </div>
      <div class="meta-row">
        <span class="chip">{esc(cat["title"])}</span>
        {warn_chip}
        {tags}
      </div>
    </div>
    <div class="place-layout" id="visitor-info">
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
{action_dock}
<div class="lightbox" id="lightbox" role="dialog" aria-label="Photo viewer">
  <button class="lb-close" aria-label="Close">×</button>
  <button class="lb-nav lb-prev" aria-label="Previous">‹</button>
  <img alt="Place photo">
  <button class="lb-nav lb-next" aria-label="Next">›</button>
  <div class="lb-count"></div>
</div>
{footer(prefix, "home")}'''
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
{footer("", "hotlines")}'''
    return head("Emergency Hotlines", "Claveria, Misamis Oriental emergency hotlines — MDDRMO, police, hospital & rescue contacts. Save them before you travel.", "") + body + scripts("")


def index_page():
    cats_html = ""
    category_order = ("cafes", "falls", "staycation")
    category_card_titles = {"cafes": "Coffee Shops", "falls": "Waterfalls", "staycation": "Stays"}
    sample_slugs = {"cafes": "skye-88-cafe", "falls": "lantawon-falls", "staycation": "hiraya-farm-escape"}
    for key in category_order:
        cat = CATEGORIES[key]
        n = len([p for p in PLACES if p["category"] == key])
        sample = next((p for p in PLACES if p["slug"] == sample_slugs[key]), next(p for p in PLACES if p["category"] == key))
        imgs = place_images(sample)
        img = imgs[0] if imgs else "assets/img/brand/hero.jpg"
        cats_html += f'''<a class="cat-card cat-card-{key} reveal" href="{key}.html">
  <div class="cat-img"><img src="{img}" alt="{esc(cat['title'])}" loading="lazy" decoding="async"></div>
  <span class="count">{n} places</span>
  <div class="cat-body">
    <div class="cat-kicker">{key.upper()}</div>
    <h3>{esc(category_card_titles[key])}</h3>
    <p>{esc(cat['blurb'])}</p>
  </div>
</a>'''
    featured = [p for p in PLACES if p["slug"] in ("baqs-bonfires", "cabinscape-ridge-resort", "lantawon-falls", "skye-88-cafe", "lone-wolf-cafe", "hiraya-farm-escape")]
    feat_cards = "\n".join(place_card(p, "") for p in featured)
    counts = {k: len([p for p in PLACES if p["category"] == k]) for k in ("staycation", "falls", "cafes")}
    body = f'''{header("", "")}
<main class="home-screen">
  <section class="mobile-greeting">
    <div class="wrap">
      <p class="greeting-kicker" data-greeting>Good morning,</p>
      <h2>Explorer</h2>
      <p class="greeting-prompt">Claveria is calling. Where will you go today?</p>
    </div>
  </section>
  <section class="hero">
    <div class="hero-bg"><picture><source media="(max-width: 720px)" srcset="assets/img/brand/hero-mobile.jpg"><img src="assets/img/brand/hero.jpg" width="1920" height="946" alt="Municipality of Claveria in Misamis Oriental" fetchpriority="high" decoding="async"></picture></div>
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
{footer("", "home")}'''
    return head(SITE["tagline"], SITE["description"], "") + body + scripts("")


def map_page():
    place_items = []
    cards = []
    for place in PLACES:
        point = MAP_LOCATIONS.get(place["slug"])
        if not point:
            continue
        item = {
            "slug": place["slug"],
            "name": plain(place["name"]),
            "category": place["category"],
            "category_title": plain(CATEGORIES[place["category"]]["title"]),
            "location": plain(place["location"]),
            "lat": float(point["lat"]),
            "lon": float(point["lon"]),
            "approximate": place["slug"] in MAP_APPROXIMATE,
        }
        place_items.append(item)
        approximate = '<span class="map-approximate">Approximate pin</span>' if item["approximate"] else ""
        cards.append(f'''<article class="map-place-card" data-map-item data-map-category="{esc(place["category"])}" data-search="{esc(place["name"] + ' ' + place["location"] + ' ' + CATEGORIES[place["category"]]['title'])}">
  <a class="map-place-link" href="place/{esc(place["slug"])}.html">
    <span class="map-place-category">{esc(CATEGORIES[place["category"]]['title'])}</span>
    <h3>{esc(place["name"])}</h3>
    <span class="map-place-location">{esc(place["location"])}</span>
{approximate}
  </a>
  <a class="map-direction-link" href="{esc(maps_url(place['maps_query']))}" target="_blank" rel="noopener">Directions</a>
</article>''')

    filters = [("all", "All"), ("cafes", "Coffee shops"), ("falls", "Waterfalls"), ("staycation", "Staycations")]
    filter_html = '<div class="filter-row map-filter-row" role="group" aria-label="Filter map locations">' + "".join(
        f'<button class="filter-chip{" active" if value == "all" else ""}" type="button" data-map-filter="{value}" aria-pressed="{"true" if value == "all" else "false"}">{label}</button>'
        for value, label in filters
    ) + '</div>'
    map_json = json.dumps(place_items, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    body = f'''{header("", "")}
<main class="app-screen map-screen">
  <section class="section map-section">
    <div class="wrap">
      <div class="section-head map-heading">
        <div>
          <span class="eyebrow">Get around</span>
          <h2>Claveria map</h2>
          <p>Browse the places in this guide, then open a listing for its location details.</p>
        </div>
        <span class="chip place-count">{len(place_items)} mapped places</span>
      </div>
      <div class="map-explorer">
        <div id="claveria-map" class="leaflet-map" aria-label="Map of places in Claveria" hidden></div>
        <div class="map-fallback">
          <iframe title="Overview map of Claveria places" src="{esc(osm_region_embed_url())}" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
        </div>
      </div>
      <p class="map-note">Map data © OpenStreetMap contributors. Four location pins are approximate; their place pages include a note. For turn-by-turn directions, use the Directions link.</p>
      <div class="map-directory-head">
        <div>
          <h3>Find a place</h3>
          <p>{len(place_items)} listings in the Claveria guide</p>
        </div>
      </div>
      <div class="search-bar map-search-bar">
        <label class="sr-only" for="map-search">Search mapped places</label>
        {SEARCH}
        <input id="map-search" type="search" placeholder="Search by place or area" autocomplete="off">
      </div>
      {filter_html}
      <div class="map-place-list" id="map-place-list">
{''.join(cards)}
      </div>
      <div class="no-results" id="map-no-results">No mapped places match your search.</div>
    </div>
  </section>
</main>
<script id="map-places-data" type="application/json">{map_json}</script>
{footer("", "map")}'''
    page_head = head("Claveria Map", "Interactive map and directory of Claveria, Misamis Oriental places, cafés, waterfalls, and stays.", "")
    page_head = page_head.replace("</head>", '<link rel="stylesheet" href="assets/vendor/leaflet/leaflet.css">\n</head>')
    return page_head + body + scripts("", include_map=True)


def saved_page():
    cards = "\n".join(place_card(place, "") for place in PLACES)
    body = f'''{header("", "")}
<main class="app-screen saved-screen">
  <section class="section saved-section">
    <div class="wrap">
      <div class="section-head">
        <div>
          <span class="eyebrow">Your shortlist</span>
          <h2>Saved places</h2>
          <p>Keep the cafés, waterfalls, and stays you want to come back to. Saved places stay on this device.</p>
        </div>
        <span class="chip saved-count-label"><span data-saved-total>0</span> saved</span>
      </div>
      <div class="empty-state" id="saved-empty" hidden>
        <h3>No saved places yet</h3>
        <p>Tap the heart on any place to add it to your shortlist.</p>
        <a class="btn btn-green" href="cafes.html">Explore coffee shops</a>
      </div>
      <div class="card-grid" id="saved-grid" data-saved-grid>
{cards}
      </div>
    </div>
  </section>
</main>
{footer("", "saved")}'''
    return head("Saved Places", "Your saved Claveria cafés, waterfalls, and stays — stored on this device.", "") + body + scripts("")


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path, f"({len(content)/1024:.1f} KB)")


def sitemap():
    pages = ["", "map.html", "saved.html", "staycation.html", "falls.html", "cafes.html", "hotlines.html"]
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
    write("map.html", map_page())
    write("saved.html", saved_page())
    write("hotlines.html", hotlines_page())
    for p in PLACES:
        write(f"place/{p['slug']}.html", place_page(p))
    sitemap()
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    data_json()
    print("\nAll pages built.")


if __name__ == "__main__":
    main()
