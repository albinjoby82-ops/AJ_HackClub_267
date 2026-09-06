(function () {
    'use strict';

    var prefix = 'docs/Micromouse2026/Hardware/';
    var viewer = document.createElement('dialog');
    viewer.className = 'hardware-viewer';
    viewer.setAttribute('aria-label', 'Hardware diagram');
    var close = document.createElement('button');
    close.type = 'button';
    close.textContent = 'Close diagram ×';
    var fullImage = document.createElement('img');
    viewer.append(close, fullImage);
    document.body.appendChild(viewer);
    close.addEventListener('click', function () { viewer.close(); });
    viewer.addEventListener('click', function (event) {
        if (event.target === viewer) viewer.close();
    });

    window.enhanceHardwareGuide = function (content, path, page) {
        var hardware = path.indexOf(prefix) === 0;
        document.body.classList.toggle('hardware-reading', hardware);
        if (!hardware) return;
        content.classList.add('hardware-guide');
        var title = content.querySelector('h1');
        if (!title) return;

        var back = document.createElement('a');
        back.className = 'hardware-back';
        back.href = 'micromouse-resources.html#hardware';
        back.textContent = '← All hardware guides';
        title.before(back);

        var match = title.textContent.match(/^(H\d)\s*-\s*/);
        if (match) {
            var meta = document.createElement('p');
            meta.className = 'hardware-meta';
            var minutes = Math.max(1, Math.ceil(page.body.replace(/<[^>]*>/g, ' ').split(/\s+/).length / 200));
            meta.textContent = match[1] + ' / HARDWARE GUIDE · ' + minutes + ' MIN READ';
            title.before(meta);
            title.textContent = title.textContent.slice(match[0].length);
        }

        var intro = title.nextElementSibling;
        if (intro && intro.tagName === 'P') intro.classList.add('hardware-lead');
        var headings = Array.from(content.querySelectorAll('h2'));
        if (headings.length > 1) {
            var nav = document.createElement('nav');
            nav.className = 'hardware-jumps';
            nav.setAttribute('aria-label', 'On this page');
            var label = document.createElement('strong');
            label.textContent = 'On this page';
            nav.appendChild(label);
            headings.forEach(function (heading, i) {
                heading.id = 'section-' + (i + 1) + '-' + heading.textContent.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-$/, '');
                heading.tabIndex = -1;
                var link = document.createElement('a');
                link.href = '#/' + path + '#' + heading.id;
                link.textContent = heading.textContent.replace(/^\d+\.\s*/, '');
                link.addEventListener('click', function (event) {
                    if (location.hash === link.hash) {
                        event.preventDefault();
                        heading.scrollIntoView();
                        heading.focus({ preventScroll: true });
                    }
                });
                nav.appendChild(link);
            });
            (intro && intro.tagName === 'P' ? intro : title).after(nav);
        }

        content.querySelectorAll('table').forEach(function (table, i) {
            var scroll = document.createElement('div');
            scroll.className = 'hardware-table';
            scroll.tabIndex = 0;
            scroll.setAttribute('role', 'region');
            scroll.setAttribute('aria-label', 'Hardware table ' + (i + 1) + ' — scroll horizontally if needed');
            table.before(scroll);
            scroll.appendChild(table);
        });

        content.querySelectorAll('img').forEach(function (img) {
            img.loading = 'lazy';
            img.decoding = 'async';
            var button = document.createElement('button');
            button.type = 'button';
            button.className = 'hardware-image';
            button.setAttribute('aria-label', 'Enlarge: ' + img.alt);
            img.before(button);
            button.appendChild(img);
            var hint = document.createElement('span');
            hint.textContent = 'Enlarge image ↗';
            button.appendChild(hint);
            function showImageFallback() {
                var source = document.createElement('a');
                source.className = 'hardware-image-fallback';
                source.href = img.src;
                source.target = '_blank';
                source.rel = 'noopener';
                source.textContent = 'Image unavailable. Open the source image ↗';
                button.replaceWith(source);
            }
            img.addEventListener('error', showImageFallback, { once: true });
            if (img.complete && !img.naturalWidth) showImageFallback();
            button.addEventListener('click', function () {
                fullImage.src = img.src;
                fullImage.alt = img.alt;
                viewer.showModal();
            });
        });
        content.querySelectorAll('iframe').forEach(function (frame) { frame.loading = 'lazy'; });
    };
})();
