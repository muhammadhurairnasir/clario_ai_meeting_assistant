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

  // ── Upload form — show spinner & percentage on submit ───────────────────────
  const uploadForm = document.getElementById('upload-form');
  const submitBtn  = document.getElementById('upload-submit-btn');
  const spinnerEl  = document.getElementById('upload-spinner');
  const pctEl      = document.getElementById('loading-percentage');
  const statusEl   = document.getElementById('loading-status-text');

  if (uploadForm && submitBtn) {
    uploadForm.addEventListener('submit', () => {
      submitBtn.style.display = 'none'; // Hide button completely
      
      // Hide the file/text inputs so the user just sees the loader
      const cards = uploadForm.querySelectorAll('.card');
      cards.forEach(c => c.style.display = 'none');
      
      if (spinnerEl) spinnerEl.style.display = 'block';

      let progress = 0;
      
      // Simulated intelligent loading progression
      const interval = setInterval(() => {
        // Fast upload phase (0 to 15%)
        if (progress < 15) {
          progress += Math.floor(Math.random() * 4) + 2;
          if (statusEl) statusEl.textContent = 'Uploading audio file...';
        }
        // AI Transcription phase (15% to 55%)
        else if (progress < 55) {
          progress += Math.floor(Math.random() * 3) + 1;
          if (statusEl) statusEl.textContent = 'Whisper AI is transcribing audio...';
        }
        // Summarization phase (55% to 80%)
        else if (progress < 80) {
          progress += Math.floor(Math.random() * 2) + 1;
          if (statusEl) statusEl.textContent = 'BART AI is generating summary...';
        }
        // Task extraction & graph phase (80% to 95%)
        else if (progress < 95) {
          progress += 1;
          if (statusEl) statusEl.textContent = 'Extracting tasks & building graphs...';
        }
        // Cap at 95% until server actually responds and page reloads
        else {
          progress = 95;
          if (statusEl) statusEl.textContent = 'Finalizing business analytics...';
        }

        if (pctEl) pctEl.textContent = progress + '%';

      }, 800); // Update every 800ms
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
