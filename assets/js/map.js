/* Claveria Escape overview map — Leaflet + OpenStreetMap tiles */
(function () {
  "use strict";
  var mapElement = document.getElementById("claveria-map");
  var dataElement = document.getElementById("map-places-data");
  if (!mapElement || !dataElement || !window.L) return;

  var places;
  try { places = JSON.parse(dataElement.textContent || "[]"); } catch (error) { return; }
  if (!places.length) return;

  var fallback = document.querySelector(".map-fallback");
  mapElement.hidden = false;
  if (fallback) fallback.hidden = true;

  var map = window.L.map(mapElement, { scrollWheelZoom: false, tap: true });
  window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap contributors</a>'
  }).addTo(map);

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[character];
    });
  }

  var entries = [];
  var bounds = [];
  places.forEach(function (place) {
    var latLng = [Number(place.lat), Number(place.lon)];
    bounds.push(latLng);
    var color = place.approximate ? "#9a6a1e" : "#116038";
    var marker = window.L.circleMarker(latLng, {
      radius: 7,
      color: "#fffdf7",
      weight: 2,
      fillColor: color,
      fillOpacity: 0.96,
      bubblingMouseEvents: false
    });
    var url = "place/" + encodeURIComponent(place.slug) + ".html";
    var note = place.approximate ? '<span class="popup-note">Approximate location</span>' : "";
    var popup = '<div class="map-popup"><span>' + escapeHtml(place.category_title) + '</span><strong>' + escapeHtml(place.name) + '</strong><small>' + escapeHtml(place.location) + '</small>' + note + '<a href="' + url + '">View place details</a></div>';
    marker.bindPopup(popup, { maxWidth: 250 });
    marker.addTo(map);
    entries.push({ marker: marker, place: place });
  });

  if (bounds.length > 1) map.fitBounds(window.L.latLngBounds(bounds).pad(0.12));
  else map.setView(bounds[0], 12);
  window.setTimeout(function () { map.invalidateSize(); }, 120);

  window.addEventListener("claveria:mapfilter", function (event) {
    var filter = event.detail || {};
    var query = String(filter.query || "").toLowerCase();
    entries.forEach(function (entry) {
      var place = entry.place;
      var searchable = (place.name + " " + place.location + " " + place.category_title).toLowerCase();
      var matchesCategory = !filter.category || filter.category === "all" || filter.category === place.category;
      var matchesQuery = !query || searchable.indexOf(query) !== -1;
      if (matchesCategory && matchesQuery) {
        if (!map.hasLayer(entry.marker)) entry.marker.addTo(map);
      } else if (map.hasLayer(entry.marker)) {
        map.removeLayer(entry.marker);
      }
    });
  });
})();
