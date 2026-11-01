/* Claveria Escape — interactions */
(function () {
  "use strict";

  /* mobile nav */
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
    links.addEventListener("click", function (e) {
      if (e.target.closest("a")) setMenu(false);
    });
    document.addEventListener("click", function (e) {
      if (!burger.contains(e.target) && !links.contains(e.target)) setMenu(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setMenu(false);
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 720) setMenu(false);
    }, { passive: true });
  }

  /* card search filter (category pages) */
  var search = document.getElementById("place-search");
  if (search) {
    var cards = Array.prototype.slice.call(document.querySelectorAll(".place-card"));
    var noRes = document.getElementById("no-results");
    search.addEventListener("input", function () {
      var q = search.value.trim().toLowerCase();
      var shown = 0;
      cards.forEach(function (c) {
        var text = (c.textContent || "").toLowerCase();
        var hit = !q || text.indexOf(q) !== -1;
        c.style.display = hit ? "" : "none";
        if (hit) shown++;
      });
      if (noRes) noRes.style.display = shown ? "none" : "block";
    });
  }

  /* lightbox for place galleries */
  var lb = document.getElementById("lightbox");
  if (lb) {
    var lbImg = lb.querySelector("img");
    var lbCount = lb.querySelector(".lb-count");
    var figs = Array.prototype.slice.call(document.querySelectorAll(".gallery figure"));
    var imgs = figs.map(function (f) { return f.querySelector("img").src; });
    var idx = 0;
    function show(i) {
      idx = (i + imgs.length) % imgs.length;
      lbImg.src = imgs[idx];
      if (lbCount) lbCount.textContent = (idx + 1) + " / " + imgs.length;
    }
    figs.forEach(function (f, i) {
      f.addEventListener("click", function () { lb.classList.add("open"); show(i); document.body.style.overflow = "hidden"; });
    });
    lb.querySelector(".lb-close").addEventListener("click", close);
    lb.querySelector(".lb-prev").addEventListener("click", function (e) { e.stopPropagation(); show(idx - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function (e) { e.stopPropagation(); show(idx + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(idx - 1);
      if (e.key === "ArrowRight") show(idx + 1);
    });
    function close() { lb.classList.remove("open"); document.body.style.overflow = ""; }
  }

  /* reveal on scroll */
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }

  /* back to top */
  var topBtn = document.querySelector(".back-top");
  if (topBtn) {
    window.addEventListener("scroll", function () {
      topBtn.classList.toggle("show", window.scrollY > 600);
    }, { passive: true });
    topBtn.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  }
})();
