/* Dublin Micromouse Open 2026 — behaviour for the event page and the
   Resource Hub. Plain ES5-ish vanilla JS, no build step, no dependencies.

   Three jobs, each a no-op when its markup isn't on the page:
     1. measure the sticky bars so anchor jumps land in the right place;
     2. scroll-spy the event page's section nav;
     3. search + category filtering on the Resource Hub.

   Both pages render their full content in HTML — script only enhances it,
   so the hub still lists all fourteen resources with JS unavailable. */
(function () {
    'use strict';

    var body = document.body;
    var toArray = function (list) { return Array.prototype.slice.call(list); };

    /* ------------------------------------------------------------------
       1. Sticky chrome measurement

       The section nav / filter bar sits directly under the topbar, and
       sections need a scroll-margin that clears both. Hard-coding those
       heights breaks as soon as the topbar wraps or the font falls back,
       so measure the real bars and publish them as custom properties.
       Inline styles on <body> override the fallbacks in the stylesheet.
       ------------------------------------------------------------------ */

    var topbar = document.querySelector('.mm-topbar');
    var stickyBar = document.querySelector('.mm-secnav, .mm-filters');

    function measure() {
        if (topbar) {
            body.style.setProperty('--mm-topbar-h',
                Math.round(topbar.getBoundingClientRect().height) + 'px');
        }
        // Always publish this one: guide pages have no second bar, and the
        // stylesheet's non-zero fallback would push their anchor jumps down
        // by a bar that isn't there.
        body.style.setProperty('--mm-secbar-h',
            (stickyBar ? Math.round(stickyBar.getBoundingClientRect().height) : 0) + 'px');
    }

    measure();

    if (window.ResizeObserver) {
        var ro = new ResizeObserver(measure);
        if (topbar) ro.observe(topbar);
        if (stickyBar) ro.observe(stickyBar);
    }
    window.addEventListener('resize', measure);
    // Web fonts land after first paint and change the bar heights.
    if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(measure).catch(function () {});
    }

    function stickyOffset() {
        var top = topbar ? topbar.getBoundingClientRect().height : 0;
        var sec = stickyBar ? stickyBar.getBoundingClientRect().height : 0;
        return top + sec;
    }

    /* ------------------------------------------------------------------
       2. Section scroll-spy (event page)

       Resolved from geometry rather than straight from an
       IntersectionObserver callback: the observer alone leaves the bar
       stale at the top of the page, at the very bottom, and for any
       section shorter than its observation band. One resolver, driven by
       a passive rAF-throttled scroll listener, answers "which section am
       I in" correctly in every one of those cases.
       ------------------------------------------------------------------ */

    var secnav = document.querySelector('.mm-secnav');

    if (secnav) {
        var track = secnav.querySelector('.mm-secnav-inner');
        var targets = toArray(secnav.querySelectorAll('a[href^="#"]'))
            .map(function (link) {
                return { link: link, el: document.getElementById(link.hash.slice(1)) };
            })
            .filter(function (target) { return target.el; });

        var activeLink = null;

        function keepPillVisible(pill) {
            if (!track || track.scrollWidth <= track.clientWidth) return;
            var trackBox = track.getBoundingClientRect();
            var pillBox = pill.getBoundingClientRect();
            if (pillBox.left < trackBox.left) {
                track.scrollLeft -= (trackBox.left - pillBox.left) + 16;
            } else if (pillBox.right > trackBox.right) {
                track.scrollLeft += (pillBox.right - trackBox.right) + 16;
            }
        }

        function setActive(link) {
            if (link === activeLink) return;
            if (activeLink) {
                activeLink.classList.remove('is-active');
                activeLink.removeAttribute('aria-current');
            }
            activeLink = link;
            if (activeLink) {
                activeLink.classList.add('is-active');
                activeLink.setAttribute('aria-current', 'true');
                keepPillVisible(activeLink);
            }
        }

        function resolveActive() {
            var line = window.pageYOffset + stickyOffset() + 40;
            var current = targets[0];

            for (var i = 0; i < targets.length; i++) {
                var top = targets[i].el.getBoundingClientRect().top + window.pageYOffset;
                if (top <= line) current = targets[i];
            }

            // Bottom of the document: the final section may never reach the
            // line, but it is plainly the one being read.
            var atBottom = window.innerHeight + window.pageYOffset >=
                document.documentElement.scrollHeight - 2;
            if (atBottom) current = targets[targets.length - 1];

            setActive(current ? current.link : null);
        }

        var queued = false;
        function scheduleResolve() {
            if (queued) return;
            queued = true;
            window.requestAnimationFrame(function () {
                queued = false;
                resolveActive();
            });
        }

        if (targets.length) {
            resolveActive();
            window.addEventListener('scroll', scheduleResolve, { passive: true });
            window.addEventListener('resize', scheduleResolve);
            window.addEventListener('hashchange', scheduleResolve);
            if (document.fonts && document.fonts.ready) {
                document.fonts.ready.then(scheduleResolve).catch(function () {});
            }
        }
    }

    /* ------------------------------------------------------------------
       3. Resource Hub filtering

       Case-insensitive substring match over each card's own text (code,
       category, title and blurb), AND-ed with the selected category pill.
       ------------------------------------------------------------------ */

    var hub = document.querySelector('[data-mm-hub]');

    if (hub) {
        var search = hub.querySelector('.mm-search input');
        var pills = toArray(hub.querySelectorAll('.mm-cat'));
        var cards = toArray(document.querySelectorAll('.mm-res'));
        var countEl = document.querySelector('.mm-count');
        var emptyEl = document.querySelector('.mm-empty');
        var category = 'All';

        // Build each card's haystack from the markup so the two can't drift.
        cards.forEach(function (card) {
            card.dataset.haystack = card.textContent
                .replace(/\s+/g, ' ').trim().toLowerCase();
        });

        function applyFilter() {
            var query = search ? search.value.trim().toLowerCase() : '';
            var shown = 0;

            cards.forEach(function (card) {
                var match =
                    (category === 'All' || card.dataset.category === category) &&
                    (!query || card.dataset.haystack.indexOf(query) !== -1);
                card.hidden = !match;
                if (match) shown++;
            });

            if (countEl) {
                countEl.textContent = shown + (shown === 1 ? ' resource' : ' resources');
            }
            if (emptyEl) emptyEl.hidden = shown !== 0;
        }

        function setCategory(next) {
            category = next;
            pills.forEach(function (pill) {
                pill.setAttribute('aria-pressed',
                    pill.dataset.category === category ? 'true' : 'false');
            });
            applyFilter();
        }

        pills.forEach(function (pill) {
            pill.addEventListener('click', function () {
                setCategory(pill.dataset.category);
            });
        });

        if (search) {
            search.addEventListener('input', applyFilter);
            search.addEventListener('keydown', function (event) {
                if (event.key === 'Escape' && search.value) {
                    event.preventDefault();
                    search.value = '';
                    applyFilter();
                }
            });

            // The "/" glyph in the field is a real affordance.
            document.addEventListener('keydown', function (event) {
                if (event.key !== '/' || event.metaKey || event.ctrlKey || event.altKey) return;
                var el = document.activeElement;
                if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' ||
                    el.tagName === 'SELECT' || el.isContentEditable)) return;
                event.preventDefault();
                search.focus();
                search.select();
            });
        }

        /* Guides link back here as #hardware / #software (see
           hardware-guides.js) — honour that by pre-selecting the category
           the reader came from. */
        function categoryFromHash() {
            var hash = window.location.hash.replace('#', '').toLowerCase();
            var match = pills.filter(function (pill) {
                return pill.dataset.category.toLowerCase() === hash;
            })[0];
            if (match) setCategory(match.dataset.category);
        }

        categoryFromHash();
        window.addEventListener('hashchange', categoryFromHash);
        applyFilter();
    }
}());
