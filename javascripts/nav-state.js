/**
 * nav-state.js
 *
 * Persists sidebar open/scroll state across SPA navigations in MkDocs Material.
 * Uses the Material document$ observable so it fires after every page swap,
 * not just on the initial DOMContentLoaded.
 */
(function () {
  "use strict";

  const STORAGE_KEY = "nav-state";
  const TOGGLE_SEL  = "input.md-nav__toggle";
  const SCROLL_SELS = [".md-sidebar__scrollwrap", ".md-sidebar__inner"];

  // AbortController for the current scroll listener so we can cleanly remove
  // it before attaching a new one on each SPA swap.
  let scrollAbort = null;

  // ── Helpers ───────────────────────────────────────────────────────────────

  function getScrollContainer() {
    for (const sel of SCROLL_SELS) {
      const el = document.querySelector(sel);
      if (el) { return el; }
    }
    return null;
  }

  function loadState() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch (_) {
      return {};
    }
  }

  function saveState(patch) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(
      Object.assign(loadState(), patch)
    ));
  }

  // Stable ID derived from the visible label text so it survives SPA swaps.
  function stableId(toggle, index) {
    if (toggle.dataset.navStateId) { return toggle.dataset.navStateId; }
    const label = toggle.closest(".md-nav__item")
                        ?.querySelector(".md-nav__link")
                        ?.textContent.trim();
    const id = label ? "nav-" + label.replace(/\s+/g, "-").toLowerCase()
                     : (toggle.id || ("nav-toggle-" + index));
    toggle.dataset.navStateId = id;
    return id;
  }

  // ── Persist open/close on user interaction ────────────────────────────────

  function bindToggleListeners() {
    document.querySelectorAll(TOGGLE_SEL).forEach((toggle, index) => {
      if (toggle.dataset.navStateBound) { return; }
      toggle.dataset.navStateBound = "true";

      toggle.addEventListener("change", () => {
        const id = stableId(toggle, index);
        const openIds = new Set(loadState().openIds || []);
        if (toggle.checked) {
          openIds.add(id);
        } else {
          openIds.delete(id);
        }
        saveState({ openIds: Array.from(openIds) });
      });
    });
  }

  function bindScrollListener() {
    // Cancel previous listener before attaching a new one.
    if (scrollAbort) { scrollAbort.abort(); }
    scrollAbort = new AbortController();

    const sc = getScrollContainer();
    if (!sc) { return; }

    sc.addEventListener("scroll", () => {
      saveState({ scrollTop: sc.scrollTop });
    }, { passive: true, signal: scrollAbort.signal });
  }

  // ── Restore state (called after every SPA navigation) ────────────────────

  function restoreState() {
    const state = loadState();
    const openIds = new Set(state.openIds || []);

    // Suppress CSS transitions while we restore toggles and scroll.
    document.body.classList.add("nav-state-restoring");

    // Restore all open toggles.
    document.querySelectorAll(TOGGLE_SEL).forEach((toggle, index) => {
      if (openIds.has(stableId(toggle, index))) {
        toggle.checked = true;
      }
    });

    // Re-bind toggle listeners to any new DOM nodes from the SPA swap.
    bindToggleListeners();

    // Restore scroll position and re-attach scroll listener only after the
    // browser has painted the restored toggle state, so the layout is stable
    // and no spurious scroll event fires before we save.
    requestAnimationFrame(() => {
      const sc = getScrollContainer();
      if (sc && Number.isFinite(state.scrollTop)) {
        sc.scrollTop = state.scrollTop;
      }

      // Re-enable transitions.
      document.body.classList.remove("nav-state-restoring");

      // Scroll the active nav link into view.  Material sets
      // md-nav__link--active after document$ fires, so wait one more
      // animation frame to be sure it is applied.
      requestAnimationFrame(() => {
        const active = document.querySelector(".md-nav__link--active");
        if (active) {
          active.scrollIntoView({ block: "nearest", behavior: "instant" });
        }

        // Attach scroll listener now — after scroll position is restored —
        // so we don't immediately overwrite the saved scrollTop with 0.
        bindScrollListener();
      });
    });
  }

  // ── No-transition style ───────────────────────────────────────────────────

  (function injectStyle() {
    if (document.getElementById("nav-state-style")) { return; }
    const s = document.createElement("style");
    s.id = "nav-state-style";
    s.textContent =
      ".nav-state-restoring * {" +
      "  transition: none !important;" +
      "  animation: none !important;" +
      "  scroll-behavior: auto !important;" +
      "}";
    document.head.appendChild(s);
  })();

  // ── Entry point ───────────────────────────────────────────────────────────
  // Material exposes a RxJS document$ observable that emits after every
  // SPA page swap.  Fall back to DOMContentLoaded for non-Material builds.

  if (typeof document$ !== "undefined") {
    document$.subscribe(restoreState);
  } else {
    document.addEventListener("DOMContentLoaded", restoreState);
  }

})();
