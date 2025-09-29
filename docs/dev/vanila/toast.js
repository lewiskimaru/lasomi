/* Minimal, independent Toast service (no backend changes required)
 * Usage:
 *   Toast.loading({ id: 'upload', title: 'Processing design', message: 'my.kml' })
 *   Toast.success({ id: 'upload', title: 'Design processed', message: 'Layers rendered' })
 *   Toast.error({ id: 'upload', title: 'Upload failed', message: 'Network error', actions:[{label:'Retry', onClick(){...}}] })
 *   Toast.info({ title: 'Heads up', message: 'Something informative' })
 *   Toast.dismiss('upload')
 */
(function () {
  const ICONS = {
    success: '<i class="fas fa-check-circle"></i>',
    error: '<i class="fas fa-exclamation-circle"></i>',
    info: '<i class="fas fa-info-circle"></i>',
    warning: '<i class="fas fa-exclamation-triangle"></i>',
    loading: '<div class="spinner" aria-hidden="true"></div>'
  };

  const AUTO_CLOSE_MS = 5000; // success/info auto close

  function ensureRoot() {
    let root = document.getElementById('toast-root');
    if (!root) {
      root = document.createElement('div');
      root.id = 'toast-root';
      root.setAttribute('role', 'status');
      root.setAttribute('aria-live', 'polite');
      document.body.appendChild(root);
    }
    return root;
  }

  function createToastEl(kind, { id, title, message, actions }) {
    const el = document.createElement('div');
    el.className = `toast ${kind}`;
    if (id) el.dataset.toastId = id;

    const iconEl = document.createElement('div');
    iconEl.className = 'icon';
    iconEl.innerHTML = ICONS[kind] || ICONS.info;

    const contentEl = document.createElement('div');
    contentEl.className = 'content';

    const titleEl = document.createElement('div');
    titleEl.className = 'title';
    titleEl.textContent = title || (kind[0].toUpperCase() + kind.slice(1));

    const msgEl = document.createElement('div');
    msgEl.className = 'message';
    if (message) msgEl.textContent = message;

    contentEl.appendChild(titleEl);
    if (message) contentEl.appendChild(msgEl);

    const rightEl = document.createElement('div');
    rightEl.className = 'actions';
    // Close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'close';
    closeBtn.setAttribute('aria-label', 'Dismiss notification');
    closeBtn.innerHTML = '<i class="fas fa-times"></i>';
    closeBtn.addEventListener('click', () => {
      removeToast(el);
    });
    rightEl.appendChild(closeBtn);

    // Optional actions
    if (Array.isArray(actions)) {
      actions.forEach(act => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-secondary btn-sm';
        btn.textContent = act.label || 'Action';
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          if (typeof act.onClick === 'function') act.onClick();
        });
        rightEl.insertBefore(btn, closeBtn);
      });
    }

    el.appendChild(iconEl);
    el.appendChild(contentEl);
    el.appendChild(rightEl);
    return el;
  }

  function removeToast(toastEl) {
    if (!toastEl || !toastEl.parentElement) return;
    toastEl.parentElement.removeChild(toastEl);
  }

  function upsert(kind, opts = {}) {
    const root = ensureRoot();
    let existing = null;
    if (opts.id) {
      existing = root.querySelector(`.toast[data-toast-id="${opts.id}"]`);
    }

    if (existing) {
      // Replace existing
      const newEl = createToastEl(kind, opts);
      existing.replaceWith(newEl);
      scheduleAutoClose(kind, newEl, opts);
      return newEl;
    }

    const el = createToastEl(kind, opts);
    root.appendChild(el);
    scheduleAutoClose(kind, el, opts);
    return el;
  }

  function scheduleAutoClose(kind, el, opts) {
    // Loading should not auto-close; success/info do; error optional
    if (kind === 'loading') return;
    const timeout = (kind === 'error') ? (opts.autoCloseMs || 7000) : (opts.autoCloseMs || AUTO_CLOSE_MS);
    if (timeout > 0) {
      setTimeout(() => removeToast(el), timeout);
    }
  }

  const Toast = {
    loading: (opts) => upsert('loading', opts),
    success: (opts) => upsert('success', opts),
    error: (opts) => upsert('error', opts),
    info: (opts) => upsert('info', opts),
    warning: (opts) => upsert('warning', opts),
    dismiss: (id) => {
      const root = document.getElementById('toast-root');
      if (!root) return;
      const el = root.querySelector(`.toast[data-toast-id="${id}"]`);
      if (el) removeToast(el);
    }
  };

  // ESC to close the last toast
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const root = document.getElementById('toast-root');
      if (!root) return;
      const toasts = root.querySelectorAll('.toast');
      const last = toasts[toasts.length - 1];
      if (last) removeToast(last);
    }
  });

  // Expose globally
  window.Toast = Toast;
})();
