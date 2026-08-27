// Normalise une URL : retire fragment, trailing slash, index.html
function normalizeUrl(url) {
  try {
    const u = new URL(url, location.href);
    let p = u.pathname.replace(/\/index\.html$/, '/')
                      .replace(/\/$/, '');
    return u.origin + p;
  } catch { return url; }
}

document.addEventListener('DOMContentLoaded', () => {
  const current = normalizeUrl(location.href);

  /* 1. Items dans les dropdowns */
  document.querySelectorAll('.dropdown-menu .dropdown-item').forEach(link => {
    const href = link.getAttribute('data-original-href') || link.href;
    if (normalizeUrl(href) === current) {
      link.classList.add('active');

      /* 2. Remonter au parent .nav-item.dropdown */
      const parentItem = link.closest('.nav-item.dropdown');
      if (parentItem) {
        parentItem.classList.add('active');
        const toggle = parentItem.querySelector(':scope > .nav-link.dropdown-toggle');
        if (toggle) toggle.classList.add('active');
      }
    }
  });
});