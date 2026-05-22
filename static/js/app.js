/**
 * SecureTask — App JavaScript
 * SECURITY: No inline event handlers, no eval(), no innerHTML with user data.
 * All DOM manipulation via textContent or safe methods.
 */
'use strict';

document.addEventListener('DOMContentLoaded', function () {

  // ─── Sidebar Toggle ──────────────────────────────────────────────────────
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar       = document.getElementById('sidebar');
  const mainWrapper   = document.getElementById('mainWrapper');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (e) {
      if (window.innerWidth < 992 &&
          sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) &&
          e.target !== sidebarToggle) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ─── Auto-dismiss alerts after 5 s ─────────────────────────────────────
  document.querySelectorAll('.alert.alert-dismissible').forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ─── Confirm delete via data attribute (avoid inline onclick) ───────────
  // Forms with data-confirm attribute will prompt before submission
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const msg = form.dataset.confirm || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // ─── Active nav highlighting ────────────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-nav .nav-link').forEach(function (link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // ─── Character counter for textareas ────────────────────────────────────
  document.querySelectorAll('textarea[maxlength]').forEach(function (ta) {
    const max     = parseInt(ta.getAttribute('maxlength'));
    const counter = document.createElement('div');
    counter.className = 'form-text text-end';
    // SECURITY: Use textContent — never innerHTML with user values
    counter.textContent = `0 / ${max}`;
    ta.parentNode.appendChild(counter);

    ta.addEventListener('input', function () {
      const len = ta.value.length;
      counter.textContent = `${len} / ${max}`;
      counter.style.color = len > max * 0.9 ? '#ef4444' : '';
    });
    // Trigger on load
    ta.dispatchEvent(new Event('input'));
  });

});
