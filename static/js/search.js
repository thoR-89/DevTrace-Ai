document.addEventListener('DOMContentLoaded', function () {

    // ── 1. Search Form — Loading Overlay ──────────────────────────────────
    const searchForm = document.getElementById('searchForm');
    const searchBtn  = document.getElementById('searchBtn');
    const overlay    = document.getElementById('loadingOverlay');

    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            // Basic validation: require at least one field
            const name   = document.getElementById('devName');
            const github = document.getElementById('devGithub');
            const hasName   = name   && name.value.trim().length > 0;
            const hasGithub = github && github.value.trim().length > 0;

            if (!hasName && !hasGithub) {
                e.preventDefault();
                if (name) {
                    name.focus();
                    name.style.borderColor = 'var(--danger)';
                    setTimeout(() => { name.style.borderColor = ''; }, 2500);
                }
                return;
            }

            if (searchBtn) {
                searchBtn.disabled = true;
                searchBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Searching Platforms...';
            }
            if (overlay) {
                overlay.classList.add('active');
            }
        });
    }

    // ── 2. Result Page — Circular Gauge Animation ─────────────────────────
    const progressRing = document.querySelector('.progress-ring');
    if (progressRing) {
        const confidence   = parseInt(progressRing.getAttribute('data-confidence') || '0', 10);
        const radius       = 42;  // matches r="42" in result.html SVG
        const circumference = 2 * Math.PI * radius;  // ≈ 263.9

        // Set dasharray and start fully-offset (invisible)
        progressRing.style.strokeDasharray  = `${circumference}`;
        progressRing.style.strokeDashoffset = `${circumference}`;

        // Animate after a tick so the browser paints the start state first
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                const offset = circumference - (confidence / 100) * circumference;
                progressRing.style.strokeDashoffset = offset;
            });
        });
    }
});

// ── PDF Download ──────────────────────────────────────────────────────────
function downloadPDFReport() {
    window.print();
}

// ── Delete History Record ─────────────────────────────────────────────────
function deleteHistoryRecord(historyId) {
    if (!confirm('Delete this search record? This action cannot be undone.')) return;

    fetch(`/history/delete/${historyId}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const row = document.getElementById(`history-row-${historyId}`);
                if (row) {
                    row.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
                    row.style.opacity  = '0';
                    row.style.transform = 'scale(0.96)';
                    setTimeout(() => row.remove(), 350);
                }
            } else {
                alert(data.error || 'Failed to delete entry.');
            }
        })
        .catch(err => {
            console.error('Delete error:', err);
            alert('Network error. Please try again.');
        });
}