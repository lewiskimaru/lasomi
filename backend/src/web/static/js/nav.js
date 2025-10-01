/* SPA-like navigation for Atlas web interface using History API (plain JS)
 * - Intercepts clicks on sidebar links (/web/*)
 * - Fetches target page, swaps #page-root contents without full reload
 * - Updates active states and handles back/forward with popstate
 */
(function() {
  function isInternalWebLink(a) {
    if (!a || !a.href) return false;
    try {
      const url = new URL(a.href, window.location.origin);
      return url.origin === window.location.origin && url.pathname.startsWith('/web/');
    } catch (_) {
      return false;
    }
  }

  function ensureHeadAssets(fromDoc) {
    if (!fromDoc) return;
    const currentHead = document.head;

    // Sync stylesheets
    const existingLinks = new Set(Array.from(currentHead.querySelectorAll('link[rel="stylesheet"]')).map(l => l.href));
    const targetLinks = Array.from(fromDoc.head.querySelectorAll('link[rel="stylesheet"]'));
    for (const link of targetLinks) {
      if (!existingLinks.has(link.href)) {
        const newLink = document.createElement('link');
        newLink.rel = 'stylesheet';
        newLink.href = link.href;
        currentHead.appendChild(newLink);
      }
    }

    // Sync script files (only external src, ignore inline for safety)
    const existingScripts = new Set(Array.from(currentHead.querySelectorAll('script[src]')).map(s => s.src));
    const targetScripts = Array.from(fromDoc.head.querySelectorAll('script[src]'));
    for (const script of targetScripts) {
      if (!existingScripts.has(script.src)) {
        const newScript = document.createElement('script');
        newScript.src = script.src;
        if (script.defer) newScript.defer = true;
        if (script.async) newScript.async = true;
        currentHead.appendChild(newScript);
      }
    }
  }

  async function navigateTo(url, push = true) {
    const root = document.getElementById('page-root');
    if (!root) return;

    // Optional: show a minimal loading state
    root.style.opacity = '0.6';

    try {
      const res = await fetch(url, { headers: { 'X-Requested-With': 'fetch' } });
      if (!res.ok) throw new Error(`Failed to load: ${res.status}`);
      const html = await res.text();

      // Parse the returned HTML and extract #page-root content
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const newRoot = doc.getElementById('page-root');
      if (!newRoot) throw new Error('Target page missing #page-root');

      // Ensure page-specific head assets (CSS/JS) are available
      ensureHeadAssets(doc);

      // Replace current root
      root.replaceWith(newRoot);

      // Update active states in mini sidebar
      updateMiniSidebarActive(url);

      // Optionally focus main content for accessibility
      setTimeout(() => {
        const main = document.querySelector('main') || document.body;
        main.setAttribute('tabindex', '-1');
        main.focus({ preventScroll: true });
      }, 0);

      // Dispatch a custom event so per-page scripts can initialize
      const pageId = newRoot.getAttribute('data-page');
      window.dispatchEvent(new CustomEvent('page:loaded', { detail: { page: pageId, url } }));

      if (push) {
        history.pushState({ url }, '', url);
      }
    } catch (err) {
      console.error('Navigation error:', err);
      window.location.href = url; // Fallback to full navigation
    } finally {
      const newCurrentRoot = document.getElementById('page-root');
      if (newCurrentRoot) newCurrentRoot.style.opacity = '';
    }
  }

  function updateMiniSidebarActive(url) {
    const links = document.querySelectorAll('.sidebar .sidebar-nav a');
    links.forEach(link => link.classList.remove('active'));
    links.forEach(link => {
      try {
        const u = new URL(link.href, window.location.origin);
        const target = new URL(url, window.location.origin);
        if (u.pathname === target.pathname) link.classList.add('active');
      } catch(_) {}
    });
  }

  function onLinkClick(e) {
    const a = e.target.closest('a');
    if (!a) return;
    if (!isInternalWebLink(a)) return;

    e.preventDefault();
    navigateTo(a.getAttribute('href'));
  }

  function onPopState(e) {
    const url = (e.state && e.state.url) ? e.state.url : window.location.pathname + window.location.search + window.location.hash;
    navigateTo(url, false);
  }

  // Attach global handlers
  document.addEventListener('click', onLinkClick);
  window.addEventListener('popstate', onPopState);

  // Initialize active state on first load
  updateMiniSidebarActive(window.location.href);
})();
