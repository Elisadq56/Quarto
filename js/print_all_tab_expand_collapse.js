(function () {
    function expandAll() {
        // --- TABSETS ---
        document.querySelectorAll('.tab-pane').forEach(p => {
            p.classList.add('show', 'active');
            p.classList.remove('fade');
            p.style.display = 'block';
            p.style.opacity = '1';
            p.removeAttribute('hidden');
            p.setAttribute('aria-hidden', 'false');

            // Ajouter un titre H2 basé sur le texte de l’onglet correspondant
            const id = p.getAttribute('id');
            const tab = document.querySelector(`a[data-bs-target="#${id}"]`);
            if (tab) {
                const titleText = tab.innerText.trim();
                if (titleText && !p.querySelector('.print-tab-title')) {
                    const h2 = document.createElement('h2');
                    h2.classList.add('print-tab-title');
                    h2.innerText = titleText;
                    p.insertBefore(h2, p.firstChild);
                }
            }
        });

        // --- CALLOUTS / COLLAPSES (hors navbar) ---
        document.querySelectorAll('.collapse:not(.navbar-collapse)').forEach(c => {
            c.classList.add('show');
            c.style.height = 'auto';
            c.style.display = 'block';
        });

        document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(t => {
            const target = t.getAttribute('data-bs-target') || t.getAttribute('aria-controls');
            if (target && target.includes('navbarCollapse')) return; // skip navbar
            t.setAttribute('aria-expanded', 'true');
            t.classList.remove('collapsed');
        });
    }

    function restore() {
        // plus simple : recharger la page pour retrouver l'état initial
        location.reload();
    }

    window.addEventListener('beforeprint', expandAll);
    window.addEventListener('afterprint', restore);
})();