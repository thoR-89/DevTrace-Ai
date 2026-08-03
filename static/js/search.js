document.addEventListener('DOMContentLoaded', function() {
    // 1. Search Form Submission Loading Overlay
    const searchForm = document.getElementById('searchForm');
    const searchBtn = document.getElementById('searchBtn');

    if (searchForm && searchBtn) {
        searchForm.addEventListener('submit', function() {
            searchBtn.disabled = true;
            searchBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Searching Platforms...';
        });
    }

    // 2. Animate Circular Progress Gauge on Result Page
    const progressRing = document.querySelector('.progress-ring');
    if (progressRing) {
        const confidence = parseInt(progressRing.getAttribute('data-confidence') || '0', 10);
        const radius = 45;
        const circumference = 2 * Math.PI * radius;
        progressRing.style.strokeDasharray = `${circumference} ${circumference}`;
        
        const offset = circumference - (confidence / 100) * circumference;
        setTimeout(() => {
            progressRing.style.strokeDashoffset = offset;
        }, 100);
    }
});

// Download Identity Report PDF
function downloadPDFReport() {
    window.print();
}

// Delete History Item
function deleteHistoryRecord(historyId) {
    if (!confirm('Are you sure you want to delete this search history entry?')) {
        return;
    }

    fetch(`/history/delete/${historyId}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const row = document.getElementById(`history-row-${historyId}`);
                if (row) row.remove();
            } else {
                alert(data.error || 'Failed to delete entry');
            }
        })
        .catch(err => console.error('Delete error:', err));
}