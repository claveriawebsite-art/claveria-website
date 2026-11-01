/* Claveria Escape — mobile navigation, search, saved places, sharing, and galleries */
(function () {
  "use strict";

  var STORAGE_KEY = "claveria-escape-saved-places";
  var savedPlaces = readSavedPlaces();

  function readSavedPlaces() {
    try {
      var value = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || "[]");
      return Array.isArray(value) ? value.filter(function (slug) { return typeof slug === "string"; }) : [];
    } catch (error) {
      return [];
    }
  }

  function persistSavedPlaces() {
    try { window.localStorage.setItem(STORAGE_KEY, JSON.stringify(savedPlaces)); } catch (error) { /* Storage can be disabled. */ }
  }

  /* compact navigation menu */
  var burger = document.querySelector(".burger");
  var links = document.querySelector(".nav-links");
  if (burger && links) {
    function setMenu(open) {
      links.classList.toggle("open", open);
      burger.setAttribute("aria-expanded", String(open));
      burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    }
    burger.addEventListener("click", function () {
      setMenu(burger.getAttribute("aria-expanded") !== "true");
    });
    links.addEventListener("click", function (event) {
      if (event.target.closest("a")) setMenu(false);
    });
    document.addEventListener("click", function (event) {
      if (!burger.contains(event.target) && !links.contains(event.target)) setMenu(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") setMenu(false);
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 720) setMenu(false);
    }, { passive: true });
  }

  /* local time greeting on the mobile Explore screen */
  var greeting = document.querySelector("[data-greeting]");
  if (greeting) {
    var hour = new Date().getHours();
    greeting.textContent = hour < 12 ? "Good morning," : hour < 18 ? "Good afternoon," : "Good evening,";
  }

  /* saved-place buttons and saved screen */
  function renderSavedPlaces() {
    var savedSet = new Set(savedPlaces);
    document.querySelectorAll("[data-save-place]").forEach(function (button) {
      var slug = button.getAttribute("data-save-place");
      var name = button.getAttribute("data-place-name") || "this place";
      var isSaved = savedSet.has(slug);
      button.classList.toggle("is-saved", isSaved);
      button.setAttribute("aria-pressed", String(isSaved));
      button.setAttribute("aria-label", (isSaved ? "Remove " : "Save ") + name + (isSaved ? " from saved places" : ""));
      button.setAttribute("title", isSaved ? "Remove from saved places" : "Save place");
      var hiddenText = button.querySelector(".sr-only");
      if (hiddenText) hiddenText.textContent = isSaved ? "Saved" : "Save place";
    });

    document.querySelectorAll("[data-saved-count]").forEach(function (badge) {
      badge.textContent = savedPlaces.length ? String(savedPlaces.length) : "";
      badge.hidden = savedPlaces.length === 0;
    });
    document.querySelectorAll("[data-saved-total]").forEach(function (label) {
      label.textContent = String(savedPlaces.length);
    });

    var savedGrid = document.querySelector("[data-saved-grid]");
    if (savedGrid) {
      savedGrid.querySelectorAll("[data-place-card]").forEach(function (card) {
        card.hidden = !savedSet.has(card.getAttribute("data-place-slug"));
      });
      savedGrid.hidden = savedPlaces.length === 0;
      var empty = document.getElementById("saved-empty");
      if (empty) empty.hidden = savedPlaces.length !== 0;
    }
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-save-place]");
    if (!button) return;
    event.preventDefault();
    var slug = button.getAttribute("data-save-place");
    var index = savedPlaces.indexOf(slug);
    if (index >= 0) savedPlaces.splice(index, 1);
    else savedPlaces.push(slug);
    persistSavedPlaces();
    renderSavedPlaces();
    window.dispatchEvent(new CustomEvent("claveria:savedchange", { detail: { saved: savedPlaces.slice() } }));
  });

  window.addEventListener("storage", function (event) {
    if (event.key === STORAGE_KEY) {
      savedPlaces = readSavedPlaces();
      renderSavedPlaces();
    }
  });
  renderSavedPlaces();

  /* Share uses the native sheet where supported, otherwise copies a link. */
  function showCopied(button) {
    var label = button.querySelector("span:not(.sr-only)");
    var previous = label ? label.textContent : "";
    var previousAria = button.getAttribute("aria-label");
    var previousTitle = button.getAttribute("title");
    if (label) label.textContent = "Copied";
    button.setAttribute("aria-label", "Link copied");
    button.setAttribute("title", "Link copied");
    window.setTimeout(function () {
      if (label) label.textContent = previous;
      if (previousAria === null) button.removeAttribute("aria-label");
      else button.setAttribute("aria-label", previousAria);
      if (previousTitle === null) button.removeAttribute("title");
      else button.setAttribute("title", previousTitle);
    }, 1600);
  }

  function copyShareUrl(button, url) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () { showCopied(button); }).catch(function () { fallbackCopy(button, url); });
    } else {
      fallbackCopy(button, url);
    }
  }

  function fallbackCopy(button, url) {
    var field = document.createElement("textarea");
    field.value = url;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    try { document.execCommand("copy"); showCopied(button); } catch (error) { /* Manual copy remains possible from the address bar. */ }
    field.remove();
  }

  document.querySelectorAll("[data-share-place]").forEach(function (button) {
    button.addEventListener("click", function () {
      var title = button.getAttribute("data-share-title") || document.title.replace(/\s·\sClaveria Escape$/, "");
      var shareData = { title: title, text: "Explore " + title + " in Claveria, Misamis Oriental.", url: window.location.href };
      if (navigator.share) {
        navigator.share(shareData).catch(function (error) {
          if (error && error.name !== "AbortError") copyShareUrl(button, shareData.url);
        });
      } else {
        copyShareUrl(button, shareData.url);
      }
    });
  });

  /* category search and tag filters */
  var search = document.getElementById("place-search");
  if (search) {
    var cards = Array.prototype.slice.call(document.querySelectorAll("#card-grid [data-place-card]"));
    var noResults = document.getElementById("no-results");
    var activeFilter = "all";
    function filterCategoryCards() {
      var query = search.value.trim().toLowerCase();
      var shown = 0;
      cards.forEach(function (card) {
        var searchable = (card.getAttribute("data-search") || card.textContent || "").toLowerCase();
        var tags = (card.getAttribute("data-tags") || "").toLowerCase();
        var terms = activeFilter === "all" ? [] : activeFilter.split("|").map(function (term) { return term.trim(); }).filter(Boolean);
        var textMatch = !query || searchable.indexOf(query) !== -1;
        var tagMatch = !terms.length || terms.some(function (term) { return tags.indexOf(term) !== -1; });
        var visible = textMatch && tagMatch;
        card.hidden = !visible;
        if (visible) shown += 1;
      });
      if (noResults) noResults.hidden = shown > 0;
    }
    search.addEventListener("input", filterCategoryCards);
    document.querySelectorAll("[data-filter-value]").forEach(function (button) {
      button.addEventListener("click", function () {
        activeFilter = button.getAttribute("data-filter-value") || "all";
        document.querySelectorAll("[data-filter-value]").forEach(function (other) {
          var selected = other === button;
          other.classList.toggle("active", selected);
          other.setAttribute("aria-pressed", String(selected));
        });
        filterCategoryCards();
      });
    });
    filterCategoryCards();
  }

  /* map-directory search/filter also filters the Leaflet pins */
  var mapSearch = document.getElementById("map-search");
  if (mapSearch) {
    var mapCards = Array.prototype.slice.call(document.querySelectorAll("[data-map-item]"));
    var mapNoResults = document.getElementById("map-no-results");
    var activeMapFilter = "all";
    function filterMapDirectory() {
      var query = mapSearch.value.trim().toLowerCase();
      var shown = 0;
      mapCards.forEach(function (card) {
        var text = (card.getAttribute("data-search") || card.textContent || "").toLowerCase();
        var category = card.getAttribute("data-map-category") || "";
        var visible = (!query || text.indexOf(query) !== -1) && (activeMapFilter === "all" || activeMapFilter === category);
        card.hidden = !visible;
        if (visible) shown += 1;
      });
      if (mapNoResults) mapNoResults.hidden = shown > 0;
      window.dispatchEvent(new CustomEvent("claveria:mapfilter", { detail: { category: activeMapFilter, query: query } }));
    }
    mapSearch.addEventListener("input", filterMapDirectory);
    document.querySelectorAll("[data-map-filter]").forEach(function (button) {
      button.addEventListener("click", function () {
        activeMapFilter = button.getAttribute("data-map-filter") || "all";
        document.querySelectorAll("[data-map-filter]").forEach(function (other) {
          var selected = other === button;
          other.classList.toggle("active", selected);
          other.setAttribute("aria-pressed", String(selected));
        });
        filterMapDirectory();
      });
    });
    filterMapDirectory();
  }

  /* lightbox for place galleries */
  var lightbox = document.getElementById("lightbox");
  if (lightbox) {
    var lightboxImage = lightbox.querySelector("img");
    var count = lightbox.querySelector(".lb-count");
    var figures = Array.prototype.slice.call(document.querySelectorAll(".gallery figure"));
    var imageUrls = figures.map(function (figure) { return figure.querySelector("img").src; });
    var currentIndex = 0;
    function showImage(index) {
      if (!imageUrls.length) return;
      currentIndex = (index + imageUrls.length) % imageUrls.length;
      lightboxImage.src = imageUrls[currentIndex];
      var placeHeading = document.querySelector(".place-hero h1");
      lightboxImage.alt = (placeHeading ? placeHeading.textContent : "Place") + " photo " + (currentIndex + 1);
      if (count) count.textContent = (currentIndex + 1) + " / " + imageUrls.length;
    }
    function openLightbox(index) {
      if (!imageUrls.length) return;
      lightbox.classList.add("open");
      showImage(index);
      document.body.style.overflow = "hidden";
    }
    function closeLightbox() {
      lightbox.classList.remove("open");
      document.body.style.overflow = "";
    }
    figures.forEach(function (figure, index) {
      figure.addEventListener("click", function () { openLightbox(index); });
    });
    var coverImage = document.querySelector(".mobile-place-cover img");
    if (coverImage && imageUrls.length) coverImage.addEventListener("click", function () { openLightbox(0); });
    var closeButton = lightbox.querySelector(".lb-close");
    if (closeButton) closeButton.addEventListener("click", closeLightbox);
    var previousButton = lightbox.querySelector(".lb-prev");
    if (previousButton) previousButton.addEventListener("click", function (event) { event.stopPropagation(); showImage(currentIndex - 1); });
    var nextButton = lightbox.querySelector(".lb-next");
    if (nextButton) nextButton.addEventListener("click", function (event) { event.stopPropagation(); showImage(currentIndex + 1); });
    lightbox.addEventListener("click", function (event) { if (event.target === lightbox) closeLightbox(); });
    document.addEventListener("keydown", function (event) {
      if (!lightbox.classList.contains("open")) return;
      if (event.key === "Escape") closeLightbox();
      if (event.key === "ArrowLeft") showImage(currentIndex - 1);
      if (event.key === "ArrowRight") showImage(currentIndex + 1);
    });
  }

  /* reveal content as it enters the viewport */
  var revealElements = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealElements.forEach(function (element) { observer.observe(element); });
  } else {
    revealElements.forEach(function (element) { element.classList.add("in"); });
  }

  /* back to top */
  var topButton = document.querySelector(".back-top");
  if (topButton) {
    window.addEventListener("scroll", function () {
      topButton.classList.toggle("show", window.scrollY > 600);
    }, { passive: true });
    topButton.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  }
})();
