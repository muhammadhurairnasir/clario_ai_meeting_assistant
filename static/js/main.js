/* static/css/style.css is the primary stylesheet.
   This file holds minor JS-driven interactions. */

// ── Upload drag-and-drop ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const zone = document.querySelector('.upload-zone');
  const fileInput = document.getElementById('audio_file');

  if (zone && fileInput) {
    zone.addEventListener('click', () => fileInput.click());

    zone.addEventListener('dragover', (e) => {
      e.preventDefault();
      zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));

    zone.addEventListener('drop', (e) => {
      e.preventDefault();
      zone.classList.remove('dragover');
      const files = e.dataTransfer.files;
      if (files.length) {
        fileInput.files = files;
        updateZoneLabel(files[0].name);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) updateZoneLabel(fileInput.files[0].name);
    });

    function updateZoneLabel(name) {
      const hint = zone.querySelector('.upload-hint');
      if (hint) hint.textContent = `✅ Selected: ${name}`;
    }
  }

  // ── Upload form — show spinner on submit ────────────────────────────────────
  const uploadForm = document.getElementById('upload-form');
  const submitBtn  = document.getElementById('upload-submit-btn');
  const spinnerEl  = document.getElementById('upload-spinner');

  if (uploadForm && submitBtn) {
    uploadForm.addEventListener('submit', () => {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Processing…';
      if (spinnerEl) spinnerEl.style.display = 'block';
    });
  }

  // ── Auto-dismiss flash messages ─────────────────────────────────────────────
  document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.5s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 500);
    }, 5000);
  });

  // ── Active nav link ─────────────────────────────────────────────────────────
  const current = window.location.pathname;
  document.querySelectorAll('.navbar-nav a').forEach(a => {
    if (a.getAttribute('href') === current) a.classList.add('active');
  });
});
